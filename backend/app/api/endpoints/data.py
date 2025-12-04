"""
Data Fetchers and Document Processors API Endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from pathlib import Path
import shutil

from app.api.schemas.data_schemas import (
    MarketDataRequest,
    MarketDataResponse,
    DocumentProcessResponse,
    DocumentUploadResponse,
    EconomicDataRequest,
    SentimentRequest
)
from app.core.config import settings
from app.data.fetchers.polygon_fetcher import PolygonFetcher
from app.data.fetchers.fmp_fetcher import FMPFetcher
from app.data.fetchers.fred_fetcher import FREDFetcher
from app.data.fetchers.trading_economics_fetcher import TradingEconomicsFetcher
from app.data.fetchers.reddit_fetcher import RedditFetcher
from app.data.processors.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["Data Sources"])

# Upload directory
UPLOAD_DIR = Path("/app/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Market Data Endpoints
@router.post("/market/polygon", response_model=MarketDataResponse)
async def get_polygon_data(request: MarketDataRequest):
    """Fetch market data from Polygon.io."""
    try:
        if not settings.POLYGON_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Polygon API key not configured"
            )
        
        fetcher = PolygonFetcher(settings.POLYGON_API_KEY)
        result = fetcher.fetch_market_snapshot(request.ticker)
        
        return MarketDataResponse(**result)
        
    except Exception as e:
        logger.error(f"Error fetching Polygon data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/market/fmp", response_model=MarketDataResponse)
async def get_fmp_data(request: MarketDataRequest):
    """Fetch fundamental data from Financial Modeling Prep."""
    try:
        if not settings.FMP_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="FMP API key not configured"
            )
        
        fetcher = FMPFetcher(settings.FMP_API_KEY)
        result = fetcher.fetch_comprehensive_data(request.ticker)
        
        return MarketDataResponse(**result)
        
    except Exception as e:
        logger.error(f"Error fetching FMP data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Economic Data Endpoints
@router.post("/economic/fred")
async def get_fred_data(request: EconomicDataRequest):
    """Fetch economic data from FRED."""
    try:
        if not settings.FRED_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="FRED API key not configured"
            )
        
        fetcher = FREDFetcher(settings.FRED_API_KEY)
        
        if request.indicator:
            result = fetcher.fetch_indicator(request.indicator)
        else:
            result = fetcher.fetch_economic_snapshot()
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching FRED data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/economic/trading-economics")
async def get_trading_economics_data(request: EconomicDataRequest):
    """Fetch economic data from Trading Economics."""
    try:
        if not settings.TRADING_ECONOMICS_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Trading Economics API key not configured"
            )
        
        fetcher = TradingEconomicsFetcher(settings.TRADING_ECONOMICS_API_KEY)
        result = fetcher.fetch_indicators(request.country)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching Trading Economics data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Sentiment Analysis Endpoints
@router.post("/sentiment/reddit")
async def get_reddit_sentiment(request: SentimentRequest):
    """Fetch sentiment data from Reddit."""
    try:
        if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Reddit API credentials not configured"
            )
        
        fetcher = RedditFetcher(
            settings.REDDIT_CLIENT_ID,
            settings.REDDIT_CLIENT_SECRET,
            settings.REDDIT_USER_AGENT
        )
        
        result = fetcher.fetch_sentiment_snapshot(request.ticker)
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching Reddit sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Document Processing Endpoints
@router.post("/document/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for processing.
    
    Supported formats: PDF, DOCX, XLSX
    """
    try:
        # Validate file type
        processor = DocumentProcessor()
        if not processor.is_supported(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Supported: {processor.get_supported_formats()}"
            )
        
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return DocumentUploadResponse(
            success=True,
            file_path=str(file_path),
            file_name=file.filename,
            file_size=file_path.stat().st_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/document/process", response_model=DocumentProcessResponse)
async def process_document(file: UploadFile = File(...)):
    """
    Upload and process a document.
    
    Extracts text content from PDF, DOCX, or XLSX files.
    """
    try:
        # Upload file first
        upload_result = await upload_document(file)
        
        if not upload_result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to upload file"
            )
        
        # Process the uploaded file
        processor = DocumentProcessor()
        result = processor.process(upload_result.file_path)
        
        return DocumentProcessResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
