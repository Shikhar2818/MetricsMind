import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import DATA_PATH, FREQ, N_DAYS, PLOT_DIR, SEED, SERVERS, START

MINUTES = N_DAYS * 1440
RNG = np.random.default_rng(SEED)
PCT = ["cpu", "memory", "disk", "error_rate"]
# metric, (min minutes, max minutes, count per server)
SPECS = {
    "cpu_spike": (18, 35, 4),
    "memory_leak": (240, 360, 2),
    "network_burst": (15, 25, 2),
    "latency_error": (12, 20, 2),
    "multivariate": (30, 60, 2),
    "disk_fill": (600, 840, 2),
}


def normal_series(ts, p):
    hour = np.asarray(ts.hour + ts.minute / 60, dtype=float)
    weekend = np.asarray(ts.dayofweek >= 5, dtype=float)
    weekly = np.sin(2 * np.pi * np.arange(len(ts)) / (1440 * 7) + RNG.uniform(0, 2 * np.pi))
    cpu = p["cpu"] + p["amp"] * np.sin(2 * np.pi * (hour - 8) / 24) * (1 - 0.3 * weekend)
    cpu = np.clip(cpu + 4 * weekly + RNG.normal(0, p["noise"], len(ts)), 2, 100)
    memory = np.clip(p["mem"] + 0.32 * cpu + RNG.normal(0, 2.0, len(ts)), 5, 100)
    network = np.clip(p["net"] * (0.55 + cpu / 75) + RNG.normal(0, p["net"] * 0.06, len(ts)), 0, None)
    latency = np.clip(p["lat"] + 0.4 * cpu + 0.011 * cpu**2 + RNG.normal(0, 2.5, len(ts)), 1, None)
    error_rate = np.clip(0.03 + 1.1 * (latency / 55) ** 2 + RNG.normal(0, 0.22, len(ts)), 0, 100)
    # disk grows monotonically; per-minute jitter is floored at zero
    growth = p["disk_rate"] / 1440 + RNG.normal(0, 0.0005, len(ts))
    disk = np.clip(p["disk"] + np.maximum(growth, 0).cumsum(), 0, 100)
    return pd.DataFrame(dict(timestamp=ts, cpu=cpu, memory=memory, disk=disk,
                             network=network, latency=latency, error_rate=error_rate))


def inject(df, kind, idx):
    t = np.linspace(0, 1, len(idx))
    ramp = np.sin(np.pi * t)
    if kind == "cpu_spike":
        df.loc[idx, "cpu"] += RNG.uniform(30, 42)
        df.loc[idx, "latency"] *= RNG.uniform(1.25, 1.45)
        df.loc[idx, "error_rate"] *= RNG.uniform(1.4, 1.9)
    elif kind == "memory_leak":
        df.loc[idx, "memory"] += RNG.uniform(16, 26) * t
        df.loc[idx, "cpu"] += RNG.uniform(2, 5) * t
    elif kind == "network_burst":
        df.loc[idx, "network"] *= RNG.uniform(4, 6)
        df.loc[idx, "latency"] *= RNG.uniform(1.2, 1.4)
    elif kind == "latency_error":
        df.loc[idx, "latency"] *= RNG.uniform(3.5, 5)
        df.loc[idx, "error_rate"] += RNG.uniform(6, 10) * ramp
    elif kind == "multivariate":
        df.loc[idx, "cpu"] += RNG.uniform(10, 14) * ramp
        df.loc[idx, "memory"] += RNG.uniform(8, 12) * ramp
        df.loc[idx, "network"] *= 1 + RNG.uniform(0.45, 0.7) * ramp
        df.loc[idx, "latency"] *= 1 + RNG.uniform(0.5, 0.8) * ramp
        df.loc[idx, "error_rate"] += RNG.uniform(1, 2) * ramp
    else:  # disk_fill: extra growth, kept permanently because disks never shrink
        extra = 0.02 * np.arange(len(idx))
        df.loc[idx, "disk"] += extra
        df.loc[idx[-1] + 1:, "disk"] += extra[-1]


def build():
    ts = pd.date_range(START, periods=MINUTES, freq=FREQ)
    frames, log = [], []
    for server, p in SERVERS.items():
        df = normal_series(ts, p)
        df["is_anomaly"] = 0
        df["anomaly_type"] = "none"
        used = np.zeros(MINUTES, bool)
        for kind, (lo, hi, count) in SPECS.items():
            if kind == "disk_fill" and server not in ("server-01", "server-04", "server-07"):
                continue
            for _ in range(count):
                minutes = int(RNG.integers(lo, hi + 1))
                start = int(RNG.integers(1440, MINUTES - minutes))
                idx = np.arange(start, start + minutes)
                while used[idx].any():
                    start = int(RNG.integers(1440, MINUTES - minutes))
                    idx = np.arange(start, start + minutes)
                used[idx] = True
                inject(df, kind, idx)
                df.loc[idx, "is_anomaly"] = 1
                df.loc[idx, "anomaly_type"] = kind
                log.append(dict(server=server, anomaly_type=kind, start=ts[idx[0]],
                                end=ts[idx[-1]], points=len(idx)))
        for col in PCT:
            df[col] = df[col].clip(0, 100)
        df["network"] = df["network"].clip(lower=0)
        df["latency"] = df["latency"].clip(lower=0.5)
        df.insert(1, "server", server)
        frames.append(df)
    return pd.concat(frames, ignore_index=True).sort_values(["timestamp", "server"]), pd.DataFrame(log)


def plot_week(df):
    start = df.timestamp.min()
    d = df[(df.server == "server-01") & (df.timestamp < start + pd.Timedelta(days=7))]
    fig, ax = plt.subplots(figsize=(14, 4.5))
    ax.plot(d.timestamp, d.cpu, lw=0.6, color="#2563eb", label="CPU %")
    ax.plot(d.timestamp, d.memory, lw=0.6, color="#7c3aed", label="Memory %")
    for kind, g in d[d.is_anomaly == 1].groupby("anomaly_type"):
        ax.axvspan(g.timestamp.min(), g.timestamp.max(), color="#ef4444", alpha=0.18,
                   label=f"anomaly: {kind}")
    ax.set_title("server-01 — first 7 days (red = labeled anomalies)")
    ax.set_ylabel("%")
    ax.legend(loc="upper left", ncol=4, fontsize=8, frameon=False)
    fig.tight_layout()
    out = PLOT_DIR / "server-01_week1.png"
    fig.savefig(out, dpi=130)
    return out


if __name__ == "__main__":
    df, log = build()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(exist_ok=True)
    df.to_parquet(DATA_PATH, index=False)

    print(f"rows={len(df):,}  servers={df.server.nunique()}  {df.timestamp.min()} -> {df.timestamp.max()}")
    print(f"label rate: {df.is_anomaly.mean():.2%} ({df.is_anomaly.sum():,} points)\n")
    per = log.groupby("anomaly_type").agg(events=("points", "size"), points=("points", "sum"),
                                           avg_minutes=("points", lambda s: int(s.mean())))
    print(per.to_string())
    print("\ninjected windows:")
    for r in log.sort_values(["server", "start"]).itertuples(index=False):
        print(f"  {r.server} {r.anomaly_type:<13} {r.start:%m-%d %H:%M} -> {r.end:%H:%M}  ({r.points:>3}m)")
    print("\nper server:")
    print(df.groupby("server").agg(rows=("is_anomaly", "size"),
                                   anomaly_pct=("is_anomaly", lambda s: round(s.mean() * 100, 2)),
                                   cpu_mean=("cpu", "mean"), cpu_max=("cpu", "max"),
                                   disk_end=("disk", "last")).round(2).to_string())
    print("\nmetric ranges:")
    print(df[["cpu", "memory", "disk", "network", "latency", "error_rate"]].describe().round(2).to_string())
    print("\nhead:")
    print(df.head(3).to_string(index=False))
    print(f"\nsaved {DATA_PATH} ({DATA_PATH.stat().st_size / 1e6:.1f} MB)")
    print(f"plot  {plot_week(df)}")
