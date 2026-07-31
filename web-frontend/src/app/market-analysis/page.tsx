"use client";

import { useEffect, useRef, useState } from "react";
import { Newspaper, Search, TrendingUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/finance/page-header";
import { ChangeBadge } from "@/components/finance/change-badge";
import { PerformanceBarChart } from "@/components/finance/bar-chart";
import { TrendChart } from "@/components/finance/trend-chart";
import { EmptyState, ErrorState } from "@/components/finance/empty-state";
import { useApi } from "@/lib/api";
import { formatCurrency, formatDateWithTime } from "@/lib/utils";
import type {
  Asset,
  AssetPriceHistory,
  MarketNewsResponse,
  MarketSummary,
  SectorPerformanceResponse,
} from "@/lib/types";

const sentimentStyle: Record<string, string> = {
  bullish: "bg-success/10 text-success hover:bg-success/10",
  bearish: "bg-destructive/10 text-destructive hover:bg-destructive/10",
  neutral: "bg-muted text-muted-foreground",
};

function OverviewTab() {
  const { get } = useApi();
  const [summary, setSummary] = useState<MarketSummary | null>(null);
  const [sectors, setSectors] = useState<SectorPerformanceResponse | null>(
    null,
  );
  const [news, setNews] = useState<MarketNewsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const [s, sec, n] = await Promise.all([
        get<MarketSummary>("/market/market_summary"),
        get<SectorPerformanceResponse>("/market/sector_performance", {
          period: "1m",
        }),
        get<MarketNewsResponse>("/market/market_news", { limit: 6 }),
      ]);
      setSummary(s);
      setSectors(sec);
      setNews(n);
    } catch {
      setError("We couldn't load market data right now.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (error) return <ErrorState message={error} onRetry={load} />;

  const sentiment = summary?.market_sentiment;
  const sentimentTotal = sentiment
    ? sentiment.bullish + sentiment.neutral + sentiment.bearish
    : 0;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        {isLoading
          ? [1, 2, 3].map((i) => <Skeleton key={i} className="h-28 w-full" />)
          : summary?.indices.map((index) => (
              <Card key={index.name}>
                <CardContent className="p-5">
                  <p className="text-sm text-muted-foreground">{index.name}</p>
                  <p className="mt-1 font-display text-xl font-semibold">
                    {index.value.toLocaleString()}
                  </p>
                  <ChangeBadge value={index.change_percent} className="mt-2" />
                </CardContent>
              </Card>
            ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="font-display">
              Sector performance (1M)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-72 w-full" />
            ) : sectors?.data.length ? (
              <PerformanceBarChart data={sectors.data} height={320} />
            ) : (
              <EmptyState icon={TrendingUp} title="No sector data available" />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-display">Market sentiment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {isLoading ? (
              <Skeleton className="h-40 w-full" />
            ) : sentiment ? (
              <>
                {(
                  [
                    ["Bullish", sentiment.bullish, "bg-success"],
                    ["Neutral", sentiment.neutral, "bg-muted-foreground"],
                    ["Bearish", sentiment.bearish, "bg-destructive"],
                  ] as const
                ).map(([label, value, color]) => (
                  <div key={label}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">{label}</span>
                      <span className="font-medium">
                        {sentimentTotal
                          ? Math.round((value / sentimentTotal) * 100)
                          : 0}
                        %
                      </span>
                    </div>
                    <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className={`h-full ${color}`}
                        style={{
                          width: `${sentimentTotal ? (value / sentimentTotal) * 100 : 0}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </>
            ) : (
              <EmptyState icon={TrendingUp} title="No sentiment data" />
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center gap-2">
          <Newspaper className="h-4 w-4 text-primary" />
          <CardTitle className="font-display">Market news</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : news?.data.length ? (
            news.data.map((item) => (
              <div
                key={item.id}
                className="border-b border-border/60 py-3.5 last:border-0"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium">{item.title}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {item.summary}
                    </p>
                    <p className="mt-1.5 text-xs text-muted-foreground">
                      {item.source} · {item.time}
                    </p>
                  </div>
                  <Badge className={sentimentStyle[item.sentiment]}>
                    {item.sentiment}
                  </Badge>
                </div>
              </div>
            ))
          ) : (
            <EmptyState icon={Newspaper} title="No news available" />
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function AssetDetailSheet({
  asset,
  open,
  onOpenChange,
}: {
  asset: Asset | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const { get } = useApi();
  const [history, setHistory] = useState<AssetPriceHistory | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!asset || !open) return;
    setIsLoading(true);
    get<AssetPriceHistory>(`/market/assets/${asset.id}/price_history`, {
      period: "3m",
    })
      .then(setHistory)
      .catch(() => setHistory(null))
      .finally(() => setIsLoading(false));
  }, [asset, open, get]);

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
        <SheetHeader>
          <SheetTitle className="font-display">
            {asset?.symbol} · {asset?.name}
          </SheetTitle>
        </SheetHeader>
        {asset && (
          <div className="mt-6 space-y-6">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground">Current price</p>
                <p className="mt-1 font-display text-lg font-semibold">
                  {asset.current_price != null
                    ? formatCurrency(asset.current_price)
                    : "N/A"}
                </p>
              </div>
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground">Type</p>
                <p className="mt-1 font-display text-lg font-semibold capitalize">
                  {asset.asset_type}
                </p>
              </div>
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground">Exchange</p>
                <p className="mt-1 text-sm font-medium">
                  {asset.exchange || "N/A"}
                </p>
              </div>
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground">Sector</p>
                <p className="mt-1 text-sm font-medium">
                  {asset.sector || "N/A"}
                </p>
              </div>
            </div>

            {asset.description && (
              <p className="text-sm text-muted-foreground">
                {asset.description}
              </p>
            )}

            <div>
              <p className="mb-2 text-sm font-medium">Price history (3M)</p>
              {isLoading ? (
                <Skeleton className="h-56 w-full" />
              ) : history && history.data.length > 0 ? (
                <TrendChart
                  data={history.data.map((p) => ({
                    label: formatDateWithTime(p.timestamp).split(",")[0],
                    value: p.price,
                  }))}
                  height={220}
                />
              ) : (
                <EmptyState
                  icon={TrendingUp}
                  title="No historical data"
                  description="Price history hasn't been recorded for this asset yet."
                />
              )}
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}

function AssetsTab() {
  const { get } = useApi();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [sheetOpen, setSheetOpen] = useState(false);

  async function load(query?: string) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await get<Asset[]>("/market/assets/", {
        limit: 100,
        search: query || undefined,
      });
      setAssets(data);
    } catch {
      setError("We couldn't load the asset catalog.");
    } finally {
      setIsLoading(false);
    }
  }

  const isFirstRun = useRef(true);

  useEffect(() => {
    if (isFirstRun.current) {
      isFirstRun.current = false;
      load();
      return;
    }
    const timeout = setTimeout(() => load(search), 350);
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search]);

  return (
    <div className="space-y-4">
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search by symbol or name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      <Card>
        <CardContent className="p-0">
          {error ? (
            <div className="p-6">
              <ErrorState message={error} onRetry={() => load(search)} />
            </div>
          ) : isLoading ? (
            <div className="space-y-2 p-6">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : assets.length === 0 ? (
            <div className="p-6">
              <EmptyState
                icon={Search}
                title="No assets found"
                description="Try a different search term."
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Symbol</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Sector</TableHead>
                    <TableHead className="text-right">Price</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {assets.map((asset) => (
                    <TableRow
                      key={asset.id}
                      className="cursor-pointer"
                      onClick={() => {
                        setSelectedAsset(asset);
                        setSheetOpen(true);
                      }}
                    >
                      <TableCell className="font-medium">
                        {asset.symbol}
                      </TableCell>
                      <TableCell className="max-w-[220px] truncate text-muted-foreground">
                        {asset.name}
                      </TableCell>
                      <TableCell className="capitalize text-muted-foreground">
                        {asset.asset_type}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {asset.sector || "N/A"}
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {asset.current_price != null
                          ? formatCurrency(asset.current_price)
                          : "N/A"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <AssetDetailSheet
        asset={selectedAsset}
        open={sheetOpen}
        onOpenChange={setSheetOpen}
      />
    </div>
  );
}

function MarketAnalysisContent() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Market analysis"
        description="Live indices, sector momentum, and the full tradable asset catalog."
      />
      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="assets">Assets</TabsTrigger>
        </TabsList>
        <TabsContent value="overview" className="mt-6">
          <OverviewTab />
        </TabsContent>
        <TabsContent value="assets" className="mt-6">
          <AssetsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function MarketAnalysisPage() {
  return (
    <AppShell>
      <MarketAnalysisContent />
    </AppShell>
  );
}
