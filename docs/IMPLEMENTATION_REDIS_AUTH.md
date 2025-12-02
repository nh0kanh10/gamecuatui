# 🔧 Implementation: Redis State + Auth + Rate Limiting

> **Mục đích**: Tài liệu về implementation Redis-backed state, authentication, rate limiting, và các fixes khác

---

## ✅ Đã Implement

### 1. Redis-Backed Session State

**Files**:
- `engine/state/redis_state.py` - Redis state management
- `engine/state/__init__.py` - Exports

**Features**:
- ✅ Ephemeral state in Redis (24h TTL)
- ✅ Redis locks for concurrency (multi-worker safe)
- ✅ Periodic snapshots to SQLite (every 60s)
- ✅ Graceful fallback if Redis unavailable (single-worker mode)

**Usage**:
```python
from engine.state import save_state, load_state, acquire_lock, release_lock

# Save state
await save_state(save_id, game_state_dict)

# Load state
state = await load_state(save_id)

# Acquire lock
if await acquire_lock(save_id):
    try:
        # Update state
        ...
    finally:
        await release_lock(save_id)
```

### 2. FastAPI Authentication

**Files**:
- `engine/auth/api_auth.py` - API key authentication
- `engine/auth/rate_limiter.py` - Rate limiting

**Features**:
- ✅ API key authentication via `X-API-Key` header
- ✅ Configurable valid keys (env: `VALID_API_KEYS`)
- ✅ Dependency injection: `Depends(require_api_key)`

**Usage**:
```python
@app.post("/game/action")
async def process_action(
    api_key: str = Depends(require_api_key)
):
    # API key validated
    ...
```

### 3. Rate Limiting

**Features**:
- ✅ Per-IP rate limiting (20/minute default)
- ✅ Per-API-key rate limiting (60/minute default)
- ✅ Configurable limits via decorators

**Usage**:
```python
from engine.auth.rate_limiter import create_rate_limit_decorator

@app.post("/game/action")
@create_rate_limit_decorator("20/minute")
@create_rate_limit_decorator("60/minute", key_func=rate_limit_key_func)
async def process_action(...):
    ...
```

### 4. LLM Cost Control

**Files**:
- `engine/llm/cost_control.py` - Token budget management

**Features**:
- ✅ Monthly token budget per API key (100K tokens/month)
- ✅ Per-request limit (10K tokens)
- ✅ Token tracking in Redis
- ✅ Auto-expiration at month end

**Usage**:
```python
from engine.llm.cost_control import check_and_charge_tokens

allowed, remaining = await check_and_charge_tokens(api_key, tokens_estimate)
if not allowed:
    raise HTTPException(429, f"Token limit exceeded. Remaining: {remaining}")
```

### 5. Content Moderation

**Files**:
- `engine/moderator/moderation.py` - Content moderation

**Features**:
- ✅ Keyword-based blacklist (Vietnamese + English)
- ✅ Prompt injection detection
- ✅ Input and output moderation
- ✅ Sanitization functions

**Usage**:
```python
from engine.moderator import moderate_content, is_safe_content

is_safe, reason = moderate_content(text)
if not is_safe:
    # Block or sanitize
    ...
```

### 6. Memory Compaction

**Files**:
- `engine/memory/compaction_worker.py` - Memory compaction

**Features**:
- ✅ Keep max 1000 memories per save
- ✅ Remove low-importance memories
- ✅ Ordered by importance + last_accessed

**Usage**:
```python
from engine.memory.compaction_worker import compaction_worker_for_save

deleted = compaction_worker_for_save(save_id)
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file

# Redis (optional - falls back to in-memory if not set)
REDIS_URL=redis://localhost:6379/0

# API Keys (comma-separated)
VALID_API_KEYS=devkey1,devkey2,production_key_xyz

# Token limits (optional - defaults in code)
MAX_TOKENS_PER_USER_PER_MONTH=100000
MAX_TOKENS_PER_REQUEST=10000
```

### Dependencies

```bash
pip install redis>=4.6.0
pip install slowapi>=0.1.9
pip install cryptography>=41.0.0
```

---

## 📊 API Changes

### New Endpoints

1. **GET /billing/usage**
   - Get token usage for API key
   - Requires: `X-API-Key` header
   - Returns: `{used, limit, remaining, month}`

2. **POST /game/save**
   - Explicitly save game to SQLite
   - Requires: `X-API-Key` header
   - Rate limit: 10/minute

### Updated Endpoints

All endpoints now require `X-API-Key` header:
- `POST /game/new` - Rate limit: 5/minute
- `POST /game/action` - Rate limit: 20/minute (IP), 60/minute (key)
- `GET /game/modes` - Requires auth

---

## 🚀 Deployment

### Single Worker (No Redis)

Works out of the box - state is in-memory only.

### Multi-Worker (With Redis)

1. **Install Redis**:
   ```bash
   # Windows: Download from https://redis.io/download
   # Linux: sudo apt install redis-server
   # Mac: brew install redis
   ```

2. **Start Redis**:
   ```bash
   redis-server
   ```

3. **Set Environment**:
   ```bash
   REDIS_URL=redis://localhost:6379/0
   ```

4. **Run Multiple Workers**:
   ```bash
   uvicorn server:app --workers 4 --host 0.0.0.0 --port 8000
   ```

### Background Workers

The snapshot worker starts automatically on FastAPI startup:
- Snapshots Redis states to SQLite every 60 seconds
- Runs in background asyncio task

---

## 🔐 Security Checklist

- ✅ API key authentication
- ✅ Rate limiting (per-IP and per-key)
- ✅ Input sanitization
- ✅ Output moderation
- ✅ Token budget control
- ✅ Redis locks for concurrency
- ⏳ Secrets management (still using .env - can improve)
- ⏳ HTTPS enforcement (production)
- ⏳ CORS configuration (currently open - restrict in production)

---

## 📝 Next Steps

### Immediate

1. ✅ Redis state management (DONE)
2. ✅ Auth + rate limiting (DONE)
3. ✅ Cost control (DONE)
4. ✅ Moderation (DONE)
5. ⏳ Integrate memory compaction into save flow

### Short Term

1. ⏳ Add Redis connection pooling
2. ⏳ Add monitoring/metrics
3. ⏳ Add admin endpoints for key management
4. ⏳ Improve moderation (LLM-based)

### Long Term

1. ⏳ Move to key vault for API keys
2. ⏳ Add user management system
3. ⏳ Add billing/subscription system
4. ⏳ Add analytics dashboard

---

**Version**: 1.0  
**Last Updated**: 2025-12-03  
**Status**: Implemented

