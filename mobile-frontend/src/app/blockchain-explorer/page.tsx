"use client";

import { useEffect, useState } from "react";
import {
  Blocks,
  Coins,
  ExternalLink,
  Loader2,
  Search,
  ShieldCheck,
  Wallet,
} from "lucide-react";
import { toast } from "sonner";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AppShell } from "@/components/layout/app-shell";
import { PageHeader } from "@/components/finance/page-header";
import { EmptyState, ErrorState } from "@/components/finance/empty-state";
import { useApi, ApiError } from "@/lib/api";
import { useBlockchain } from "@/lib/blockchain";
import {
  formatCurrency,
  formatDateWithTime,
  shortenAddress,
} from "@/lib/utils";
import type {
  BlockchainNetworksResponse,
  BlockchainTransaction,
  SmartContract,
  TokenizedAssetsResponse,
  WalletBalance,
} from "@/lib/types";

const statusStyle: Record<string, string> = {
  confirmed: "bg-success/10 text-success hover:bg-success/10",
  completed: "bg-success/10 text-success hover:bg-success/10",
  pending: "bg-warning/10 text-warning hover:bg-warning/10",
  failed: "bg-destructive/10 text-destructive hover:bg-destructive/10",
};

function WalletCard() {
  const {
    account,
    isConnected,
    isConnecting,
    connectWallet,
    disconnectWallet,
    error,
  } = useBlockchain();
  const { get } = useApi();
  const [balance, setBalance] = useState<WalletBalance | null>(null);
  const [manualAddress, setManualAddress] = useState("");
  const [isLookingUp, setIsLookingUp] = useState(false);

  async function lookupBalance(address: string) {
    if (!address) return;
    setIsLookingUp(true);
    try {
      const data = await get<WalletBalance>(
        `/blockchain/wallet/${address}/balance`,
      );
      setBalance(data);
    } catch (err) {
      toast.error(
        err instanceof ApiError
          ? err.message
          : "Could not fetch wallet balance.",
      );
    } finally {
      setIsLookingUp(false);
    }
  }

  useEffect(() => {
    if (account) lookupBalance(account);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [account]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2">
        <Wallet className="h-4 w-4 text-primary" />
        <CardTitle className="font-display">Wallet</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isConnected && account ? (
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border/60 p-3">
            <div>
              <p className="text-sm font-medium">{shortenAddress(account)}</p>
              <p className="text-xs text-muted-foreground">Connected</p>
            </div>
            <Button variant="outline" size="sm" onClick={disconnectWallet}>
              Disconnect
            </Button>
          </div>
        ) : (
          <Button
            onClick={connectWallet}
            disabled={isConnecting}
            className="w-full"
          >
            {isConnecting && <Loader2 className="h-4 w-4 animate-spin" />}
            Connect wallet
          </Button>
        )}
        {error && <p className="text-xs text-destructive">{error}</p>}

        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Or paste any wallet address..."
              value={manualAddress}
              onChange={(e) => setManualAddress(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button
            variant="outline"
            disabled={isLookingUp || !manualAddress}
            onClick={() => lookupBalance(manualAddress)}
          >
            {isLookingUp ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "Look up"
            )}
          </Button>
        </div>

        {balance && (
          <div>
            <p className="text-sm text-muted-foreground">Total value</p>
            <p className="font-display text-2xl font-semibold">
              {formatCurrency(balance.total_value_usd)}
            </p>
            <div className="mt-3 space-y-2">
              {Object.entries(balance.balances).map(([token, info]) => (
                <div
                  key={token}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="font-medium">{token}</span>
                  <span className="text-muted-foreground">
                    {info.balance} · {formatCurrency(info.value_usd)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function BlockchainExplorerContent() {
  const { get } = useApi();
  const [networks, setNetworks] = useState<BlockchainNetworksResponse | null>(
    null,
  );
  const [network, setNetwork] = useState<string>("");
  const [contracts, setContracts] = useState<SmartContract[]>([]);
  const [transactions, setTransactions] = useState<BlockchainTransaction[]>([]);
  const [tokenizedAssets, setTokenizedAssets] =
    useState<TokenizedAssetsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load(selectedNetwork?: string) {
    setIsLoading(true);
    setError(null);
    try {
      const [networksRes, contractsRes, txRes, tokensRes] = await Promise.all([
        networks
          ? Promise.resolve(networks)
          : get<BlockchainNetworksResponse>("/blockchain/networks"),
        get<SmartContract[]>("/blockchain/contracts/", {
          network: selectedNetwork || undefined,
          limit: 20,
        }),
        get<BlockchainTransaction[]>("/blockchain/transactions/", {
          network: selectedNetwork || undefined,
          limit: 10,
        }),
        get<TokenizedAssetsResponse>("/blockchain/tokenization/assets"),
      ]);
      setNetworks(networksRes);
      setContracts(contractsRes);
      setTransactions(txRes);
      setTokenizedAssets(tokensRes);
    } catch {
      setError("We couldn't load blockchain data right now.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (network) load(network);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [network]);

  if (error)
    return <ErrorState message={error} onRetry={() => load(network)} />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Blockchain explorer"
        description="Smart contracts, on-chain transactions, and tokenized real-world assets."
        actions={
          networks && (
            <Select value={network} onValueChange={setNetwork}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All networks" />
              </SelectTrigger>
              <SelectContent>
                {networks.networks.map((n) => (
                  <SelectItem key={n.id} value={n.id}>
                    {n.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <WalletCard />

        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center gap-2">
            <Coins className="h-4 w-4 text-primary" />
            <CardTitle className="font-display">Tokenized assets</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-40 w-full" />
            ) : tokenizedAssets?.data.length ? (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Token</TableHead>
                      <TableHead>Underlying</TableHead>
                      <TableHead className="text-right">Price</TableHead>
                      <TableHead className="text-right">Market cap</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {tokenizedAssets.data.map((token) => (
                      <TableRow key={token.token_symbol}>
                        <TableCell>
                          <p className="font-medium">{token.token_symbol}</p>
                          <p className="text-xs text-muted-foreground">
                            {token.name}
                          </p>
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {token.underlying_asset}
                        </TableCell>
                        <TableCell className="text-right">
                          {formatCurrency(token.price_per_token)}
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(token.market_cap)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            ) : (
              <EmptyState icon={Coins} title="No tokenized assets found" />
            )}
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="transactions">
        <TabsList>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="contracts">Smart contracts</TabsTrigger>
        </TabsList>

        <TabsContent value="transactions" className="mt-6">
          <Card>
            <CardContent className="p-0">
              {isLoading ? (
                <div className="space-y-2 p-6">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-10 w-full" />
                  ))}
                </div>
              ) : transactions.length === 0 ? (
                <div className="p-6">
                  <EmptyState icon={Blocks} title="No transactions found" />
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Hash</TableHead>
                        <TableHead>From → To</TableHead>
                        <TableHead className="text-right">Value</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Timestamp</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {transactions.map((tx) => (
                        <TableRow key={tx.id}>
                          <TableCell className="font-mono text-xs">
                            {shortenAddress(tx.tx_hash)}
                          </TableCell>
                          <TableCell className="font-mono text-xs text-muted-foreground">
                            {shortenAddress(tx.from_address)} →{" "}
                            {shortenAddress(tx.to_address)}
                          </TableCell>
                          <TableCell className="text-right font-medium">
                            {tx.value.toFixed(4)}
                          </TableCell>
                          <TableCell>
                            <Badge className={statusStyle[tx.status] || ""}>
                              {tx.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground">
                            {formatDateWithTime(tx.timestamp)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="contracts" className="mt-6">
          {isLoading ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-32 w-full" />
              ))}
            </div>
          ) : contracts.length === 0 ? (
            <EmptyState icon={ShieldCheck} title="No smart contracts found" />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {contracts.map((contract) => (
                <Card key={contract.id} className="card-hover">
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-display text-sm font-semibold">
                          {contract.name}
                        </p>
                        <p className="text-xs capitalize text-muted-foreground">
                          {contract.contract_type} · {contract.network}
                        </p>
                      </div>
                      {contract.is_verified && (
                        <Badge className="bg-success/10 text-success hover:bg-success/10">
                          <ShieldCheck className="mr-1 h-3 w-3" /> Verified
                        </Badge>
                      )}
                    </div>
                    <div className="mt-3 flex items-center gap-1.5 font-mono text-xs text-muted-foreground">
                      {shortenAddress(contract.address)}
                      <ExternalLink className="h-3 w-3" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function BlockchainExplorerPage() {
  return (
    <AppShell>
      <BlockchainExplorerContent />
    </AppShell>
  );
}
