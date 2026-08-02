import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from app.core.time_utils import utc_now
from app.models.models import (
    Asset,
    AssetType,
    Portfolio,
    PortfolioAsset,
    RiskLevel,
    User,
)
from app.services.market_data_service import MarketDataService
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """Portfolio risk metrics"""

    portfolio_id: int
    total_value: Decimal
    var_95: Decimal
    var_99: Decimal
    expected_shortfall: Decimal
    volatility: Decimal
    sharpe_ratio: Optional[Decimal]
    max_drawdown: Decimal
    beta: Optional[Decimal]
    correlation_matrix: Optional[Dict[str, Dict[str, float]]]
    concentration_risk: Dict[str, float]
    liquidity_risk: float
    calculated_at: datetime


@dataclass
class RiskLimit:
    """Risk limit definition"""

    name: str
    limit_type: str
    threshold: Decimal
    current_value: Decimal
    utilization: Decimal
    breached: bool
    severity: str


@dataclass
class OrderRiskCheck:
    """Order risk assessment result"""

    approved: bool
    reason: str
    risk_score: float
    warnings: List[str]
    required_approvals: List[str]


class RiskManagementService:
    """Comprehensive risk management and compliance service"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.market_data = MarketDataService()
        self.logger = logging.get_logger(__name__)
        self.max_position_size = Decimal("0.10")
        self.max_sector_concentration = Decimal("0.25")
        self.max_single_day_loss = Decimal("0.05")
        self.min_liquidity_ratio = Decimal("0.05")
        self.var_confidence_levels = [0.95, 0.99]
        self.var_time_horizon = 1
        self.historical_window = 252

    async def calculate_portfolio_risk(
        self, portfolio_id: int
    ) -> Optional[RiskMetrics]:
        """Calculate comprehensive risk metrics for a portfolio"""
        try:
            portfolio = (
                self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            )
            if not portfolio:
                return None
            positions = (
                self.db.query(PortfolioAsset)
                .filter(PortfolioAsset.portfolio_id == portfolio_id)
                .all()
            )
            if not positions:
                return RiskMetrics(
                    portfolio_id=portfolio_id,
                    total_value=Decimal("0"),
                    var_95=Decimal("0"),
                    var_99=Decimal("0"),
                    expected_shortfall=Decimal("0"),
                    volatility=Decimal("0"),
                    sharpe_ratio=None,
                    max_drawdown=Decimal("0"),
                    beta=None,
                    correlation_matrix=None,
                    concentration_risk={},
                    liquidity_risk=0.0,
                    calculated_at=utc_now(),
                )
            total_value = Decimal("0")
            position_data = []
            for position in positions:
                current_price = await self.market_data.get_current_price(
                    position.asset.symbol
                )
                if current_price:
                    market_value = position.quantity * current_price
                    total_value += market_value
                    position_data.append(
                        {
                            "symbol": position.asset.symbol,
                            "quantity": position.quantity,
                            "price": current_price,
                            "value": market_value,
                            "sector": position.asset.sector,
                            "asset_type": position.asset.asset_type,
                        }
                    )
            if total_value == 0:
                return None
            for pos in position_data:
                pos["weight"] = float(pos["value"] / total_value)
            returns_data = await self._get_portfolio_returns(position_data)
            var_95, var_99, expected_shortfall = self._calculate_var(
                returns_data, total_value
            )
            volatility = self._calculate_volatility(returns_data)
            sharpe_ratio = self._calculate_sharpe_ratio(returns_data)
            max_drawdown = self._calculate_max_drawdown(returns_data)
            beta = await self._calculate_beta(position_data, returns_data)
            concentration_risk = self._calculate_concentration_risk(position_data)
            liquidity_risk = self._calculate_liquidity_risk(position_data)
            correlation_matrix = await self._calculate_correlation_matrix(position_data)
            return RiskMetrics(
                portfolio_id=portfolio_id,
                total_value=total_value,
                var_95=var_95,
                var_99=var_99,
                expected_shortfall=expected_shortfall,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                beta=beta,
                correlation_matrix=correlation_matrix,
                concentration_risk=concentration_risk,
                liquidity_risk=liquidity_risk,
                calculated_at=utc_now(),
            )
        except Exception as e:
            self.logger.error(
                f"Error calculating portfolio risk: {str(e)}", exc_info=True
            )
            return None

    async def evaluate_order_risk(
        self, order, current_price: Decimal
    ) -> OrderRiskCheck:
        """Evaluate risk for a proposed order"""
        try:
            warnings = []
            risk_score = 0.0
            required_approvals = []
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == order.portfolio_id)
                .first()
            )
            if not portfolio:
                return OrderRiskCheck(
                    approved=False,
                    reason="Portfolio not found",
                    risk_score=1.0,
                    warnings=[],
                    required_approvals=[],
                )
            order_value = order.quantity * current_price
            current_positions = (
                self.db.query(PortfolioAsset)
                .filter(PortfolioAsset.portfolio_id == order.portfolio_id)
                .all()
            )
            total_portfolio_value = Decimal("0")
            for pos in current_positions:
                pos_price = await self.market_data.get_current_price(pos.asset.symbol)
                if pos_price:
                    total_portfolio_value += pos.quantity * pos_price
            if total_portfolio_value > 0:
                position_size_ratio = order_value / total_portfolio_value
                if position_size_ratio > self.max_position_size:
                    risk_score += 0.3
                    warnings.append(
                        f"Large position size: {position_size_ratio:.1%} of portfolio"
                    )
                    if position_size_ratio > self.max_position_size * 2:
                        required_approvals.append("senior_trader")
            asset = self.db.query(Asset).filter(Asset.symbol == order.symbol).first()
            if asset and asset.sector:
                sector_exposure = self._calculate_sector_exposure(
                    current_positions,
                    asset.sector,
                    order_value if order.side == "buy" else -order_value,
                )
                if sector_exposure > self.max_sector_concentration:
                    risk_score += 0.2
                    warnings.append(
                        f"High sector concentration: {sector_exposure:.1%} in {asset.sector}"
                    )
            if asset:
                liquidity_score = await self._assess_liquidity(
                    asset.symbol, order.quantity
                )
                if liquidity_score < 0.5:
                    risk_score += 0.2
                    warnings.append("Low liquidity asset")
            volatility = await self._get_asset_volatility(order.symbol)
            if volatility and volatility > 0.5:
                risk_score += 0.1
                warnings.append("High volatility asset")
            user = self.db.query(User).filter(User.id == order.user_id).first()
            if user and user.risk_tolerance:
                asset_risk = self._assess_asset_risk_level(asset)
                if not self._is_suitable_for_risk_tolerance(
                    asset_risk, user.risk_tolerance
                ):
                    risk_score += 0.2
                    warnings.append("Asset risk level exceeds user tolerance")
            if order_value > Decimal("100000"):
                required_approvals.append("risk_manager")
                warnings.append("Large order requires additional approval")
            approved = risk_score < 0.7 and len(required_approvals) == 0
            reason = "Order approved" if approved else "Order requires review"
            if required_approvals:
                reason += f" - Approvals needed: {', '.join(required_approvals)}"
            return OrderRiskCheck(
                approved=approved,
                reason=reason,
                risk_score=risk_score,
                warnings=warnings,
                required_approvals=required_approvals,
            )
        except Exception as e:
            self.logger.error(f"Error evaluating order risk: {str(e)}", exc_info=True)
            return OrderRiskCheck(
                approved=False,
                reason="Risk evaluation failed",
                risk_score=1.0,
                warnings=["System error during risk assessment"],
                required_approvals=["risk_manager"],
            )

    async def check_risk_limits(self, portfolio_id: int) -> List[RiskLimit]:
        """Check all risk limits for a portfolio"""
        try:
            limits = []
            risk_metrics = await self.calculate_portfolio_risk(portfolio_id)
            if not risk_metrics:
                return limits
            var_limit = risk_metrics.total_value * Decimal("0.05")
            limits.append(
                RiskLimit(
                    name="Value at Risk (95%)",
                    limit_type="absolute",
                    threshold=var_limit,
                    current_value=risk_metrics.var_95,
                    utilization=(
                        float(risk_metrics.var_95 / var_limit * 100)
                        if var_limit > 0
                        else 0
                    ),
                    breached=risk_metrics.var_95 > var_limit,
                    severity="high" if risk_metrics.var_95 > var_limit else "low",
                )
            )
            vol_limit = Decimal("0.25")
            limits.append(
                RiskLimit(
                    name="Portfolio Volatility",
                    limit_type="percentage",
                    threshold=vol_limit,
                    current_value=risk_metrics.volatility,
                    utilization=(
                        float(risk_metrics.volatility / vol_limit * 100)
                        if vol_limit > 0
                        else 0
                    ),
                    breached=risk_metrics.volatility > vol_limit,
                    severity="medium" if risk_metrics.volatility > vol_limit else "low",
                )
            )
            for risk_type, concentration in risk_metrics.concentration_risk.items():
                if risk_type == "single_position":
                    limit_threshold = 0.15
                elif risk_type == "sector":
                    limit_threshold = 0.3
                else:
                    limit_threshold = 0.5
                limits.append(
                    RiskLimit(
                        name=f"{risk_type.replace('_', ' ').title()} Concentration",
                        limit_type="percentage",
                        threshold=Decimal(str(limit_threshold)),
                        current_value=Decimal(str(concentration)),
                        utilization=concentration / limit_threshold * 100,
                        breached=concentration > limit_threshold,
                        severity="high" if concentration > limit_threshold else "low",
                    )
                )
            return limits
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {str(e)}", exc_info=True)
            return []

    async def generate_risk_report(self, portfolio_id: int) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        try:
            risk_metrics = await self.calculate_portfolio_risk(portfolio_id)
            if not risk_metrics:
                return {"error": "Unable to calculate risk metrics"}
            risk_limits = await self.check_risk_limits(portfolio_id)
            portfolio = (
                self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            )
            risk_score = self._calculate_overall_risk_score(risk_metrics, risk_limits)
            recommendations = self._generate_risk_recommendations(
                risk_metrics, risk_limits
            )
            return {
                "portfolio_id": portfolio_id,
                "portfolio_name": portfolio.name if portfolio else "Unknown",
                "risk_score": risk_score,
                "risk_level": self._get_risk_level_from_score(risk_score),
                "metrics": {
                    "total_value": float(risk_metrics.total_value),
                    "var_95": float(risk_metrics.var_95),
                    "var_99": float(risk_metrics.var_99),
                    "expected_shortfall": float(risk_metrics.expected_shortfall),
                    "volatility": float(risk_metrics.volatility),
                    "sharpe_ratio": (
                        float(risk_metrics.sharpe_ratio)
                        if risk_metrics.sharpe_ratio
                        else None
                    ),
                    "max_drawdown": float(risk_metrics.max_drawdown),
                    "beta": float(risk_metrics.beta) if risk_metrics.beta else None,
                    "liquidity_risk": risk_metrics.liquidity_risk,
                },
                "concentration_risk": risk_metrics.concentration_risk,
                "limits": [
                    {
                        "name": limit.name,
                        "threshold": float(limit.threshold),
                        "current_value": float(limit.current_value),
                        "utilization": float(limit.utilization),
                        "breached": limit.breached,
                        "severity": limit.severity,
                    }
                    for limit in risk_limits
                ],
                "recommendations": recommendations,
                "calculated_at": risk_metrics.calculated_at.isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Error generating risk report: {str(e)}", exc_info=True)
            return {"error": "Failed to generate risk report"}

    def _calculate_var(
        self, returns: List[float], portfolio_value: Decimal
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """Calculate Value at Risk and Expected Shortfall"""
        if not returns or len(returns) < 30:
            return (Decimal("0"), Decimal("0"), Decimal("0"))
        returns_array = np.array(returns)
        var_95 = np.percentile(returns_array, 5) * float(portfolio_value)
        var_99 = np.percentile(returns_array, 1) * float(portfolio_value)
        var_95_threshold = np.percentile(returns_array, 5)
        tail_losses = returns_array[returns_array <= var_95_threshold]
        expected_shortfall = (
            np.mean(tail_losses) * float(portfolio_value) if len(tail_losses) > 0 else 0
        )
        return (
            abs(Decimal(str(var_95))),
            abs(Decimal(str(var_99))),
            abs(Decimal(str(expected_shortfall))),
        )

    def _calculate_volatility(self, returns: List[float]) -> Decimal:
        """Calculate annualized volatility"""
        if not returns or len(returns) < 2:
            return Decimal("0")
        returns_array = np.array(returns)
        daily_vol = np.std(returns_array)
        annualized_vol = daily_vol * np.sqrt(252)
        return Decimal(str(annualized_vol))

    def _calculate_sharpe_ratio(
        self, returns: List[float], risk_free_rate: float = 0.02
    ) -> Optional[Decimal]:
        """Calculate Sharpe ratio"""
        if not returns or len(returns) < 2:
            return None
        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate / 252
        if np.std(excess_returns) == 0:
            return None
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return Decimal(str(sharpe))

    def _calculate_max_drawdown(self, returns: List[float]) -> Decimal:
        """Calculate maximum drawdown"""
        if not returns:
            return Decimal("0")
        cumulative_returns = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        return abs(Decimal(str(max_drawdown)))

    async def _calculate_beta(
        self, position_data: List[Dict], returns: List[float]
    ) -> Optional[Decimal]:
        """Calculate portfolio beta against market benchmark"""
        try:
            benchmark_prices = await self.market_data.get_historical_prices(
                "SPY", days=len(returns)
            )
            if len(benchmark_prices) < len(returns):
                return None
            benchmark_returns = []
            for i in range(1, len(benchmark_prices)):
                ret = (
                    benchmark_prices[i]["close"] - benchmark_prices[i - 1]["close"]
                ) / benchmark_prices[i - 1]["close"]
                benchmark_returns.append(ret)
            if len(benchmark_returns) != len(returns):
                return None
            covariance = np.cov(returns, benchmark_returns)[0][1]
            market_variance = np.var(benchmark_returns)
            if market_variance == 0:
                return None
            beta = covariance / market_variance
            return Decimal(str(beta))
        except Exception as e:
            self.logger.debug(f"Error calculating beta: {str(e)}")
            return None

    def _calculate_concentration_risk(
        self, position_data: List[Dict]
    ) -> Dict[str, float]:
        """Calculate various concentration risk metrics"""
        if not position_data:
            return {}
        max_position_weight = max((pos["weight"] for pos in position_data))
        sector_weights = {}
        for pos in position_data:
            sector = pos.get("sector", "Unknown")
            sector_weights[sector] = sector_weights.get(sector, 0) + pos["weight"]
        max_sector_weight = max(sector_weights.values()) if sector_weights else 0
        asset_type_weights = {}
        for pos in position_data:
            asset_type = pos.get("asset_type", "Unknown")
            asset_type_weights[asset_type] = (
                asset_type_weights.get(asset_type, 0) + pos["weight"]
            )
        max_asset_type_weight = (
            max(asset_type_weights.values()) if asset_type_weights else 0
        )
        hhi = sum((pos["weight"] ** 2 for pos in position_data))
        return {
            "single_position": max_position_weight,
            "sector": max_sector_weight,
            "asset_type": max_asset_type_weight,
            "hhi": hhi,
        }

    def _calculate_liquidity_risk(self, position_data: List[Dict]) -> float:
        """Calculate portfolio liquidity risk score"""
        if not position_data:
            return 0.0
        total_weight = sum((pos["weight"] for pos in position_data))
        liquidity_score = 0.0
        for pos in position_data:
            asset_type = pos.get("asset_type", "stock")
            if asset_type == "stock":
                asset_liquidity = 0.9
            elif asset_type == "etf":
                asset_liquidity = 0.95
            elif asset_type == "bond":
                asset_liquidity = 0.7
            elif asset_type == "crypto":
                asset_liquidity = 0.6
            else:
                asset_liquidity = 0.5
            liquidity_score += pos["weight"] * asset_liquidity
        return liquidity_score / total_weight if total_weight > 0 else 0.0

    async def _calculate_correlation_matrix(
        self, position_data: List[Dict]
    ) -> Optional[Dict[str, Dict[str, float]]]:
        """Calculate correlation matrix between portfolio assets"""
        try:
            if len(position_data) < 2:
                return None
            symbols = [pos["symbol"] for pos in position_data]
            returns_data = {}
            for symbol in symbols:
                prices = await self.market_data.get_historical_prices(symbol, days=60)
                if len(prices) < 30:
                    continue
                returns = []
                for i in range(1, len(prices)):
                    ret = (prices[i]["close"] - prices[i - 1]["close"]) / prices[i - 1][
                        "close"
                    ]
                    returns.append(ret)
                returns_data[symbol] = returns
            correlation_matrix = {}
            for symbol1 in returns_data:
                correlation_matrix[symbol1] = {}
                for symbol2 in returns_data:
                    if len(returns_data[symbol1]) == len(returns_data[symbol2]):
                        corr = np.corrcoef(
                            returns_data[symbol1], returns_data[symbol2]
                        )[0][1]
                        correlation_matrix[symbol1][symbol2] = (
                            float(corr) if not np.isnan(corr) else 0.0
                        )
                    else:
                        correlation_matrix[symbol1][symbol2] = 0.0
            return correlation_matrix
        except Exception as e:
            self.logger.debug(f"Error calculating correlation matrix: {str(e)}")
            return None

    async def _get_portfolio_returns(self, position_data: List[Dict]) -> List[float]:
        """Calculate historical portfolio returns"""
        try:
            if not position_data:
                return []
            all_returns = {}
            min_length = float("inf")
            for pos in position_data:
                prices = await self.market_data.get_historical_prices(
                    pos["symbol"], days=60
                )
                if len(prices) < 30:
                    continue
                returns = []
                for i in range(1, len(prices)):
                    ret = (prices[i]["close"] - prices[i - 1]["close"]) / prices[i - 1][
                        "close"
                    ]
                    returns.append(ret)
                all_returns[pos["symbol"]] = returns
                min_length = min(min_length, len(returns))
            if not all_returns or min_length == float("inf"):
                return []
            portfolio_returns = []
            for i in range(min_length):
                daily_return = 0.0
                for pos in position_data:
                    if pos["symbol"] in all_returns:
                        daily_return += pos["weight"] * all_returns[pos["symbol"]][i]
                portfolio_returns.append(daily_return)
            return portfolio_returns
        except Exception as e:
            self.logger.debug(f"Error calculating portfolio returns: {str(e)}")
            return []

    def _calculate_sector_exposure(
        self, positions: List, sector: str, additional_value: Decimal = Decimal("0")
    ) -> Decimal:
        """Calculate total exposure to a specific sector"""
        sector_value = additional_value
        total_value = additional_value
        for pos in positions:
            if hasattr(pos, "asset") and pos.asset.sector == sector:
                sector_value += pos.quantity * pos.average_cost
            total_value += pos.quantity * pos.average_cost
        return sector_value / total_value if total_value > 0 else Decimal("0")

    async def _assess_liquidity(self, symbol: str, quantity: Decimal) -> float:
        """Assess liquidity for a specific order"""
        try:
            prices = await self.market_data.get_historical_prices(symbol, days=20)
            if not prices:
                return 0.5
            avg_volume = sum((p["volume"] for p in prices)) / len(prices)
            if avg_volume == 0:
                return 0.1
            order_impact = float(quantity) / avg_volume
            if order_impact < 0.01:
                return 1.0
            elif order_impact < 0.05:
                return 0.8
            elif order_impact < 0.1:
                return 0.6
            else:
                return 0.3
        except Exception as e:
            self.logger.debug(f"Error assessing liquidity for {symbol}: {str(e)}")
            return 0.5

    async def _get_asset_volatility(self, symbol: str) -> Optional[float]:
        """Get asset volatility"""
        try:
            prices = await self.market_data.get_historical_prices(symbol, days=30)
            if len(prices) < 20:
                return None
            returns = []
            for i in range(1, len(prices)):
                ret = (prices[i]["close"] - prices[i - 1]["close"]) / prices[i - 1][
                    "close"
                ]
                returns.append(ret)
            daily_vol = np.std(returns)
            annualized_vol = daily_vol * np.sqrt(252)
            return annualized_vol
        except Exception as e:
            self.logger.debug(f"Error calculating volatility for {symbol}: {str(e)}")
            return None

    def _assess_asset_risk_level(self, asset: Asset) -> RiskLevel:
        """Assess risk level of an asset"""
        if not asset:
            return RiskLevel.MODERATE
        if asset.asset_type == AssetType.BOND:
            return RiskLevel.LOW
        elif asset.asset_type == AssetType.STOCK:
            return RiskLevel.MODERATE
        elif asset.asset_type == AssetType.CRYPTO:
            return RiskLevel.VERY_HIGH
        elif asset.asset_type == AssetType.DERIVATIVE:
            return RiskLevel.HIGH
        else:
            return RiskLevel.MODERATE

    def _is_suitable_for_risk_tolerance(
        self, asset_risk: RiskLevel, user_risk_tolerance: RiskLevel
    ) -> bool:
        """Check if asset risk is suitable for user's risk tolerance"""
        risk_levels = {
            RiskLevel.VERY_LOW: 1,
            RiskLevel.LOW: 2,
            RiskLevel.MODERATE: 3,
            RiskLevel.HIGH: 4,
            RiskLevel.VERY_HIGH: 5,
        }
        return risk_levels.get(asset_risk, 3) <= risk_levels.get(user_risk_tolerance, 3)

    def _calculate_overall_risk_score(
        self, risk_metrics: RiskMetrics, risk_limits: List[RiskLimit]
    ) -> float:
        """Calculate overall risk score (0-100)"""
        score = 0.0
        vol_score = min(float(risk_metrics.volatility) * 100, 50)
        score += vol_score
        for limit in risk_limits:
            if limit.breached:
                if limit.severity == "critical":
                    score += 20
                elif limit.severity == "high":
                    score += 15
                elif limit.severity == "medium":
                    score += 10
                else:
                    score += 5
        for _risk_type, concentration in risk_metrics.concentration_risk.items():
            if concentration > 0.2:
                score += min(concentration * 50, 15)
        return min(score, 100)

    def _get_risk_level_from_score(self, score: float) -> str:
        """Convert risk score to risk level"""
        if score < 20:
            return "Very Low"
        elif score < 40:
            return "Low"
        elif score < 60:
            return "Moderate"
        elif score < 80:
            return "High"
        else:
            return "Very High"

    def _generate_risk_recommendations(
        self, risk_metrics: RiskMetrics, risk_limits: List[RiskLimit]
    ) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        for limit in risk_limits:
            if limit.breached:
                if "Concentration" in limit.name:
                    recommendations.append(
                        f"Consider diversifying to reduce {limit.name.lower()}"
                    )
                elif "Volatility" in limit.name:
                    recommendations.append(
                        "Consider adding lower volatility assets to reduce portfolio risk"
                    )
                elif "Value at Risk" in limit.name:
                    recommendations.append(
                        "Consider reducing position sizes or hedging to lower VaR"
                    )
        if risk_metrics.volatility > Decimal("0.3"):
            recommendations.append(
                "High portfolio volatility detected - consider rebalancing with stable assets"
            )
        for risk_type, concentration in risk_metrics.concentration_risk.items():
            if concentration > 0.25:
                recommendations.append(
                    f"High {risk_type.replace('_', ' ')} concentration - consider diversification"
                )
        if risk_metrics.liquidity_risk < 0.7:
            recommendations.append(
                "Consider increasing allocation to more liquid assets"
            )
        if risk_metrics.sharpe_ratio and risk_metrics.sharpe_ratio < Decimal("0.5"):
            recommendations.append(
                "Low risk-adjusted returns - review asset selection and allocation"
            )
        return (
            recommendations
            if recommendations
            else ["Portfolio risk profile appears balanced"]
        )
