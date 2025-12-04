"""
Performance Monitoring - Tracks system performance and health metrics.
Provides metrics collection, alerting, and performance profiling.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps
import psutil
import asyncio

logger = logging.getLogger(__name__)


class MetricPoint:
    """Represents a single metric data point."""
    
    def __init__(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.value = value
        self.tags = tags or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat()
        }


class MetricsCollector:
    """
    Collects and aggregates metrics.
    
    Metric types:
    - Counter: Monotonically increasing value
    - Gauge: Point-in-time value
    - Histogram: Distribution of values
    - Timer: Duration measurements
    """
    
    def __init__(self, retention_hours: int = 24):
        """
        Initialize metrics collector.
        
        Args:
            retention_hours: How long to retain metrics
        """
        self.retention_hours = retention_hours
        self.retention_seconds = retention_hours * 3600
        
        # Storage for different metric types
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.timers: Dict[str, List[float]] = defaultdict(list)
        
        # Time series data
        self.time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        logger.info(f"Initialized MetricsCollector (retention={retention_hours}h)")
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        key = self._make_key(name, tags)
        self.counters[key] += value
        self._record_time_series(name, self.counters[key], tags)
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric."""
        key = self._make_key(name, tags)
        self.gauges[key] = value
        self._record_time_series(name, value, tags)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a value in histogram."""
        key = self._make_key(name, tags)
        self.histograms[key].append(value)
        self._record_time_series(name, value, tags)
    
    def record_timer(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a timer duration."""
        key = self._make_key(name, tags)
        self.timers[key].append(duration)
        self._record_time_series(name, duration, tags)
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a unique key from name and tags."""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def _record_time_series(self, name: str, value: float, tags: Optional[Dict[str, str]]) -> None:
        """Record metric in time series."""
        key = self._make_key(name, tags)
        point = MetricPoint(name, value, tags)
        self.time_series[key].append(point)
    
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get counter value."""
        key = self._make_key(name, tags)
        return self.counters.get(key, 0.0)
    
    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get gauge value."""
        key = self._make_key(name, tags)
        return self.gauges.get(key)
    
    def get_histogram_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics."""
        key = self._make_key(name, tags)
        values = list(self.histograms.get(key, []))
        
        if not values:
            return {}
        
        values_sorted = sorted(values)
        count = len(values)
        
        return {
            "count": count,
            "min": values_sorted[0],
            "max": values_sorted[-1],
            "mean": sum(values) / count,
            "median": values_sorted[count // 2],
            "p95": values_sorted[int(count * 0.95)] if count > 0 else 0,
            "p99": values_sorted[int(count * 0.99)] if count > 0 else 0
        }
    
    def get_timer_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get timer statistics."""
        key = self._make_key(name, tags)
        durations = self.timers.get(key, [])
        
        if not durations:
            return {}
        
        durations_sorted = sorted(durations)
        count = len(durations)
        
        return {
            "count": count,
            "min": durations_sorted[0],
            "max": durations_sorted[-1],
            "mean": sum(durations) / count,
            "median": durations_sorted[count // 2],
            "p95": durations_sorted[int(count * 0.95)] if count > 0 else 0,
            "p99": durations_sorted[int(count * 0.99)] if count > 0 else 0
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                name: self.get_histogram_stats(name.split("[")[0])
                for name in self.histograms.keys()
            },
            "timers": {
                name: self.get_timer_stats(name.split("[")[0])
                for name in self.timers.keys()
            }
        }
    
    def cleanup_old_data(self) -> int:
        """Remove data older than retention period."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.retention_seconds)
        removed = 0
        
        for key in list(self.time_series.keys()):
            series = self.time_series[key]
            original_len = len(series)
            
            # Remove old points
            while series and series[0].timestamp < cutoff_time:
                series.popleft()
            
            removed += original_len - len(series)
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} old metric points")
        
        return removed


class PerformanceMonitor:
    """
    Performance Monitor tracks system health and performance.
    
    Monitors:
    - API endpoint latency
    - Agent execution time
    - Cache hit rates
    - External API calls
    - System resources (CPU, memory)
    - Error rates
    """
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.start_time = datetime.utcnow()
        
        logger.info("Initialized PerformanceMonitor")
    
    def track_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration: float
    ) -> None:
        """Track API request metrics."""
        tags = {
            "endpoint": endpoint,
            "method": method,
            "status": str(status_code)
        }
        
        self.metrics.increment_counter("api.requests", tags=tags)
        self.metrics.record_timer("api.latency", duration, tags=tags)
        
        if status_code >= 400:
            self.metrics.increment_counter("api.errors", tags=tags)
    
    def track_agent_execution(
        self,
        agent_name: str,
        duration: float,
        success: bool
    ) -> None:
        """Track agent execution metrics."""
        tags = {
            "agent": agent_name,
            "status": "success" if success else "failure"
        }
        
        self.metrics.increment_counter("agent.executions", tags=tags)
        self.metrics.record_timer("agent.duration", duration, tags=tags)
    
    def track_cache_access(self, cache_type: str, hit: bool) -> None:
        """Track cache access metrics."""
        tags = {"cache_type": cache_type}
        
        self.metrics.increment_counter("cache.accesses", tags=tags)
        
        if hit:
            self.metrics.increment_counter("cache.hits", tags=tags)
        else:
            self.metrics.increment_counter("cache.misses", tags=tags)
    
    def track_external_api_call(
        self,
        api_name: str,
        duration: float,
        success: bool
    ) -> None:
        """Track external API call metrics."""
        tags = {
            "api": api_name,
            "status": "success" if success else "failure"
        }
        
        self.metrics.increment_counter("external_api.calls", tags=tags)
        self.metrics.record_timer("external_api.latency", duration, tags=tags)
    
    def track_rag_query(self, duration: float, num_results: int) -> None:
        """Track RAG query metrics."""
        self.metrics.increment_counter("rag.queries")
        self.metrics.record_timer("rag.latency", duration)
        self.metrics.record_histogram("rag.results_count", num_results)
    
    def update_system_metrics(self) -> None:
        """Update system resource metrics."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics.set_gauge("system.cpu_percent", cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.metrics.set_gauge("system.memory_percent", memory.percent)
        self.metrics.set_gauge("system.memory_available_mb", memory.available / 1024 / 1024)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.metrics.set_gauge("system.disk_percent", disk.percent)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        # Calculate uptime
        uptime = datetime.utcnow() - self.start_time
        
        # Get error rate
        total_requests = self.metrics.get_counter("api.requests")
        total_errors = self.metrics.get_counter("api.errors")
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        # Get average latency
        latency_stats = self.metrics.get_timer_stats("api.latency")
        avg_latency = latency_stats.get("mean", 0) if latency_stats else 0
        
        # Determine health status
        if error_rate > 10 or avg_latency > 5.0:
            status = "unhealthy"
        elif error_rate > 5 or avg_latency > 2.0:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "uptime_seconds": uptime.total_seconds(),
            "error_rate_percent": error_rate,
            "avg_latency_seconds": avg_latency,
            "total_requests": total_requests
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            "health": self.get_health_status(),
            "api_metrics": {
                "total_requests": self.metrics.get_counter("api.requests"),
                "total_errors": self.metrics.get_counter("api.errors"),
                "latency": self.metrics.get_timer_stats("api.latency")
            },
            "agent_metrics": {
                "total_executions": self.metrics.get_counter("agent.executions"),
                "duration": self.metrics.get_timer_stats("agent.duration")
            },
            "cache_metrics": {
                "total_accesses": self.metrics.get_counter("cache.accesses"),
                "total_hits": self.metrics.get_counter("cache.hits"),
                "total_misses": self.metrics.get_counter("cache.misses")
            },
            "rag_metrics": {
                "total_queries": self.metrics.get_counter("rag.queries"),
                "latency": self.metrics.get_timer_stats("rag.latency")
            },
            "system_metrics": {
                "cpu_percent": self.metrics.get_gauge("system.cpu_percent"),
                "memory_percent": self.metrics.get_gauge("system.memory_percent")
            }
        }


# Global monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def track_performance(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """
    Decorator to track function performance.
    
    Args:
        metric_name: Name of the metric
        tags: Optional tags
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start_time = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                monitor.metrics.record_timer(metric_name, duration, tags)
                monitor.metrics.increment_counter(
                    f"{metric_name}.calls",
                    tags={**(tags or {}), "status": "success" if success else "failure"}
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                monitor.metrics.record_timer(metric_name, duration, tags)
                monitor.metrics.increment_counter(
                    f"{metric_name}.calls",
                    tags={**(tags or {}), "status": "success" if success else "failure"}
                )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


if __name__ == "__main__":
    # Test monitoring
    monitor = PerformanceMonitor()
    
    # Track some metrics
    monitor.track_api_request("/api/analyze", "POST", 200, 0.5)
    monitor.track_api_request("/api/analyze", "POST", 200, 0.6)
    monitor.track_api_request("/api/analyze", "POST", 500, 1.2)
    
    monitor.track_agent_execution("value_agent", 2.5, True)
    monitor.track_agent_execution("growth_agent", 2.1, True)
    
    monitor.track_cache_access("rag", True)
    monitor.track_cache_access("rag", False)
    
    # Get reports
    print("Health Status:")
    print(monitor.get_health_status())
    
    print("\nPerformance Report:")
    print(monitor.get_performance_report())
