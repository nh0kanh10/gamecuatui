# 🌟 Cultivation Simulator - Standalone Game

Tu Tiên Life Simulation - Từ lúc sinh ra đến cultivation master

## 🎯 Tính Năng

- **Character Creation**: Chọn giới tính, thiên phú, chủng tộc, bối cảnh
- **AI Generation**: AI tự động tạo background và gia đình
- **Age Progression**: Từ 0 tuổi → cultivation master
- **Choice-Based**: 4-6 lựa chọn mỗi năm
- **Xianxia World**: Trùng sinh, chuyển sinh, cultivation realms

## 🚀 Quick Start

### Windows
```bash
# Double-click
START.bat

# Hoặc manual
python server.py
```

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
echo GEMINI_API_KEY=your_key_here > .env
```

## 📁 Cấu Trúc

```
cultivation-sim/
├── server.py              # FastAPI server (port 8001)
├── game.py                # Game logic
├── agent.py               # AI agent (CultivationAgent)
├── schemas.py             # Pydantic schemas
├── memory.py              # Memory system (riêng)
├── database.py            # Database (riêng)
├── compaction.py          # Memory compaction
├── data/
│   ├── saves/            # Save files (riêng)
│   └── prompts/
│       └── master.md     # System prompt
├── requirements.txt
├── START.bat
└── README.md
```

## 🎮 Game Flow

1. **Character Creation** → AI generates background
2. **Age 0**: First choices (4-6 options)
3. **Each Year**: Select choice → AI continues story
4. **Progress** until cultivation master or death

## 🔧 Configuration

- **Database**: `data/saves/{save_id}.db` (SQLite riêng)
- **Memory**: SQLite FTS5 (riêng cho cultivation sim)
- **AI**: Gemini 1.5 Flash
- **Port**: 8001 (khác với Last Voyage ở 8000)

## 🌐 API Endpoints

- `POST /game/new` - Create new game
- `POST /game/action` - Process choice (1-6)
- `GET /game/state` - Get current state
- `GET /memory/count` - Get memory count
- `GET /health` - Health check

## 📝 Example

```python
# Create character
POST /game/new
{
    "player_name": "Lâm Tiêu",
    "character_data": {
        "gender": "Nam",
        "talent": "Thiên Linh Căn",
        "race": "Nhân Tộc",
        "background": "Gia Đình Tu Tiên"
    }
}

# Select choice
POST /game/action
{
    "user_input": "1"  # Choice index
}
```

## 🔐 Features

- ✅ Standalone (không phụ thuộc multi-game)
- ✅ Database riêng
- ✅ Memory system riêng
- ✅ Pydantic validation
- ✅ Input/output moderation
- ✅ Error handling với fallback

---

**Status**: ✅ Standalone Game - Ready to Play
