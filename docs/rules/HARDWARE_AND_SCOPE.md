# Quy Tắc Phần Cứng & Phạm Vi Dự Án

## 🎯 Phạm Vi Dự Án

### Game Solo Player Only

**QUAN TRỌNG**: Game này được thiết kế **CHỈ cho một người chơi duy nhất** (bạn).

**Ý nghĩa**:
- ✅ KHÔNG cần multi-user support
- ✅ KHÔNG cần enterprise-grade security
- ✅ KHÔNG cần production monitoring
- ✅ KHÔNG cần scalability cho hàng nghìn users
- ✅ Ưu tiên: Trải nghiệm tốt cho 1 người > Kiến trúc phức tạp

**Nguyên tắc**:
```
Simple > Complex
Working > Perfect
Fun > Enterprise-grade
```

---

## 💻 Cấu Hình Phần Cứng Mục Tiêu

### Thông Số Hệ Thống

**Máy chơi game**:
- **OS**: Microsoft Windows 10 Pro (Build 19045)
- **CPU**: Intel Core i7-10850H @ 2.70GHz
  - 6 Cores, 12 Logical Processors
- **RAM**: 32.0 GB (31.9 GB Total, ~18-20 GB Available)
- **Storage**: Local SSD/HDD
- **GPU**: Integrated (không có VRAM riêng hoặc 4GB VRAM nếu có GPU rời)

### Ràng Buộc Phần Cứng

**Phân bổ tài nguyên**:
- **LLM Inference**: ~18-20 GB RAM (cho model lớn)
- **Game Engine**: ~500 MB - 1 GB RAM
- **OS + Background**: ~4 GB RAM
- **Buffer**: ~2-4 GB RAM (để tránh swap)

**Tổng cộng**: ~25-28 GB / 32 GB → **Còn lại ~4-7 GB buffer**

**Quy tắc**:
1. ✅ **KHÔNG** thêm dependencies nặng (>500 MB RAM)
2. ✅ **KHÔNG** sử dụng vector database phức tạp (ChromaDB, Pinecone)
3. ✅ **Ưu tiên** SQLite cho TẤT CẢ (game state + memory)
4. ✅ **Tối ưu** cho single-threaded hoặc 2-4 threads
5. ✅ **Tránh** GPU acceleration không kiểm soát được

### Memory System: SQLite FTS5 Only

**Quy tắc cốt lõi**:
- ✅ Memory system dùng SQLite FTS5 (cùng database với game state)
- ✅ Single-database architecture (không có exception)
- ✅ Zero dependencies mới
- ✅ Performance: < 10ms cho 10K memories
- ✅ RAM: < 10 MB

**Lý do**:
- Tuân thủ kiến trúc single-database
- Performance đủ tốt cho text adventure
- Đơn giản, dễ maintain
- Keyword search đủ dùng (không cần semantic search)

**Nếu thực sự cần semantic search** (future):
- Optional embedding module (lazy-loaded, hardware-aware)
- Chỉ enable khi RAM > 500 MB trống
- Fallback về FTS5 nếu không đủ resources

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
- MongoDB riêng
- Multiple database systems
```

**Lý do**:
- Đơn giản: 1 database = dễ backup, dễ restore
- Nhẹ: SQLite ~5-10 MB
- Đủ mạnh: FTS5 hỗ trợ full-text search tốt
- Không cần setup: Có sẵn trong Python

### 2. Minimal Dependencies

**Quy tắc**:
- ✅ Sử dụng thư viện có sẵn (SQLite, JSON)
- ✅ Chỉ thêm dependency khi THỰC SỰ cần
- ❌ Tránh "solution looking for a problem"

**Ví dụ**:
```python
# ✅ ĐÚNG: SQLite FTS5 cho memory search
CREATE VIRTUAL TABLE memory_fts USING fts5(...);

# ❌ SAI: ChromaDB cho memory search
from chromadb import Client  # Thêm 10+ dependencies
```

### 3. Performance Targets

**Latency requirements**:
- Memory recall: **< 50ms** (cho 10K-50K memories)
- Game action processing: **< 100ms** (tổng thời gian)
- LLM inference: **< 5s** (có thể chấp nhận)

**Memory usage**:
- Game engine: **< 1 GB**
- Memory/RAG system: **< 100 MB**
- Total overhead: **< 2 GB**

### 4. Solo Player = Simple Architecture

**Nguyên tắc**:
```
Enterprise Architecture:
- Multi-user support
- Audit trails
- Security compliance
- Monitoring dashboards
→ 2000+ lines code
→ 3 tuần development
→ Stressful

Solo Player Architecture:
- Single user
- Simple logging
- Basic security
- Console.log debugging
→ 500 lines code
→ 1 tuần development
→ Fun!
```

---

## 🚫 Anti-Patterns (Tránh)

### 1. Over-Engineering

**❌ SAI**:
- Thêm ChromaDB khi SQLite FTS5 đủ dùng
- Thêm monitoring dashboard cho 1 user
- Thêm multi-database sync
- Thêm enterprise security cho solo game

**✅ ĐÚNG**:
- Sử dụng SQLite FTS5
- Console.log cho debugging
- Single database
- Basic input sanitization

### 2. Ignoring Hardware Constraints

**❌ SAI**:
- Thêm 400 MB embedding model khi không cần
- Sử dụng GPU acceleration không kiểm soát
- Thêm dependencies nặng (>500 MB RAM)
- Bỏ qua RAM limits

**✅ ĐÚNG**:
- Kiểm tra RAM usage trước khi thêm feature
- Sử dụng model nhẹ hoặc không dùng embedding
- Monitor memory usage
- Tối ưu cho hardware có sẵn

### 3. Breaking Architecture Consistency

**❌ SAI**:
- Thêm database mới (ChromaDB) khi đã có SQLite
- Tạo system mới thay vì extend system cũ
- Phá vỡ "single database" principle

**✅ ĐÚNG**:
- Extend SQLite với FTS5
- Sử dụng existing ECS components
- Tuân thủ "single database" principle

---

## ✅ Best Practices

### 1. Hardware-Aware Development

```python
# Kiểm tra RAM trước khi load model
import psutil

def can_load_model(model_size_mb):
    available = psutil.virtual_memory().available / (1024**2)
    return available > model_size_mb * 2  # 2x buffer
```

### 2. Progressive Enhancement

```python
# Bắt đầu đơn giản, nâng cấp khi cần
# Phase 1: SQLite FTS5 (đủ dùng)
# Phase 2: Thêm embedding nếu THỰC SỰ cần
# Phase 3: Optimize nếu performance không đủ
```

### 3. Measure Before Optimize

```python
# Benchmark trước khi optimize
import time

def benchmark_search():
    start = time.time()
    results = search_memory(query)
    elapsed = time.time() - start
    print(f"Search took {elapsed*1000:.2f}ms")
    return elapsed < 0.05  # Target: <50ms
```

---

## 📊 Resource Allocation Guide

### RAM Budget (32 GB Total)

| Component | Allocation | Notes |
|-----------|------------|-------|
| OS + Background | 4 GB | Windows + apps |
| LLM Model | 18-20 GB | Large language model |
| Game Engine | 500 MB - 1 GB | ECS + game logic |
| Memory/RAG | 50-100 MB | SQLite + FTS5 |
| Buffer | 2-4 GB | Safety margin |
| **Total Used** | ~25-28 GB | |
| **Available** | ~4-7 GB | For future features |

### CPU Budget (6 Cores, 12 Threads)

| Task | Threads | Priority |
|------|---------|----------|
| LLM Inference | 8-10 | High |
| Game Engine | 1-2 | Medium |
| Memory Search | 1 | Low |
| Background | 1 | Low |

---

## 🎯 Decision Framework

Khi quyết định thêm feature mới, hỏi:

1. **Có cần cho solo player không?**
   - Nếu không → Bỏ qua

2. **Có phù hợp với hardware không?**
   - Nếu vượt quá RAM/CPU → Tối ưu hoặc bỏ

3. **Có tuân thủ kiến trúc không?**
   - Nếu phá vỡ "single database" → Tìm cách khác

4. **Có đơn giản hơn không?**
   - Nếu có cách đơn giản hơn → Dùng cách đơn giản

5. **Có làm game vui hơn không?**
   - Nếu không → Ưu tiên thấp

---

## 📝 Checklist Trước Khi Thêm Feature

- [ ] Feature này có cần cho solo player không?
- [ ] RAM usage < 100 MB?
- [ ] Latency < 100ms?
- [ ] Sử dụng SQLite (không thêm database mới)?
- [ ] Không thêm >3 dependencies mới?
- [ ] Code < 500 lines?
- [ ] Dễ debug và maintain?
- [ ] Làm game vui hơn?

**Nếu tất cả ✅ → Có thể thêm**

**Nếu có ❌ → Cần đánh giá lại**

---

**Version**: 1.0  
**Last Updated**: 2025-12-02  
**Status**: Active Rule

