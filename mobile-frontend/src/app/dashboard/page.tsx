"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  Layers,
  Newspaper,
  PieChart as PieChartIcon,
  Sparkles,
  TrendingUp,
  Wallet,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/finance/page-header";
import { StatCard } from "@/components/finance/stat-card";
import { ChangeBadge } from "@/components/finance/change-badge";
import {
  AllocationChart,
  AllocationLegend,
} from "@/components/finance/allocation-chart";
import { PerformanceBarChart } from "@/components/finance/bar-chart";
import { EmptyState, ErrorState } from "@/components/finance/empty-state";
import { useApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useAssetCatalog } from "@/hooks/use-asset-catalog";
import { displayName, formatCurrency, formatDate } from "@/lib/utils";
import type {
  MarketRecommendations,
  MarketSummary,
  Portfolio,
  PortfolioSummary,
  PortfolioWithAssets,
  SectorPerformanceResponse,
  Transaction,
} from "@/lib/types";

function DashboardContent() {
  const { get } = useApi();
  const { user } = useAuth();
  const { byId: assetsById, isLoading: assetsLoading } = useAssetCatalog();

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [summaries, setSummaries] = useState<PortfolioSummary[]>([]);
  const [primaryPortfolio, setPrimaryPortfolio] =
    useState<PortfolioWithAssets | null>(null);
  const [marketSummary, setMarketSummary] = useState<MarketSummary | null>(
    null,
  );
  const [sectorPerformance, setSectorPerformance] =
    useState<SectorPerformanceResponse | null>(null);
  const [aiOutlook, setAiOutlook] = useState<MarketRecommendations | null>(
    null,
  );
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>(
    [],
  );

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const portfolioList = await get<Portfolio[]>("/portfolio/", {
          limit: 50,
        });
        if (cancelled) return;
        setPortfolios(portfolioList);

        const summaryResults = await Promise.all(
          portfolioList.map((p) =>
            get<PortfolioSummary>(`/portfolio/summary/${p.id}`).catch(
              () => null,
            ),
          ),
        );
        const validSummaries = summaryResults.filter(
          (s): s is PortfolioSummary => s !== null,
        );
        if (cancelled) return;
        setSummaries(validSummaries);

        const top = [...validSummaries].sort(
          (a, b) => b.total_value - a.total_value,
        )[0];
        if (top) {
          get<PortfolioWithAssets>(`/portfolio/${top.portfolio_id}`)
            .then((data) => !cancelled && setPrimaryPortfolio(data))
            .catch(() => {});
        }

        const [summaryRes, sectorRes, aiRes, txRes] = await Promise.allSettled([
          get<MarketSummary>("/market/market_summary"),
          get<SectorPerformanceResponse>("/market/sector_performance", {
            period: "1m",
          }),
          get<MarketRecommendations>("/ai/recommendations/market"),
          get<Transaction[]>("/market/transactions/", { limit: 5 }),
        ]);
        if (cancelled) return;
        if (summaryRes.status === "fulfilled")
          setMarketSummary(summaryRes.value);
        if (sectorRes.status === "fulfilled")
          setSectorPerformance(sectorRes.value);
        if (aiRes.status === "fulfilled") setAiOutlook(aiRes.value);
        if (txRes.status === "fulfilled") setRecentTransactions(txRes.value);
      } catch {
        if (!cancelled) setError("We couldn't load your dashboard right now.");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const totalValue = summaries.reduce((sum, s) => sum + s.total_value, 0);
  const totalCost = summaries.reduce((sum, s) => sum + s.total_cost, 0);
  const totalReturn =
    totalCost > 0 ? ((totalValue - totalCost) / totalCost) * 100 : 0;
  const totalHoldings = summaries.reduce((sum, s) => sum + s.total_assets, 0);

  const allocation =
    primaryPortfolio?.assets.map((holding) => {
      const asset = assetsById.get(holding.asset_id);
      const value =
        holding.current_value ?? holding.quantity * holding.purchase_price;
      return { name: asset?.symbol || `#${holding.asset_id}`, value };
    }) || [];

  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Dashboard"
          description="Your portfolio, at a glance."
        />
        <ErrorState message={error} onRetry={() => window.location.reload()} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Welcome back${user ? `, ${displayName(user)}` : ""}`}
        description="Here's what's happening across your portfolios today."
        actions={
          <Button asChild>
            <Link href="/portfolio">
              <Wallet className="h-4 w-4" /> Manage portfolios
            </Link>
          </Button>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total portfolio value"
          value={formatCurrency(totalValue)}
          change={totalReturn}
          icon={Wallet}
          isLoading={isLoading}
        />
        <StatCard
          label="Total unrealized return"
          value={formatCurrency(totalValue - totalCost)}
          icon={TrendingUp}
          isLoading={isLoading}
          hint={`vs ${formatCurrency(totalCost)} invested`}
        />
        <StatCard
          label="Active portfolios"
          value={String(portfolios.length)}
          icon={Layers}
          isLoading={isLoading}
        />
        <StatCard
          label="Total holdings"
          value={String(totalHoldings)}
          icon={PieChartIcon}
          isLoading={isLoading}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="font-display">Sector performance</CardTitle>
            <span className="text-xs text-muted-foreground">Last month</span>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : sectorPerformance?.data.length ? (
              <PerformanceBarChart data={sectorPerformance.data} height={260} />
            ) : (
              <EmptyState
                icon={TrendingUp}
                title="No sector data available"
                description="Sector performance will appear here once market data syncs."
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-display">
              {primaryPortfolio
                ? `${primaryPortfolio.name} allocation`
                : "Allocation"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading || assetsLoading ? (
              <Skeleton className="h-52 w-full" />
            ) : allocation.length ? (
              <>
                <AllocationChart data={allocation} height={190} />
                <div className="mt-4">
                  <AllocationLegend data={allocation} />
                </div>
              </>
            ) : (
              <EmptyState
                icon={PieChartIcon}
                title="No holdings yet"
                description="Add assets to a portfolio to see your allocation breakdown."
                action={
                  <Button size="sm" asChild>
                    <Link href="/portfolio">Go to portfolios</Link>
                  </Button>
                }
              />
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="font-display">Recent activity</CardTitle>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/portfolio">
                View all <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="space-y-1">
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : recentTransactions.length ? (
              recentTransactions.map((tx) => (
                <div
                  key={tx.id}
                  className="flex items-center justify-between border-b border-border/60 py-3 last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <Wallet className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-sm font-medium capitalize">
                        {tx.transaction_type}
                        {tx.asset_id
                          ? ` · ${assetsById.get(tx.asset_id)?.symbol || `#${tx.asset_id}`}`
                          : ""}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(tx.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold">
                      {formatCurrency(tx.amount)}
                    </p>
                    <Badge
                      variant="outline"
                      className="mt-0.5 text-[10px] capitalize"
                    >
                      {tx.status}
                    </Badge>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState
                icon={Wallet}
                title="No transactions yet"
                description="Your buy, sell, and transfer activity will show up here."
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            <CardTitle className="font-display">AI market outlook</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoading ? (
              <Skeleton className="h-40 w-full" />
            ) : aiOutlook ? (
              <>
                <div className="grid grid-cols-3 gap-2 text-center">
                  {(
                    [
                      ["Short", aiOutlook.market_outlook.short_term],
                      ["Medium", aiOutlook.market_outlook.medium_term],
                      ["Long", aiOutlook.market_outlook.long_term],
                    ] as const
                  ).map(([label, outlook]) => (
                    <div key={label} className="rounded-lg bg-muted/50 p-2.5">
                      <p className="text-[10px] uppercase text-muted-foreground">
                        {label}
                      </p>
                      <p className="mt-1 text-xs font-semibold capitalize text-foreground">
                        {outlook}
                      </p>
                    </div>
                  ))}
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">
                    Top asset calls
                  </p>
                  <div className="mt-2 space-y-2">
                    {aiOutlook.asset_recommendations.slice(0, 3).map((rec) => (
                      <div
                        key={rec.asset_symbol}
                        className="flex items-center justify-between text-sm"
                      >
                        <span className="font-medium">{rec.asset_symbol}</span>
                        <Badge
                          className={
                            rec.recommendation === "buy"
                              ? "bg-success/10 text-success hover:bg-success/10"
                              : rec.recommendation === "sell"
                                ? "bg-destructive/10 text-destructive hover:bg-destructive/10"
                                : "bg-muted text-muted-foreground"
                          }
                        >
                          {rec.recommendation}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
                <Button variant="outline" size="sm" className="w-full" asChild>
                  <Link href="/recommendations">
                    View full AI insights <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </Button>
              </>
            ) : (
              <EmptyState
                icon={Sparkles}
                title="AI insights unavailable"
                description="Check back shortly for updated recommendations."
              />
            )}
          </CardContent>
        </Card>
      </div>

      {marketSummary && (
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Newspaper className="h-4 w-4 text-primary" />
            <CardTitle className="font-display">Market snapshot</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-3">
              {marketSummary.indices.map((index) => (
                <div
                  key={index.name}
                  className="rounded-lg border border-border/60 p-4"
                >
                  <p className="text-sm text-muted-foreground">{index.name}</p>
                  <p className="mt-1 font-display text-lg font-semibold">
                    {index.value.toLocaleString()}
                  </p>
                  <ChangeBadge value={index.change_percent} className="mt-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function DashboardPage() {
  return (
    <AppShell>
      <DashboardContent />
    </AppShell>
  );
}
