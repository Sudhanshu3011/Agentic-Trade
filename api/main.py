# api/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.validators import (
    validate_ticker_format,
    validate_ticker_exists,
    _refresh_cache_if_stale,
)
from core.logging import get_logger
from graph.builder import build_graph
import asyncio

logger = get_logger(__name__)

# Build graph once at startup
graph = build_graph()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Preload NSE ticker cache at startup.
    """
    _refresh_cache_if_stale()
    yield


# FastAPI App
app = FastAPI(
    title="Indian Trading Agent API",
    description="Multi-agent stock analysis for Indian markets",
    version="1.0.0",
    lifespan=lifespan,
)


# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later for frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request / Response Model
class AnalyzeRequest(BaseModel):
    ticker: str


class AnalyzeResponse(BaseModel):
    ticker: str
    news_report: str
    technical_report: str
    fundamental_report: str
    market_report: str
    sector_report: str
    status: str


# Routes
@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("3/minute")
async def analyze(request: Request, body: AnalyzeRequest):

    ticker = body.ticker.strip().upper()

    # ── Level 1 — format validation ────────────────────────────────────────

    is_valid_format, format_error = validate_ticker_format(ticker)

    if not is_valid_format:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "invalid_ticker_format",
                "message": format_error,
                "hint": ("Use NSE format like 'RELIANCE.NS'"),
            },
        )

    # ── Level 2 — existence validation ─────────────────────────────────────

    is_valid_ticker, ticker_error = validate_ticker_exists(ticker)

    if not is_valid_ticker:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ticker_not_found",
                "message": ticker_error,
            },
        )

    # ── Run LangGraph workflow ─────────────────────────────────────────────

    try:

        final_state = await asyncio.to_thread(
            graph.invoke, {"ticker_of_company": ticker}
        )

        return AnalyzeResponse(
            ticker=ticker,
            news_report=final_state.get("news_analyst_report", ""),
            technical_report=final_state.get("technical_analyst_report", ""),
            fundamental_report=final_state.get("fundamental_analyst_report", ""),
            market_report=final_state.get("market_analyst_report", ""),
            sector_report=final_state.get("sector_analyst_report", ""),
            status="success",
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "analysis_failed",
                "message": str(e),
            },
        )


# Local Run
if __name__ == "__main__":

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
