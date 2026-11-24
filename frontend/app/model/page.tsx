"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { KpiCard } from "@/components/kpi-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  anomalyComparison,
  detection,
  diskComparison,
  events,
  fleet,
  forecastByServer,
  forecastPooled,
  perTypeRecall,
  riskMix,
  sarima,
} from "@/lib/results";
import { Activity, BarChart3, Target, TrendingUp } from "lucide-react";

const chartTooltip = {
  background: "#12151c",
  border: "1px solid #1e2430",
  borderRadius: 8,
  fontSize: 12,
  color: "#e4e4e7",
};

const axis = { fill: "#7d8699", fontSize: 11 };

const guide = [
  {
    term: "Anomaly score (0–1)",
    text: "Every minute gets a score for how unlike that server's own normal it looks. 0.9+ counts as HIGH risk; ordinary minutes sit around 0.1–0.3.",
  },
  {
    term: "Precision 0.70",
    text: "About 7 in 10 flags were real. The fixed CPU>90 rule is far less precise (0.07) because several busy servers sit near 90% while still missing most incidents.",
  },
  {
    term: "Recall 0.46",
    text: "Of all truly abnormal minutes, it caught about 46%, and 24 of the 26 injected incidents at some point. It misses subtle changes.",
  },
  {
    term: "F1 0.55",
    text: "One score balancing precision and recall (1.0 is perfect, 0 is useless). The CPU>90 rule scores 0.02, so the learned model is the better all-round detector.",
  },
  {
    term: "Events caught / delay",
    text: "An incident counts as caught if at least one of its minutes is flagged. The detector caught 24 of 26, typically 3.5 minutes after the incident started.",
  },
  {
    term: "MAE / RMSE",
    text: "Forecast error in CPU percentage points, 30 minutes ahead. MAE 2.53 means a typical miss of ~2.5 points; RMSE 3.54 punishes large misses more (naive: 3.58 / 4.84).",
  },
  {
    term: "Risk levels",
    text: "LOW = nothing to look at, MEDIUM = worth a look, HIGH = score above 0.9 or CPU at/forecast above 90%. Of the test minutes, 96.4% were LOW, 3.2% MEDIUM and 0.48% HIGH.",
  },
  {
    term: "Why the memory leak is missed",
    text: "It caught only ~1% of leak minutes and 2 of 3 leaks: the slow climb overlaps normal daytime memory, so it hides under the false-alarm budget.",
  },
];

export default function ModelPage() {
  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold tracking-tight">Model evaluation</h2>
        <p className="mt-0.5 text-xs text-muted">
          The detector and forecasters are scored on the last 25% of each server&apos;s history, which they never saw
          while learning · {fleet.servers} servers × {fleet.days} days · from{" "}
          <span className="font-mono text-zinc-400">backend/evaluate.py</span>
        </p>
      </div>

      <div className="rounded-xl border border-accent/25 bg-accent/[0.06] px-4 py-3 text-xs leading-relaxed text-zinc-300">
        <span className="font-medium text-zinc-100">Short version:</span> the learned detector catches 24 of 26
        incidents, typically 3.5 minutes after they start, and about 7 in 10 of its flags are real. Forecasts beat the
        naive baseline on all eight servers; the slow memory leak remains the blind spot.
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <KpiCard label="Detector F1" value="0.553" icon={BarChart3} tone="accent" hint="0 worst, 1 perfect · CPU>90 rule: 0.02" />
        <KpiCard label="XGBoost MAE" value="2.53" icon={TrendingUp} tone="ok" hint="typical miss: 2.5 CPU points, 30 min out" />
        <KpiCard
          label="Events detected"
          value={`${detection.eventsCaught} / ${detection.eventsTotal}`}
          icon={Target}
          tone="accent"
          hint={`${detection.medianDelay} min median delay`}
        />
        <KpiCard
          label="Slow leak recall"
          value={detection.memoryLeakRecall.toFixed(2)}
          icon={Activity}
          tone="warn"
          hint={`${detection.memoryLeakCaught} of ${detection.memoryLeakTotal} leaks caught · ~1% of leak minutes`}
        />
      </div>

      <Card>
        <CardHeader>
          <div>
            <CardTitle>How to read these numbers</CardTitle>
            <p className="mt-0.5 text-[11px] text-muted">Plain-language guide to every score on this page</p>
          </div>
        </CardHeader>
        <CardContent className="grid gap-x-6 gap-y-4 pt-0 sm:grid-cols-2">
          {guide.map((g) => (
            <div key={g.term}>
              <div className="text-[11px] font-medium text-zinc-200">{g.term}</div>
              <p className="mt-1 text-[11px] leading-relaxed text-zinc-500">{g.text}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Learned detector vs fixed CPU alarm</CardTitle>
              <p className="mt-0.5 text-[11px] text-muted">
                Isolation Forest vs &quot;warn when CPU is over 90%&quot; · 0–1, higher is better
              </p>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={anomalyComparison} barGap={8}>
                <CartesianGrid stroke="#1e2430" vertical={false} />
                <XAxis dataKey="metric" tick={axis} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 1]} tick={axis} axisLine={false} tickLine={false} width={34} />
                <Tooltip contentStyle={chartTooltip} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                <Legend wrapperStyle={{ fontSize: 11, color: "#8b93a7" }} />
                <Bar dataKey="isolation" name="Isolation Forest" fill="#3b82f6" radius={[4, 4, 0, 0]} isAnimationActive={false} />
                <Bar dataKey="baseline" name="CPU>90" fill="#3f4654" radius={[4, 4, 0, 0]} isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-3 grid grid-cols-2 gap-2 text-[11px]">
              {events.map((e) => (
                <div key={e.label} className="rounded-lg border border-line bg-ink-950/60 px-3 py-2">
                  <div className="text-zinc-500">{e.label}</div>
                  <div className="mt-0.5 font-mono text-zinc-200">
                    {e.isolation} <span className="text-zinc-600">vs {e.baseline}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Catch rate by failure type</CardTitle>
              <p className="mt-0.5 text-[11px] text-muted">Recall · 1.0 = every abnormal minute caught</p>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={perTypeRecall} layout="vertical" margin={{ left: 8, right: 12 }}>
                <CartesianGrid stroke="#1e2430" horizontal={false} />
                <XAxis type="number" domain={[0, 1]} tick={axis} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="type" width={106} tick={axis} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={chartTooltip} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                <Bar dataKey="recall" name="Recall" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={16} isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Forecast accuracy · CPU 30 min</CardTitle>
              <p className="mt-0.5 text-[11px] text-muted">
                Average CPU %-point error over {fleet.forecastTestPoints.toLocaleString()} test points · lower is better
              </p>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={forecastPooled} barGap={8}>
                <CartesianGrid stroke="#1e2430" vertical={false} />
                <XAxis dataKey="metric" tick={axis} axisLine={false} tickLine={false} />
                <YAxis tick={axis} axisLine={false} tickLine={false} width={34} />
                <Tooltip contentStyle={chartTooltip} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                <Legend wrapperStyle={{ fontSize: 11, color: "#8b93a7" }} />
                <Bar dataKey="naive" name="Naive" fill="#3f4654" radius={[4, 4, 0, 0]} isAnimationActive={false} />
                <Bar dataKey="xgb" name="XGBoost" fill="#3b82f6" radius={[4, 4, 0, 0]} isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-3 flex items-center justify-between rounded-lg border border-line bg-ink-950/60 px-3 py-2 text-[11px]">
              <span className="text-zinc-500">{sarima.note}</span>
              <span className="font-mono text-zinc-300">
                naive {sarima.naive.toFixed(2)} · SARIMA {sarima.sarima.toFixed(2)} · XGB {sarima.xgb.toFixed(2)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Forecast error per server</CardTitle>
              <p className="mt-0.5 text-[11px] text-muted">MAE · XGBoost beats the naive baseline on all five</p>
            </div>
          </CardHeader>
          <CardContent className="pt-2">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-line text-left text-[10px] uppercase tracking-wider text-zinc-500">
                  <th className="py-2 font-medium">Server</th>
                  <th className="py-2 text-right font-medium">Naive</th>
                  <th className="py-2 text-right font-medium">XGBoost</th>
                  <th className="py-2 text-right font-medium">Delta</th>
                </tr>
              </thead>
              <tbody>
                {forecastByServer.map((r) => (
                  <tr key={r.server} className="border-b border-line/50 last:border-0">
                    <td className="py-2 font-mono text-zinc-300">{r.server}</td>
                    <td className="py-2 text-right font-mono text-zinc-500">{r.naive.toFixed(2)}</td>
                    <td className="py-2 text-right font-mono text-zinc-200">{r.xgb.toFixed(2)}</td>
                    <td className="py-2 text-right font-mono text-ok">
                      {(((r.xgb - r.naive) / r.naive) * 100).toFixed(0)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Disk forecast error</CardTitle>
              <p className="mt-0.5 text-[11px] text-muted">MAE in disk % points · trend model vs assuming no change</p>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-2">
              {diskComparison.map((d) => (
                <div key={d.horizon} className="rounded-lg border border-line bg-ink-950/60 p-3">
                  <div className="text-[10px] uppercase tracking-wider text-zinc-500">{d.horizon}</div>
                  <div className="mt-1 font-mono text-lg text-zinc-100">{d.trend.toFixed(2)}</div>
                  <div className="text-[11px] text-zinc-500">naive {d.naive.toFixed(2)}</div>
                </div>
              ))}
            </div>
            <p className="mt-3 text-[11px] leading-relaxed text-muted">
              The trend model has lower average error at every horizon (7 days: 4.15 vs 4.98), but RMSE is slightly
              worse at 3–7 days, so a few large misses remain.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Risk level distribution</CardTitle>
              <p className="mt-0.5 text-[11px] text-muted">
                Share of {fleet.riskTestPoints.toLocaleString()} test minutes at each level
              </p>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 pt-1">
              {riskMix.map((r) => (
                <div key={r.label}>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-zinc-400">{r.label}</span>
                    <span className="font-mono text-zinc-300">{r.value.toFixed(2)}%</span>
                  </div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
                    <div
                      className={r.tone === "ok" ? "h-full bg-ok" : r.tone === "warn" ? "h-full bg-warn" : "h-full bg-crit"}
                      style={{ width: `${Math.max(r.value, 1)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <p className="mt-4 text-[11px] leading-relaxed text-zinc-500">
              The memory leak is the blind spot: only ~1% of leak minutes and 2 of 3 leaks were caught, because its
              level overlaps normal daytime memory.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
