# 🌟 Cultivation Simulator - Tài Liệu Chi Tiết

> **Mục đích**: Tài liệu chi tiết về cách Cultivation Simulator hoạt động, workflow, công nghệ sử dụng, và cách sử dụng

---

## 📋 Mục Lục

1. [Tổng Quan](#tổng-quan)
2. [Workflow (Luồng Làm Việc)](#workflow-luồng-làm-việc)
3. [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)
4. [Cấu Trúc Code](#cấu-trúc-code)
5. [Character Creation System](#character-creation-system)
6. [Age Progression System](#age-progression-system)
7. [AI Integration](#ai-integration)
8. [Memory System](#memory-system)
9. [API Endpoints](#api-endpoints)
10. [Ví Dụ Sử Dụng](#ví-dụ-sử-dụng)

---

## 🎯 Tổng Quan

**Cultivation Simulator** là một game mode mô phỏng cuộc sống trong thế giới Tu Tiên (Xianxia), cho phép người chơi:

- Tạo nhân vật với các lựa chọn: Giới tính, Thiên phú, Chủng tộc, Bối cảnh
- Trải nghiệm cuộc sống từ lúc sinh ra (0 tuổi) đến khi trở thành cultivation master
- Đưa ra quyết định mỗi năm với 4-6 lựa chọn
- AI tự động tạo câu chuyện dựa trên lựa chọn của người chơi

### Core Principle

**User Decision → AI Response**

Người chơi đưa ra quyết định → AI (Gemini) tạo narrative và đưa ra lựa chọn tiếp theo

---

## 🔄 Workflow (Luồng Làm Việc)

### Phase 1: Khởi Tạo Game

```
1. User gọi API: POST /game/new
   {
     "game_mode": "cultivation_sim",
     "player_name": "Lâm Tiêu",
     "character_data": {
       "gender": "Nam",
       "talent": "Thiên Linh Căn",
       "race": "Nhân Tộc",
       "background": "Gia Đình Tu Tiên"
     }
   }

2. Server tạo CultivationSimGame instance
   - game_instance = CultivationSimGame()
   - save_id = game_instance.start_new_game(character=character_data)

3. Game instance setup_world():
   - Tạo player entity trong ECS
   - Set initial stats (HP=10, Mana=0)
   - Set location = "birthplace"
   - Set age = 0
   - Lưu character data (gender, talent, race, background)

4. AI Generation (Character Background):
   - Gọi CultivationAgent.process_turn("Tạo nhân vật", context, save_id, char_data)
   - AI đọc prompt từ data/prompts/cultivation_master.md
   - AI generate character background story
   - AI đưa ra 4-6 lựa chọn cho năm 1 tuổi
   - Response: {narrative, choices, state_updates}

5. Lưu vào game state:
   - character_story = response['narrative']
   - current_choices = response['choices']
   - Return game state cho frontend
```

### Phase 2: Gameplay Loop (Mỗi Năm)

```
1. User chọn lựa chọn (1-6):
   POST /game/action
   {
     "user_input": "1"  // Choice index
   }

2. Server xử lý:
   - Check game_mode == "cultivation_sim"
   - Check user_input.isdigit() → choice index
   - game_instance.process_year_turn(choice_idx)

3. process_year_turn():
   a. Validate choice index
   b. Get selected choice từ current_choices
   c. Build user_input = "Lựa chọn {index}: {choice}"
   d. Call process_turn(user_input)

4. process_turn():
   a. Build context từ ECS (player stats, location, etc.)
   b. Get character_data (age, gender, talent, race, background)
   c. Get memory context từ SimpleMemory (5 relevant memories)
   d. Call CultivationAgent.process_turn()

5. CultivationAgent.process_turn():
   a. Load system prompt từ cultivation_master.md
   b. Build prompt với:
      - Current state (HP, location, description)
      - Character info (age, gender, talent, race, background)
      - Relevant memories
      - User input (selected choice)
   c. Send to Gemini API
   d. Parse JSON response:
      {
        "narrative": "Câu chuyện năm này...",
        "choices": ["Lựa chọn 1", "Lựa chọn 2", ...],
        "action_intent": "YEAR_PROGRESS",
        "state_updates": {"age": new_age, ...}
      }
   e. Save narrative to memory
   f. Return response

6. Apply Updates:
   - Age += 1
   - Update identity.age trong ECS
   - Apply state_updates (cultivation_realm, spiritual_power, etc.)
   - Store new choices: current_choices = response['choices']

7. Return to Frontend:
   {
     "narrative": "...",
     "choices": ["...", "...", ...],
     "game_state": {...}
   }

8. Frontend hiển thị:
   - Narrative text
   - 4-6 choice buttons
   - Character stats (age, HP, etc.)
```

### Phase 3: Memory System

```
Mỗi turn, narrative được lưu vào memory:

1. MemoryManager.remember_action():
   - Content: narrative text
   - Memory type: "episodic"
   - Importance: 0.7 (high, vì là story progression)
   - Entity ID: player_id
   - Location ID: current location
   - Save ID: game save ID

2. SimpleMemory.add():
   - Insert vào memory_content table
   - Insert vào memory_metadata table
   - Trigger tự động sync vào memory_fts (FTS5)

3. Khi search context:
   - FTS5 search với BM25 ranking
   - Join với metadata để filter
   - Return top 5 relevant memories
   - Include trong prompt cho AI
```

---

## 🛠️ Công Nghệ Sử Dụng

### Backend

1. **Python 3.8+**
   - Core language

2. **FastAPI**
   - Web framework cho REST API
   - Auto-generated API docs
   - Async support

3. **SQLite + FTS5**
   - Database cho game state (ECS)
   - Full-text search cho memory system
   - WAL mode cho concurrency

4. **ECS (Entity-Component-System)**
   - Entity: Pure IDs
   - Components: StatsComponent, LocationComponent, IdentityComponent
   - Systems: Actions, Validation

5. **Google Gemini 1.5 Flash**
   - AI model cho narrative generation
   - API: `google-generativeai`
   - Model: `gemini-2.0-flash` (default)

### Frontend

1. **React 18**
   - UI framework

2. **TypeScript**
   - Type safety

3. **Vite**
   - Build tool, dev server

4. **TailwindCSS**
   - Styling

5. **Axios**
   - HTTP client cho API calls

### Memory System

1. **SQLite FTS5**
   - Full-text search engine
   - BM25 ranking
   - Porter tokenizer

2. **SimpleMemory**
   - Custom memory system
   - Rule-based compression
   - No external dependencies

---

## 📁 Cấu Trúc Code

### File Structure

```
engine/
├── games/
│   ├── base_game.py              # Base class cho tất cả games
│   └── cultivation_sim/
│       ├── __init__.py
│       └── game.py              # CultivationSimGame class
│
├── ai/
│   ├── cultivation_agent.py     # CultivationAgent - AI cho cultivation sim
│   ├── gemini_agent.py          # GeminiAgent - AI cho other games
│   └── schemas.py               # GameContext, ActionProposal, etc.
│
├── core/
│   ├── entity.py                # Entity Manager (ECS)
│   ├── components.py            # Component definitions
│   └── database.py              # SQLite wrapper
│
└── memory/
    ├── simple_memory.py         # Core memory system (FTS5)
    └── memory_manager_simple.py # High-level memory interface

data/
└── prompts/
    └── cultivation_master.md    # System prompt cho CultivationAgent

server.py                        # FastAPI server
```

### Class Hierarchy

```
BaseGame (abstract)
  ├── setup_world() [abstract]
  ├── get_game_state() [abstract]
  ├── process_turn() [concrete]
  └── apply_updates() [concrete]
      │
      └── CultivationSimGame
          ├── character_age
          ├── character_gender
          ├── character_talent
          ├── character_race
          ├── character_background
          ├── character_story
          ├── current_choices
          │
          ├── setup_world() [override]
          ├── get_game_state() [override]
          ├── process_year_turn() [new]
          └── apply_updates() [override]
```

### Data Flow

```
User Input (Choice Index)
    ↓
server.py: process_action()
    ↓
CultivationSimGame.process_year_turn()
    ↓
CultivationSimGame.process_turn()
    ↓
CultivationAgent.process_turn()
    ↓
Gemini API (with prompt)
    ↓
JSON Response {narrative, choices, state_updates}
    ↓
MemoryManager.remember_action()
    ↓
SimpleMemory.add()
    ↓
SQLite FTS5
    ↓
Return to Frontend
```

---

## 👤 Character Creation System

### Step 1: Player Selection

Người chơi chọn 4 thuộc tính:

1. **Giới Tính (Gender)**
   - `"Nam"` - Male
   - `"Nữ"` - Female

2. **Thiên Phú (Talent)**
   - `"Thiên Linh Căn"` - Heavenly Spirit Root (Top tier)
   - `"Địa Linh Căn"` - Earth Spirit Root (High tier)
   - `"Hỗn Độn Thể"` - Chaos Body (Special)
   - `"Phàm Thể"` - Mortal Body (Low tier)

3. **Chủng Tộc (Race)**
   - `"Nhân Tộc"` - Human
   - `"Yêu Tộc"` - Demon/Beast
   - `"Ma Tộc"` - Devil
   - `"Tiên Tộc"` - Immortal

4. **Bối Cảnh (Background)**
   - `"Gia Đình Tu Tiên"` - Cultivation Family
   - `"Gia Đình Phàm Nhân"` - Mortal Family
   - `"Mồ Côi"` - Orphan
   - `"Tông Môn Đệ Tử"` - Sect Disciple

### Step 2: AI Generation

```python
# API Call
POST /game/new
{
    "game_mode": "cultivation_sim",
    "player_name": "Lâm Tiêu",
    "character_data": {
        "gender": "Nam",
        "talent": "Thiên Linh Căn",
        "race": "Nhân Tộc",
        "background": "Gia Đình Tu Tiên"
    }
}

# Server Process
game_instance = CultivationSimGame()
game_instance.setup_world(
    character=character_data,
    player_name="Lâm Tiêu"
)

# AI Generation
agent = get_cultivation_agent()
context = game_instance.context_builder.build(player_id)
char_data = {
    'age': 0,
    'gender': 'Nam',
    'talent': 'Thiên Linh Căn',
    'race': 'Nhân Tộc',
    'background': 'Gia Đình Tu Tiên'
}
response = agent.process_turn("Tạo nhân vật", context, save_id, char_data)

# Response Structure
{
    "narrative": "Ngươi tên là Lâm Tiêu, con trai của tộc trưởng Lâm gia...",
    "choices": [
        "Tập trung phát triển thể chất",
        "Nghe các trưởng lão kể chuyện",
        "Chơi đùa với các đứa trẻ khác",
        "Quan sát cha mẹ tu luyện"
    ],
    "action_intent": "YEAR_PROGRESS",
    "state_updates": {}
}
```

### Step 3: Storage

Character data được lưu trong:
- `CultivationSimGame` instance (in-memory)
- ECS database (IdentityComponent, StatsComponent)
- Memory system (narrative)

---

## 📅 Age Progression System

### Age Stages

1. **Age 0 (Birth)**
   - Character creation
   - AI generates background
   - First choices for age 1

2. **Age 1-5 (Infancy/Toddler)**
   - Focus: Family interactions
   - No cultivation yet
   - Basic character development

3. **Age 6-12 (Childhood)**
   - Begin basic cultivation knowledge
   - School/education choices
   - Social interactions
   - May discover special talents

4. **Age 13-18 (Adolescence)**
   - Start actual cultivation
   - Join sects or stay with family
   - First cultivation breakthroughs
   - Romance options may appear

5. **Age 19+ (Adulthood)**
   - Full cultivation journey
   - Sect conflicts, adventures
   - Cultivation realm breakthroughs
   - Major story events

### Progression Flow

```python
# Mỗi năm:
1. Player chọn lựa chọn (1-6)
2. process_year_turn(choice_index):
   - Get selected choice
   - Call AI với choice
   - AI generate narrative cho năm đó
   - AI đưa ra choices cho năm tiếp theo
3. Age += 1
4. Update ECS (identity.age)
5. Apply state_updates (cultivation_realm, etc.)
6. Store new choices
7. Return to frontend
```

### State Updates

AI có thể update:
- `age`: Age progression (thường tự động +1)
- `cultivation_realm`: Cultivation realm (Qi Refining, Foundation Building, etc.)
- `spiritual_power`: Spiritual power (mana)
- `new_location_id`: Change location
- Custom stats theo game logic

---

## 🤖 AI Integration

### CultivationAgent

**File**: `engine/ai/cultivation_agent.py`

**Responsibilities**:
- Load cultivation-specific prompt
- Build context với character data
- Call Gemini API
- Parse JSON response
- Save to memory

### Prompt System

**File**: `data/prompts/cultivation_master.md`

**Structure**:
1. Role Definition
2. World Context (Xianxia setting)
3. Character Creation Guidelines
4. Response Format
5. Age Progression Rules
6. Cultivation System
7. Examples

### Prompt Building

```python
prompt = f"""
CURRENT STATE:
- Player: {context.player_name} (HP: {context.player_hp}/{context.player_max_hp})
- Location: {context.current_room_id}
- Description: {context.room_description}

CHARACTER INFO:
- Age: {character_data.get('age', 0)}
- Gender: {character_data.get('gender', 'Unknown')}
- Talent: {character_data.get('talent', 'Unknown')}
- Race: {character_data.get('race', 'Unknown')}
- Background: {character_data.get('background', 'Unknown')}

RELEVANT MEMORIES (Context from past turns):
{memory_context}

USER INPUT: "{user_input}"

QUAN TRỌNG: 
- Khi player chọn một lựa chọn, mô tả những gì xảy ra trong năm đó
- Sau đó đưa ra 4-6 lựa chọn cho năm tiếp theo
- KHÔNG BAO GIỜ kết thúc bằng câu hỏi tu từ
- Cho thông tin cụ thể về những gì xảy ra

Generate the JSON response with format:
{{
  "narrative": "Câu chuyện năm này...",
  "choices": ["Lựa chọn 1", "Lựa chọn 2", "Lựa chọn 3", "Lựa chọn 4"],
  "action_intent": "YEAR_PROGRESS",
  "state_updates": {{"age": new_age, ...}}
}}
"""
```

### Response Format

```json
{
  "narrative": "Năm 5 tuổi, ngươi đã trở thành một đứa trẻ thông minh...",
  "choices": [
    "Tập trung học văn hóa và lịch sử tu tiên",
    "Chơi đùa với các đứa trẻ khác trong tộc",
    "Thầm lén quan sát các đệ tử lớn tu luyện",
    "Giúp đỡ cha mẹ trong công việc hàng ngày",
    "Khám phá khu rừng phía sau tộc",
    "Học cách chế tạo đan dược cơ bản"
  ],
  "action_intent": "YEAR_PROGRESS",
  "state_updates": {
    "age": 6,
    "spiritual_power": 5
  }
}
```

---

## 💾 Memory System

### SimpleMemory

**File**: `engine/memory/simple_memory.py`

**Technology**: SQLite FTS5

**Tables**:
1. `memory_content` - Store narrative content
2. `memory_metadata` - Store metadata (age, location, importance, etc.)
3. `memory_fts` - FTS5 virtual table for search

### Memory Flow

```
1. Narrative generated by AI
   ↓
2. MemoryManager.remember_action()
   - Determine importance (0.7 for cultivation sim)
   - Extract entity_id, location_id
   ↓
3. SimpleMemory.add()
   - Insert into memory_content
   - Insert into memory_metadata
   - Trigger auto-syncs to memory_fts
   ↓
4. When searching context:
   - FTS5 search với BM25 ranking
   - Join với metadata
   - Filter by save_id, location_id
   - Return top 5 results
   ↓
5. Include in AI prompt
```

### Memory Schema

```sql
-- Content table
CREATE TABLE memory_content (
    memory_id TEXT PRIMARY KEY,
    content TEXT NOT NULL
)

-- Metadata table
CREATE TABLE memory_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT UNIQUE,
    entity_id INTEGER,
    location_id TEXT,
    save_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    importance REAL DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    metadata_json TEXT
)

-- FTS5 table
CREATE VIRTUAL TABLE memory_fts USING fts5(
    memory_id UNINDEXED,
    content,
    memory_type,
    tokenize='porter'
)
```

---

## 🌐 API Endpoints

### 1. Create New Game

```http
POST /game/new
Content-Type: application/json

{
    "player_name": "Lâm Tiêu",
    "game_mode": "cultivation_sim",
    "character_data": {
        "gender": "Nam",
        "talent": "Thiên Linh Căn",
        "race": "Nhân Tộc",
        "background": "Gia Đình Tu Tiên"
    }
}

Response:
{
    "message": "Game started",
    "save_id": "cultivation_sim_20251203_123456",
    "game_mode": "cultivation_sim",
    "game_state": {
        "player_name": "Lâm Tiêu",
        "age": 0,
        "gender": "Nam",
        "talent": "Thiên Linh Căn",
        "race": "Nhân Tộc",
        "background": "Gia Đình Tu Tiên",
        "character_story": "Ngươi tên là Lâm Tiêu...",
        "current_choices": [
            "Tập trung phát triển thể chất",
            "Nghe các trưởng lão kể chuyện",
            ...
        ],
        "player_hp": 10,
        "player_max_hp": 10,
        "current_location": "birthplace",
        "room_description": "..."
    }
}
```

### 2. Process Action (Select Choice)

```http
POST /game/action
Content-Type: application/json

{
    "user_input": "1"  // Choice index (1-6)
}

Response:
{
    "narrative": "Năm 1 tuổi, ngươi đã bắt đầu...",
    "action_intent": "YEAR_PROGRESS",
    "choices": [
        "Lựa chọn 1",
        "Lựa chọn 2",
        "Lựa chọn 3",
        "Lựa chọn 4"
    ],
    "game_state": {
        "age": 1,
        "player_hp": 10,
        ...
    }
}
```

### 3. Get Game State

```http
GET /game/state

Response:
{
    "player_name": "Lâm Tiêu",
    "age": 5,
    "gender": "Nam",
    "talent": "Thiên Linh Căn",
    "race": "Nhân Tộc",
    "background": "Gia Đình Tu Tiên",
    "character_story": "...",
    "current_choices": [...],
    "player_hp": 10,
    "player_max_hp": 10,
    "current_location": "birthplace",
    "room_description": "..."
}
```

### 4. Load Game

```http
POST /game/load
Content-Type: application/json

{
    "save_id": "cultivation_sim_20251203_123456"
}

Response:
{
    "message": "Game loaded",
    "save_id": "cultivation_sim_20251203_123456",
    "game_mode": "cultivation_sim",
    "game_state": {...}
}
```

### 5. List Saves

```http
GET /game/saves

Response:
{
    "saves": [
        "cultivation_sim_20251203_123456",
        "cultivation_sim_20251203_234567"
    ]
}
```

---

## 📝 Ví Dụ Sử Dụng

### Example 1: Complete Game Flow

```python
# 1. Create Character
POST /game/new
{
    "game_mode": "cultivation_sim",
    "player_name": "Lâm Tiêu",
    "character_data": {
        "gender": "Nam",
        "talent": "Thiên Linh Căn",
        "race": "Nhân Tộc",
        "background": "Gia Đình Tu Tiên"
    }
}

# Response: Character created, age 0, choices for age 1

# 2. Select Choice for Age 1
POST /game/action
{"user_input": "1"}

# Response: Narrative for age 1, choices for age 2

# 3. Continue...
POST /game/action
{"user_input": "3"}

# Response: Narrative for age 2, choices for age 3

# ... Continue until cultivation master or death
```

### Example 2: Frontend Integration

```typescript
// React Component
const CultivationSim = () => {
  const [gameState, setGameState] = useState(null);
  const [choices, setChoices] = useState([]);
  
  // Create game
  const createGame = async () => {
    const response = await axios.post('/game/new', {
      game_mode: 'cultivation_sim',
      player_name: 'Lâm Tiêu',
      character_data: {
        gender: 'Nam',
        talent: 'Thiên Linh Căn',
        race: 'Nhân Tộc',
        background: 'Gia Đình Tu Tiên'
      }
    });
    
    setGameState(response.data.game_state);
    setChoices(response.data.game_state.current_choices);
  };
  
  // Select choice
  const selectChoice = async (index: number) => {
    const response = await axios.post('/game/action', {
      user_input: String(index + 1)
    });
    
    setGameState(response.data.game_state);
    setChoices(response.data.choices);
  };
  
  return (
    <div>
      <h1>{gameState?.player_name} - Age {gameState?.age}</h1>
      <p>{gameState?.character_story}</p>
      <div>
        {choices.map((choice, index) => (
          <button key={index} onClick={() => selectChoice(index)}>
            {choice}
          </button>
        ))}
      </div>
    </div>
  );
};
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash  # Optional, default
```

### Database

- **Location**: `data/saves/{save_id}.db`
- **Format**: SQLite
- **Tables**: ECS tables + Memory tables

### Memory Settings

- **Max memories**: 10,000 (configurable)
- **Compression threshold**: 8,000
- **Search results**: 5 (for context)

---

## 📊 Performance

### Benchmarks

- **AI Response Time**: ~2-5 seconds (Gemini API)
- **Memory Search**: <10ms (FTS5)
- **Database Operations**: <5ms (SQLite WAL mode)
- **Memory Usage**: ~15MB (for 10K memories)

### Optimization

1. **Memory System**: FTS5 với BM25 ranking
2. **Database**: WAL mode cho concurrency
3. **AI**: Caching prompt, batching requests (future)
4. **Frontend**: React state management

---

## 🐛 Troubleshooting

### Common Issues

1. **AI không trả về choices**
   - Check prompt format
   - Verify JSON parsing
   - Check API key

2. **Memory không lưu**
   - Check database permissions
   - Verify save_id
   - Check trigger sync

3. **Age không tăng**
   - Check process_year_turn()
   - Verify state_updates
   - Check ECS update

---

## 📚 References

- **System Prompt**: `data/prompts/cultivation_master.md`
- **Base Game**: `engine/games/base_game.py`
- **Cultivation Game**: `engine/games/cultivation_sim/game.py`
- **Cultivation Agent**: `engine/ai/cultivation_agent.py`
- **Memory System**: `engine/memory/simple_memory.py`
- **API Server**: `server.py`

---

**Version**: 1.0  
**Last Updated**: 2025-12-03  
**Author**: Game Engine Team

