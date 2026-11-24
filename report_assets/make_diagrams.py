"""Generate the design diagrams used in the mini-project report (final)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle, Circle

OUT = Path(__file__).resolve().parent
plt.rcParams["font.family"] = "DejaVu Sans"

NAVY = "#1F3864"
BLUE = "#2E5C9A"
INK = "#12233f"
GREY = "#4b5563"
LIGHT = "#EAF1FB"
AMBER = "#B45309"
AMBER_BG = "#FFF4E5"
GREEN = "#3F6212"
GREEN_BG = "#F0F7E6"
RED = "#B91C1C"
RED_BG = "#FDECEC"


PRINT_SCALE = 0.58  # canvas is authored at ~12 in; shrink to print width so labels stay legible
FONT_SCALE = 0.68    # labels were sized for the large canvas; scale them with it


def canvas(w=12, h=8):
    fig, ax = plt.subplots(figsize=(w * PRINT_SCALE, h * PRINT_SCALE))
    raw_text = ax.text

    def scaled_text(*args, **kwargs):
        if "fontsize" in kwargs:
            kwargs["fontsize"] = kwargs["fontsize"] * FONT_SCALE
        return raw_text(*args, **kwargs)

    ax.text = scaled_text
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, title, sub="", fc=LIGHT, ec=NAVY, fs=9.6, subfs=7.8, dashed=False, tc=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=0.6",
                                fc=fc, ec=ec, lw=1.3, linestyle="--" if dashed else "-"))
    if sub:
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center", fontsize=fs,
                fontweight="bold", color=tc)
        ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center", fontsize=subfs, color=GREY)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fs,
                fontweight="bold", color=tc)


def arrow(ax, p1, p2, label="", ls="-", color=NAVY, style="-|>", fs=7.2, off=(0, 1.2)):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=13, lw=1.15,
                                 color=color, linestyle=ls, shrinkA=2, shrinkB=2))
    if label:
        ax.text((p1[0] + p2[0]) / 2 + off[0], (p1[1] + p2[1]) / 2 + off[1], label,
                ha="center", va="bottom", fontsize=fs, color=GREY,
                bbox=dict(fc="white", ec="none", pad=0.6))


def elbow(ax, pts, label="", color=NAVY, label_at=None, fs=7.2):
    for a, b in zip(pts[:-1], pts[1:]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=1.15, solid_capstyle="round")
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=13, lw=1.15,
                                 color=color, shrinkA=0, shrinkB=2))
    if label:
        lx, ly = label_at if label_at else ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2)
        ax.text(lx, ly, label, ha="center", va="center", fontsize=fs, color=GREY,
                bbox=dict(fc="white", ec="none", pad=0.6))


def diamond(ax, cx, cy, w, h, text, fs=7.4):
    pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, fc=AMBER_BG, ec=AMBER, lw=1.2))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color="#7c2d12")


def save(fig, name):
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


# ------------------------------------------------------------------ architecture
def architecture():
    fig, ax = canvas(11.5, 8.4)
    x, w = 5, 56
    box(ax, x, 86, w, 10, "SYNTHETIC DATA LAYER",
        "data_gen.py  ·  8 servers × 45 days × 1 min  ·  6 metrics + injected labels")
    box(ax, x, 71, w, 10, "FEATURE ENGINEERING",
        "features.py  ·  68 causal features: rolling mean/std, deltas, deviations, hour encoding")
    box(ax, 5, 48, 27, 14, "ANOMALY DETECTION",
        "Isolation Forest per server\n200 trees\n99.5th percentile threshold", subfs=7.4)
    box(ax, 34, 48, 27, 14, "FORECASTING",
        "CPU: XGBoost, +30 min\nDisk: 7-day linear trend\n% per day, days to 90%", subfs=7.4)
    box(ax, x, 35, w, 9, "RISK ENGINE",
        "risk.py  ·  LOW / MEDIUM / HIGH + a short reason sentence")
    box(ax, x, 21, w, 9, "FASTAPI SERVICE",
        "api.py  ·  7 REST endpoints  ·  60× replay clock  ·  CORS for the dashboard")
    box(ax, x, 7, w, 10, "NEXT.JS DASHBOARD",
        "Overview  ·  Server detail  ·  Alerts  ·  Model evaluation")

    box(ax, 68, 35, 27, 28, "OFFLINE EVALUATION",
        "evaluate.py\n\nprecision / recall / F1\nevent detection\nMAE / RMSE\nrisk distribution",
        fc="#F7F7F7", ec="#6B7280", dashed=True, fs=8.8, subfs=7.2, tc="#374151")

    arrow(ax, (33, 86), (33, 81))
    arrow(ax, (33, 71), (33, 66.2), style="-")
    ax.plot([18.5, 47.5], [66.2, 66.2], color=NAVY, lw=1.15)
    arrow(ax, (18.5, 66.2), (18.5, 62))
    arrow(ax, (47.5, 66.2), (47.5, 62))
    arrow(ax, (18.5, 48), (29, 45.2))
    arrow(ax, (47.5, 48), (38, 45.2))
    arrow(ax, (33, 35), (33, 30))
    arrow(ax, (33, 21), (33, 17))

    arrow(ax, (61, 58), (68, 55), ls=(0, (4, 3)), color="#6B7280", style="-|>")
    arrow(ax, (61, 52), (68, 50), ls=(0, (4, 3)), color="#6B7280", style="-|>")
    ax.text(64.5, 66.0, "held-out test data", fontsize=6.6, color="#6B7280", ha="center", va="bottom")
    save(fig, "fig_architecture.png")


# ------------------------------------------------------------------ use case
def usecase():
    fig, ax = canvas(12, 8)

    def actor(cx, cy, label, y_text):
        ax.add_patch(Circle((cx, cy + 8), 2.1, fill=False, lw=1.5, color=INK))
        ax.plot([cx, cx], [cy + 5.9, cy - 2], color=INK, lw=1.5)
        ax.plot([cx - 5, cx + 5], [cy + 2, cy + 2], color=INK, lw=1.5)
        ax.plot([cx, cx - 4], [cy - 2, cy - 9], color=INK, lw=1.5)
        ax.plot([cx, cx + 4], [cy - 2, cy - 9], color=INK, lw=1.5)
        ax.text(cx, y_text, label, ha="center", va="top", fontsize=9, fontweight="bold", color=INK)

    actor(9, 62, "Operations\nEngineer", 48)
    actor(9, 18, "Evaluator", 4)

    ax.add_patch(Rectangle((24, 8), 72, 88, fill=False, ec=NAVY, lw=1.3))
    ax.text(60, 92.5, "PulseGrid Monitoring System", ha="center", va="center",
            fontsize=9.5, fontweight="bold", color=NAVY)

    def uc(cx, cy, text, w=28, h=9):
        ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.2,rounding_size=3.2",
                                    fc=LIGHT, ec=BLUE, lw=1.2))
        ax.text(cx, cy, text, ha="center", va="center", fontsize=8.4, color=INK)

    uc(44, 78, "View fleet overview")
    uc(44, 62, "Inspect server metrics\nand forecast", w=27)
    uc(44, 46, "Filter and sort alerts")
    uc(44, 30, "Review model evaluation")
    uc(79, 62, "Open server\nfrom an alert", w=22, h=10)

    for y in (78, 62, 46):
        ax.plot([19, 30], [y, y], color="#4B5563", lw=1.0)
    ax.plot([19, 30], [14, 30], color="#4B5563", lw=1.0)

    ax.add_patch(FancyArrowPatch((68, 62), (57.5, 62), arrowstyle="-|>", mutation_scale=11,
                                 lw=1.0, color=AMBER, linestyle=(0, (4, 3))))
    ax.text(62.7, 63.6, "«extend»", fontsize=7, color=AMBER, ha="center", va="bottom")

    ax.text(60, 3.6, "Both actors use the same web dashboard; the evaluator only needs the read-only model page.",
            fontsize=7, color=GREY, ha="center")
    save(fig, "fig_usecase.png")


# ------------------------------------------------------------------ class
def classdiagram():
    fig, ax = canvas(13, 8.4)

    def cls(x, y, w, name, attrs, methods):
        line = 3.2
        h = 6 + len(attrs) * line + 5 + len(methods) * line + 5
        ax.add_patch(Rectangle((x, y), w, h, fc="white", ec=NAVY, lw=1.2))
        ax.add_patch(Rectangle((x, y + h - 6), w, 6, fc=LIGHT, ec=NAVY, lw=1.2))
        ax.text(x + w / 2, y + h - 3, name, ha="center", va="center", fontsize=8.4,
                fontweight="bold", color=INK)
        sep = y + h - 6 - len(attrs) * line - 4.5
        ax.plot([x, x + w], [sep, sep], color=NAVY, lw=0.8)
        for i, a in enumerate(attrs):
            ax.text(x + 1.4, y + h - 8.8 - i * line, a, fontsize=6.6, color="#1f2937", va="top")
        for i, m in enumerate(methods):
            ax.text(x + 1.4, sep - 3.4 - i * line, m, fontsize=6.6, color="#1f2937", va="top")
        return h

    cls(2, 61, 30, "AnomalyDetector",
        ["- threshold: float", "- model: IsolationForest", "- features: list[str]"],
        ["+ fit(train): void", "+ score(row): float", "+ is_flagged(score): bool"])
    cls(36, 61, 30, "Forecaster",
        ["- cpu_model: XGBRegressor", "- disk_window_days: int"],
        ["+ predict_cpu(df): float", "+ disk_slope(df): float", "+ days_to_threshold(): float"])
    cls(70, 61, 28, "RiskEngine",
        ["- cpu_limit = 90", "- high_score = 0.90", "- medium_cpu = 80"],
        ["+ assess(cpu, score, fc, flag)", "+ reason(): str"])

    cls(2, 19, 30, "ServerStatus",
        ["- server: str", "- metric[6]: float", "- anomaly_score: float", "- severity: Severity"],
        ["+ is_flagged(): bool", "+ to_json(): dict"])
    cls(36, 19, 30, "Alert",
        ["- time: datetime", "- server: str", "- signal: str", "- score: float", "- reason: str"],
        ["+ severity(): Severity", "+ to_row(): dict"])
    cls(70, 19, 28, "APIService",
        ["- scored: DataFrame", "- live: DataFrame", "- replay_speed = 60"],
        ["+ servers(): JSON", "+ metrics(range): JSON", "+ alerts(limit): JSON"])

    def rel(x1, y1, x2, y2, label):
        ax.plot([x1, x2], [y1, y2], color="#4B5563", lw=1.0)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 2.2, label, fontsize=6.4, color=GREY,
                ha="center", va="bottom", bbox=dict(fc="white", ec="none", pad=0.4))

    rel(32, 78, 36, 78, "1 uses 1")
    rel(66, 78, 70, 78, "1 → 1")
    rel(17, 61, 17, 54.4, "produces *")
    rel(51, 61, 51, 57.6, "raises *")
    rel(84, 61, 84, 54.4, "serves *")

    ax.text(4, 4, "Classes mirror the Python modules in backend/;  * = many.", fontsize=7, color=GREY)
    save(fig, "fig_class.png")


# ------------------------------------------------------------------ ER
def er():
    fig, ax = canvas(13, 7.6)

    def entity(cx, cy, title, attrs, w=26):
        line = 3.2
        h = 6 + len(attrs) * line + 4
        x, y = cx - w / 2, cy - h / 2
        ax.add_patch(Rectangle((x, y), w, h, fc="white", ec=NAVY, lw=1.2))
        ax.add_patch(Rectangle((x, y + h - 6), w, 6, fc=LIGHT, ec=NAVY, lw=1.2))
        ax.text(cx, y + h - 3, title, ha="center", va="center", fontsize=8.4,
                fontweight="bold", color=INK)
        for i, a in enumerate(attrs):
            ax.text(x + 1.5, y + h - 8.8 - i * line, a, fontsize=6.5, color="#1f2937", va="top")
        return y, h

    s_y, s_h = entity(17, 74, "SERVER",
                      ["PK  server_id", "    role", "    cpu_base", "    memory_base", "    disk_rate"])
    m_y, m_h = entity(51, 74, "METRIC_READING",
                      ["PK  reading_id", "FK  server_id", "    timestamp", "    cpu / memory / disk",
                       "    network / latency / error", "    is_anomaly (label)"], w=30)
    e_y, e_h = entity(86, 74, "ANOMALY_EVENT",
                      ["PK  event_id", "FK  server_id", "    start_time", "    end_time", "    max_score", "    severity"])

    f_y, f_h = entity(35, 28, "FORECAST",
                      ["PK  forecast_id", "FK  server_id", "    origin_time", "    horizon_min", "    predicted_cpu", "    disk_days_to_90"], w=28)
    a_y, a_h = entity(72, 28, "ALERT",
                      ["PK  alert_id", "FK  server_id", "    time", "    score", "    severity", "    reason"], w=24)

    ax.plot([30, 36], [74, 74], color="#4B5563", lw=1.1)
    ax.text(31.2, 75.6, "1", fontsize=7.4, color=INK)
    ax.text(34.8, 75.6, "N", fontsize=7.4, color=INK)
    ax.plot([66, 74], [74, 74], color="#4B5563", lw=1.1)
    ax.text(67.2, 75.6, "1", fontsize=7.4, color=INK)
    ax.text(71.6, 75.6, "N", fontsize=7.4, color=INK)

    def diag(p1, p2, label):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#4B5563", lw=1.1)
        ax.text(p1[0] + 2.0, p1[1] - 2.6, "1", fontsize=7.4, color=INK)
        ax.text(p2[0] + 2.0, p2[1] + 2.2, "N", fontsize=7.4, color=INK)
        ax.text((p1[0] + p2[0]) / 2 + 4.5, (p1[1] + p2[1]) / 2, label, fontsize=6.6, color=GREY,
                ha="left", va="center", bbox=dict(fc="white", ec="none", pad=0.5))

    diag((46, m_y), (37, f_y + f_h), "derived from")
    diag((58, m_y), (62, a_y + a_h), "triggers")

    ax.text(4, 5, "Logical model: readings are stored in Parquet; events, forecasts and alerts are derived views held in memory.",
            fontsize=7.2, color=GREY)
    save(fig, "fig_er.png")


# ------------------------------------------------------------------ DFD
def dfd():
    fig, ax = canvas(12.4, 8)

    def proc(cx, cy, name, r=7.6):
        ax.add_patch(Circle((cx, cy), r, fc=LIGHT, ec=BLUE, lw=1.3))
        ax.text(cx, cy, name, ha="center", va="center", fontsize=7.4, color=INK, fontweight="bold")

    def store(cx, cy, name, w=24, h=8):
        ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc="#F7F7F7", ec="#6B7280", lw=1.1))
        ax.plot([cx - w / 2, cx - w / 2], [cy - h / 2, cy + h / 2], color="#6B7280", lw=2.4)
        ax.text(cx, cy, name, ha="center", va="center", fontsize=7.4, color="#374151")

    proc(34, 85, "1.0\nGenerate\ntelemetry")
    proc(34, 66, "2.0\nBuild\nfeatures")
    proc(34, 47, "3.0\nScore &\nforecast")
    proc(34, 28, "4.0\nAssess\nrisk")
    proc(34, 10, "5.0\nServe API")

    store(77, 85, "D1  metrics.parquet")
    store(77, 47, "D2  scored frame\n(in memory)")
    ax.add_patch(Rectangle((67, 6), 20, 9, fc="#EEF2F7", ec=INK, lw=1.2))
    ax.text(77, 10.5, "Operator /\nEvaluator", ha="center", va="center", fontsize=7.4, color=INK)

    arrow(ax, (34, 77.4), (34, 73.6), "raw rows", off=(-7, 0))
    arrow(ax, (34, 58.4), (34, 54.6), "feature vectors", off=(-11, 0))
    arrow(ax, (34, 39.4), (34, 35.6), "scores + flags", off=(-10, 0))
    arrow(ax, (34, 20.4), (34, 17.6), "verdicts", off=(-6, 0))

    arrow(ax, (41.6, 85), (65, 85), "write", off=(0, 1.0))
    elbow(ax, [(65, 81), (65, 70), (41.6, 70)], "read", label_at=(53, 71))
    arrow(ax, (41.6, 47), (65, 47), "store scores", off=(0, 1.0))
    elbow(ax, [(65, 43), (65, 32), (41.6, 32)], "scores", label_at=(53, 33))
    arrow(ax, (41.6, 10), (67, 10), "JSON responses", off=(0, 1.0))
    arrow(ax, (67, 14), (41.6, 14), "HTTP requests", off=(0, 1.0))

    ax.text(60, 95, "Processes are numbered; D1 and D2 are data stores.", fontsize=7, color=GREY)
    save(fig, "fig_dfd.png")


architecture()
usecase()
classdiagram()
er()
dfd()
