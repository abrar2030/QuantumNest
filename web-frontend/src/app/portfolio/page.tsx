"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Layers, Trash2, Wallet } from "lucide-react";
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
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/finance/page-header";
import { EmptyState, ErrorState } from "@/components/finance/empty-state";
import { ChangeBadge } from "@/components/finance/change-badge";
import { CreatePortfolioDialog } from "@/components/portfolio/create-portfolio-dialog";
import { ApiError, useApi } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import type { Portfolio, PortfolioSummary } from "@/lib/types";

const riskLabels: Record<string, string> = {
  very_low: "Very low risk",
  low: "Low risk",
  moderate: "Moderate risk",
  high: "High risk",
  very_high: "Very high risk",
};

function PortfolioListContent() {
  const { get, del } = useApi();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [summaries, setSummaries] = useState<Record<number, PortfolioSummary>>(
    {},
  );
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      const list = await get<Portfolio[]>("/portfolio/", { limit: 100 });
      setPortfolios(list);
      const entries = await Promise.all(
        list.map(async (p) => {
          try {
            const summary = await get<PortfolioSummary>(
              `/portfolio/summary/${p.id}`,
            );
            return [p.id, summary] as const;
          } catch {
            return null;
          }
        }),
      );
      setSummaries(
        Object.fromEntries(
          entries.filter((e): e is [number, PortfolioSummary] => e !== null),
        ),
      );
    } catch {
      setError("We couldn't load your portfolios right now.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleDelete(id: number) {
    setDeletingId(id);
    try {
      await del(`/portfolio/${id}`);
      toast.success("Portfolio deleted.");
      setPortfolios((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      toast.error(
        err instanceof ApiError ? err.message : "Could not delete portfolio.",
      );
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Portfolios"
        description="Create and manage portfolios across every asset class you hold."
        actions={
          <CreatePortfolioDialog
            onCreated={(p) => setPortfolios((prev) => [p, ...prev])}
          />
        }
      />

      {error ? (
        <ErrorState message={error} onRetry={load} />
      ) : isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-48 w-full" />
          ))}
        </div>
      ) : portfolios.length === 0 ? (
        <EmptyState
          icon={Wallet}
          title="No portfolios yet"
          description="Create your first portfolio to start tracking holdings, performance, and AI recommendations."
          action={
            <CreatePortfolioDialog
              onCreated={(p) => setPortfolios((prev) => [p, ...prev])}
            />
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {portfolios.map((portfolio) => {
            const summary = summaries[portfolio.id];
            const returnPct =
              summary && summary.total_cost > 0
                ? ((summary.total_value - summary.total_cost) /
                    summary.total_cost) *
                  100
                : 0;
            return (
              <Card key={portfolio.id} className="card-hover flex flex-col">
                <CardHeader className="flex-row items-start justify-between space-y-0 pb-2">
                  <div>
                    <Link
                      href={`/portfolio/${portfolio.id}`}
                      className="font-display text-base font-semibold hover:text-primary"
                    >
                      {portfolio.name}
                    </Link>
                    <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                      {portfolio.description || "No description provided."}
                    </p>
                  </div>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 shrink-0 text-muted-foreground hover:text-destructive"
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
                          disabled={deletingId === portfolio.id}
                          onClick={() => handleDelete(portfolio.id)}
                        >
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </CardHeader>
                <CardContent className="flex flex-1 flex-col justify-between gap-4">
                  <div>
                    <Badge variant="secondary">
                      {riskLabels[portfolio.risk_level] || portfolio.risk_level}
                    </Badge>
                  </div>
                  <div>
                    <p className="font-display text-2xl font-semibold">
                      {summary ? formatCurrency(summary.total_value) : "N/A"}
                    </p>
                    <div className="mt-1 flex items-center gap-2">
                      {summary && <ChangeBadge value={returnPct} />}
                      <span className="text-xs text-muted-foreground">
                        {summary?.total_assets ?? 0} holdings
                      </span>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="justify-between"
                    asChild
                  >
                    <Link href={`/portfolio/${portfolio.id}`}>
                      View details <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {!isLoading && portfolios.length > 0 && (
        <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Layers className="h-3.5 w-3.5" />
          {portfolios.length} portfolio{portfolios.length === 1 ? "" : "s"}{" "}
          total
        </p>
      )}
    </div>
  );
}

export default function PortfolioPage() {
  return (
    <AppShell>
      <PortfolioListContent />
    </AppShell>
  );
}
