"use client";

import { Clock } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import useSWR from "swr";

import { fetcher, fmtDateTime, fmtTime, type Health } from "@/lib/api";
import { cn } from "@/lib/utils";

const mobileNav = [
  { href: "/", label: "Overview" },
  { href: "/alerts", label: "Alerts" },
  { href: "/model", label: "Model" },
];

export function TopBar() {
  const pathname = usePathname();
  const { data } = useSWR<Health>("/health", fetcher, { refreshInterval: 5000 });
  const [synced, setSynced] = useState<Date | null>(null);

  useEffect(() => {
    if (data) setSynced(new Date());
  }, [data]);

  const title = pathname.startsWith("/servers/")
    ? "Server detail"
    : pathname.startsWith("/alerts")
      ? "Alerts"
      : pathname.startsWith("/model")
        ? "Model evaluation"
        : "Fleet overview";

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-ink-950/85 backdrop-blur">
      <div className="flex h-14 items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2.5">
          <Link href="/" className="md:hidden">
            <span className="flex h-7 w-7 items-center justify-center rounded-md bg-accent/15 text-accent-soft">
              <Clock className="h-3.5 w-3.5" />
            </span>
          </Link>
          <h1 className="text-[13px] font-medium text-zinc-300">{title}</h1>
        </div>

        <div className="flex items-center gap-2 text-[11px]">
          <span className="flex items-center gap-1.5 rounded-full border border-line bg-ink-900 px-2.5 py-1">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-ok opacity-70" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-ok" />
            </span>
            <span className="font-semibold tracking-wide text-zinc-200">LIVE</span>
            <span className="text-zinc-500">replay {data?.replay_speed ?? 60}×</span>
          </span>
          <span className="hidden items-center gap-1.5 rounded-full border border-line bg-ink-900 px-2.5 py-1 font-mono text-zinc-400 sm:flex">
            <Clock className="h-3 w-3 text-zinc-500" />
            {data ? fmtDateTime(data.now) : "—"}
          </span>
          <span className="hidden text-zinc-600 lg:inline">synced {synced ? fmtTime(synced.toISOString()) : "—"}</span>
        </div>
      </div>

      <nav className="flex gap-1 border-t border-line/60 px-3 py-2 md:hidden">
        {mobileNav.map(({ href, label }) => {
          const active = href === "/" ? pathname === "/" || pathname.startsWith("/servers") : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "rounded-md px-2.5 py-1 text-xs",
                active ? "bg-white/[0.06] text-zinc-100" : "text-muted",
              )}
            >
              {label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
