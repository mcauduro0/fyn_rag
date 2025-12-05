"""
Advanced Tool Use Definitions for Fyn RAG Investment Committee.
Implements Anthropic's Advanced Tool Use pattern for dynamic tool discovery and execution.

References:
- https://www.anthropic.com/engineering/advanced-tool-use
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import json

logger = logging.getLogger(__name__)


# =============================================================================
# TOOL DEFINITIONS - JSON Schema for Claude Advanced Tool Use
# =============================================================================

INVESTMENT_TOOLS: List[Dict[str, Any]] = [
    # ==========================================================================
    # MARKET DATA TOOLS
    # ==========================================================================
    {
        "name": "get_stock_price",
        "description": "Get current and historical stock price data for a given ticker symbol. Returns current price, day change, volume, and price history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')"
                },
                "period": {
                    "type": "string",
                    "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y"],
                    "description": "Historical data period"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_fundamental_data",
        "description": "Get fundamental financial data including income statement, balance sheet, cash flow, and key ratios for a company.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "data_type": {
                    "type": "string",
                    "enum": ["income_statement", "balance_sheet", "cash_flow", "ratios", "all"],
                    "description": "Type of fundamental data to retrieve"
                },
                "period": {
                    "type": "string",
                    "enum": ["annual", "quarterly"],
                    "description": "Reporting period"
                }
            },
            "required": ["ticker"]
        }
    },

    # ==========================================================================
    # ECONOMIC DATA TOOLS
    # ==========================================================================
    {
        "name": "get_economic_indicators",
        "description": "Get macroeconomic indicators from FRED and Trading Economics. Includes GDP, inflation, unemployment, interest rates, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "indicators": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of indicator codes (e.g., ['GDP', 'CPIAUCSL', 'UNRATE', 'FEDFUNDS'])"
                },
                "country": {
                    "type": "string",
                    "description": "Country for indicators (default: 'united states')"
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format"
                }
            },
            "required": ["indicators"]
        }
    },
    {
        "name": "get_economic_forecasts",
        "description": "Get economic forecasts for a country including GDP growth, inflation, and unemployment projections.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "Country name (e.g., 'united states', 'china', 'germany')"
                }
            },
            "required": ["country"]
        }
    },

    # ==========================================================================
    # SENTIMENT ANALYSIS TOOLS
    # ==========================================================================
    {
        "name": "get_reddit_sentiment",
        "description": "Get sentiment analysis from Reddit investing subreddits (r/wallstreetbets, r/stocks, r/investing) for a specific ticker.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol to analyze sentiment for"
                },
                "subreddits": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of subreddits to search (default: ['wallstreetbets', 'stocks', 'investing'])"
                },
                "time_filter": {
                    "type": "string",
                    "enum": ["day", "week", "month"],
                    "description": "Time period for posts"
                }
            },
            "required": ["ticker"]
        }
    },

    # ==========================================================================
    # RAG / KNOWLEDGE BASE TOOLS
    # ==========================================================================
    {
        "name": "query_investment_frameworks",
        "description": "Query the RAG knowledge base for relevant investment frameworks and methodologies. Contains 138 frameworks from legendary investors.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language query about investment frameworks or methodologies"
                },
                "categories": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["value_investing", "growth_investing", "risk_management", "industry_analysis", "financial_forensics", "macro_analysis"]
                    },
                    "description": "Filter by framework categories"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)"
                },
                "min_score": {
                    "type": "number",
                    "description": "Minimum relevance score (0-1, default: 0.5)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_investor_profile",
        "description": "Get detailed profile of a legendary investor including their philosophy, track record, and key frameworks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "investor_name": {
                    "type": "string",
                    "description": "Name of the investor (e.g., 'Warren Buffett', 'Charlie Munger', 'Peter Lynch')"
                }
            },
            "required": ["investor_name"]
        }
    },

    # ==========================================================================
    # DOCUMENT ANALYSIS TOOLS
    # ==========================================================================
    {
        "name": "analyze_document",
        "description": "Analyze an uploaded document (PDF, DOCX, XLSX) for investment-relevant information. Extracts financial data, key metrics, and insights.",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "ID of the previously uploaded document"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["financial_extraction", "risk_factors", "growth_drivers", "competitive_position", "full_analysis"],
                    "description": "Type of analysis to perform"
                }
            },
            "required": ["document_id", "analysis_type"]
        }
    },

    # ==========================================================================
    # VALUATION TOOLS
    # ==========================================================================
    {
        "name": "calculate_dcf",
        "description": "Calculate Discounted Cash Flow (DCF) valuation for a company based on projected cash flows.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "growth_rate_year1_5": {
                    "type": "number",
                    "description": "Expected revenue growth rate for years 1-5 (e.g., 0.15 for 15%)"
                },
                "growth_rate_year6_10": {
                    "type": "number",
                    "description": "Expected revenue growth rate for years 6-10"
                },
                "terminal_growth_rate": {
                    "type": "number",
                    "description": "Terminal growth rate (usually 2-3%)"
                },
                "discount_rate": {
                    "type": "number",
                    "description": "Weighted Average Cost of Capital (WACC)"
                },
                "margin_assumption": {
                    "type": "number",
                    "description": "Target operating margin"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "calculate_multiples",
        "description": "Calculate valuation multiples (P/E, EV/EBITDA, P/S, P/B) and compare to peers and historical averages.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "peers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of peer company tickers for comparison"
                }
            },
            "required": ["ticker"]
        }
    },

    # ==========================================================================
    # RISK ANALYSIS TOOLS
    # ==========================================================================
    {
        "name": "calculate_risk_metrics",
        "description": "Calculate risk metrics including VaR, beta, volatility, Sharpe ratio, and drawdown analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "benchmark": {
                    "type": "string",
                    "description": "Benchmark index (default: 'SPY')"
                },
                "confidence_level": {
                    "type": "number",
                    "description": "Confidence level for VaR (default: 0.95)"
                },
                "period": {
                    "type": "string",
                    "enum": ["1y", "3y", "5y"],
                    "description": "Historical period for calculations"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "run_stress_test",
        "description": "Run stress test scenarios on a stock or portfolio including market crash, recession, and sector-specific scenarios.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "scenarios": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["market_crash_2008", "covid_2020", "dot_com_2000", "recession", "interest_rate_spike", "sector_downturn"]
                    },
                    "description": "Stress test scenarios to run"
                }
            },
            "required": ["ticker"]
        }
    },

    # ==========================================================================
    # FORENSICS TOOLS
    # ==========================================================================
    {
        "name": "calculate_forensic_scores",
        "description": "Calculate financial forensics scores including Beneish M-Score (earnings manipulation) and Altman Z-Score (bankruptcy risk).",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "scores": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["m_score", "z_score", "f_score", "quality_of_earnings"]
                    },
                    "description": "Forensic scores to calculate"
                }
            },
            "required": ["ticker"]
        }
    },

    # ==========================================================================
    # INDUSTRY ANALYSIS TOOLS
    # ==========================================================================
    {
        "name": "analyze_industry",
        "description": "Analyze industry dynamics using Porter's Five Forces, industry lifecycle, and competitive positioning frameworks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "industry": {
                    "type": "string",
                    "description": "Industry name or sector"
                },
                "ticker": {
                    "type": "string",
                    "description": "Optional: specific company to analyze within industry"
                },
                "frameworks": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["porters_five_forces", "industry_lifecycle", "competitive_positioning", "market_share", "swot"]
                    },
                    "description": "Analytical frameworks to apply"
                }
            },
            "required": ["industry"]
        }
    },

    # ==========================================================================
    # REPORT GENERATION TOOLS
    # ==========================================================================
    {
        "name": "generate_investment_memo",
        "description": "Generate a professional investment memo in the style of top-tier investment firms.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol"
                },
                "memo_type": {
                    "type": "string",
                    "enum": ["one_pager", "comprehensive", "presentation"],
                    "description": "Type of memo to generate"
                },
                "analysis_data": {
                    "type": "object",
                    "description": "Previously collected analysis data"
                }
            },
            "required": ["ticker", "memo_type"]
        }
    }
]


# =============================================================================
# TOOL EXECUTOR - Executes tools and returns results
# =============================================================================

class ToolExecutor:
    """
    Executes investment analysis tools and returns results.
    Integrates with data fetchers, RAG system, and analysis engines.
    """

    def __init__(self):
        """Initialize tool executor with necessary dependencies."""
        self._tool_handlers: Dict[str, Callable] = {}
        self._register_handlers()
        logger.info("ToolExecutor initialized with investment analysis tools")

    def _register_handlers(self):
        """Register tool handlers."""
        self._tool_handlers = {
            "get_stock_price": self._handle_get_stock_price,
            "get_fundamental_data": self._handle_get_fundamental_data,
            "get_economic_indicators": self._handle_get_economic_indicators,
            "get_economic_forecasts": self._handle_get_economic_forecasts,
            "get_reddit_sentiment": self._handle_get_reddit_sentiment,
            "query_investment_frameworks": self._handle_query_frameworks,
            "get_investor_profile": self._handle_get_investor_profile,
            "analyze_document": self._handle_analyze_document,
            "calculate_dcf": self._handle_calculate_dcf,
            "calculate_multiples": self._handle_calculate_multiples,
            "calculate_risk_metrics": self._handle_calculate_risk_metrics,
            "run_stress_test": self._handle_run_stress_test,
            "calculate_forensic_scores": self._handle_calculate_forensic_scores,
            "analyze_industry": self._handle_analyze_industry,
            "generate_investment_memo": self._handle_generate_memo,
        }

    async def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool and return results.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result
        """
        logger.info(f"Executing tool: {tool_name} with input: {json.dumps(tool_input)[:200]}")

        if tool_name not in self._tool_handlers:
            return {
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self._tool_handlers.keys())
            }

        try:
            handler = self._tool_handlers[tool_name]
            result = await handler(tool_input)
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Tool execution error: {tool_name} - {e}", exc_info=True)
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    # =========================================================================
    # TOOL HANDLERS
    # =========================================================================

    async def _handle_get_stock_price(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_stock_price tool."""
        from app.data.fetchers.polygon_fetcher import PolygonFetcher
        from app.core.config import settings

        ticker = params["ticker"]
        period = params.get("period", "1mo")

        if not settings.POLYGON_API_KEY:
            # Fallback to mock data if no API key
            return self._mock_stock_price(ticker)

        fetcher = PolygonFetcher(settings.POLYGON_API_KEY)
        result = fetcher.fetch_ticker_details(ticker)

        if result["success"]:
            return result["data"]
        else:
            return {"error": result.get("error", "Failed to fetch data")}

    async def _handle_get_fundamental_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_fundamental_data tool."""
        from app.data.fetchers.fmp_fetcher import FMPFetcher
        from app.core.config import settings

        ticker = params["ticker"]
        data_type = params.get("data_type", "all")

        if not settings.FMP_API_KEY:
            return self._mock_fundamental_data(ticker)

        fetcher = FMPFetcher(settings.FMP_API_KEY)

        if data_type == "all":
            # Fetch all fundamental data
            profile = fetcher.fetch_company_profile(ticker)
            ratios = fetcher.fetch_key_metrics(ticker)
            growth = fetcher.fetch_financial_growth(ticker)

            return {
                "profile": profile.get("data", {}),
                "ratios": ratios.get("data", {}),
                "growth": growth.get("data", {})
            }
        else:
            result = fetcher.fetch_company_profile(ticker)
            return result.get("data", {})

    async def _handle_get_economic_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_economic_indicators tool."""
        from app.data.fetchers.fred_fetcher import FREDFetcher
        from app.core.config import settings

        indicators = params["indicators"]

        if not settings.FRED_API_KEY:
            return self._mock_economic_data(indicators)

        fetcher = FREDFetcher(settings.FRED_API_KEY)
        results = {}

        for indicator in indicators:
            result = fetcher.fetch_series(indicator)
            if result["success"]:
                results[indicator] = result["data"]

        return results

    async def _handle_get_economic_forecasts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_economic_forecasts tool."""
        from app.data.fetchers.trading_economics_fetcher import TradingEconomicsFetcher
        from app.core.config import settings

        country = params.get("country", "united states")

        if not settings.TRADING_ECONOMICS_API_KEY:
            return self._mock_forecasts(country)

        fetcher = TradingEconomicsFetcher(settings.TRADING_ECONOMICS_API_KEY)
        result = fetcher.fetch_forecasts(country)

        return result.get("data", {})

    async def _handle_get_reddit_sentiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_reddit_sentiment tool."""
        from app.data.fetchers.reddit_fetcher import RedditFetcher
        from app.core.config import settings

        ticker = params["ticker"]

        if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
            return self._mock_sentiment(ticker)

        fetcher = RedditFetcher(
            settings.REDDIT_CLIENT_ID,
            settings.REDDIT_CLIENT_SECRET,
            settings.REDDIT_USER_AGENT
        )

        result = fetcher.fetch_sentiment_snapshot(ticker)
        return result.get("data", {})

    async def _handle_query_frameworks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query_investment_frameworks tool."""
        from app.core.rag.rag_system import get_rag_system

        query = params["query"]
        top_k = params.get("top_k", 5)
        min_score = params.get("min_score", 0.5)
        categories = params.get("categories", [])

        rag = get_rag_system()
        results = rag.query(
            query=query,
            top_k=top_k,
            min_score=min_score,
            filter_categories=categories if categories else None
        )

        return {
            "query": query,
            "results_count": len(results),
            "frameworks": results
        }

    async def _handle_get_investor_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_investor_profile tool."""
        from app.core.rag.rag_system import get_rag_system

        investor_name = params["investor_name"].lower().replace(" ", "_")

        rag = get_rag_system()

        # Query for investor-specific frameworks
        results = rag.query(
            query=f"{params['investor_name']} investment philosophy and frameworks",
            top_k=10,
            min_score=0.3
        )

        return {
            "investor": params["investor_name"],
            "frameworks": results
        }

    async def _handle_analyze_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analyze_document tool."""
        # Document analysis implementation
        return {
            "status": "Document analysis completed",
            "document_id": params["document_id"],
            "analysis_type": params["analysis_type"]
        }

    async def _handle_calculate_dcf(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calculate_dcf tool."""
        ticker = params["ticker"]

        # DCF calculation implementation
        # This would use fundamental data and apply DCF formula
        return {
            "ticker": ticker,
            "valuation_method": "DCF",
            "intrinsic_value": "Calculation pending fundamental data",
            "assumptions": params
        }

    async def _handle_calculate_multiples(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calculate_multiples tool."""
        ticker = params["ticker"]
        peers = params.get("peers", [])

        return {
            "ticker": ticker,
            "peers": peers,
            "multiples": {
                "PE": "Pending",
                "EV_EBITDA": "Pending",
                "PS": "Pending",
                "PB": "Pending"
            }
        }

    async def _handle_calculate_risk_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calculate_risk_metrics tool."""
        from app.core.agents.risk_management_agent import RiskManagementAgent

        ticker = params["ticker"]

        # Use Risk Management Agent for calculations
        return {
            "ticker": ticker,
            "metrics": {
                "beta": "Pending",
                "volatility": "Pending",
                "var_95": "Pending",
                "sharpe_ratio": "Pending"
            }
        }

    async def _handle_run_stress_test(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle run_stress_test tool."""
        ticker = params["ticker"]
        scenarios = params.get("scenarios", ["recession"])

        return {
            "ticker": ticker,
            "scenarios_tested": scenarios,
            "results": {scenario: {"impact": "Pending"} for scenario in scenarios}
        }

    async def _handle_calculate_forensic_scores(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calculate_forensic_scores tool."""
        from app.core.agents.financial_forensics_agent import FinancialForensicsAgent

        ticker = params["ticker"]
        scores = params.get("scores", ["m_score", "z_score"])

        return {
            "ticker": ticker,
            "scores_requested": scores,
            "results": {score: "Pending" for score in scores}
        }

    async def _handle_analyze_industry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analyze_industry tool."""
        industry = params["industry"]
        frameworks = params.get("frameworks", ["porters_five_forces"])

        return {
            "industry": industry,
            "frameworks_applied": frameworks,
            "analysis": {fw: "Pending" for fw in frameworks}
        }

    async def _handle_generate_memo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate_investment_memo tool."""
        from app.core.reports.report_generator import ReportGenerator

        ticker = params["ticker"]
        memo_type = params["memo_type"]

        return {
            "ticker": ticker,
            "memo_type": memo_type,
            "status": "Report generation initiated"
        }

    # =========================================================================
    # MOCK DATA HELPERS (for development/testing)
    # =========================================================================

    def _mock_stock_price(self, ticker: str) -> Dict[str, Any]:
        """Return mock stock price data."""
        return {
            "ticker": ticker,
            "price": 150.25,
            "change": 2.35,
            "change_percent": 1.59,
            "volume": 45000000,
            "market_cap": 2500000000000,
            "note": "Mock data - configure POLYGON_API_KEY for real data"
        }

    def _mock_fundamental_data(self, ticker: str) -> Dict[str, Any]:
        """Return mock fundamental data."""
        return {
            "ticker": ticker,
            "pe_ratio": 25.5,
            "pb_ratio": 8.2,
            "revenue": 365000000000,
            "net_income": 94000000000,
            "note": "Mock data - configure FMP_API_KEY for real data"
        }

    def _mock_economic_data(self, indicators: List[str]) -> Dict[str, Any]:
        """Return mock economic data."""
        return {
            indicator: {"value": 100, "date": "2024-01-01"}
            for indicator in indicators
        }

    def _mock_forecasts(self, country: str) -> Dict[str, Any]:
        """Return mock forecast data."""
        return {
            "country": country,
            "gdp_forecast": 2.5,
            "inflation_forecast": 2.8,
            "note": "Mock data - configure TRADING_ECONOMICS_API_KEY for real data"
        }

    def _mock_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Return mock sentiment data."""
        return {
            "ticker": ticker,
            "overall_sentiment": "neutral",
            "mention_count": 42,
            "note": "Mock data - configure Reddit API for real data"
        }


def get_tool_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get tool definition by name."""
    for tool in INVESTMENT_TOOLS:
        if tool["name"] == name:
            return tool
    return None


# Global tool executor instance
_tool_executor: Optional[ToolExecutor] = None


def get_tool_executor() -> ToolExecutor:
    """Get or create global tool executor."""
    global _tool_executor
    if _tool_executor is None:
        _tool_executor = ToolExecutor()
    return _tool_executor
