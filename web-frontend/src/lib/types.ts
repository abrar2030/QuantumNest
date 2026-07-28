// Types mirror code/backend/app/schemas/schemas.py

export type UserRole =
  | "admin"
  | "portfolio_manager"
  | "analyst"
  | "user"
  | "api_user";

export type UserTier =
  | "basic"
  | "premium"
  | "professional"
  | "enterprise"
  | "institutional";

export type UserStatus = "active" | "inactive" | "suspended" | "pending_verification";

export type RiskLevel = "very_low" | "low" | "moderate" | "high" | "very_high";

export type TransactionType =
  | "buy"
  | "sell"
  | "deposit"
  | "withdrawal"
  | "dividend"
  | "split"
  | "merger"
  | "transfer";

export type TransactionStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled"
  | "rejected";

export interface User {
  id: number;
  email: string;
  username: string | null;
  first_name: string;
  last_name: string;
  role: UserRole;
  tier: UserTier;
  status: UserStatus;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface RegisterInput {
  email: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  password: string;
}

export interface Portfolio {
  id: number;
  name: string;
  description: string | null;
  risk_level: RiskLevel;
  investment_strategy: string | null;
  base_currency: string;
  owner_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface PortfolioAsset {
  id: number;
  portfolio_id: number;
  asset_id: number;
  quantity: number;
  purchase_price: number;
  purchase_date: string | null;
  target_weight: number | null;
  current_price: number | null;
  current_value: number | null;
  unrealized_pnl: number | null;
  unrealized_pnl_pct: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface PortfolioWithAssets extends Portfolio {
  assets: PortfolioAsset[];
}

export interface PortfolioPerformance {
  portfolio_id: number;
  portfolio_name: string;
  period: string;
  start_value: number;
  end_value: number;
  return_percentage: number;
  benchmark_return: number;
  alpha: number;
  beta: number;
  sharpe_ratio: number;
  volatility: number;
  max_drawdown: number;
  total_assets: number;
  data_points: Array<{ date: string; value: number }>;
  timestamp: string;
}

export interface PortfolioSummary {
  portfolio_id: number;
  name: string;
  risk_level: string;
  base_currency: string;
  total_assets: number;
  total_value: number;
  total_cost: number;
  is_active: boolean;
  created_at: string | null;
}

export interface Asset {
  id: number;
  symbol: string;
  name: string;
  asset_type: string;
  description: string | null;
  exchange: string | null;
  currency: string;
  sector: string | null;
  current_price: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface AssetPricePoint {
  timestamp: string;
  price: number;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
}

export interface AssetPriceHistory {
  asset_id: number;
  symbol: string;
  name: string;
  period: string;
  count: number;
  data: AssetPricePoint[];
}

export interface Transaction {
  id: number;
  user_id: number;
  asset_id: number | null;
  portfolio_id: number | null;
  transaction_type: TransactionType;
  amount: number;
  quantity: number | null;
  price: number | null;
  fees: number;
  currency: string;
  notes: string | null;
  status: TransactionStatus;
  created_at: string;
  updated_at: string | null;
}

export interface MarketIndex {
  name: string;
  value: number;
  change: number;
  change_percent: number;
}

export interface MarketSummary {
  indices: MarketIndex[];
  sectors: Array<{ name: string; change_percent: number }>;
  economic_indicators: Array<{ name: string; value: number; previous: number }>;
  market_sentiment: { bullish: number; neutral: number; bearish: number };
  timestamp: string;
}

export interface MarketNewsItem {
  id: number;
  title: string;
  source: string;
  time: string;
  summary: string;
  sentiment: "bullish" | "bearish" | "neutral";
}

export interface MarketNewsResponse {
  count: number;
  data: MarketNewsItem[];
}

export interface SectorPerformanceItem {
  name: string;
  value: number;
}

export interface SectorPerformanceResponse {
  period: string;
  data: SectorPerformanceItem[];
  timestamp: string;
}

export interface PortfolioCreateInput {
  name: string;
  description?: string;
  risk_level?: RiskLevel;
  investment_strategy?: string;
  base_currency?: string;
}

export interface PortfolioAssetCreateInput {
  portfolio_id: number;
  asset_id: number;
  quantity: number;
  purchase_price: number;
  purchase_date?: string;
  target_weight?: number;
}

export interface TransactionCreateInput {
  asset_id?: number;
  portfolio_id?: number;
  transaction_type: TransactionType;
  amount: number;
  quantity?: number;
  price?: number;
  fees?: number;
  currency?: string;
  notes?: string;
}

export interface AIModel {
  id: number;
  name: string;
  description: string | null;
  model_type: string;
  accuracy: number | null;
  version: string;
  is_active: boolean;
  is_trained: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface MarketRecommendations {
  timestamp: string;
  market_outlook: {
    short_term: string;
    medium_term: string;
    long_term: string;
    confidence: number;
  };
  sector_recommendations: Array<{
    sector: string;
    outlook: string;
    confidence: number;
  }>;
  asset_recommendations: Array<{
    asset_symbol: string;
    recommendation: string;
    target_price: number;
    confidence: number;
    time_horizon: string;
  }>;
  economic_indicators_forecast: Array<{
    indicator: string;
    forecast: number;
    previous: number;
    confidence: number;
  }>;
}

export interface PortfolioRecommendations {
  portfolio_id: number;
  timestamp: string;
  rebalance_recommendations: Array<{
    asset_symbol: string;
    current_allocation: number;
    recommended_allocation: number;
    action: string;
  }>;
  new_asset_recommendations: Array<{
    asset_symbol: string;
    recommended_allocation: number;
    reason: string;
  }>;
  risk_assessment: {
    current_risk_score: number;
    recommended_risk_score: number;
    volatility: string;
    diversification_score: number;
  };
  expected_performance: {
    current_expected_return: number;
    recommended_expected_return: number;
    current_sharpe_ratio: number;
    recommended_sharpe_ratio: number;
  };
}

export interface AssetSentiment {
  asset_symbol: string;
  timestamp: string;
  overall_sentiment: { score: number; label: string; confidence: number };
  sentiment_breakdown: Record<
    string,
    { score: number; sources_analyzed: number; key_topics: string[] }
  >;
  sentiment_trend: Array<{ date: string; score: number }>;
  key_insights: string[];
}

export interface PortfolioRiskAnalysis {
  portfolio_id: number;
  timestamp: string;
  overall_risk_score: number;
  risk_metrics: {
    volatility: number;
    beta: number;
    value_at_risk: number;
    max_drawdown: number;
    sharpe_ratio: number;
    sortino_ratio: number;
  };
  risk_breakdown: Record<string, number>;
  stress_test_scenarios: Array<{ scenario: string; portfolio_impact: number }>;
  risk_mitigation_recommendations: string[];
}

export interface SmartContract {
  id: number;
  address: string;
  name: string;
  contract_type: string;
  network: string;
  abi: unknown;
  bytecode: string | null;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface BlockchainTransaction {
  id: number;
  tx_hash: string;
  from_address: string;
  to_address: string;
  contract_id: number | null;
  value: number;
  gas_used: number | null;
  status: string;
  network: string;
  block_number: number | null;
  confirmations: number;
  timestamp: string;
}

export interface TokenizedAsset {
  token_symbol: string;
  name: string;
  contract_address: string;
  total_supply: number;
  price_per_token: number;
  underlying_asset: string;
  market_cap: number;
}

export interface TokenizedAssetsResponse {
  total: number;
  data: TokenizedAsset[];
}

export interface BlockchainNetwork {
  id: string;
  name: string;
  chain_id: number;
  currency: string;
}

export interface BlockchainNetworksResponse {
  networks: BlockchainNetwork[];
}

export interface WalletBalance {
  address: string;
  network: string;
  balances: Record<string, { balance: number; value_usd: number }>;
  total_value_usd: number;
  timestamp: string;
}

export interface AdminDashboard {
  timestamp: string;
  user_stats: {
    total_users: number;
    active_users: number;
    user_growth: Array<{ month: string; users: number }>;
    user_tiers: Record<string, number>;
  };
  portfolio_stats: {
    total_portfolios: number;
    average_assets_per_portfolio: number;
    total_assets_under_management: number;
  };
  transaction_stats: {
    total_transactions: number;
    transactions_today: number;
    transaction_volume_today: number;
    transaction_types: Record<string, number>;
  };
  system_health: {
    api_uptime: number;
    database_performance: number;
    average_response_time: number;
    error_rate: number;
    active_sessions: number;
  };
  alerts: Array<{ id: number; type: string; message: string; timestamp: string }>;
}

export interface AdminUserRow {
  id: number;
  email: string;
  username: string | null;
  role: string;
  tier: string;
  is_active: boolean;
  created_at: string | null;
  last_login: string | null;
}

export interface AdminUsersResponse {
  total: number;
  data: AdminUserRow[];
}

export interface SystemLog {
  id: number;
  log_level: string;
  component: string;
  message: string;
  request_id: string | null;
  user_id: number | null;
  timestamp: string;
}

export interface SystemPerformance {
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network: { incoming: number; outgoing: number };
  database: {
    connections: number;
    query_time_avg: number;
    active_transactions: number;
  };
  api: {
    requests_per_minute: number;
    average_response_time: number;
    error_rate: number;
  };
}

export interface UserActivityAnalytics {
  period: string;
  total_active_users: number;
  average_session_duration_minutes: number;
  average_sessions_per_user: number;
  most_active_times: Array<{ hour: number; activity: number }>;
  most_used_features: Array<{ feature: string; usage_percent: number }>;
  user_retention: { day1: number; day7: number; day30: number };
}
