import type { ReactNode } from "react";
import Link from "next/link";
import { ShieldCheck, Sparkles, TrendingUp } from "lucide-react";
import { Logo } from "./logo";

const highlights = [
  {
    icon: Sparkles,
    title: "AI-native intelligence",
    description:
      "Transformer-based forecasting and sentiment models surface opportunities before the crowd.",
  },
  {
    icon: TrendingUp,
    title: "Institutional-grade analytics",
    description:
      "Risk, drawdown, Sharpe, and factor exposure: the same tooling hedge funds rely on.",
  },
  {
    icon: ShieldCheck,
    title: "Blockchain-secured assets",
    description:
      "Tokenized holdings settle on-chain with full transparency and verifiable custody.",
  },
];

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
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-surface p-10 lg:flex">
        <div className="grid-backdrop absolute inset-0" />
        <div className="absolute inset-0 bg-hero-glow" />
        <div className="relative z-10">
          <Logo />
        </div>
        <div className="relative z-10 max-w-md space-y-8">
          <h2 className="font-display text-3xl font-semibold leading-tight text-balance">
            Where AI meets tokenized wealth management.
          </h2>
          <div className="space-y-6">
            {highlights.map((item) => (
              <div key={item.title} className="flex gap-3.5">
                <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/15 text-primary">
                  <item.icon className="h-4.5 w-4.5" />
                </div>
                <div>
                  <p className="font-display text-sm font-semibold">
                    {item.title}
                  </p>
                  <p className="mt-0.5 text-sm text-muted-foreground">
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <p className="relative z-10 text-xs text-muted-foreground">
          © {new Date().getFullYear()} QuantumNest Capital
        </p>
      </div>

      <div className="flex flex-col items-center justify-center px-6 py-12 sm:px-10">
        <div className="mb-8 lg:hidden">
          <Logo />
        </div>
        <div className="w-full max-w-sm">
          <div className="mb-8 text-center lg:text-left">
            <h1 className="font-display text-2xl font-semibold tracking-tight">
              {title}
            </h1>
            <p className="mt-1.5 text-sm text-muted-foreground">
              {description}
            </p>
          </div>
          {children}
        </div>
        <p className="mt-8 text-center text-xs text-muted-foreground">
          By continuing you agree to QuantumNest&apos;s{" "}
          <Link href="/terms" className="underline hover:text-foreground">
            Terms of Service
          </Link>{" "}
          and{" "}
          <Link href="/privacy" className="underline hover:text-foreground">
            Privacy Policy
          </Link>
          .
        </p>
      </div>
    </div>
  );
}
