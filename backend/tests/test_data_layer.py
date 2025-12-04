"""
Tests for Data Fetchers and Document Processors.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from app.data.fetchers.base_fetcher import BaseFetcher
from app.data.processors.pdf_processor import PDFProcessor
from app.data.processors.docx_processor import DOCXProcessor
from app.data.processors.xlsx_processor import XLSXProcessor
from app.data.processors.document_processor import DocumentProcessor


class TestBaseFetcher:
    """Tests for BaseFetcher class."""
    
    def test_success_response(self):
        """Test creating a success response."""
        
        class TestFetcher(BaseFetcher):
            def _validate_credentials(self):
                pass
            
            def fetch(self, **kwargs):
                return self._success_response(
                    data={"test": "data"},
                    source="TestSource"
                )
        
        fetcher = TestFetcher()
        response = fetcher.fetch()
        
        assert response["success"] is True
        assert response["data"] == {"test": "data"}
        assert response["source"] == "TestSource"
        assert "timestamp" in response
    
    def test_error_response(self):
        """Test creating an error response."""
        
        class TestFetcher(BaseFetcher):
            def _validate_credentials(self):
                pass
            
            def fetch(self, **kwargs):
                return self._handle_error(
                    error=ValueError("Test error"),
                    source="TestSource"
                )
        
        fetcher = TestFetcher()
        response = fetcher.fetch()
        
        assert response["success"] is False
        assert "Test error" in response["error"]
        assert response["source"] == "TestSource"


class TestDocumentProcessors:
    """Tests for document processors."""
    
    def test_pdf_processor_validation(self):
        """Test PDF processor file validation."""
        processor = PDFProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.process("nonexistent.pdf")
    
    def test_docx_processor_validation(self):
        """Test DOCX processor file validation."""
        processor = DOCXProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.process("nonexistent.docx")
    
    def test_xlsx_processor_validation(self):
        """Test XLSX processor file validation."""
        processor = XLSXProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.process("nonexistent.xlsx")
    
    def test_document_processor_supported_formats(self):
        """Test DocumentProcessor supported formats."""
        processor = DocumentProcessor()
        
        formats = processor.get_supported_formats()
        
        assert '.pdf' in formats
        assert '.docx' in formats
        assert '.xlsx' in formats
    
    def test_document_processor_is_supported(self):
        """Test DocumentProcessor format checking."""
        processor = DocumentProcessor()
        
        assert processor.is_supported("test.pdf") is True
        assert processor.is_supported("test.docx") is True
        assert processor.is_supported("test.xlsx") is True
        assert processor.is_supported("test.txt") is False
        assert processor.is_supported("test.jpg") is False


class TestDataFetchersIntegration:
    """Integration tests for data fetchers (requires API keys)."""
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="Integration tests require --run-integration flag"
    )
    def test_polygon_fetcher(self):
        """Test Polygon fetcher with real API."""
        import os
        from app.data.fetchers.polygon_fetcher import PolygonFetcher
        
        api_key = os.getenv("POLYGON_API_KEY")
        if not api_key:
            pytest.skip("POLYGON_API_KEY not set")
        
        fetcher = PolygonFetcher(api_key)
        result = fetcher.fetch_quote("AAPL")
        
        assert result["success"] is True
        assert "data" in result
        assert result["data"]["ticker"] == "AAPL"
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="Integration tests require --run-integration flag"
    )
    def test_fmp_fetcher(self):
        """Test FMP fetcher with real API."""
        import os
        from app.data.fetchers.fmp_fetcher import FMPFetcher
        
        api_key = os.getenv("FMP_API_KEY")
        if not api_key:
            pytest.skip("FMP_API_KEY not set")
        
        fetcher = FMPFetcher(api_key)
        result = fetcher.fetch_company_profile("AAPL")
        
        assert result["success"] is True
        assert "data" in result
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="Integration tests require --run-integration flag"
    )
    def test_fred_fetcher(self):
        """Test FRED fetcher with real API."""
        import os
        from app.data.fetchers.fred_fetcher import FREDFetcher
        
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            pytest.skip("FRED_API_KEY not set")
        
        fetcher = FREDFetcher(api_key)
        result = fetcher.fetch_indicator("gdp")
        
        assert result["success"] is True
        assert "data" in result


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require API keys"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
