# PulseGrid — AI-Powered Infrastructure Anomaly Detection & Forecasting

MVP that learns each server's normal metric behavior, flags abnormal periods, forecasts CPU/disk, and serves a
replay-driven monitoring dashboard. Results are framed as "abnormal behavior detected", not attacks or root causes.

## Structure

```
backend/   data_gen.py features.py anomaly.py forecast.py risk.py api.py evaluate.py config.py
frontend/  Next.js App Router dashboard (overview, server detail, alerts, model evaluation)
results.md generated evaluation report (real test-set numbers)
```

## Backend

```bash
cd backend
pip install -r requirements.txt
python data_gen.py                 # 8 servers x 45 days, 1-min, labeled anomalies -> data/metrics.parquet
python anomaly.py                  # detector sanity check
python forecast.py                 # CPU/disk forecast comparison + time-to-threshold
python evaluate.py                 # writes ../results.md and backend/plots/server-02_test.png (~2 min)
uvicorn api:app --host 127.0.0.1 --port 8000
```

The API fits the models once at startup (~25-30 s) and serves them under a replay clock (60x, looping the test
period). Endpoints: `/health`, `/servers`, `/summary`, `/metrics?server=&metric=&range=`, `/anomalies`,
`/forecast?server=`, `/alerts`. CORS allows `http://localhost:3000`.

## Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000, expects the API at 127.0.0.1:8000
```

Set `NEXT_PUBLIC_API_URL` to point at another API origin. Polling is 5 s via SWR; no websockets.

## Notes

- Synthetic generator is seeded (`SEED=42`) and uses chronological 60/20/20 splits; features are per server and
  causal only.
- Disk uses a rolling 7-day linear trend; CPU uses XGBoost with lags/rolling features (naive and one small SARIMA
  comparison reported in `results.md`).
- Risk rules: HIGH at anomaly score >= 0.90 or CPU at/forecast above 90%; MEDIUM when flagged or CPU trending to 80%.
- Explanations: `explain.py` attributes each flag by re-scoring the row with one feature at a time reset to its
  normal value; the biggest score drops become the "main signal" text in the alert reason. Run `python explain.py`
  to print real examples from the test period.
- Known limitation: slow memory leaks are missed at the 0.5% false-positive operating point (details in results.md).
