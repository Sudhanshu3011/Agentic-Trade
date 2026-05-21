import re
import yfinance as yf


def validate_ticker_format(ticker: str) -> tuple[bool, str]:
    """
    Level 1 — format check, no API call.
    Valid formats:
        NSE stocks : RELIANCE.NS
        BSE stocks : 500325.BO
    """
    ticker = ticker.strip().upper()

    # Basic sanity
    if not ticker:
        return False, "Ticker cannot be empty."

    if len(ticker) > 20:
        return False, "Ticker too long."

    # Must end with .NS or .BO for Indian market
    if not (ticker.endswith(".NS") or ticker.endswith(".BO")):
        return False, (
            f"Invalid ticker format '{ticker}'. "
            "Indian market tickers must end with '.NS' (NSE) or '.BO' (BSE). "
            "Example: 'RELIANCE.NS' or '500325.BO'."
        )

    # Only allow alphanumeric and hyphen before the suffix
    symbol = ticker.rsplit(".", 1)[0]
    if not re.match(r"^[A-Z0-9\-&]+$", symbol):
        return False, f"Ticker '{ticker}' contains invalid characters."

    return True, ""


def validate_ticker_exists(ticker: str) -> tuple[bool, str]:
    """
    Level 2 — existence check via yfinance.
    Makes one lightweight API call to verify ticker exists.
    """
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        # yfinance returns minimal dict for invalid tickers
        # checking for symbol or shortName confirms it exists
        if not info or info.get("trailingPps") is None:
            if not info.get("symbol") and not info.get("shortName"):
                return False, (
                    f"Ticker '{ticker}' not found on Yahoo Finance. "
                    "Please verify the ticker symbol is correct."
                )

        return True, ""

    except Exception as e:
        return False, f"Could not verify ticker '{ticker}': {str(e)}"