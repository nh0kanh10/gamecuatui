"""
Procedural Generation System với Perlin Noise
Spawn Linh Thú và Thảo Dược dựa trên noise functions
"""

import random
import hashlib
import math
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json

try:
    from noise import pnoise2
    HAS_NOISE = True
except ImportError:
    HAS_NOISE = False
    # Fallback: Simple hash-based noise
    def pnoise2(x, y, octaves=1, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024, base=0):
        """Simple hash-based noise fallback"""
        hash_val = hash(f"{x}_{y}_{base}") % 10000
        return (hash_val / 10000.0) * 2.0 - 1.0  # Normalize to -1 to 1


class ProceduralSpawner:
    """
    Procedural spawner với Perlin Noise
    Tạo spawn patterns tự nhiên với clustering
    """
    
    def __init__(self, world_db, seed: int = None):
        self.world_db = world_db
        self.seed = seed or 42
        self.rng = random.Random(self.seed)
        self._spawn_tables_cache: Dict[str, Dict] = {}
        self._noise_cache: Dict[Tuple[int, int], float] = {}
        
        # Load spawn tables
        self._load_spawn_tables()
    
    def _load_spawn_tables(self):
        """Load spawn tables from JSON"""
        spawn_tables_path = Path("data/spawn_tables.json")
        if spawn_tables_path.exists():
            with open(spawn_tables_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._spawn_tables_cache = data.get("spawn_tables", {})
    
    def _get_noise_value(self, x: float, y: float, octaves: int = 4) -> float:
        """
        Get Perlin Noise value tại coordinate (x, y)
        
        Returns:
            Value từ -1.0 đến 1.0
        """
        cache_key = (int(x), int(y))
        if cache_key in self._noise_cache:
            return self._noise_cache[cache_key]
        
        # Scale coordinates để tạo patterns lớn hơn
        scale = 0.1
        nx = x * scale
        ny = y * scale
        
        # Generate noise
        noise_value = pnoise2(
            nx, ny,
            octaves=octaves,
            persistence=0.5,
            lacunarity=2.0,
            repeatx=1024,
            repeaty=1024,
            base=self.seed
        )
        
        # Normalize to 0.0 - 1.0
        normalized = (noise_value + 1.0) / 2.0
        
        self._noise_cache[cache_key] = normalized
        return normalized
    
    def spawn_herb_at_location(
        self,
        location_id: str,
        x: int = 0,
        y: int = 0,
        player_level: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Spawn một Thảo Dược tại location với Perlin Noise
        
        Args:
            location_id: Location ID
            x, y: Coordinates (for noise calculation)
            player_level: Player level (for filtering)
        
        Returns:
            {"herb_id": str, "age": int, "potency": float, "origin_signature": str} hoặc None
        """
        location = self.world_db.get_location(location_id)
        if not location:
            return None
        
        region_id = location.get("region", "unknown")
        spawn_table = self._get_spawn_table(region_id, "herbs")
        
        if not spawn_table:
            return None
        
        # Get noise value for clustering
        noise_value = self._get_noise_value(x, y, octaves=4)
        
        # Weighted random với noise filtering
        herb_id = self._weighted_random_with_noise(
            spawn_table, player_level, noise_value
        )
        
        if not herb_id:
            return None
        
        # Get herb template
        herb_template = self.world_db.get_spirit_herb(herb_id)
        if not herb_template:
            return None
        
        # Generate age (procedural, based on noise)
        age = self._generate_herb_age(herb_id, location_id, noise_value)
        
        # Calculate potency
        from components import SpiritHerbComponent
        herb_component = SpiritHerbComponent(
            template_id=herb_id,
            age=age,
            origin_signature=location_id
        )
        potency = herb_component.calculate_potency(herb_template)
        
        return {
            "herb_id": herb_id,
            "age": age,
            "potency": potency,
            "location_id": location_id,
            "origin_signature": location_id,
            "x": x,
            "y": y
        }
    
    def spawn_beast_at_location(
        self,
        location_id: str,
        x: int = 0,
        y: int = 0,
        player_level: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Spawn một Linh Thú tại location với Perlin Noise
        
        Returns:
            {"beast_id": str, "level": int, "mutations": Dict, "bloodline": List} hoặc None
        """
        location = self.world_db.get_location(location_id)
        if not location:
            return None
        
        region_id = location.get("region", "unknown")
        spawn_table = self._get_spawn_table(region_id, "beasts")
        
        if not spawn_table:
            return None
        
        # Get noise value
        noise_value = self._get_noise_value(x, y, octaves=3)
        
        # Weighted random với noise filtering
        beast_id = self._weighted_random_with_noise(
            spawn_table, player_level, noise_value
        )
        
        if not beast_id:
            return None
        
        # Generate level
        level = self._generate_beast_level(player_level, noise_value)
        
        # Generate mutations
        mutations = self._generate_mutations(beast_id, level, noise_value)
        
        # Generate bloodline modifiers
        bloodline_modifiers = self._generate_bloodline_modifiers(beast_id, noise_value)
        
        return {
            "beast_id": beast_id,
            "level": level,
            "mutations": mutations,
            "bloodline_modifiers": bloodline_modifiers,
            "location_id": location_id,
            "x": x,
            "y": y
        }
    
    def _weighted_random_with_noise(
        self,
        spawn_table: Dict[str, Dict],
        player_level: int,
        noise_value: float
    ) -> Optional[str]:
        """
        Weighted random selection với noise filtering
        
        Noise value cao → spawn rare items
        Noise value thấp → spawn common items
        """
        # Filter by level requirement
        eligible = {
            k: v for k, v in spawn_table.items()
            if v.get("min_level", 1) <= player_level
        }
        
        if not eligible:
            return None
        
        # Filter by noise threshold
        noise_filtered = {}
        for item_id, data in eligible.items():
            min_noise = data.get("min_noise", 0.0)
            if noise_value >= min_noise:
                # Boost weight nếu noise cao (rare items)
                weight = data.get("weight", 0.0)
                if noise_value > 0.8:
                    weight *= 1.5  # Boost rare spawns
                noise_filtered[item_id] = {**data, "weight": weight}
        
        if not noise_filtered:
            return None
        
        # Weighted random
        total_weight = sum(item["weight"] for item in noise_filtered.values())
        if total_weight == 0:
            return None
        
        random_value = self.rng.random() * total_weight
        current = 0
        
        for item_id, data in noise_filtered.items():
            current += data["weight"]
            if random_value <= current:
                return item_id
        
        return None
    
    def _generate_herb_age(
        self,
        herb_id: str,
        location_id: str,
        noise_value: float
    ) -> int:
        """
        Generate herb age dựa trên noise value
        Noise cao → age cao (rare herbs)
        """
        herb = self.world_db.get_spirit_herb(herb_id)
        if not herb:
            return 1
        
        rarity = herb.get("rarity", "Common")
        
        # Base age range
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
        
        # Noise value ảnh hưởng đến age
        # Noise cao → age cao hơn
        age_multiplier = 1.0 + (noise_value * 2.0)  # 1.0 - 3.0x
        
        base_age = age_range[0] + (age_range[1] - age_range[0]) // 2
        age = int(base_age * age_multiplier)
        
        # Clamp to range
        age = max(age_range[0], min(age_range[1], age))
        
        return age
    
    def _generate_beast_level(
        self,
        player_level: int,
        noise_value: float
    ) -> int:
        """
        Generate beast level
        Noise cao → level cao hơn (stronger beasts)
        """
        # Base level range
        min_level = max(1, player_level - 2)
        max_level = player_level + 5
        
        # Noise ảnh hưởng đến level
        level_offset = int((noise_value - 0.5) * 10)  # -5 to +5
        
        level = player_level + level_offset
        level = max(min_level, min(max_level, level))
        
        return level
    
    def _generate_mutations(
        self,
        beast_id: str,
        level: int,
        noise_value: float
    ) -> Dict[str, float]:
        """
        Generate procedural mutations
        Noise cao → mutations mạnh hơn
        """
        mutations = {}
        
        # Mutation chance tăng theo level và noise
        mutation_chance = min(0.5, (level / 100.0) + (noise_value * 0.3))
        
        if self.rng.random() < mutation_chance:
            # Random stat boost
            stat = self.rng.choice(["atk", "def", "hp", "spd", "mp"])
            # Boost strength depends on noise
            boost_min = 1.05 + (noise_value * 0.05)
            boost_max = 1.2 + (noise_value * 0.1)
            boost = self.rng.uniform(boost_min, boost_max)
            mutations[stat] = boost
        
        # Multiple mutations possible
        if noise_value > 0.8 and self.rng.random() < 0.3:
            stat = self.rng.choice(["atk", "def", "hp", "spd", "mp"])
            if stat not in mutations:
                mutations[stat] = self.rng.uniform(1.1, 1.3)
        
        return mutations
    
    def _generate_bloodline_modifiers(
        self,
        beast_id: str,
        noise_value: float
    ) -> List[Dict[str, Any]]:
        """
        Generate bloodline modifiers
        Noise cao → rare bloodlines
        """
        beast_template = self.world_db.get_spirit_beast(beast_id)
        if not beast_template:
            return []
        
        bloodline_data = beast_template.get("bloodline", {})
        possible_bloodlines = bloodline_data.get("possible_bloodlines", [])
        
        modifiers = []
        
        # Base bloodline
        base_bloodline = bloodline_data.get("base_bloodline", "")
        if base_bloodline:
            modifiers.append({
                "bloodline": base_bloodline,
                "percentage": 100.0
            })
        
        # Rare bloodlines (noise cao)
        if noise_value > 0.7 and possible_bloodlines:
            # 30% chance for rare bloodline
            if self.rng.random() < 0.3:
                rare_bloodline = self.rng.choice(possible_bloodlines)
                percentage = self.rng.uniform(5.0, 20.0)  # 5-20% bloodline
                modifiers.append({
                    "bloodline": rare_bloodline,
                    "percentage": percentage
                })
        
        return modifiers
    
    def _get_spawn_table(self, region_id: str, entity_type: str) -> Dict:
        """Get spawn table from cache"""
        region_table = self._spawn_tables_cache.get(region_id, {})
        return region_table.get(entity_type, {})
    
    def generate_spawn_map(
        self,
        region_id: str,
        width: int = 100,
        height: int = 100,
        entity_type: str = "herbs"
    ) -> List[Dict[str, Any]]:
        """
        Generate spawn map cho một region
        Dùng Perlin Noise để tạo clustering patterns
        
        Returns:
            List of spawns với coordinates
        """
        spawn_table = self._get_spawn_table(region_id, entity_type)
        if not spawn_table:
            return []
        
        spawns = []
        
        for x in range(0, width, 10):  # Sample every 10 units
            for y in range(0, height, 10):
                noise_value = self._get_noise_value(x, y)
                
                # Spawn chance based on noise
                base_chance = 0.1
                spawn_chance = base_chance * (1.0 + noise_value)
                
                if self.rng.random() < spawn_chance:
                    # Spawn entity
                    if entity_type == "herbs":
                        spawn = self.spawn_herb_at_location(
                            location_id=f"{region_id}_spawn",
                            x=x,
                            y=y,
                            player_level=1
                        )
                    else:
                        spawn = self.spawn_beast_at_location(
                            location_id=f"{region_id}_spawn",
                            x=x,
                            y=y,
                            player_level=1
                        )
                    
                    if spawn:
                        spawns.append(spawn)
        
        return spawns

