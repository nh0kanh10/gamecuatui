# 🌏 World Database - Thiên Nguyên Giới

> **Dữ liệu thế giới cho Cultivation Simulator**  
> **Format**: JSON-based, Modding-friendly  
> **Architecture**: Entity-Component compatible

---

## 📁 Cấu Trúc Dữ Liệu

### 1. **Sects** (`data/sects.json`)
Tông môn với requirements, exclusive techniques, resources.

**Fields**:
- `id`: Unique identifier
- `name`: Tên tông môn
- `type`: Righteous / Demonic / Neutral
- `alignment`: Lawful Good / Chaotic Evil / etc.
- `requirements`: Min attributes, preferred/forbidden traits
- `exclusive_techniques`: List technique IDs
- `resources`: Specialty, wealth rating
- `sect_hierarchy`: Ranks, promotion requirements

**Usage**:
```python
from world_database import WorldDatabase

db = WorldDatabase("data")
sect = db.get_sect("sect_001")
eligible = db.check_sect_requirements("sect_001", attributes, traits)
```

---

### 2. **Techniques** (`data/techniques.json`)
Công pháp với modifiers và special abilities.

**Fields**:
- `id`: Unique identifier
- `name`: Tên công pháp
- `type`: Cultivation / Combat
- `tier`: Foundation / Golden_Core / etc.
- `element`: Pure / Blood / Ice / etc.
- `requirements`: Min realm, attributes, sect
- `effects`: Modifiers (cultivation_speed, damage, etc.)
- `special_abilities`: List special skills

**Usage**:
```python
tech = db.get_technique("tech_taiqing_01")
can_learn = db.check_technique_requirements("tech_taiqing_01", realm, attributes, sect_id)
```

---

### 3. **Races** (`data/races.json`)
Chủng tộc với base stats và growth modifiers.

**Fields**:
- `id`: Unique identifier
- `name`: Tên chủng tộc
- `base_stats`: CON, INT, PER, LUK, CHA, KAR
- `growth_modifiers`: Multipliers for stats
- `traits`: List racial traits
- `rarity`: Optional (for rare races)

**Usage**:
```python
race = db.get_race("race_dragon_blood")
base_stats = db.get_race_base_stats("race_dragon_blood")
growth = db.get_race_growth_modifiers("race_dragon_blood")
```

---

### 4. **Clans** (`data/clans.json`)
Gia tộc với starting perks và relationships.

**Fields**:
- `id`: Unique identifier
- `name`: Tên gia tộc
- `tier`: Noble / Declining / Merchant / etc.
- `specialty`: Alchemy / Fire / Trade / etc.
- `starting_perks`: Spirit stones, items, reputation, connections
- `rivals` / `allies`: Relationship network
- `flag_events`: Special events (Engagement_Annulment, etc.)

**Usage**:
```python
clan = db.get_clan("clan_lin")
perks = db.get_clan_starting_perks("clan_lin")
relationships = db.get_clan_relationships("clan_lin")
```

---

### 5. **Locations** (`data/locations.json`)
Địa danh với level range, danger, services.

**Fields**:
- `id`: Unique identifier
- `name`: Tên địa điểm
- `type`: Village / City / Sect / Wilderness / Forbidden Zone
- `region`: Trung Châu / Bắc Hoang / Nam Cương / etc.
- `qi_density`: Mật độ linh khí (0-10)
- `level_range`: [min, max] recommended level
- `danger_level`: Safe / Low / Medium / High / Extreme
- `services`: List services (auction_house, blacksmith, etc.)
- `connected_to`: List location IDs
- `loot_table`: Optional (for dungeons)
- `debuffs`: Optional (for dangerous areas)

**Usage**:
```python
loc = db.get_location("loc_city_01")
can_access = db.can_access_location("loc_forbidden_01", realm, attributes)
connected = db.get_connected_locations("loc_city_01")
```

---

## 🔧 Integration với Game Systems

### Attributes Component
```python
from attributes import AttributesComponent
from world_database import WorldDatabase

db = WorldDatabase("data")
race = db.get_race("race_dragon_blood")

# Apply base stats
attrs = AttributesComponent(**race["base_stats"])

# Apply growth modifiers
growth = race["growth_modifiers"]
attrs.con *= growth.get("CON", 1.0)
```

### Breakthrough Mechanics
```python
from breakthrough import BreakthroughMechanics
from world_database import WorldDatabase

db = WorldDatabase("data")
tech = db.get_technique("tech_taiqing_01")

# Apply technique effects to breakthrough
modifiers = {
    "pills": 0.1,
    "feng_shui": tech["effects"].get("cultivation_speed", 1.0) - 1.0
}
```

### Zhuazhou System
```python
from zhuazhou import ZhuazhouSystem
from world_database import WorldDatabase

db = WorldDatabase("data")
clan = db.get_clan("clan_lin")

# Add clan starting items to Zhuazhou pool
starting_items = clan["starting_perks"].get("items", [])
```

---

## 🎯 AI Integration

### For NPCs
```python
# Load sect data into AI prompt
sect = db.get_sect("sect_001")
ai_prompt = f"""
Bạn là đệ tử {sect['name']}, tính cách {sect['alignment']}.
Triết lý: {sect['description']}
Bạn có thể sử dụng: {sect['exclusive_techniques']}
"""
```

### For World Context
```python
# Load location data into AI prompt
location = db.get_location("loc_city_01")
ai_prompt = f"""
Người chơi đang ở {location['name']} ({location['region']}).
Mật độ linh khí: {location['qi_density']}
Dịch vụ có sẵn: {', '.join(location['services'])}
"""
```

---

## 📊 Data Statistics

Sau khi load:
- **Sects**: 5 tông môn
- **Techniques**: 6 công pháp
- **Races**: 6 chủng tộc
- **Clans**: 5 gia tộc
- **Locations**: 12 địa điểm

**Total**: ~34KB JSON data, load vào RAM < 1MB

---

## 🔄 Modding Guide

### Thêm Tông Môn Mới

1. Mở `data/sects.json`
2. Thêm object mới:
```json
{
  "id": "sect_006",
  "name": "Tên Tông Môn",
  "type": "Righteous",
  "alignment": "Lawful Good",
  "description": "Mô tả...",
  "location_zone": "Trung Châu",
  "requirements": {
    "min_int": 60,
    "min_kar": 50
  },
  "exclusive_techniques": ["tech_new_01"],
  "resources": {
    "specialty": "Pills",
    "wealth_rating": 5
  }
}
```

3. Restart game → Tự động load

### Thêm Địa Điểm Mới

1. Mở `data/locations.json`
2. Thêm object mới:
```json
{
  "id": "loc_new_01",
  "name": "Tên Địa Điểm",
  "type": "City",
  "region": "Trung Châu",
  "qi_density": 5.0,
  "level_range": [2, 3],
  "danger_level": "Low",
  "services": ["auction_house"],
  "connected_to": ["loc_city_01"]
}
```

---

## ✅ Benefits

1. **Modding-friendly**: Chỉ cần sửa JSON
2. **AI Integration**: Dễ inject vào prompts
3. **Performance**: O(1) lookup, < 1MB RAM
4. **Extensible**: Dễ thêm fields mới
5. **Type-safe**: Pydantic validation (future)

---

**Version**: 1.0  
**Last Updated**: 2025-12-03  
**Status**: ✅ Ready to Use

