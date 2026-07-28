"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatCurrency } from "@/lib/utils";

interface TrendPoint {
  label: string;
  value: number;
}

export function TrendChart({
  data,
  color = "hsl(var(--primary))",
  height = 280,
  valuePrefix = "$",
  showGrid = true,
  showAxes = true,
}: {
  data: TrendPoint[];
  color?: string;
  height?: number;
  valuePrefix?: string;
  showGrid?: boolean;
  showAxes?: boolean;
}) {
  const gradientId = "trend-gradient";

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.35} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        {showGrid && (
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="hsl(var(--border))"
            vertical={false}
          />
        )}
        {showAxes && (
          <XAxis
            dataKey="label"
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: "hsl(var(--border))" }}
            minTickGap={24}
          />
        )}
        {showAxes && (
          <YAxis
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            width={56}
            tickFormatter={(v) =>
              valuePrefix
                ? `${valuePrefix}${Math.round(v).toLocaleString()}`
                : v
            }
          />
        )}
        <Tooltip
          contentStyle={{
            backgroundColor: "hsl(var(--popover))",
            borderColor: "hsl(var(--border))",
            borderRadius: 12,
            color: "hsl(var(--popover-foreground))",
            fontSize: 12,
          }}
          formatter={(value: number) => [
            valuePrefix === "$" ? formatCurrency(value) : `${value}`,
            "Value",
          ]}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          fill={`url(#${gradientId})`}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
