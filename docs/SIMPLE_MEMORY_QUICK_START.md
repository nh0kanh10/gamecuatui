# Simple Memory System - Quick Start

## ✅ Đã Hoàn Thành Migration

Hệ thống đã chuyển từ **Advanced RAG (ChromaDB)** sang **Simple Memory (SQLite FTS5)**.

---

## 🚀 Sử Dụng Ngay

### Basic Usage

```python
from engine.memory import get_memory_manager

# Get memory manager (tự động dùng SimpleMemory)
mm = get_memory_manager()

# Remember action
mm.remember_action(
    user_input="I attack the goblin",
    narrative="You swing your sword and hit the goblin for 12 damage.",
    save_id="save_001",
    entity_id=2,
    importance=None  # Auto-calculate
)

# Get context
context = mm.get_relevant_context(
    query="What happened with the goblin?",
    save_id="save_001",
    n_results=5
)
```

### Direct Access

```python
from engine.memory import get_simple_memory, MemoryType

memory = get_simple_memory()

# Add
memory.add(
    content="Player found ancient sword",
    memory_type=MemoryType.EPISODIC.value,
    save_id="save_001",
    importance=0.8
)

# Search
results = memory.search(
    query="ancient sword",
    save_id="save_001",
    n_results=5
)
```

---

## 📊 Performance

- **Search**: < 10ms cho 10K memories
- **Add**: < 5ms per memory
- **RAM**: ~5-10 MB
- **Dependencies**: 0 (chỉ SQLite)

---

## 🎯 Features

- ✅ Full-text search với BM25 ranking
- ✅ Metadata filtering (entity_id, location_id, memory_type)
- ✅ Auto importance scoring
- ✅ Rule-based compression
- ✅ Hierarchical memory types

---

## 📝 Documentation

- `docs/SIMPLE_MEMORY_SYSTEM.md` - Full documentation
- `docs/MEMORY_SYSTEM_MIGRATION.md` - Migration guide
- `engine/memory/simple_memory.py` - Source code

---

**Status**: ✅ Ready to Use

