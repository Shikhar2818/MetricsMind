"use client";

import { Activity, BarChart3, Bell, LayoutDashboard } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const nav = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/model", label: "Model evaluation", icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-56 flex-col border-r border-line bg-ink-950 px-3 pb-5 pt-12 md:flex lg:w-60">
      <Link href="/" className="flex items-center gap-2.5 px-2">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent/15 text-accent-soft ring-1 ring-inset ring-accent/20">
          <Activity className="h-4 w-4" />
        </span>
        <span>
          <span className="block text-sm font-semibold tracking-tight">PulseGrid</span>
          <span className="block text-[10px] uppercase tracking-[0.14em] text-zinc-500">Infra intelligence</span>
        </span>
      </Link>

      <nav className="mt-8 space-y-1">
        {nav.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" || pathname.startsWith("/servers") : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-[13px] transition-colors",
                active ? "bg-white/[0.05] text-zinc-100" : "text-muted hover:bg-white/[0.03] hover:text-zinc-200",
              )}
            >
              <Icon className={cn("h-4 w-4", active ? "text-accent-soft" : "text-zinc-500")} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-lg border border-line bg-ink-900/70 p-3">
        <div className="flex items-center gap-1.5 text-[11px] font-medium text-zinc-300">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" />
          Replay feed · 60×
        </div>
        <p className="mt-1 text-[11px] leading-relaxed text-zinc-500">Synthetic fleet · 8 servers · 45 days</p>
      </div>
    </aside>
  );
}
