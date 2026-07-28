import type { ReactNode } from "react";
import Link from "next/link";
import { Logo } from "./logo";

export function AuthShell({
  children,
  title,
  description,
}: {
  children: ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex min-h-screen flex-col px-5 py-8">
      <Logo />
      <div className="flex flex-1 flex-col justify-center py-8">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-7">
            <h1 className="font-display text-2xl font-semibold tracking-tight">
              {title}
            </h1>
            <p className="mt-1.5 text-sm text-muted-foreground">
              {description}
            </p>
          </div>
          {children}
        </div>
      </div>
      <p className="text-center text-xs text-muted-foreground">
        By continuing you agree to QuantumNest&apos;s{" "}
        <Link href="/terms" className="underline hover:text-foreground">
          Terms
        </Link>{" "}
        and{" "}
        <Link href="/privacy" className="underline hover:text-foreground">
          Privacy Policy
        </Link>
        .
      </p>
    </div>
  );
}
