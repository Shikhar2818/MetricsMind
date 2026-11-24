"use client";

import { useRouter } from "next/navigation";

import { StatusBadge } from "@/components/status-badge";
import { fmtDateTime, type Alert } from "@/lib/api";

export function AlertsTable({ alerts }: { alerts: Alert[] }) {
  const router = useRouter();
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[780px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-line text-left text-[10px] uppercase tracking-[0.12em] text-zinc-500">
            <th className="px-5 py-3 font-medium">Severity</th>
            <th className="px-5 py-3 font-medium">Server</th>
            <th className="px-5 py-3 font-medium">Signal</th>
            <th className="px-5 py-3 text-right font-medium">Score</th>
            <th className="px-5 py-3 text-right font-medium">CPU 30m</th>
            <th className="px-5 py-3 font-medium">Reason</th>
            <th className="px-5 py-3 text-right font-medium">Time</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((a) => (
            <tr
              key={`${a.server}-${a.time}`}
              onClick={() => router.push(`/servers/${a.server}`)}
              className="cursor-pointer border-b border-line/60 transition-colors last:border-0 hover:bg-white/[0.025]"
            >
              <td className="px-5 py-3">
                <StatusBadge severity={a.severity} />
              </td>
              <td className="px-5 py-3 font-mono text-xs text-zinc-300">{a.server}</td>
              <td className="px-5 py-3 text-xs text-zinc-400">
                {a.metric === "multivariate" ? "combined" : a.metric.toUpperCase()}
              </td>
              <td className="px-5 py-3 text-right font-mono text-xs tabular-nums text-zinc-200">
                {a.score.toFixed(2)}
              </td>
              <td className="px-5 py-3 text-right font-mono text-xs tabular-nums text-zinc-400">
                {a.forecast_30min.toFixed(1)}%
              </td>
              <td className="max-w-[340px] truncate px-5 py-3 text-xs text-muted" title={a.reason}>
                {a.reason}
              </td>
              <td className="whitespace-nowrap px-5 py-3 text-right font-mono text-[11px] text-zinc-500">
                {fmtDateTime(a.time)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
