# 🚀 Quick Install Guide

## ⚡ Fastest Way

```bash
# Windows
install_all.bat

# Hoặc từng package
pip install fastapi uvicorn python-dotenv google-generativeai nicegui networkx loguru
```

## 📋 Required Packages

1. **fastapi** - API server
2. **uvicorn** - ASGI server
3. **python-dotenv** - Environment variables
4. **google-generativeai** - Gemini AI
5. **nicegui** - UI framework
6. **networkx** - Graph utilities
7. **loguru** - Logging

## ✅ Verify Installation

```bash
python -c "import fastapi, uvicorn, google.generativeai; print('✅ All OK!')"
```

## 🔑 Setup API Key

Create `.env` file in root folder:
```
GEMINI_API_KEY=your_api_key_here
```

## 🎮 Run Game

```bash
# Start server
python server.py

# Or use UI
play\start_game_ui.bat
```

---

**Status**: ✅ Ready to Play

