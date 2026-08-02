import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
import logging

import cvxpy as cp
from app.services.market_data_service import MarketDataService
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class OptimizationObjective(str, Enum):
    MAX_SHARPE = "max_sharpe"
    MIN_VOLATILITY = "min_volatility"
    MAX_RETURN = "max_return"
    RISK_PARITY = "risk_parity"
    BLACK_LITTERMAN = "black_litterman"
    HIERARCHICAL_RISK_PARITY = "hierarchical_risk_parity"


class RiskModel(str, Enum):
    SAMPLE_COVARIANCE = "sample_covariance"
    LEDOIT_WOLF = "ledoit_wolf"
    FACTOR_MODEL = "factor_model"
    ROBUST_COVARIANCE = "robust_covariance"


@dataclass
class OptimizationConstraints:
    """Portfolio optimization constraints"""

    min_weight: float = 0.0
    max_weight: float = 1.0
    max_sector_weight: Optional[float] = None
    target_return: Optional[float] = None
    max_volatility: Optional[float] = None
    turnover_limit: Optional[float] = None
    transaction_costs: float = 0.001
    long_only: bool = True


@dataclass
class PortfolioResult:
    """Portfolio optimization result"""

    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    var_95: float
    var_99: float
    max_drawdown: float
    optimization_status: str
    objective_value: float
    risk_contributions: Dict[str, float]
    sector_allocations: Dict[str, float]
    performance_attribution: Dict[str, Any]


class AdvancedPortfolioOptimizer:
    """Advanced portfolio optimization with multiple objectives and constraints"""

    def __init__(self, config: Optional[Dict] = None) -> None:
        """Initialize portfolio optimizer"""
        self.config = {
            "lookback_period": 252,
            "min_history": 60,
            "return_frequency": "daily",
            "risk_free_rate": 0.02,
            "confidence_levels": [0.95, 0.99],
            "risk_model": RiskModel.LEDOIT_WOLF,
            "objective": OptimizationObjective.MAX_SHARPE,
            "solver": "ECOS",
            "max_iterations": 1000,
            "tolerance": 1e-06,
            "tau": 0.025,
            "market_cap_weights": True,
            "linkage_method": "ward",
            "distance_metric": "euclidean",
            "factors": ["market", "size", "value", "momentum", "quality"],
            "factor_exposure_limit": 0.3,
            "rebalance_frequency": "monthly",
            "rebalance_threshold": 0.05,
            "benchmark": "SPY",
            "attribution_factors": ["sector", "style", "selection"],
        }
        if config:
            self.config.update(config)
        self.market_data = MarketDataService()
        self.risk_models = {}
        self.factor_models = {}

    async def optimize_portfolio(
        self,
        assets: List[str],
        constraints: Optional[OptimizationConstraints] = None,
        current_weights: Optional[Dict[str, float]] = None,
    ) -> PortfolioResult:
        """Optimize portfolio allocation"""
        try:
            logger.info(f"Optimizing portfolio for {len(assets)} assets")
            if constraints is None:
                constraints = OptimizationConstraints()
            returns_data = await self._get_returns_data(assets)
            if returns_data.empty:
                raise ValueError("No market data available for optimization")
            expected_returns = self._calculate_expected_returns(returns_data)
            covariance_matrix = self._calculate_covariance_matrix(returns_data)
            if self.config["objective"] == OptimizationObjective.MAX_SHARPE:
                result = self._optimize_max_sharpe(
                    expected_returns, covariance_matrix, constraints
                )
            elif self.config["objective"] == OptimizationObjective.MIN_VOLATILITY:
                result = self._optimize_min_volatility(covariance_matrix, constraints)
            elif self.config["objective"] == OptimizationObjective.MAX_RETURN:
                result = self._optimize_max_return(expected_returns, constraints)
            elif self.config["objective"] == OptimizationObjective.RISK_PARITY:
                result = self._optimize_risk_parity(covariance_matrix, constraints)
            elif self.config["objective"] == OptimizationObjective.BLACK_LITTERMAN:
                result = await self._optimize_black_litterman(
                    assets, returns_data, constraints
                )
            elif (
                self.config["objective"]
                == OptimizationObjective.HIERARCHICAL_RISK_PARITY
            ):
                result = self._optimize_hierarchical_risk_parity(
                    returns_data, constraints
                )
            else:
                raise ValueError(
                    f"Unknown optimization objective: {self.config['objective']}"
                )
            portfolio_metrics = self._calculate_portfolio_metrics(
                result["weights"], expected_returns, covariance_matrix, returns_data
            )
            sector_allocations = await self._calculate_sector_allocations(
                assets, result["weights"]
            )
            risk_contributions = self._calculate_risk_contributions(
                result["weights"], covariance_matrix
            )
            performance_attribution = await self._calculate_performance_attribution(
                assets, result["weights"], returns_data
            )
            portfolio_result = PortfolioResult(
                weights=dict(zip(assets, result["weights"], strict=False)),
                expected_return=portfolio_metrics["expected_return"],
                volatility=portfolio_metrics["volatility"],
                sharpe_ratio=portfolio_metrics["sharpe_ratio"],
                var_95=portfolio_metrics["var_95"],
                var_99=portfolio_metrics["var_99"],
                max_drawdown=portfolio_metrics["max_drawdown"],
                optimization_status=result["status"],
                objective_value=result["objective_value"],
                risk_contributions=dict(zip(assets, risk_contributions, strict=False)),
                sector_allocations=sector_allocations,
                performance_attribution=performance_attribution,
            )
            logger.info("Portfolio optimization completed successfully")
            return portfolio_result
        except Exception as e:
            logger.error(f"Error in portfolio optimization: {str(e)}", exc_info=True)
            raise

    async def _get_returns_data(self, assets: List[str]) -> pd.DataFrame:
        """Get historical returns data for assets"""
        try:
            returns_data = pd.DataFrame()
            for asset in assets:
                prices = await self.market_data.get_historical_prices(
                    asset, days=self.config["lookback_period"] + 30
                )
                if len(prices) < self.config["min_history"]:
                    logger.warning(f"Insufficient data for {asset}: {len(prices)} days")
                    continue
                price_df = pd.DataFrame(prices)
                price_df["timestamp"] = pd.to_datetime(price_df["timestamp"])
                price_df.set_index("timestamp", inplace=True)
                if self.config["return_frequency"] == "daily":
                    returns = price_df["close"].pct_change().dropna()
                elif self.config["return_frequency"] == "weekly":
                    weekly_prices = price_df["close"].resample("W").last()
                    returns = weekly_prices.pct_change().dropna()
                elif self.config["return_frequency"] == "monthly":
                    monthly_prices = price_df["close"].resample("M").last()
                    returns = monthly_prices.pct_change().dropna()
                else:
                    returns = price_df["close"].pct_change().dropna()
                returns_data[asset] = returns
            returns_data = returns_data.dropna()
            if len(returns_data) > self.config["lookback_period"]:
                returns_data = returns_data.tail(self.config["lookback_period"])
            return returns_data
        except Exception as e:
            logger.error(f"Error getting returns data: {str(e)}")
            return pd.DataFrame()

    def _calculate_expected_returns(self, returns_data: pd.DataFrame) -> np.ndarray:
        """Calculate expected returns using various methods"""
        if self.config["return_frequency"] == "daily":
            expected_returns = returns_data.mean() * 252
        elif self.config["return_frequency"] == "weekly":
            expected_returns = returns_data.mean() * 52
        elif self.config["return_frequency"] == "monthly":
            expected_returns = returns_data.mean() * 12
        else:
            expected_returns = returns_data.mean() * 252
        return expected_returns.values

    def _calculate_covariance_matrix(self, returns_data: pd.DataFrame) -> np.ndarray:
        """Calculate covariance matrix using specified risk model"""
        if self.config["risk_model"] == RiskModel.SAMPLE_COVARIANCE:
            cov_matrix = returns_data.cov().values
        elif self.config["risk_model"] == RiskModel.LEDOIT_WOLF:
            lw = LedoitWolf()
            cov_matrix, _ = (lw.fit(returns_data.values).covariance_, lw.shrinkage_)
        elif self.config["risk_model"] == RiskModel.ROBUST_COVARIANCE:
            from sklearn.covariance import MinCovDet

            robust_cov = MinCovDet().fit(returns_data.values)
            cov_matrix = robust_cov.covariance_
        else:
            cov_matrix = returns_data.cov().values
        if self.config["return_frequency"] == "daily":
            cov_matrix *= 252
        elif self.config["return_frequency"] == "weekly":
            cov_matrix *= 52
        elif self.config["return_frequency"] == "monthly":
            cov_matrix *= 12
        return cov_matrix

    def _optimize_max_sharpe(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        constraints: OptimizationConstraints,
    ) -> Dict[str, Any]:
        """Optimize for maximum Sharpe ratio"""
        n_assets = len(expected_returns)
        weights = cp.Variable(n_assets)
        excess_returns = expected_returns - self.config["risk_free_rate"]
        portfolio_return = weights.T @ excess_returns
        portfolio_variance = cp.quad_form(weights, covariance_matrix)
        objective = cp.Maximize(portfolio_return)
        constraint_list = [
            cp.sum(weights) == 1,
            weights >= constraints.min_weight,
            weights <= constraints.max_weight,
        ]
        if constraints.long_only:
            constraint_list.append(weights >= 0)
        if constraints.max_volatility:
            constraint_list.append(
                cp.sqrt(portfolio_variance) <= constraints.max_volatility
            )
        problem = cp.Problem(objective, constraint_list)
        problem.solve(solver=self.config["solver"])
        if problem.status not in ["infeasible", "unbounded"]:
            optimal_weights = weights.value
            portfolio_ret = np.dot(optimal_weights, expected_returns)
            portfolio_vol = np.sqrt(
                np.dot(optimal_weights.T, np.dot(covariance_matrix, optimal_weights))
            )
            sharpe_ratio = (
                portfolio_ret - self.config["risk_free_rate"]
            ) / portfolio_vol
            return {
                "weights": optimal_weights,
                "status": problem.status,
                "objective_value": sharpe_ratio,
            }
        else:
            raise ValueError(f"Optimization failed with status: {problem.status}")

    def _optimize_min_volatility(
        self, covariance_matrix: np.ndarray, constraints: OptimizationConstraints
    ) -> Dict[str, Any]:
        """Optimize for minimum volatility"""
        n_assets = covariance_matrix.shape[0]
        weights = cp.Variable(n_assets)
        portfolio_variance = cp.quad_form(weights, covariance_matrix)
        objective = cp.Minimize(portfolio_variance)
        constraint_list = [
            cp.sum(weights) == 1,
            weights >= constraints.min_weight,
            weights <= constraints.max_weight,
        ]
        if constraints.long_only:
            constraint_list.append(weights >= 0)
        problem = cp.Problem(objective, constraint_list)
        problem.solve(solver=self.config["solver"])
        if problem.status not in ["infeasible", "unbounded"]:
            return {
                "weights": weights.value,
                "status": problem.status,
                "objective_value": np.sqrt(problem.value),
            }
        else:
            raise ValueError(f"Optimization failed with status: {problem.status}")

    def _optimize_max_return(
        self, expected_returns: np.ndarray, constraints: OptimizationConstraints
    ) -> Dict[str, Any]:
        """Optimize for maximum return"""
        n_assets = len(expected_returns)
        weights = cp.Variable(n_assets)
        portfolio_return = weights.T @ expected_returns
        objective = cp.Maximize(portfolio_return)
        constraint_list = [
            cp.sum(weights) == 1,
            weights >= constraints.min_weight,
            weights <= constraints.max_weight,
        ]
        if constraints.long_only:
            constraint_list.append(weights >= 0)
        problem = cp.Problem(objective, constraint_list)
        problem.solve(solver=self.config["solver"])
        if problem.status not in ["infeasible", "unbounded"]:
            return {
                "weights": weights.value,
                "status": problem.status,
                "objective_value": problem.value,
            }
        else:
            raise ValueError(f"Optimization failed with status: {problem.status}")

    def _optimize_risk_parity(
        self, covariance_matrix: np.ndarray, constraints: OptimizationConstraints
    ) -> Dict[str, Any]:
        """Optimize for risk parity (equal risk contribution)"""
        n_assets = covariance_matrix.shape[0]

        def risk_parity_objective(weights):
            """Objective function for risk parity optimization"""
            portfolio_vol = np.sqrt(
                np.dot(weights.T, np.dot(covariance_matrix, weights))
            )
            marginal_contrib = np.dot(covariance_matrix, weights) / portfolio_vol
            contrib = weights * marginal_contrib
            target_contrib = portfolio_vol / n_assets
            return np.sum((contrib - target_contrib) ** 2)

        constraint_dict = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
        bounds = [
            (constraints.min_weight, constraints.max_weight) for _ in range(n_assets)
        ]
        if constraints.long_only:
            bounds = [
                (max(0, constraints.min_weight), constraints.max_weight)
                for _ in range(n_assets)
            ]
        x0 = np.ones(n_assets) / n_assets
        result = minimize(
            risk_parity_objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraint_dict,
            options={"maxiter": self.config["max_iterations"]},
        )
        if result.success:
            return {
                "weights": result.x,
                "status": "optimal",
                "objective_value": result.fun,
            }
        else:
            raise ValueError(f"Risk parity optimization failed: {result.message}")

    async def _optimize_black_litterman(
        self,
        assets: List[str],
        returns_data: pd.DataFrame,
        constraints: OptimizationConstraints,
    ) -> Dict[str, Any]:
        """Black-Litterman optimization"""
        try:
            market_caps = await self._get_market_caps(assets)
            market_weights = np.array([market_caps.get(asset, 1.0) for asset in assets])
            market_weights = market_weights / np.sum(market_weights)
            covariance_matrix = self._calculate_covariance_matrix(returns_data)
            risk_aversion = 3.0
            implied_returns = risk_aversion * np.dot(covariance_matrix, market_weights)
            self.config["tau"]
            bl_returns = implied_returns
            bl_covariance = covariance_matrix
            return self._optimize_max_sharpe(bl_returns, bl_covariance, constraints)
        except Exception as e:
            logger.error(f"Error in Black-Litterman optimization: {str(e)}")
            expected_returns = self._calculate_expected_returns(returns_data)
            covariance_matrix = self._calculate_covariance_matrix(returns_data)
            return self._optimize_max_sharpe(
                expected_returns, covariance_matrix, constraints
            )

    def _optimize_hierarchical_risk_parity(
        self, returns_data: pd.DataFrame, constraints: OptimizationConstraints
    ) -> Dict[str, Any]:
        """Hierarchical Risk Parity optimization"""
        try:
            from scipy.cluster.hierarchy import cut_tree, linkage
            from scipy.spatial.distance import squareform

            corr_matrix = returns_data.corr()
            distance_matrix = np.sqrt(0.5 * (1 - corr_matrix))
            condensed_distances = squareform(distance_matrix, checks=False)
            linkage_matrix = linkage(
                condensed_distances, method=self.config["linkage_method"]
            )
            n_clusters = min(5, len(returns_data.columns) // 2)
            clusters = cut_tree(linkage_matrix, n_clusters=n_clusters).flatten()
            cluster_weights = {}
            for cluster_id in np.unique(clusters):
                cluster_assets = [
                    asset
                    for i, asset in enumerate(returns_data.columns)
                    if clusters[i] == cluster_id
                ]
                cluster_returns = returns_data[cluster_assets]
                cluster_cov = cluster_returns.cov().values
                if len(cluster_assets) == 1:
                    cluster_weights[cluster_id] = {cluster_assets[0]: 1.0}
                else:
                    cluster_vol = np.sqrt(np.diag(cluster_cov))
                    inv_vol_weights = 1 / cluster_vol / np.sum(1 / cluster_vol)
                    cluster_weights[cluster_id] = dict(
                        zip(cluster_assets, inv_vol_weights, strict=False)
                    )
            final_weights = np.zeros(len(returns_data.columns))
            cluster_sizes = [
                np.sum(clusters == cluster_id) for cluster_id in np.unique(clusters)
            ]
            cluster_allocation = np.array(cluster_sizes) / np.sum(cluster_sizes)
            for i, asset in enumerate(returns_data.columns):
                cluster_id = clusters[i]
                within_cluster_weight = cluster_weights[cluster_id][asset]
                final_weights[i] = (
                    cluster_allocation[cluster_id] * within_cluster_weight
                )
            return {
                "weights": final_weights,
                "status": "optimal",
                "objective_value": 0.0,
            }
        except Exception as e:
            logger.error(f"Error in HRP optimization: {str(e)}")
            n_assets = len(returns_data.columns)
            return {
                "weights": np.ones(n_assets) / n_assets,
                "status": "fallback",
                "objective_value": 0.0,
            }

    def _calculate_portfolio_metrics(
        self,
        weights: np.ndarray,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        returns_data: pd.DataFrame,
    ) -> Dict[str, float]:
        """Calculate portfolio performance metrics"""
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        sharpe_ratio = (
            portfolio_return - self.config["risk_free_rate"]
        ) / portfolio_volatility
        portfolio_returns = np.dot(returns_data.values, weights)
        var_95 = np.percentile(portfolio_returns, 5)
        var_99 = np.percentile(portfolio_returns, 1)
        cumulative_returns = np.cumprod(1 + portfolio_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        return {
            "expected_return": float(portfolio_return),
            "volatility": float(portfolio_volatility),
            "sharpe_ratio": float(sharpe_ratio),
            "var_95": float(var_95),
            "var_99": float(var_99),
            "max_drawdown": float(abs(max_drawdown)),
        }

    def _calculate_risk_contributions(
        self, weights: np.ndarray, covariance_matrix: np.ndarray
    ) -> np.ndarray:
        """Calculate risk contributions of each asset"""
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
        marginal_contrib = np.dot(covariance_matrix, weights) / portfolio_vol
        risk_contrib = weights * marginal_contrib
        return risk_contrib / np.sum(risk_contrib)

    async def _calculate_sector_allocations(
        self, assets: List[str], weights: np.ndarray
    ) -> Dict[str, float]:
        """Calculate sector allocations"""
        try:
            sector_allocations = {}
            for i, asset in enumerate(assets):
                company_info = await self.market_data.get_company_info(asset)
                sector = (
                    company_info.get("sector", "Unknown") if company_info else "Unknown"
                )
                if sector in sector_allocations:
                    sector_allocations[sector] += weights[i]
                else:
                    sector_allocations[sector] = weights[i]
            return sector_allocations
        except Exception as e:
            logger.error(f"Error calculating sector allocations: {str(e)}")
            return {"Unknown": 1.0}

    async def _calculate_performance_attribution(
        self, assets: List[str], weights: np.ndarray, returns_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calculate performance attribution"""
        try:
            attribution = {
                "asset_contribution": {},
                "sector_contribution": {},
                "total_return": 0.0,
            }
            portfolio_returns = np.dot(returns_data.values, weights)
            total_return = np.mean(portfolio_returns) * 252
            for i, asset in enumerate(assets):
                asset_return = returns_data[asset].mean() * 252
                contribution = weights[i] * asset_return
                attribution["asset_contribution"][asset] = float(contribution)
            attribution["total_return"] = float(total_return)
            return attribution
        except Exception as e:
            logger.error(f"Error calculating performance attribution: {str(e)}")
            return {
                "asset_contribution": {},
                "sector_contribution": {},
                "total_return": 0.0,
            }

    async def _get_market_caps(self, assets: List[str]) -> Dict[str, float]:
        """Get market capitalizations for assets"""
        market_caps = {}
        for asset in assets:
            try:
                company_info = await self.market_data.get_company_info(asset)
                if company_info and "market_cap" in company_info:
                    market_caps[asset] = company_info["market_cap"]
                else:
                    market_caps[asset] = 1.0
            except Exception:
                market_caps[asset] = 1.0
        return market_caps

    async def backtest_strategy(
        self,
        assets: List[str],
        constraints: OptimizationConstraints,
        start_date: datetime,
        end_date: datetime,
        rebalance_frequency: str = "monthly",
    ) -> Dict[str, Any]:
        """Backtest portfolio optimization strategy"""
        try:
            logger.info(
                f"Backtesting portfolio strategy from {start_date} to {end_date}"
            )
            rebalance_dates = pd.date_range(
                start=start_date,
                end=end_date,
                freq="MS" if rebalance_frequency == "monthly" else "QS",
            )
            backtest_results = {
                "returns": [],
                "weights_history": [],
                "rebalance_dates": [],
                "turnover": [],
                "transaction_costs": [],
            }
            current_weights = None
            for rebalance_date in rebalance_dates:
                try:
                    rebalance_date - timedelta(days=1)
                    result = await self.optimize_portfolio(
                        assets, constraints, current_weights
                    )
                    new_weights = np.array(
                        [result.weights.get(asset, 0.0) for asset in assets]
                    )
                    if current_weights is not None:
                        turnover = np.sum(np.abs(new_weights - current_weights))
                        transaction_cost = turnover * constraints.transaction_costs
                    else:
                        turnover = np.sum(new_weights)
                        transaction_cost = turnover * constraints.transaction_costs
                    backtest_results["weights_history"].append(new_weights.tolist())
                    backtest_results["rebalance_dates"].append(
                        rebalance_date.isoformat()
                    )
                    backtest_results["turnover"].append(float(turnover))
                    backtest_results["transaction_costs"].append(
                        float(transaction_cost)
                    )
                    current_weights = new_weights
                except Exception as e:
                    logger.warning(
                        f"Error in backtest for date {rebalance_date}: {str(e)}"
                    )
                    continue
            if backtest_results["weights_history"]:
                total_turnover = np.mean(backtest_results["turnover"])
                total_transaction_costs = np.sum(backtest_results["transaction_costs"])
                backtest_results["summary"] = {
                    "total_turnover": float(total_turnover),
                    "total_transaction_costs": float(total_transaction_costs),
                    "average_rebalancing_cost": float(
                        np.mean(backtest_results["transaction_costs"])
                    ),
                    "number_of_rebalances": len(backtest_results["rebalance_dates"]),
                }
            logger.info("Portfolio backtest completed successfully")
            return backtest_results
        except Exception as e:
            logger.error(f"Error in portfolio backtest: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def generate_efficient_frontier(
        self,
        assets: List[str],
        constraints: OptimizationConstraints,
        n_points: int = 50,
    ) -> Dict[str, Any]:
        """Generate efficient frontier"""
        try:
            logger.info(f"Generating efficient frontier with {n_points} points")
            frontier_data = {
                "returns": [],
                "volatilities": [],
                "sharpe_ratios": [],
                "weights": [],
            }
            return {
                "success": True,
                "frontier_data": frontier_data,
                "optimal_portfolio": None,
                "min_volatility_portfolio": None,
            }
        except Exception as e:
            logger.error(f"Error generating efficient frontier: {str(e)}")
            return {"success": False, "error": str(e)}

    def stress_test_portfolio(
        self, weights: Dict[str, float], stress_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Stress test portfolio under various scenarios"""
        try:
            stress_results = {}
            for i, scenario in enumerate(stress_scenarios):
                scenario_name = scenario.get("name", f"Scenario_{i + 1}")
                asset_shocks = scenario.get("asset_shocks", {})
                portfolio_impact = 0.0
                for asset, weight in weights.items():
                    shock = asset_shocks.get(asset, 0.0)
                    portfolio_impact += weight * shock
                stress_results[scenario_name] = {
                    "portfolio_impact": float(portfolio_impact),
                    "description": scenario.get("description", ""),
                    "probability": scenario.get("probability", None),
                }
            return {
                "success": True,
                "stress_results": stress_results,
                "worst_case_loss": min(
                    [result["portfolio_impact"] for result in stress_results.values()]
                ),
                "best_case_gain": max(
                    [result["portfolio_impact"] for result in stress_results.values()]
                ),
            }
        except Exception as e:
            logger.error(f"Error in portfolio stress test: {str(e)}")
            return {"success": False, "error": str(e)}
