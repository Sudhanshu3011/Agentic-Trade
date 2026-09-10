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
        "medium": 300,
        "high": 400,
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

import os

DEFAULT_MODEL = os.getenv(
    "OPEN_ROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free"
)

AGENT_MODEL_CONFIG = {
    "FundamentalAnalyst": os.getenv("FUNDAMENTAL_ANALYST_MODEL", DEFAULT_MODEL),
    "MarketAnalyst": os.getenv("MARKET_ANALYST_MODEL", DEFAULT_MODEL),
    "NewsAnalyst": os.getenv("NEWS_ANALYST_MODEL", DEFAULT_MODEL),
    "SectorAnalyst": os.getenv("SECTOR_ANALYST_MODEL", DEFAULT_MODEL),
    "TechnicalAnalyst": os.getenv("TECHNICAL_ANALYST_MODEL", DEFAULT_MODEL),
    "ResearchManager": os.getenv("RESEARCH_MANAGER_MODEL", DEFAULT_MODEL),
    "BullResearcher": os.getenv("BULL_RESEARCHER_MODEL", DEFAULT_MODEL),
    "BearResearcher": os.getenv("BEAR_RESEARCHER_MODEL", DEFAULT_MODEL),
}

