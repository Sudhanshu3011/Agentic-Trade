import pandas as pd
import time
import threading
from core.logging import get_logger

logger = get_logger(__name__)

#TTL Cache
_cache      : dict            = {}
_index_cache: dict            = {}
_cache_lock : threading.Lock  = threading.Lock()
_CACHE_TTL  : int             = 300   # 5 minutes
_INDEX_TTL  : int             = 3600  # 1 hour for market indices


def _get_cached(ticker: str) -> dict | None:
    with _cache_lock:
        entry = _cache.get(ticker)
        if entry is None:
            return None
        bundle, cached_at = entry
        if time.time() - cached_at > _CACHE_TTL:
            del _cache[ticker]
            logger.info(f"[cache] expired | ticker={ticker}")
            return None
        logger.info(f"[cache] hit | ticker={ticker}")
        return bundle


def _set_cached(ticker: str, bundle: dict) -> None:
    with _cache_lock:
        _cache[ticker] = (bundle, time.time())
        logger.info(f"[cache] stored | ticker={ticker}")


def _get_cached_index(index_name: str) -> dict | None:
    with _cache_lock:
        entry = _index_cache.get(index_name)
        if entry is None:
            return None
        val, cached_at = entry
        if time.time() - cached_at > _INDEX_TTL:
            del _index_cache[index_name]
            return None
        return val


def _set_cached_index(index_name: str, val: dict) -> None:
    with _cache_lock:
        _index_cache[index_name] = (val, time.time())

def _normalize_df(df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Clean and standardize a raw yfinance OHLCV DataFrame."""

    if df is None or df.empty:
        return None

    df = df.dropna(how="any")

    if df.empty:
        return None

    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.sort_index(inplace=True)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df