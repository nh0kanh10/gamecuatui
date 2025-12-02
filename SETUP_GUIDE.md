# 🚀 Setup Guide - Neurosymbolic Text Adventure

## 📦 Dependencies Cần Download

### 1. Python Packages

#### Core Engine
```bash
pip install esper pydantic sqlalchemy chromadb
```

- `esper` - ECS framework
- `pydantic` - Data validation & schemas
- `sqlalchemy` - Advanced database ORM (optional, có thể dùng sqlite3 thuần)
- `chromadb` - Vector database cho semantic memory

#### AI Integration
```bash
pip install google-generativeai ollama
```

- `google-generativeai` - Gemini Pro SDK
- `ollama` - Local LLM client

#### Async & Messaging
```bash
pip install pyzmq fastapi uvicorn websockets
```

- `pyzmq` - ZeroMQ cho async messaging
- `fastapi` - Backend API server
- `uvicorn` - ASGI server
- `websockets` - Real-time updates

#### UI (Optional - nếu dùng NiceGUI thay vì SvelteKit)
```bash
pip install nicegui
```

#### Utilities
```bash
pip install networkx python-dotenv loguru
```

- `networkx` - Graph cho world simulation
- `python-dotenv` - Environment variables
- `loguru` - Structured logging

---

### 2. Ollama Models

```bash
# Nếu chưa cài Ollama, download tại: https://ollama.ai

# Pull model chính (đã có từ benchmark)
ollama pull qwen2.5:3b

# Optional: Pull model dự phòng nhỏ hơn (nhanh hơn, quality thấp hơn)
ollama pull gemma2:2b
```

---

### 3. Gemini API Key

1. Đăng nhập Google AI Studio: https://aistudio.google.com/
2. Tạo API key (hoặc dùng existing key từ Gemini Pro subscription)
3. Tạo file `.env` trong `d:\GameBuild`:

```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

---

### 4. Node.js & Frontend (Nếu dùng SvelteKit)

**Đã có**: Node.js v24.11.1 ✅

Cài dependencies cho `game-ui`:
```bash
cd game-ui
npm install
```

---

## 🔧 Automated Setup Script

Tạo file `setup_full.bat`:

```batch
@echo off
echo ========================================
echo   Neurosymbolic Game - Full Setup
echo ========================================

echo [1/5] Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [2/5] Installing Python dependencies...
pip install --upgrade pip
pip install esper pydantic sqlalchemy chromadb
pip install google-generativeai ollama
pip install pyzmq fastapi uvicorn websockets
pip install nicegui
pip install networkx python-dotenv loguru

echo.
echo [3/5] Checking Ollama models...
ollama list

echo.
echo [4/5] Setting up frontend...
cd game-ui
call npm install
cd ..

echo.
echo [5/5] Creating directory structure...
mkdir engine
mkdir engine\core
mkdir engine\ai
mkdir engine\systems
mkdir data
mkdir data\lore
mkdir logs

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Add GEMINI_API_KEY to .env file
echo 2. Run: python engine/main.py
echo.
pause
```

---

## 📁 Project Structure (Sẽ tạo)

```
d:\GameBuild\
├── engine\                 # Python backend
│   ├── __init__.py
│   ├── main.py            # Entry point
│   ├── core\              # ECS core
│   │   ├── components.py  # Component definitions
│   │   ├── systems.py     # System processors
│   │   └── entity.py      # Entity manager
│   ├── ai\                # AI agents
│   │   ├── gemini.py      # Gemini integration
│   │   ├── ollama.py      # Ollama integration
│   │   └── router.py      # Hybrid router
│   ├── systems\           # Game systems
│   │   ├── actions.py     # Action execution
│   │   ├── validation.py  # Precondition checks
│   │   └── narrative.py   # Narrative generation
│   └── utils\
│       ├── database.py
│       └── schemas.py     # Pydantic schemas
├── game-ui\               # SvelteKit frontend
├── data\
│   ├── world.db           # SQLite database
│   ├── vector.db          # ChromaDB
│   └── lore\              # JSON lore files
├── logs\
├── .env                   # API keys
└── requirements.txt       # Python deps
```

---

## ⚡ Quick Start (Sau khi setup)

### Backend
```bash
# Activate venv
venv\Scripts\activate

# Run engine
python engine/main.py
```

### Frontend (Terminal riêng)
```bash
cd game-ui
npm run dev
```

### Or: All-in-one với NiceGUI
```bash
venv\Scripts\activate
python engine/main_nicegui.py
# Mở browser: http://localhost:8080
```

---

## 🧪 Verification Tests

```bash
# Test 1: Ollama
curl http://localhost:11434/api/generate -d '{"model":"qwen2.5:3b","prompt":"Hello"}'

# Test 2: Gemini
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('OK')"

# Test 3: ChromaDB
python -c "import chromadb; print(chromadb.__version__)"

# Test 4: ZeroMQ
python -c "import zmq; print(zmq.zmq_version())"
```

---

## 🐛 Troubleshooting

### Issue: `pip install esper` fails
**Fix**: Esper có thể không active maintain. Dùng alternative:
```bash
pip install entitas-python
# Hoặc implement custom ECS (sẽ cung cấp code mẫu)
```

### Issue: ChromaDB requires specific Python version
**Fix**: ChromaDB yêu cầu Python 3.10+. Check:
```bash
python --version
```

### Issue: Gemini API quota exceeded
**Fix**: 
- Check https://aistudio.google.com/app/apikey
- Switch sang Ollama fallback trong dev
- Implement rate limiting

---

## 📊 Estimated Download Sizes

| Component | Size | Time (10Mbps) |
|-----------|------|---------------|
| Python packages | ~500MB | 5-7 min |
| Ollama qwen2.5:3b | 1.9GB | 15-20 min |
| Node modules (game-ui) | ~300MB | 3-5 min |
| **Total** | **~2.7GB** | **25-30 min** |

---

## ✅ Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] All Python packages installed
- [ ] Ollama running (`ollama serve`)
- [ ] qwen2.5:3b model pulled
- [ ] Gemini API key in `.env`
- [ ] Frontend dependencies installed
- [ ] Directory structure created

---

**Sau khi hoàn thành checklist này, bạn đã sẵn sàng để implement Phase 1!** 🎉
