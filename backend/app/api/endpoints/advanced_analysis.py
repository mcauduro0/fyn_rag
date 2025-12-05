"""
Advanced Analysis Endpoints with Anthropic Advanced Tool Use.
Provides institutional-grade investment analysis using Claude's latest capabilities.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.llm.advanced_tool_client import AdvancedToolClient, analyze_investment
from app.core.utils.monitoring import get_performance_monitor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/advanced-analysis", tags=["Advanced Analysis"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class AnalysisRequest(BaseModel):
    """Request model for investment analysis."""
    query: str = Field(..., description="Natural language analysis request")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol (if applicable)")
    asset_type: str = Field(default="listed", description="Asset type: 'listed' or 'illiquid'")
    analysis_depth: str = Field(default="standard", description="Analysis depth: 'quick', 'standard', 'deep'")
    include_sentiment: bool = Field(default=True, description="Include social media sentiment")
    include_forensics: bool = Field(default=True, description="Include financial forensics")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Should I invest in Apple (AAPL)? Consider valuation, growth prospects, and risks.",
                "ticker": "AAPL",
                "asset_type": "listed",
                "analysis_depth": "deep",
                "include_sentiment": True,
                "include_forensics": True
            }
        }


class QuickAnalysisRequest(BaseModel):
    """Simplified request for quick analysis."""
    ticker: str = Field(..., description="Stock ticker symbol")
    question: Optional[str] = Field(None, description="Specific question about the stock")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "NVDA",
                "question": "Is NVIDIA overvalued at current prices?"
            }
        }


class ComparisonRequest(BaseModel):
    """Request for comparing multiple stocks."""
    tickers: List[str] = Field(..., description="List of stock tickers to compare")
    criteria: List[str] = Field(
        default=["valuation", "growth", "risk", "moat"],
        description="Comparison criteria"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tickers": ["AAPL", "MSFT", "GOOGL"],
                "criteria": ["valuation", "growth", "risk", "moat"]
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for investment analysis."""
    success: bool
    request_id: str
    query: str
    ticker: Optional[str]
    analysis: Optional[str]
    recommendation: Optional[str]
    confidence: Optional[float]
    tool_results: Optional[List[Dict[str, Any]]]
    frameworks_used: Optional[List[str]]
    concerns: Optional[List[str]]
    opportunities: Optional[List[str]]
    execution_time_seconds: float
    model: str
    timestamp: str


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/analyze", response_model=AnalysisResponse)
async def perform_advanced_analysis(request: AnalysisRequest):
    """
    Perform advanced investment analysis using Claude's Advanced Tool Use.

    This endpoint leverages:
    - 138 investment frameworks from legendary investors
    - Real-time market data and fundamentals
    - Economic indicators and forecasts
    - Social media sentiment analysis
    - Financial forensics (M-Score, Z-Score)
    - DCF and multiples valuation

    The analysis is conducted as an agentic loop where Claude:
    1. Determines which tools to use based on the query
    2. Executes tools to gather data
    3. Applies relevant investment frameworks
    4. Synthesizes findings into a recommendation
    """
    logger.info(f"Advanced analysis request: {request.query[:100]}...")

    start_time = datetime.utcnow()
    request_id = f"analysis_{start_time.strftime('%Y%m%d_%H%M%S')}"

    try:
        # Build context from request
        context = request.context or {}
        context.update({
            "asset_type": request.asset_type,
            "analysis_depth": request.analysis_depth,
            "include_sentiment": request.include_sentiment,
            "include_forensics": request.include_forensics
        })

        if request.ticker:
            context["ticker"] = request.ticker

        # Initialize advanced tool client
        client = AdvancedToolClient(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096
        )

        # Perform analysis
        result = await client.analyze(
            query=request.query,
            context=context,
            max_iterations=15 if request.analysis_depth == "deep" else 10
        )

        execution_time = (datetime.utcnow() - start_time).total_seconds()

        # Track metrics
        monitor = get_performance_monitor()
        monitor.track_analysis_request(
            ticker=request.ticker,
            duration=execution_time,
            success=result["success"]
        )

        if result["success"]:
            # Extract recommendation and confidence from analysis
            analysis_text = result.get("analysis", "")
            recommendation = _extract_recommendation(analysis_text)
            confidence = _calculate_confidence(result)

            return AnalysisResponse(
                success=True,
                request_id=request_id,
                query=request.query,
                ticker=request.ticker,
                analysis=analysis_text,
                recommendation=recommendation,
                confidence=confidence,
                tool_results=result.get("tool_results", []),
                frameworks_used=_extract_frameworks(result),
                concerns=_extract_concerns(analysis_text),
                opportunities=_extract_opportunities(analysis_text),
                execution_time_seconds=execution_time,
                model=result.get("model", "claude-sonnet-4-5-20250929"),
                timestamp=datetime.utcnow().isoformat()
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-analysis")
async def quick_stock_analysis(request: QuickAnalysisRequest):
    """
    Quick analysis for a single stock.

    Provides a faster, focused analysis for quick decision-making.
    """
    query = request.question or f"Provide a quick investment analysis of {request.ticker}"

    result = await analyze_investment(
        query=query,
        ticker=request.ticker
    )

    return {
        "ticker": request.ticker,
        "analysis": result.get("analysis", "Analysis pending"),
        "success": result.get("success", False),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/compare")
async def compare_stocks(request: ComparisonRequest):
    """
    Compare multiple stocks across specified criteria.

    Provides side-by-side comparison for portfolio decisions.
    """
    if len(request.tickers) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 tickers required for comparison"
        )

    if len(request.tickers) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 tickers allowed for comparison"
        )

    query = f"""Compare the following stocks for investment: {', '.join(request.tickers)}

Criteria to evaluate:
{chr(10).join(f'- {c.title()}' for c in request.criteria)}

Provide a structured comparison with a clear recommendation on which stock(s) to prefer and why."""

    client = AdvancedToolClient()
    result = await client.analyze(
        query=query,
        context={"tickers": request.tickers, "criteria": request.criteria}
    )

    return {
        "tickers": request.tickers,
        "criteria": request.criteria,
        "comparison": result.get("analysis", "Comparison pending"),
        "success": result.get("success", False),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/frameworks")
async def list_available_frameworks():
    """
    List all available investment frameworks in the knowledge base.
    """
    from app.core.rag.rag_system import get_rag_system

    rag = get_rag_system()

    return {
        "total_frameworks": 138,
        "categories": [
            {
                "name": "Value Investing",
                "description": "Buffett, Graham, Munger methodologies",
                "framework_count": 35
            },
            {
                "name": "Growth & VC",
                "description": "Growth investing and venture capital frameworks",
                "framework_count": 28
            },
            {
                "name": "Risk Management",
                "description": "Risk assessment and portfolio management",
                "framework_count": 25
            },
            {
                "name": "Industry Analysis",
                "description": "Competitive analysis and industry research",
                "framework_count": 30
            },
            {
                "name": "Financial Forensics",
                "description": "Earnings quality and fraud detection",
                "framework_count": 20
            }
        ],
        "legendary_investors": [
            "Warren Buffett",
            "Charlie Munger",
            "Benjamin Graham",
            "Peter Lynch",
            "Howard Marks",
            "Ray Dalio",
            "Seth Klarman",
            "Joel Greenblatt"
        ]
    }


@router.get("/tools")
async def list_available_tools():
    """
    List all available analysis tools.
    """
    from app.core.tools.tool_definitions import INVESTMENT_TOOLS

    return {
        "total_tools": len(INVESTMENT_TOOLS),
        "tools": [
            {
                "name": tool["name"],
                "description": tool["description"]
            }
            for tool in INVESTMENT_TOOLS
        ]
    }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _extract_recommendation(analysis: str) -> str:
    """Extract recommendation from analysis text."""
    analysis_upper = analysis.upper()

    if "STRONG BUY" in analysis_upper:
        return "STRONG BUY"
    elif "BUY" in analysis_upper:
        return "BUY"
    elif "STRONG SELL" in analysis_upper:
        return "STRONG SELL"
    elif "SELL" in analysis_upper:
        return "SELL"
    else:
        return "HOLD"


def _calculate_confidence(result: Dict[str, Any]) -> float:
    """Calculate confidence score based on analysis completeness."""
    base_confidence = 0.5

    tool_results = result.get("tool_results", [])
    successful_tools = sum(1 for t in tool_results if t.get("success", False))

    if len(tool_results) > 0:
        tool_confidence = successful_tools / len(tool_results) * 0.3
    else:
        tool_confidence = 0

    # More iterations = more thorough analysis
    iterations = result.get("iterations", 1)
    iteration_bonus = min(iterations / 10, 0.2)

    return min(base_confidence + tool_confidence + iteration_bonus, 1.0)


def _extract_frameworks(result: Dict[str, Any]) -> List[str]:
    """Extract frameworks used from tool results."""
    frameworks = []

    for tool_result in result.get("tool_results", []):
        if tool_result.get("tool_name") == "query_investment_frameworks":
            if "result" in tool_result and "frameworks" in tool_result["result"]:
                for fw in tool_result["result"]["frameworks"]:
                    if isinstance(fw, dict) and "framework_name" in fw:
                        frameworks.append(fw["framework_name"])

    return list(set(frameworks))


def _extract_concerns(analysis: str) -> List[str]:
    """Extract key concerns from analysis."""
    concerns = []
    concern_keywords = ["risk", "concern", "warning", "caution", "threat", "weakness"]

    lines = analysis.split("\n")
    for line in lines:
        if any(kw in line.lower() for kw in concern_keywords):
            if len(line.strip()) > 10:
                concerns.append(line.strip()[:200])

    return concerns[:5]  # Top 5 concerns


def _extract_opportunities(analysis: str) -> List[str]:
    """Extract key opportunities from analysis."""
    opportunities = []
    opp_keywords = ["opportunity", "strength", "advantage", "growth", "potential", "upside"]

    lines = analysis.split("\n")
    for line in lines:
        if any(kw in line.lower() for kw in opp_keywords):
            if len(line.strip()) > 10:
                opportunities.append(line.strip()[:200])

    return opportunities[:5]  # Top 5 opportunities
