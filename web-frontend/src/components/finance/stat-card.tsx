import type { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { ChangeBadge } from "./change-badge";

export function StatCard({
  label,
  value,
  change,
  icon: Icon,
  isLoading,
  hint,
  className,
}: {
  label: string;
  value: string;
  change?: number;
  icon?: LucideIcon;
  isLoading?: boolean;
  hint?: string;
  className?: string;
}) {
  return (
    <Card className={cn("card-hover", className)}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <p className="text-sm font-medium text-muted-foreground">{label}</p>
          {Icon && (
            <div className="rounded-lg bg-primary/10 p-2 text-primary">
              <Icon className="h-4 w-4" />
            </div>
          )}
        </div>
        {isLoading ? (
          <Skeleton className="mt-3 h-8 w-28" />
        ) : (
          <p className="mt-2 font-display text-2xl font-semibold tracking-tight">
            {value}
          </p>
        )}
        <div className="mt-2 flex items-center gap-2">
          {typeof change === "number" && !isLoading && (
            <ChangeBadge value={change} />
          )}
          {hint && (
            <span className="text-xs text-muted-foreground">{hint}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
