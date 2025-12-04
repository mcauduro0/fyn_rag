"""
Financial Modeling Prep (FMP) Data Fetcher.
Retrieves fundamental financial data, ratios, and company information.
"""

import logging
import requests
from typing import Dict, Any, Optional, List

from app.data.fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class FMPFetcher(BaseFetcher):
    """Fetcher for Financial Modeling Prep API."""
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    
    def __init__(self, api_key: str):
        """
        Initialize FMP fetcher.
        
        Args:
            api_key: FMP API key
        """
        super().__init__(api_key)
        self.session = requests.Session()
    
    def _validate_credentials(self) -> None:
        """Validate FMP API key."""
        if not self.api_key:
            raise ValueError("FMP API key is required")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to FMP API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response
        """
        if params is None:
            params = {}
        
        params["apikey"] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def fetch(self, **kwargs) -> Dict[str, Any]:
        """Generic fetch method."""
        raise NotImplementedError("Use specific fetch methods")
    
    def fetch_company_profile(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch company profile and overview.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Company profile data
        """
        self._log_fetch("FMP", {"ticker": ticker, "type": "profile"})
        
        try:
            data = self._make_request(f"profile/{ticker}")
            
            if isinstance(data, list) and len(data) > 0:
                profile = data[0]
            else:
                profile = data
            
            return self._success_response(profile, "FMP Company Profile")
            
        except Exception as e:
            return self._handle_error(e, "FMP Company Profile")
    
    def fetch_income_statement(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Fetch income statement data.
        
        Args:
            ticker: Stock ticker symbol
            period: 'annual' or 'quarter'
            limit: Number of periods to fetch
            
        Returns:
            Income statement data
        """
        self._log_fetch("FMP", {"ticker": ticker, "type": "income_statement", "period": period})
        
        try:
            data = self._make_request(
                f"income-statement/{ticker}",
                params={"period": period, "limit": limit}
            )
            
            return self._success_response(data, "FMP Income Statement")
            
        except Exception as e:
            return self._handle_error(e, "FMP Income Statement")
    
    def fetch_balance_sheet(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Fetch balance sheet data.
        
        Args:
            ticker: Stock ticker symbol
            period: 'annual' or 'quarter'
            limit: Number of periods to fetch
            
        Returns:
            Balance sheet data
        """
        self._log_fetch("FMP", {"ticker": ticker, "type": "balance_sheet", "period": period})
        
        try:
            data = self._make_request(
                f"balance-sheet-statement/{ticker}",
                params={"period": period, "limit": limit}
            )
            
            return self._success_response(data, "FMP Balance Sheet")
            
        except Exception as e:
            return self._handle_error(e, "FMP Balance Sheet")
    
    def fetch_cash_flow(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Fetch cash flow statement data.
        
        Args:
            ticker: Stock ticker symbol
            period: 'annual' or 'quarter'
            limit: Number of periods to fetch
            
        Returns:
            Cash flow data
        """
        self._log_fetch("FMP", {"ticker": ticker, "type": "cash_flow", "period": period})
        
        try:
            data = self._make_request(
                f"cash-flow-statement/{ticker}",
                params={"period": period, "limit": limit}
            )
            
            return self._success_response(data, "FMP Cash Flow")
            
        except Exception as e:
            return self._handle_error(e, "FMP Cash Flow")
    
    def fetch_key_metrics(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Fetch key financial metrics and ratios.
        
        Args:
            ticker: Stock ticker symbol
            period: 'annual' or 'quarter'
            limit: Number of periods to fetch
            
        Returns:
            Key metrics data
        """
        self._log_fetch("FMP", {"ticker": ticker, "type": "key_metrics", "period": period})
        
        try:
            data = self._make_request(
                f"key-metrics/{ticker}",
                params={"period": period, "limit": limit}
            )
            
            return self._success_response(data, "FMP Key Metrics")
            
        except Exception as e:
            return self._handle_error(e, "FMP Key Metrics")
    
    def fetch_financial_ratios(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Fetch financial ratios.
        
        Args:
            ticker: Stock ticker symbol
            period: 'annual' or 'quarter'
            limit: Number of periods to fetch
            
        Returns:
            Financial ratios data
        """
        self._log_fetch("FMP", {"ticker": ticker, "type": "ratios", "period": period})
        
        try:
            data = self._make_request(
                f"ratios/{ticker}",
                params={"period": period, "limit": limit}
            )
            
            return self._success_response(data, "FMP Financial Ratios")
            
        except Exception as e:
            return self._handle_error(e, "FMP Financial Ratios")
    
    def fetch_financial_growth(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Fetch financial growth metrics.
        
        Args:
            ticker: Stock ticker symbol
            period: 'annual' or 'quarter'
            limit: Number of periods to fetch
            
        Returns:
            Growth metrics data
        """
        self._log_fetch("FMP", {"ticker": ticker, "type": "growth", "period": period})
        
        try:
            data = self._make_request(
                f"financial-growth/{ticker}",
                params={"period": period, "limit": limit}
            )
            
            return self._success_response(data, "FMP Financial Growth")
            
        except Exception as e:
            return self._handle_error(e, "FMP Financial Growth")
    
    def fetch_dcf(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch DCF (Discounted Cash Flow) valuation.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            DCF valuation data
        """
        self._log_fetch("FMP", {"ticker": ticker, "type": "dcf"})
        
        try:
            data = self._make_request(f"discounted-cash-flow/{ticker}")
            
            return self._success_response(data, "FMP DCF Valuation")
            
        except Exception as e:
            return self._handle_error(e, "FMP DCF Valuation")
    
    def fetch_comprehensive_data(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch comprehensive fundamental data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Comprehensive financial data
        """
        self._log_fetch("FMP", {"ticker": ticker, "type": "comprehensive"})
        
        try:
            data = {
                "ticker": ticker,
                "profile": self.fetch_company_profile(ticker).get("data"),
                "income_statement": self.fetch_income_statement(ticker).get("data"),
                "balance_sheet": self.fetch_balance_sheet(ticker).get("data"),
                "cash_flow": self.fetch_cash_flow(ticker).get("data"),
                "key_metrics": self.fetch_key_metrics(ticker).get("data"),
                "ratios": self.fetch_financial_ratios(ticker).get("data"),
                "growth": self.fetch_financial_growth(ticker).get("data"),
                "dcf": self.fetch_dcf(ticker).get("data")
            }
            
            return self._success_response(data, "FMP Comprehensive Data")
            
        except Exception as e:
            return self._handle_error(e, "FMP Comprehensive Data")


if __name__ == "__main__":
    # Test the FMP fetcher
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("FMP_API_KEY not found in environment")
        exit(1)
    
    fetcher = FMPFetcher(api_key)
    
    # Test with Apple stock
    ticker = "AAPL"
    
    print(f"\nFetching profile for {ticker}...")
    profile = fetcher.fetch_company_profile(ticker)
    
    if profile["success"]:
        data = profile["data"]
        print(f"\nCompany: {data.get('companyName')}")
        print(f"Industry: {data.get('industry')}")
        print(f"Market Cap: ${data.get('mktCap'):,.0f}")
    else:
        print(f"\nError: {profile['error']}")
