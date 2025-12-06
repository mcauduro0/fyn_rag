"""
API Health Check Endpoints.
Monitors the status of external API integrations.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api-health", tags=["API Health"])


class APIStatus(BaseModel):
    """Status of a single API."""
    name: str
    status: str  # "connected", "error", "not_configured"
    latency_ms: float | None = None
    last_checked: str
    error: str | None = None


class HealthCheckResponse(BaseModel):
    """Response for health check endpoint."""
    overall_status: str  # "healthy", "degraded", "unhealthy"
    apis: List[APIStatus]
    timestamp: str


async def check_polygon() -> APIStatus:
    """Check Polygon.io API status."""
    start = datetime.utcnow()

    if not settings.POLYGON_API_KEY:
        return APIStatus(
            name="Polygon.io",
            status="not_configured",
            last_checked=start.isoformat()
        )

    try:
        from app.data.fetchers.polygon_fetcher import PolygonFetcher
        fetcher = PolygonFetcher(settings.POLYGON_API_KEY)

        # Quick test - fetch ticker details
        result = fetcher.fetch_ticker_details("AAPL")
        latency = (datetime.utcnow() - start).total_seconds() * 1000

        if result["success"]:
            return APIStatus(
                name="Polygon.io",
                status="connected",
                latency_ms=round(latency, 2),
                last_checked=start.isoformat()
            )
        else:
            return APIStatus(
                name="Polygon.io",
                status="error",
                latency_ms=round(latency, 2),
                last_checked=start.isoformat(),
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        return APIStatus(
            name="Polygon.io",
            status="error",
            last_checked=start.isoformat(),
            error=str(e)
        )


async def check_fmp() -> APIStatus:
    """Check Financial Modeling Prep API status."""
    start = datetime.utcnow()

    if not settings.FMP_API_KEY:
        return APIStatus(
            name="FMP",
            status="not_configured",
            last_checked=start.isoformat()
        )

    try:
        from app.data.fetchers.fmp_fetcher import FMPFetcher
        fetcher = FMPFetcher(settings.FMP_API_KEY)

        result = fetcher.fetch_company_profile("AAPL")
        latency = (datetime.utcnow() - start).total_seconds() * 1000

        if result["success"]:
            return APIStatus(
                name="FMP",
                status="connected",
                latency_ms=round(latency, 2),
                last_checked=start.isoformat()
            )
        else:
            return APIStatus(
                name="FMP",
                status="error",
                latency_ms=round(latency, 2),
                last_checked=start.isoformat(),
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        return APIStatus(
            name="FMP",
            status="error",
            last_checked=start.isoformat(),
            error=str(e)
        )


async def check_fred() -> APIStatus:
    """Check FRED API status."""
    start = datetime.utcnow()

    if not settings.FRED_API_KEY:
        return APIStatus(
            name="FRED",
            status="not_configured",
            last_checked=start.isoformat()
        )

    try:
        from app.data.fetchers.fred_fetcher import FREDFetcher
        fetcher = FREDFetcher(settings.FRED_API_KEY)

        result = fetcher.fetch_series("GDP")
        latency = (datetime.utcnow() - start).total_seconds() * 1000

        if result["success"]:
            return APIStatus(
                name="FRED",
                status="connected",
                latency_ms=round(latency, 2),
                last_checked=start.isoformat()
            )
        else:
            return APIStatus(
                name="FRED",
                status="error",
                latency_ms=round(latency, 2),
                last_checked=start.isoformat(),
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        return APIStatus(
            name="FRED",
            status="error",
            last_checked=start.isoformat(),
            error=str(e)
        )


async def check_trading_economics() -> APIStatus:
    """Check Trading Economics API status."""
    start = datetime.utcnow()

    if not settings.TRADING_ECONOMICS_API_KEY:
        return APIStatus(
            name="Trading Economics",
            status="not_configured",
            last_checked=start.isoformat()
        )

    try:
        from app.data.fetchers.trading_economics_fetcher import TradingEconomicsFetcher
        fetcher = TradingEconomicsFetcher(settings.TRADING_ECONOMICS_API_KEY)

        result = fetcher.fetch_indicators("united states")
        latency = (datetime.utcnow() - start).total_seconds() * 1000

        if result["success"]:
            return APIStatus(
                name="Trading Economics",
                status="connected",
                latency_ms=round(latency, 2),
                last_checked=start.isoformat()
            )
        else:
            return APIStatus(
                name="Trading Economics",
                status="error",
                latency_ms=round(latency, 2),
                last_checked=start.isoformat(),
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        return APIStatus(
            name="Trading Economics",
            status="error",
            last_checked=start.isoformat(),
            error=str(e)
        )


async def check_reddit() -> APIStatus:
    """Check Reddit API status."""
    start = datetime.utcnow()

    if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
        return APIStatus(
            name="Reddit",
            status="not_configured",
            last_checked=start.isoformat()
        )

    try:
        from app.data.fetchers.reddit_fetcher import RedditFetcher
        fetcher = RedditFetcher(
            settings.REDDIT_CLIENT_ID,
            settings.REDDIT_CLIENT_SECRET,
            settings.REDDIT_USER_AGENT
        )

        result = fetcher.fetch_subreddit_posts("wallstreetbets", limit=1)
        latency = (datetime.utcnow() - start).total_seconds() * 1000

        if result["success"]:
            return APIStatus(
                name="Reddit",
                status="connected",
                latency_ms=round(latency, 2),
                last_checked=start.isoformat()
            )
        else:
            return APIStatus(
                name="Reddit",
                status="error",
                latency_ms=round(latency, 2),
                last_checked=start.isoformat(),
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        return APIStatus(
            name="Reddit",
            status="error",
            last_checked=start.isoformat(),
            error=str(e)
        )


async def check_openai() -> APIStatus:
    """Check OpenAI API status."""
    start = datetime.utcnow()

    if not settings.OPENAI_API_KEY:
        return APIStatus(
            name="OpenAI",
            status="not_configured",
            last_checked=start.isoformat()
        )

    # Just verify the key format is valid (don't make actual call to save tokens)
    if settings.OPENAI_API_KEY.startswith("sk-"):
        return APIStatus(
            name="OpenAI",
            status="connected",
            last_checked=start.isoformat()
        )
    else:
        return APIStatus(
            name="OpenAI",
            status="error",
            last_checked=start.isoformat(),
            error="Invalid API key format"
        )


async def check_anthropic() -> APIStatus:
    """Check Anthropic API status."""
    start = datetime.utcnow()

    if not settings.ANTHROPIC_API_KEY:
        return APIStatus(
            name="Anthropic",
            status="not_configured",
            last_checked=start.isoformat()
        )

    # Just verify the key format is valid
    if settings.ANTHROPIC_API_KEY.startswith("sk-ant-"):
        return APIStatus(
            name="Anthropic",
            status="connected",
            last_checked=start.isoformat()
        )
    else:
        return APIStatus(
            name="Anthropic",
            status="error",
            last_checked=start.isoformat(),
            error="Invalid API key format"
        )


@router.get("/status", response_model=HealthCheckResponse)
async def check_all_apis():
    """
    Check the status of all external API integrations.

    Returns connection status, latency, and any errors for each API.
    """
    logger.info("Running API health checks...")

    # Run all checks in parallel
    results = await asyncio.gather(
        check_polygon(),
        check_fmp(),
        check_fred(),
        check_trading_economics(),
        check_reddit(),
        check_openai(),
        check_anthropic(),
        return_exceptions=True
    )

    # Process results
    apis = []
    for result in results:
        if isinstance(result, Exception):
            apis.append(APIStatus(
                name="Unknown",
                status="error",
                last_checked=datetime.utcnow().isoformat(),
                error=str(result)
            ))
        else:
            apis.append(result)

    # Determine overall status
    connected = sum(1 for a in apis if a.status == "connected")
    errors = sum(1 for a in apis if a.status == "error")
    total = len(apis)

    if errors == 0 and connected == total:
        overall = "healthy"
    elif errors > total // 2:
        overall = "unhealthy"
    else:
        overall = "degraded"

    return HealthCheckResponse(
        overall_status=overall,
        apis=apis,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/status/{api_name}")
async def check_single_api(api_name: str):
    """
    Check the status of a specific API.

    Args:
        api_name: Name of the API (polygon, fmp, fred, trading_economics, reddit, openai, anthropic)
    """
    checkers = {
        "polygon": check_polygon,
        "fmp": check_fmp,
        "fred": check_fred,
        "trading_economics": check_trading_economics,
        "reddit": check_reddit,
        "openai": check_openai,
        "anthropic": check_anthropic
    }

    api_name_lower = api_name.lower()

    if api_name_lower not in checkers:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown API: {api_name}. Available: {list(checkers.keys())}"
        )

    result = await checkers[api_name_lower]()
    return result


@router.get("/configuration")
async def get_api_configuration():
    """
    Get the configuration status of all APIs (without exposing keys).

    Shows which APIs are configured vs not configured.
    """
    return {
        "apis": {
            "polygon": {
                "configured": bool(settings.POLYGON_API_KEY),
                "description": "Real-time and historical market data"
            },
            "fmp": {
                "configured": bool(settings.FMP_API_KEY),
                "description": "Fundamental financial data and ratios"
            },
            "fred": {
                "configured": bool(settings.FRED_API_KEY),
                "description": "Federal Reserve economic data"
            },
            "trading_economics": {
                "configured": bool(settings.TRADING_ECONOMICS_API_KEY),
                "description": "Global economic indicators and forecasts"
            },
            "reddit": {
                "configured": bool(settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET),
                "description": "Social sentiment from Reddit"
            },
            "openai": {
                "configured": bool(settings.OPENAI_API_KEY),
                "description": "GPT-4 for analysis"
            },
            "anthropic": {
                "configured": bool(settings.ANTHROPIC_API_KEY),
                "description": "Claude for Advanced Tool Use"
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }
