from typing import Any, Dict
from core.logging import get_logger

logger = get_logger(__name__)


def extract_ground_truth_benchmarks(state: dict) -> str:
    """
    Extract a concise, factual anchor of real market price, support/resistance levels,
    and core valuation metrics from state to prevent hallucinated prices.
    """
    bundle = state.get("data_bundle") or {}
    tech = state.get("technical_data") or bundle.get("technical_data") or {}
    fund = state.get("fundamental_data") or bundle.get("fundamental_data") or {}
    info = state.get("company_info") or bundle.get("company_info") or {}

    price_levels = tech.get("price_levels") or {}
    rsi_data = tech.get("rsi") or {}
    ma_data = tech.get("moving_averages") or {}
    atr_data = tech.get("atr") or {}

    # 1. Real stock price
    cmp_val = (
        price_levels.get("current")
        or info.get("currentPrice")
        or info.get("regularMarketPrice")
        or "N/A"
    )
    currency = info.get("currency") or "INR"
    curr_symbol = "₹" if currency == "INR" else f"{currency} "

    lines = [
        "=== VERIFIED MARKET BENCHMARKS (FACTUAL GROUND-TRUTH) ===",
        f"• Current Market Price (CMP): {curr_symbol}{cmp_val}",
    ]

    # 2. Key technical levels & price boundaries
    if price_levels:
        s1 = price_levels.get("support_1")
        s2 = price_levels.get("support_2")
        r1 = price_levels.get("resistance_1")
        r2 = price_levels.get("resistance_2")
        h52 = price_levels.get("high_52w") or info.get("fiftyTwoWeekHigh")
        l52 = price_levels.get("low_52w") or info.get("fiftyTwoWeekLow")
        lines.append(
            f"• Technical Price Levels: Support [S1: {s1}, S2: {s2}] | Resistance [R1: {r1}, R2: {r2}]"
        )
        if h52 or l52:
            lines.append(f"• 52-Week Range: Low: {l52} | High: {h52}")

    # 3. Technical Momentum & Trend Indicators
    tech_indicators = []
    if rsi_data:
        rsi_curr = rsi_data.get("current") or rsi_data.get("value")
        if rsi_curr is not None:
            tech_indicators.append(f"RSI(14): {rsi_curr}")
    if atr_data:
        atr_val = atr_data.get("current") or atr_data.get("atr")
        if atr_val is not None:
            tech_indicators.append(f"ATR: {atr_val}")
    if ma_data:
        sma_50 = ma_data.get("sma_50") or ma_data.get("SMA_50")
        sma_200 = ma_data.get("sma_200") or ma_data.get("SMA_200")
        if sma_50 is not None:
            tech_indicators.append(f"50-DMA: {sma_50}")
        if sma_200 is not None:
            tech_indicators.append(f"200-DMA: {sma_200}")

    if tech_indicators:
        lines.append(f"• Technical Indicators: {' | '.join(tech_indicators)}")

    # 4. Core fundamental valuation & leverage
    valuation = fund.get("valuation") or {}
    health = fund.get("fundamentals") or {}

    pe = (
        valuation.get("trailing_pe")
        or valuation.get("pe_ratio")
        or fund.get("pe_ratio")
        or info.get("trailingPE")
    )
    pb = (
        valuation.get("price_to_book")
        or valuation.get("pb_ratio")
        or fund.get("pb_ratio")
    )
    de = (
        health.get("debt_to_equity")
        or fund.get("debt_to_equity")
        or info.get("debtToEquity")
    )
    roce = health.get("roce") or fund.get("roce")
    roe = health.get("roe") or fund.get("roe")
    raw_mkt_cap = valuation.get("market_cap") or info.get("marketCap")
    mkt_cap = None
    if raw_mkt_cap is not None:
        if isinstance(raw_mkt_cap, (int, float)):
            if currency == "INR":
                mkt_cap = f"₹ {raw_mkt_cap / 1e7:,.2f} Cr"
            else:
                mkt_cap = f"{curr_symbol}{raw_mkt_cap:,.2f}"
        elif isinstance(raw_mkt_cap, str):
            if any(sym in raw_mkt_cap for sym in ["₹", "INR", "$", "Cr"]):
                mkt_cap = raw_mkt_cap
            else:
                try:
                    num = float(raw_mkt_cap)
                    if currency == "INR":
                        mkt_cap = f"₹ {num / 1e7:,.2f} Cr"
                    else:
                        mkt_cap = f"{curr_symbol}{num:,.2f}"
                except (ValueError, TypeError):
                    mkt_cap = (
                        f"₹ {raw_mkt_cap}"
                        if currency == "INR"
                        else f"{curr_symbol}{raw_mkt_cap}"
                    )

    fund_indicators = []
    if pe is not None:
        fund_indicators.append(f"P/E: {pe}")
    if pb is not None:
        fund_indicators.append(f"P/B: {pb}")
    if de is not None:
        fund_indicators.append(f"D/E: {de}")
    if roce is not None:
        fund_indicators.append(f"ROCE: {roce}%")
    if roe is not None:
        fund_indicators.append(f"ROE: {roe}%")
    if mkt_cap is not None:
        fund_indicators.append(f"Market Cap: {mkt_cap}")

    if fund_indicators:
        lines.append(f"• Fundamental Benchmarks: {' | '.join(fund_indicators)}")

    lines.append(
        "* MANDATORY CONSTRAINT: Derive your trade parameters (entry_price, exit_price, stop_loss) "
        "directly from these verified numbers. Do NOT invent prices that deviate from the CMP and key levels."
    )

    return "\n".join(lines)
