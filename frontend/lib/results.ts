export const fleet = {
  servers: 8,
  days: 45,
  anomalyTestPoints: 126_728,
  forecastTestPoints: 103_544,
  riskTestPoints: 99_778,
};

export const anomalyComparison = [
  { metric: "Precision", isolation: 0.695, baseline: 0.074 },
  { metric: "Recall", isolation: 0.459, baseline: 0.014 },
  { metric: "F1", isolation: 0.553, baseline: 0.023 },
];

export const detection = {
  eventsCaught: 24,
  eventsTotal: 26,
  medianDelay: 3.5,
  baselineCaught: 2,
  baselineEvents: 26,
  memoryLeakRecall: 0.01,
  memoryLeakCaught: 2,
  memoryLeakTotal: 3,
};

export const perTypeRecall = [
  { type: "cpu spike", recall: 0.62 },
  { type: "memory leak", recall: 0.01 },
  { type: "latency/error", recall: 0.96 },
  { type: "multivariate", recall: 0.6 },
  { type: "network burst", recall: 0.44 },
  { type: "disk fill", recall: 0.91 },
];

export const events = [
  { label: "Events detected", isolation: "24 / 26", baseline: "2 / 26" },
  { label: "Median delay", isolation: "3.5 min", baseline: "—" },
];

export const forecastByServer = [
  { server: "server-01", naive: 3.11, xgb: 2.15 },
  { server: "server-02", naive: 4.0, xgb: 2.72 },
  { server: "server-03", naive: 2.86, xgb: 1.92 },
  { server: "server-04", naive: 4.55, xgb: 3.19 },
  { server: "server-05", naive: 3.49, xgb: 2.3 },
  { server: "server-06", naive: 2.62, xgb: 1.86 },
  { server: "server-07", naive: 3.65, xgb: 3.13 },
  { server: "server-08", naive: 4.35, xgb: 2.98 },
];

export const forecastPooled = [
  { metric: "MAE", naive: 3.58, xgb: 2.53 },
  { metric: "RMSE", naive: 4.84, xgb: 3.54 },
];

export const diskComparison = [
  { horizon: "1 day", trend: 0.58, naive: 0.69 },
  { horizon: "3 days", trend: 1.64, naive: 2.05 },
  { horizon: "7 days", trend: 4.15, naive: 4.98 },
];

export const sarima = { naive: 1.2, sarima: 2.77, xgb: 2.08, note: "server-01 · 30-min grid" };

export const riskMix = [
  { label: "Low", value: 96.36, tone: "ok" },
  { label: "Medium", value: 3.16, tone: "warn" },
  { label: "High", value: 0.48, tone: "crit" },
];
