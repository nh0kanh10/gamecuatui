# Phân Tích: Procedural Generation cho Linh Thú và Thảo Dược

## 1. Tại Sao Procedural Generation "Khá Hay"?

### 1.1. **Vô Hạn Nội Dung với Dung Lượng Tối Thiểu**
- **Không cần lưu trữ**: Thay vì lưu 10,000 vị trí spawn, chỉ cần lưu **rules** (vài KB)
- **Deterministic**: Cùng seed → cùng kết quả (reproducible)
- **Infinite World**: Có thể tạo thế giới vô hạn mà không tốn storage

### 1.2. **Tự Nhiên và Đa Dạng**
- **Clustering**: Perlin Noise tạo ra cụm (clusters) tự nhiên
  - Thảo Dược mọc theo cụm (realistic)
  - Linh Thú sống theo đàn (realistic)
- **Variation**: Mỗi vùng có đặc điểm riêng
- **Emergent Gameplay**: Người chơi phải khám phá để tìm resources

### 1.3. **Replayability**
- **Different Seeds**: Mỗi playthrough có world khác nhau
- **Exploration**: Không thể dùng guide cố định
- **Discovery**: Luôn có điều mới để khám phá

---

## 2. Vấn Đề với Perlin Noise (Báo Cáo Đề Xuất)

### 2.1. **Phức Tạp**
- **Dependencies**: Cần `noise` library hoặc implement Perlin Noise
- **Learning Curve**: Phải hiểu noise functions
- **Debugging**: Khó debug khi có bug

### 2.2. **Performance**
- **CPU Cost**: Tính toán noise cho mỗi coordinate
- **Memory**: Có thể cache noise values nhưng tốn RAM

### 2.3. **Overkill cho MVP**
- **MVP chỉ cần**: Spawn items/beasts ở locations
- **Chưa cần**: Infinite world generation

---

## 3. ✅ GIẢI PHÁP: Simplified Procedural Generation

### 3.1. **Weighted Random với Seed-Based**

Thay vì Perlin Noise phức tạp, dùng **weighted random** với **deterministic seed**:

```python
import random
import hashlib

class ProceduralSpawner:
    def __init__(self, region_id: str, seed: int = None):
        self.region_id = region_id
        self.seed = seed or hash(region_id) % (2**31)
        self.rng = random.Random(self.seed)
    
    def spawn_herb(self, x: int, y: int, spawn_table: Dict) -> Optional[str]:
        """
        Spawn herb dựa trên weighted random + coordinate hash
        
        Args:
            x, y: Coordinates
            spawn_table: {"herb_id": {"weight": 0.5, "min_level": 1}}
        
        Returns:
            herb_id hoặc None
        """
        # Tạo deterministic hash từ coordinates
        coord_hash = hash(f"{self.region_id}_{x}_{y}") % 10000
        
        # Dùng hash để tạo "noise-like" value (0.0 - 1.0)
        noise_value = coord_hash / 10000.0
        
        # Weighted selection
        total_weight = sum(item["weight"] for item in spawn_table.values())
        random_value = self.rng.random() * total_weight
        
        current = 0
        for herb_id, data in spawn_table.items():
            current += data["weight"]
            # Kết hợp noise_value để tạo clustering
            if random_value <= current and noise_value > data.get("min_noise", 0.0):
                return herb_id
        
        return None
```

### 3.2. **Clustering với Simple Grid-Based**

Thay vì Perlin Noise, dùng **grid-based clustering**:

```python
class SimpleClustering:
    def __init__(self, region_id: str, seed: int):
        self.region_id = region_id
        self.rng = random.Random(seed)
        # Tạo các "hotspots" (cụm)
        self.hotspots = self._generate_hotspots()
    
    def _generate_hotspots(self, num_hotspots: int = 10) -> List[Dict]:
        """Tạo các điểm nóng (hotspots) cho spawn"""
        hotspots = []
        for _ in range(num_hotspots):
            hotspots.append({
                "x": self.rng.randint(0, 1000),
                "y": self.rng.randint(0, 1000),
                "radius": self.rng.randint(50, 200),
                "intensity": self.rng.uniform(0.5, 1.0)
            })
        return hotspots
    
    def get_spawn_chance(self, x: int, y: int, base_chance: float) -> float:
        """Tính spawn chance dựa trên distance từ hotspots"""
        max_influence = 0.0
        
        for hotspot in self.hotspots:
            distance = ((x - hotspot["x"])**2 + (y - hotspot["y"])**2)**0.5
            
            if distance < hotspot["radius"]:
                # Influence giảm theo distance
                influence = hotspot["intensity"] * (1 - distance / hotspot["radius"])
                max_influence = max(max_influence, influence)
        
        # Base chance + hotspot bonus
        return min(1.0, base_chance + max_influence)
```

### 3.3. **JSON Configuration (Simple)**

```json
{
  "spawn_tables": {
    "region_forest": {
      "seed": 12345,
      "herbs": {
        "herb_ginseng": {
          "weight": 0.3,
          "base_chance": 0.1,
          "clustering": "high",  // Mọc theo cụm
          "min_level": 1
        },
        "herb_rare_flower": {
          "weight": 0.05,
          "base_chance": 0.01,
          "clustering": "very_high",  // Rất hiếm, mọc cụm nhỏ
          "min_level": 10
        }
      },
      "beasts": {
        "beast_fire_tiger": {
          "weight": 0.2,
          "base_chance": 0.05,
          "pack_size": 3,  // Sống theo đàn
          "min_level": 5
        }
      }
    }
  }
}
```

---

## 4. 🎯 IMPLEMENTATION PLAN

### Phase 1: Simple Weighted Random (MVP - 1 tuần)

**Mục tiêu**: Spawn items/beasts dựa trên weighted random table

**Features**:
- ✅ Weighted random selection
- ✅ Seed-based (deterministic)
- ✅ Region-based spawn tables
- ✅ Level requirements

**Code Structure**:
```python
# cultivation-sim/procedural_spawn.py
class SimpleSpawner:
    def spawn_herb_at_location(self, location_id: str, player_level: int) -> Optional[str]
    def spawn_beast_at_location(self, location_id: str, player_level: int) -> Optional[str]
    def get_spawn_table(self, region_id: str) -> Dict
```

### Phase 2: Clustering (Sau MVP - 1 tuần)

**Mục tiêu**: Thêm clustering để spawn tự nhiên hơn

**Features**:
- ✅ Grid-based hotspots
- ✅ Distance-based influence
- ✅ Clustering intensity

### Phase 3: Advanced (Future - 2 tuần)

**Mục tiêu**: Perlin Noise nếu cần infinite world

**Features**:
- ⚠️ Perlin Noise implementation
- ⚠️ Infinite world generation
- ⚠️ Biome-based spawning

---

## 5. 📊 SO SÁNH: Perlin Noise vs Simple Approach

| Tiêu chí | Perlin Noise | Simple Weighted + Clustering |
|----------|--------------|------------------------------|
| **Complexity** | ⚠️ Cao (cần library) | ✅ Thấp (pure Python) |
| **Dependencies** | ❌ Cần `noise` hoặc `numpy` | ✅ Không cần |
| **Performance** | ⚠️ Chậm hơn (tính toán) | ✅ Nhanh (hash-based) |
| **Clustering** | ✅ Tự nhiên | ✅ Tốt (grid-based) |
| **Deterministic** | ✅ Có | ✅ Có (seed-based) |
| **Debugging** | ❌ Khó | ✅ Dễ |
| **MVP Ready** | ❌ Không | ✅ Có |

---

## 6. 💡 KHUYẾN NGHỊ

### ✅ **Nên Implement**: Simple Weighted Random + Clustering

**Lý do**:
1. **Đủ cho MVP**: Tạo được variation và clustering
2. **Không phức tạp**: Pure Python, không cần dependencies
3. **Dễ debug**: Logic rõ ràng
4. **Performance tốt**: Hash-based, nhanh hơn Perlin Noise
5. **Có thể nâng cấp**: Sau này có thể thêm Perlin Noise nếu cần

### ❌ **Bỏ Qua**: Perlin Noise (cho MVP)

**Lý do**:
1. **Quá phức tạp**: Cần library, learning curve
2. **Overkill**: MVP chưa cần infinite world
3. **Performance**: Chậm hơn simple approach
4. **Có thể thêm sau**: Nếu cần infinite world generation

---

## 7. 🚀 CODE EXAMPLE: Simple Implementation

```python
"""
Simple Procedural Spawner cho Linh Thú và Thảo Dược
MVP version - không cần Perlin Noise
"""

import random
import hashlib
from typing import Dict, List, Optional, Any
from world_database import WorldDatabase


class SimpleSpawner:
    """
    Simple procedural spawner với weighted random + clustering
    """
    
    def __init__(self, world_db: WorldDatabase, seed: int = None):
        self.world_db = world_db
        self.seed = seed or 42
        self.rng = random.Random(self.seed)
        self._hotspots_cache: Dict[str, List[Dict]] = {}
    
    def spawn_herb_at_location(
        self,
        location_id: str,
        player_level: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Spawn một Thảo Dược tại location
        
        Returns:
            {"herb_id": str, "age": int, "potency": float} hoặc None
        """
        location = self.world_db.get_location(location_id)
        if not location:
            return None
        
        region_id = location.get("region", "unknown")
        spawn_table = self._get_spawn_table(region_id, "herbs")
        
        if not spawn_table:
            return None
        
        # Weighted random selection
        herb_id = self._weighted_random(spawn_table, player_level)
        if not herb_id:
            return None
        
        # Get herb template
        herb_template = self.world_db.get_item(herb_id)
        if not herb_template:
            return None
        
        # Generate age (procedural)
        age = self._generate_herb_age(herb_id, location_id)
        
        # Calculate potency based on age
        potency = self._calculate_potency(herb_template, age)
        
        return {
            "herb_id": herb_id,
            "age": age,
            "potency": potency,
            "location_id": location_id
        }
    
    def spawn_beast_at_location(
        self,
        location_id: str,
        player_level: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Spawn một Linh Thú tại location
        
        Returns:
            {"beast_id": str, "level": int, "mutations": Dict} hoặc None
        """
        location = self.world_db.get_location(location_id)
        if not location:
            return None
        
        region_id = location.get("region", "unknown")
        spawn_table = self._get_spawn_table(region_id, "beasts")
        
        if not spawn_table:
            return None
        
        # Weighted random selection
        beast_id = self._weighted_random(spawn_table, player_level)
        if not beast_id:
            return None
        
        # Generate level (procedural, based on player level)
        level = self._generate_beast_level(player_level)
        
        # Generate mutations (procedural)
        mutations = self._generate_mutations(beast_id, level)
        
        return {
            "beast_id": beast_id,
            "level": level,
            "mutations": mutations,
            "location_id": location_id
        }
    
    def _weighted_random(
        self,
        spawn_table: Dict[str, Dict],
        player_level: int
    ) -> Optional[str]:
        """Weighted random selection với level filtering"""
        # Filter by level requirement
        eligible = {
            k: v for k, v in spawn_table.items()
            if v.get("min_level", 1) <= player_level
        }
        
        if not eligible:
            return None
        
        # Calculate total weight
        total_weight = sum(item["weight"] for item in eligible.values())
        if total_weight == 0:
            return None
        
        # Random selection
        random_value = self.rng.random() * total_weight
        current = 0
        
        for item_id, data in eligible.items():
            current += data["weight"]
            if random_value <= current:
                return item_id
        
        return None
    
    def _generate_herb_age(self, herb_id: str, location_id: str) -> int:
        """
        Generate herb age dựa trên herb type và location
        Deterministic (cùng seed → cùng age)
        """
        # Tạo hash từ herb_id + location_id
        hash_value = hash(f"{herb_id}_{location_id}_{self.seed}") % 10000
        
        # Age range dựa trên herb rarity
        herb = self.world_db.get_item(herb_id)
        if not herb:
            return 1
        
        rarity = herb.get("rarity", "Common")
        
        if rarity == "Common":
            age_range = (1, 100)
        elif rarity == "Uncommon":
            age_range = (50, 500)
        elif rarity == "Rare":
            age_range = (200, 2000)
        elif rarity == "Legendary":
            age_range = (1000, 10000)
        else:
            age_range = (1, 100)
        
        # Map hash to age range
        age = age_range[0] + (hash_value % (age_range[1] - age_range[0] + 1))
        return age
    
    def _calculate_potency(self, herb_template: Dict, age: int) -> float:
        """Calculate potency based on age"""
        base_potency = herb_template.get("base_potency", 10)
        
        # Logarithmic growth (giống báo cáo đề xuất)
        import math
        age_multiplier = math.log10(max(1, age)) + 1
        
        return base_potency * age_multiplier
    
    def _generate_beast_level(self, player_level: int) -> int:
        """Generate beast level (slightly above player level)"""
        # Level range: player_level - 2 to player_level + 5
        min_level = max(1, player_level - 2)
        max_level = player_level + 5
        
        return self.rng.randint(min_level, max_level)
    
    def _generate_mutations(self, beast_id: str, level: int) -> Dict[str, float]:
        """Generate procedural mutations"""
        # Mutation chance tăng theo level
        mutation_chance = min(0.3, level / 100.0)
        
        mutations = {}
        
        if self.rng.random() < mutation_chance:
            # Random stat boost
            stat = self.rng.choice(["atk", "def", "hp", "spd"])
            boost = self.rng.uniform(1.05, 1.2)  # 5-20% boost
            mutations[stat] = boost
        
        return mutations
    
    def _get_spawn_table(self, region_id: str, entity_type: str) -> Dict:
        """Get spawn table from world database"""
        # TODO: Load from data/spawn_tables.json
        # For now, return empty (will be implemented)
        return {}
    
    def _get_hotspots(self, region_id: str) -> List[Dict]:
        """Get or generate hotspots for region"""
        if region_id not in self._hotspots_cache:
            # Generate hotspots (deterministic)
            self.rng.seed(hash(f"{region_id}_{self.seed}") % (2**31))
            hotspots = []
            
            for _ in range(10):  # 10 hotspots per region
                hotspots.append({
                    "x": self.rng.randint(0, 1000),
                    "y": self.rng.randint(0, 1000),
                    "radius": self.rng.randint(50, 200),
                    "intensity": self.rng.uniform(0.5, 1.0)
                })
            
            self._hotspots_cache[region_id] = hotspots
        
        return self._hotspots_cache[region_id]
```

---

## 8. 📝 KẾT LUẬN

### ✅ **Procedural Generation LÀ "Khá Hay"**:
- Vô hạn nội dung
- Tự nhiên và đa dạng
- Replayability cao

### ⚠️ **Nhưng Perlin Noise QUÁ PHỨC TẠP cho MVP**:
- Cần dependencies
- Performance overhead
- Overkill cho nhu cầu hiện tại

### 🎯 **Giải Pháp**: Simple Weighted Random + Clustering
- ✅ Đủ cho MVP
- ✅ Không phức tạp
- ✅ Performance tốt
- ✅ Có thể nâng cấp sau

**Khuyến nghị**: Implement Simple Procedural Generation cho MVP, có thể thêm Perlin Noise sau nếu cần infinite world.

