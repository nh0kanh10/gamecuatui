# 🌟 Cultivation Simulator - Standalone Project

> **Mục đích**: Cultivation Simulator đã được tách ra thành project riêng biệt, độc lập hoàn toàn

---

## 📋 Lý Do Tách Ra

1. **Đơn giản hóa**: Multi-game architecture quá phức tạp cho nhu cầu thực tế
2. **Độc lập**: Mỗi game có database, memory system, và thuộc tính riêng
3. **Dễ maintain**: Không cần lo về conflicts giữa các game modes
4. **Tối ưu**: Mỗi game có thể optimize riêng

---

## 📁 Cấu Trúc Project

```
cultivation-sim/
├── server.py              # FastAPI server (port 8001)
├── game.py                # Game logic (CultivationSimulator)
├── agent.py               # AI agent (CultivationAgent)
├── schemas.py             # Pydantic schemas
├── memory.py              # Memory system (riêng)
├── database.py            # Database (riêng)
├── compaction.py          # Memory compaction
├── data/
│   ├── saves/            # Save files (riêng)
│   └── prompts/
│       └── master.md     # System prompt
├── requirements.txt       # Dependencies riêng
├── START.bat             # Launcher
└── README.md
```

---

## 🔧 Khác Biệt Với Multi-Game

### Trước (Multi-Game)

```
engine/games/
├── base_game.py          # Base class
├── last_voyage/
└── cultivation_sim/      # Phụ thuộc base_game

server.py                 # Handle cả 2 games
```

**Vấn đề**:
- Phức tạp không cần thiết
- Shared code gây confusion
- Khó optimize riêng

### Sau (Standalone)

```
cultivation-sim/          # Hoàn toàn độc lập
├── game.py               # Không phụ thuộc base_game
├── server.py             # Server riêng
└── ...

GameBuild/                # Last Voyage (riêng)
├── server.py
└── ...
```

**Lợi ích**:
- ✅ Đơn giản, rõ ràng
- ✅ Mỗi game optimize riêng
- ✅ Dễ maintain
- ✅ Có thể deploy riêng

---

## 🎮 Game Features

### Character Creation

```python
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
```

### Age Progression

```python
POST /game/action
{
    "user_input": "1"  # Choice index (1-6)
}
```

### Game State

```python
GET /game/state
{
    "save_id": "...",
    "character_name": "Lâm Tiêu",
    "age": 5,
    "gender": "Nam",
    "talent": "Thiên Linh Căn",
    "current_choices": [...]
}
```

---

## 💾 Database & Memory

### Database

- **Location**: `cultivation-sim/data/saves/{save_id}.db`
- **Tables**: 
  - `game_state` - Game state
  - `memory_content` - Memory content
  - `memory_metadata` - Memory metadata
  - `memory_fts` - FTS5 search

### Memory System

- **Standalone**: Không share với Last Voyage
- **FTS5**: Full-text search riêng
- **Compaction**: Auto cleanup khi > 1000 memories

---

## 🚀 Deployment

### Single Instance

```bash
cd cultivation-sim
python server.py
# Runs on http://localhost:8001
```

### With Last Voyage

```bash
# Terminal 1: Last Voyage
cd GameBuild
python server.py
# Port 8000

# Terminal 2: Cultivation Simulator
cd cultivation-sim
python server.py
# Port 8001
```

---

## 📊 So Sánh

| Aspect | Multi-Game | Standalone |
|--------|-----------|------------|
| **Complexity** | High | Low |
| **Dependencies** | Shared | Independent |
| **Database** | Shared | Separate |
| **Memory** | Shared | Separate |
| **Deployment** | Single server | Can separate |
| **Maintenance** | Complex | Simple |

---

## ✅ Benefits

1. **Simplicity**: Code đơn giản, dễ hiểu
2. **Independence**: Mỗi game độc lập
3. **Optimization**: Có thể optimize riêng
4. **Deployment**: Có thể deploy riêng
5. **Maintenance**: Dễ maintain và debug

---

## 🔄 Migration Notes

### Từ Multi-Game

Nếu có save files từ multi-game version:
- Save files: `data/saves/cultivation_sim_*.db`
- Copy sang: `cultivation-sim/data/saves/`
- Format tương tự, không cần convert

### Code Changes

- ❌ Removed: `engine/games/cultivation_sim/`
- ❌ Removed: `CultivationSimGame` from `server.py`
- ✅ Created: `cultivation-sim/` standalone

---

**Version**: 1.0  
**Last Updated**: 2025-12-03  
**Status**: ✅ Standalone - Ready

