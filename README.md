# 🗡️ AI Text Adventure Game

A neurosymbolic text adventure game powered by local AI, built with custom ECS architecture.

ollama serve

# Pull required model
ollama pull qwen2.5:3b
```

### Setup

**Install Dependencies:**
```bash
# Windows
install_all.bat

# Hoặc manual
pip install fastapi uvicorn python-dotenv google-generativeai networkx loguru
```

**Setup API Key:**
Create `.env` file:
```
GEMINI_API_KEY=your_key_here
```

### Play

**CLI Version:**
```bash
cd play
python play.py
# Hoặc: play_game.bat (Windows)
```

**React UI (Recommended):**
```bash
# Auto start (server + UI)
START_REACT_UI.bat

# Or manual:
# Terminal 1: python server.py
# Terminal 2: cd react-ui && npm run dev
# Then open: http://localhost:5173
```

**Server Mode:**
```bash
python server.py
# API runs on http://localhost:8000
```

## 🎯 Example Commands

```
🎮 > take the iron sword
🎮 > equip sword
🎮 > attack the goblin
🎮 > talk to the guard
🎮 > examine the door
🎮 > go north
```

## 📚 Documentation

- [How to Play](HOW_TO_PLAY.md) - Detailed gameplay guide
- [ECS Architecture](docs/architecture/ECS_EXPLAINED.md) - Technical design
- [Benchmark Results](BENCHMARK_RESULTS.md) - AI model performance

## 🛠️ Architecture

### Core Components

```
engine/
├── core/           # ECS system
│   ├── components.py   # 13 component types
│   ├── database.py     # SQLite storage
│   └── entity.py       # Entity manager
├── systems/        # Game logic
│   ├── validation.py   # Precondition checks
│   └── actions.py      # Action execution
└── ai/            # AI integration
    ├── schemas.py      # Pydantic models
    └── ollama_agent.py # Local LLM client
```

### Technology Stack

- **Language**: Python 3.10+
- **AI Backend**: Ollama (local LLM)
- **Database**: SQLite with JSON components
- **Validation**: Pydantic schemas
- **Architecture**: Entity-Component-System (ECS)

## 🧪 Testing

```bash
# Test core ECS
python test_ecs.py

# Run demo (without AI)
python demo_game.py

# Full playable game
python play.py
```

## 📊 Benchmark Results

Model performance on HP ZBook G7:

| Model | Speed (t/s) | Latency | Quality |
|-------|-------------|---------|---------|
| qwen2.5:3b | 41.91 | 24ms | ⭐⭐⭐⭐ |
| gemma2:2b | 27.51 | 36ms | ⭐⭐⭐ |
| phi3:3.8b | 18.34 | 55ms | ⭐⭐⭐⭐ |

All exceeded 3 t/s target by **6-14x**! See [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md) for details.

## 🎮 Current Features

- ✅ Natural language parsing
- ✅ AI-generated narratives
- ✅ Combat system with death
- ✅ Inventory management
- ✅ Equipment system
- ✅ NPC dialogues
- ✅ Door/container interactions
- ✅ Physics validation
- ✅ Auto-save to database

## 🚧 Roadmap

### Phase 2: Enhanced AI (Planned)
- [ ] Gemini Pro integration (cloud fallback)
- [ ] Hybrid routing (local + cloud)
- [ ] Context caching
- [ ] Self-correction on errors

### Phase 3: Advanced Features (Planned)
- [ ] ZeroMQ async messaging
- [ ] Vector memory (semantic lore)
- [ ] Drama/tension manager
- [ ] Procedural world generation

### Phase 4: UI (✅ Complete)
- [x] FastAPI backend
- [x] React frontend (Vite)
- [ ] Real-time WebSocket updates (Future)
- [x] Rich visual interface

## 🤝 Contributing

Contributions welcome! This is an experimental project exploring neurosymbolic AI for games.

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Built following neurosymbolic AI principles
- Inspired by Dwarf Fortress, AI Dungeon, and Façade
- Powered by Ollama and the open-source LLM community

## 📞 Support

For issues or questions, please open a GitHub issue.

---

**Made with ❤️ and AI** | *"Where physics meets creativity"*
