# Hướng Dẫn Sử Dụng: Artifacts, Items, Regional Cultures

## 1. Load Dữ Liệu

Dữ liệu đã được tự động load khi khởi tạo `WorldDatabase`:

```python
from world_database import WorldDatabase

# Khởi tạo World Database (tự động load tất cả JSON files)
world_db = WorldDatabase("data")

# Kiểm tra đã load bao nhiêu items
print(f"Loaded: {len(world_db.artifacts)} artifacts")
print(f"Loaded: {len(world_db.items)} items")
print(f"Loaded: {len(world_db.regional_cultures)} regional cultures")
```

## 2. Truy Xuất Vật Phẩm (Items)

### 2.1. Lấy thông tin item bằng ID

```python
# Lấy thông tin item
item = world_db.get_item("pill_breakthrough_foundation")

if item:
    print(f"Nhặt được: {item['name']}")
    print(f"Công dụng: {item['lore']}")
    print(f"Hiệu ứng: {item['effect']}")
    print(f"Độc tính: {item.get('toxicity', 0)}")
```

### 2.2. Lấy items theo loại

```python
# Lấy tất cả pills
pills = world_db.get_items_by_type("Pill")
for pill in pills:
    print(f"- {pill['name']}: {pill['effect']}")

# Lấy tất cả materials
materials = world_db.get_items_by_type("Material")
for mat in materials:
    print(f"- {mat['name']}: Grade {mat.get('grade', 1)}")
```

### 2.3. Lấy materials tại một location

```python
# Lấy materials có thể tìm thấy ở location
materials = world_db.get_materials_by_location("loc_mountain_02")
for mat in materials:
    print(f"- {mat['name']}: {mat.get('lore', '')}")
```

### 2.4. Sử dụng Item System

```python
from item_system import ItemSystem

item_system = ItemSystem(world_db)

# Sử dụng item
player_state = {
    "cultivation": {
        "spiritual_power": 50,
        "max_spiritual_power": 100
    }
}

result = item_system.use_item("pill_qi_gathering", player_state)
print(result["message"])  # "Tăng 50 linh khí (Tích độc +5)"
print(f"Effect: {result['effect_applied']}")
print(f"Toxicity: +{result['toxicity_added']}")
```

## 3. Truy Xuất Pháp Bảo (Artifacts)

### 3.1. Lấy thông tin artifact bằng ID

```python
# Lấy thông tin artifact
artifact = world_db.get_artifact("spirit_tool_fire_blade")

if artifact:
    print(f"Pháp bảo: {artifact['name']}")
    print(f"Cấp bậc: {artifact['tier']}")
    print(f"Yêu cầu cảnh giới: {artifact['realm_requirement']}")
    print(f"Tấn công: {artifact['stats']['attack']}")
    print(f"Lịch sử: {artifact['lore']}")
```

### 3.2. Lấy artifacts theo tier

```python
# Lấy tất cả Spirit Tools
spirit_tools = world_db.get_artifacts_by_tier("Spirit_Tool")
for tool in spirit_tools:
    print(f"- {tool['name']}: {tool['stats']['attack']} ATK")
```

### 3.3. Lấy artifacts theo realm requirement

```python
# Lấy artifacts dùng được ở Foundation realm
foundation_artifacts = world_db.get_artifacts_by_realm("Foundation")
for artifact in foundation_artifacts:
    print(f"- {artifact['name']}: {artifact['tier']}")
```

### 3.4. Tính sát thương với Artifact System

```python
from artifact_system import ArtifactSystem

artifact_system = ArtifactSystem(world_db)

# Player stats
player_stats = {
    "element": "Fire",
    "current_qi": 80,
    "max_qi": 100,
    "target_type": "normal"
}

# Tính damage
damage_result = artifact_system.calculate_artifact_damage(
    player_stats=player_stats,
    artifact_id="spirit_tool_fire_blade",
    target_defense=20
)

print(f"Tổng sát thương: {damage_result['total_damage']}")
print(f"Chi tiết: {damage_result['damage_breakdown']}")
# Output: "Base: 45 × 1.2 (Element) + 8.0 (Qi Power) - 20 (Defense) = 42"
```

### 3.5. Kiểm tra có thể dùng artifact không

```python
# Check requirements
check = world_db.check_artifact_requirements(
    artifact_id="magic_treasure_phoenix_blade",
    current_realm="Foundation",
    attributes={"INT": 50, "CON": 40}
)

if check["can_use"]:
    print("Có thể sử dụng!")
else:
    print(f"Thiếu: {check['missing_requirements']}")
```

## 4. Văn Hóa Khu Vực (Regional Cultures)

### 4.1. Lấy thông tin văn hóa vùng

```python
# Lấy văn hóa vùng
culture = world_db.get_regional_culture("region_central_plains")

if culture:
    print(f"Vùng: {culture['name']}")
    print(f"Không khí: {culture['vibe']}")
    print(f"Quy tắc xã hội: {culture['social_rules']}")
    print(f"Đặc điểm: {[t['effect'] for t in culture['cultural_traits']]}")
```

### 4.2. Lấy văn hóa từ location

```python
# Lấy văn hóa của location hiện tại
location_id = "loc_village_01"
culture = world_db.get_culture_by_location(location_id)

if culture:
    print(f"Bạn đang ở vùng: {culture['name']}")
    print(f"NPC ở đây sẽ: {culture['vibe']}")
```

### 4.3. Tạo NPC behavior dựa trên văn hóa

```python
# Generate NPC behavior
npc_behavior = world_db.get_npc_behavior(
    region_id="region_northern_tundra",
    player_reputation=1500,  # Cao
    player_realm="Golden_Core"
)

print(f"Thái độ: {npc_behavior['attitude']}")  # "Respectful"
print(f"Cách chào: {npc_behavior['greeting']}")  # "Show weapon or aura"
print(f"Hoạt động đặc biệt: {npc_behavior['unique_activities']}")
```

### 4.4. Ví dụ: NPC ở Trung Châu vs Bắc Hoang

```python
# NPC ở Trung Châu (văn minh)
central_plains = world_db.get_npc_behavior(
    region_id="region_central_plains",
    player_reputation=100,
    player_realm="Foundation"
)
# → "Polite" - Giữ kẽ, tôn trọng lễ nghi

# NPC ở Bắc Hoang (hoang dã)
northern_tundra = world_db.get_npc_behavior(
    region_id="region_northern_tundra",
    player_reputation=100,
    player_realm="Foundation"
)
# → "Aggressive_Test" - Thách đấu trực tiếp
```

## 5. Tích Hợp Vào Game Logic

### 5.1. Trong Character Creation

```python
# Khi tạo nhân vật, set location và load culture
game.current_location_id = "loc_village_01"
location_data = game._get_location_data()

# Location data đã bao gồm culture info
if "culture" in location_data:
    culture = location_data["culture"]
    print(f"Bạn sinh ra ở: {location_data['name']}")
    print(f"Văn hóa: {culture['vibe']}")
```

### 5.2. Trong AI Prompts

```python
# AI agent tự động thêm regional culture vào prompt
character_data = {
    "location_id": "loc_village_01",
    # ... other data
}

# Agent sẽ tự động load culture và thêm vào prompt
response = agent.process_turn(character_data=character_data)
# → Prompt sẽ có thông tin về văn hóa vùng
```

### 5.3. Khi Player nhặt item

```python
# Khi player nhặt item
item_id = "pill_breakthrough_foundation"
item = world_db.get_item(item_id)

if item:
    # Add to inventory
    player.inventory.add(item_id, quantity=1)
    
    # Show notification
    print(f"✨ Nhặt được: {item['name']}")
    print(f"   {item['lore']}")
    
    # Show effect
    if item['type'] == 'Pill':
        effect = item['effect']
        print(f"   Hiệu ứng: {effect['target']} +{effect['value']}")
```

### 5.4. Khi Player sử dụng artifact

```python
# Khi player tấn công với artifact
artifact_id = "spirit_tool_fire_blade"
player_stats = {
    "element": "Fire",
    "current_qi": 80,
    "max_qi": 100
}

damage = artifact_system.calculate_artifact_damage(
    player_stats=player_stats,
    artifact_id=artifact_id,
    target_defense=20
)

print(f"Bạn tấn công với {artifact['name']}: {damage['total_damage']} dmg")
```

## 6. Ví Dụ Hoàn Chỉnh: NPC Interaction

```python
def interact_with_npc(npc_id, player, world_db):
    """Ví dụ tương tác với NPC dựa trên văn hóa vùng"""
    
    # Get player location
    location_id = player.current_location_id
    culture = world_db.get_culture_by_location(location_id)
    
    if not culture:
        return "NPC không có phản ứng đặc biệt."
    
    # Get NPC behavior
    behavior = world_db.get_npc_behavior(
        region_id=culture['region_id'],
        player_reputation=player.reputation,
        player_realm=player.cultivation.realm
    )
    
    # Generate interaction based on culture
    if behavior['attitude'] == "Polite":
        greeting = "NPC cúi đầu chào bạn một cách lịch sự."
    elif behavior['attitude'] == "Aggressive_Test":
        greeting = "NPC nhìn bạn với ánh mắt thách thức: 'Muốn đánh không?'"
    elif behavior['attitude'] == "Respectful":
        greeting = "NPC tỏ ra tôn trọng: 'Đạo hữu, xin mời vào lều uống rượu.'"
    else:
        greeting = "NPC nhìn bạn một cách bình thường."
    
    return greeting
```

## 7. Tìm Kiếm (Search)

```python
# Tìm kiếm theo tên (fuzzy search)
results = world_db.search_by_name("rồng")

print(f"Artifacts: {[a['name'] for a in results['artifacts']]}")
print(f"Items: {[i['name'] for i in results['items']]}")
# → ["Vảy Rồng Đất", "Trảm Long Kiếm", ...]
```

## 8. Lưu Ý

1. **Tất cả dữ liệu được load vào RAM** khi khởi tạo `WorldDatabase` → O(1) lookup
2. **Không cần database** → Chỉ cần JSON files
3. **Modding-friendly** → Chỉ cần sửa JSON, không cần sửa code
4. **Tự động tích hợp** → `game.py` và `agent.py` đã tự động sử dụng các hệ thống này

## 9. File Structure

```
cultivation-sim/
├── data/
│   ├── artifacts.json          # Pháp bảo
│   ├── items.json              # Vật phẩm
│   ├── regional_cultures.json  # Văn hóa vùng
│   ├── sects.json
│   ├── techniques.json
│   ├── races.json
│   ├── clans.json
│   └── locations.json
├── world_database.py           # Load và quản lý dữ liệu
├── artifact_system.py         # Logic pháp bảo
├── item_system.py             # Logic vật phẩm
└── game.py                    # Tích hợp vào game
```

