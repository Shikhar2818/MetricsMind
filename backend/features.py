import numpy as np
import pandas as pd

from config import METRICS

WINDOWS = (5, 15, 60)
LONG = (360, 1440)  # 6 h and 24 h baselines expose slow drifts the 60 min window hides
META = ["timestamp", "server", "is_anomaly", "anomaly_type", *METRICS]


def add_features(df):
    parts = []
    for _, g in df.groupby("server", sort=True):
        g = g.sort_values("timestamp")
        f = {}
        for m in METRICS:
            s = g[m]
            for w in WINDOWS:
                f[f"{m}_mean{w}"] = s.rolling(w).mean()
                f[f"{m}_std{w}"] = s.rolling(w).std()
            f[f"{m}_diff"] = s.diff()
            f[f"{m}_diff60"] = s.diff(60)
            f[f"{m}_dev"] = s - s.rolling(60).mean()  # deviation from the server's own recent baseline
            for w in LONG:
                f[f"{m}_dev{w}"] = s - s.rolling(w).mean()
        hour = g.timestamp.dt.hour + g.timestamp.dt.minute / 60
        f["hour_sin"] = np.sin(2 * np.pi * hour / 24)
        f["hour_cos"] = np.cos(2 * np.pi * hour / 24)
        parts.append(g.join(pd.DataFrame(f, index=g.index)))
    return pd.concat(parts).reset_index(drop=True)


def feature_cols(df):
    return [c for c in df.columns if c not in META and c != "drivers"]
