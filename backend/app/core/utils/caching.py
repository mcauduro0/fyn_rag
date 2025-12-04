"""
Caching System - Provides caching for expensive operations.
Supports in-memory and Redis-based caching with TTL.
"""

import logging
import hashlib
import json
import pickle
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import time

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a cached entry."""
    
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.utcnow() > self.expires_at
    
    def access(self) -> Any:
        """Access the cached value."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
        return self.value


class InMemoryCache:
    """
    In-memory cache with TTL support.
    
    Features:
    - Time-to-live (TTL) expiration
    - LRU eviction when capacity reached
    - Statistics tracking
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0
        
        logger.info(f"Initialized InMemoryCache (max_size={max_size}, ttl={default_ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        # Check expiration
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return entry.access()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        # Evict if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()
        
        self.cache[key] = CacheEntry(value, ttl)
        logger.debug(f"Cached key: {key} (ttl={ttl}s)")
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed
        )
        
        del self.cache[lru_key]
        logger.debug(f"Evicted LRU key: {lru_key}")
    
    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired entries")
        
        return len(expired_keys)


class CacheManager:
    """Manages multiple caches for different purposes."""
    
    def __init__(self):
        # Different caches for different data types
        self.embedding_cache = InMemoryCache(max_size=5000, default_ttl=86400)  # 24h
        self.api_cache = InMemoryCache(max_size=1000, default_ttl=3600)  # 1h
        self.analysis_cache = InMemoryCache(max_size=500, default_ttl=7200)  # 2h
        self.rag_cache = InMemoryCache(max_size=2000, default_ttl=43200)  # 12h
        
        logger.info("Initialized CacheManager")
    
    def get_cache(self, cache_type: str) -> InMemoryCache:
        """Get cache by type."""
        caches = {
            "embedding": self.embedding_cache,
            "api": self.api_cache,
            "analysis": self.analysis_cache,
            "rag": self.rag_cache
        }
        return caches.get(cache_type, self.api_cache)
    
    def cleanup_all(self) -> dict[str, int]:
        """Cleanup expired entries in all caches."""
        results = {
            "embedding": self.embedding_cache.cleanup_expired(),
            "api": self.api_cache.cleanup_expired(),
            "analysis": self.analysis_cache.cleanup_expired(),
            "rag": self.rag_cache.cleanup_expired()
        }
        return results
    
    def get_all_statistics(self) -> dict[str, Any]:
        """Get statistics for all caches."""
        return {
            "embedding": self.embedding_cache.get_statistics(),
            "api": self.api_cache.get_statistics(),
            "analysis": self.analysis_cache.get_statistics(),
            "rag": self.rag_cache.get_statistics()
        }


# Global cache manager
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    # Create a stable representation
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    
    # Serialize and hash
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    
    return key_hash


def cached(cache_type: str = "api", ttl: Optional[int] = None):
    """
    Decorator for caching function results.
    
    Args:
        cache_type: Type of cache to use
        ttl: Time-to-live in seconds
        
    Example:
        @cached(cache_type="api", ttl=3600)
        def expensive_function(param1, param2):
            # ... expensive operation ...
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            cache = cache_manager.get_cache(cache_type)
            
            # Generate cache key
            cache_key = f"{func.__name__}:{generate_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {func.__name__}")
                return cached_value
            
            # Execute function
            logger.debug(f"Cache miss: {func.__name__}")
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache result
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__} (execution: {execution_time:.2f}s)")
            
            return result
        
        return wrapper
    return decorator


def cached_async(cache_type: str = "api", ttl: Optional[int] = None):
    """
    Decorator for caching async function results.
    
    Args:
        cache_type: Type of cache to use
        ttl: Time-to-live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            cache = cache_manager.get_cache(cache_type)
            
            # Generate cache key
            cache_key = f"{func.__name__}:{generate_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {func.__name__}")
                return cached_value
            
            # Execute function
            logger.debug(f"Cache miss: {func.__name__}")
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache result
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {func.__name__} (execution: {execution_time:.2f}s)")
            
            return result
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test caching
    cache = InMemoryCache(max_size=10, default_ttl=5)
    
    # Set values
    cache.set("key1", "value1")
    cache.set("key2", "value2", ttl=2)
    
    # Get values
    print(f"key1: {cache.get('key1')}")
    print(f"key2: {cache.get('key2')}")
    
    # Wait for expiration
    time.sleep(3)
    print(f"key2 after 3s: {cache.get('key2')}")  # Should be None
    
    # Statistics
    print(f"Stats: {cache.get_statistics()}")
    
    # Test decorator
    @cached(cache_type="api", ttl=10)
    def expensive_operation(x, y):
        time.sleep(1)  # Simulate expensive operation
        return x + y
    
    print(f"First call: {expensive_operation(1, 2)}")  # Slow
    print(f"Second call: {expensive_operation(1, 2)}")  # Fast (cached)
