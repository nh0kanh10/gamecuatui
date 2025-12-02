"""
LLM Cost Control - Token Budget Management
"""

import asyncio
from datetime import datetime
from typing import Optional
from engine.state.redis_state import get_redis_client

# Token limits
MAX_TOKENS_PER_USER_PER_MONTH = 100000  # 100K tokens per month per API key
MAX_TOKENS_PER_REQUEST = 10000  # Max tokens per single request


def get_current_month() -> str:
    """Get current month string (YYYY-MM)"""
    return datetime.now().strftime("%Y-%m")


def billing_key(api_key: str) -> str:
    """Redis key for billing tracking"""
    month = get_current_month()
    return f"billing:tokens:{api_key}:{month}"


async def check_and_charge_tokens(
    api_key: str,
    tokens_estimate: int,
    actual_tokens: Optional[int] = None
) -> tuple[bool, int]:
    """
    Check if user has enough token budget and charge if available
    Returns: (allowed, remaining_tokens)
    """
    redis = get_redis_client()
    if not redis:
        # No Redis - allow all (single user, no tracking)
        return True, MAX_TOKENS_PER_USER_PER_MONTH
    
    # Use actual tokens if provided, otherwise estimate
    tokens_to_charge = actual_tokens if actual_tokens else tokens_estimate
    
    # Check per-request limit
    if tokens_to_charge > MAX_TOKENS_PER_REQUEST:
        return False, 0
    
    key = billing_key(api_key)
    
    # Get current usage
    current = await redis.get(key)
    current_tokens = int(current) if current else 0
    
    # Check monthly limit
    if current_tokens + tokens_to_charge > MAX_TOKENS_PER_USER_PER_MONTH:
        remaining = MAX_TOKENS_PER_USER_PER_MONTH - current_tokens
        return False, remaining
    
    # Charge tokens
    new_total = await redis.incrby(key, tokens_to_charge)
    
    # Set expiration to end of month (30 days)
    await redis.expire(key, 30 * 24 * 3600)
    
    remaining = MAX_TOKENS_PER_USER_PER_MONTH - new_total
    return True, remaining


async def get_token_usage(api_key: str) -> dict:
    """Get current token usage for API key"""
    redis = get_redis_client()
    if not redis:
        return {"used": 0, "limit": MAX_TOKENS_PER_USER_PER_MONTH, "remaining": MAX_TOKENS_PER_USER_PER_MONTH}
    
    key = billing_key(api_key)
    current = await redis.get(key)
    used = int(current) if current else 0
    
    return {
        "used": used,
        "limit": MAX_TOKENS_PER_USER_PER_MONTH,
        "remaining": MAX_TOKENS_PER_USER_PER_MONTH - used,
        "month": get_current_month()
    }


def estimate_tokens(text: str) -> int:
    """
    Rough token estimation (4 chars ≈ 1 token for English/Vietnamese)
    More accurate: use tiktoken or count actual tokens from API response
    """
    return len(text) // 4


async def reset_token_budget(api_key: str):
    """Reset token budget for API key (admin function)"""
    redis = get_redis_client()
    if not redis:
        return
    
    key = billing_key(api_key)
    await redis.delete(key)

