"""
FRED (Federal Reserve Economic Data) Fetcher.
Retrieves macroeconomic data from the Federal Reserve.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fredapi import Fred

from app.data.fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class FREDFetcher(BaseFetcher):
    """Fetcher for FRED economic data."""
    
    # Common economic indicators
    INDICATORS = {
        "gdp": "GDP",
        "unemployment": "UNRATE",
        "inflation": "CPIAUCSL",
        "fed_funds_rate": "DFF",
        "10y_treasury": "DGS10",
        "2y_treasury": "DGS2",
        "consumer_sentiment": "UMCSENT",
        "industrial_production": "INDPRO",
        "retail_sales": "RSXFS",
        "housing_starts": "HOUST"
    }
    
    def __init__(self, api_key: str):
        """
        Initialize FRED fetcher.
        
        Args:
            api_key: FRED API key
        """
        super().__init__(api_key)
        self.client = Fred(api_key=api_key)
    
    def _validate_credentials(self) -> None:
        """Validate FRED API key."""
        if not self.api_key:
            raise ValueError("FRED API key is required")
    
    def fetch(self, **kwargs) -> Dict[str, Any]:
        """Generic fetch method."""
        raise NotImplementedError("Use specific fetch methods")
    
    def fetch_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch a specific economic data series.
        
        Args:
            series_id: FRED series ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Series data
        """
        self._log_fetch("FRED", {"series_id": series_id})
        
        try:
            series = self.client.get_series(
                series_id,
                observation_start=start_date,
                observation_end=end_date
            )
            
            data = {
                "series_id": series_id,
                "data": series.to_dict(),
                "latest_value": float(series.iloc[-1]) if len(series) > 0 else None,
                "latest_date": series.index[-1].strftime("%Y-%m-%d") if len(series) > 0 else None
            }
            
            return self._success_response(data, "FRED Series")
            
        except Exception as e:
            return self._handle_error(e, "FRED Series")
    
    def fetch_indicator(self, indicator_name: str) -> Dict[str, Any]:
        """
        Fetch a common economic indicator by name.
        
        Args:
            indicator_name: Name of indicator (gdp, unemployment, inflation, etc.)
            
        Returns:
            Indicator data
        """
        series_id = self.INDICATORS.get(indicator_name.lower())
        
        if not series_id:
            return {
                "success": False,
                "error": f"Unknown indicator: {indicator_name}. Available: {list(self.INDICATORS.keys())}",
                "source": "FRED"
            }
        
        return self.fetch_series(series_id)
    
    def fetch_economic_snapshot(self) -> Dict[str, Any]:
        """
        Fetch snapshot of key economic indicators.
        
        Returns:
            Dictionary of key economic indicators
        """
        self._log_fetch("FRED", {"type": "economic_snapshot"})
        
        try:
            snapshot = {}
            
            for name, series_id in self.INDICATORS.items():
                try:
                    result = self.fetch_series(series_id)
                    if result["success"]:
                        snapshot[name] = {
                            "value": result["data"]["latest_value"],
                            "date": result["data"]["latest_date"],
                            "series_id": series_id
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch {name}: {e}")
                    snapshot[name] = None
            
            return self._success_response(snapshot, "FRED Economic Snapshot")
            
        except Exception as e:
            return self._handle_error(e, "FRED Economic Snapshot")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        print("FRED_API_KEY not found in environment")
        exit(1)
    
    fetcher = FREDFetcher(api_key)
    
    print("\nFetching economic snapshot...")
    snapshot = fetcher.fetch_economic_snapshot()
    
    if snapshot["success"]:
        print("\nKey Economic Indicators:")
        for name, data in snapshot["data"].items():
            if data:
                print(f"  {name}: {data['value']} (as of {data['date']})")
