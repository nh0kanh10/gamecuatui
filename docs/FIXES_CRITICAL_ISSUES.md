# 🔧 Critical Issues Fixes - Cultivation Simulator

> **Mục đích**: Tài liệu về các vấn đề đã được fix và các vấn đề còn lại

---

## ✅ Đã Fix

### 1. LLM Output Validation (HIGH)

**Vấn đề**: Không kiểm soát output LLM → parsing crash, injection, undefined state

**Giải pháp đã implement**:
- ✅ Pydantic schema: `CultivationLLMResponse` với strict validation
- ✅ Fallback parsing: `parse_with_fallback()` với 3 retry attempts
- ✅ Input sanitization: Remove prompt injection patterns
- ✅ Field validation: Min/max length, type checking
- ✅ Safe defaults: Fallback response khi parsing fails

**Files**:
- `engine/ai/cultivation_schemas.py` - Pydantic schemas
- `engine/ai/cultivation_agent.py` - Updated to use schemas
- `engine/games/cultivation_sim/game.py` - Added input sanitization

**Example**:
```python
# Before: json.loads(text) → crash if malformed
# After: CultivationLLMResponse.parse_with_fallback(text) → always returns valid response
```

### 2. Input Sanitization (HIGH)

**Vấn đề**: Prompt injection & poisoning

**Giải pháp đã implement**:
- ✅ `_sanitize_input()` method trong `CultivationSimGame`
- ✅ Remove dangerous patterns: ````, `---`, `system:`, `ignore previous`
- ✅ Length limit: Max 500 characters
- ✅ Remove zero-width characters

### 3. Vietnamese Tokenization (HIGH)

**Vấn đề**: FTS5 Porter tokenizer không phù hợp cho tiếng Việt

**Giải pháp đã implement**:
- ✅ `engine/memory/vietnamese_tokenizer.py`
- ✅ Support underthesea (if installed)
- ✅ Fallback to simple tokenization
- ✅ Unicode normalization

**Note**: Cần update `SimpleMemory.add()` để sử dụng Vietnamese tokenizer

---

## ⚠️ Cần Fix (HIGH Priority)

### 1. SQLite Concurrency (HIGH)

**Vấn đề**: Per-save SQLite + in-memory instances không scale, dễ corrupt

**Giải pháp đề xuất**:
```python
# Option 1: Per-request DB connections
def get_db_connection(save_id: str):
    return sqlite3.connect(f"data/saves/{save_id}.db", check_same_thread=False)

# Option 2: Redis for session state + SQLite for persistence
# - Redis: Fast ephemeral state
# - SQLite: Periodic durable snapshots
# - Redis locks for concurrency
```

**Status**: ⏳ Chưa implement

### 2. Rate Limiting & Auth (HIGH)

**Vấn đề**: No auth/rate-limiting → dễ bị abuse & cost overrun

**Giải pháp đề xuất**:
```python
# FastAPI middleware
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/game/action")
@limiter.limit("10/minute")  # 10 requests per minute
async def process_action(...):
    ...
```

**Status**: ⏳ Chưa implement

### 3. Memory Growth Control (HIGH)

**Vấn đề**: Unbounded FTS table → DB bloat, search slowdown

**Giải pháp đề xuất**:
```python
# Retention policy
MAX_MEMORIES_PER_SAVE = 1000

# Compression: Merge similar memories
def compress_memories(save_id: str):
    # Keep only important memories (importance > 0.6)
    # Merge similar memories
    # Delete old low-importance memories
```

**Status**: ⏳ Chưa implement (có compression.py nhưng chưa tích hợp)

### 4. LLM Cost Control (HIGH)

**Vấn đề**: Gemini calls có thể tốn chi phí không kiểm soát

**Giải pháp đề xuất**:
```python
# Token budget per user
MAX_TOKENS_PER_USER = 100000  # per month

# Cache LLM responses
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_llm_call(prompt_hash: str):
    ...

# Circuit breaker
if total_tokens_this_month > MAX_TOKENS_PER_USER:
    raise HTTPException(429, "Token limit exceeded")
```

**Status**: ⏳ Chưa implement

### 5. Content Moderation (HIGH)

**Vấn đề**: User-generated narratives có thể chứa toxic/NSFW content

**Giải pháp đề xuất**:
```python
# Moderation check before saving
def moderate_content(text: str) -> bool:
    # Use moderation API or classifier
    # Return True if safe, False if unsafe
    pass

# In cultivation_agent.py
if not moderate_content(data['narrative']):
    data['narrative'] = "Nội dung không phù hợp đã được lọc."
```

**Status**: ⏳ Chưa implement

---

## 📋 Cần Fix (MEDIUM Priority)

### 1. Logging & Audit

**Vấn đề**: Không có log cho LLM calls

**Giải pháp**:
```python
import logging

logger = logging.getLogger("cultivation_sim")

def log_llm_call(prompt: str, response: str, tokens: int):
    logger.info(f"LLM Call: {tokens} tokens, prompt_hash={hash(prompt)}")
```

**Status**: ⏳ Chưa implement

### 2. Model Versioning

**Vấn đề**: Không track model version cho reproducibility

**Giải pháp**:
```python
# Store in memory metadata
metadata = {
    "model_version": "gemini-2.0-flash",
    "prompt_version": "1.0",
    "timestamp": datetime.now().isoformat()
}
```

**Status**: ⏳ Chưa implement

### 3. Deterministic Replay

**Vấn đề**: Không thể replay để debug

**Giải pháp**:
```python
# Store all inputs and outputs
replay_log = {
    "turn": 1,
    "input": "...",
    "output": "...",
    "state_before": {...},
    "state_after": {...}
}
```

**Status**: ⏳ Chưa implement

---

## 🎯 Architecture Simplification (Nếu cần)

### Current Architecture

```
FastAPI + React + ECS + SQLite + Memory + Gemini
```

### Simplified MVP (Nếu over-engineered)

```
Flask + Terminal/Simple HTML + Dict + SQLite + Gemini
```

**Decision**: Giữ current architecture vì:
- ✅ Đã implement xong
- ✅ Có thể scale sau
- ✅ Frontend React tốt cho UX

**Nhưng cần**:
- ⚠️ Simplify ECS nếu không cần thiết
- ⚠️ Consider CLI mode cho testing

---

## 📊 Performance Improvements

### Current Issues

1. **AI Latency**: 5-15s per turn (thực tế)
2. **Memory Search**: <10ms (OK)
3. **DB Operations**: <5ms (OK)

### Solutions

1. **Caching**:
   ```python
   # Cache similar prompts
   @lru_cache(maxsize=100)
   def cached_llm_call(prompt_hash: str):
       ...
   ```

2. **Streaming**:
   ```python
   # Stream response để improve perceived latency
   response = model.generate_content_stream(prompt)
   ```

3. **Batch Processing**:
   ```python
   # Batch multiple turns (future)
   ```

**Status**: ⏳ Chưa implement

---

## 🔐 Security Checklist

- ✅ Input sanitization
- ✅ Output validation (Pydantic)
- ⏳ Rate limiting (chưa)
- ⏳ Auth (chưa)
- ⏳ Secrets management (chưa - vẫn dùng .env)
- ⏳ Content moderation (chưa)
- ⏳ Audit logging (chưa)

---

## 📝 Next Steps

### Immediate (This Week)

1. ✅ Fix LLM output validation (DONE)
2. ✅ Add input sanitization (DONE)
3. ✅ Add Vietnamese tokenizer (DONE - cần integrate)
4. ⏳ Add rate limiting
5. ⏳ Add memory growth control

### Short Term (Next Week)

1. ⏳ SQLite concurrency fix
2. ⏳ LLM cost control
3. ⏳ Content moderation
4. ⏳ Logging & audit

### Long Term (Future)

1. ⏳ Model versioning
2. ⏳ Deterministic replay
3. ⏳ Performance optimization (caching, streaming)
4. ⏳ Architecture simplification (nếu cần)

---

**Version**: 1.0  
**Last Updated**: 2025-12-03  
**Status**: In Progress

