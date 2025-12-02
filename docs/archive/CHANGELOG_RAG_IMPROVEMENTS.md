# Changelog: RAG System Improvements

## Version 2.0 - 2025-12-02

### ✅ Đã Sửa (Theo 2 Bài Đánh Giá)

#### 1. Embedding Version Tracking
- ✅ Thêm `TextNormalizer` class để normalize text
- ✅ Track `embedding_model_name` và `embedding_model_hash`
- ✅ Lưu `text_hash` và `normalized_text` snippet
- ✅ Detect embedding drift khi model đổi

#### 2. Compression Implementation
- ✅ Two-tier compression: Lossless (facts) + Lossy (summary)
- ✅ Preserve important entities, items, flags
- ✅ Cluster-based summarization
- ✅ Store `cluster_members` để recover
- ✅ Không nén memories có importance >= 0.8

#### 3. Configurable Weights
- ✅ `search_weights` parameter trong `__init__`
- ✅ Default: `{"semantic": 0.4, "keyword": 0.2, "temporal": 0.2, "importance": 0.2}`
- ✅ Có thể customize khi khởi tạo

#### 4. Temporal Decay Fix
- ✅ Half-life theo memory type:
  - `episodic`: 7 ngày
  - `semantic`: 90 ngày
  - `procedural`: 365 ngày
  - `lore`: 99999 (không decay)
- ✅ Function: `_temporal_score(timestamp_str, memory_type)`

#### 5. Auto Importance Scoring
- ✅ `auto_importance()` method với heuristics
- ✅ MemoryManager tự động dùng nếu `importance=None`
- ✅ Scoring dựa trên: quest_critical, NPC interaction, combat, etc.

#### 6. Database Compaction
- ✅ `compact_database()` method
- ✅ Remove duplicates bằng `text_hash`
- ✅ Có thể gọi định kỳ

#### 7. Architecture Rule Update
- ✅ Exception cho ChromaDB trong `HARDWARE_AND_SCOPE.md`
- ✅ Điều kiện: Chỉ cho RAG, < 500MB RAM, có fallback
- ✅ Game state vẫn SQLite

---

## Breaking Changes

### None
- Tất cả changes đều backward compatible
- Default behavior không đổi
- Chỉ thêm features mới

---

## Migration Guide

### Không cần migration
- Code cũ vẫn hoạt động
- New features là optional

### Nếu muốn dùng features mới:

```python
# 1. Custom weights
rag = AdvancedRAG(
    search_weights={"semantic": 0.5, ...}
)

# 2. Auto importance
memory_manager.remember_action(..., importance=None)

# 3. Compaction
rag.compact_database()
```

---

## Performance Impact

- **RAM**: Không đổi (~200-400 MB)
- **Speed**: Không đổi (~50-200ms)
- **Storage**: Compression giảm storage usage

---

## Known Issues

- ChromaDB không hỗ trợ update metadata dễ dàng
- Compression summary đơn giản (có thể nâng cấp với LLM)

---

**Status**: ✅ Production Ready

