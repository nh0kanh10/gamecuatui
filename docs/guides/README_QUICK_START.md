# 🚀 Quick Start Guide

## ⚡ One-Click Start

**Chỉ cần double-click file: `PLAY_GAME.bat`**

Script sẽ tự động:
- ✅ Kiểm tra Python và Node.js
- ✅ Cài đặt dependencies (nếu thiếu)
- ✅ Khởi động server
- ✅ Khởi động React UI
- ✅ Mở browser tự động

## 📋 Requirements

1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download](https://nodejs.org/)
3. **GEMINI_API_KEY** - Thêm vào file `.env`

## 🔧 First Time Setup

1. **Clone repository:**
   ```bash
   git clone https://github.com/nh0kanh10/gamecuatui.git
   cd gamecuatui
   ```

2. **Tạo file `.env`:**
   ```bash
   # Copy template
   copy .env.template .env
   
   # Edit .env và thêm:
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Chạy game:**
   - Double-click `PLAY_GAME.bat`
   - Hoặc: `QUICK_START.bat`

## 🎮 Game Modes

### Last Voyage
- Post-apocalyptic survival RPG
- Dungeon exploration, combat, NPCs

### Cultivation Simulator
- Tu Tiên life simulation
- Character creation → Age progression
- 4-6 choices per year

## 🌐 URLs

- **Server API**: http://localhost:8000
- **Game UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## 🛠️ Manual Start (if needed)

### Start Server:
```bash
python server.py
```

### Start UI:
```bash
cd react-ui
npm install  # First time only
npm run dev
```

## ❌ Troubleshooting

### Port 8000 already in use:
```bash
# Kill process on port 8000
call kill_port_8000.bat
```

### Dependencies missing:
```bash
# Install Python packages
pip install -r requirements.txt

# Install React packages
cd react-ui
npm install
```

### API Key not working:
- Check `.env` file exists
- Verify `GEMINI_API_KEY` is set correctly
- Get API key from: https://makersuite.google.com/app/apikey

---

**Enjoy the game! 🎮**

