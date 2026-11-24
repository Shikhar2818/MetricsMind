"use client";

import { Line, LineChart, ResponsiveContainer } from "recharts";

export function Sparkline({ data, color }: { data: number[]; color: string }) {
  const rows = data.map((value, i) => ({ i, value }));
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={rows} margin={{ top: 2, right: 0, bottom: 2, left: 0 }}>
        <Line type="monotone" dataKey="value" stroke={color} strokeWidth={1.5} dot={false} isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
