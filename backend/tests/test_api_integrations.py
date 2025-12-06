"""
Integration tests for external API integrations.
Tests FRED, Trading Economics, and Reddit APIs.
"""

import pytest
from unittest.mock import patch, MagicMock
import os

from app.data.fetchers.fred_fetcher import FREDFetcher
from app.data.fetchers.trading_economics_fetcher import TradingEconomicsFetcher
from app.data.fetchers.reddit_fetcher import RedditFetcher


class TestFREDFetcher:
    """Tests for FRED API fetcher."""

    @pytest.fixture
    def fetcher(self):
        """Create FRED fetcher with test API key."""
        # Use environment variable or test key
        api_key = os.getenv("FRED_API_KEY", "test_key")
        return FREDFetcher(api_key)

    def test_fetcher_initialization(self, fetcher):
        """Test fetcher initializes correctly."""
        assert fetcher is not None
        assert fetcher.api_key is not None

    @pytest.mark.integration
    def test_fetch_gdp_series(self, fetcher):
        """Test fetching GDP series from FRED."""
        if not os.getenv("FRED_API_KEY"):
            pytest.skip("FRED_API_KEY not set")

        result = fetcher.fetch_series("GDP")

        assert result["success"] is True
        assert "data" in result

    @pytest.mark.integration
    def test_fetch_inflation_data(self, fetcher):
        """Test fetching inflation (CPI) data."""
        if not os.getenv("FRED_API_KEY"):
            pytest.skip("FRED_API_KEY not set")

        result = fetcher.fetch_series("CPIAUCSL")

        assert result["success"] is True

    def test_fetch_with_mock(self, fetcher):
        """Test fetching with mocked response."""
        mock_data = {
            "observations": [
                {"date": "2024-01-01", "value": "100.5"},
                {"date": "2024-02-01", "value": "101.2"}
            ]
        }

        with patch.object(fetcher, '_make_request', return_value=mock_data):
            result = fetcher.fetch_series("TEST")
            assert result["success"] is True


class TestTradingEconomicsFetcher:
    """Tests for Trading Economics API fetcher."""

    @pytest.fixture
    def fetcher(self):
        """Create Trading Economics fetcher."""
        api_key = os.getenv("TRADING_ECONOMICS_API_KEY", "test_key:test_secret")
        return TradingEconomicsFetcher(api_key)

    def test_fetcher_initialization(self, fetcher):
        """Test fetcher initializes correctly."""
        assert fetcher is not None

    def test_api_key_parsing(self, fetcher):
        """Test API key parsing with key:secret format."""
        te_fetcher = TradingEconomicsFetcher("mykey:mysecret")
        assert te_fetcher.key == "mykey"
        assert te_fetcher.secret == "mysecret"

    @pytest.mark.integration
    def test_fetch_us_indicators(self, fetcher):
        """Test fetching US economic indicators."""
        if not os.getenv("TRADING_ECONOMICS_API_KEY"):
            pytest.skip("TRADING_ECONOMICS_API_KEY not set")

        result = fetcher.fetch_indicators("united states")

        assert "success" in result
        if result["success"]:
            assert "data" in result

    @pytest.mark.integration
    def test_fetch_forecasts(self, fetcher):
        """Test fetching economic forecasts."""
        if not os.getenv("TRADING_ECONOMICS_API_KEY"):
            pytest.skip("TRADING_ECONOMICS_API_KEY not set")

        result = fetcher.fetch_forecasts("united states")

        assert "success" in result


class TestRedditFetcher:
    """Tests for Reddit API fetcher."""

    @pytest.fixture
    def fetcher(self):
        """Create Reddit fetcher with test credentials."""
        client_id = os.getenv("REDDIT_CLIENT_ID", "test_id")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET", "test_secret")
        user_agent = os.getenv("REDDIT_USER_AGENT", "FynRAG/1.0 test")
        return RedditFetcher(client_id, client_secret, user_agent)

    def test_fetcher_initialization(self, fetcher):
        """Test fetcher initializes correctly."""
        assert fetcher is not None
        assert fetcher.client_id is not None

    @pytest.mark.integration
    def test_fetch_wsb_posts(self, fetcher):
        """Test fetching posts from r/wallstreetbets."""
        if not os.getenv("REDDIT_CLIENT_ID"):
            pytest.skip("Reddit credentials not set")

        result = fetcher.fetch_subreddit_posts(
            subreddit_name="wallstreetbets",
            limit=10,
            sort="hot"
        )

        assert "success" in result
        if result["success"]:
            assert "data" in result
            assert "posts" in result["data"]

    @pytest.mark.integration
    def test_fetch_ticker_mentions(self, fetcher):
        """Test fetching mentions of a specific ticker."""
        if not os.getenv("REDDIT_CLIENT_ID"):
            pytest.skip("Reddit credentials not set")

        result = fetcher.fetch_ticker_mentions(
            ticker="AAPL",
            subreddit_name="wallstreetbets",
            limit=10
        )

        assert "success" in result

    @pytest.mark.integration
    def test_sentiment_snapshot(self, fetcher):
        """Test getting sentiment snapshot for a ticker."""
        if not os.getenv("REDDIT_CLIENT_ID"):
            pytest.skip("Reddit credentials not set")

        result = fetcher.fetch_sentiment_snapshot("AAPL")

        assert "success" in result
        if result["success"]:
            assert "data" in result
            assert "total_mentions" in result["data"]


class TestAPIErrorHandling:
    """Test error handling for API integrations."""

    def test_fred_invalid_key(self):
        """Test FRED with invalid API key."""
        fetcher = FREDFetcher("invalid_key")
        result = fetcher.fetch_series("GDP")

        # Should handle error gracefully
        assert "success" in result or "error" in result

    def test_trading_economics_invalid_key(self):
        """Test Trading Economics with invalid key."""
        fetcher = TradingEconomicsFetcher("invalid:key")
        result = fetcher.fetch_indicators("united states")

        # Should handle error gracefully
        assert "success" in result or "error" in result


class TestAPIResponseParsing:
    """Test parsing of API responses."""

    def test_fred_response_structure(self):
        """Test FRED response is properly structured."""
        fetcher = FREDFetcher("test_key")

        mock_data = {
            "observations": [
                {"date": "2024-01-01", "value": "100.5"},
                {"date": "2024-02-01", "value": "101.2"}
            ]
        }

        with patch.object(fetcher, '_make_request', return_value=mock_data):
            result = fetcher.fetch_series("TEST")

            assert result["success"] is True
            assert "data" in result
            assert "source" in result

    def test_trading_economics_response_structure(self):
        """Test Trading Economics response is properly structured."""
        fetcher = TradingEconomicsFetcher("test:key")

        mock_data = [
            {"Country": "United States", "Category": "GDP", "Value": 25000}
        ]

        with patch.object(fetcher, '_make_request', return_value=mock_data):
            result = fetcher.fetch_indicators("united states")

            assert result["success"] is True
            assert "data" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
