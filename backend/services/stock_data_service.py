import asyncio
import time
from typing import Any, Optional
from services.cache_service import CacheService
from core.logging import get_logger
from tools.data_preftech import prefetch_ticker_bundle
from tools.data_processor import process_prefetch_result

logger = get_logger(__name__)


class StockDataService:
    """
    Centralized market data gateway for YFinance, IndianAPI, and indicators.
    Integrates with Upstash Redis via CacheService with differentiated TTLs:
    - Quotes: 60s
    - News: 300s (5 mins)
    - Indicators (RSI, MACD, MA): 600s (10 mins)
    - Fundamentals / Company Info: 43200s (12 hours)
    - Full Market Bundle: 600s (10 mins)
    """

    TTL_QUOTE = 60
    TTL_NEWS = 300
    TTL_INDICATORS = 600
    TTL_FUNDAMENTALS = 43200
    TTL_BUNDLE = 600

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

    async def get_stock_bundle(
        self, ticker: str, force_refresh: bool = False
    ) -> dict[str, Any]:
        """
        Retrieve processed deterministic stock data bundle.
        Checks Redis cache first. On miss, runs thread-safe prefetch + processing
        with a lightweight distributed lock to prevent thundering herd.
        """
        symbol = ticker.strip().upper()
        cache_key = f"market:bundle:{symbol}"
        lock_key = f"market:lock:{symbol}"

        if not force_refresh:
            cached_bundle = await self.cache.get_json(cache_key)
            if cached_bundle:
                logger.info(f"Market bundle cache hit | ticker={symbol}")
                cached_bundle["cached"] = True
                return cached_bundle

        # Acquire lock to prevent duplicate simultaneous fetches
        lock_acquired = await self.cache.acquire_lock(lock_key, ttl_seconds=30)
        if not lock_acquired:
            logger.info(
                f"Another request fetching bundle | ticker={symbol}, waiting..."
            )
            for _ in range(6):
                await asyncio.sleep(0.5)
                cached_bundle = await self.cache.get_json(cache_key)
                if cached_bundle:
                    cached_bundle["cached"] = True
                    return cached_bundle

        try:
            logger.info(f"Fetching raw market bundle from source | ticker={symbol}")
            raw_bundle = await asyncio.to_thread(prefetch_ticker_bundle, symbol)
            if not isinstance(raw_bundle, dict) or raw_bundle.get("status") in (
                "invalid_ticker",
                "failed",
            ):
                return {
                    "ticker": symbol,
                    "status": (
                        raw_bundle.get("status", "failed")
                        if isinstance(raw_bundle, dict)
                        else "failed"
                    ),
                    "error": (
                        raw_bundle.get("error", "Failed to retrieve stock data")
                        if isinstance(raw_bundle, dict)
                        else "Unknown error"
                    ),
                    "cached": False,
                }

            processed = await asyncio.to_thread(process_prefetch_result, raw_bundle)
            processed["ticker"] = symbol
            processed["status"] = "success"

            # Cache in Redis with differentiated bundle TTL
            await self.cache.set_json(cache_key, processed, ttl_seconds=self.TTL_BUNDLE)
            return {**processed, "cached": False}
        finally:
            if lock_acquired:
                await self.cache.release_lock(lock_key)
