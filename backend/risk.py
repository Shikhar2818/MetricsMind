import pandas as pd

from anomaly import detect
from config import CPU_THRESHOLD
from forecast import predict_cpu, time_to_cross


def assess(cpu, score, forecast, flagged, drivers=""):
    reasons = []
    if score >= 0.9:
        reasons.append(f"high anomaly score {score:.2f}")
    elif flagged:
        reasons.append(f"abnormal behavior flagged, score {score:.2f}")
    if forecast >= CPU_THRESHOLD:
        reasons.append(f"CPU forecast {forecast:.0f}% in ~{time_to_cross(cpu, forecast, CPU_THRESHOLD)} min")
    elif forecast >= 80:
        reasons.append(f"CPU trending to {forecast:.0f}%")
    if cpu >= CPU_THRESHOLD:
        reasons.append(f"CPU already {cpu:.0f}%")
    if drivers:
        reasons.append(f"main signal: {drivers}")
    if not reasons:
        return "LOW", "metrics within learned normal range"
    high = score >= 0.9 or forecast >= CPU_THRESHOLD or cpu >= CPU_THRESHOLD
    return ("HIGH" if high else "MEDIUM"), "; ".join(reasons)


def fleet_risk():
    scored, _ = detect()
    tests = pd.concat([t.assign(server=s) for s, t in predict_cpu().items()])
    cols = ["timestamp", "server", "anomaly_score", "if_flag", "drivers"]
    m = tests.merge(scored[scored.split == "test"][cols], on=["timestamp", "server"], how="inner")
    m[["severity", "reason"]] = m.apply(
        lambda r: pd.Series(assess(r.cpu, r.anomaly_score, r.pred, r.if_flag, r.drivers)), axis=1)
    return m


if __name__ == "__main__":
    m = fleet_risk()
    counts = m.severity.value_counts()
    print(f"risk over test period ({len(m):,} points):")
    print(pd.DataFrame({"points": counts, "share": (counts / len(m) * 100).round(2)}).to_string())

    print("\nHIGH / MEDIUM examples:")
    top = pd.concat([m[m.severity == "HIGH"].head(4), m[m.severity == "MEDIUM"].head(4)])
    print(top[["timestamp", "server", "cpu", "anomaly_score", "pred", "severity", "reason"]]
          .round(2).to_string(index=False))

    print("\nlatest snapshot per server:")
    last = m.sort_values("timestamp").groupby("server").tail(1)
    print(last[["server", "cpu", "anomaly_score", "pred", "severity", "reason"]].round(2).to_string(index=False))
