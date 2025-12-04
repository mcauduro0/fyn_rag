"""
Tests for utility modules: caching, rate limiting, and monitoring.
"""

import pytest
import time
import asyncio
from datetime import datetime, timedelta

from app.core.utils.caching import (
    InMemoryCache,
    CacheManager,
    get_cache_manager,
    cached,
    cached_async,
    generate_cache_key
)
from app.core.utils.rate_limiter import (
    TokenBucket,
    SlidingWindowCounter,
    RateLimiter,
    get_rate_limiter
)
from app.core.utils.monitoring import (
    MetricsCollector,
    PerformanceMonitor,
    get_performance_monitor,
    track_performance
)


class TestInMemoryCache:
    """Tests for InMemoryCache."""
    
    @pytest.fixture
    def cache(self):
        """Create cache instance."""
        return InMemoryCache(max_size=10, default_ttl=5)
    
    def test_cache_initialization(self, cache):
        """Test cache is properly initialized."""
        assert cache.max_size == 10
        assert cache.default_ttl == 5
        assert len(cache.cache) == 0
    
    def test_set_and_get(self, cache):
        """Test setting and getting values."""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_get_nonexistent_key(self, cache):
        """Test getting nonexistent key returns None."""
        assert cache.get("nonexistent") is None
    
    def test_ttl_expiration(self, cache):
        """Test TTL expiration."""
        cache.set("key1", "value1", ttl=1)
        assert cache.get("key1") == "value1"
        
        time.sleep(1.5)
        assert cache.get("key1") is None
    
    def test_lru_eviction(self, cache):
        """Test LRU eviction when capacity reached."""
        # Fill cache to capacity
        for i in range(10):
            cache.set(f"key{i}", f"value{i}")
        
        # Access key0 to make it recently used
        cache.get("key0")
        
        # Add new key, should evict least recently used (key1)
        cache.set("key10", "value10")
        
        assert cache.get("key0") is not None  # Recently accessed
        assert cache.get("key1") is None  # Should be evicted
        assert cache.get("key10") is not None  # New key
    
    def test_delete(self, cache):
        """Test deleting keys."""
        cache.set("key1", "value1")
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.delete("key1") is False  # Already deleted
    
    def test_clear(self, cache):
        """Test clearing cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert len(cache.cache) == 0
        assert cache.get("key1") is None
    
    def test_statistics(self, cache):
        """Test cache statistics."""
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.get_statistics()
        
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1
        assert stats["hit_rate"] == 0.5
    
    def test_cleanup_expired(self, cache):
        """Test cleanup of expired entries."""
        cache.set("key1", "value1", ttl=1)
        cache.set("key2", "value2", ttl=10)
        
        time.sleep(1.5)
        
        removed = cache.cleanup_expired()
        
        assert removed == 1
        assert cache.get("key1") is None
        assert cache.get("key2") is not None


class TestCacheManager:
    """Tests for CacheManager."""
    
    @pytest.fixture
    def manager(self):
        """Create cache manager instance."""
        return CacheManager()
    
    def test_manager_initialization(self, manager):
        """Test manager is properly initialized."""
        assert manager.embedding_cache is not None
        assert manager.api_cache is not None
        assert manager.analysis_cache is not None
        assert manager.rag_cache is not None
    
    def test_get_cache(self, manager):
        """Test getting cache by type."""
        embedding = manager.get_cache("embedding")
        api = manager.get_cache("api")
        
        assert embedding == manager.embedding_cache
        assert api == manager.api_cache
    
    def test_cleanup_all(self, manager):
        """Test cleanup of all caches."""
        # Add expired entries
        manager.api_cache.set("key1", "value1", ttl=1)
        time.sleep(1.5)
        
        results = manager.cleanup_all()
        
        assert isinstance(results, dict)
        assert "api" in results
    
    def test_get_all_statistics(self, manager):
        """Test getting statistics for all caches."""
        stats = manager.get_all_statistics()
        
        assert "embedding" in stats
        assert "api" in stats
        assert "analysis" in stats
        assert "rag" in stats


def test_generate_cache_key():
    """Test cache key generation."""
    key1 = generate_cache_key("arg1", "arg2", param1="value1")
    key2 = generate_cache_key("arg1", "arg2", param1="value1")
    key3 = generate_cache_key("arg1", "arg2", param1="value2")
    
    assert key1 == key2  # Same args should produce same key
    assert key1 != key3  # Different args should produce different key


def test_cached_decorator():
    """Test cached decorator."""
    call_count = 0
    
    @cached(cache_type="api", ttl=10)
    def expensive_function(x, y):
        nonlocal call_count
        call_count += 1
        return x + y
    
    # First call - should execute function
    result1 = expensive_function(1, 2)
    assert result1 == 3
    assert call_count == 1
    
    # Second call with same args - should use cache
    result2 = expensive_function(1, 2)
    assert result2 == 3
    assert call_count == 1  # Not incremented
    
    # Call with different args - should execute function
    result3 = expensive_function(2, 3)
    assert result3 == 5
    assert call_count == 2


@pytest.mark.asyncio
async def test_cached_async_decorator():
    """Test cached_async decorator."""
    call_count = 0
    
    @cached_async(cache_type="api", ttl=10)
    async def async_expensive_function(x, y):
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.1)
        return x + y
    
    # First call
    result1 = await async_expensive_function(1, 2)
    assert result1 == 3
    assert call_count == 1
    
    # Second call - cached
    result2 = await async_expensive_function(1, 2)
    assert result2 == 3
    assert call_count == 1


class TestTokenBucket:
    """Tests for TokenBucket rate limiter."""
    
    def test_token_bucket_initialization(self):
        """Test token bucket initialization."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        assert bucket.capacity == 10
        assert bucket.refill_rate == 1.0
        assert bucket.tokens == 10
    
    def test_consume_tokens(self):
        """Test consuming tokens."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        assert bucket.consume(5) is True
        assert bucket.tokens == 5
        
        assert bucket.consume(5) is True
        assert bucket.tokens == 0
        
        assert bucket.consume(1) is False  # No tokens left
    
    def test_token_refill(self):
        """Test token refill over time."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens/second
        
        bucket.consume(10)  # Empty bucket
        assert bucket.tokens == 0
        
        time.sleep(0.5)  # Wait for refill
        bucket._refill()
        
        assert bucket.tokens >= 4  # Should have refilled ~5 tokens
    
    def test_wait_time_calculation(self):
        """Test wait time calculation."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)
        
        bucket.consume(10)  # Empty bucket
        
        wait_time = bucket.wait_time(5)
        assert wait_time >= 4.5  # Need to wait for 5 tokens at 1/sec


class TestSlidingWindowCounter:
    """Tests for SlidingWindowCounter rate limiter."""
    
    def test_sliding_window_initialization(self):
        """Test sliding window initialization."""
        window = SlidingWindowCounter(max_requests=5, window_seconds=1)
        
        assert window.max_requests == 5
        assert window.window_seconds == 1
    
    def test_allow_requests_within_limit(self):
        """Test allowing requests within limit."""
        window = SlidingWindowCounter(max_requests=5, window_seconds=1)
        
        for i in range(5):
            assert window.is_allowed() is True
        
        assert window.is_allowed() is False  # Exceeded limit
    
    def test_window_sliding(self):
        """Test window slides over time."""
        window = SlidingWindowCounter(max_requests=3, window_seconds=1)
        
        # Fill window
        for i in range(3):
            assert window.is_allowed() is True
        
        assert window.is_allowed() is False
        
        # Wait for window to slide
        time.sleep(1.1)
        
        assert window.is_allowed() is True  # Window has slid


class TestRateLimiter:
    """Tests for RateLimiter."""
    
    @pytest.fixture
    def limiter(self):
        """Create rate limiter instance."""
        return RateLimiter()
    
    def test_limiter_initialization(self, limiter):
        """Test rate limiter initialization."""
        assert len(limiter.external_api_limiters) > 0
        assert "openai" in limiter.external_api_limiters
        assert "anthropic" in limiter.external_api_limiters
    
    def test_check_user_limit(self, limiter):
        """Test user rate limiting."""
        user_id = "test_user"
        
        # Should allow initial requests
        assert limiter.check_user_limit(user_id) is True
        
        # Exhaust limit
        for i in range(100):
            limiter.check_user_limit(user_id)
        
        # Should be rate limited
        assert limiter.check_user_limit(user_id) is False
    
    def test_check_endpoint_limit(self, limiter):
        """Test endpoint rate limiting."""
        endpoint = "/api/analyze"
        
        assert limiter.check_endpoint_limit(endpoint) is True
    
    def test_check_external_api_limit(self, limiter):
        """Test external API rate limiting."""
        assert limiter.check_external_api_limit("openai") is True
        assert limiter.check_external_api_limit("anthropic") is True
    
    @pytest.mark.asyncio
    async def test_wait_for_external_api(self, limiter):
        """Test waiting for external API quota."""
        # This should complete without error
        await limiter.wait_for_external_api("openai", tokens=1)
    
    def test_get_statistics(self, limiter):
        """Test getting rate limiter statistics."""
        stats = limiter.get_statistics()
        
        assert "active_users" in stats
        assert "active_endpoints" in stats
        assert "external_apis" in stats


class TestMetricsCollector:
    """Tests for MetricsCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create metrics collector instance."""
        return MetricsCollector(retention_hours=1)
    
    def test_collector_initialization(self, collector):
        """Test collector initialization."""
        assert collector.retention_hours == 1
        assert len(collector.counters) == 0
    
    def test_increment_counter(self, collector):
        """Test incrementing counter."""
        collector.increment_counter("requests", 1.0)
        collector.increment_counter("requests", 2.0)
        
        assert collector.get_counter("requests") == 3.0
    
    def test_set_gauge(self, collector):
        """Test setting gauge."""
        collector.set_gauge("cpu_usage", 45.5)
        
        assert collector.get_gauge("cpu_usage") == 45.5
    
    def test_record_histogram(self, collector):
        """Test recording histogram values."""
        collector.record_histogram("latency", 0.5)
        collector.record_histogram("latency", 1.0)
        collector.record_histogram("latency", 1.5)
        
        stats = collector.get_histogram_stats("latency")
        
        assert stats["count"] == 3
        assert stats["min"] == 0.5
        assert stats["max"] == 1.5
    
    def test_record_timer(self, collector):
        """Test recording timer durations."""
        collector.record_timer("api_call", 0.1)
        collector.record_timer("api_call", 0.2)
        
        stats = collector.get_timer_stats("api_call")
        
        assert stats["count"] == 2
        assert stats["mean"] == 0.15


class TestPerformanceMonitor:
    """Tests for PerformanceMonitor."""
    
    @pytest.fixture
    def monitor(self):
        """Create performance monitor instance."""
        return PerformanceMonitor()
    
    def test_monitor_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.metrics is not None
        assert monitor.start_time is not None
    
    def test_track_api_request(self, monitor):
        """Test tracking API requests."""
        monitor.track_api_request("/api/analyze", "POST", 200, 0.5)
        
        assert monitor.metrics.get_counter("api.requests") > 0
    
    def test_track_agent_execution(self, monitor):
        """Test tracking agent execution."""
        monitor.track_agent_execution("value_agent", 2.5, True)
        
        assert monitor.metrics.get_counter("agent.executions") > 0
    
    def test_track_cache_access(self, monitor):
        """Test tracking cache access."""
        monitor.track_cache_access("rag", True)
        monitor.track_cache_access("rag", False)
        
        assert monitor.metrics.get_counter("cache.accesses") == 2
        assert monitor.metrics.get_counter("cache.hits") == 1
        assert monitor.metrics.get_counter("cache.misses") == 1
    
    def test_get_health_status(self, monitor):
        """Test getting health status."""
        health = monitor.get_health_status()
        
        assert "status" in health
        assert "uptime_seconds" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_get_performance_report(self, monitor):
        """Test getting performance report."""
        report = monitor.get_performance_report()
        
        assert "health" in report
        assert "api_metrics" in report
        assert "agent_metrics" in report
        assert "cache_metrics" in report


@pytest.mark.asyncio
async def test_track_performance_decorator():
    """Test track_performance decorator."""
    monitor = get_performance_monitor()
    
    @track_performance("test_function")
    async def test_func(x):
        await asyncio.sleep(0.1)
        return x * 2
    
    result = await test_func(5)
    
    assert result == 10
    assert monitor.metrics.get_counter("test_function.calls") > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
