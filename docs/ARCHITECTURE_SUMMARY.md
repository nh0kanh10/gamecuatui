# Tổng Hợp Kiến Trúc & Quy Tắc Dự Án

## 📋 Mục Lục

1. [Phạm Vi & Phần Cứng](#phạm-vi--phần-cứng)
2. [Nguyên Tắc Kiến Trúc](#nguyên-tắc-kiến-trúc)
3. [Hệ Thống RAG](#hệ-thống-rag)
4. [Quy Tắc Phát Triển](#quy-tắc-phát-triển)
5. [Tài Liệu Tham Khảo](#tài-liệu-tham-khảo)

---

## 🎯 Phạm Vi & Phần Cứng

### Game Solo Player Only

**QUAN TRỌNG**: Game này được thiết kế **CHỈ cho một người chơi duy nhất**.

**Ý nghĩa**:
- ✅ KHÔNG cần multi-user support
- ✅ KHÔNG cần enterprise-grade security
- ✅ KHÔNG cần production monitoring
- ✅ Ưu tiên: Trải nghiệm tốt > Kiến trúc phức tạp

### Cấu Hình Phần Cứng

**Máy chơi game**:
- **OS**: Windows 10 Pro (Build 19045)
- **CPU**: Intel Core i7-10850H @ 2.70GHz (6 Cores, 12 Threads)
- **RAM**: 32.0 GB (Available: ~18-20 GB)
- **Storage**: Local SSD/HDD

**Ràng buộc**:
- LLM Inference: ~18-20 GB RAM
- Game Engine: ~500 MB - 1 GB RAM
- Memory/RAG: < 100 MB RAM
- Buffer: ~2-4 GB RAM

**Xem chi tiết**: `docs/rules/HARDWARE_AND_SCOPE.md`

---

## 🏗️ Nguyên Tắc Kiến Trúc

### 1. Single Database Architecture

**QUY TẮC CỐT LÕI**: Mọi thứ lưu trong SQLite.

```
✅ ĐÚNG:
- Game state → SQLite
- Memory/RAG → SQLite FTS5
- Save files → SQLite
- Metadata → SQLite JSONB

❌ SAI:
- ChromaDB riêng
- PostgreSQL riêng
- Multiple database systems
```

### 2. Minimal Dependencies

- ✅ Sử dụng thư viện có sẵn (SQLite, JSON)
- ✅ Chỉ thêm dependency khi THỰC SỰ cần
- ❌ Tránh "solution looking for a problem"

### 3. Lean Architecture

**Nguyên tắc**:
```
Solo Player = Simple Architecture

Enterprise (2000+ lines):
- Multi-user support
- Audit trails
- Monitoring dashboards
→ 3 tuần development
→ Stressful

Solo Player (500 lines):
- Single user
- Simple logging
- Console.log debugging
→ 1 tuần development
→ Fun!
```

**Xem chi tiết**: `docs/architecture/LEAN_ARCHITECTURE.md`

### 4. Performance Targets

- Memory recall: **< 50ms** (cho 10K-50K memories)
- Game action: **< 100ms** (tổng thời gian)
- LLM inference: **< 5s** (có thể chấp nhận)

---

## 🧠 Hệ Thống Memory

### ✅ Simple Memory System (SQLite FTS5) - ĐANG DÙNG

**Đặc điểm**:
- ✅ Tuân thủ single database architecture
- ✅ Nhẹ: < 10 MB RAM
- ✅ Nhanh: < 10ms cho 50K memories
- ✅ Đơn giản: ~200 lines code
- ✅ Không dependencies mới
- ✅ Rule-based compression (không dùng LLM)

**So với Advanced RAG (ChromaDB) - ĐÃ XÓA**:
- ❌ Advanced RAG: 200-400 MB RAM, phức tạp, phá vỡ kiến trúc
- ✅ Simple Memory: 5-10 MB RAM, đơn giản, tuân thủ kiến trúc

**Xem chi tiết**: 
- `docs/SIMPLE_MEMORY_SYSTEM.md` - Implementation guide
- `engine/memory/simple_memory.py` - Core implementation

### Memory Types (Giữ lại ý tưởng tốt)

```python
EPISODIC    # Sự kiện gần đây, hành động người chơi
SEMANTIC    # Kiến thức thế giới, NPCs, địa điểm
PROCEDURAL  # Quy tắc game, cơ chế
LORE        # Lịch sử thế giới, câu chuyện nền
```

### Scoring (Đơn giản)

```python
score = (
    0.5 * fts_score +      # Full-text search (BM25)
    0.3 * importance +     # User-defined importance
    0.2 * temporal_decay   # Recency (half-life theo type)
)
```

---

## 📝 Quy Tắc Phát Triển

### Core Principles

1. **Solo Player First**: Đơn giản > Phức tạp
2. **Hardware Aware**: Kiểm tra RAM/CPU trước khi thêm feature
3. **Single Database**: Mọi thứ trong SQLite
4. **Minimal Dependencies**: Chỉ thêm khi THỰC SỰ cần
5. **Clean Architecture**: Thiết kế trước, code sau

### File Organization

```
✅ Production code → src/
✅ Game content → data/
✅ Documentation → docs/
✅ Test code → test/
✅ Ideas → ideas/
```

**Xem chi tiết**: `docs/rules/file-organization.md`

### Code Standards

- **Naming**: camelCase (functions), PascalCase (classes), UPPER_SNAKE_CASE (constants)
- **Functions**: Nhỏ, focused, single responsibility
- **Comments**: JSDoc cho public APIs, giải thích logic phức tạp
- **Error Handling**: Proper error handling, không silent failures

**Xem chi tiết**: `docs/DEVELOPMENT_RULES.md`

### Decision Framework

Khi quyết định thêm feature:

1. **Có cần cho solo player không?** → Nếu không → Bỏ qua
2. **Có phù hợp hardware không?** → Nếu vượt quá → Tối ưu hoặc bỏ
3. **Có tuân thủ kiến trúc không?** → Nếu phá vỡ → Tìm cách khác
4. **Có đơn giản hơn không?** → Nếu có → Dùng cách đơn giản
5. **Có làm game vui hơn không?** → Nếu không → Ưu tiên thấp

---

## 📚 Tài Liệu Tham Khảo

### Kiến Trúc

- `docs/architecture/LEAN_ARCHITECTURE.md` - Lean architecture principles
- `docs/architecture/MVP_ARCHITECTURE.md` - MVP approach
- `docs/architecture/ARCHITECTURE.md` - Full architecture (reference)

### Quy Tắc

- `docs/rules/HARDWARE_AND_SCOPE.md` - Hardware constraints & scope
- `docs/rules/file-organization.md` - File organization rules
- `docs/DEVELOPMENT_RULES.md` - Development rules & guidelines

### Hệ Thống

- `docs/SIMPLE_MEMORY_SYSTEM.md` - **Đang dùng**: Simple Memory System (SQLite FTS5)
- `docs/RAG_SYSTEM.md` - Advanced RAG (deprecated, backup only)
- `docs/RAG_ANALYSIS_AND_IMPROVEMENTS.md` - Phân tích và lessons learned

### Game

- `docs/GAME_OVERVIEW.md` - Game overview
- `docs/architecture/AI_INTEGRATION.md` - AI integration guide
- `HOW_TO_PLAY.md` - How to play guide

---

## 🎯 Quick Reference

### Checklist Trước Khi Thêm Feature

- [ ] Feature này có cần cho solo player không?
- [ ] RAM usage < 100 MB?
- [ ] Latency < 100ms?
- [ ] Sử dụng SQLite (không thêm database mới)?
- [ ] Không thêm >3 dependencies mới?
- [ ] Code < 500 lines?
- [ ] Dễ debug và maintain?
- [ ] Làm game vui hơn?

**Nếu tất cả ✅ → Có thể thêm**

### Anti-Patterns (Tránh)

- ❌ Thêm ChromaDB khi SQLite FTS5 đủ dùng
- ❌ Thêm monitoring dashboard cho 1 user
- ❌ Thêm multi-database sync
- ❌ Ignore hardware constraints
- ❌ Break architecture consistency

### Best Practices

- ✅ Sử dụng SQLite FTS5 cho memory search
- ✅ Console.log cho debugging
- ✅ Single database architecture
- ✅ Basic input sanitization
- ✅ Measure before optimize

---

## 📊 So Sánh Approaches

| Approach | RAM | Dependencies | Speed | Complexity | Fit Architecture |
|----------|-----|--------------|-------|------------|------------------|
| **Simple Memory (FTS5)** ✅ | 5-10 MB | 0 | <10ms | Low | ✅ Perfect |
| Advanced RAG (ChromaDB) ❌ | 200-400 MB | 10+ | 50-200ms | High | ❌ Breaks |

**Kết luận**: Simple Memory System là lựa chọn đúng cho solo player game.

---

**Version**: 1.0  
**Last Updated**: 2025-12-02  
**Status**: Active Documentation

