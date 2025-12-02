# Benchmark Testing Guide

## Mục đích
Đo lường hiệu năng thực tế của LLM trên HP ZBook G7 (i7-10850H, 32GB RAM, Quadro T1000 4GB) để quyết định:
- Model size phù hợp (3B, 4B, 7B, 8B)
- Quantization level (Q4_K_M, Q5_K_M, Q8)
- Chiến lược inference (CPU-only vs Hybrid GPU offloading)

## Các thông số đo

### 1. **Tokens/Second (t/s)**
- Tốc độ sinh token trong quá trình generation
- **Target**: ≥3 t/s cho trải nghiệm chấp nhận được

### 2. **Prompt Processing Time (ms)**
- Thời gian xử lý context ban đầu
- **Target**: <2000ms cho prompt 1K tokens

### 3. **VRAM Usage (MB)**
- Bộ nhớ GPU thực tế sử dụng
- **Limit**: <3500MB để tránh OOM

### 4. **RAM Usage (MB)**
- Bộ nhớ hệ thống sử dụng
- **Limit**: <20GB để dành cho OS + game engine

### 5. **Latency per Token (ms)**
- Thời gian trung bình để sinh 1 token
- **Target**: <300ms/token

## Models cần download để test

### Option A: CPU-focused (Khuyến nghị)
```bash
# Phi-3-mini 3.8B (Nhỏ, nhanh, quality tốt)
huggingface-cli download microsoft/Phi-3-mini-4k-instruct-gguf \
  Phi-3-mini-4k-instruct-q4.gguf --local-dir ./models

# Llama-3.2-3B (Mới, context 128K)
huggingface-cli download lmstudio-community/Llama-3.2-3B-Instruct-GGUF \
  Llama-3.2-3B-Instruct-Q4_K_M.gguf --local-dir ./models
```

### Option B: Balanced (Test để so sánh)
```bash
# Mistral-7B (Balanced quality/speed)
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF \
  mistral-7b-instruct-v0.2.Q4_K_M.gguf --local-dir ./models

# Llama-3-8B (High quality nhưng chậm hơn)
huggingface-cli download lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF \
  Meta-Llama-3-8B-Instruct-Q4_K_M.gguf --local-dir ./models
```

## Cài đặt dependencies

```bash
# Tạo virtual environment
python -m venv venv
venv\Scripts\activate

# Cài llama-cpp-python với CUDA support (nếu có)
# Lưu ý: Nếu lỗi, thử CPU-only build trước
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121

# Hoặc CPU-only:
pip install llama-cpp-python

# Cài dependencies khác
pip install psutil GPUtil tabulate colorama
```

## Chạy benchmark

### Test 1: Baseline CPU-only
```bash
python benchmark_inference.py --model models/Phi-3-mini-4k-instruct-q4.gguf --n_gpu_layers 0 --test_name "Phi3_CPU"
```

### Test 2: Hybrid với 8 layers trên GPU
```bash
python benchmark_inference.py --model models/Phi-3-mini-4k-instruct-q4.gguf --n_gpu_layers 8 --test_name "Phi3_8GPU"
```

### Test 3: So sánh model 7B
```bash
python benchmark_inference.py --model models/mistral-7b-instruct-v0.2.Q4_K_M.gguf --n_gpu_layers 0 --test_name "Mistral7B_CPU"
```

### Test 4: Full sweep (tất cả configs)
```bash
python benchmark_sweep.py
```

## Đọc kết quả

Kết quả được lưu trong `results/benchmark_results.json`:

```json
{
  "test_name": "Phi3_CPU",
  "model": "Phi-3-mini-4k-instruct-q4.gguf",
  "config": {
    "n_gpu_layers": 0,
    "n_ctx": 2048,
    "n_threads": 8
  },
  "metrics": {
    "tokens_per_second": 4.2,
    "prompt_processing_ms": 1250,
    "vram_mb": 450,
    "ram_mb": 3800,
    "avg_latency_ms": 238
  }
}
```

## Decision Matrix

| Metric | Phi-3-3.8B CPU | Mistral-7B CPU | Llama-3-8B Hybrid |
|--------|---------------|----------------|-------------------|
| t/s    | ✅ >3         | ⚠️ 2-3         | ❌ <2             |
| VRAM   | ✅ <1GB       | ✅ <1GB        | ⚠️ 3-3.5GB       |
| RAM    | ✅ ~4GB       | ⚠️ ~6GB        | ❌ ~8GB           |
| Quality| ⚠️ Good       | ✅ Excellent   | ✅ Best           |

## Khuyến nghị dựa trên kết quả

- **tokens/s ≥ 4**: Phi-3-mini hoặc Llama-3.2-3B → Dùng làm model chính
- **tokens/s 2-3**: Mistral-7B → Dùng cho "lazy inflation" offline, không real-time
- **tokens/s <2**: Loại bỏ, quá chậm cho text adventure

## Troubleshooting

### Lỗi: `ImportError: DLL load failed`
→ Cài lại với CPU-only build:
```bash
pip uninstall llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=off" pip install llama-cpp-python --no-cache-dir
```

### Lỗi: `CUDA out of memory`
→ Giảm `n_gpu_layers` hoặc `n_ctx`

### Lỗi: Tốc độ quá chậm (<1 t/s)
→ Kiểm tra:
1. `n_threads` = số cores vật lý (6 cho i7-10850H)
2. Tắt Turbo Boost throttling
3. Đảm bảo không chạy app khác nặng

## Next Steps

1. ✅ Chạy benchmark với ít nhất 3 models
2. ✅ So sánh kết quả trong `results/`
3. ✅ Quyết định model chính dựa trên decision matrix
4. ➡️ Update `ARCHITECTURE.md` với con số thực tế
5. ➡️ Bắt đầu implement game engine với model đã chọn
