export type Severity = "LOW" | "MEDIUM" | "HIGH";
export type Metric = "cpu" | "memory" | "disk" | "network" | "latency" | "error_rate";

export interface Health {
  status: string;
  now: string;
  replay_speed: number;
  data_start: string;
  data_end: string;
  servers: number;
}

export interface ServerStatus {
  server: string;
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  latency: number;
  error_rate: number;
  anomaly_score: number;
  forecast_30min: number | null;
  severity: Severity;
  reason: string;
  flagged: boolean;
  sparklines: Record<string, number[]>;
}

export interface ServersResponse {
  now: string;
  servers: ServerStatus[];
}

export interface Summary {
  now: string;
  total_servers: number;
  healthy: number;
  warning: number;
  critical: number;
  active_anomalies: number;
  highest_forecast_risk: number;
  highest_risk_server: string;
}

export interface MetricPoint {
  t: string;
  value: number;
  score: number;
  flagged: boolean;
}

export interface ForecastPoint {
  t: string;
  value: number;
}

export interface AnomalyWindow {
  start: string;
  end: string;
  score: number;
}

export interface MetricsResponse {
  server: string;
  metric: Metric;
  range: string;
  current: number;
  threshold: number | null;
  points: MetricPoint[];
  anomalies: AnomalyWindow[];
  forecast: ForecastPoint[];
}

export interface AnomalyEvent {
  server: string;
  start: string;
  end: string;
  max_score: number;
  severity: Severity;
  reason: string;
}

export interface AnomaliesResponse {
  now: string;
  events: AnomalyEvent[];
}

export interface ForecastResponse {
  server: string;
  now: string;
  cpu_now: number;
  forecast_30min: number;
  minutes_to_90: number | null;
  disk_now: number;
  disk_pct_per_day: number;
  disk_days_to_90: number | null;
  points: ForecastPoint[];
}

export interface Alert {
  time: string;
  server: string;
  metric: string;
  score: number;
  forecast_30min: number;
  severity: Severity;
  reason: string;
}

export interface AlertsResponse {
  now: string;
  alerts: Alert[];
}

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function fetcher<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error((await res.json().catch(() => null))?.detail ?? res.statusText);
  return (await res.json()) as T;
}

export const METRICS: { key: Metric; label: string; unit: string }[] = [
  { key: "cpu", label: "CPU", unit: "%" },
  { key: "memory", label: "Memory", unit: "%" },
  { key: "disk", label: "Disk", unit: "%" },
  { key: "network", label: "Network", unit: "MB/s" },
  { key: "latency", label: "Latency", unit: "ms" },
  { key: "error_rate", label: "Error rate", unit: "%" },
];

export const RANGES = ["1h", "6h", "24h", "3d", "7d"];

export const fmtTime = (iso: string) =>
  new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });

export const fmtDateTime = (iso: string) =>
  new Date(iso).toLocaleString([], { month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit" });

export const fmtShort = (iso: string) =>
  new Date(iso).toLocaleString([], { month: "short", day: "2-digit", hour: "2-digit", minute: "2-digit" });
