import type { Severity } from "@/lib/api";
import { cn } from "@/lib/utils";

const config: Record<Severity, { label: string; className: string; dot: string }> = {
  LOW: { label: "Healthy", className: "border-ok/20 bg-ok/10 text-ok", dot: "bg-ok" },
  MEDIUM: { label: "Warning", className: "border-warn/20 bg-warn/10 text-warn", dot: "bg-warn" },
  HIGH: { label: "Critical", className: "border-crit/20 bg-crit/10 text-crit", dot: "bg-crit" },
};

export function StatusBadge({ severity, className }: { severity: Severity; className?: string }) {
  const c = config[severity];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-medium",
        c.className,
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", c.dot)} />
      {c.label}
    </span>
  );
}
