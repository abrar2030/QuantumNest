"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { formatPercentage } from "@/lib/utils";

const PALETTE = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
  "hsl(var(--muted-foreground))",
];

interface Slice {
  name: string;
  value: number;
}

export function AllocationChart({
  data,
  height = 240,
}: {
  data: Slice[];
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          innerRadius="58%"
          outerRadius="85%"
          paddingAngle={2}
          strokeWidth={0}
        >
          {data.map((entry, index) => (
            <Cell key={entry.name} fill={PALETTE[index % PALETTE.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "hsl(var(--popover))",
            borderColor: "hsl(var(--border))",
            borderRadius: 12,
            color: "hsl(var(--popover-foreground))",
            fontSize: 12,
          }}
          formatter={(value: number, name: string) => [
            formatPercentage(value),
            name,
          ]}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function AllocationLegend({ data }: { data: Slice[] }) {
  return (
    <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2">
      {data.map((entry, index) => (
        <li key={entry.name} className="flex items-center gap-2 text-sm">
          <span
            className="h-2.5 w-2.5 shrink-0 rounded-full"
            style={{ backgroundColor: PALETTE[index % PALETTE.length] }}
          />
          <span className="truncate text-foreground">{entry.name}</span>
          <span className="ml-auto shrink-0 text-muted-foreground">
            {formatPercentage(entry.value)}
          </span>
        </li>
      ))}
    </ul>
  );
}
