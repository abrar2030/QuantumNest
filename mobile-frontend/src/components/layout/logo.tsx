import Link from "next/link";
import { cn } from "@/lib/utils";

export function Logo({
  href = "/",
  className,
  iconOnly = false,
}: {
  href?: string | null;
  className?: string;
  iconOnly?: boolean;
}) {
  const content = (
    <span
      className={cn("inline-flex items-center gap-2 select-none", className)}
    >
      <span className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent font-display text-sm font-bold text-primary-foreground shadow-lg shadow-primary/30">
        Q
      </span>
      {!iconOnly && (
        <span className="font-display text-base font-semibold tracking-tight text-foreground">
          QuantumNest
        </span>
      )}
    </span>
  );

  if (!href) return content;

  return (
    <Link href={href} className="shrink-0">
      {content}
    </Link>
  );
}
