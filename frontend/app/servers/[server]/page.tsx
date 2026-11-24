"use client";

import { ArrowLeft, Clock3, Gauge, HardDrive, Info, TrendingUp } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import useSWR from "swr";

import { ErrorState } from "@/components/error-state";
import { MetricChart } from "@/components/metric-chart";
import { StatusBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  fetcher,
  METRICS,
  RANGES,
  type ForecastResponse,
  type Metric,
  type MetricsResponse,
  type ServersResponse,
} from "@/lib/api";
import { METRIC_HELP, SERVER_PROFILES } from "@/lib/servers";
import { cn } from "@/lib/utils";

export default function ServerPage() {
  const { server } = useParams<{ server: string }>();
  const [metric, setMetric] = useState<Metric>("cpu");
  const [range, setRange] = useState("24h");

  const { data, error, isLoading, mutate } = useSWR<MetricsResponse>(
    `/metrics?server=${server}&metric=${metric}&range=${range}`,
    fetcher,
    { refreshInterval: 5000 },
  );
  const { data: fc } = useSWR<ForecastResponse>(`/forecast?server=${server}`, fetcher, { refreshInterval: 5000 });
  const { data: fleet } = useSWR<ServersResponse>("/servers", fetcher, { refreshInterval: 5000 });
  const status = fleet?.servers.find((s) => s.server === server);
  const meta = METRICS.find((m) => m.key === metric)!;
  const profile = SERVER_PROFILES[server];

  return (
    <div className="space-y-5">
      <div>
        <Link href="/" className="inline-flex items-center gap-1.5 text-xs text-muted transition-colors hover:text-zinc-200">
          <ArrowLeft className="h-3.5 w-3.5" /> Fleet
        </Link>
        <div className="mt-2 flex flex-wrap items-center gap-3">
          <h2 className="font-mono text-xl font-semibold tracking-tight">{server}</h2>
          {status && <StatusBadge severity={status.severity} />}
          {profile && (
            <span className="rounded-md border border-line px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-zinc-500">
              {profile.role}
            </span>
          )}
          {status && <span className="text-xs text-muted">{status.reason}</span>}
        </div>
      </div>

      <div className="flex flex-col gap-3 rounded-xl border border-line bg-ink-900 p-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-1">
          {METRICS.map((m) => (
            <button
              key={m.key}
              onClick={() => setMetric(m.key)}
              className={cn(
                "rounded-md px-2.5 py-1.5 text-xs transition-colors",
                metric === m.key
                  ? "bg-accent/15 text-accent-soft ring-1 ring-inset ring-accent/25"
                  : "text-muted hover:bg-white/5 hover:text-zinc-200",
              )}
            >
              {m.label}
            </button>
          ))}
        </div>
        <div className="flex gap-1 rounded-lg bg-ink-950 p-1 ring-1 ring-inset ring-line">
          {RANGES.map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={cn(
                "rounded-md px-2.5 py-1 text-[11px] transition-colors",
                range === r ? "bg-white/[0.08] text-zinc-100" : "text-muted hover:text-zinc-200",
              )}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {error ? (
        <ErrorState message={error.message} onRetry={() => mutate()} />
      ) : isLoading || !data ? (
        <Skeleton className="h-[430px] w-full" />
      ) : (
        <Card>
          <CardHeader className="items-end">
            <div>
              <CardTitle>
                {meta.label} <span className="font-normal text-zinc-500">· last {range}</span>
              </CardTitle>
              <p className="mt-1 text-[11px] text-zinc-400">{METRIC_HELP[metric]}</p>
              <p className="mt-0.5 text-[10px] text-zinc-600">
                red dots = flagged anomalies · shaded = detected abnormal periods
                {metric === "cpu" ? " · dashed = +30 min forecast" : ""}
              </p>
            </div>
            <div className="text-right">
              <div className="font-mono text-lg tabular-nums text-zinc-100">
                {data.current.toFixed(1)}
                <span className="ml-0.5 text-xs text-zinc-500">{meta.unit}</span>
              </div>
              <div className="text-[10px] uppercase tracking-wider text-zinc-500">current</div>
            </div>
          </CardHeader>
          <CardContent>
            <MetricChart
              metric={metric}
              points={data.points}
              forecast={data.forecast}
              anomalies={data.anomalies}
              range={range}
              threshold={data.threshold}
            />
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>CPU outlook</CardTitle>
            <TrendingUp className="h-3.5 w-3.5 text-accent-soft" />
          </CardHeader>
          <CardContent>
            <div className="font-mono text-2xl tabular-nums">
              {fc ? `${fc.forecast_30min.toFixed(1)}%` : "—"}
              <span className="ml-1 text-xs font-normal text-zinc-500">in 30 min</span>
            </div>
            <p className={cn("mt-2 text-xs", fc?.minutes_to_90 != null ? "text-warn" : "text-muted")}>
              {fc?.minutes_to_90 != null
                ? `Threshold crossing in ~${fc.minutes_to_90} min`
                : "No 90% threshold crossing in the next 30 min"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Disk capacity</CardTitle>
            <HardDrive className="h-3.5 w-3.5 text-zinc-500" />
          </CardHeader>
          <CardContent>
            <div className="font-mono text-2xl tabular-nums">
              {fc ? `${fc.disk_now.toFixed(1)}%` : "—"}
              <span className="ml-1 text-xs font-normal text-zinc-500">used</span>
            </div>
            <p className={cn("mt-2 text-xs", (fc?.disk_days_to_90 ?? 99) < 14 ? "text-warn" : "text-muted")}>
              {fc?.disk_days_to_90 != null
                ? `Reaches 90% in ~${fc.disk_days_to_90.toFixed(0)} days at ${fc.disk_pct_per_day.toFixed(2)} pct/day`
                : "No growth trend detected"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Detection</CardTitle>
            <Gauge className="h-3.5 w-3.5 text-zinc-500" />
          </CardHeader>
          <CardContent>
            <div className="font-mono text-2xl tabular-nums">
              {status ? status.anomaly_score.toFixed(2) : "—"}
              <span className="ml-1 text-xs font-normal text-zinc-500">score</span>
            </div>
            <p className="mt-2 flex items-center gap-1.5 text-xs text-muted">
              <Clock3 className="h-3 w-3" />
              {status ? (status.flagged ? "abnormal behavior at current time" : "no abnormal behavior now") : "—"}
            </p>
          </CardContent>
        </Card>
      </div>

      {profile && (
        <Card>
          <CardHeader>
            <CardTitle>About {server}</CardTitle>
            <Info className="h-3.5 w-3.5 text-zinc-500" />
          </CardHeader>
          <CardContent className="grid gap-4 pt-0 text-[11px] leading-relaxed sm:grid-cols-3">
            <div>
              <div className="text-[10px] uppercase tracking-wider text-zinc-500">What it is</div>
              <p className="mt-1 text-zinc-400">{profile.summary}</p>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-wider text-zinc-500">Normal day (before incidents)</div>
              <p className="mt-1 text-zinc-400">{profile.normalDay}</p>
            </div>
            <div>
              <div className="text-[10px] uppercase tracking-wider text-zinc-500">What the data shows</div>
              <p className="mt-1 text-zinc-400">{profile.watch}</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
