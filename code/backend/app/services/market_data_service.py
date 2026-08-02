import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import aiohttp
import pandas as pd
import yfinance as yf
from app.core.config import get_settings
from app.core.time_utils import utc_now

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    """Price data structure"""

    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    adjusted_close: Optional[Decimal] = None


@dataclass
class MarketQuote:
    """Real-time market quote"""

    symbol: str
    price: Decimal
    change: Decimal
    change_percent: Decimal
    volume: int
    timestamp: datetime
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None


class MarketDataService:
    """Comprehensive market data service with multiple providers"""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = logging.get_logger(__name__)
        self._cache = {}
        self._cache_timeout = 60

    async def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current price for a symbol"""
        try:
            cache_key = f"price_{symbol}"
            if self._is_cached(cache_key):
                return self._cache[cache_key]["data"]
            price = await self._get_yahoo_price(symbol)
            if price:
                self._cache_data(cache_key, price)
                return price
            if self.settings.ALPHA_VANTAGE_API_KEY:
                price = await self._get_alpha_vantage_price(symbol)
                if price:
                    self._cache_data(cache_key, price)
                    return price
            return None
        except Exception as e:
            self.logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return None

    async def get_market_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Get detailed market quote"""
        try:
            cache_key = f"quote_{symbol}"
            if self._is_cached(cache_key):
                return self._cache[cache_key]["data"]
            quote = await self._get_yahoo_quote(symbol)
            if quote:
                self._cache_data(cache_key, quote)
                return quote
            return None
        except Exception as e:
            self.logger.error(f"Error getting market quote for {symbol}: {str(e)}")
            return None

    async def get_historical_prices(
        self, symbol: str, days: int = 30, interval: str = "1d"
    ) -> List[Dict]:
        """Get historical price data"""
        try:
            cache_key = f"history_{symbol}_{days}_{interval}"
            if self._is_cached(cache_key, timeout=300):
                return self._cache[cache_key]["data"]
            ticker = yf.Ticker(symbol)
            end_date = utc_now()
            start_date = end_date - timedelta(days=days)
            hist = ticker.history(start=start_date, end=end_date, interval=interval)
            if hist.empty:
                return []
            prices = []
            for date, row in hist.iterrows():
                prices.append(
                    {
                        "timestamp": date.isoformat(),
                        "open": float(row["Open"]),
                        "high": float(row["High"]),
                        "low": float(row["Low"]),
                        "close": float(row["Close"]),
                        "volume": int(row["Volume"]),
                        "adjusted_close": float(row["Close"]),
                    }
                )
            self._cache_data(cache_key, prices, timeout=300)
            return prices
        except Exception as e:
            self.logger.error(f"Error getting historical prices for {symbol}: {str(e)}")
            return []

    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, MarketQuote]:
        """Get quotes for multiple symbols efficiently"""
        try:
            tasks = [self.get_market_quote(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            quotes = {}
            for symbol, result in zip(symbols, results, strict=False):
                if isinstance(result, MarketQuote):
                    quotes[symbol] = result
                elif isinstance(result, Exception):
                    self.logger.warning(
                        f"Failed to get quote for {symbol}: {str(result)}"
                    )
            return quotes
        except Exception as e:
            self.logger.error(f"Error getting multiple quotes: {str(e)}")
            return {}

    async def get_market_movers(
        self, market: str = "US", limit: int = 20
    ) -> Dict[str, List[Dict]]:
        """Get market movers (gainers, losers, most active)"""
        try:
            return {"gainers": [], "losers": [], "most_active": []}
        except Exception as e:
            self.logger.error(f"Error getting market movers: {str(e)}")
            return {"gainers": [], "losers": [], "most_active": []}

    async def get_sector_performance(self) -> List[Dict]:
        """Get sector performance data"""
        try:
            sector_etfs = {
                "XLK": "Technology",
                "XLF": "Financial",
                "XLV": "Healthcare",
                "XLE": "Energy",
                "XLI": "Industrial",
                "XLY": "Consumer Discretionary",
                "XLP": "Consumer Staples",
                "XLU": "Utilities",
                "XLB": "Materials",
                "XLRE": "Real Estate",
                "XLC": "Communication Services",
            }
            sector_data = []
            for etf, sector_name in sector_etfs.items():
                quote = await self.get_market_quote(etf)
                if quote:
                    sector_data.append(
                        {
                            "sector": sector_name,
                            "symbol": etf,
                            "price": float(quote.price),
                            "change": float(quote.change),
                            "change_percent": float(quote.change_percent),
                        }
                    )
            return sorted(sector_data, key=lambda x: x["change_percent"], reverse=True)
        except Exception as e:
            self.logger.error(f"Error getting sector performance: {str(e)}")
            return []

    async def get_economic_indicators(self) -> Dict[str, Any]:
        """Get key economic indicators"""
        try:
            indicators = {
                "^TNX": "10-Year Treasury",
                "^VIX": "VIX Volatility Index",
                "DX-Y.NYB": "US Dollar Index",
                "GC=F": "Gold Futures",
                "CL=F": "Oil Futures",
            }
            indicator_data = {}
            for symbol, name in indicators.items():
                quote = await self.get_market_quote(symbol)
                if quote:
                    indicator_data[name] = {
                        "symbol": symbol,
                        "value": float(quote.price),
                        "change": float(quote.change),
                        "change_percent": float(quote.change_percent),
                        "timestamp": quote.timestamp.isoformat(),
                    }
            return indicator_data
        except Exception as e:
            self.logger.error(f"Error getting economic indicators: {str(e)}")
            return {}

    async def search_symbols(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for symbols by name or ticker"""
        try:
            try:
                ticker = yf.Ticker(query.upper())
                info = ticker.info
                if info and "symbol" in info:
                    return [
                        {
                            "symbol": info.get("symbol", query.upper()),
                            "name": info.get("longName", info.get("shortName", "")),
                            "type": info.get("quoteType", "EQUITY"),
                            "exchange": info.get("exchange", ""),
                            "currency": info.get("currency", "USD"),
                        }
                    ]
            except Exception:
                pass
            return []
        except Exception as e:
            self.logger.error(f"Error searching symbols for '{query}': {str(e)}")
            return []

    async def get_company_info(self, symbol: str) -> Optional[Dict]:
        """Get detailed company information"""
        try:
            cache_key = f"info_{symbol}"
            if self._is_cached(cache_key, timeout=3600):
                return self._cache[cache_key]["data"]
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if not info:
                return None
            company_info = {
                "symbol": symbol,
                "name": info.get("longName", info.get("shortName", "")),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "description": info.get("longBusinessSummary", ""),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "debt_to_equity": info.get("debtToEquity"),
                "return_on_equity": info.get("returnOnEquity"),
                "return_on_assets": info.get("returnOnAssets"),
                "profit_margin": info.get("profitMargins"),
                "operating_margin": info.get("operatingMargins"),
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "dividend_yield": info.get("dividendYield"),
                "payout_ratio": info.get("payoutRatio"),
                "beta": info.get("beta"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "average_volume": info.get("averageVolume"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "float_shares": info.get("floatShares"),
                "website": info.get("website", ""),
                "employees": info.get("fullTimeEmployees"),
                "headquarters": f"{info.get('city', '')}, {info.get('state', '')} {info.get('country', '')}".strip(),
            }
            company_info = {k: v for k, v in company_info.items() if v is not None}
            self._cache_data(cache_key, company_info, timeout=3600)
            return company_info
        except Exception as e:
            self.logger.error(f"Error getting company info for {symbol}: {str(e)}")
            return None

    async def get_technical_indicators(
        self, symbol: str, period: int = 20
    ) -> Dict[str, float]:
        """Calculate technical indicators"""
        try:
            prices = await self.get_historical_prices(symbol, days=max(period * 2, 50))
            if len(prices) < period:
                return {}
            df = pd.DataFrame(prices)
            df["close"] = pd.to_numeric(df["close"])
            df["high"] = pd.to_numeric(df["high"])
            df["low"] = pd.to_numeric(df["low"])
            df["volume"] = pd.to_numeric(df["volume"])
            indicators = {}
            indicators["sma_20"] = float(df["close"].rolling(window=20).mean().iloc[-1])
            indicators["sma_50"] = (
                float(df["close"].rolling(window=50).mean().iloc[-1])
                if len(df) >= 50
                else None
            )
            indicators["ema_12"] = float(df["close"].ewm(span=12).mean().iloc[-1])
            indicators["ema_26"] = float(df["close"].ewm(span=26).mean().iloc[-1])
            ema_12 = df["close"].ewm(span=12).mean()
            ema_26 = df["close"].ewm(span=26).mean()
            indicators["macd"] = float((ema_12 - ema_26).iloc[-1])
            delta = df["close"].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators["rsi"] = float(100 - 100 / (1 + rs.iloc[-1]))
            sma_20 = df["close"].rolling(window=20).mean()
            std_20 = df["close"].rolling(window=20).std()
            indicators["bollinger_upper"] = float((sma_20 + std_20 * 2).iloc[-1])
            indicators["bollinger_lower"] = float((sma_20 - std_20 * 2).iloc[-1])
            indicators["volume_sma"] = float(
                df["volume"].rolling(window=20).mean().iloc[-1]
            )
            indicators = {
                k: v
                for k, v in indicators.items()
                if v is not None and (not pd.isna(v))
            }
            return indicators
        except Exception as e:
            self.logger.error(
                f"Error calculating technical indicators for {symbol}: {str(e)}"
            )
            return {}

    async def _get_yahoo_price(self, symbol: str) -> Optional[Decimal]:
        """Get price from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return Decimal(str(data["Close"].iloc[-1]))
            return None
        except Exception as e:
            self.logger.debug(f"Yahoo Finance error for {symbol}: {str(e)}")
            return None

    async def _get_yahoo_quote(self, symbol: str) -> Optional[MarketQuote]:
        """Get detailed quote from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            if not info:
                return None
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            if not current_price:
                return None
            previous_close = info.get("previousClose", current_price)
            change = current_price - previous_close
            change_percent = change / previous_close * 100 if previous_close > 0 else 0
            return MarketQuote(
                symbol=symbol,
                price=Decimal(str(current_price)),
                change=Decimal(str(change)),
                change_percent=Decimal(str(change_percent)),
                volume=info.get("volume", 0),
                timestamp=utc_now(),
                bid=Decimal(str(info["bid"])) if info.get("bid") else None,
                ask=Decimal(str(info["ask"])) if info.get("ask") else None,
                bid_size=info.get("bidSize"),
                ask_size=info.get("askSize"),
            )
        except Exception as e:
            self.logger.debug(f"Yahoo Finance quote error for {symbol}: {str(e)}")
            return None

    async def _get_alpha_vantage_price(self, symbol: str) -> Optional[Decimal]:
        """Get price from Alpha Vantage API"""
        try:
            if not self.settings.ALPHA_VANTAGE_API_KEY:
                return None
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.settings.ALPHA_VANTAGE_API_KEY,
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        quote = data.get("Global Quote", {})
                        price = quote.get("05. price")
                        if price:
                            return Decimal(price)
            return None
        except Exception as e:
            self.logger.debug(f"Alpha Vantage error for {symbol}: {str(e)}")
            return None

    def _is_cached(self, key: str, timeout: int = None) -> bool:
        """Check if data is cached and not expired"""
        if key not in self._cache:
            return False
        cache_timeout = timeout or self._cache_timeout
        age = (utc_now() - self._cache[key]["timestamp"]).total_seconds()
        return age < cache_timeout

    def _cache_data(self, key: str, data: Any, timeout: int = None) -> Any:
        """Cache data with timestamp"""
        self._cache[key] = {"data": data, "timestamp": utc_now()}

    def clear_cache(self) -> Any:
        """Clear all cached data"""
        self._cache.clear()
        self.logger.info("Market data cache cleared")


class RealTimeDataService:
    """Real-time market data streaming service"""

    def __init__(self) -> None:
        self.logger = logging.get_logger(__name__)
        self.subscribers = {}
        self.is_running = False

    async def subscribe(self, symbol: str, callback):
        """Subscribe to real-time updates for a symbol"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
        self.subscribers[symbol].append(callback)
        if not self.is_running:
            asyncio.create_task(self._start_streaming())

    async def unsubscribe(self, symbol: str, callback):
        """Unsubscribe from real-time updates"""
        if symbol in self.subscribers:
            try:
                self.subscribers[symbol].remove(callback)
                if not self.subscribers[symbol]:
                    del self.subscribers[symbol]
            except ValueError:
                pass

    async def _start_streaming(self):
        """Start the real-time data streaming loop"""
        self.is_running = True
        market_data = MarketDataService()
        while self.is_running and self.subscribers:
            try:
                symbols = list(self.subscribers.keys())
                quotes = await market_data.get_multiple_quotes(symbols)
                for symbol, quote in quotes.items():
                    if symbol in self.subscribers:
                        for callback in self.subscribers[symbol]:
                            try:
                                await callback(quote)
                            except Exception as e:
                                self.logger.error(
                                    f"Error in subscriber callback: {str(e)}"
                                )
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in streaming loop: {str(e)}")
                await asyncio.sleep(5)
        self.is_running = False
