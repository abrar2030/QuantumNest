"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  BarChart3,
  PieChart as PieChartIcon,
  Trash2,
  Wallet,
} from "lucide-react";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/finance/page-header";
import { StatCard } from "@/components/finance/stat-card";
import { ChangeBadge } from "@/components/finance/change-badge";
import {
  AllocationChart,
  AllocationLegend,
} from "@/components/finance/allocation-chart";
import { EmptyState, ErrorState } from "@/components/finance/empty-state";
import { AddAssetDialog } from "@/components/portfolio/add-asset-dialog";
import { useAssetCatalog } from "@/hooks/use-asset-catalog";
import { ApiError, useApi } from "@/lib/api";
import { formatCurrency, formatDate, formatNumber } from "@/lib/utils";
import type {
  PortfolioAsset,
  PortfolioPerformance,
  PortfolioWithAssets,
} from "@/lib/types";

const riskLabels: Record<string, string> = {
  very_low: "Very low risk",
  low: "Low risk",
  moderate: "Moderate risk",
  high: "High risk",
  very_high: "Very high risk",
};

const periods = [
  { value: "1m", label: "1M" },
  { value: "3m", label: "3M" },
  { value: "6m", label: "6M" },
  { value: "1y", label: "1Y" },
];

function PortfolioDetailContent({ portfolioId }: { portfolioId: number }) {
  const { get, del } = useApi();
  const router = useRouter();
  const {
    assets,
    byId: assetsById,
    isLoading: assetsLoading,
  } = useAssetCatalog();

  const [portfolio, setPortfolio] = useState<PortfolioWithAssets | null>(null);
  const [performance, setPerformance] = useState<PortfolioPerformance | null>(
    null,
  );
  const [period, setPeriod] = useState("1m");
  const [isLoading, setIsLoading] = useState(true);
  const [isPerfLoading, setIsPerfLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const loadPortfolio = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await get<PortfolioWithAssets>(`/portfolio/${portfolioId}`);
      setPortfolio(data);
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 404
          ? "This portfolio doesn't exist or you don't have access to it."
          : "We couldn't load this portfolio right now.",
      );
    } finally {
      setIsLoading(false);
    }
  }, [get, portfolioId]);

  const loadPerformance = useCallback(async () => {
    setIsPerfLoading(true);
    try {
      const data = await get<PortfolioPerformance>(
        `/portfolio/performance/${portfolioId}`,
        { period },
      );
      setPerformance(data);
    } catch {
      setPerformance(null);
    } finally {
      setIsPerfLoading(false);
    }
  }, [get, portfolioId, period]);

  useEffect(() => {
    loadPortfolio();
  }, [loadPortfolio]);

  useEffect(() => {
    loadPerformance();
  }, [loadPerformance]);

  async function handleRemoveHolding(holdingId: number) {
    setRemovingId(holdingId);
    try {
      await del(`/portfolio/assets/${holdingId}`);
      toast.success("Holding removed.");
      setPortfolio((prev) =>
        prev
          ? { ...prev, assets: prev.assets.filter((a) => a.id !== holdingId) }
          : prev,
      );
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Could not remove holding.",
      );
    } finally {
      setRemovingId(null);
    }
  }

  async function handleDeletePortfolio() {
    setIsDeleting(true);
    try {
      await del(`/portfolio/${portfolioId}`);
      toast.success("Portfolio deleted.");
      router.push("/portfolio");
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Could not delete portfolio.",
      );
      setIsDeleting(false);
    }
  }

  if (error) {
    return (
      <div className="space-y-6">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/portfolio">
            <ArrowLeft className="h-4 w-4" /> Back to portfolios
          </Link>
        </Button>
        <ErrorState message={error} onRetry={loadPortfolio} />
      </div>
    );
  }

  const totalValue =
    portfolio?.assets.reduce(
      (sum, a) => sum + (a.current_value ?? a.quantity * a.purchase_price),
      0,
    ) || 0;
  const totalCost =
    portfolio?.assets.reduce(
      (sum, a) => sum + a.quantity * a.purchase_price,
      0,
    ) || 0;
  const totalReturn =
    totalCost > 0 ? ((totalValue - totalCost) / totalCost) * 100 : 0;

  const allocation =
    portfolio?.assets.map((holding) => {
      const asset = assetsById.get(holding.asset_id);
      const value =
        holding.current_value ?? holding.quantity * holding.purchase_price;
      return { name: asset?.symbol || `#${holding.asset_id}`, value };
    }) || [];

  return (
    <div className="space-y-6">
      <div>
        <Button variant="ghost" size="sm" asChild className="mb-2 -ml-2">
          <Link href="/portfolio">
            <ArrowLeft className="h-4 w-4" /> Back to portfolios
          </Link>
        </Button>
        <PageHeader
          title={isLoading ? "Loading..." : portfolio?.name || "Portfolio"}
          description={portfolio?.description || undefined}
          actions={
            portfolio && (
              <>
                <Badge variant="secondary">
                  {riskLabels[portfolio.risk_level] || portfolio.risk_level}
                </Badge>
                <AddAssetDialog
                  portfolioId={portfolioId}
                  assets={assets}
                  isLoadingAssets={assetsLoading}
                  onAdded={(holding) =>
                    setPortfolio((prev) =>
                      prev
                        ? { ...prev, assets: [...prev.assets, holding] }
                        : prev,
                    )
                  }
                />
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="outline"
                      size="icon"
                      className="text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>
                        Delete this portfolio?
                      </AlertDialogTitle>
                      <AlertDialogDescription>
                        This will permanently remove &quot;{portfolio.name}
                        &quot; and its holdings. This action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        disabled={isDeleting}
                        onClick={handleDeletePortfolio}
                      >
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </>
            )
          }
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Current value"
          value={formatCurrency(totalValue)}
          change={totalReturn}
          icon={Wallet}
          isLoading={isLoading}
        />
        <StatCard
          label="Sharpe ratio"
          value={performance ? performance.sharpe_ratio.toFixed(2) : "N/A"}
          isLoading={isPerfLoading}
          icon={BarChart3}
        />
        <StatCard
          label="Volatility"
          value={performance ? `${performance.volatility.toFixed(1)}%` : "N/A"}
          isLoading={isPerfLoading}
        />
        <StatCard
          label="Max drawdown"
          value={
            performance ? `${performance.max_drawdown.toFixed(1)}%` : "N/A"
          }
          isLoading={isPerfLoading}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="font-display">Performance metrics</CardTitle>
            <Tabs value={period} onValueChange={setPeriod}>
              <TabsList>
                {periods.map((p) => (
                  <TabsTrigger
                    key={p.value}
                    value={p.value}
                    className="text-xs"
                  >
                    {p.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </CardHeader>
          <CardContent>
            {isPerfLoading ? (
              <Skeleton className="h-40 w-full" />
            ) : performance ? (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                <MetricTile
                  label="Return"
                  value={`${performance.return_percentage.toFixed(2)}%`}
                />
                <MetricTile
                  label="Benchmark return"
                  value={`${performance.benchmark_return.toFixed(2)}%`}
                />
                <MetricTile
                  label="Alpha"
                  value={performance.alpha.toFixed(2)}
                />
                <MetricTile label="Beta" value={performance.beta.toFixed(2)} />
                <MetricTile
                  label="Start value"
                  value={formatCurrency(performance.start_value)}
                />
                <MetricTile
                  label="End value"
                  value={formatCurrency(performance.end_value)}
                />
              </div>
            ) : (
              <EmptyState
                icon={BarChart3}
                title="No performance data"
                description="Metrics will appear once this portfolio has enough history."
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-display">Allocation</CardTitle>
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
                description="Add your first asset to see allocation."
              />
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="font-display">Holdings</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Skeleton className="h-56 w-full" />
          ) : portfolio && portfolio.assets.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Asset</TableHead>
                    <TableHead className="text-right">Quantity</TableHead>
                    <TableHead className="text-right">Avg. cost</TableHead>
                    <TableHead className="text-right">Current price</TableHead>
                    <TableHead className="text-right">Value</TableHead>
                    <TableHead className="text-right">P&amp;L</TableHead>
                    <TableHead className="w-10" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {portfolio.assets.map((holding: PortfolioAsset) => {
                    const asset = assetsById.get(holding.asset_id);
                    const value =
                      holding.current_value ??
                      holding.quantity * holding.purchase_price;
                    const pnl =
                      holding.unrealized_pnl ??
                      value - holding.quantity * holding.purchase_price;
                    const pnlPct =
                      holding.unrealized_pnl_pct ??
                      (holding.purchase_price > 0
                        ? (pnl / (holding.quantity * holding.purchase_price)) *
                          100
                        : 0);
                    return (
                      <TableRow key={holding.id}>
                        <TableCell>
                          <p className="font-medium">
                            {asset?.symbol || `#${holding.asset_id}`}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {asset?.name || "Unknown asset"}
                          </p>
                        </TableCell>
                        <TableCell className="text-right">
                          {formatNumber(holding.quantity)}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(holding.purchase_price)}
                        </TableCell>
                        <TableCell className="text-right">
                          {holding.current_price != null
                            ? formatCurrency(holding.current_price)
                            : asset?.current_price != null
                              ? formatCurrency(asset.current_price)
                              : "N/A"}
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(value)}
                        </TableCell>
                        <TableCell className="text-right">
                          <ChangeBadge value={pnlPct} showIcon={false} />
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-muted-foreground hover:text-destructive"
                            disabled={removingId === holding.id}
                            onClick={() => handleRemoveHolding(holding.id)}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          ) : (
            <EmptyState
              icon={Wallet}
              title="No holdings yet"
              description="Add an asset to start tracking this portfolio's performance."
              action={
                <AddAssetDialog
                  portfolioId={portfolioId}
                  assets={assets}
                  isLoadingAssets={assetsLoading}
                  onAdded={(holding) =>
                    setPortfolio((prev) =>
                      prev
                        ? { ...prev, assets: [...prev.assets, holding] }
                        : prev,
                    )
                  }
                />
              }
            />
          )}
        </CardContent>
      </Card>

      {portfolio && (
        <p className="text-xs text-muted-foreground">
          Created {formatDate(portfolio.created_at)}
        </p>
      )}
    </div>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-muted/50 p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 font-display text-sm font-semibold">{value}</p>
    </div>
  );
}

export default function PortfolioDetailPage() {
  const params = useParams<{ id: string }>();
  const portfolioId = Number(params.id);

  return (
    <AppShell>
      <PortfolioDetailContent portfolioId={portfolioId} />
    </AppShell>
  );
}
