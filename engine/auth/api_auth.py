"""
API Key Authentication for FastAPI
"""

import os
from fastapi import Request, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from typing import Optional

API_KEY_HEADER = "X-API-Key"

# In production, store API keys in keyvault/DB
# For now, load from env (comma-separated)
VALID_API_KEYS = set(
    os.getenv("VALID_API_KEYS", "devkey1,devkey2").split(",")
)

api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


async def get_api_key_from_request(
    api_key: Optional[str] = Depends(api_key_header)
) -> Optional[str]:
    """Extract API key from request header"""
    return api_key


async def require_api_key(
    api_key: Optional[str] = Depends(get_api_key_from_request)
) -> str:
    """
    Dependency to require valid API key
    Raises 401 if invalid or missing
    """
    if not api_key or api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Provide X-API-Key header."
        )
    return api_key


def add_api_key_to_valid_keys(api_key: str):
    """Add API key to valid keys (for dynamic key management)"""
    VALID_API_KEYS.add(api_key)


def remove_api_key(api_key: str):
    """Remove API key from valid keys"""
    VALID_API_KEYS.discard(api_key)

