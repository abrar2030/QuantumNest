"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  Gauge,
  Search,
  ShieldAlert,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/finance/page-header";
import { TrendChart } from "@/components/finance/trend-chart";
import { EmptyState, ErrorState } from "@/components/finance/empty-state";
import { useApi, ApiError } from "@/lib/api";
import { formatCurrency, formatPercentage } from "@/lib/utils";
import type {
  AssetSentiment,
  MarketRecommendations,
  Portfolio,
  PortfolioRecommendations,
  PortfolioRiskAnalysis,
} from "@/lib/types";

const recBadge: Record<string, string> = {
  buy: "bg-success/10 text-success hover:bg-success/10",
  sell: "bg-destructive/10 text-destructive hover:bg-destructive/10",
  hold: "bg-muted text-muted-foreground",
};

function MarketOutlookTab() {
  const { get } = useApi();
  const [data, setData] = useState<MarketRecommendations | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      setData(await get<MarketRecommendations>("/ai/recommendations/market"));
    } catch {
      setError("AI market recommendations are unavailable right now.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isLoading) return <Skeleton className="h-96 w-full" />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        {(
          [
            ["Short term", data.market_outlook.short_term],
            ["Medium term", data.market_outlook.medium_term],
            ["Long term", data.market_outlook.long_term],
          ] as const
        ).map(([label, outlook]) => (
          <Card key={label}>
            <CardContent className="p-5">
              <p className="text-sm text-muted-foreground">{label}</p>
              <p className="mt-1 font-display text-lg font-semibold capitalize">
                {outlook}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="font-display">Sector outlook</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.sector_recommendations.map((sector) => (
              <div
                key={sector.sector}
                className="flex items-center justify-between rounded-lg border border-border/60 p-3"
              >
                <div>
                  <p className="text-sm font-medium">{sector.sector}</p>
                  <p className="text-xs text-muted-foreground">
                    Confidence {Math.round(sector.confidence * 100)}%
                  </p>
                </div>
                <Badge variant="outline" className="capitalize">
                  {sector.outlook}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="font-display">Asset calls</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.asset_recommendations.map((rec) => (
              <div
                key={rec.asset_symbol}
                className="flex items-center justify-between rounded-lg border border-border/60 p-3"
              >
                <div>
                  <p className="text-sm font-medium">{rec.asset_symbol}</p>
                  <p className="text-xs text-muted-foreground">
                    Target {formatCurrency(rec.target_price)} ·{" "}
                    {rec.time_horizon}
                  </p>
                </div>
                <Badge className={recBadge[rec.recommendation] || ""}>
                  {rec.recommendation}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="font-display">
            Economic indicator forecasts
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {data.economic_indicators_forecast.map((indicator) => (
            <div
              key={indicator.indicator}
              className="rounded-lg bg-muted/50 p-3.5"
            >
              <p className="text-xs text-muted-foreground">
                {indicator.indicator}
              </p>
              <p className="mt-1 font-display text-lg font-semibold">
                {indicator.forecast}
              </p>
              <p className="text-xs text-muted-foreground">
                Previous: {indicator.previous}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function usePortfolios() {
  const { get } = useApi();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    get<Portfolio[]>("/portfolio/", { limit: 100 })
      .then(setPortfolios)
      .finally(() => setIsLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { portfolios, isLoading };
}

function PortfolioSelector({
  portfolios,
  value,
  onChange,
}: {
  portfolios: Portfolio[];
  value: string;
  onChange: (value: string) => void;
}) {
  if (portfolios.length === 0) return null;
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-64">
        <SelectValue placeholder="Choose a portfolio" />
      </SelectTrigger>
      <SelectContent>
        {portfolios.map((p) => (
          <SelectItem key={p.id} value={String(p.id)}>
            {p.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

function PortfolioInsightsTab() {
  const { get } = useApi();
  const { portfolios, isLoading: portfoliosLoading } = usePortfolios();
  const [portfolioId, setPortfolioId] = useState<string>("");
  const [data, setData] = useState<PortfolioRecommendations | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!portfolioId && portfolios.length > 0)
      setPortfolioId(String(portfolios[0].id));
  }, [portfolios, portfolioId]);

  useEffect(() => {
    if (!portfolioId) return;
    setIsLoading(true);
    setError(null);
    get<PortfolioRecommendations>(
      `/ai/recommendations/portfolio/${portfolioId}`,
    )
      .then(setData)
      .catch((err) =>
        setError(
          err instanceof ApiError
            ? err.message
            : "Portfolio recommendations are unavailable right now.",
        ),
      )
      .finally(() => setIsLoading(false));
  }, [portfolioId, get]);

  if (portfoliosLoading) return <Skeleton className="h-72 w-full" />;
  if (portfolios.length === 0) {
    return (
      <EmptyState
        icon={Sparkles}
        title="No portfolios yet"
        description="Create a portfolio first to get personalized AI recommendations."
      />
    );
  }

  return (
    <div className="space-y-6">
      <PortfolioSelector
        portfolios={portfolios}
        value={portfolioId}
        onChange={setPortfolioId}
      />

      {isLoading ? (
        <Skeleton className="h-96 w-full" />
      ) : error ? (
        <ErrorState message={error} />
      ) : data ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardContent className="p-5">
                <p className="text-sm text-muted-foreground">
                  Current risk score
                </p>
                <p className="mt-1 font-display text-2xl font-semibold">
                  {data.risk_assessment.current_risk_score}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-5">
                <p className="text-sm text-muted-foreground">
                  Recommended risk score
                </p>
                <p className="mt-1 font-display text-2xl font-semibold">
                  {data.risk_assessment.recommended_risk_score}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-5">
                <p className="text-sm text-muted-foreground">Current Sharpe</p>
                <p className="mt-1 font-display text-2xl font-semibold">
                  {data.expected_performance.current_sharpe_ratio.toFixed(2)}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-5">
                <p className="text-sm text-muted-foreground">
                  Recommended Sharpe
                </p>
                <p className="mt-1 font-display text-2xl font-semibold">
                  {data.expected_performance.recommended_sharpe_ratio.toFixed(
                    2,
                  )}
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="font-display">
                  Rebalancing suggestions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {data.rebalance_recommendations.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    Your portfolio is already well balanced.
                  </p>
                ) : (
                  data.rebalance_recommendations.map((rec) => (
                    <div
                      key={rec.asset_symbol}
                      className="flex items-center justify-between rounded-lg border border-border/60 p-3"
                    >
                      <div>
                        <p className="text-sm font-medium">
                          {rec.asset_symbol}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatPercentage(rec.current_allocation)} →{" "}
                          {formatPercentage(rec.recommended_allocation)}
                        </p>
                      </div>
                      <Badge variant="outline" className="capitalize">
                        {rec.action}
                      </Badge>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="font-display">New asset ideas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {data.new_asset_recommendations.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    No new asset suggestions at this time.
                  </p>
                ) : (
                  data.new_asset_recommendations.map((rec) => (
                    <div
                      key={rec.asset_symbol}
                      className="rounded-lg border border-border/60 p-3"
                    >
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium">
                          {rec.asset_symbol}
                        </p>
                        <Badge variant="outline">
                          {formatPercentage(rec.recommended_allocation)}
                        </Badge>
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {rec.reason}
                      </p>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          </div>
        </>
      ) : null}
    </div>
  );
}

function SentimentTab() {
  const { get } = useApi();
  const [symbol, setSymbol] = useState("AAPL");
  const [queryInput, setQueryInput] = useState("AAPL");
  const [data, setData] = useState<AssetSentiment | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) return;
    setIsLoading(true);
    setError(null);
    get<AssetSentiment>(`/ai/sentiment/asset/${symbol.toUpperCase()}`)
      .then(setData)
      .catch((err) =>
        setError(
          err instanceof ApiError
            ? err.message
            : "Sentiment data is unavailable for this asset.",
        ),
      )
      .finally(() => setIsLoading(false));
  }, [symbol, get]);

  return (
    <div className="space-y-6">
      <form
        className="flex max-w-sm gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          setSymbol(queryInput.trim());
        }}
      >
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            placeholder="Asset symbol, e.g. AAPL"
            className="pl-9 uppercase"
          />
        </div>
        <Button type="submit">Analyze</Button>
      </form>

      {isLoading ? (
        <Skeleton className="h-80 w-full" />
      ) : error ? (
        <ErrorState message={error} />
      ) : data ? (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <Card>
              <CardContent className="p-5">
                <p className="text-sm text-muted-foreground">
                  Overall sentiment
                </p>
                <p className="mt-1 font-display text-xl font-semibold capitalize">
                  {data.overall_sentiment.label}
                </p>
                <p className="text-xs text-muted-foreground">
                  Score {data.overall_sentiment.score.toFixed(2)} · Confidence{" "}
                  {Math.round(data.overall_sentiment.confidence * 100)}%
                </p>
              </CardContent>
            </Card>
            {Object.entries(data.sentiment_breakdown)
              .slice(0, 2)
              .map(([source, breakdown]) => (
                <Card key={source}>
                  <CardContent className="p-5">
                    <p className="text-sm capitalize text-muted-foreground">
                      {source}
                    </p>
                    <p className="mt-1 font-display text-xl font-semibold">
                      {breakdown.score.toFixed(2)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {breakdown.sources_analyzed} sources analyzed
                    </p>
                  </CardContent>
                </Card>
              ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="font-display">Sentiment trend</CardTitle>
            </CardHeader>
            <CardContent>
              <TrendChart
                data={data.sentiment_trend.map((point) => ({
                  label: point.date,
                  value: point.score,
                }))}
                valuePrefix=""
                height={220}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="font-display">Key insights</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {data.key_insights.map((insight, i) => (
                  <li key={i} className="flex gap-2 text-sm">
                    <Sparkles className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                    {insight}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  );
}

function RiskAnalysisTab() {
  const { get } = useApi();
  const { portfolios, isLoading: portfoliosLoading } = usePortfolios();
  const [portfolioId, setPortfolioId] = useState<string>("");
  const [data, setData] = useState<PortfolioRiskAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!portfolioId && portfolios.length > 0)
      setPortfolioId(String(portfolios[0].id));
  }, [portfolios, portfolioId]);

  useEffect(() => {
    if (!portfolioId) return;
    setIsLoading(true);
    setError(null);
    get<PortfolioRiskAnalysis>(`/ai/risk/portfolio/${portfolioId}`)
      .then(setData)
      .catch((err) =>
        setError(
          err instanceof ApiError
            ? err.message
            : "Risk analysis is unavailable right now.",
        ),
      )
      .finally(() => setIsLoading(false));
  }, [portfolioId, get]);

  if (portfoliosLoading) return <Skeleton className="h-72 w-full" />;
  if (portfolios.length === 0) {
    return (
      <EmptyState
        icon={ShieldAlert}
        title="No portfolios yet"
        description="Create a portfolio first to run a risk analysis."
      />
    );
  }

  return (
    <div className="space-y-6">
      <PortfolioSelector
        portfolios={portfolios}
        value={portfolioId}
        onChange={setPortfolioId}
      />

      {isLoading ? (
        <Skeleton className="h-96 w-full" />
      ) : error ? (
        <ErrorState message={error} />
      ) : data ? (
        <>
          <Card>
            <CardContent className="flex items-center gap-4 p-6">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-2xl font-bold text-primary">
                {data.overall_risk_score}
              </div>
              <div>
                <p className="font-display text-base font-semibold">
                  Overall risk score
                </p>
                <p className="text-sm text-muted-foreground">Out of 100</p>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-6">
            {(
              [
                ["Volatility", `${data.risk_metrics.volatility}%`],
                ["Beta", data.risk_metrics.beta],
                ["VaR", `${data.risk_metrics.value_at_risk}%`],
                ["Max drawdown", `${data.risk_metrics.max_drawdown}%`],
                ["Sharpe", data.risk_metrics.sharpe_ratio],
                ["Sortino", data.risk_metrics.sortino_ratio],
              ] as const
            ).map(([label, value]) => (
              <div key={label} className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="mt-1 font-display text-sm font-semibold">
                  {value}
                </p>
              </div>
            ))}
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="font-display">Risk breakdown</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {Object.entries(data.risk_breakdown).map(([key, value]) => (
                  <div key={key}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="capitalize text-muted-foreground">
                        {key.replace(/_/g, " ")}
                      </span>
                      <span className="font-medium">{value}%</span>
                    </div>
                    <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full bg-primary"
                        style={{ width: `${Math.min(value, 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-warning" />
                <CardTitle className="font-display">
                  Stress test scenarios
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {data.stress_test_scenarios.map((scenario) => (
                  <div
                    key={scenario.scenario}
                    className="flex items-center justify-between rounded-lg border border-border/60 p-3"
                  >
                    <p className="text-sm">{scenario.scenario}</p>
                    <span
                      className={
                        scenario.portfolio_impact < 0
                          ? "flex items-center gap-1 text-sm font-medium text-destructive"
                          : "flex items-center gap-1 text-sm font-medium text-success"
                      }
                    >
                      {scenario.portfolio_impact < 0 ? (
                        <TrendingDown className="h-3.5 w-3.5" />
                      ) : (
                        <TrendingUp className="h-3.5 w-3.5" />
                      )}
                      {scenario.portfolio_impact}%
                    </span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader className="flex flex-row items-center gap-2">
              <Gauge className="h-4 w-4 text-primary" />
              <CardTitle className="font-display">
                Risk mitigation recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {data.risk_mitigation_recommendations.map((rec, i) => (
                  <li key={i} className="flex gap-2 text-sm">
                    <Sparkles className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                    {rec}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  );
}

function RecommendationsContent() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Insights"
        description="Transformer-driven market outlook, portfolio optimization, and risk intelligence."
      />
      <Tabs defaultValue="market">
        <TabsList className="flex-wrap">
          <TabsTrigger value="market">Market outlook</TabsTrigger>
          <TabsTrigger value="portfolio">Portfolio insights</TabsTrigger>
          <TabsTrigger value="sentiment">Asset sentiment</TabsTrigger>
          <TabsTrigger value="risk">Risk analysis</TabsTrigger>
        </TabsList>
        <TabsContent value="market" className="mt-6">
          <MarketOutlookTab />
        </TabsContent>
        <TabsContent value="portfolio" className="mt-6">
          <PortfolioInsightsTab />
        </TabsContent>
        <TabsContent value="sentiment" className="mt-6">
          <SentimentTab />
        </TabsContent>
        <TabsContent value="risk" className="mt-6">
          <RiskAnalysisTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function RecommendationsPage() {
  return (
    <AppShell>
      <RecommendationsContent />
    </AppShell>
  );
}
