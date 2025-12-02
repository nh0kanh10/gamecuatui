# 🎮 Multi-Game Mode Architecture

## 📋 Overview

Game engine đã được tái cấu trúc để hỗ trợ nhiều game modes, nhưng **core principle vẫn giữ nguyên**: **User Decision → AI Response**.

## 🏗️ Architecture

### Base Structure

```
engine/games/
├── __init__.py          # Exports all game modes
├── base_game.py          # BaseGame class - base cho tất cả games
├── last_voyage/          # Game mode: Post-apocalyptic survival RPG
│   ├── __init__.py
│   └── game.py
└── cultivation_sim/       # Game mode: Tu Tiên Life Simulation
    ├── __init__.py
    └── game.py
```

### Core Flow (Unchanged)

```
User Input → AI (Gemini) → Response
```

Mỗi game mode có:
- Setup riêng (character creation, world setup)
- Prompt riêng (cultivation_master.md, game-master.md)
- State management riêng
- Nhưng đều dùng chung: ECS engine, Memory system, AI infrastructure

## 🎯 Game Modes

### 1. Last Voyage
- **Type**: Post-apocalyptic survival RPG
- **Prompt**: `data/prompts/game-master.md`
- **AI Agent**: `GeminiAgent`
- **Features**: Dungeon exploration, combat, NPCs

### 2. Cultivation Simulator
- **Type**: Tu Tiên Life Simulation
- **Prompt**: `data/prompts/cultivation_master.md`
- **AI Agent**: `CultivationAgent`
- **Features**:
  - Character creation (giới tính, thiên phú, chủng tộc, bối cảnh)
  - Age progression (0 tuổi → cultivation master)
  - 4-6 choices per year
  - Xianxia tropes (trùng sinh, chuyển sinh, cultivation realms)

## 🔧 Implementation

### BaseGame Class

```python
class BaseGame(ABC):
    def __init__(self, game_mode: str):
        self.game_mode = game_mode
        self.save_id = None
        self.em = None
        self.ai = get_gemini_agent()
        self.memory_manager = get_memory_manager()
    
    @abstractmethod
    def setup_world(self, **kwargs):
        """Create initial game world"""
        pass
    
    @abstractmethod
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state"""
        pass
    
    def process_turn(self, user_input: str) -> Dict[str, Any]:
        """Core flow: User input → AI → Response"""
        context = self.context_builder.build(self.player_id)
        response = self.ai.process_turn(user_input, context, save_id=self.save_id)
        self.apply_updates(response.get('state_updates', {}))
        return response
```

### Cultivation Simulator Flow

1. **Character Creation**:
   ```python
   character_data = {
       'gender': 'Nam',
       'talent': 'Thiên Linh Căn',
       'race': 'Nhân Tộc',
       'background': 'Gia Đình Tu Tiên'
   }
   game.start_new_game(character=character_data)
   ```

2. **AI Generates Background**:
   - Character name
   - Family story
   - Initial circumstances
   - First choices (age 0 → age 1)

3. **Year Progression**:
   ```python
   # Player selects choice (1-6)
   response = game.process_year_turn(choice_index=0)
   # AI continues story, provides new choices
   ```

## 🌐 API Endpoints

### New Game
```http
POST /game/new
{
    "player_name": "Hero",
    "game_mode": "cultivation_sim",  # or "last_voyage"
    "character_data": {  # For cultivation_sim
        "gender": "Nam",
        "talent": "Thiên Linh Căn",
        "race": "Nhân Tộc",
        "background": "Gia Đình Tu Tiên"
    }
}
```

### Process Action
```http
POST /game/action
{
    "user_input": "1"  # Choice index for cultivation sim
}
```

### List Game Modes
```http
GET /game/modes
```

## 📝 Adding New Game Modes

1. Create folder: `engine/games/your_game/`
2. Create `game.py` inheriting from `BaseGame`
3. Implement `setup_world()` and `get_game_state()`
4. Create prompt file: `data/prompts/your_game_master.md`
5. (Optional) Create specialized AI agent
6. Update `server.py` to handle new mode
7. Export in `engine/games/__init__.py`

## ✅ Benefits

- **Modular**: Mỗi game mode độc lập
- **Extensible**: Dễ thêm game mode mới
- **Consistent**: Core flow giữ nguyên
- **Reusable**: Shared ECS, Memory, AI infrastructure

---

**Version**: 1.0  
**Last Updated**: 2025-12-03

