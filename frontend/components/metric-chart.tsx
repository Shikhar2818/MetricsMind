"use client";

import { useMemo } from "react";
import {
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { AnomalyWindow, ForecastPoint, MetricPoint } from "@/lib/api";

const UNIT: Record<string, string> = {
  cpu: "%",
  memory: "%",
  disk: "%",
  network: "MB/s",
  latency: "ms",
  error_rate: "%",
};

type Row = { t: number; value?: number; score?: number; forecast?: number; flag?: number };

const tick = (value: number, range: string) => {
  const d = new Date(value);
  return range === "3d" || range === "7d"
    ? d.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
    : d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

function ChartTip({ active, payload, label, metric }: any) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload as Row;
  const unit = UNIT[metric] ?? "";
  return (
    <div className="rounded-lg border border-line bg-ink-800/95 px-3 py-2 text-xs shadow-2xl">
      <div className="text-zinc-500">
        {new Date(Number(label)).toLocaleString([], {
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        })}
      </div>
      <div className="mt-1 font-mono text-zinc-100">
        {row.value != null
          ? `${row.value.toFixed(1)} ${unit}`
          : row.forecast != null
            ? `forecast ${row.forecast.toFixed(1)} ${unit}`
            : "—"}
      </div>
      {row.score != null && <div className="mt-0.5 text-zinc-500">score {row.score.toFixed(2)}</div>}
    </div>
  );
}

export function MetricChart({
  metric,
  points,
  forecast,
  anomalies,
  range,
  threshold,
}: {
  metric: string;
  points: MetricPoint[];
  forecast: ForecastPoint[];
  anomalies: AnomalyWindow[];
  range: string;
  threshold: number | null;
}) {
  const rows = useMemo(() => {
    const map = new Map<number, Row>();
    for (const p of points) {
      const t = new Date(p.t).getTime();
      map.set(t, { t, value: p.value, score: p.score, flag: p.flagged ? p.value : undefined });
    }
    for (const f of forecast) {
      const t = new Date(f.t).getTime();
      const row = map.get(t) ?? { t };
      row.forecast = f.value;
      map.set(t, row);
    }
    return [...map.values()].sort((a, b) => a.t - b.t);
  }, [points, forecast]);

  const percent = ["cpu", "memory", "disk", "error_rate"].includes(metric);

  return (
    <div className="h-[340px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={rows} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
          <CartesianGrid stroke="#1e2430" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="t"
            type="number"
            domain={["dataMin", "dataMax"]}
            scale="time"
            tickFormatter={(v) => tick(v, range)}
            stroke="#2a3140"
            tick={{ fill: "#7d8699", fontSize: 11 }}
            tickLine={false}
            minTickGap={range === "3d" || range === "7d" ? 110 : 48}
          />
          <YAxis
            domain={percent ? [0, 100] : ["auto", "auto"]}
            stroke="#2a3140"
            tick={{ fill: "#7d8699", fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            width={46}
          />
          <Tooltip content={<ChartTip metric={metric} />} cursor={{ stroke: "#3f4654", strokeDasharray: "3 3" }} />
          {anomalies.map((a) => (
            <ReferenceArea
              key={a.start}
              x1={new Date(a.start).getTime()}
              x2={new Date(a.end).getTime()}
              fill="#f87171"
              fillOpacity={0.16}
              stroke="#f87171"
              strokeOpacity={0.25}
            />
          ))}
          {threshold != null && (
            <ReferenceLine
              y={threshold}
              stroke="#52525b"
              strokeDasharray="3 3"
              label={{ value: "90% threshold", fill: "#71717a", fontSize: 10, position: "insideTopRight" }}
            />
          )}
          <Line
            type="monotone"
            dataKey="value"
            stroke="#60a5fa"
            strokeWidth={1.4}
            dot={false}
            isAnimationActive={false}
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#d4d4d8"
            strokeWidth={1.2}
            strokeDasharray="4 4"
            dot={false}
            isAnimationActive={false}
            connectNulls
          />
          <Line
            dataKey="flag"
            stroke="none"
            dot={{ r: 2.4, fill: "#f87171", stroke: "none" }}
            activeDot={false}
            isAnimationActive={false}
            connectNulls={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
