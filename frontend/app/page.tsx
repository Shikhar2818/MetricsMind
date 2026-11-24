"use client";

import { Activity, AlertTriangle, BellRing, Gauge, ShieldCheck } from "lucide-react";
import useSWR from "swr";

import { ErrorState } from "@/components/error-state";
import { KpiCard } from "@/components/kpi-card";
import { ServerCard } from "@/components/server-card";
import { Skeleton } from "@/components/ui/skeleton";
import { fetcher, type ServersResponse, type Summary } from "@/lib/api";

export default function OverviewPage() {
  const { data, error, isLoading, mutate } = useSWR<ServersResponse>("/servers", fetcher, {
    refreshInterval: 5000,
  });
  const { data: summary } = useSWR<Summary>("/summary", fetcher, { refreshInterval: 5000 });

  if (error) return <ErrorState message={error.message} onRetry={() => mutate()} />;

  if (isLoading || !data || !summary) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-5 w-56" />
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-52 w-full" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">Fleet overview</h2>
          <p className="mt-0.5 text-xs text-muted">
            {summary.total_servers} synthetic servers, each with its own learned idea of normal · sparklines show the
            last 2 hours
          </p>
        </div>
        <span className="flex items-center gap-1.5 text-[11px] text-zinc-500">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" />
          refreshing every 5s
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <KpiCard label="Healthy" value={summary.healthy} icon={ShieldCheck} tone="ok" hint="nothing to look at" />
        <KpiCard label="Warning" value={summary.warning} icon={AlertTriangle} tone="warn" hint="worth a look" />
        <KpiCard label="Critical" value={summary.critical} icon={BellRing} tone="crit" hint="act now" />
        <KpiCard
          label="Active anomalies"
          value={summary.active_anomalies}
          icon={Activity}
          tone="accent"
          hint="flagged at this replay moment"
        />
        <KpiCard
          label="Peak anomaly score"
          value={summary.highest_forecast_risk.toFixed(2)}
          icon={Gauge}
          tone="accent"
          hint={summary.highest_risk_server}
        />
      </div>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-medium text-zinc-300">Servers</h3>
            <span className="text-[11px] text-zinc-500">{data.servers.length} monitored</span>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {[...data.servers]
            .sort((a, b) => a.server.localeCompare(b.server))
            .map((s) => (
              <ServerCard key={s.server} server={s} />
            ))}
        </div>
      </section>
    </div>
  );
}
