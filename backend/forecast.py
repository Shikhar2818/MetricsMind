import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
from xgboost import XGBRegressor

from config import CPU_THRESHOLD, DATA_PATH, DISK_THRESHOLD, METRICS, SEED

H = 30  # forecast horizon in minutes
LAGS = (1, 5, 15)
FEATS = ["cpu", "cpu_lag1", "cpu_lag5", "cpu_lag15", "cpu_mean15", "cpu_std15", "cpu_mean60", "cpu_std60",
         "hour", "dow", "memory", "disk", "network", "latency", "error_rate"]


def build(df):
    parts = []
    for _, g in df.groupby("server", sort=True):
        g = g.sort_values("timestamp")
        f = {f"cpu_lag{l}": g.cpu.shift(l) for l in LAGS}
        for w in (15, 60):
            f[f"cpu_mean{w}"] = g.cpu.rolling(w).mean()
            f[f"cpu_std{w}"] = g.cpu.rolling(w).std()
        f["hour"] = g.timestamp.dt.hour
        f["dow"] = g.timestamp.dt.dayofweek
        f["target"] = g.cpu.shift(-H)
        parts.append(g.join(pd.DataFrame(f, index=g.index)))
    return pd.concat(parts).reset_index(drop=True)


def mae_rmse(y, p):
    return mean_absolute_error(y, p), float(np.sqrt(mean_squared_error(y, p)))


def predict_cpu(df=None):
    d = build(pd.read_parquet(DATA_PATH) if df is None else df).dropna(subset=[*FEATS, "target"])
    tests = {}
    for server, g in d.groupby("server"):
        g = g.sort_values("timestamp").reset_index(drop=True)
        a, b = int(len(g) * 0.6), int(len(g) * 0.8)
        tr, va, te = g.iloc[:a], g.iloc[a:b], g.iloc[b:]
        model = XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=6, subsample=0.8,
                             colsample_bytree=0.8, random_state=SEED, n_jobs=-1,
                             early_stopping_rounds=30, eval_metric="rmse")
        model.fit(tr[FEATS], tr.target, eval_set=[(va[FEATS], va.target)], verbose=False)
        tests[server] = te.assign(pred=model.predict(te[FEATS]).astype(float))
    return tests


def sarima_compare(df, tests):
    raw = df[df.server == "server-01"].set_index("timestamp").cpu.resample("30min").mean()
    cut = int(len(raw) * 0.8)
    fit = SARIMAX(raw.iloc[:cut], order=(1, 0, 0), seasonal_order=(1, 0, 1, 48),
                  enforce_stationarity=True, enforce_invertibility=True).fit(disp=False, maxiter=100)
    actual = raw.iloc[cut:]
    pred_sarima = fit.get_prediction(start=cut, end=len(raw) - 1, dynamic=False).predicted_mean
    naive = raw.shift(1).iloc[cut:]
    te = tests["server-01"].set_index("timestamp")
    common = actual.index.intersection(te[te.index.minute % 30 == 0].index)
    grid = te.reindex(common)
    rows = [{"model": "naive (30-min grid)", "target": "next 30-min mean", **dict(zip(("mae", "rmse"), mae_rmse(actual.loc[common], naive.loc[common])))},
            {"model": "SARIMA(1,0,0)(1,0,1,48)", "target": "next 30-min mean", **dict(zip(("mae", "rmse"), mae_rmse(actual.loc[common], pred_sarima.loc[common])))},
            {"model": "XGBoost (same origins)", "target": "point at +30 min", **dict(zip(("mae", "rmse"), mae_rmse(grid.target, grid.pred)))}]
    return pd.DataFrame(rows).set_index("model").round(2)


def disk_table(df):
    rows = []
    for _, g in df.groupby("server"):
        daily = g.set_index("timestamp").disk.resample("1D").last().dropna()
        for i in range(7, len(daily)):
            slope = np.polyfit(np.arange(7), daily.iloc[i - 6:i + 1].to_numpy(), 1)[0]
            origin = daily.iloc[i]
            for h in (1, 3, 7):
                if i + h < len(daily):
                    rows.append(dict(horizon=h, trend=origin + slope * h - daily.iloc[i + h],
                                     naive=origin - daily.iloc[i + h]))
    r = pd.DataFrame(rows)
    out = r.groupby("horizon").agg(trend_mae=("trend", lambda x: x.abs().mean()),
                                   naive_mae=("naive", lambda x: x.abs().mean()),
                                   trend_rmse=("trend", lambda x: np.sqrt((x**2).mean())),
                                   naive_rmse=("naive", lambda x: np.sqrt((x**2).mean())))
    return out.round(2)


def time_to_cross(now, pred, threshold, horizon=H):
    if pred <= threshold:
        return None
    if now >= threshold:
        return 0
    return round(horizon * (threshold - now) / (pred - now))


def disk_rate(df):
    out = {}
    for server, g in df.groupby("server"):
        daily = g.set_index("timestamp").disk.resample("1D").last().dropna()
        slope = np.polyfit(np.arange(7), daily.iloc[-7:].to_numpy(), 1)[0]
        last = daily.iloc[-1]
        out[server] = (slope, (DISK_THRESHOLD - last) / slope if slope > 0 else np.nan)
    return out


if __name__ == "__main__":
    df = pd.read_parquet(DATA_PATH)
    tests = predict_cpu(df)
    keys = ("naive_mae", "naive_rmse", "xgb_mae", "xgb_rmse")
    rows = [dict(server=s, **dict(zip(keys, (*mae_rmse(t.target, t.cpu), *mae_rmse(t.target, t.pred)))))
            for s, t in tests.items()]
    allte = pd.concat(tests.values())
    rows.append(dict(server="ALL", **dict(zip(keys, (*mae_rmse(allte.target, allte.cpu), *mae_rmse(allte.target, allte.pred))))))
    print(f"CPU forecast, horizon {H} min, test rows {len(allte):,}:")
    print(pd.DataFrame(rows).set_index("server").round(2).to_string())
    print("\nserver-01 small SARIMA comparison:")
    print(sarima_compare(df, tests).to_string())
    print("\ndisk trend vs naive (daily, MAE/RMSE in pct points):")
    print(disk_table(df).to_string())

    print("\ntime to threshold:")
    rates = disk_rate(df)
    out = []
    for s, t in tests.items():
        now, fc = t.cpu.iloc[-1], t.pred.iloc[-1]
        slope, days = rates[s]
        out.append(dict(server=s, cpu_now=round(now, 1), cpu_forecast_30=round(fc, 1),
                        cpu_min_to_90=time_to_cross(now, fc, CPU_THRESHOLD),
                        disk_now=round(df[df.server == s].disk.iloc[-1], 1),
                        disk_pct_per_day=round(slope, 3), disk_days_to_90=round(days, 1)))
    print(pd.DataFrame(out).set_index("server").fillna("-").to_string())

    hits = pd.concat([t.assign(server=s) for s, t in tests.items()])
    hits = hits[hits.pred > CPU_THRESHOLD].sort_values("timestamp")
    if hits.empty:
        print("\nCPU: no 30-min forecast above 90 in the test period")
    else:
        r = hits.iloc[0]
        print(f"\nCPU crossing example: {r.server} {r.timestamp} cpu {r.cpu:.1f} -> forecast {r.pred:.1f} "
              f"in {time_to_cross(r.cpu, r.pred, CPU_THRESHOLD)} min")
