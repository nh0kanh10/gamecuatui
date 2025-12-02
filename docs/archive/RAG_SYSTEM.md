# 🧠 Advanced RAG System Documentation

## 📋 Tổng Quan

Hệ thống RAG (Retrieval-Augmented Generation) nâng cao được thiết kế đặc biệt cho game text adventure, với các tính năng:

- **Hierarchical Memory**: Phân loại memory thành episodic, semantic, procedural, và lore
- **Local Embedding Model**: Sử dụng sentence-transformers để tạo embeddings local (không cần API)
- **Hybrid Search**: Kết hợp semantic search, keyword search (TF-IDF), và temporal scoring
- **Importance Scoring**: Tự động đánh giá tầm quan trọng của memories
- **Memory Compression**: Tự động nén memories cũ để tiết kiệm không gian
- **Lore Integration**: Tích hợp world knowledge từ files

---

## 🏗️ Kiến Trúc

### 1. Các Loại Memory (Bộ Nhớ Phân Cấp)

```python
MemoryType.EPISODIC    # Sự kiện gần đây, hành động của người chơi
MemoryType.SEMANTIC    # Kiến thức thế giới, NPCs, địa điểm
MemoryType.PROCEDURAL  # Quy tắc game, cơ chế
MemoryType.LORE        # Lịch sử thế giới, câu chuyện nền
```

### 2. Các Thành Phần

#### `AdvancedRAG` (engine/memory/advanced_rag.py)
- Hệ thống RAG cốt lõi với ChromaDB
- Model embedding local (sentence-transformers)
- Triển khai hybrid search
- Nén memory tự động

#### `MemoryManager` (engine/memory/memory_manager.py)
- Giao diện cấp cao cho game
- Tự động phân loại
- Các phương thức helper cho các thao tác thường dùng

---

## 🚀 Setup

### 1. Cài Đặt Dependencies

```bash
pip install sentence-transformers chromadb scikit-learn numpy
```

Hoặc thêm vào `requirements.txt`:
```
sentence-transformers>=2.2.0
chromadb>=0.4.0
scikit-learn>=1.3.0
numpy>=1.24.0
```

### 2. Chọn Embedding Model

**Khuyến nghị cho Vietnamese:**
```python
embedding_model = "paraphrase-multilingual-MiniLM-L12-v2"
```

**Các model khác:**
- `all-MiniLM-L6-v2` - Nhỏ nhất, nhanh nhất (English only)
- `paraphrase-multilingual-MiniLM-L12-v2` - Hỗ trợ đa ngôn ngữ (khuyến nghị)
- `all-mpnet-base-v2` - Chất lượng cao nhất nhưng chậm hơn

### 3. Khởi Tạo

```python
from engine.memory import get_advanced_rag, get_memory_manager

# Advanced RAG sẽ tự động khởi tạo
rag = get_advanced_rag()
memory_manager = get_memory_manager()
```

---

## 💻 Cách Sử Dụng

### Sử Dụng Cơ Bản

```python
from engine.memory import get_memory_manager, MemoryType

memory_manager = get_memory_manager()

# Ghi nhớ một hành động
memory_manager.remember_action(
    user_input="Tôi tấn công con goblin",
    narrative="Bạn vung kiếm và đánh trúng goblin gây 12 sát thương.",
    save_id="save_001",
    entity_id=2,  # ID của Goblin
    location_id="entrance",
    importance=0.8
)

# Lấy ngữ cảnh liên quan
context = memory_manager.get_relevant_context(
    query="Điều gì đã xảy ra với goblin?",
    save_id="save_001",
    n_results=5
)
```

### Sử Dụng Nâng Cao

```python
from engine.memory import AdvancedRAG, MemoryType

rag = get_advanced_rag()

# Thêm memory trực tiếp
memory_id = rag.add_memory(
    text="Người chơi phát hiện thanh kiếm cổ trong hầm mộ",
    memory_type=MemoryType.EPISODIC,
    save_id="save_001",
    location_id="crypt",
    importance=0.9,
    metadata={"discovery": True, "item": "ancient_sword"}
)

# Hybrid search
results = rag.search(
    query="thanh kiếm cổ hầm mộ",
    save_id="save_001",
    memory_types=[MemoryType.EPISODIC, MemoryType.SEMANTIC],
    n_results=5,
    min_importance=0.5,
    use_hybrid=True
)

for result in results:
    print(f"Điểm số: {result['score']:.2f}")
    print(f"Nội dung: {result['text']}")
    print(f"Loại: {result['memory_type']}")
```

### Các Helper Methods của Memory Manager

```python
# Ghi nhớ tương tác với NPC
memory_manager.remember_npc_interaction(
    npc_name="Marcus",
    dialogue="Động cơ đang nóng, thuyền trưởng.",
    save_id="save_001",
    npc_id=3,
    relationship_change=+5.0
)

# Ghi nhớ combat
memory_manager.remember_combat(
    enemy_name="Goblin",
    outcome="đã đánh bại",
    save_id="save_001",
    enemy_id=2,
    player_damage=5,
    enemy_damage=15
)

# Lấy memory về NPC
npc_memories = memory_manager.get_npc_memory(
    npc_name="Marcus",
    save_id="save_001"
)

# Lấy memory về địa điểm
location_memories = memory_manager.get_location_memory(
    location_name="entrance",
    save_id="save_001"
)
```

### Tải Lore

```python
# Tải world lore từ files
rag = get_advanced_rag()
rag.load_lore("data/lore")  # Tải tất cả file .md, .txt, .json

# Lore được lưu dưới dạng MemoryType.LORE với save_id="global"
```

---

## 🔍 Thuật Toán Hybrid Search

### Công Thức Tính Điểm

```
điểm_tổng = 
    0.4 * điểm_semantic +      # Độ tương đồng vector
    0.2 * điểm_keyword +       # Độ tương đồng TF-IDF
    0.2 * điểm_temporal +      # Độ mới (suy giảm theo hàm mũ)
    0.2 * điểm_importance      # Tầm quan trọng do người dùng định nghĩa
```

### Điểm Semantic
- Cosine similarity giữa query embedding và document embedding
- Phạm vi: 0.0 - 1.0

### Điểm Keyword
- Cosine similarity dựa trên TF-IDF
- Phạm vi: 0.0 - 1.0

### Điểm Temporal
- Suy giảm theo hàm mũ: `e^(-số_ngày / 30)`
- Chu kỳ bán rã 30 ngày
- Phạm vi: 0.0 - 1.0

### Điểm Importance
- Tầm quan trọng do người dùng định nghĩa khi thêm memory
- Phạm vi: 0.0 - 1.0

---

## 📊 Hiệu Năng

### Sử Dụng Bộ Nhớ

- **Model Embedding**: ~100-200 MB RAM
- **ChromaDB**: ~50-100 MB cho 10,000 memories
- **TF-IDF**: ~10-20 MB

**Tổng cộng**: ~200-400 MB cho hệ thống đầy đủ

### Tốc Độ

- **Tạo Embedding**: ~10-50ms mỗi query (CPU)
- **Tìm Kiếm**: ~50-200ms cho 10,000 memories
- **Thêm Memory**: ~20-50ms

**Khuyến nghị**: Hệ thống này phù hợp với máy có 32GB RAM như của bạn.

---

## ⚙️ Cấu Hình

### Tham Số AdvancedRAG

```python
rag = AdvancedRAG(
    persist_path="data/memory",           # Đường dẫn lưu trữ ChromaDB
    embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
    max_memories=10000,                   # Số lượng tối đa trước khi nén
    compression_threshold=5000            # Ngưỡng bắt đầu nén
)
```

### Tham Số Tìm Kiếm

```python
results = rag.search(
    query="...",
    save_id="save_001",
    memory_types=[MemoryType.EPISODIC],  # Lọc theo loại
    n_results=5,                         # Số lượng kết quả
    min_importance=0.3,                  # Tầm quan trọng tối thiểu
    entity_id=2,                         # Lọc theo entity
    location_id="entrance",              # Lọc theo địa điểm
    use_hybrid=True                      # Sử dụng hybrid search
)
```

---

## 🎯 Thực Hành Tốt Nhất

### 1. Đánh Giá Tầm Quan Trọng

```python
# Tầm quan trọng cao (0.8-1.0)
- Sự kiện cốt truyện lớn
- Cái chết của NPC
- Khám phá quan trọng
- Hoàn thành nhiệm vụ

# Tầm quan trọng trung bình (0.5-0.7)
- Combat thông thường
- Cuộc trò chuyện với NPC
- Thu thập vật phẩm
- Khám phá địa điểm

# Tầm quan trọng thấp (0.3-0.5)
- Hành động nhỏ
- Mô tả môi trường
- Thử nghiệm thất bại
```

### 2. Các Loại Memory

```python
# Sử dụng EPISODIC cho:
- Hành động của người chơi
- Gặp gỡ combat
- Tương tác với NPC
- Thu thập vật phẩm

# Sử dụng SEMANTIC cho:
- Mô tả địa điểm
- Lý lịch NPC
- Trạng thái thế giới
- Mối quan hệ giữa các entity

# Sử dụng PROCEDURAL cho:
- Quy tắc game
- Giải thích cơ chế
- Thông điệp hệ thống

# Sử dụng LORE cho:
- Bối cảnh thế giới
- Lịch sử
- Thần thoại
- Câu chuyện nền
```

### 3. Tối Ưu Query

```python
# Query tốt
"Cuộc trò chuyện với Marcus về động cơ"
"Combat với goblin ở cửa vào"
"Khám phá thanh kiếm cổ"

# Query không tốt
"cái"
"chuyện gì đã xảy ra"
"thứ gì đó"
```

### 4. Nén Memory

Hệ thống tự động nén khi đạt `compression_threshold`. Có thể tăng ngưỡng nếu cần:

```python
rag = AdvancedRAG(compression_threshold=10000)
```

---

## 🐛 Xử Lý Sự Cố

### Vấn Đề: "sentence-transformers not installed"

**Giải Pháp:**
```bash
pip install sentence-transformers
```

### Vấn Đề: "ChromaDB not available"

**Giải Pháp:**
```bash
pip install chromadb
```

### Vấn Đề: Hiệu năng tìm kiếm chậm

**Giải Pháp:**
1. Giảm `n_results`
2. Lọc bằng `memory_types`, `entity_id`, `location_id`
3. Tăng `min_importance` để loại bỏ memories không quan trọng
4. Sử dụng model nhỏ hơn: `all-MiniLM-L6-v2`

### Vấn Đề: Sử dụng bộ nhớ cao

**Giải Pháp:**
1. Giảm `max_memories`
2. Giảm `compression_threshold`
3. Sử dụng model nhỏ hơn
4. Xóa memories cũ thủ công

---

## 📈 Cải Tiến Tương Lai

- [ ] Tóm tắt memory (dựa trên LLM)
- [ ] Memory đa phương thức (hình ảnh, âm thanh)
- [ ] Phân cụm memory
- [ ] Tự động đánh giá tầm quan trọng
- [ ] Trực quan hóa memory
- [ ] Xuất/nhập memories
- [ ] Phân tích memory

---

## 🔗 References

- [Sentence Transformers](https://www.sbert.net/)
- [ChromaDB](https://www.trychroma.com/)
- [RAG Papers](https://arxiv.org/abs/2005.11401)

---

**Phiên bản**: 1.0  
**Cập nhật lần cuối**: 2025-12-02  
**Tác giả**: AI Assistant

