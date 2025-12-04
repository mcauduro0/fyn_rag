"""
Base class for all data fetchers.
Provides common functionality and interface for data retrieval.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):
    """Abstract base class for data fetchers."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the fetcher.
        
        Args:
            api_key: API key for the data source
        """
        self.api_key = api_key
        self._validate_credentials()
    
    @abstractmethod
    def _validate_credentials(self) -> None:
        """Validate that required credentials are present."""
        pass
    
    @abstractmethod
    def fetch(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from the source.
        
        Returns:
            Dictionary containing fetched data
        """
        pass
    
    def _log_fetch(self, source: str, params: Dict[str, Any]) -> None:
        """Log fetch operation."""
        logger.info(f"Fetching data from {source} with params: {params}")
    
    def _handle_error(self, error: Exception, source: str) -> Dict[str, Any]:
        """
        Handle fetch errors consistently.
        
        Args:
            error: The exception that occurred
            source: Name of the data source
            
        Returns:
            Error response dictionary
        """
        logger.error(f"Error fetching from {source}: {str(error)}")
        return {
            "success": False,
            "error": str(error),
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _success_response(self, data: Any, source: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a standardized success response.
        
        Args:
            data: The fetched data
            source: Name of the data source
            metadata: Optional metadata about the fetch
            
        Returns:
            Success response dictionary
        """
        response = {
            "success": True,
            "data": data,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if metadata:
            response["metadata"] = metadata
        
        return response
