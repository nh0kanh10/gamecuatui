# ✅ Benchmark Testing Setup - Hoàn tất

## 📦 Đã tạo

### Scripts
- ✅ `benchmarks/benchmark_inference.py` - Script test đơn lẻ
- ✅ `benchmarks/download_models.py` - Download models tự động
- ✅ `benchmarks/benchmark_sweep.py` - Test tất cả configs
- ✅ `benchmarks/requirements.txt` - Dependencies
- ✅ `setup_benchmark.bat` - Setup nhanh (Windows)

### Docs
- ✅ `benchmarks/README.md` - Hướng dẫn chi tiết
- ✅ `QUICK_START_BENCHMARK.md` - Quick start guide
- ✅ `models/README.md` - Hướng dẫn download models

### Folders
- ✅ `models/` - Chứa AI models (.gguf)
- ✅ `benchmarks/results/` - Chứa kết quả benchmark

### Config
- ✅ `.gitignore` - Exclude models + results (files lớn)

---

## 🚀 Bước tiếp theo (cho bạn)

### 1️⃣ Setup môi trường (3-5 phút)

```bash
# Chạy script tự động
setup_benchmark.bat
```

Hoặc:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r benchmarks\requirements.txt
```

### 2️⃣ Download models (10-30 phút tùy mạng)

```bash
# Activate venv trước
venv\Scripts\activate

# Download
python benchmarks\download_models.py
```

**Khuyến nghị**: Chọn Option 2 (Priority 1 only) để tải Phi-3-mini (2.4GB) - nhanh nhất.

### 3️⃣ Chạy benchmark đầu tiên (2-3 phút)

```bash
# Test CPU-only
python benchmarks\benchmark_inference.py ^
  --model models\phi-3-mini-4k-q4.gguf ^
  --n_gpu_layers 0 ^
  --test_name Phi3_CPU
```

Xem kết quả ngay trong console!

### 4️⃣ Test với GPU (nếu muốn so sánh)

```bash
# Test 4 layers trên GPU
python benchmarks\benchmark_inference.py ^
  --model models\phi-3-mini-4k-q4.gguf ^
  --n_gpu_layers 4 ^
  --test_name Phi3_4GPU

# Test 8 layers
python benchmarks\benchmark_inference.py ^
  --model models\phi-3-mini-4k-q4.gguf ^
  --n_gpu_layers 8 ^
  --test_name Phi3_8GPU
```

### 5️⃣ (Optional) Full sweep tất cả - chạy qua đêm

```bash
python benchmarks\benchmark_sweep.py
```

Sau khi xong, xem `benchmarks/results/COMPARISON_REPORT.md`

---

## 📊 Sau khi có kết quả

### Quyết định dựa trên metrics

| tokens/s | Quyết định |
|----------|-----------|
| ≥4 t/s | ✅ Dùng làm model chính, real-time |
| 3-4 t/s | ✅ OK cho text adventure |
| 2-3 t/s | ⚠️ Dùng offline generation only |
| <2 t/s | ❌ Loại bỏ |

### Update architecture docs

Sau khi biết con số thực tế:
1. Mở `docs/architecture/ARCHITECTURE.md`
2. Update phần "Hardware Analysis" với số liệu thực
3. Chọn chiến lược: CPU-only hoặc Hybrid
4. Document model đã chọn

---

## 🎯 Expected Results (dự đoán)

### Phi-3-mini-4k Q4 (CPU-only)
- Speed: **4-5 t/s** ✅
- VRAM: **~500MB** ✅
- RAM: **~4GB** ✅
- **→ Khả năng cao sẽ chọn config này**

### Mistral-7B Q4 (CPU-only)
- Speed: **2-3 t/s** ⚠️
- RAM: **~6GB** ✅
- **→ Có thể dùng cho lazy inflation**

### Hybrid offloading
- Có thể **KHÔNG giúp ích** trên Quadro T1000 do PCIe overhead
- Cần test để chắc chắn

---

## 🆘 Troubleshooting

### Q: Download lỗi "SSL Certificate error"
A: 
```bash
pip install --upgrade certifi
# Hoặc download manual từ HuggingFace
```

### Q: llama-cpp-python install lỗi
A:
```bash
# Thử CPU-only build
pip install llama-cpp-python --no-cache-dir
```

### Q: Out of memory khi test
A: Giảm `--n_gpu_layers` hoặc `--n_ctx 1024`

---

## 📝 Notes

- Models được download vào `models/` và **KHÔNG được commit** vào git
- Tất cả kết quả lưu trong `benchmarks/results/`
- Mỗi test mất ~2-5 phút
- Full sweep (~7 tests) mất ~30-60 phút

---

## ✨ Sau khi benchmark xong

Ping tôi với kết quả để:
1. Phân tích con số thực tế
2. So với dự đoán ban đầu
3. Quyết định model + config cuối cùng
4. Bắt đầu implement game engine 🎮

Good luck! 🚀
