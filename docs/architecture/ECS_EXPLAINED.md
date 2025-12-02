# 📚 ECS Architecture - Giải Thích Chi Tiết

## 1. ECS Là Gì?

**ECS (Entity-Component-System)** là một design pattern tách biệt hoàn toàn:
- **Dữ liệu** (Components)
- **Logic** (Systems)  
- **Định danh** (Entities)

Khác với lập trình hướng đối tượng (OOP) truyền thống nơi dữ liệu và hành vi được đóng gói cùng nhau trong classes.

---

## 2. Tại Sao Dùng ECS Cho Text Adventure?

### ❌ Vấn Đề Với OOP Truyền Thống

Trong OOP, bạn có thể thiết kế như này:

```python
class GameObject:
    def __init__(self, name):
        self.name = name

class Door(GameObject):
    def __init__(self, name, is_locked=False):
        super().__init__(name)
        self.is_locked = is_locked
    
    def open(self):
        if self.is_locked:
            return "Cửa bị khóa!"
        return "Bạn mở cửa."

class NPC(GameObject):
    def __init__(self, name, dialogue):
        super().__init__(name)
        self.dialogue = dialogue
    
    def talk(self):
        return self.dialogue
```

**Vấn đề:**
1. **Rigid hierarchy**: Nếu muốn Door có thể nói chuyện (như Talking Door trong game), phải tạo class mới hoặc multiple inheritance (phức tạp).
2. **Code duplication**: Nhiều class cần chung logic (ví dụ: có vị trí, có thể bị phá hủy).
3. **Khó mở rộng**: Mỗi tính năng mới = phải refactor classes.

### ✅ Giải Pháp Với ECS

Trong ECS:
- **Door** = Entity ID + `StateComponent(is_locked=True)` + `DescriptionComponent`
- **NPC** = Entity ID + `DialogueComponent` + `AIComponent`
- **Talking Door** = Entity ID + `StateComponent` + `DialogueComponent` (mix & match!)

➜ **Linh hoạt tuyệt đối**: Chỉ cần gắn/gỡ Components!

---

## 3. Kiến Trúc ECS Chi Tiết

### 3.1 Entity (Thực Thể)

**Entity chỉ là một ID duy nhất**. Không chứa data, không chứa logic.

```python
# Entity chỉ là integer hoặc UUID
entity_player = 1
entity_door = 2
entity_sword = 3
```

Trong database:
```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY,
    label TEXT  -- "player", "door_main_hall", etc. (for debugging)
);
```

### 3.2 Component (Thành Phần Dữ Liệu)

**Component là struct thuần túy chứa data**. Không có methods (ngoài `__init__`).

#### Ví dụ Components cho Text Adventure:

```python
from pydantic import BaseModel
from typing import List, Optional

# 1. Identity - Định danh cơ bản
class IdentityComponent(BaseModel):
    name: str
    description: str

# 2. Location - Vị trí trong thế giới
class LocationComponent(BaseModel):
    zone_id: str        # "dungeon_level_1"
    room_id: str        # "entrance_hall"
    x: int = 0
    y: int = 0

# 3. State - Trạng thái vật lý
class StateComponent(BaseModel):
    is_locked: bool = False
    is_open: bool = False
    is_broken: bool = False
    is_lit: bool = False

# 4. Inventory - Túi đồ
class InventoryComponent(BaseModel):
    items: List[int] = []  # List of entity IDs
    capacity: int = 20

# 5. Stats - Chỉ số nhân vật
class StatsComponent(BaseModel):
    hp: int = 100
    max_hp: int = 100
    strength: int = 10
    intelligence: int = 10

# 6. Dialogue - Khả năng nói chuyện
class DialogueComponent(BaseModel):
    greeting: str
    topics: dict = {}  # {"quest": "I need help!", ...}

# 7. AI - Hành vi NPC
class AIComponent(BaseModel):
    behavior_type: str  # "passive", "aggressive", "trader"
    aggro_range: int = 5
```

#### Lưu trữ trong SQLite:

```sql
CREATE TABLE components (
    entity_id INTEGER,
    component_type TEXT,  -- "location", "stats", "inventory"...
    data TEXT,            -- JSON serialized
    PRIMARY KEY (entity_id, component_type),
    FOREIGN KEY (entity_id) REFERENCES entities(id)
);
```

**Ví dụ:**
```sql
-- Player entity
INSERT INTO components VALUES (1, 'identity', '{"name": "Hero", "description": "A brave adventurer"}');
INSERT INTO components VALUES (1, 'location', '{"zone_id": "dungeon_1", "room_id": "entrance", "x": 0, "y": 0}');
INSERT INTO components VALUES (1, 'stats', '{"hp": 100, "max_hp": 100, "strength": 15}');
INSERT INTO components VALUES (1, 'inventory', '{"items": [3], "capacity": 20}');

-- Door entity
INSERT INTO components VALUES (2, 'identity', '{"name": "Oak Door", "description": "A sturdy door"}');
INSERT INTO components VALUES (2, 'location', '{"zone_id": "dungeon_1", "room_id": "entrance", "x": 1, "y": 0}');
INSERT INTO components VALUES (2, 'state', '{"is_locked": true, "is_open": false}');
```

### 3.3 System (Hệ Thống Xử Lý)

**System chứa toàn bộ logic**. System quét qua entities và xử lý những entity có components mà nó quan tâm.

#### Ví dụ: Movement System

```python
class MovementSystem:
    """System xử lý di chuyển"""
    
    def move_entity(self, entity_id: int, direction: str):
        # 1. Lấy LocationComponent của entity
        location = db.get_component(entity_id, LocationComponent)
        if not location:
            return False, "Entity không có vị trí"
        
        # 2. Tính toán vị trí mới
        new_x, new_y = location.x, location.y
        if direction == "north":
            new_y += 1
        elif direction == "south":
            new_y -= 1
        elif direction == "east":
            new_x += 1
        elif direction == "west":
            new_x -= 1
        
        # 3. Kiểm tra obstacle
        blocked = self._check_collision(location.room_id, new_x, new_y)
        if blocked:
            return False, "Đường bị chặn"
        
        # 4. Cập nhật component
        location.x = new_x
        location.y = new_y
        db.update_component(entity_id, location)
        
        return True, f"Di chuyển tới ({new_x}, {new_y})"
    
    def _check_collision(self, room_id, x, y):
        # Tìm tất cả entities ở vị trí (x, y) trong room
        entities = db.get_entities_at_location(room_id, x, y)
        for entity in entities:
            # Nếu có StateComponent và không phải "passable"
            state = db.get_component(entity, StateComponent)
            if state and not state.is_open:
                return True  # Blocked
        return False
```

#### Ví dụ: Inventory System

```python
class InventorySystem:
    """System quản lý inventory"""
    
    def take_item(self, player_id: int, item_id: int):
        # 1. Get player's inventory
        player_inv = db.get_component(player_id, InventoryComponent)
        if not player_inv:
            return False, "Player không có inventory"
        
        # 2. Check capacity
        if len(player_inv.items) >= player_inv.capacity:
            return False, "Túi đồ đầy"
        
        # 3. Check if item exists and is in same location
        player_loc = db.get_component(player_id, LocationComponent)
        item_loc = db.get_component(item_id, LocationComponent)
        
        if not item_loc or item_loc.room_id != player_loc.room_id:
            return False, "Vật phẩm không ở đây"
        
        # 4. Add item to inventory
        player_inv.items.append(item_id)
        db.update_component(player_id, player_inv)
        
        # 5. Remove item's location (nó giờ trong túi, không ở thế giới)
        db.remove_component(item_id, LocationComponent)
        
        return True, "Đã nhặt vật phẩm"
```

#### Ví dụ: Precondition Validation System (Quan Trọng!)

```python
class PreconditionSystem:
    """
    Hệ thống kiểm tra điều kiện tiên quyết.
    Đây là "gatekeeper" - LLM đề xuất action, system này validate.
    """
    
    def validate_open_door(self, player_id: int, door_id: int):
        """Kiểm tra xem player có thể mở cửa không"""
        
        # Check 1: Cửa có tồn tại không?
        door_identity = db.get_component(door_id, IdentityComponent)
        if not door_identity:
            return False, "ERR_NOT_FOUND", "Không có cửa nào ở đây"
        
        # Check 2: Cửa có ở cùng room không?
        player_loc = db.get_component(player_id, LocationComponent)
        door_loc = db.get_component(door_id, LocationComponent)
        
        if door_loc.room_id != player_loc.room_id:
            return False, "ERR_TOO_FAR", "Cửa quá xa"
        
        # Check 3: Cửa đã mở chưa?
        door_state = db.get_component(door_id, StateComponent)
        if door_state.is_open:
            return False, "ERR_ALREADY_OPEN", "Cửa đã mở rồi"
        
        # Check 4: Cửa có bị khóa không?
        if door_state.is_locked:
            # Check if player has key
            player_inv = db.get_component(player_id, InventoryComponent)
            has_key = self._check_has_key(player_inv.items, door_id)
            
            if not has_key:
                return False, "ERR_LOCKED_NO_KEY", "Cửa bị khóa, cần chìa khóa"
        
        # All checks passed
        return True, "OK", "Có thể mở cửa"
    
    def _check_has_key(self, items, door_id):
        # Logic kiểm tra key (tìm item có KeyComponent match door)
        for item_id in items:
            key_comp = db.get_component(item_id, KeyComponent)
            if key_comp and key_comp.unlocks_door_id == door_id:
                return True
        return False
```

---

## 4. Luồng Hoạt Động Hoàn Chỉnh

### Scenario: Player muốn mở cửa

```
User Input: "Open the wooden door"
    ↓
[AI Agent] Parse → JSON ActionProposal
    {
        "intent": "OPEN",
        "target_id": 42,  // entity_id of door
        "tool_id": null
    }
    ↓
[PreconditionSystem] Validate
    → Check door exists ✅
    → Check same room ✅
    → Check not already open ✅
    → Check if locked → need key ❌
    → RETURN: False, "ERR_LOCKED_NO_KEY"
    ↓
[ActionExecutor] Don't execute (validation failed)
    ↓
[NarrativeGenerator] Generate failure text
    Input: ActionResult(success=False, reason="ERR_LOCKED_NO_KEY")
    AI Prompt: "Player tried to open door but it's locked and they have no key. Describe."
    Output: "You try the handle, but the door is locked tight. You'll need to find a key."
    ↓
[UI] Display to player
```

**Nếu player có key:**
```
[PreconditionSystem] Validate
    → All checks pass ✅
    → RETURN: True, "OK"
    ↓
[ActionExecutor] Execute
    → Update door's StateComponent: is_open = True
    → RETURN: ActionResult(success=True)
    ↓
[NarrativeGenerator] Generate success text
    Input: ActionResult(success=True, action="OPEN", target="wooden door")
    AI Output: "You insert the rusty key and turn it. The lock clicks open with a satisfying sound."
```

---

## 5. Tại Sao Đây Là "Single Source of Truth"?

### ❌ Nếu LLM có quyền trực tiếp:
```python
# BAD: LLM tự do thay đổi state
llm_output = "You walk through the wall and find treasure."
# → Vô lý! Player đi xuyên tường!
```

### ✅ Với ECS + Validation:
```python
# GOOD: LLM chỉ đề xuất
proposal = ActionProposal(intent="MOVE", direction="east")

# Engine validate
wall_exists = check_obstacle(player.x + 1, player.y)
if wall_exists:
    return False, "Có tường chắn"

# Nếu pass → execute
# Nếu fail → LLM tạo narrative từ error code
```

➜ **Engine = Truth, LLM = Storyteller dựa trên truth**

---

## 6. Code Structure Thực Tế

```
engine/
├── core/
│   ├── entity.py          # EntityManager class
│   ├── components.py      # Tất cả Component definitions
│   └── database.py        # SQLite wrapper
├── systems/
│   ├── movement.py        # MovementSystem
│   ├── inventory.py       # InventorySystem
│   ├── combat.py          # CombatSystem
│   └── validation.py      # PreconditionSystem
├── ai/
│   ├── schemas.py         # ActionProposal, ActionResult
│   ├── gemini.py          # Gemini Agent
│   └── router.py          # Hybrid router
└── game_loop.py           # Main loop
```

---

## 7. Lợi Ích Cụ Thể

### 7.1 Dễ Mở Rộng
Muốn thêm hệ thống "weather"?
1. Tạo `WeatherComponent(temperature, rain, wind)`
2. Tạo `WeatherSystem` process tác động
3. **KHÔNG CẦN** sửa code cũ!

### 7.2 Performance
- Query nhanh: `SELECT * FROM components WHERE entity_id=? AND component_type='location'`
- Cache-friendly: Components là data thuần, dễ serialize

### 7.3 Save/Load Game
```python
# Save = dump toàn bộ components ra JSON
save_data = db.dump_all_components()
with open('savegame.json', 'w') as f:
    json.dump(save_data, f)

# Load = restore components
with open('savegame.json') as f:
    data = json.load(f)
    db.restore_components(data)
```

### 7.4 Multiplayer-Ready (Future)
Mỗi player = entity riêng với components riêng. Systems xử lý song song.

---

## 8. So Sánh Với Game Nổi Tiếng

| Game | Architecture | Tại Sao |
|------|--------------|---------|
| **Dwarf Fortress** | ECS-like | Quản lý hàng nghìn entities (dwarf, item, tile) |
| **Unity Engine** | Pure ECS | Transform, Mesh, Collider đều là Components |
| **Minecraft** | Tile-based + ECS | Mobs = entities, blocks = components |
| **Rimworld** | ECS | Colonist, animal, item = entities với components khác nhau |

---

## 🎯 Tóm Tắt

**ECS cho phép:**
- ✅ Mix & match tính năng thoải mái (Talking Door, Flying Sword, ...)
- ✅ Engine kiểm soát tuyệt đối state → No hallucination
- ✅ Easy save/load, easy debug
- ✅ Scale tốt (hàng nghìn entities)

**Trong text adventure của chúng ta:**
- **Entities** = Player, NPCs, Doors, Items, Rooms
- **Components** = Location, Stats, Inventory, Dialogue, State
- **Systems** = Movement, Combat, Inventory, Precondition Validation

**Workflow:**
```
Player Input → AI Parse → Proposal → Validate → Execute → Narrate → Display
              (JSON)      (Check)    (Update DB) (AI)     (UI)
```

---

Bạn đã hiểu rõ ECS chưa? Có câu hỏi gì không trước khi tôi bắt đầu code Phase 1?
