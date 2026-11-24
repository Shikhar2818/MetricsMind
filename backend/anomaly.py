import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from config import CPU_THRESHOLD, DATA_PATH, SEED
from explain import explain
from features import add_features, feature_cols

BOUNDS = (0.6, 0.75)  # train | validation | test split on each server's timeline


def detect(df=None):
    d = pd.read_parquet(DATA_PATH) if df is None else df
    d = add_features(d)
    cols = feature_cols(d)
    d = d.dropna(subset=cols)
    scored, thresholds = [], {}
    for server, g in d.groupby("server", sort=True):
        g = g.sort_values("timestamp")
        n = len(g)
        cut1, cut2 = int(n * BOUNDS[0]), int(n * BOUNDS[1])
        tr, va = g.iloc[:cut1], g.iloc[cut1:cut2]
        model = make_pipeline(StandardScaler(), IsolationForest(n_estimators=200, random_state=SEED, n_jobs=-1))
        model.fit(tr[cols])
        raw_va = -model.decision_function(va[cols])
        lo, hi = raw_va.min(), raw_va.max()
        score_va = np.clip((raw_va - lo) / (hi - lo), 0, 1)
        thr = float(np.quantile(score_va[va.is_anomaly == 0], 0.995))  # 0.5% FP budget, calibrated on normal validation points
        thresholds[server] = round(thr, 3)
        parts = [("train", g.iloc[:cut1]), ("val", va), ("test", g.iloc[cut2:])]
        for split, part in parts:
            raw = -model.decision_function(part[cols])
            s = np.clip((raw - lo) / (hi - lo), 0, 1)
            part = part.assign(anomaly_score=s, if_flag=(s >= thr).astype(int),
                               baseline_flag=(part.cpu > CPU_THRESHOLD).astype(int))
            part["drivers"] = "" if split == "train" else explain(part, model, tr, cols)
            scored.append(part.assign(split=split))
    return pd.concat(scored, ignore_index=True), thresholds


def _prf(y, p):
    return dict(precision=precision_score(y, p, zero_division=0),
                recall=recall_score(y, p, zero_division=0),
                f1=f1_score(y, p, zero_division=0))


def event_table(g, flag):
    g = g.sort_values(["server", "timestamp"])
    breaks = (g.server.ne(g.server.shift()) | g.anomaly_type.ne(g.anomaly_type.shift())
              | g.timestamp.diff().ne(pd.Timedelta("1min")))
    rows = []
    for _, e in g.groupby(breaks.cumsum()):
        hit = e.timestamp[e[flag] == 1]
        rows.append(dict(detected=not hit.empty,
                         delay=(hit.iloc[0] - e.timestamp.iloc[0]).total_seconds() / 60 if not hit.empty else np.nan))
    return pd.DataFrame(rows, columns=["detected", "delay"])


if __name__ == "__main__":
    d, thresholds = detect()
    test = d[d.split == "test"]
    y = test.is_anomaly.to_numpy()
    print("split rows:", d.split.value_counts().to_dict(), f"| per-server thresholds: {thresholds}")
    print(f"test label rate {y.mean():.3%} | IF flag rate {test.if_flag.mean():.3%} | CPU>90 flag rate {test.baseline_flag.mean():.3%}\n")
    scores = pd.DataFrame([{"model": "IsolationForest", **_prf(y, test.if_flag)},
                           {"model": f"CPU>{CPU_THRESHOLD}", **_prf(y, test.baseline_flag)}])
    print(scores.set_index("model").round(3).to_string())

    rows = []
    for t, g in test[test.is_anomaly == 1].groupby("anomaly_type"):
        ev, evb = event_table(g, "if_flag"), event_table(g, "baseline_flag")
        rows.append(dict(anomaly_type=t, points=len(g),
                         if_recall=round(g.if_flag.mean(), 3), base_recall=round(g.baseline_flag.mean(), 3),
                         events=len(ev), if_events=int(ev.detected.sum()), base_events=int(evb.detected.sum()),
                         if_delay_min=round(ev.delay.median(), 1) if ev.detected.any() else None))
    print("\nper anomaly_type (test):")
    print(pd.DataFrame(rows).set_index("anomaly_type").to_string())

    ev, evb = event_table(test[test.is_anomaly == 1], "if_flag"), event_table(test[test.is_anomaly == 1], "baseline_flag")
    print(f"\nevent-wise: IF {int(ev.detected.sum())}/{len(ev)} detected, median delay {ev.delay.median():.1f} min "
          f"| baseline {int(evb.detected.sum())}/{len(evb)}")
    print("\nscore on test anomalies by type:")
    print(test[test.is_anomaly == 1].groupby("anomaly_type").anomaly_score.agg(["mean", "max"]).round(3).to_string())
