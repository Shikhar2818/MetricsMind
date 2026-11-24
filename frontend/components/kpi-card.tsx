import type { LucideIcon } from "lucide-react";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const tones = {
  default: "text-zinc-100",
  ok: "text-ok",
  warn: "text-warn",
  crit: "text-crit",
  accent: "text-accent-soft",
} as const;

export function KpiCard({
  label,
  value,
  icon: Icon,
  tone = "default",
  hint,
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: keyof typeof tones;
  hint?: string;
}) {
  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <span className="text-[10px] uppercase tracking-[0.12em] text-zinc-500">{label}</span>
        <Icon className={cn("h-3.5 w-3.5", tones[tone])} />
      </div>
      <div className={cn("mt-2 text-2xl font-semibold tabular-nums tracking-tight", tones[tone])}>{value}</div>
      <div className="mt-0.5 h-4 truncate text-[11px] text-zinc-500">{hint}</div>
    </Card>
  );
}
