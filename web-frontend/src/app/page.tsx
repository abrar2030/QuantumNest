"use client";

import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Blocks,
  Brain,
  Gauge,
  Lock,
  ShieldCheck,
  Sparkles,
  Wallet,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { PublicShell } from "@/components/layout/public-shell";
import { useAuth } from "@/lib/auth-context";

const platformFeatures = [
  {
    icon: Wallet,
    title: "Unified portfolios",
    description:
      "Track equities, crypto, and tokenized real-world assets side by side with live valuations.",
  },
  {
    icon: BarChart3,
    title: "Institutional analytics",
    description:
      "Sharpe ratio, alpha, beta, drawdown, and volatility computed continuously in the background.",
  },
  {
    icon: Blocks,
    title: "On-chain settlement",
    description:
      "Tokenized assets and smart contracts give every holding a verifiable, transparent record.",
  },
];

const intelligenceFeatures = [
  {
    icon: Brain,
    title: "Transformer forecasting",
    description:
      "Multi-transformer volatility and price models trained on years of market microstructure data.",
  },
  {
    icon: Sparkles,
    title: "Portfolio optimization",
    description:
      "AI-generated rebalancing and diversification recommendations tailored to your risk profile.",
  },
  {
    icon: Gauge,
    title: "Sentiment & risk scoring",
    description:
      "Real-time news and social sentiment fused with quantitative risk metrics for every asset.",
  },
];

const securityFeatures = [
  {
    icon: ShieldCheck,
    title: "Bank-grade authentication",
    description:
      "JWT-based session security with granular role and tier permissions.",
  },
  {
    icon: Lock,
    title: "Encrypted by default",
    description:
      "Sensitive data is encrypted in transit and at rest across the platform.",
  },
  {
    icon: Zap,
    title: "Real-time monitoring",
    description:
      "System health, anomaly detection, and audit logs available to administrators.",
  },
];

const stats = [
  { label: "Assets tracked", value: "12K+" },
  { label: "AI models in production", value: "8" },
  { label: "Avg. API response", value: "<120ms" },
  { label: "Supported networks", value: "5" },
];

export default function HomePage() {
  const { isAuthenticated } = useAuth();

  return (
    <PublicShell>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="grid-backdrop absolute inset-0" />
        <div className="absolute inset-0 bg-hero-glow" />
        <div className="container relative py-24 sm:py-32">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-muted-foreground">
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              AI-native investment infrastructure
            </div>
            <h1 className="font-display text-4xl font-semibold tracking-tight text-balance sm:text-6xl">
              Invest smarter with{" "}
              <span className="text-gradient">AI and tokenized assets</span>
            </h1>
            <p className="mx-auto mt-6 max-w-xl text-balance text-base text-muted-foreground sm:text-lg">
              QuantumNest fuses transformer-based market intelligence with
              blockchain-secured portfolios, giving you an institutional edge in
              a single platform.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button size="lg" asChild>
                <Link href={isAuthenticated ? "/dashboard" : "/auth/register"}>
                  {isAuthenticated ? "Go to dashboard" : "Get started free"}
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="/market-analysis">Explore live markets</Link>
              </Button>
            </div>
          </div>

          <div className="mx-auto mt-20 grid max-w-4xl grid-cols-2 gap-6 sm:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="font-display text-2xl font-semibold text-foreground sm:text-3xl">
                  {stat.value}
                </p>
                <p className="mt-1 text-xs text-muted-foreground sm:text-sm">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platform */}
      <section id="platform" className="border-t border-border/60 py-24">
        <div className="container">
          <SectionHeading
            eyebrow="Platform"
            title="One place for every asset you hold"
            description="From equities to tokenized real-world assets, manage everything with the same institutional-grade tooling."
          />
          <FeatureGrid features={platformFeatures} />
        </div>
      </section>

      {/* Intelligence */}
      <section
        id="intelligence"
        className="border-t border-border/60 bg-surface/40 py-24"
      >
        <div className="container">
          <SectionHeading
            eyebrow="Intelligence"
            title="AI that works while you sleep"
            description="QuantumNest's models continuously analyze markets, sentiment, and your portfolio to surface the next best move."
          />
          <FeatureGrid features={intelligenceFeatures} />
        </div>
      </section>

      {/* Security */}
      <section id="security" className="border-t border-border/60 py-24">
        <div className="container">
          <SectionHeading
            eyebrow="Security"
            title="Built for trust, from day one"
            description="Every layer of QuantumNest is designed around transparency, verifiability, and control."
          />
          <FeatureGrid features={securityFeatures} />
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-border/60 py-24">
        <div className="container">
          <Card className="overflow-hidden border-primary/20 bg-gradient-to-br from-primary/10 via-card to-accent/5">
            <CardContent className="flex flex-col items-center gap-6 p-10 text-center sm:p-16">
              <h2 className="font-display text-3xl font-semibold text-balance sm:text-4xl">
                Ready to put AI to work on your portfolio?
              </h2>
              <p className="max-w-lg text-balance text-muted-foreground">
                Create your free account and get a personalized risk profile, AI
                recommendations, and live market analytics in minutes.
              </p>
              <Button size="lg" asChild>
                <Link href={isAuthenticated ? "/dashboard" : "/auth/register"}>
                  {isAuthenticated ? "Go to dashboard" : "Create your account"}
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>
    </PublicShell>
  );
}

function SectionHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      <p className="text-xs font-semibold uppercase tracking-widest text-primary">
        {eyebrow}
      </p>
      <h2 className="mt-3 font-display text-3xl font-semibold text-balance">
        {title}
      </h2>
      <p className="mt-3 text-muted-foreground text-balance">{description}</p>
    </div>
  );
}

function FeatureGrid({
  features,
}: {
  features: Array<{ icon: typeof Brain; title: string; description: string }>;
}) {
  return (
    <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {features.map((feature) => (
        <Card key={feature.title} className="card-hover">
          <CardContent className="p-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <feature.icon className="h-5 w-5" />
            </div>
            <h3 className="mt-4 font-display text-base font-semibold">
              {feature.title}
            </h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {feature.description}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
