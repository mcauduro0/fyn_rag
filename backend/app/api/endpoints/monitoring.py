"""
Monitoring API endpoints - Health checks, metrics, and system status.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.api.schemas.agent_schemas import (
    HealthCheckResponse,
    PerformanceMetrics,
    CacheStatistics,
    RateLimitInfo
)
from app.core.utils.monitoring import get_performance_monitor
from app.core.utils.caching import get_cache_manager
from app.core.utils.rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.
    
    Returns system health status including:
    - Overall status (healthy/degraded/unhealthy)
    - Uptime
    - Error rate
    - Average latency
    - Total requests processed
    """
    try:
        monitor = get_performance_monitor()
        health_status = monitor.get_health_status()
        
        return HealthCheckResponse(**health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/metrics", response_model=PerformanceMetrics)
async def get_metrics() -> PerformanceMetrics:
    """
    Get comprehensive performance metrics.
    
    Returns:
    - Health status
    - API metrics (requests, errors, latency)
    - Agent metrics (executions, duration)
    - Cache metrics (hits, misses, hit rate)
    - RAG metrics (queries, latency)
    - System metrics (CPU, memory)
    """
    try:
        monitor = get_performance_monitor()
        
        # Update system metrics before returning
        monitor.update_system_metrics()
        
        performance_report = monitor.get_performance_report()
        
        return PerformanceMetrics(**performance_report)
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.get("/cache/stats", response_model=CacheStatistics)
async def get_cache_statistics() -> CacheStatistics:
    """
    Get cache statistics.
    
    Returns statistics for all cache types:
    - Embedding cache
    - API cache
    - Analysis cache
    - RAG cache
    
    Each includes:
    - Size and capacity
    - Hits and misses
    - Hit rate
    - Total requests
    """
    try:
        cache_manager = get_cache_manager()
        stats = cache_manager.get_all_statistics()
        
        return CacheStatistics(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve cache statistics")


@router.post("/cache/clear")
async def clear_cache(cache_type: str = "all") -> Dict[str, str]:
    """
    Clear cache.
    
    Args:
        cache_type: Type of cache to clear (embedding, api, analysis, rag, all)
        
    Returns:
        Success message
    """
    try:
        cache_manager = get_cache_manager()
        
        if cache_type == "all":
            cache_manager.embedding_cache.clear()
            cache_manager.api_cache.clear()
            cache_manager.analysis_cache.clear()
            cache_manager.rag_cache.clear()
            message = "All caches cleared"
        else:
            cache = cache_manager.get_cache(cache_type)
            cache.clear()
            message = f"{cache_type} cache cleared"
        
        logger.info(message)
        return {"message": message}
        
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@router.post("/cache/cleanup")
async def cleanup_cache() -> Dict[str, Any]:
    """
    Cleanup expired cache entries.
    
    Returns:
        Number of entries removed per cache type
    """
    try:
        cache_manager = get_cache_manager()
        results = cache_manager.cleanup_all()
        
        total_removed = sum(results.values())
        logger.info(f"Cleaned up {total_removed} expired cache entries")
        
        return {
            "total_removed": total_removed,
            "by_cache": results
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup cache: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to cleanup cache")


@router.get("/rate-limits", response_model=RateLimitInfo)
async def get_rate_limit_info() -> RateLimitInfo:
    """
    Get rate limiter information.
    
    Returns:
    - Active users count
    - Active endpoints count
    - External API quota information
    """
    try:
        rate_limiter = get_rate_limiter()
        stats = rate_limiter.get_statistics()
        
        return RateLimitInfo(**stats)
        
    except Exception as e:
        logger.error(f"Failed to get rate limit info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve rate limit information")


@router.get("/system/status")
async def get_system_status() -> Dict[str, Any]:
    """
    Get comprehensive system status.
    
    Combines health, metrics, cache stats, and rate limits into one response.
    """
    try:
        monitor = get_performance_monitor()
        cache_manager = get_cache_manager()
        rate_limiter = get_rate_limiter()
        
        # Update system metrics
        monitor.update_system_metrics()
        
        return {
            "health": monitor.get_health_status(),
            "performance": monitor.get_performance_report(),
            "cache": cache_manager.get_all_statistics(),
            "rate_limits": rate_limiter.get_statistics(),
            "timestamp": monitor.start_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve system status")
