# 🚀 Quick Start: Benchmark Testing

## Bước 1: Setup môi trường (chỉ chạy 1 lần)

```bash
# Chạy script tự động
setup_benchmark.bat
```

Hoặc làm thủ công:
```bash
# Tạo virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Cài dependencies
pip install -r benchmarks\requirements.txt
```

---

## Bước 2: Download models

```bash
# Chạy script download tự động
python benchmarks\download_models.py
```

Script sẽ hỏi bạn chọn:
- **Option 1**: Tải tất cả (khuyến nghị nếu đủ dung lượng)
- **Option 2**: Chỉ tải Phi-3-mini (nhanh nhất, ~2.4GB)
- **Option 3**: Chọn từng model

**Models được download:**
- `Phi-3-mini-4k-q4.gguf` (2.4GB) - Khuyến nghị
- `llama-3.2-3b-q4.gguf` (1.9GB) - Mới nhất
- `mistral-7b-q4.gguf` (4.4GB) - So sánh

---

## Bước 3: Chạy benchmark

### Option A: Test đơn lẻ (nhanh)

```bash
# Test CPU-only với Phi-3
python benchmarks\benchmark_inference.py ^
  --model models\phi-3-mini-4k-q4.gguf ^
  --n_gpu_layers 0 ^
  --test_name Phi3_CPU

# Test với GPU (8 layers)
python benchmarks\benchmark_inference.py ^
  --model models\phi-3-mini-4k-q4.gguf ^
  --n_gpu_layers 8 ^
  --test_name Phi3_8GPU
```

### Option B: Test tất cả configs (tự động)

```bash
# Chạy full sweep (5-10 phút/test)
python benchmarks\benchmark_sweep.py
```

Script sẽ:
- Test tất cả models với các configs khác nhau
- Tự động lưu kết quả
- Tạo báo cáo so sánh

---

## Bước 4: Xem kết quả

Kết quả được lưu trong:
```
benchmarks/results/
├── Phi3_CPU_20251202_164830.json
├── Phi3_8GPU_20251202_165245.json
├── ...
└── COMPARISON_REPORT.md   ← Báo cáo so sánh
```

### Mở báo cáo so sánh:
```bash
code benchmarks\results\COMPARISON_REPORT.md
```

### Đọc JSON kết quả:
```bash
python -m json.tool benchmarks\results\Phi3_CPU_*.json
```

---

## Các thông số quan trọng

| Metric | Target | Ý nghĩa |
|--------|--------|---------|
| **tokens/second** | ≥3 t/s | Tốc độ sinh text - càng cao càng tốt |
| **avg_latency_ms** | <300ms | Độ trễ mỗi token - càng thấp càng tốt |
| **max_vram_mb** | <3500MB | VRAM sử dụng - phải < 4GB |
| **max_ram_mb** | <20GB | RAM sử dụng - để lại cho OS |

---

## Giải thích kết quả

### ✅ Excellent (≥4 t/s)
→ Dùng làm model chính cho real-time gameplay

### ✅ Good (3-4 t/s)
→ Chấp nhận được cho text adventure

### ⚠️ Marginal (2-3 t/s)
→ Có thể dùng cho "lazy inflation" (offline generation)

### ❌ Poor (<2 t/s)
→ Quá chậm, không sử dụng

---

## Troubleshooting

### Lỗi: `ImportError: DLL load failed`
**Nguyên nhân**: llama-cpp-python không build được với CUDA

**Giải pháp**: Dùng CPU-only build
```bash
pip uninstall llama-cpp-python
pip install llama-cpp-python --no-cache-dir
```

### Lỗi: `CUDA out of memory`
**Nguyên nhân**: Quá nhiều layers trên GPU

**Giải pháp**: Giảm `--n_gpu_layers`
```bash
# Thay vì 8, dùng 4
python benchmarks\benchmark_inference.py --model models\phi-3-mini-4k-q4.gguf --n_gpu_layers 4 --test_name Phi3_4GPU
```

### Tốc độ quá chậm (<1 t/s)
**Kiểm tra**:
1. Đúng số threads: `--n_threads 8` (= số threads vật lý)
2. Không chạy app khác nặng
3. Laptop không ở chế độ tiết kiệm pin

---

## Next Steps sau khi có kết quả

1. ✅ Chọn model tốt nhất từ `COMPARISON_REPORT.md`
2. ✅ Update `docs/architecture/ARCHITECTURE.md` với con số thực tế
3. ✅ Quyết định chiến lược:
   - CPU-only nếu GPU không giúp được gì
   - Hybrid nếu GPU tăng tốc đáng kể
4. ➡️ Bắt đầu implement game engine với config đã chọn

---

## Example Output

```
🔬 Benchmark: Phi3_CPU
============================================================
Model: phi-3-mini-4k-q4.gguf
Config: n_gpu_layers=0, n_ctx=2048, n_threads=8
============================================================

🧪 Test: Short Context
   Prompt length: 53 chars
   ✅ Tokens: 100 | Speed: 4.23 t/s | Latency: 236ms
   VRAM: 450MB | RAM: 3800MB

📊 SUMMARY: Phi3_CPU
============================================================
Average Speed:    4.15 tokens/second
Average Latency:  241 ms/token
Peak VRAM:        450 MB
Peak RAM:         3850 MB

🎯 VERDICT:
   ✅ EXCELLENT - Suitable for real-time text adventure
```
