import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { cn, formatPercentage } from "@/lib/utils";

export function ChangeBadge({
  value,
  className,
  showIcon = true,
}: {
  value: number;
  className?: string;
  showIcon?: boolean;
}) {
  const isPositive = value > 0;
  const isNegative = value < 0;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold",
        isPositive && "bg-success/10 text-success",
        isNegative && "bg-destructive/10 text-destructive",
        !isPositive && !isNegative && "bg-muted text-muted-foreground",
        className,
      )}
    >
      {showIcon &&
        (isPositive ? (
          <ArrowUpRight className="h-3 w-3" />
        ) : isNegative ? (
          <ArrowDownRight className="h-3 w-3" />
        ) : (
          <Minus className="h-3 w-3" />
        ))}
      {formatPercentage(Math.abs(value))}
    </span>
  );
}
