"""
Redis-backed Session State Management
All ephemeral game state in Redis, periodic snapshots to SQLite
Supports multi-worker uvicorn safely
"""

import asyncio
import json
import time
from typing import Any, Dict, Optional
import sqlite3
from pathlib import Path
import os

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    print("⚠️  Redis not installed. Install with: pip install redis>=4.6.0")

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SNAPSHOT_DIR = Path("data/snapshots")
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Global Redis client (lazy init)
_redis_client: Optional[aioredis.Redis] = None


def get_redis_client() -> Optional[aioredis.Redis]:
    """Get or create Redis client"""
    global _redis_client
    if not HAS_REDIS:
        return None
    if _redis_client is None:
        try:
            _redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
        except Exception as e:
            print(f"⚠️  Failed to connect to Redis: {e}")
            print("   Falling back to in-memory state (single-worker only)")
            return None
    return _redis_client


# Redis key patterns
def state_key(save_id: str) -> str:
    return f"game:state:{save_id}"


def lock_key(save_id: str) -> str:
    return f"lock:game:{save_id}"


async def acquire_lock(save_id: str, ttl: int = 10) -> bool:
    """
    Acquire Redis lock (cooperative locking)
    Returns True if lock acquired, False if already locked
    """
    redis = get_redis_client()
    if not redis:
        # No Redis - assume single worker, always succeed
        return True
    
    k = lock_key(save_id)
    # SET NX PX - set if not exists, with expiration
    return await redis.set(name=k, value="1", nx=True, ex=ttl)


async def release_lock(save_id: str):
    """Release Redis lock"""
    redis = get_redis_client()
    if not redis:
        return
    
    await redis.delete(lock_key(save_id))


async def save_state(save_id: str, state: Dict[str, Any], expire: int = 3600 * 24):
    """
    Save ephemeral state to Redis
    expire: TTL in seconds (default 24 hours)
    """
    redis = get_redis_client()
    if not redis:
        # No Redis - state is only in-memory (single worker)
        return
    
    await redis.set(state_key(save_id), json.dumps(state, ensure_ascii=False), ex=expire)


async def load_state(save_id: str) -> Dict[str, Any]:
    """Load state from Redis"""
    redis = get_redis_client()
    if not redis:
        return {}
    
    raw = await redis.get(state_key(save_id))
    return json.loads(raw) if raw else {}


def snapshot_to_sqlite_blocking(save_id: str, state: Dict[str, Any]):
    """
    Blocking function - call inside asyncio.to_thread
    Stores snapshot to data/saves/{save_id}.db in table snapshots
    """
    db_path = Path(f"data/saves/{save_id}.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at INTEGER NOT NULL,
            state_json TEXT NOT NULL
        )""")
        
        # Use transaction
        cur = conn.cursor()
        cur.execute("BEGIN IMMEDIATE")
        cur.execute(
            "INSERT INTO snapshots (created_at, state_json) VALUES (?, ?)",
            (int(time.time()), json.dumps(state, ensure_ascii=False))
        )
        conn.commit()
    finally:
        conn.close()


async def snapshot_save(save_id: str):
    """Async helper to snapshot current Redis state to SQLite"""
    st = await load_state(save_id)
    if st:
        await asyncio.to_thread(snapshot_to_sqlite_blocking, save_id, st)


async def periodic_snapshot_worker(interval_seconds: int = 60):
    """
    Background worker that snapshots Redis states to SQLite periodically
    In production, use a set of active save_ids instead of KEYS scan
    """
    redis = get_redis_client()
    if not redis:
        return  # No Redis, nothing to snapshot
    
    while True:
        try:
            # Scan for all game state keys
            keys = await redis.keys("game:state:*")
            for k in keys:
                save_id = k.split(":", 2)[2]
                state = await redis.get(k)
                if state:
                    await asyncio.to_thread(
                        snapshot_to_sqlite_blocking,
                        save_id,
                        json.loads(state)
                    )
        except Exception as e:
            print(f"⚠️  Snapshot worker error: {e}")
        
        await asyncio.sleep(interval_seconds)


async def cleanup_expired_states():
    """Clean up expired Redis states (optional maintenance)"""
    redis = get_redis_client()
    if not redis:
        return
    
    # Redis will auto-expire based on TTL, but we can also manually clean
    # This is optional - Redis handles expiration automatically

