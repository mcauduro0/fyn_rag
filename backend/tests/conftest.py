"""
Pytest configuration and fixtures.
"""

import pytest
import os
from pathlib import Path


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests requiring API keys"
    )


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def sample_kb():
    """Provide sample knowledge base data."""
    return [
        {
            "name": "DCF Valuation",
            "category": "Valuation",
            "description": "Discounted Cash Flow valuation method",
            "core_concept": "Present value of future cash flows",
            "key_metrics": ["FCF", "WACC", "Terminal Value"],
            "application": "Used for valuing companies based on cash flow projections"
        },
        {
            "name": "Moat Analysis",
            "category": "Value Investing",
            "description": "Framework for identifying sustainable competitive advantages",
            "core_concept": "Economic moats protect long-term profitability",
            "key_metrics": ["Switching costs", "Network effects", "Brand strength"],
            "application": "Identify companies with durable competitive advantages"
        }
    ]


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
