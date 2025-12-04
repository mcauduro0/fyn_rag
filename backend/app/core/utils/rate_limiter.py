"""
Rate Limiter - Protects APIs from abuse and manages external API quotas.
Implements token bucket and sliding window algorithms.
"""

import logging
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import deque
import asyncio

logger = logging.getLogger(__name__)


class TokenBucket:
    """
    Token Bucket rate limiter.
    
    Allows bursts while maintaining average rate limit.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if rate limited
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def wait_time(self, tokens: int = 1) -> float:
        """
        Calculate wait time until tokens available.
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Wait time in seconds
        """
        self._refill()
        
        if self.tokens >= tokens:
            return 0.0
        
        tokens_needed = tokens - self.tokens
        wait_seconds = tokens_needed / self.refill_rate
        return wait_seconds


class SlidingWindowCounter:
    """
    Sliding Window Counter rate limiter.
    
    More accurate than fixed window, prevents bursts at window boundaries.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize sliding window counter.
        
        Args:
            max_requests: Maximum requests in window
            window_seconds: Window size in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: deque = deque()
    
    def _cleanup_old_requests(self) -> None:
        """Remove requests outside the current window."""
        cutoff_time = time.time() - self.window_seconds
        
        while self.requests and self.requests[0] < cutoff_time:
            self.requests.popleft()
    
    def is_allowed(self) -> bool:
        """
        Check if request is allowed.
        
        Returns:
            True if allowed, False if rate limited
        """
        self._cleanup_old_requests()
        
        if len(self.requests) < self.max_requests:
            self.requests.append(time.time())
            return True
        return False
    
    def wait_time(self) -> float:
        """
        Calculate wait time until next request allowed.
        
        Returns:
            Wait time in seconds
        """
        self._cleanup_old_requests()
        
        if len(self.requests) < self.max_requests:
            return 0.0
        
        # Wait until oldest request expires
        oldest_request = self.requests[0]
        wait_seconds = (oldest_request + self.window_seconds) - time.time()
        return max(0.0, wait_seconds)


class RateLimiter:
    """
    Rate Limiter with multiple strategies.
    
    Supports:
    - Per-user rate limiting
    - Per-endpoint rate limiting
    - Global rate limiting
    - External API quota management
    """
    
    def __init__(self):
        # User rate limiters (per user)
        self.user_limiters: Dict[str, TokenBucket] = {}
        
        # Endpoint rate limiters (per endpoint)
        self.endpoint_limiters: Dict[str, SlidingWindowCounter] = {}
        
        # External API rate limiters
        self.external_api_limiters: Dict[str, TokenBucket] = {}
        
        self._initialize_external_apis()
        
        logger.info("Initialized RateLimiter")
    
    def _initialize_external_apis(self) -> None:
        """Initialize rate limiters for external APIs."""
        # OpenAI: 3500 requests/min for GPT-4
        self.external_api_limiters["openai"] = TokenBucket(
            capacity=3500,
            refill_rate=3500 / 60  # per second
        )
        
        # Anthropic: 1000 requests/min
        self.external_api_limiters["anthropic"] = TokenBucket(
            capacity=1000,
            refill_rate=1000 / 60
        )
        
        # Polygon.io: 5 requests/second (free tier)
        self.external_api_limiters["polygon"] = TokenBucket(
            capacity=5,
            refill_rate=5
        )
        
        # FMP: 250 requests/day (free tier)
        self.external_api_limiters["fmp"] = TokenBucket(
            capacity=250,
            refill_rate=250 / 86400  # per second
        )
        
        # FRED: 120 requests/minute
        self.external_api_limiters["fred"] = TokenBucket(
            capacity=120,
            refill_rate=120 / 60
        )
        
        # Trading Economics: 1000 requests/day
        self.external_api_limiters["trading_economics"] = TokenBucket(
            capacity=1000,
            refill_rate=1000 / 86400
        )
        
        # Reddit: 60 requests/minute
        self.external_api_limiters["reddit"] = TokenBucket(
            capacity=60,
            refill_rate=60 / 60
        )
    
    def check_user_limit(self, user_id: str, tokens: int = 1) -> bool:
        """
        Check if user is within rate limit.
        
        Args:
            user_id: User identifier
            tokens: Number of tokens to consume
            
        Returns:
            True if allowed, False if rate limited
        """
        if user_id not in self.user_limiters:
            # Default: 100 requests per minute per user
            self.user_limiters[user_id] = TokenBucket(
                capacity=100,
                refill_rate=100 / 60
            )
        
        limiter = self.user_limiters[user_id]
        allowed = limiter.consume(tokens)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for user: {user_id}")
        
        return allowed
    
    def check_endpoint_limit(self, endpoint: str) -> bool:
        """
        Check if endpoint is within rate limit.
        
        Args:
            endpoint: Endpoint identifier
            
        Returns:
            True if allowed, False if rate limited
        """
        if endpoint not in self.endpoint_limiters:
            # Default: 1000 requests per minute per endpoint
            self.endpoint_limiters[endpoint] = SlidingWindowCounter(
                max_requests=1000,
                window_seconds=60
            )
        
        limiter = self.endpoint_limiters[endpoint]
        allowed = limiter.is_allowed()
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for endpoint: {endpoint}")
        
        return allowed
    
    def check_external_api_limit(self, api_name: str, tokens: int = 1) -> bool:
        """
        Check if external API call is within quota.
        
        Args:
            api_name: API identifier (openai, polygon, etc.)
            tokens: Number of tokens to consume
            
        Returns:
            True if allowed, False if rate limited
        """
        if api_name not in self.external_api_limiters:
            logger.warning(f"Unknown external API: {api_name}")
            return True  # Allow by default
        
        limiter = self.external_api_limiters[api_name]
        allowed = limiter.consume(tokens)
        
        if not allowed:
            wait_time = limiter.wait_time(tokens)
            logger.warning(
                f"Rate limit exceeded for {api_name}. "
                f"Wait {wait_time:.1f}s before retry."
            )
        
        return allowed
    
    async def wait_for_external_api(self, api_name: str, tokens: int = 1) -> None:
        """
        Wait until external API quota is available.
        
        Args:
            api_name: API identifier
            tokens: Number of tokens needed
        """
        if api_name not in self.external_api_limiters:
            return
        
        limiter = self.external_api_limiters[api_name]
        
        while not limiter.consume(tokens):
            wait_time = limiter.wait_time(tokens)
            logger.info(f"Waiting {wait_time:.1f}s for {api_name} quota")
            await asyncio.sleep(wait_time)
    
    def get_statistics(self) -> Dict[str, any]:
        """Get rate limiter statistics."""
        return {
            "active_users": len(self.user_limiters),
            "active_endpoints": len(self.endpoint_limiters),
            "external_apis": {
                api_name: {
                    "tokens_available": limiter.tokens,
                    "capacity": limiter.capacity,
                    "refill_rate": limiter.refill_rate
                }
                for api_name, limiter in self.external_api_limiters.items()
            }
        }


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# Decorator for rate limiting
def rate_limit(user_id: Optional[str] = None, endpoint: Optional[str] = None):
    """
    Decorator for rate limiting functions.
    
    Args:
        user_id: User identifier (if None, extracted from function args)
        endpoint: Endpoint identifier
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()
            
            # Check user limit
            if user_id:
                if not limiter.check_user_limit(user_id):
                    raise Exception(f"Rate limit exceeded for user: {user_id}")
            
            # Check endpoint limit
            if endpoint:
                if not limiter.check_endpoint_limit(endpoint):
                    raise Exception(f"Rate limit exceeded for endpoint: {endpoint}")
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test token bucket
    bucket = TokenBucket(capacity=10, refill_rate=1.0)
    
    print("Testing Token Bucket:")
    for i in range(15):
        allowed = bucket.consume()
        print(f"Request {i+1}: {'Allowed' if allowed else 'Denied'}")
        if not allowed:
            wait = bucket.wait_time()
            print(f"  Wait time: {wait:.2f}s")
        time.sleep(0.5)
    
    # Test sliding window
    print("\nTesting Sliding Window:")
    window = SlidingWindowCounter(max_requests=5, window_seconds=2)
    
    for i in range(10):
        allowed = window.is_allowed()
        print(f"Request {i+1}: {'Allowed' if allowed else 'Denied'}")
        if not allowed:
            wait = window.wait_time()
            print(f"  Wait time: {wait:.2f}s")
        time.sleep(0.3)
