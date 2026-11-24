"use client";

import { BellOff } from "lucide-react";
import { useMemo, useState } from "react";
import useSWR from "swr";

import { AlertsTable } from "@/components/alerts-table";
import { ErrorState } from "@/components/error-state";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { fetcher, type AlertsResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function AlertsPage() {
  const { data, error, isLoading, mutate } = useSWR<AlertsResponse>("/alerts?limit=200", fetcher, {
    refreshInterval: 5000,
  });
  const [severity, setSeverity] = useState<"ALL" | "HIGH" | "MEDIUM">("ALL");
  const [server, setServer] = useState("ALL");
  const [sort, setSort] = useState<"time" | "score">("time");

  const servers = useMemo(() => [...new Set(data?.alerts.map((a) => a.server) ?? [])], [data]);
  const rows = useMemo(() => {
    let r = data?.alerts ?? [];
    if (severity !== "ALL") r = r.filter((a) => a.severity === severity);
    if (server !== "ALL") r = r.filter((a) => a.server === server);
    return [...r].sort((a, b) =>
      sort === "score" ? b.score - a.score : +new Date(b.time) - +new Date(a.time),
    );
  }, [data, severity, server, sort]);

  if (error) return <ErrorState message={error.message} onRetry={() => mutate()} />;

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-lg font-semibold tracking-tight">Alerts</h2>
        <p className="mt-0.5 text-xs text-muted">
          One row = a minute where a server behaved unlike its own normal. Click any row to open that server&apos;s
          charts.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value as typeof severity)}
          className="h-9 rounded-lg border border-line bg-ink-900 px-3 text-xs text-zinc-300 outline-none focus:border-accent/50"
        >
          <option value="ALL">All severities</option>
          <option value="HIGH">Critical</option>
          <option value="MEDIUM">Warning</option>
        </select>
        <select
          value={server}
          onChange={(e) => setServer(e.target.value)}
          className="h-9 rounded-lg border border-line bg-ink-900 px-3 text-xs text-zinc-300 outline-none focus:border-accent/50"
        >
          <option value="ALL">All servers</option>
          {servers.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <div className="ml-auto flex gap-1 rounded-lg border border-line bg-ink-900 p-1">
          {(["time", "score"] as const).map((key) => (
            <button
              key={key}
              onClick={() => setSort(key)}
              className={cn(
                "rounded-md px-2.5 py-1 text-[11px] transition-colors",
                sort === key ? "bg-white/[0.08] text-zinc-100" : "text-muted hover:text-zinc-200",
              )}
            >
              {key === "time" ? "Newest" : "Highest score"}
            </button>
          ))}
        </div>
      </div>

      <Card>
        {isLoading ? (
          <div className="space-y-3 p-5">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-9 w-full" />
            ))}
          </div>
        ) : rows.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 px-6 py-16 text-center">
            <BellOff className="h-6 w-6 text-zinc-600" />
            <p className="text-sm text-zinc-300">No alerts at this replay position</p>
            <p className="max-w-sm text-xs text-muted">
              {data?.alerts.length
                ? "No alerts match the current filters."
                : "Alerts appear as the replay feed reaches periods of abnormal behavior."}
            </p>
          </div>
        ) : (
          <AlertsTable alerts={rows} />
        )}
      </Card>
      <p className="text-[11px] text-zinc-600">{rows.length} alerts shown · auto-refresh every 5s</p>
    </div>
  );
}
