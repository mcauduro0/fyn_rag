"""
Trading Economics Data Fetcher.
Retrieves global economic indicators and forecasts.
"""

import logging
import requests
from typing import Dict, Any, Optional, List

from app.data.fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class TradingEconomicsFetcher(BaseFetcher):
    """Fetcher for Trading Economics API."""
    
    BASE_URL = "https://api.tradingeconomics.com"
    
    def __init__(self, api_key: str):
        """
        Initialize Trading Economics fetcher.
        
        Args:
            api_key: Trading Economics API key (format: KEY:SECRET)
        """
        super().__init__(api_key)
        self.session = requests.Session()
        # API key format: KEY:SECRET
        if ":" in api_key:
            self.key, self.secret = api_key.split(":", 1)
        else:
            self.key = api_key
            self.secret = None
    
    def _validate_credentials(self) -> None:
        """Validate Trading Economics API key."""
        if not self.api_key:
            raise ValueError("Trading Economics API key is required")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Make HTTP request to Trading Economics API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response
        """
        if params is None:
            params = {}
        
        params["c"] = self.key
        if self.secret:
            params["s"] = self.secret
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def fetch(self, **kwargs) -> Dict[str, Any]:
        """Generic fetch method."""
        raise NotImplementedError("Use specific fetch methods")
    
    def fetch_indicators(self, country: str = "united states") -> Dict[str, Any]:
        """
        Fetch economic indicators for a country.
        
        Args:
            country: Country name
            
        Returns:
            Economic indicators data
        """
        self._log_fetch("Trading Economics", {"country": country, "type": "indicators"})
        
        try:
            data = self._make_request(f"indicators/country/{country}")
            
            return self._success_response(data, "Trading Economics Indicators")
            
        except Exception as e:
            return self._handle_error(e, "Trading Economics Indicators")
    
    def fetch_historical(
        self,
        country: str,
        indicator: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch historical data for an indicator.
        
        Args:
            country: Country name
            indicator: Indicator name (e.g., 'gdp', 'inflation')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Historical data
        """
        self._log_fetch("Trading Economics", {
            "country": country,
            "indicator": indicator,
            "type": "historical"
        })
        
        try:
            endpoint = f"historical/country/{country}/indicator/{indicator}"
            params = {}
            
            if start_date:
                params["d1"] = start_date
            if end_date:
                params["d2"] = end_date
            
            data = self._make_request(endpoint, params)
            
            return self._success_response(data, "Trading Economics Historical")
            
        except Exception as e:
            return self._handle_error(e, "Trading Economics Historical")
    
    def fetch_forecasts(self, country: str = "united states") -> Dict[str, Any]:
        """
        Fetch economic forecasts for a country.
        
        Args:
            country: Country name
            
        Returns:
            Economic forecasts data
        """
        self._log_fetch("Trading Economics", {"country": country, "type": "forecasts"})
        
        try:
            data = self._make_request(f"forecast/country/{country}")
            
            return self._success_response(data, "Trading Economics Forecasts")
            
        except Exception as e:
            return self._handle_error(e, "Trading Economics Forecasts")
    
    def fetch_markets(self, country: str = "united states") -> Dict[str, Any]:
        """
        Fetch market data for a country.
        
        Args:
            country: Country name
            
        Returns:
            Market data
        """
        self._log_fetch("Trading Economics", {"country": country, "type": "markets"})
        
        try:
            data = self._make_request(f"markets/country/{country}")
            
            return self._success_response(data, "Trading Economics Markets")
            
        except Exception as e:
            return self._handle_error(e, "Trading Economics Markets")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("TRADING_ECONOMICS_API_KEY")
    if not api_key:
        print("TRADING_ECONOMICS_API_KEY not found in environment")
        exit(1)
    
    fetcher = TradingEconomicsFetcher(api_key)
    
    print("\nFetching US economic indicators...")
    indicators = fetcher.fetch_indicators("united states")
    
    if indicators["success"]:
        print(f"\nRetrieved {len(indicators['data'])} indicators")
