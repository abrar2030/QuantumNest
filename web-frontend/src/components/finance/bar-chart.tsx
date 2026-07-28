"use client";

import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatPercentage } from "@/lib/utils";

interface BarPoint {
  name: string;
  value: number;
}

export function PerformanceBarChart({
  data,
  height = 280,
  layout = "vertical",
}: {
  data: BarPoint[];
  height?: number;
  layout?: "vertical" | "horizontal";
}) {
  const isHorizontal = layout === "horizontal";

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout={isHorizontal ? "horizontal" : "vertical"}
        margin={{ top: 4, right: 16, left: isHorizontal ? 0 : 8, bottom: 0 }}
      >
        {isHorizontal ? (
          <>
            <XAxis
              dataKey="name"
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={{ stroke: "hsl(var(--border))" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${v}%`}
            />
          </>
        ) : (
          <>
            <XAxis
              type="number"
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${v}%`}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={90}
            />
          </>
        )}
        <Tooltip
          cursor={{ fill: "hsl(var(--muted) / 0.4)" }}
          contentStyle={{
            backgroundColor: "hsl(var(--popover))",
            borderColor: "hsl(var(--border))",
            borderRadius: 12,
            color: "hsl(var(--popover-foreground))",
            fontSize: 12,
          }}
          formatter={(value: number) => [formatPercentage(value), "Change"]}
        />
        <Bar dataKey="value" radius={[4, 4, 4, 4]} maxBarSize={22}>
          {data.map((entry) => (
            <Cell
              key={entry.name}
              fill={
                entry.value >= 0
                  ? "hsl(var(--success))"
                  : "hsl(var(--destructive))"
              }
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
