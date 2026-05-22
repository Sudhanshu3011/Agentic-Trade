# tools/data_prefetch.py

import threading
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.yf_context import yf_call, YFinance401Error
from core.logging import get_logger

logger = get_logger(__name__)

# ── Serialization gate ────────────────────────────────────────────────────────
# yfinance manages its own curl_cffi session + crumb internally.
# Concurrent threads sharing that session cause "Invalid Crumb" 401s.
# One semaphore slot = one yfinance call at a time = crumb never races.
_YF_SEMAPHORE = threading.Semaphore(1)

# ── Fixed market index tickers ────────────────────────────────────────────────
_MARKET_TICKERS: dict[str, str] = {
    "GSPC": "^GSPC",
    "VIX": "^VIX",
    "NSEI": "^NSEI",
    "BSESN": "^BSESN",
    "IXIC": "^IXIC",
}


# ── Shared DataFrame normalizer ───────────────────────────────────────────────
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


# ── Main prefetch function ────────────────────────────────────────────────────
def prefetch_ticker_bundle(ticker: str) -> dict:
    """
    Fetch ALL yfinance data needed by every analyst in one controlled pass.

    - Company data  : ohlcv, financials, balance_sheet, cash_flow,
                      info, major_holders, news
    - Market indices: GSPC, VIX, NSEI, BSESN, IXIC

    Concurrency model
    -----------------
    ThreadPoolExecutor queues the fetch tasks.
    _YF_SEMAPHORE(1) ensures only ONE thread talks to yfinance at a time,
    preventing the "Invalid Crumb" 401 that occurs when Yahoo's session
    is hit concurrently from multiple threads.

    Returns
    -------
    dict with status: "success" | "invalid_ticker" | "failed"
    """
    bundle: dict = {
        "ticker": ticker,
        "status": "success",
        "error": None,
        # company — keys mirror ticker_data() return shape exactly
        "ohlcv": None,  # → TechnicalAnalyst
        "financials": None,  # → FundamentalAnalyst
        "balance_sheet": None,  # → FundamentalAnalyst
        "cash_flow": None,  # → FundamentalAnalyst
        "info": {},  # → FundamentalAnalyst + SectorAnalyst
        "major_holders": None,  # → FundamentalAnalyst
        "news": [],  # → NewsAnalyst
        # market — key per index, value mirrors fetch_df() return shape
        "market_indices": {},  # → MarketAnalyst
    }

    # ── company fetch closures ────────────────────────────────────────────────

    def _fetch_ohlcv() -> pd.DataFrame | None:
        with _YF_SEMAPHORE:
            with yf_call("prefetch_ohlcv"):
                df = yf.download(
                    ticker,
                    period="1y",
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                )
        return _normalize_df(df)

    def _fetch_financials():
        with _YF_SEMAPHORE:
            with yf_call("prefetch_financials"):
                return yf.Ticker(ticker).financials

    def _fetch_balance_sheet():
        with _YF_SEMAPHORE:
            with yf_call("prefetch_balance_sheet"):
                return yf.Ticker(ticker).balance_sheet

    def _fetch_cash_flow():
        with _YF_SEMAPHORE:
            with yf_call("prefetch_cash_flow"):
                return yf.Ticker(ticker).cash_flow

    def _fetch_info() -> dict:
        with _YF_SEMAPHORE:
            with yf_call("prefetch_info"):
                raw = yf.Ticker(ticker).info
        if not isinstance(raw, dict):
            return {}
        return {
            k: v
            for k, v in raw.items()
            if v not in (None, "None", "null", "Null", "", [], {})
        }

    def _fetch_holders():
        with _YF_SEMAPHORE:
            with yf_call("prefetch_holders"):
                return yf.Ticker(ticker).major_holders

    def _fetch_news() -> list:
        with _YF_SEMAPHORE:
            with yf_call("prefetch_news"):
                return yf.Ticker(ticker).get_news() or []

    # ── market index fetch closure ────────────────────────────────────────────

    def _fetch_market_index(name: str, sym: str) -> tuple[str, dict]:
        with _YF_SEMAPHORE:
            with yf_call(f"prefetch_market_{name}"):
                df = yf.download(
                    sym,
                    period="1y",
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                )
        normalized = _normalize_df(df)
        return name, {
            "data": normalized,
            "status": "success" if normalized is not None else "failed",
            "error": None if normalized is not None else "empty_dataframe",
            "ticker": sym,
            "source": "yfinance",
        }

    # ── task registry ─────────────────────────────────────────────────────────

    _company_tasks: dict[str, callable] = {
        "ohlcv": _fetch_ohlcv,
        "financials": _fetch_financials,
        "balance_sheet": _fetch_balance_sheet,
        "cash_flow": _fetch_cash_flow,
        "info": _fetch_info,
        "major_holders": _fetch_holders,
        "news": _fetch_news,
    }

    # ── parallel dispatch (serialized inside by semaphore) ────────────────────

    with ThreadPoolExecutor(max_workers=4) as executor:

        company_futures: dict = {
            executor.submit(fn): key for key, fn in _company_tasks.items()
        }
        market_futures: dict = {
            executor.submit(_fetch_market_index, name, sym): name
            for name, sym in _MARKET_TICKERS.items()
        }
        all_futures = {**company_futures, **market_futures}

        for future in as_completed(all_futures):
            key = company_futures.get(future) or market_futures.get(future)
            try:
                result = future.result()

                if future in market_futures:
                    idx_name, idx_payload = result
                    bundle["market_indices"][idx_name] = idx_payload
                else:
                    bundle[key] = result

            except YFinance401Error as e:
                # 401 on one call means every subsequent call will also 401.
                # Abort immediately — no point running the rest.
                logger.error(f"[prefetch] 401 in '{e.caller}' — aborting pipeline")
                bundle["status"] = "failed"
                bundle["error"] = f"401 Unauthorized in '{e.caller}'"
                return bundle

            except Exception as exc:
                # Non-fatal — the analyst that needs this key handles None gracefully.
                logger.warning(f"[prefetch] '{key}' fetch failed (non-fatal): {exc}")

    # ── validity check ────────────────────────────────────────────────────────
    # If info came back empty, the ticker is almost certainly invalid.
    # Every other field can be None and the pipeline still runs partially,
    # but an empty info with no identity fields means the ticker doesn't exist.

    info = bundle.get("info", {})
    has_identity = any(info.get(k) for k in ("longName", "shortName", "symbol"))

    if not has_identity:
        logger.warning(
            f"[prefetch] no identity fields in info — "
            f"ticker likely invalid | ticker={ticker}"
        )
        bundle["status"] = "invalid_ticker"
        bundle["error"] = (
            f"Ticker '{ticker}' returned no identifiable company data. "
            "Check the symbol and exchange suffix (e.g. RELIANCE.NS)."
        )
        return bundle

    logger.info(
        f"[prefetch] bundle ready | ticker={ticker} "
        f"| company={info.get('longName', 'N/A')} "
        f"| indices={list(bundle['market_indices'].keys())}"
    )
    return bundle
