"""
Polygon.io Data Fetcher.
Retrieves real-time and historical market data.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from polygon import RESTClient

from app.data.fetchers.base_fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class PolygonFetcher(BaseFetcher):
    """Fetcher for Polygon.io market data API."""
    
    def __init__(self, api_key: str):
        """
        Initialize Polygon fetcher.
        
        Args:
            api_key: Polygon.io API key
        """
        super().__init__(api_key)
        self.client = RESTClient(api_key)
    
    def _validate_credentials(self) -> None:
        """Validate Polygon API key."""
        if not self.api_key:
            raise ValueError("Polygon API key is required")
    
    def fetch(self, **kwargs) -> Dict[str, Any]:
        """
        Generic fetch method (delegates to specific methods).
        
        Args:
            **kwargs: Parameters for the fetch operation
            
        Returns:
            Fetched data dictionary
        """
        raise NotImplementedError("Use specific fetch methods (fetch_quote, fetch_aggregates, etc.)")
    
    def fetch_quote(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch real-time quote for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Quote data dictionary
        """
        self._log_fetch("Polygon.io", {"ticker": ticker, "type": "quote"})
        
        try:
            quote = self.client.get_last_quote(ticker)
            
            data = {
                "ticker": ticker,
                "bid": quote.bid_price if hasattr(quote, 'bid_price') else None,
                "ask": quote.ask_price if hasattr(quote, 'ask_price') else None,
                "bid_size": quote.bid_size if hasattr(quote, 'bid_size') else None,
                "ask_size": quote.ask_size if hasattr(quote, 'ask_size') else None,
                "timestamp": quote.sip_timestamp if hasattr(quote, 'sip_timestamp') else None
            }
            
            return self._success_response(data, "Polygon.io Quote")
            
        except Exception as e:
            return self._handle_error(e, "Polygon.io Quote")
    
    def fetch_last_trade(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch last trade for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Trade data dictionary
        """
        self._log_fetch("Polygon.io", {"ticker": ticker, "type": "last_trade"})
        
        try:
            trade = self.client.get_last_trade(ticker)
            
            data = {
                "ticker": ticker,
                "price": trade.price if hasattr(trade, 'price') else None,
                "size": trade.size if hasattr(trade, 'size') else None,
                "exchange": trade.exchange if hasattr(trade, 'exchange') else None,
                "timestamp": trade.sip_timestamp if hasattr(trade, 'sip_timestamp') else None
            }
            
            return self._success_response(data, "Polygon.io Trade")
            
        except Exception as e:
            return self._handle_error(e, "Polygon.io Trade")
    
    def fetch_aggregates(
        self,
        ticker: str,
        timespan: str = "day",
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: int = 120
    ) -> Dict[str, Any]:
        """
        Fetch aggregate bars (OHLCV data).
        
        Args:
            ticker: Stock ticker symbol
            timespan: Timespan (minute, hour, day, week, month, quarter, year)
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            limit: Maximum number of results
            
        Returns:
            Aggregates data dictionary
        """
        # Default date range: last 120 days
        if not from_date:
            from_date = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        
        self._log_fetch("Polygon.io", {
            "ticker": ticker,
            "type": "aggregates",
            "timespan": timespan,
            "from": from_date,
            "to": to_date
        })
        
        try:
            aggs = self.client.get_aggs(
                ticker=ticker,
                multiplier=1,
                timespan=timespan,
                from_=from_date,
                to=to_date,
                limit=limit
            )
            
            bars = []
            for agg in aggs:
                bars.append({
                    "timestamp": agg.timestamp if hasattr(agg, 'timestamp') else None,
                    "open": agg.open if hasattr(agg, 'open') else None,
                    "high": agg.high if hasattr(agg, 'high') else None,
                    "low": agg.low if hasattr(agg, 'low') else None,
                    "close": agg.close if hasattr(agg, 'close') else None,
                    "volume": agg.volume if hasattr(agg, 'volume') else None,
                    "vwap": agg.vwap if hasattr(agg, 'vwap') else None,
                    "transactions": agg.transactions if hasattr(agg, 'transactions') else None
                })
            
            data = {
                "ticker": ticker,
                "timespan": timespan,
                "from": from_date,
                "to": to_date,
                "bars": bars,
                "count": len(bars)
            }
            
            return self._success_response(data, "Polygon.io Aggregates")
            
        except Exception as e:
            return self._handle_error(e, "Polygon.io Aggregates")
    
    def fetch_ticker_details(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch detailed information about a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Ticker details dictionary
        """
        self._log_fetch("Polygon.io", {"ticker": ticker, "type": "details"})
        
        try:
            details = self.client.get_ticker_details(ticker)
            
            data = {
                "ticker": details.ticker if hasattr(details, 'ticker') else ticker,
                "name": details.name if hasattr(details, 'name') else None,
                "market": details.market if hasattr(details, 'market') else None,
                "locale": details.locale if hasattr(details, 'locale') else None,
                "primary_exchange": details.primary_exchange if hasattr(details, 'primary_exchange') else None,
                "type": details.type if hasattr(details, 'type') else None,
                "currency_name": details.currency_name if hasattr(details, 'currency_name') else None,
                "market_cap": details.market_cap if hasattr(details, 'market_cap') else None,
                "share_class_shares_outstanding": details.share_class_shares_outstanding if hasattr(details, 'share_class_shares_outstanding') else None,
                "weighted_shares_outstanding": details.weighted_shares_outstanding if hasattr(details, 'weighted_shares_outstanding') else None,
                "description": details.description if hasattr(details, 'description') else None,
                "homepage_url": details.homepage_url if hasattr(details, 'homepage_url') else None,
                "total_employees": details.total_employees if hasattr(details, 'total_employees') else None,
                "list_date": details.list_date if hasattr(details, 'list_date') else None,
                "sic_code": details.sic_code if hasattr(details, 'sic_code') else None,
                "sic_description": details.sic_description if hasattr(details, 'sic_description') else None
            }
            
            return self._success_response(data, "Polygon.io Ticker Details")
            
        except Exception as e:
            return self._handle_error(e, "Polygon.io Ticker Details")
    
    def fetch_market_snapshot(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch complete market snapshot for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Complete market data including quote, trade, and aggregates
        """
        self._log_fetch("Polygon.io", {"ticker": ticker, "type": "snapshot"})
        
        try:
            # Fetch multiple data points
            quote_data = self.fetch_quote(ticker)
            trade_data = self.fetch_last_trade(ticker)
            details_data = self.fetch_ticker_details(ticker)
            
            # Combine into snapshot
            data = {
                "ticker": ticker,
                "quote": quote_data.get("data") if quote_data.get("success") else None,
                "last_trade": trade_data.get("data") if trade_data.get("success") else None,
                "details": details_data.get("data") if details_data.get("success") else None
            }
            
            return self._success_response(data, "Polygon.io Market Snapshot")
            
        except Exception as e:
            return self._handle_error(e, "Polygon.io Market Snapshot")


if __name__ == "__main__":
    # Test the Polygon fetcher
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        print("POLYGON_API_KEY not found in environment")
        exit(1)
    
    fetcher = PolygonFetcher(api_key)
    
    # Test with Apple stock
    ticker = "AAPL"
    
    print(f"\nFetching data for {ticker}...")
    snapshot = fetcher.fetch_market_snapshot(ticker)
    
    if snapshot["success"]:
        print("\nSnapshot retrieved successfully!")
        print(f"Company: {snapshot['data']['details']['name']}")
        print(f"Last Price: ${snapshot['data']['last_trade']['price']}")
    else:
        print(f"\nError: {snapshot['error']}")
