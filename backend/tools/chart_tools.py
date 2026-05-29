import pandas as pd
import ta
import math
from typing import Any, Optional
from core.logging import get_logger

logger = get_logger(__name__)

def extract_charts_data(raw_data: dict, fundamental_data: dict) -> Optional[dict]:
    """
    Extract and format chart-friendly data for the UI components.
    Computes historical time-series arrays for technical indicators
    and formats financial history data.
    """
    charts_data: dict[str, Any] = {}

    # ── Technical history (OHLCV + indicators) ──────────────────────────
    try:
        raw_ohlcv = raw_data.get("ohlcv")
        if raw_ohlcv is not None and not raw_ohlcv.empty:
            df = raw_ohlcv.copy()
            close = df["Close"]

            # Compute indicators
            ma50 = close.rolling(50).mean()
            ma200 = close.rolling(200).mean()

            bb = ta.volatility.BollingerBands(close)
            bb_upper = bb.bollinger_hband()
            bb_lower = bb.bollinger_lband()
            bb_mid = bb.bollinger_mavg()

            rsi = ta.momentum.RSIIndicator(close, window=14).rsi()

            volume = df["Volume"] if "Volume" in df.columns else pd.Series(dtype=float)

            def _safe(val: Any) -> Any:
                """Convert NaN/inf to None for JSON serialization."""
                if val is None:
                    return None
                try:
                    f = float(val)
                    if math.isnan(f) or math.isinf(f):
                        return None
                    return round(f, 2)
                except (ValueError, TypeError):
                    return None

            technical_history = []
            for i in range(len(df)):
                row = {
                    "date": str(df.index[i].date()) if hasattr(df.index[i], "date") else str(df.index[i]),
                    "close": _safe(close.iloc[i]),
                    "ma50": _safe(ma50.iloc[i]),
                    "ma200": _safe(ma200.iloc[i]),
                    "bb_upper": _safe(bb_upper.iloc[i]),
                    "bb_lower": _safe(bb_lower.iloc[i]),
                    "bb_mid": _safe(bb_mid.iloc[i]),
                    "rsi": _safe(rsi.iloc[i]),
                    "volume": _safe(volume.iloc[i]) if len(volume) > i else None,
                }
                technical_history.append(row)

            charts_data["technical_history"] = technical_history
    except Exception as exc:
        logger.warning(f"Failed to extract technical chart data: {exc}")
        charts_data["technical_history"] = []

    # ── Financials history ──────────────────────────────────────────────
    try:
        if fundamental_data and fundamental_data.get("status") == "success":
            income_stmt = fundamental_data.get("income_stmt", {})
            balance_sheet_data = fundamental_data.get("balance_sheet", {})
            cash_flow_data = fundamental_data.get("cash_flow", {})
            fundamentals = fundamental_data.get("fundamentals", {})

            financials_history = {
                "income_stmt": income_stmt.get("income_statement", {}),
                "balance_sheet": balance_sheet_data.get("balance_sheet", {}),
                "cash_flow": cash_flow_data.get("cash_flow", {}),
                "ratios": fundamentals.get("fundamentals", {}),
            }

            charts_data["financials_history"] = financials_history
    except Exception as exc:
        logger.warning(f"Failed to extract financials chart data: {exc}")

    return charts_data if charts_data else None
