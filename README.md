# 🎮 Game Engine - AI-Powered Text Adventure

Multi-game mode engine với AI (Gemini) để tạo trải nghiệm text adventure linh hoạt.

## ⚡ Quick Start

**Chỉ cần double-click: `PLAY_GAME.bat`**

Script sẽ tự động:
- ✅ Kiểm tra dependencies
- ✅ Cài đặt packages
- ✅ Khởi động server + UI
- ✅ Mở browser

## 📋 Requirements

- Python 3.8+
- Node.js 18+
- GEMINI_API_KEY (thêm vào `.env`)

## 🎯 Game Modes

### 1. Last Voyage
Post-apocalyptic survival RPG với dungeon exploration.

### 2. Cultivation Simulator
Tu Tiên life simulation - từ lúc sinh ra đến cultivation master.

## 📁 Project Structure

```
GameBuild/
├── PLAY_GAME.bat          # ⭐ One-click launcher
├── engine/                # Game engine core
│   ├── games/            # Game modes
│   ├── ai/               # AI integration
│   ├── core/             # ECS system
│   └── memory/           # Memory system
├── react-ui/             # React frontend
├── server.py             # FastAPI backend
├── data/                 # Game data
│   ├── prompts/         # AI prompts
│   └── saves/           # Save files
└── docs/                 # Documentation
```

## 🚀 Manual Start

### Server:
```bash
python server.py
```

### UI:
```bash
cd react-ui
npm install  # First time
npm run dev
```

## 📚 Documentation

- **Quick Start**: `docs/guides/README_QUICK_START.md`
- **Architecture**: `docs/MULTI_GAME_ARCHITECTURE.md`
- **File Organization**: `docs/rules/file-organization.md`

## 🔧 Scripts

- `PLAY_GAME.bat` - Main launcher (⭐ use this)
- `scripts/launchers/` - Alternative launchers
- `scripts/` - Utility scripts

## 🌐 URLs

- **Game UI**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📝 License

MIT

---

**Repository**: https://github.com/nh0kanh10/gamecuatui
