# 🚀 Hướng Dẫn Setup RAG System

## 📋 Yêu Cầu Hệ Thống

**Máy của bạn:**
- ✅ Intel Core i7-10850H (6 cores, 12 threads)
- ✅ 32 GB RAM
- ✅ Windows 10 Pro

**Phù hợp hoàn toàn!** Hệ thống RAG sẽ chạy mượt mà trên máy này.

---

## 🔧 Cài Đặt

### Cách 1: Sử dụng Setup Script (Khuyến nghị)

**Windows:**
```bash
setup_rag.bat
```

**Linux/Mac:**
```bash
chmod +x setup_rag.sh
./setup_rag.sh
```

### Cách 2: Cài Đặt Thủ Công

```bash
# Activate virtual environment (nếu có)
venv\Scripts\activate  # Windows
# hoặc
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Hoặc cài từng package
pip install sentence-transformers>=2.2.0
pip install chromadb>=0.4.0
pip install scikit-learn>=1.3.0
pip install numpy>=1.24.0
```

---

## 📦 Dependencies Cần Cài

| Package | Version | Mục Đích | Kích Thước |
|---------|---------|----------|------------|
| `sentence-transformers` | >=2.2.0 | Embedding model | ~200 MB |
| `chromadb` | >=0.4.0 | Vector database | ~50 MB |
| `scikit-learn` | >=1.3.0 | TF-IDF search | ~30 MB |
| `numpy` | >=1.24.0 | Numerical operations | ~20 MB |

**Total**: ~300 MB download, ~500 MB sau khi cài đặt

---

## ⚙️ Cấu Hình

### 1. Embedding Model

Model mặc định: `paraphrase-multilingual-MiniLM-L12-v2`

**Tại sao chọn model này?**
- ✅ Hỗ trợ tiếng Việt
- ✅ Cân bằng tốt giữa tốc độ và chất lượng
- ✅ Kích thước hợp lý (~400 MB)

**Các model khác:**

```python
# Trong engine/memory/advanced_rag.py, thay đổi:
embedding_model = "all-MiniLM-L6-v2"  # Nhỏ nhất, nhanh nhất (English only)
embedding_model = "all-mpnet-base-v2"  # Chất lượng cao nhất (chậm hơn)
```

### 2. Memory Storage

Mặc định: `data/memory/`

Có thể thay đổi:
```python
rag = AdvancedRAG(persist_path="custom/path/memory")
```

### 3. Memory Limits

```python
rag = AdvancedRAG(
    max_memories=10000,        # Max memories trước khi compress
    compression_threshold=5000  # Khi nào bắt đầu compress
)
```

---

## 🧪 Test Setup

Tạo file test: `test_rag.py`

```python
from engine.memory import get_advanced_rag, get_memory_manager, MemoryType

# Test 1: Initialize
print("Testing RAG initialization...")
rag = get_advanced_rag()
print("✅ RAG initialized")

# Test 2: Add memory
print("\nTesting memory addition...")
memory_id = rag.add_memory(
    text="Player discovered the ancient sword",
    memory_type=MemoryType.EPISODIC,
    save_id="test_save",
    importance=0.8
)
print(f"✅ Memory added: {memory_id}")

# Test 3: Search
print("\nTesting search...")
results = rag.search(
    query="ancient sword",
    save_id="test_save",
    n_results=3
)
print(f"✅ Found {len(results)} results")
for r in results:
    print(f"  - {r['text'][:50]}... (score: {r['score']:.2f})")

# Test 4: Memory Manager
print("\nTesting Memory Manager...")
mm = get_memory_manager()
mm.remember_action(
    user_input="I attack the goblin",
    narrative="You hit the goblin for 12 damage",
    save_id="test_save",
    importance=0.7
)
print("✅ Memory Manager working")

print("\n🎉 All tests passed!")
```

Chạy test:
```bash
python test_rag.py
```

---

## 📚 Thêm Lore Files

Tạo lore files trong `data/lore/`:

**Ví dụ: `data/lore/world_background.md`**
```markdown
# World Background

The world was consumed by rising seas in 2087.
Only 5% of landmass remains above water.
Civilization has collapsed into floating settlements.
```

**Ví dụ: `data/lore/npcs.md`**
```markdown
# NPCs

## Marcus Chen
Age: 45
Role: Engineer
Personality: Cautious, loyal, pessimistic
Background: Lost family in the floods
```

Sau đó load lore:
```python
from engine.memory import get_advanced_rag

rag = get_advanced_rag()
rag.load_lore("data/lore")
```

---

## 🐛 Troubleshooting

### Issue: "sentence-transformers not installed"

**Solution:**
```bash
pip install sentence-transformers
```

Nếu vẫn lỗi, thử:
```bash
pip install --upgrade pip
pip install sentence-transformers --no-cache-dir
```

### Issue: Model download fails

**Solution:**
Model sẽ tự động download khi lần đầu sử dụng. Nếu fail:
1. Kiểm tra internet connection
2. Thử download thủ công:
```python
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
```

### Issue: ChromaDB errors

**Solution:**
```bash
pip install --upgrade chromadb
```

Nếu vẫn lỗi, xóa và tạo lại:
```bash
rm -rf data/memory  # Linux/Mac
# hoặc
rmdir /s data\memory  # Windows
```

### Issue: Out of memory

**Solutions:**
1. Giảm `max_memories`:
```python
rag = AdvancedRAG(max_memories=5000)
```

2. Sử dụng model nhỏ hơn:
```python
rag = AdvancedRAG(embedding_model="all-MiniLM-L6-v2")
```

3. Tăng compression threshold:
```python
rag = AdvancedRAG(compression_threshold=3000)
```

### Issue: Slow performance

**Solutions:**
1. Filter search results tốt hơn
2. Giảm `n_results`
3. Sử dụng model nhỏ hơn
4. Tắt hybrid search nếu không cần:
```python
results = rag.search(..., use_hybrid=False)
```

---

## 📊 Performance Benchmarks

**Trên máy của bạn (i7-10850H, 32GB RAM):**

| Operation | Time | Notes |
|-----------|------|-------|
| Initialize RAG | ~5-10s | First time (download model) |
| Add memory | ~20-50ms | Per memory |
| Search (10k memories) | ~100-200ms | Hybrid search |
| Embedding generation | ~10-30ms | Per query |

**Memory Usage:**
- Embedding model: ~200 MB
- ChromaDB: ~100 MB (10k memories)
- Total: ~300-400 MB

---

## ✅ Checklist

- [ ] Cài đặt dependencies (`pip install -r requirements.txt`)
- [ ] Chạy setup script (`setup_rag.bat` hoặc `setup_rag.sh`)
- [ ] Test system (`python test_rag.py`)
- [ ] Tạo lore files (optional)
- [ ] Load lore vào system (optional)
- [ ] Chạy game và test RAG

---

## 🎯 Next Steps

1. **Chạy game**: `python play.py`
2. **Xem documentation**: `docs/RAG_SYSTEM.md`
3. **Customize**: Điều chỉnh parameters theo nhu cầu
4. **Add lore**: Thêm world knowledge vào `data/lore/`

---

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra `docs/RAG_SYSTEM.md` để xem troubleshooting
2. Kiểm tra logs trong console
3. Đảm bảo đã cài đủ dependencies

---

**Version**: 1.0  
**Last Updated**: 2025-12-02

