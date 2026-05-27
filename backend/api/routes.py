from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import StreamingResponse

from core.logging import get_logger
from api.validators import (
    validate_ticker_format,
    validate_ticker_exists,
    validate_api_keys,
)
from api.limiter import limiter
from api.models import AnalyzeRequest
from service.analyzer_service import stream_analyze_events

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


@router.post("/analyze/stream")
@limiter.limit("3/minute")
async def analyze_stream(
    request: Request,
    body: AnalyzeRequest,
    groq_api_key: str = Header(..., alias="Groq-API-Key"),
):
    ticker = body.ticker.strip().upper()
    logger.info(f"Streaming analyze request received | ticker={ticker}")

    is_valid_key, key_error = validate_api_keys(groq_api_key=groq_api_key)
    if not is_valid_key:
        raise HTTPException(
            status_code=422, detail={"error": "invalid_api_key", "message": key_error}
        )

    is_valid_format, format_error = validate_ticker_format(ticker)
    if not is_valid_format:
        logger.warning(f"Invalid ticker format received | ticker={ticker}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": "invalid_ticker_format",
                "message": format_error,
                "hint": ("Use NSE format like 'RELIANCE.NS'"),
            },
        )

    is_valid_ticker, ticker_error = validate_ticker_exists(ticker)
    if not is_valid_ticker:
        logger.warning(f"Ticker not found | ticker={ticker}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ticker_not_found",
                "message": ticker_error,
            },
        )

    return StreamingResponse(
        stream_analyze_events(ticker=ticker, groq_api_key=groq_api_key),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
