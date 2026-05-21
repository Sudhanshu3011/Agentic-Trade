# api/main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from api.validators import validate_ticker_format, validate_ticker_exists
from pydantic import BaseModel
from graph.builder import build_graph
import uvicorn

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded



app = FastAPI(
    title       = "Indian Trading Agent API",
    description = "Multi-agent stock analysis for Indian markets",
    version     = "1.0.0"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow frontend to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # tighten this when frontend URL is known
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# Build graph once at startup — not on every request
graph = build_graph()


# ── Request / Response models ─────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    ticker       : str    # "RELIANCE.NS"


class AnalyzeResponse(BaseModel):
    ticker              : str
    news_report         : str
    technical_report    : str
    fundamental_report  : str
    market_report       : str
    sector_report       : str
    status              : str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Simple health check — call this to verify API is running."""
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("3/minute")
async def analyze(request: Request, body: AnalyzeRequest):

    # Level 1 — format check
    is_valid_format, format_error = validate_ticker_format(body.ticker)
    if not is_valid_format:
        raise HTTPException(
            status_code = 422,
            detail      = {
                "error"  : "invalid_ticker_format",
                "message": format_error,
                "hint"   : "Use NSE format: 'RELIANCE.NS' or BSE: '500325.BO'"
            }
        )

    # Level 2 — existence check
    is_valid_ticker, ticker_error = validate_ticker_exists(body.ticker)
    if not is_valid_ticker:
        raise HTTPException(
            status_code = 404,
            detail      = {
                "error"  : "ticker_not_found",
                "message": ticker_error,
            }
        )

    # Run graph — just a dict with ticker, matching your existing code
    try:
        final_state = graph.invoke({"ticker_of_company": body.ticker.strip().upper()})

        return AnalyzeResponse(
            ticker             = body.ticker,
            news_report        = final_state.get("news_analyst_report", ""),
            technical_report   = final_state.get("technical_analyst_report", ""),
            fundamental_report = final_state.get("fundamental_analyst_report", ""),
            market_report      = final_state.get("market_analyst_report", ""),
            sector_report      = final_state.get("sector_analyst_report", ""),
            status             = "success",
        )

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail      = {
                "error"  : "analysis_failed",
                "message": str(e),
            }
        )

    


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)