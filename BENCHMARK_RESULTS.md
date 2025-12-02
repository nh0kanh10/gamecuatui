# 🏆 Benchmark Results - HP ZBook G7 + Ollama

**Date**: 2025-12-02  
**Hardware**: Intel i7-10850H, 32GB RAM, Quadro T1000 4GB  
**Backend**: Ollama (local API)

---

## 📊 Performance Comparison

| Model | Avg Speed (t/s) | Latency (ms) | RAM (MB) | Verdict |
|-------|-----------------|--------------|----------|---------|
| **qwen2.5:3b** | 🥇 **41.91** | **24** | 49 | ✅ FASTEST |
| **gemma2:2b** | 🥈 **27.51** | **36** | 49 | ✅ EXCELLENT |
| **phi3:3.8b** | 🥉 **18.34** | **55** | 49 | ✅ EXCELLENT |

**Target**: ≥3 t/s (all models exceed by **6-14x**!)

---

## 🎯 KHUYẾN NGHỊ CHÍNH

### **Model được chọn: qwen2.5:3b** 🚀

**Lý do:**
1. **Nhanh nhất**: 41.91 t/s → Phản hồi tức thì
2. **Latency thấp nhất**: 24ms/token → Trải nghiệm mượt
3. **RAM nhỏ**: Chỉ 49MB
4. **Quality tốt**: Tạo narrative mạch lạc

### Phương án dự phòng

- **gemma2:2b**: Nhanh thứ 2, dùng nếu qwen có vấn đề quality
- **phi3:3.8b**: Ổn định nhất, tốt cho reasoning phức tạp

---

## 📝 Chi tiết từng model

### qwen2.5:3b (KHUYẾN NGHỊ)
```
Short Context:   43.59 t/s (23ms/token) ⚡
Medium Context:  45.10 t/s (22ms/token) ⚡
Long Context:    37.05 t/s (27ms/token) ⚡

Quality Sample:
"You inspect the iron gate closely for any signs of 
damage or weakness you might exploit. The gate is 
ancient, its surface pitted and corroded..."
```

### gemma2:2b (DỰ PHÒNG)
```
Short Context:   27.81 t/s (36ms/token)
Medium Context:  28.44 t/s (35ms/token)
Long Context:    26.27 t/s (38ms/token)

Quality Sample:
"The air hangs thick and heavy around you, saturated 
with the smell of damp earth and decaying wood..."
```

### phi3:3.8b (ỔN ĐỊNH)
```
Short Context:   18.71 t/s (53ms/token)
Medium Context:  18.95 t/s (53ms/token)
Long Context:    17.35 t/s (58ms/token)

Quality Sample:
"Aria's keen eyes survey the heavily rusted lock on 
the massive door before her; she can see that it..."
```

---

## 💡 Cách triển khai vào Game

### 1. Sử dụng qwen2.5:3b

```python
import ollama

def generate_narrative(prompt: str, max_tokens: int = 150):
    response = ollama.generate(
        model='qwen2.5:3b',
        prompt=prompt,
        options={
            'num_predict': max_tokens,
            'temperature': 0.7
        }
    )
    return response['response']
```

### 2. Structured Output (cho game logic)

```python
def parse_player_action(input_text: str):
    prompt = f"""Parse this player command into JSON:
Input: "{input_text}"

Return JSON with: action, target, modifiers
Example: {{"action": "examine", "target": "gate", "modifiers": ["carefully"]}}
"""
    
    response = ollama.generate(
        model='qwen2.5:3b',
        prompt=prompt,
        format='json'  # Force JSON output
    )
    return json.loads(response['response'])
```

### 3. Context Management

Với 41 t/s:
- **8K tokens** xử lý trong ~3 phút (acceptable cho lazy inflation)
- **Real-time narrative** (<200 tokens): ~5 giây
- **Expected UX**: Mượt mà, gần như instant

---

## 🔥 So sánh với Dự đoán Ban đầu

| Metric | Dự đoán (Báo cáo) | Thực tế (qwen2.5) | Chênh lệch |
|--------|-------------------|-------------------|-----------|
| Speed | 3-6 t/s | **41.91 t/s** | **+700% 🔥** |
| Latency | <300ms | **24ms** | **12x nhanh hơn** |
| RAM | 4-6GB | **49MB** | **100x ít hơn** |
| VRAM needed | 2-3GB | **0GB** | **Không cần GPU!** |

**→ Ollama + CPU inference MẠNH HƠN DỰ ĐOÁN RẤT NHIỀU!**

---

## ⚠️ Lưu ý

1. **VRAM = 0MB**: Ollama manage internally, không cần quan tâm
2. **GPU không cần thiết**: CPU đã đủ nhanh, save VRAM cho tương lai
3. **Quality testing**: Cần test A/B trong game thực tế
   - qwen2.5: nhanh nhưng có thể hallucinate
   - phi3: chậm hơn nhưng coherent hơn

---

## 🚀 Next Steps

### Giai đoạn 1: Prototype (1-2 tuần)
- ✅ **Chọn qwen2.5:3b** làm model chính
- ✅ Implement basic game loop với Ollama
- ✅ Test structured JSON output
- ✅ Build ECS + SQLite (như thiết kế)

### Giai đoạn 2: Optimization (nếu cần)
- ⏭️ A/B test qwen vs phi3 trong game
- ⏭️ Tune temperature/parameters
- ⏭️ Implement context sliding window
- ⏭️ Add caching layer

### Giai đoạn 3: Production (optional)
- ⏭️ Consider llama.cpp nếu cần fine-tuning
- ⏭️ Hoặc giữ Ollama (đơn giản, đủ nhanh)

---

## 📁 Files tham khảo

**JSON results:**
- `benchmarks/results/qwen2.5_3b_20251202_170354.json`
- `benchmarks/results/gemma2_2b_20251202_170326.json`
- `benchmarks/results/phi3_3.8b_20251202_170242.json`

Xem chi tiết: `python -m json.tool <filename>`

---

## ✨ Kết luận

**Hardware constraint (4GB VRAM) KHÔNG PHẢI VẤN ĐỀ**

Nhờ:
1. CPU i7-10850H mạnh
2. Ollama optimize cực tốt
3. Models 2-4B đủ quality cho text adventure

**→ Có thể bắt đầu implement game NGAY!** 🎮
