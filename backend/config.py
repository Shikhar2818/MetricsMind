from pathlib import Path

SEED = 42
N_DAYS = 45
START = "2026-10-07"
FREQ = "1min"
METRICS = ["cpu", "memory", "disk", "network", "latency", "error_rate"]
CPU_THRESHOLD = 90
DISK_THRESHOLD = 90
REPLAY_SPEED = 60  # simulated seconds per real second

BASE = Path(__file__).parent
DATA_PATH = BASE / "data" / "metrics.parquet"
PLOT_DIR = BASE / "plots"

# per-server normal profile: level, daily amplitude, noise, load-coupled bases
SERVERS = {
    "server-01": dict(cpu=26, amp=14, noise=2.6, mem=36, net=150, lat=16, disk=21, disk_rate=0.30),
    "server-02": dict(cpu=38, amp=20, noise=3.2, mem=48, net=240, lat=22, disk=34, disk_rate=0.15),
    "server-03": dict(cpu=48, amp=16, noise=2.2, mem=55, net=320, lat=26, disk=46, disk_rate=0.40),
    "server-04": dict(cpu=31, amp=11, noise=3.8, mem=42, net=180, lat=19, disk=28, disk_rate=0.20),
    "server-05": dict(cpu=57, amp=22, noise=2.8, mem=60, net=410, lat=31, disk=52, disk_rate=0.10),
    "server-06": dict(cpu=22, amp=9, noise=2.0, mem=30, net=110, lat=14, disk=18, disk_rate=0.05),
    "server-07": dict(cpu=44, amp=18, noise=3.0, mem=52, net=290, lat=24, disk=32, disk_rate=0.20),
    "server-08": dict(cpu=63, amp=24, noise=3.4, mem=68, net=460, lat=35, disk=57, disk_rate=0.05),
}
