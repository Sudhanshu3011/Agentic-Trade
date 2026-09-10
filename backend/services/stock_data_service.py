import time
from typing import Any, Optional
from services.cache_service import CacheService
from core.logging import get_logger

logger = get_logger(__name__)


class StockDataService:
    """
    Centralized market data gateway for YFinance, IndianAPI, and indicators.
    Integrates with Upstash Redis via CacheService with differentiated TTLs:
    - Quotes: 60s
    - News: 300s (5 mins)
    - Indicators (RSI, MACD, MA): 600s (10 mins)
    - Fundamentals / Company Info: 43200s (12 hours)
    """

    TTL_QUOTE = 60
    TTL_NEWS = 300
    TTL_INDICATORS = 600
    TTL_FUNDAMENTALS = 43200

    def __init__(self, cache_service: Optional[CacheService] = None):
        self.cache = cache_service or CacheService()

    async def get_cached_quote(self, ticker: str) -> Optional[dict[str, Any]]:
        key = f"market:quote:{ticker.upper()}"
        return await self.cache.get_json(key)

    async def set_cached_quote(self, ticker: str, data: dict[str, Any]) -> bool:
        key = f"market:quote:{ticker.upper()}"
        return await self.cache.set_json(key, data, ttl_seconds=self.TTL_QUOTE)

    async def get_cached_news(self, ticker: str) -> Optional[dict[str, Any]]:
        key = f"market:news:{ticker.upper()}"
        return await self.cache.get_json(key)

    async def set_cached_news(self, ticker: str, data: dict[str, Any]) -> bool:
        key = f"market:news:{ticker.upper()}"
        return await self.cache.set_json(key, data, ttl_seconds=self.TTL_NEWS)

    async def get_cached_indicators(self, ticker: str) -> Optional[dict[str, Any]]:
        key = f"market:indicators:{ticker.upper()}"
        return await self.cache.get_json(key)

    async def set_cached_indicators(self, ticker: str, data: dict[str, Any]) -> bool:
        key = f"market:indicators:{ticker.upper()}"
        return await self.cache.set_json(key, data, ttl_seconds=self.TTL_INDICATORS)

    async def get_cached_fundamentals(self, ticker: str) -> Optional[dict[str, Any]]:
        key = f"market:fundamentals:{ticker.upper()}"
        return await self.cache.get_json(key)

    async def set_cached_fundamentals(self, ticker: str, data: dict[str, Any]) -> bool:
        key = f"market:fundamentals:{ticker.upper()}"
        return await self.cache.set_json(key, data, ttl_seconds=self.TTL_FUNDAMENTALS)
