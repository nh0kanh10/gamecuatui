"""
Rate Limiting for FastAPI using slowapi
"""

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    HAS_SLOWAPI = True
except ImportError:
    HAS_SLOWAPI = False
    print("⚠️  slowapi not installed. Install with: pip install slowapi")
    print("   Rate limiting will be disabled")

from fastapi import Request
from typing import Callable, Optional

# Global limiter instance
_limiter: Optional[Limiter] = None


def setup_rate_limiter(app):
    """Setup rate limiter middleware for FastAPI app"""
    global _limiter
    
    if not HAS_SLOWAPI:
        return None
    
    _limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = _limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    return _limiter


def get_rate_limiter() -> Optional[Limiter]:
    """Get rate limiter instance"""
    return _limiter


def rate_limit_key_func(request: Request) -> str:
    """Custom key function for per-API-key rate limiting"""
    # Try to get API key from request state (set by require_api_key)
    api_key = getattr(request.state, 'api_key', None)
    if api_key:
        return f"api_key:{api_key}"
    # Fallback to IP
    return get_remote_address(request)


def create_rate_limit_decorator(limit: str, key_func: Optional[Callable] = None):
    """
    Create rate limit decorator
    Usage: @create_rate_limit_decorator("20/minute")
    """
    if not HAS_SLOWAPI or not _limiter:
        # No-op decorator if slowapi not available
        def noop_decorator(func):
            return func
        return noop_decorator
    
    if key_func is None:
        key_func = get_remote_address
    
    return _limiter.limit(limit, key_func=key_func)

