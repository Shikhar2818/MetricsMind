import type { Metric } from "@/lib/api";

export interface ServerProfile {
  role: string;
  summary: string;
  normalDay: string;
  watch: string;
}

/**
 * Plain-language profiles for the eight synthetic servers.
 * Numbers come from backend/config.py (baseline) and the 45-day injected incident log.
 */
export const SERVER_PROFILES: Record<string, ServerProfile> = {
  "server-01": {
    role: "Quiet lightweight node",
    summary:
      "One of the two lightest machines: low CPU, memory and traffic. It received two injected disk-fill incidents, so its disk grows the fastest.",
    normalDay:
      "CPU ~26% (daily swing ±14) · memory ~36% · network ~150 MB/s · latency ~16 ms · disk starts at ~21%",
    watch:
      "Disk is the story: the two fills take it from ~21% to ~72% over 45 days. CPU itself rarely leaves the 10–40% band.",
  },
  "server-02": {
    role: "Medium app load",
    summary:
      "A middle-of-the-road workload with a strong day/night rhythm. No disk fill was injected, so its disk grows slowly.",
    normalDay:
      "CPU ~38% (daily swing ±20) · memory ~48% · network ~240 MB/s · latency ~22 ms · disk starts at ~34%",
    watch:
      "CPU spikes reach ~87%. Disk ends near 51%, so capacity is not a near-term risk on this machine.",
  },
  "server-03": {
    role: "Steady busy worker",
    summary:
      "Consistently busy and smooth: high baseline CPU and memory but the least noisy readings, which makes real deviations easier to spot.",
    normalDay:
      "CPU ~48% (daily swing ±16) · memory ~55% · network ~320 MB/s · latency ~26 ms · disk starts at ~46%",
    watch:
      "No injected disk fill, but steady growth takes disk to ~70% by day 45. CPU spikes touch 100%.",
  },
  "server-04": {
    role: "Low load, noisy readings",
    summary:
      "Low average CPU but the jumpiest signal in the fleet. Noise makes normal minutes look stranger, so this server is the most likely source of false alarms.",
    normalDay:
      "CPU ~31% (daily swing ±11) · memory ~42% · network ~180 MB/s · latency ~19 ms · disk starts at ~28%",
    watch:
      "It received two injected disk fills (disk ends near ~76%). Expect more detector noise here than on most servers.",
  },
  "server-05": {
    role: "High-load app node",
    summary:
      "A busy machine with high CPU, memory, network and latency. Its CPU spikes reach 100%, the condition a fixed 90% alarm is meant to catch.",
    normalDay:
      "CPU ~57% (daily swing ±22) · memory ~60% · network ~410 MB/s · latency ~31 ms · disk starts at ~52%",
    watch:
      "CPU is the metric to watch: the baseline already sits in the high 50s and spikes hit 100%. No disk fill was injected.",
  },
  "server-06": {
    role: "Lightweight edge node",
    summary:
      "The quietest machine in the fleet: lowest CPU, memory and traffic. Useful as the calm baseline against the busier servers.",
    normalDay:
      "CPU ~22% (daily swing ±9) · memory ~30% · network ~110 MB/s · latency ~14 ms · disk starts at ~18%",
    watch:
      "Almost nothing dramatic happens here: disk ends near 32% and CPU stays below ~64%. It should mostly stay LOW risk.",
  },
  "server-07": {
    role: "Busy worker with disk pressure",
    summary:
      "A medium-high workload that also received two injected disk fills, making it the closest thing to a capacity incident in the fleet.",
    normalDay:
      "CPU ~44% (daily swing ±18) · memory ~52% · network ~290 MB/s · latency ~24 ms · disk starts at ~32%",
    watch:
      "Disk climbs from ~32% to ~79%, and CPU spikes touch 100%. This is the server to open when studying disk alerts.",
  },
  "server-08": {
    role: "Heaviest batch node",
    summary:
      "The busiest machine: highest CPU, memory, network and latency. Its normal level is already near the fixed 90% CPU alarm, which explains many of that baseline's false flags.",
    normalDay:
      "CPU ~63% (daily swing ±24) · memory ~68% · network ~460 MB/s · latency ~35 ms · disk starts at ~57%",
    watch:
      "CPU spikes hit 100% and its baseline sits in the 60s, so it dominates HIGH-risk counts. No disk fill was injected.",
  },
};

export const METRIC_HELP: Record<Metric, string> = {
  cpu: "How much of the processor is busy (%). Injected CPU spikes push this up within minutes.",
  memory: "RAM in use (%). A memory leak looks like a slow, steady climb rather than a jump.",
  disk: "Disk used (%). It only goes up, so a fill is a slow countdown toward 90%.",
  network: "Traffic in MB/s. A network burst is a sudden jump, often 4–6× normal.",
  latency: "Request response time (ms). Stress shows up here before failures do.",
  error_rate: "Share of failed requests (%). It usually follows latency upward.",
};
