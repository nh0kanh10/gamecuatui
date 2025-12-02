# Dependencies Guide

## ✅ Core Dependencies (Required)

```bash
pip install fastapi uvicorn python-dotenv google-generativeai nicegui networkx loguru
```

Hoặc:
```bash
pip install -r requirements.txt
```

## 📦 Optional Dependencies

### Legacy RAG System (Not Used)
Các packages này **KHÔNG CẦN** vì đã chuyển sang Simple Memory System:
- `chromadb` - Không cần
- `sentence-transformers` - Không cần
- `scikit-learn` - Không cần
- `numpy` - Không cần (trừ khi dùng legacy code)

**Lý do**: Simple Memory System dùng SQLite FTS5, không cần vector database.

### Nếu Muốn Dùng Legacy VectorMemory
```bash
pip install chromadb sentence-transformers scikit-learn numpy
```

---

## 🐛 Troubleshooting

### Error: "ResolutionImpossible"
**Solution**: 
1. Xóa các optional dependencies khỏi requirements.txt
2. Hoặc install từng package một:
   ```bash
   pip install fastapi
   pip install uvicorn
   pip install python-dotenv
   pip install google-generativeai
   pip install nicegui
   ```

### Error: "chromadb not found"
**Solution**: Không cần ChromaDB! Simple Memory System không dùng nó.

### Error: "sentence-transformers not found"
**Solution**: Không cần sentence-transformers! Simple Memory System không dùng nó.

---

## ✅ Minimal Installation

Chỉ cần các packages này để chạy game:

```bash
pip install fastapi uvicorn python-dotenv google-generativeai nicegui
```

---

**Status**: ✅ Simple Memory System không cần ChromaDB/sentence-transformers

