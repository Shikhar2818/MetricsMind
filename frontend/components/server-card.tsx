import { ArrowUpRight, Server } from "lucide-react";
import Link from "next/link";

import { Sparkline } from "@/components/sparkline";
import { StatusBadge } from "@/components/status-badge";
import { Card } from "@/components/ui/card";
import type { ServerStatus } from "@/lib/api";
import { SERVER_PROFILES } from "@/lib/servers";

const rows = [
  { key: "cpu", label: "CPU", color: "#60a5fa" },
  { key: "memory", label: "MEM", color: "#a78bfa" },
  { key: "network", label: "NET", color: "#22d3ee" },
] as const;

export function ServerCard({ server: s }: { server: ServerStatus }) {
  return (
    <Link href={`/servers/${s.server}`} className="group">
      <Card className="h-full p-4 transition-colors hover:border-zinc-600/70 hover:bg-ink-850">
        <div className="flex items-center justify-between gap-2">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <Server className="h-3.5 w-3.5 text-zinc-500" />
              <span className="font-mono text-[13px] text-zinc-200">{s.server}</span>
            </div>
            <div className="mt-0.5 truncate pl-[22px] text-[10px] text-zinc-600">
              {SERVER_PROFILES[s.server]?.role ?? "synthetic server"}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <StatusBadge severity={s.severity} />
            <ArrowUpRight className="h-3.5 w-3.5 text-zinc-600 transition-colors group-hover:text-zinc-300" />
          </div>
        </div>

        <div className="mt-1 flex items-baseline justify-between text-[11px]">
          <span className="text-zinc-500">anomaly score</span>
          <span className={s.flagged ? "font-mono text-crit" : "font-mono text-zinc-300"}>
            {s.anomaly_score.toFixed(2)}
          </span>
        </div>

        <div className="mt-4 space-y-2.5">
          {rows.map(({ key, label, color }) => (
            <div key={key} className="flex items-center gap-2">
              <span className="w-7 text-[9px] font-medium uppercase tracking-wide text-zinc-600">{label}</span>
              <div className="h-7 flex-1">
                <Sparkline data={s.sparklines[key] ?? []} color={color} />
              </div>
              <span className="w-10 text-right font-mono text-[11px] tabular-nums text-zinc-400">
                {s[key].toFixed(0)}
              </span>
            </div>
          ))}
        </div>

        <div className="mt-4 flex items-center justify-between border-t border-line/70 pt-3 text-[11px]">
          <span className={s.flagged ? "text-crit" : "text-zinc-500"}>{s.flagged ? "abnormal" : "normal"}</span>
          <span className="text-zinc-500">
            30m forecast{" "}
            <span className="font-mono text-zinc-300">
              {s.forecast_30min != null ? `${s.forecast_30min.toFixed(1)}%` : "—"}
            </span>
          </span>
        </div>
      </Card>
    </Link>
  );
}
