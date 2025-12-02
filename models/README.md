# Models Directory

Thư mục chứa các AI models (GGUF format).

**Không commit models vào git** (files rất lớn, đã exclude trong `.gitignore`)

## Download models

```bash
python benchmarks/download_models.py
```

## Models khuyến nghị

| Model | Size | Use Case |
|-------|------|----------|
| phi-3-mini-4k-q4.gguf | 2.4GB | Main model - real-time inference |
| llama-3.2-3b-q4.gguf | 1.9GB | Alternative - very fast |
| mistral-7b-q4.gguf | 4.4GB | Offline generation - best quality |

## Manual download

Nếu script không hoạt động, tải thủ công:

- Phi-3: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
- Llama-3.2: https://huggingface.co/lmstudio-community/Llama-3.2-3B-Instruct-GGUF
- Mistral-7B: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF

Đặt file `.gguf` vào thư mục này.
