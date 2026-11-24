import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Literal

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from anomaly import detect
from config import CPU_THRESHOLD, DATA_PATH, DISK_THRESHOLD, METRICS, REPLAY_SPEED
from forecast import predict_cpu, time_to_cross
from risk import assess

Severity = Literal["LOW", "MEDIUM", "HIGH"]
RANGES = {"1h": 60, "6h": 360, "24h": 1440, "3d": 4320, "7d": 10080}
STATE = {}


class Health(BaseModel):
    status: str
    now: datetime
    replay_speed: int
    data_start: datetime
    data_end: datetime
    servers: int


class ServerStatus(BaseModel):
    server: str
    cpu: float
    memory: float
    disk: float
    network: float
    latency: float
    error_rate: float
    anomaly_score: float
    forecast_30min: float | None
    severity: Severity
    reason: str
    flagged: bool
    sparklines: dict[str, list[float]]


class ServersResponse(BaseModel):
    now: datetime
    servers: list[ServerStatus]


class Summary(BaseModel):
    now: datetime
    total_servers: int
    healthy: int
    warning: int
    critical: int
    active_anomalies: int
    highest_forecast_risk: float
    highest_risk_server: str


class MetricPoint(BaseModel):
    t: datetime
    value: float
    score: float
    flagged: bool


class ForecastPoint(BaseModel):
    t: datetime
    value: float


class AnomalyWindow(BaseModel):
    start: datetime
    end: datetime
    score: float


class MetricResponse(BaseModel):
    server: str
    metric: str
    range: str
    current: float
    threshold: float | None
    points: list[MetricPoint]
    anomalies: list[AnomalyWindow]
    forecast: list[ForecastPoint]


class AnomalyEvent(BaseModel):
    server: str
    start: datetime
    end: datetime
    max_score: float
    severity: Severity
    reason: str


class AnomalyResponse(BaseModel):
    now: datetime
    events: list[AnomalyEvent]


class ForecastResponse(BaseModel):
    server: str
    now: datetime
    cpu_now: float
    forecast_30min: float
    minutes_to_90: int | None
    disk_now: float
    disk_pct_per_day: float
    disk_days_to_90: float | None
    points: list[ForecastPoint]


class Alert(BaseModel):
    time: datetime
    server: str
    metric: str
    score: float
    forecast_30min: float
    severity: Severity
    reason: str


class AlertsResponse(BaseModel):
    now: datetime
    alerts: list[Alert]


def now() -> pd.Timestamp:
    span = (STATE["end"] - STATE["start"]).total_seconds()
    elapsed = (time.time() - STATE["t0"]) * REPLAY_SPEED
    return (STATE["start"] + pd.Timedelta(seconds=elapsed % span)).floor("s")


def runs(d, gap="2min"):
    out = []
    for server, g in d[d.if_flag == 1].groupby("server"):
        for _, e in g.groupby(g.timestamp.diff().gt(pd.Timedelta(gap)).cumsum()):
            out.append(dict(server=server, start=e.timestamp.min(), end=e.timestamp.max(),
                            score=float(e.anomaly_score.max())))
    return out


def load():
    df = pd.read_parquet(DATA_PATH)
    scored, thresholds = detect(df)
    tests = pd.concat([t.assign(server=s) for s, t in predict_cpu(df).items()])
    scored = scored.merge(tests[["timestamp", "server", "pred"]], on=["timestamp", "server"], how="left")
    scored = scored.sort_values(["server", "timestamp"]).reset_index(drop=True)
    live = scored[scored.pred.notna()].copy()
    verdicts = [assess(r.cpu, r.anomaly_score, r.pred, r.if_flag, r.drivers) for r in live.itertuples()]
    live["severity"] = [v[0] for v in verdicts]
    live["reason"] = [v[1] for v in verdicts]
    STATE.update(scored=scored, live=live, thresholds=thresholds, servers=sorted(df.server.unique()),
                 start=live.timestamp.min().ceil("min"), end=live.timestamp.max(), t0=time.time())


@asynccontextmanager
async def lifespan(app):
    load()
    yield


app = FastAPI(title="Infrastructure Anomaly Detection API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000",
                                                   "http://localhost:3001", "http://127.0.0.1:3001"],
                   allow_methods=["*"], allow_headers=["*"])


def latest(now_ts):
    return STATE["live"][STATE["live"].timestamp <= now_ts].sort_values("timestamp").groupby("server").tail(1)


@app.get("/health", response_model=Health)
def health():
    return Health(status="ok", now=now().to_pydatetime(), replay_speed=REPLAY_SPEED,
                  data_start=STATE["start"].to_pydatetime(), data_end=STATE["end"].to_pydatetime(),
                  servers=len(STATE["servers"]))


@app.get("/servers", response_model=ServersResponse)
def servers():
    t = now()
    rows, sparks = latest(t), {}
    hist = STATE["scored"][(STATE["scored"].timestamp <= t) & (STATE["scored"].timestamp > t - pd.Timedelta(hours=2))]
    for s, g in hist.groupby("server"):
        g = g[g.timestamp.dt.minute % 5 == 0]
        sparks[s] = {m: g[m].round(2).tolist() for m in ("cpu", "memory", "network")}
    out = [ServerStatus(server=r.server, cpu=round(float(r.cpu), 1), memory=round(float(r.memory), 1),
                        disk=round(float(r.disk), 1), network=round(float(r.network), 1),
                        latency=round(float(r.latency), 1), error_rate=round(float(r.error_rate), 2),
                        anomaly_score=round(float(r.anomaly_score), 2),
                        forecast_30min=round(float(r.pred), 1), severity=r.severity, reason=r.reason,
                        flagged=bool(r.if_flag), sparklines=sparks.get(r.server, {}))
           for r in rows.itertuples()]
    return ServersResponse(now=t.to_pydatetime(), servers=out)


@app.get("/summary", response_model=Summary)
def summary():
    t, rows = now(), latest(now())
    counts = rows.severity.value_counts()
    top = rows.loc[rows.anomaly_score.idxmax()]
    return Summary(now=t.to_pydatetime(), total_servers=len(rows), healthy=int(counts.get("LOW", 0)),
                   warning=int(counts.get("MEDIUM", 0)), critical=int(counts.get("HIGH", 0)),
                   active_anomalies=int(rows.if_flag.sum()),
                   highest_forecast_risk=round(float(rows.anomaly_score.max()), 2),
                   highest_risk_server=top.server)


@app.get("/metrics", response_model=MetricResponse)
def metrics(server: str, metric: str, range: str = "6h"):
    if server not in STATE["servers"]:
        raise HTTPException(404, "unknown server")
    if metric not in METRICS:
        raise HTTPException(400, f"metric must be one of {METRICS}")
    if range not in RANGES:
        raise HTTPException(400, f"range must be one of {list(RANGES)}")
    t = now()
    d = STATE["scored"][(STATE["scored"].server == server) & (STATE["scored"].timestamp > t - pd.Timedelta(minutes=RANGES[range])) & (STATE["scored"].timestamp <= t)]
    if d.empty:
        raise HTTPException(404, "no data in range")
    step = max(1, len(d) // 400)
    pts = d.iloc[::step]
    wins = [AnomalyWindow(start=e["start"].to_pydatetime(), end=e["end"].to_pydatetime(), score=round(e["score"], 2))
            for e in runs(d)]
    f = STATE["live"][(STATE["live"].server == server) & (STATE["live"].timestamp > t - pd.Timedelta(minutes=RANGES[range])) & (STATE["live"].timestamp <= t)]
    f = f.iloc[::max(1, len(f) // 200)]
    forecast = [ForecastPoint(t=(r.timestamp + pd.Timedelta(minutes=30)).to_pydatetime(), value=round(float(r.pred), 1))
                for r in f.itertuples()] if metric == "cpu" else []
    return MetricResponse(server=server, metric=metric, range=range, current=round(float(d[metric].iloc[-1]), 1),
                          threshold=float(CPU_THRESHOLD) if metric == "cpu" else None,
                          points=[MetricPoint(t=r.timestamp.to_pydatetime(), value=round(float(getattr(r, metric)), 2),
                                              score=round(float(r.anomaly_score), 2), flagged=bool(r.if_flag))
                                  for r in pts.itertuples()],
                          anomalies=wins, forecast=forecast)


@app.get("/anomalies", response_model=AnomalyResponse)
def anomalies():
    t = now()
    d = STATE["scored"][(STATE["scored"].timestamp > t - pd.Timedelta(hours=24)) & (STATE["scored"].timestamp <= t)]
    out = [AnomalyEvent(server=e["server"], start=e["start"].to_pydatetime(), end=e["end"].to_pydatetime(),
                        max_score=round(e["score"], 2), severity="HIGH" if e["score"] >= 0.9 else "MEDIUM",
                        reason=f"{e['server']}: abnormal behavior detected (score {e['score']:.2f})")
           for e in runs(d)]
    return AnomalyResponse(now=t.to_pydatetime(), events=out)


@app.get("/forecast", response_model=ForecastResponse)
def forecast(server: str):
    if server not in STATE["servers"]:
        raise HTTPException(404, "unknown server")
    t = now()
    last = STATE["live"][(STATE["live"].server == server) & (STATE["live"].timestamp <= t)].sort_values("timestamp").tail(1).iloc[0]
    daily = STATE["scored"][(STATE["scored"].server == server) & (STATE["scored"].timestamp <= t)].set_index("timestamp").disk.resample("1D").last().dropna()
    slope = float(np.polyfit(np.arange(len(daily.iloc[-7:])), daily.iloc[-7:].to_numpy(), 1)[0])
    days = (DISK_THRESHOLD - float(daily.iloc[-1])) / slope if slope > 0 else None
    f = STATE["live"][(STATE["live"].server == server) & (STATE["live"].timestamp > t - pd.Timedelta(hours=6)) & (STATE["live"].timestamp <= t)]
    f = f.iloc[::max(1, len(f) // 200)]
    pts = [ForecastPoint(t=(r.timestamp + pd.Timedelta(minutes=30)).to_pydatetime(), value=round(float(r.pred), 1))
           for r in f.itertuples()]
    return ForecastResponse(server=server, now=t.to_pydatetime(), cpu_now=round(float(last.cpu), 1),
                            forecast_30min=round(float(last.pred), 1),
                            minutes_to_90=time_to_cross(float(last.cpu), float(last.pred), CPU_THRESHOLD),
                            disk_now=round(float(daily.iloc[-1]), 1), disk_pct_per_day=round(slope, 3),
                            disk_days_to_90=round(float(days), 1) if days else None, points=pts)


@app.get("/alerts", response_model=AlertsResponse)
def alerts(limit: int = 50):
    t = now()
    d = STATE["live"][(STATE["live"].severity != "LOW") & (STATE["live"].timestamp <= t)].sort_values("timestamp", ascending=False).head(min(max(limit, 1), 500))
    out = [Alert(time=r.timestamp.to_pydatetime(), server=r.server,
                 metric="cpu" if (r.pred >= 80 or r.cpu >= 85) else "multivariate",
                 score=round(float(r.anomaly_score), 2), forecast_30min=round(float(r.pred), 1),
                 severity=r.severity, reason=r.reason)
           for r in d.itertuples()]
    return AlertsResponse(now=t.to_pydatetime(), alerts=out)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
