"""
Live Integration Tests for External APIs.
These tests call real APIs with actual credentials.

Run with: pytest tests/test_live_apis.py -v --run-live
"""

import pytest
import os
import asyncio
from datetime import datetime

# Skip all tests if not running live tests
pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_LIVE_TESTS"),
    reason="Live API tests disabled. Set RUN_LIVE_TESTS=1 to run."
)


class TestPolygonLive:
    """Live tests for Polygon.io API."""

    @pytest.fixture
    def fetcher(self):
        from app.data.fetchers.polygon_fetcher import PolygonFetcher
        api_key = os.getenv("POLYGON_API_KEY")
        if not api_key:
            pytest.skip("POLYGON_API_KEY not set")
        return PolygonFetcher(api_key)

    def test_fetch_ticker_details_aapl(self, fetcher):
        """Test fetching Apple ticker details."""
        result = fetcher.fetch_ticker_details("AAPL")

        assert result["success"] is True
        assert result["data"]["ticker"] == "AAPL"
        assert result["data"]["name"] is not None
        assert "Apple" in result["data"]["name"]
        print(f"\n✅ AAPL Details: {result['data']['name']}")
        print(f"   Market Cap: ${result['data'].get('market_cap', 'N/A'):,}")

    def test_fetch_aggregates_msft(self, fetcher):
        """Test fetching Microsoft price aggregates."""
        result = fetcher.fetch_aggregates("MSFT", timespan="day", limit=5)

        assert result["success"] is True
        assert result["data"]["ticker"] == "MSFT"
        assert len(result["data"]["bars"]) > 0

        latest_bar = result["data"]["bars"][-1]
        print(f"\n✅ MSFT Latest Bar:")
        print(f"   Close: ${latest_bar['close']}")
        print(f"   Volume: {latest_bar['volume']:,}")

    def test_fetch_last_trade_googl(self, fetcher):
        """Test fetching Google last trade."""
        result = fetcher.fetch_last_trade("GOOGL")

        # May fail outside market hours
        if result["success"]:
            assert result["data"]["ticker"] == "GOOGL"
            print(f"\n✅ GOOGL Last Trade: ${result['data']['price']}")
        else:
            print(f"\n⚠️ GOOGL Trade (may be outside market hours): {result.get('error')}")


class TestFMPLive:
    """Live tests for Financial Modeling Prep API."""

    @pytest.fixture
    def fetcher(self):
        from app.data.fetchers.fmp_fetcher import FMPFetcher
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            pytest.skip("FMP_API_KEY not set")
        return FMPFetcher(api_key)

    def test_fetch_company_profile_aapl(self, fetcher):
        """Test fetching Apple company profile."""
        result = fetcher.fetch_company_profile("AAPL")

        assert result["success"] is True
        assert "companyName" in result["data"] or "symbol" in result["data"]
        print(f"\n✅ AAPL Profile: {result['data'].get('companyName', 'Apple Inc.')}")
        print(f"   Industry: {result['data'].get('industry', 'N/A')}")
        print(f"   CEO: {result['data'].get('ceo', 'N/A')}")

    def test_fetch_income_statement_msft(self, fetcher):
        """Test fetching Microsoft income statement."""
        result = fetcher.fetch_income_statement("MSFT", limit=1)

        assert result["success"] is True
        assert isinstance(result["data"], list)

        if len(result["data"]) > 0:
            latest = result["data"][0]
            print(f"\n✅ MSFT Income Statement:")
            print(f"   Revenue: ${latest.get('revenue', 0):,.0f}")
            print(f"   Net Income: ${latest.get('netIncome', 0):,.0f}")

    def test_fetch_key_metrics_nvda(self, fetcher):
        """Test fetching NVIDIA key metrics."""
        result = fetcher.fetch_key_metrics("NVDA", limit=1)

        assert result["success"] is True

        if len(result["data"]) > 0:
            metrics = result["data"][0]
            print(f"\n✅ NVDA Key Metrics:")
            print(f"   PE Ratio: {metrics.get('peRatio', 'N/A')}")
            print(f"   ROE: {metrics.get('roe', 'N/A')}")

    def test_fetch_dcf_tsla(self, fetcher):
        """Test fetching Tesla DCF valuation."""
        result = fetcher.fetch_dcf("TSLA")

        assert result["success"] is True

        if isinstance(result["data"], list) and len(result["data"]) > 0:
            dcf = result["data"][0]
            print(f"\n✅ TSLA DCF Valuation:")
            print(f"   DCF: ${dcf.get('dcf', 'N/A')}")
            print(f"   Stock Price: ${dcf.get('Stock Price', 'N/A')}")


class TestFREDLive:
    """Live tests for FRED API."""

    @pytest.fixture
    def fetcher(self):
        from app.data.fetchers.fred_fetcher import FREDFetcher
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            pytest.skip("FRED_API_KEY not set")
        return FREDFetcher(api_key)

    def test_fetch_gdp(self, fetcher):
        """Test fetching GDP data."""
        result = fetcher.fetch_series("GDP")

        assert result["success"] is True
        assert result["data"]["series_id"] == "GDP"
        assert result["data"]["latest_value"] is not None

        print(f"\n✅ US GDP: ${result['data']['latest_value']:,.0f}B")
        print(f"   Date: {result['data']['latest_date']}")

    def test_fetch_unemployment(self, fetcher):
        """Test fetching unemployment rate."""
        result = fetcher.fetch_indicator("unemployment")

        assert result["success"] is True
        print(f"\n✅ Unemployment Rate: {result['data']['latest_value']}%")

    def test_fetch_inflation(self, fetcher):
        """Test fetching CPI inflation."""
        result = fetcher.fetch_series("CPIAUCSL")

        assert result["success"] is True
        print(f"\n✅ CPI: {result['data']['latest_value']}")

    def test_fetch_fed_funds_rate(self, fetcher):
        """Test fetching Fed Funds Rate."""
        result = fetcher.fetch_series("DFF")

        assert result["success"] is True
        print(f"\n✅ Fed Funds Rate: {result['data']['latest_value']}%")


class TestTradingEconomicsLive:
    """Live tests for Trading Economics API."""

    @pytest.fixture
    def fetcher(self):
        from app.data.fetchers.trading_economics_fetcher import TradingEconomicsFetcher
        api_key = os.getenv("TRADING_ECONOMICS_API_KEY")
        if not api_key:
            pytest.skip("TRADING_ECONOMICS_API_KEY not set")
        return TradingEconomicsFetcher(api_key)

    def test_fetch_us_indicators(self, fetcher):
        """Test fetching US economic indicators."""
        result = fetcher.fetch_indicators("united states")

        if result["success"]:
            assert isinstance(result["data"], list)
            print(f"\n✅ US Indicators: {len(result['data'])} found")
            if len(result["data"]) > 0:
                sample = result["data"][0]
                print(f"   Sample: {sample.get('Category', 'N/A')}: {sample.get('LatestValue', 'N/A')}")
        else:
            print(f"\n⚠️ Trading Economics: {result.get('error', 'Unknown error')}")


class TestRedditLive:
    """Live tests for Reddit API."""

    @pytest.fixture
    def fetcher(self):
        from app.data.fetchers.reddit_fetcher import RedditFetcher
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        if not client_id or not client_secret:
            pytest.skip("Reddit credentials not set")
        return RedditFetcher(client_id, client_secret, "FynRAG/1.0 test")

    def test_fetch_wsb_hot_posts(self, fetcher):
        """Test fetching hot posts from r/wallstreetbets."""
        result = fetcher.fetch_subreddit_posts("wallstreetbets", limit=5, sort="hot")

        assert result["success"] is True
        assert result["data"]["subreddit"] == "wallstreetbets"
        assert len(result["data"]["posts"]) > 0

        print(f"\n✅ WSB Hot Posts: {len(result['data']['posts'])} fetched")
        for post in result["data"]["posts"][:3]:
            print(f"   - {post['title'][:60]}... (Score: {post['score']})")

    def test_fetch_ticker_mentions_nvda(self, fetcher):
        """Test fetching NVDA mentions."""
        result = fetcher.fetch_ticker_mentions("NVDA", limit=10)

        if result["success"]:
            print(f"\n✅ NVDA Mentions: {result['data']['count']} found")
        else:
            print(f"\n⚠️ NVDA Mentions: {result.get('error', 'None found')}")


class TestToolExecutorLive:
    """Live tests for ToolExecutor with real APIs."""

    @pytest.fixture
    def executor(self):
        from app.core.tools.tool_definitions import ToolExecutor
        return ToolExecutor()

    @pytest.mark.asyncio
    async def test_get_stock_price_live(self, executor):
        """Test stock price tool with real data."""
        result = await executor.execute("get_stock_price", {"ticker": "AAPL"})

        assert result["success"] is True
        print(f"\n✅ Tool get_stock_price: {result['result']}")

    @pytest.mark.asyncio
    async def test_get_fundamental_data_live(self, executor):
        """Test fundamental data tool with real data."""
        result = await executor.execute("get_fundamental_data", {
            "ticker": "MSFT",
            "data_type": "all"
        })

        assert result["success"] is True
        print(f"\n✅ Tool get_fundamental_data executed")

    @pytest.mark.asyncio
    async def test_get_economic_indicators_live(self, executor):
        """Test economic indicators tool."""
        result = await executor.execute("get_economic_indicators", {
            "indicators": ["GDP", "UNRATE", "CPIAUCSL"]
        })

        assert result["success"] is True
        print(f"\n✅ Tool get_economic_indicators: {len(result['result'])} indicators")


if __name__ == "__main__":
    # Run with live tests enabled
    os.environ["RUN_LIVE_TESTS"] = "1"
    pytest.main([__file__, "-v", "-s"])
