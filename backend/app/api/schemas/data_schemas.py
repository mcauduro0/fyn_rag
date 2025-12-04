"""
Pydantic schemas for Data Fetchers and Document Processors API endpoints.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


# Market Data Schemas
class MarketDataRequest(BaseModel):
    """Request model for market data."""
    
    ticker: str = Field(..., description="Stock ticker symbol", min_length=1, max_length=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL"
            }
        }


class MarketDataResponse(BaseModel):
    """Response model for market data."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    source: str
    timestamp: str


# Document Processing Schemas
class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    
    success: bool
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None


class DocumentProcessResponse(BaseModel):
    """Response model for document processing."""
    
    success: bool
    content: Optional[str] = None
    content_length: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    error: Optional[str] = None


# Economic Data Schemas
class EconomicDataRequest(BaseModel):
    """Request model for economic data."""
    
    indicator: Optional[str] = Field(default=None, description="Economic indicator name")
    country: Optional[str] = Field(default="united states", description="Country name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "indicator": "gdp",
                "country": "united states"
            }
        }


# Sentiment Data Schemas
class SentimentRequest(BaseModel):
    """Request model for sentiment analysis."""
    
    ticker: str = Field(..., description="Stock ticker symbol", min_length=1, max_length=10)
    subreddit: Optional[str] = Field(default="wallstreetbets", description="Subreddit to search")
    limit: Optional[int] = Field(default=100, description="Maximum posts to fetch", ge=1, le=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "subreddit": "wallstreetbets",
                "limit": 100
            }
        }
