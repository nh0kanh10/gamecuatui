# 📝 Prompt: Expand Database Content

## 🎯 Mục Tiêu

Tạo thêm nội dung cho database để game phong phú hơn:
- **500+ items** (vật phẩm)
- **200+ techniques** (công pháp)
- **100+ NPCs** (nhân vật)

---

## 📋 Format Database

### 1. Items Database (`data/items.json`)

**Format:**
```json
[
  {
    "id": "item_001",
    "name": "Huyền Thiên Kiếm",
    "type": "Weapon",
    "subtype": "Sword",
    "tier": "Legendary",
    "rarity": "Epic",
    "price": 50000,
    "description": "Kiếm huyền thoại từ thời cổ đại, sắc bén vô cùng",
    "stats": {
      "attack": 150,
      "speed": 10,
      "durability": 1000
    },
    "requirements": {
      "level": 50,
      "cultivation_realm": "Kim Đan",
      "cultivation_level": 5
    },
    "effects": {
      "on_equip": {
        "attack_bonus": 150,
        "speed_bonus": 10
      },
      "special": "lightning_damage"
    },
    "locations": ["loc_sect_01", "loc_treasure_01"],
    "lore": "Kiếm này được rèn từ thiên thạch, có sức mạnh sấm sét"
  },
  {
    "id": "pill_001",
    "name": "Tụ Linh Đan",
    "type": "Pill",
    "subtype": "Cultivation",
    "tier": "Rare",
    "rarity": "Uncommon",
    "price": 1000,
    "description": "Đan dược tăng tu vi, dùng khi tu luyện",
    "stats": {},
    "requirements": {},
    "effects": {
      "on_use": {
        "cultivation_bonus": 100,
        "spiritual_power": 50
      }
    },
    "locations": ["loc_shop_01", "loc_alchemist_01"],
    "lore": "Đan dược phổ biến trong giới tu tiên"
  }
]
```

**Yêu Cầu:**
- ✅ **500+ items** với đa dạng types:
  - Weapons (Sword, Spear, Bow, Staff, etc.)
  - Armor (Robe, Armor, Boots, Helmet, etc.)
  - Pills (Cultivation, Healing, Breakthrough, etc.)
  - Materials (Herbs, Ores, Cores, etc.)
  - Artifacts (Special items với effects đặc biệt)
- ✅ Mỗi item có: name, description, stats, requirements, effects, lore
- ✅ Phân tier: Common, Uncommon, Rare, Epic, Legendary
- ✅ Phân realm requirements: Luyện Khí, Trúc Cơ, Kim Đan, etc.

---

### 2. Techniques Database (`data/techniques.json`)

**Format:**
```json
[
  {
    "id": "tech_thunder_sword_01",
    "name": "Thiên Vũ Kiếm Pháp",
    "type": "Combat",
    "subtype": "Sword Technique",
    "tier": "Hoàng Cấp",
    "rarity": "Epic",
    "description": "Kiếm pháp huyền diệu, triệu hồi sấm sét",
    "requirements": {
      "cultivation_realm": "Trúc Cơ",
      "cultivation_level": 3,
      "weapon_type": "Sword"
    },
    "learning_cost": {
      "spirit_stones": 5000,
      "time_months": 3,
      "prerequisites": ["tech_basic_sword_01"]
    },
    "effects": {
      "attack_bonus": 50,
      "special_attack": "lightning_strike",
      "damage_multiplier": 1.5
    },
    "levels": [
      {
        "level": 1,
        "damage": 100,
        "cost": 10
      },
      {
        "level": 2,
        "damage": 150,
        "cost": 15
      },
      {
        "level": 3,
        "damage": 200,
        "cost": 20
      }
    ],
    "lore": "Kiếm pháp được truyền từ đời này sang đời khác"
  },
  {
    "id": "tech_cultivation_01",
    "name": "Thái Thanh Tâm Pháp",
    "type": "Cultivation",
    "subtype": "Cultivation Method",
    "tier": "Địa Cấp",
    "rarity": "Rare",
    "description": "Tâm pháp tu luyện cao cấp, tăng tốc độ tu luyện",
    "requirements": {
      "cultivation_realm": "Luyện Khí",
      "cultivation_level": 1
    },
    "learning_cost": {
      "spirit_stones": 1000,
      "time_months": 1
    },
    "effects": {
      "cultivation_speed_bonus": 1.5,
      "spiritual_power_gain": 20
    },
    "lore": "Tâm pháp cơ bản cho người mới bắt đầu"
  }
]
```

**Yêu Cầu:**
- ✅ **200+ techniques** với đa dạng types:
  - Combat Techniques (Sword, Spear, Fist, etc.)
  - Cultivation Methods (Tâm pháp)
  - Support Techniques (Healing, Buff, Debuff)
  - Movement Techniques (Light Body, Teleport, etc.)
- ✅ Mỗi technique có: name, description, requirements, learning_cost, effects, levels
- ✅ Phân tier: Nhân Cấp, Hoàng Cấp, Địa Cấp, Thiên Cấp
- ✅ Có prerequisites (kỹ năng cần học trước)

---

### 3. NPCs Database (`data/npcs.json`)

**Format:**
```json
[
  {
    "id": "npc_sect_master_01",
    "name": "Lâm Thanh Phong",
    "title": "Trưởng Lão",
    "type": "Sect Elder",
    "location_id": "loc_sect_01",
    "sect_id": "sect_taiqing",
    "cultivation_realm": "Kim Đan",
    "cultivation_level": 9,
    "personality": {
      "traits": ["Strict", "Wise", "Protective"],
      "alignment": "Lawful Good"
    },
    "dialogue_templates": [
      "Ngươi muốn học kỹ năng gì?",
      "Tu luyện cần kiên trì, không được nóng vội",
      "Nếu ngươi chứng minh được năng lực, ta sẽ truyền thụ cho ngươi"
    ],
    "services": ["teach_technique", "give_quest", "sell_items"],
    "relationships": {
      "initial_affinity": 0,
      "relationship_type": "teacher"
    },
    "quests": ["quest_prove_worth_01"],
    "lore": "Trưởng lão của tông môn, tu luyện đã hơn 300 năm"
  },
  {
    "id": "npc_merchant_01",
    "name": "Vương Thương",
    "title": "Thương Nhân",
    "type": "Merchant",
    "location_id": "loc_market_01",
    "cultivation_realm": "Trúc Cơ",
    "cultivation_level": 3,
    "personality": {
      "traits": ["Friendly", "Greedy", "Talkative"],
      "alignment": "Neutral"
    },
    "dialogue_templates": [
      "Chào mừng! Có gì cần mua không?",
      "Hàng của tôi chất lượng tốt nhất!",
      "Nếu mua nhiều, tôi sẽ giảm giá cho ngươi"
    ],
    "services": ["buy_items", "sell_items"],
    "shop_items": ["item_001", "item_002", "pill_001"],
    "relationships": {
      "initial_affinity": 20,
      "relationship_type": "merchant"
    },
    "lore": "Thương nhân giàu có, buôn bán khắp nơi"
  }
]
```

**Yêu Cầu:**
- ✅ **100+ NPCs** với đa dạng types:
  - Sect Elders (Trưởng lão, Sư phụ)
  - Merchants (Thương nhân)
  - Cultivators (Tu sĩ)
  - Quest Givers (Người cho nhiệm vụ)
  - Companions (Đồng đội)
- ✅ Mỗi NPC có: name, title, location, personality, services, dialogue_templates
- ✅ Có relationships system
- ✅ Có quests (nếu là quest giver)

---

## 🎯 Yêu Cầu Chi Tiết

### Items (500+):

**Phân bổ:**
- Weapons: 100 items (Sword 30, Spear 20, Bow 15, Staff 15, Fist 10, Other 10)
- Armor: 80 items (Robe 25, Armor 25, Boots 15, Helmet 15)
- Pills: 150 items (Cultivation 50, Healing 30, Breakthrough 30, Buff 20, Special 20)
- Materials: 100 items (Herbs 40, Ores 30, Cores 20, Other 10)
- Artifacts: 70 items (Special effects, unique items)

**Tier Distribution:**
- Common: 200 items (40%)
- Uncommon: 150 items (30%)
- Rare: 100 items (20%)
- Epic: 40 items (8%)
- Legendary: 10 items (2%)

---

### Techniques (200+):

**Phân bổ:**
- Combat: 80 techniques (Sword 25, Spear 15, Fist 15, Bow 10, Staff 10, Other 5)
- Cultivation: 60 techniques (Tâm pháp các loại)
- Support: 40 techniques (Healing 15, Buff 15, Debuff 10)
- Movement: 20 techniques (Light Body, Teleport, etc.)

**Tier Distribution:**
- Nhân Cấp: 80 techniques (40%)
- Hoàng Cấp: 70 techniques (35%)
- Địa Cấp: 35 techniques (17.5%)
- Thiên Cấp: 15 techniques (7.5%)

---

### NPCs (100+):

**Phân bổ:**
- Sect Elders: 30 NPCs
- Merchants: 20 NPCs
- Cultivators: 25 NPCs
- Quest Givers: 15 NPCs
- Companions: 10 NPCs

**Location Distribution:**
- Sects: 40 NPCs
- Markets: 20 NPCs
- Villages: 20 NPCs
- Dungeons: 10 NPCs
- Other: 10 NPCs

---

## 📝 Checklist

### Items:
- [ ] 500+ items với đầy đủ thông tin
- [ ] Đa dạng types (Weapon, Armor, Pill, Material, Artifact)
- [ ] Phân tier rõ ràng (Common → Legendary)
- [ ] Có requirements (realm, level)
- [ ] Có effects và stats
- [ ] Có lore cho mỗi item

### Techniques:
- [ ] 200+ techniques với đầy đủ thông tin
- [ ] Đa dạng types (Combat, Cultivation, Support, Movement)
- [ ] Phân tier rõ ràng (Nhân → Thiên)
- [ ] Có prerequisites
- [ ] Có learning_cost
- [ ] Có levels và effects

### NPCs:
- [ ] 100+ NPCs với đầy đủ thông tin
- [ ] Đa dạng types (Elder, Merchant, Cultivator, etc.)
- [ ] Có personality và dialogue_templates
- [ ] Có services (teach, sell, quest)
- [ ] Có relationships
- [ ] Có lore

---

## 🎨 Style Guide

### Naming:
- **Items:** Tên tiếng Việt, có tính chất tu tiên (Huyền Thiên Kiếm, Tụ Linh Đan)
- **Techniques:** Tên kỹ thuật, có tier (Thiên Vũ Kiếm Pháp - Hoàng Cấp)
- **NPCs:** Tên người Việt (Lâm Thanh Phong, Vương Thương)

### Description:
- Ngắn gọn, 1-2 câu
- Có tính chất tu tiên
- Mô tả rõ ràng công dụng

### Lore:
- 1-2 câu về nguồn gốc/history
- Tạo depth cho world

---

## ✅ Deliverables

1. **`data/items.json`** - 500+ items
2. **`data/techniques.json`** - 200+ techniques (merge với file hiện tại)
3. **`data/npcs.json`** - 100+ NPCs (file mới)

**Format:** JSON array, UTF-8 encoding

---

## 🎯 Priority

1. **High Priority:**
   - Items: Weapons, Pills (cần cho gameplay)
   - Techniques: Combat, Cultivation (cần cho gameplay)
   - NPCs: Sect Elders, Merchants (cần cho gameplay)

2. **Medium Priority:**
   - Items: Armor, Materials
   - Techniques: Support, Movement
   - NPCs: Cultivators, Quest Givers

3. **Low Priority:**
   - Items: Artifacts (special)
   - NPCs: Companions

---

**Bắt đầu với High Priority items trước!** 🚀

