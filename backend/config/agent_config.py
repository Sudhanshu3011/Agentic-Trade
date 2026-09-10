import os

# ---------------------------------------------------------
# Agent Model Priority Pools
# ---------------------------------------------------------

# 1. Debate and Research Manager Agents
DEBATE_MANAGER_MODELS = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "inclusionai/ling-3.0-flash-fin:free",
]

# 2. Sector Analyst
SECTOR_ANALYST_MODELS = [
    "dots-studio/dots-3-note-preview:free",
    "thinking-machines/inkling-small:free",
    "nvidia/nemotron-3.5-lightning:free",
]

# 3. Other 4 Analysts (Fundamental, Market, News, Technical)
OTHER_ANALYST_MODELS = [
    "nex-agi/nex-n2.5-mini:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "inclusionai/ling-3.0-flash-fin:free",
]


def _parse_model_env(env_var: str, default_models: list) -> list:
    val = os.getenv(env_var)
    if val:
        parsed = [m.strip() for m in val.split(",") if m.strip()]
        if parsed:
            return parsed
    return default_models


AGENT_MODEL_CONFIG = {
    # Debate and Manager agents
    "ResearchManager": _parse_model_env("RESEARCH_MANAGER_MODEL", DEBATE_MANAGER_MODELS),
    "BullResearcher": _parse_model_env("BULL_RESEARCHER_MODEL", DEBATE_MANAGER_MODELS),
    "BearResearcher": _parse_model_env("BEAR_RESEARCHER_MODEL", DEBATE_MANAGER_MODELS),

    # Sector analyst
    "SectorAnalyst": _parse_model_env("SECTOR_ANALYST_MODEL", SECTOR_ANALYST_MODELS),

    # Other 4 analysts
    "FundamentalAnalyst": _parse_model_env("FUNDAMENTAL_ANALYST_MODEL", OTHER_ANALYST_MODELS),
    "MarketAnalyst": _parse_model_env("MARKET_ANALYST_MODEL", OTHER_ANALYST_MODELS),
    "NewsAnalyst": _parse_model_env("NEWS_ANALYST_MODEL", OTHER_ANALYST_MODELS),
    "TechnicalAnalyst": _parse_model_env("TECHNICAL_ANALYST_MODEL", OTHER_ANALYST_MODELS),
}


AGENT_TOKEN_CONFIG = {
    "FundamentalAnalyst": {
        "low": 2500,
        "medium": 3000,
        "high": 4000,
    },
    "MarketAnalyst": {
        "low": 2500,
        "medium": 3000,
        "high": 4000,
    },
    "NewsAnalyst": {
        "low": 1500,
        "medium": 2000,
        "high": 2500,
    },
    "SectorAnalyst": {
        "low": 200,
        "medium": 400,
        "high": 500,
    },
    "TechnicalAnalyst": {
        "low": 2500,
        "medium": 3000,
        "high": 4000,
    },
    "ResearchManager": {
        "low": 1000,
        "medium": 1500,
        "high": 2000,
    },
    "BullResearcher": {
        "low": 1500,
        "medium": 2000,
        "high": 2500,
    },
    "BearResearcher": {
        "low": 1500,
        "medium": 2000,
        "high": 2500,
    },
}

