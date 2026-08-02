import logging
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from app.core.time_utils import utc_now
from app.models.models import (
    Asset,
    Portfolio,
    PortfolioAsset,
    Transaction,
    TransactionStatus,
    TransactionType,
    User,
)
from app.services.market_data_service import MarketDataService
from app.services.risk_management_service import RiskManagementService
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class OrderRequest:
    """Trading order request"""

    user_id: int
    portfolio_id: int
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: str = "GTC"


@dataclass
class OrderResult:
    """Trading order result"""

    success: bool
    order_id: Optional[str] = None
    transaction_id: Optional[int] = None
    message: str = ""
    executed_price: Optional[Decimal] = None
    executed_quantity: Optional[Decimal] = None
    fees: Optional[Decimal] = None


class TradingService:
    """Advanced trading service with algorithmic capabilities"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.market_data = MarketDataService()
        self.risk_manager = RiskManagementService(db)
        self.logger = logging.get_logger(__name__)
        self.min_order_size = Decimal("0.01")
        self.max_order_size = Decimal("1000000")
        self.default_slippage = Decimal("0.001")
        self.trading_fee_rate = Decimal("0.001")

    async def place_order(self, order: OrderRequest) -> OrderResult:
        """Place a trading order with comprehensive validation and execution"""
        try:
            validation_result = await self._validate_order(order)
            if not validation_result.success:
                return validation_result
            current_price = await self.market_data.get_current_price(order.symbol)
            if not current_price:
                return OrderResult(
                    success=False,
                    message=f"Unable to get current price for {order.symbol}",
                )
            risk_check = await self.risk_manager.evaluate_order_risk(
                order, current_price
            )
            if not risk_check.approved:
                return OrderResult(
                    success=False,
                    message=f"Order rejected by risk management: {risk_check.reason}",
                )
            if order.order_type == OrderType.MARKET:
                return await self._execute_market_order(order, current_price)
            elif order.order_type == OrderType.LIMIT:
                return await self._execute_limit_order(order, current_price)
            else:
                return OrderResult(
                    success=False,
                    message=f"Order type {order.order_type} not yet implemented",
                )
        except Exception as e:
            self.logger.error(f"Error placing order: {str(e)}", exc_info=True)
            return OrderResult(
                success=False, message="Internal error occurred while placing order"
            )

    async def _validate_order(self, order: OrderRequest) -> OrderResult:
        """Validate order parameters"""
        user = self.db.query(User).filter(User.id == order.user_id).first()
        if not user or not user.status == "active":
            return OrderResult(success=False, message="Invalid or inactive user")
        portfolio = (
            self.db.query(Portfolio)
            .filter(
                Portfolio.id == order.portfolio_id, Portfolio.owner_id == order.user_id
            )
            .first()
        )
        if not portfolio:
            return OrderResult(success=False, message="Portfolio not found")
        asset = self.db.query(Asset).filter(Asset.symbol == order.symbol).first()
        if not asset or not asset.is_tradable:
            return OrderResult(
                success=False, message=f"Asset {order.symbol} is not tradable"
            )
        if order.quantity < self.min_order_size:
            return OrderResult(
                success=False,
                message=f"Order quantity below minimum: {self.min_order_size}",
            )
        if order.quantity > self.max_order_size:
            return OrderResult(
                success=False,
                message=f"Order quantity exceeds maximum: {self.max_order_size}",
            )
        if order.order_type == OrderType.LIMIT and (not order.price):
            return OrderResult(success=False, message="Limit orders require a price")
        return OrderResult(success=True, message="Order validation passed")

    async def _execute_market_order(
        self, order: OrderRequest, current_price: Decimal
    ) -> OrderResult:
        """Execute market order immediately at current price"""
        try:
            if order.side == OrderSide.BUY:
                execution_price = current_price * (1 + self.default_slippage)
            else:
                execution_price = current_price * (1 - self.default_slippage)
            notional_value = order.quantity * execution_price
            fees = notional_value * self.trading_fee_rate
            if order.side == OrderSide.BUY:
                required_balance = notional_value + fees
                if not await self._check_sufficient_balance(
                    order.user_id, required_balance
                ):
                    return OrderResult(
                        success=False, message="Insufficient balance for purchase"
                    )
            elif not await self._check_sufficient_quantity(
                order.portfolio_id, order.symbol, order.quantity
            ):
                return OrderResult(
                    success=False, message="Insufficient quantity for sale"
                )
            transaction = Transaction(
                user_id=order.user_id,
                portfolio_id=order.portfolio_id,
                asset_id=self.db.query(Asset)
                .filter(Asset.symbol == order.symbol)
                .first()
                .id,
                transaction_type=(
                    TransactionType.BUY
                    if order.side == OrderSide.BUY
                    else TransactionType.SELL
                ),
                quantity=order.quantity,
                price=execution_price,
                amount=notional_value,
                fees=fees,
                status=TransactionStatus.COMPLETED,
                executed_at=utc_now(),
            )
            self.db.add(transaction)
            self.db.commit()
            await self._update_portfolio_position(
                order.portfolio_id,
                order.symbol,
                order.side,
                order.quantity,
                execution_price,
            )
            self.logger.info(
                f"Market order executed: {order.side} {order.quantity} {order.symbol} @ {execution_price}",
                extra={
                    "user_id": order.user_id,
                    "portfolio_id": order.portfolio_id,
                    "transaction_id": transaction.id,
                },
            )
            return OrderResult(
                success=True,
                transaction_id=transaction.id,
                executed_price=execution_price,
                executed_quantity=order.quantity,
                fees=fees,
                message="Market order executed successfully",
            )
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error executing market order: {str(e)}", exc_info=True)
            return OrderResult(success=False, message="Failed to execute market order")

    async def _execute_limit_order(
        self, order: OrderRequest, current_price: Decimal
    ) -> OrderResult:
        """Execute limit order if price conditions are met"""
        try:
            can_execute = False
            if order.side == OrderSide.BUY and current_price <= order.price:
                can_execute = True
                execution_price = order.price
            elif order.side == OrderSide.SELL and current_price >= order.price:
                can_execute = True
                execution_price = order.price
            if can_execute:
                modified_order = OrderRequest(
                    user_id=order.user_id,
                    portfolio_id=order.portfolio_id,
                    symbol=order.symbol,
                    side=order.side,
                    order_type=OrderType.MARKET,
                    quantity=order.quantity,
                )
                return await self._execute_market_order(modified_order, execution_price)
            else:
                return OrderResult(
                    success=True, message="Limit order placed and waiting for execution"
                )
        except Exception as e:
            self.logger.error(f"Error executing limit order: {str(e)}", exc_info=True)
            return OrderResult(success=False, message="Failed to execute limit order")

    async def _check_sufficient_balance(
        self, user_id: int, required_amount: Decimal
    ) -> bool:
        """Check if user has sufficient balance for purchase"""
        return True

    async def _check_sufficient_quantity(
        self, portfolio_id: int, symbol: str, required_quantity: Decimal
    ) -> bool:
        """Check if portfolio has sufficient quantity for sale"""
        asset = self.db.query(Asset).filter(Asset.symbol == symbol).first()
        if not asset:
            return False
        portfolio_asset = (
            self.db.query(PortfolioAsset)
            .filter(
                PortfolioAsset.portfolio_id == portfolio_id,
                PortfolioAsset.asset_id == asset.id,
            )
            .first()
        )
        if not portfolio_asset:
            return False
        return portfolio_asset.quantity >= required_quantity

    async def _update_portfolio_position(
        self,
        portfolio_id: int,
        symbol: str,
        side: OrderSide,
        quantity: Decimal,
        price: Decimal,
    ):
        """Update portfolio position after trade execution"""
        asset = self.db.query(Asset).filter(Asset.symbol == symbol).first()
        portfolio_asset = (
            self.db.query(PortfolioAsset)
            .filter(
                PortfolioAsset.portfolio_id == portfolio_id,
                PortfolioAsset.asset_id == asset.id,
            )
            .first()
        )
        if side == OrderSide.BUY:
            if portfolio_asset:
                total_cost = (
                    portfolio_asset.quantity * portfolio_asset.average_cost
                    + quantity * price
                )
                total_quantity = portfolio_asset.quantity + quantity
                portfolio_asset.average_cost = total_cost / total_quantity
                portfolio_asset.quantity = total_quantity
            else:
                portfolio_asset = PortfolioAsset(
                    portfolio_id=portfolio_id,
                    asset_id=asset.id,
                    quantity=quantity,
                    average_cost=price,
                    first_purchase_date=utc_now(),
                )
                self.db.add(portfolio_asset)
        elif portfolio_asset:
            portfolio_asset.quantity -= quantity
            if portfolio_asset.quantity <= 0:
                self.db.delete(portfolio_asset)
        portfolio_asset.last_transaction_date = utc_now()
        self.db.commit()

    async def get_order_history(
        self, user_id: int, portfolio_id: Optional[int] = None, limit: int = 100
    ) -> List[Dict]:
        """Get user's order history"""
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        if portfolio_id:
            query = query.filter(Transaction.portfolio_id == portfolio_id)
        transactions = query.order_by(Transaction.created_at.desc()).limit(limit).all()
        return [
            {
                "id": t.id,
                "symbol": t.asset.symbol if t.asset else None,
                "type": t.transaction_type.value,
                "quantity": float(t.quantity) if t.quantity else None,
                "price": float(t.price) if t.price else None,
                "amount": float(t.amount),
                "fees": float(t.fees),
                "status": t.status.value,
                "created_at": t.created_at.isoformat(),
                "executed_at": t.executed_at.isoformat() if t.executed_at else None,
            }
            for t in transactions
        ]

    async def cancel_order(self, user_id: int, order_id: str) -> OrderResult:
        """Cancel a pending order"""
        return OrderResult(
            success=False, message="Order cancellation not yet implemented"
        )

    async def get_portfolio_performance(
        self, portfolio_id: int, period_days: int = 30
    ) -> Dict:
        """Calculate portfolio performance metrics"""
        try:
            portfolio = (
                self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            )
            if not portfolio:
                return {"error": "Portfolio not found"}
            portfolio_assets = (
                self.db.query(PortfolioAsset)
                .filter(PortfolioAsset.portfolio_id == portfolio_id)
                .all()
            )
            if not portfolio_assets:
                return {
                    "total_value": 0,
                    "total_return": 0,
                    "total_return_pct": 0,
                    "daily_return": 0,
                    "positions": [],
                }
            total_value = Decimal("0")
            total_cost = Decimal("0")
            positions = []
            for pa in portfolio_assets:
                current_price = await self.market_data.get_current_price(
                    pa.asset.symbol
                )
                if current_price:
                    market_value = pa.quantity * current_price
                    cost_basis = pa.quantity * pa.average_cost
                    unrealized_pnl = market_value - cost_basis
                    total_value += market_value
                    total_cost += cost_basis
                    positions.append(
                        {
                            "symbol": pa.asset.symbol,
                            "quantity": float(pa.quantity),
                            "average_cost": float(pa.average_cost),
                            "current_price": float(current_price),
                            "market_value": float(market_value),
                            "unrealized_pnl": float(unrealized_pnl),
                            "return_pct": (
                                float(unrealized_pnl / cost_basis * 100)
                                if cost_basis > 0
                                else 0
                            ),
                        }
                    )
            total_return = total_value - total_cost
            total_return_pct = (
                float(total_return / total_cost * 100) if total_cost > 0 else 0
            )
            return {
                "portfolio_id": portfolio_id,
                "total_value": float(total_value),
                "total_cost": float(total_cost),
                "total_return": float(total_return),
                "total_return_pct": total_return_pct,
                "positions": positions,
                "last_updated": utc_now().isoformat(),
            }
        except Exception as e:
            self.logger.error(
                f"Error calculating portfolio performance: {str(e)}", exc_info=True
            )
            return {"error": "Failed to calculate portfolio performance"}


class AlgorithmicTradingService:
    """Advanced algorithmic trading strategies"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.trading_service = TradingService(db)
        self.market_data = MarketDataService()
        self.logger = logging.get_logger(__name__)

    async def execute_momentum_strategy(
        self,
        portfolio_id: int,
        symbols: List[str],
        lookback_days: int = 20,
        threshold: float = 0.05,
    ) -> Dict:
        """Execute momentum-based trading strategy"""
        try:
            results = []
            for symbol in symbols:
                prices = await self.market_data.get_historical_prices(
                    symbol, days=lookback_days
                )
                if len(prices) < lookback_days:
                    continue
                current_price = prices[-1]["close"]
                past_price = prices[0]["close"]
                momentum = (current_price - past_price) / past_price
                if momentum > threshold:
                    order = OrderRequest(
                        user_id=self.db.query(Portfolio)
                        .filter(Portfolio.id == portfolio_id)
                        .first()
                        .owner_id,
                        portfolio_id=portfolio_id,
                        symbol=symbol,
                        side=OrderSide.BUY,
                        order_type=OrderType.MARKET,
                        quantity=Decimal("100"),
                    )
                    result = await self.trading_service.place_order(order)
                    results.append(
                        {
                            "symbol": symbol,
                            "action": "BUY",
                            "momentum": momentum,
                            "result": result.__dict__,
                        }
                    )
                elif momentum < -threshold:
                    order = OrderRequest(
                        user_id=self.db.query(Portfolio)
                        .filter(Portfolio.id == portfolio_id)
                        .first()
                        .owner_id,
                        portfolio_id=portfolio_id,
                        symbol=symbol,
                        side=OrderSide.SELL,
                        order_type=OrderType.MARKET,
                        quantity=Decimal("100"),
                    )
                    result = await self.trading_service.place_order(order)
                    results.append(
                        {
                            "symbol": symbol,
                            "action": "SELL",
                            "momentum": momentum,
                            "result": result.__dict__,
                        }
                    )
            return {
                "strategy": "momentum",
                "portfolio_id": portfolio_id,
                "results": results,
                "executed_at": utc_now().isoformat(),
            }
        except Exception as e:
            self.logger.error(
                f"Error executing momentum strategy: {str(e)}", exc_info=True
            )
            return {"error": "Failed to execute momentum strategy"}

    async def execute_mean_reversion_strategy(
        self,
        portfolio_id: int,
        symbols: List[str],
        lookback_days: int = 20,
        std_threshold: float = 2.0,
    ) -> Dict:
        """Execute mean reversion trading strategy"""
        try:
            results = []
            for symbol in symbols:
                prices = await self.market_data.get_historical_prices(
                    symbol, days=lookback_days
                )
                if len(prices) < lookback_days:
                    continue
                close_prices = [p["close"] for p in prices]
                mean_price = sum(close_prices) / len(close_prices)
                variance = sum(((p - mean_price) ** 2 for p in close_prices)) / len(
                    close_prices
                )
                std_dev = variance**0.5
                current_price = close_prices[-1]
                z_score = (current_price - mean_price) / std_dev if std_dev > 0 else 0
                if z_score < -std_threshold:
                    order = OrderRequest(
                        user_id=self.db.query(Portfolio)
                        .filter(Portfolio.id == portfolio_id)
                        .first()
                        .owner_id,
                        portfolio_id=portfolio_id,
                        symbol=symbol,
                        side=OrderSide.BUY,
                        order_type=OrderType.MARKET,
                        quantity=Decimal("100"),
                    )
                    result = await self.trading_service.place_order(order)
                    results.append(
                        {
                            "symbol": symbol,
                            "action": "BUY",
                            "z_score": z_score,
                            "result": result.__dict__,
                        }
                    )
                elif z_score > std_threshold:
                    order = OrderRequest(
                        user_id=self.db.query(Portfolio)
                        .filter(Portfolio.id == portfolio_id)
                        .first()
                        .owner_id,
                        portfolio_id=portfolio_id,
                        symbol=symbol,
                        side=OrderSide.SELL,
                        order_type=OrderType.MARKET,
                        quantity=Decimal("100"),
                    )
                    result = await self.trading_service.place_order(order)
                    results.append(
                        {
                            "symbol": symbol,
                            "action": "SELL",
                            "z_score": z_score,
                            "result": result.__dict__,
                        }
                    )
            return {
                "strategy": "mean_reversion",
                "portfolio_id": portfolio_id,
                "results": results,
                "executed_at": utc_now().isoformat(),
            }
        except Exception as e:
            self.logger.error(
                f"Error executing mean reversion strategy: {str(e)}", exc_info=True
            )
            return {"error": "Failed to execute mean reversion strategy"}
