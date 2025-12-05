"""
Main FastAPI application entry point for Fyn RAG Investment Committee System.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.api.endpoints import rag, data, analysis, monitoring, advanced_analysis

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Fyn RAG Investment Committee",
    description="AI-powered Investment Analysis System with Multi-Agent Architecture",
    version="2.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rag.router, prefix="/api/v1")
app.include_router(data.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")
app.include_router(advanced_analysis.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "online",
        "service": "Fyn RAG Investment Committee",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "rag_system": "initialized"  # TODO: Add actual RAG check
    }


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    logger.info("Starting Fyn RAG Investment Committee System...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize RAG System
    try:
        from app.core.rag.rag_system import get_rag_system
        rag = get_rag_system()
        logger.info("RAG system instance created (will initialize on first use)")
    except Exception as e:
        logger.error(f"Failed to create RAG system: {e}")
    
    logger.info("Startup complete!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down Fyn RAG Investment Committee System...")
    # TODO: Close database connections
    # TODO: Save any pending data
    logger.info("Shutdown complete!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
