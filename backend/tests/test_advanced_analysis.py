"""
Integration tests for Advanced Analysis with Tool Use.
Tests the complete investment analysis pipeline.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.core.tools.tool_definitions import (
    INVESTMENT_TOOLS,
    ToolExecutor,
    get_tool_by_name,
    get_tool_executor
)
from app.core.llm.advanced_tool_client import AdvancedToolClient, analyze_investment


class TestToolDefinitions:
    """Tests for investment tool definitions."""

    def test_investment_tools_count(self):
        """Verify we have the expected number of tools."""
        assert len(INVESTMENT_TOOLS) >= 15, "Should have at least 15 investment tools"

    def test_all_tools_have_required_fields(self):
        """Verify all tools have required schema fields."""
        required_fields = ["name", "description", "input_schema"]

        for tool in INVESTMENT_TOOLS:
            for field in required_fields:
                assert field in tool, f"Tool missing required field: {field}"

    def test_get_tool_by_name(self):
        """Test tool lookup by name."""
        tool = get_tool_by_name("get_stock_price")
        assert tool is not None
        assert tool["name"] == "get_stock_price"

        # Non-existent tool
        assert get_tool_by_name("non_existent") is None

    def test_tool_input_schemas_valid(self):
        """Verify all tool input schemas are valid JSON schema."""
        for tool in INVESTMENT_TOOLS:
            schema = tool["input_schema"]
            assert "type" in schema
            assert schema["type"] == "object"
            assert "properties" in schema


class TestToolExecutor:
    """Tests for the ToolExecutor class."""

    @pytest.fixture
    def executor(self):
        """Create a ToolExecutor instance."""
        return ToolExecutor()

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self, executor):
        """Test executing an unknown tool returns error."""
        result = await executor.execute("unknown_tool", {})
        assert "error" in result
        assert "Unknown tool" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_stock_price_mock(self, executor):
        """Test stock price tool with mock data."""
        result = await executor.execute("get_stock_price", {"ticker": "AAPL"})

        assert result["success"] is True
        assert "result" in result
        assert result["tool"] == "get_stock_price"

    @pytest.mark.asyncio
    async def test_execute_fundamental_data_mock(self, executor):
        """Test fundamental data tool with mock data."""
        result = await executor.execute("get_fundamental_data", {
            "ticker": "AAPL",
            "data_type": "all"
        })

        assert result["success"] is True
        assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_query_frameworks(self, executor):
        """Test querying investment frameworks."""
        with patch('app.core.tools.tool_definitions.get_rag_system') as mock_rag:
            mock_rag.return_value.query.return_value = [
                {"framework_name": "DCF Analysis", "content": "Test content", "score": 0.9}
            ]

            result = await executor.execute("query_investment_frameworks", {
                "query": "valuation methods",
                "top_k": 5
            })

            assert result["success"] is True


class TestAdvancedToolClient:
    """Tests for the AdvancedToolClient."""

    @pytest.fixture
    def mock_anthropic(self):
        """Mock the Anthropic client."""
        with patch('app.core.llm.advanced_tool_client.AsyncAnthropic') as mock:
            yield mock

    @pytest.fixture
    def client(self, mock_anthropic):
        """Create an AdvancedToolClient with mocked dependencies."""
        with patch('app.core.llm.advanced_tool_client.settings') as mock_settings:
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            return AdvancedToolClient()

    def test_client_initialization(self, client):
        """Test client initializes correctly."""
        assert client.model is not None
        assert client.system_prompt is not None
        assert len(client.system_prompt) > 0

    def test_system_prompt_contains_key_elements(self, client):
        """Verify system prompt includes key investment concepts."""
        prompt = client.system_prompt.lower()

        assert "investment" in prompt
        assert "analysis" in prompt
        assert "framework" in prompt

    @pytest.mark.asyncio
    async def test_analyze_with_mock_response(self, client, mock_anthropic):
        """Test analysis with mocked Anthropic response."""
        # Mock the message response
        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        mock_response.content = [MagicMock(text="Test analysis result", type="text")]

        mock_anthropic.return_value.messages.create = AsyncMock(return_value=mock_response)

        with patch.object(client, 'client', mock_anthropic.return_value):
            # This would need more complete mocking for a full test
            pass


class TestToolIntegration:
    """Integration tests for the complete tool use flow."""

    @pytest.mark.asyncio
    async def test_complete_analysis_flow_mock(self):
        """Test a complete analysis flow with mocked components."""
        with patch('app.core.llm.advanced_tool_client.AsyncAnthropic') as mock_anthropic:
            with patch('app.core.llm.advanced_tool_client.settings') as mock_settings:
                mock_settings.ANTHROPIC_API_KEY = "test-key"

                # Mock a complete analysis response
                mock_response = MagicMock()
                mock_response.stop_reason = "end_turn"
                mock_response.content = [
                    MagicMock(
                        text="Based on the analysis, AAPL shows strong fundamentals with a BUY recommendation.",
                        type="text"
                    )
                ]

                mock_anthropic.return_value.messages.create = AsyncMock(return_value=mock_response)

                client = AdvancedToolClient()
                client.client = mock_anthropic.return_value

                result = await client.analyze(
                    query="Analyze Apple stock",
                    context={"ticker": "AAPL"}
                )

                assert result["success"] is True
                assert "analysis" in result
                assert result["iterations"] >= 1


class TestToolCategories:
    """Test that tools are properly categorized."""

    def test_market_data_tools_exist(self):
        """Verify market data tools are defined."""
        market_tools = ["get_stock_price", "get_fundamental_data"]
        for tool_name in market_tools:
            assert get_tool_by_name(tool_name) is not None

    def test_economic_data_tools_exist(self):
        """Verify economic data tools are defined."""
        economic_tools = ["get_economic_indicators", "get_economic_forecasts"]
        for tool_name in economic_tools:
            assert get_tool_by_name(tool_name) is not None

    def test_sentiment_tools_exist(self):
        """Verify sentiment analysis tools are defined."""
        assert get_tool_by_name("get_reddit_sentiment") is not None

    def test_rag_tools_exist(self):
        """Verify RAG/knowledge base tools are defined."""
        rag_tools = ["query_investment_frameworks", "get_investor_profile"]
        for tool_name in rag_tools:
            assert get_tool_by_name(tool_name) is not None

    def test_valuation_tools_exist(self):
        """Verify valuation tools are defined."""
        valuation_tools = ["calculate_dcf", "calculate_multiples"]
        for tool_name in valuation_tools:
            assert get_tool_by_name(tool_name) is not None

    def test_risk_tools_exist(self):
        """Verify risk analysis tools are defined."""
        risk_tools = ["calculate_risk_metrics", "run_stress_test"]
        for tool_name in risk_tools:
            assert get_tool_by_name(tool_name) is not None

    def test_forensics_tools_exist(self):
        """Verify forensics tools are defined."""
        assert get_tool_by_name("calculate_forensic_scores") is not None

    def test_report_tools_exist(self):
        """Verify report generation tools are defined."""
        assert get_tool_by_name("generate_investment_memo") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
