"""
Physique System - Hệ thống thể chất với tương tác thực tế
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class PhysiqueEffect:
    """Effects của thể chất"""
    defense_percent: float = 0.0
    attack_power: float = 1.0
    hp_multiplier: float = 1.0
    cultivation_speed: float = 1.0
    crit_chance: float = 0.0
    crit_damage: float = 1.0
    dodge_chance: float = 0.0
    hp_regen_percent: float = 0.0
    lifesteal: float = 0.0
    armor_penetration: float = 0.0
    movement_speed: float = 1.0
    attack_speed: float = 1.0
    qi_efficiency: float = 1.0
    breakthrough_chance: float = 0.0
    # Special effects
    fire_resistance: float = 0.0
    ice_resistance: float = 0.0
    poison_resistance: float = 0.0
    mental_resistance: float = 0.0
    cc_resistance: float = 0.0
    # Elemental damage
    fire_damage: float = 1.0
    ice_damage: float = 1.0
    dark_damage: float = 1.0
    # Other
    luck_bonus: float = 0.0
    perception_bonus: float = 0.0
    stability: float = 0.0


class PhysiqueSystem:
    """Hệ thống quản lý thể chất"""
    
    TIER_MULTIPLIERS = {
        "Phàm": 1.0,
        "Linh": 1.2,
        "Dị": 1.4,
        "Thần": 1.6,
        "Huyền": 1.8,
        "Tiên": 2.0,
        "Cổ": 2.5,
        "Hỗn Nguyên": 3.0
    }
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize physique system"""
        if data_path is None:
            data_path = Path(__file__).parent / "data" / "physiques.json"
        
        self.physiques: Dict[str, Dict[str, Any]] = {}
        self._load_physiques(data_path)
    
    def _load_physiques(self, data_path: Path):
        """Load physiques from JSON"""
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                physiques_list = json.load(f)
                for physique in physiques_list:
                    self.physiques[physique['id']] = physique
        except Exception as e:
            print(f"Error loading physiques: {e}")
            self.physiques = {}
    
    def get_physique(self, physique_id: str) -> Optional[Dict[str, Any]]:
        """Get physique by ID"""
        return self.physiques.get(physique_id)
    
    def get_physique_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get physique by name"""
        for physique in self.physiques.values():
            if physique['name'] == name:
                return physique
        return None
    
    def get_physiques_by_element(self, element: str) -> List[Dict[str, Any]]:
        """Get all physiques of an element"""
        return [p for p in self.physiques.values() if p.get('element') == element]
    
    def get_physiques_by_tier(self, tier: str) -> List[Dict[str, Any]]:
        """Get all physiques of a tier"""
        return [p for p in self.physiques.values() if p.get('tier') == tier]
    
    def calculate_effects(self, physique_id: str, level: int = 1) -> PhysiqueEffect:
        """
        Calculate actual effects of a physique
        
        Args:
            physique_id: ID of the physique
            level: Level of the physique (1-10)
        
        Returns:
            PhysiqueEffect with calculated values
        """
        physique = self.get_physique(physique_id)
        if not physique:
            return PhysiqueEffect()
        
        effects = PhysiqueEffect()
        base_effects = physique.get('effects', {})
        tier = physique.get('tier', 'Phàm')
        tier_multiplier = self.TIER_MULTIPLIERS.get(tier, 1.0)
        level_multiplier = 1.0 + (level - 1) * 0.1  # +10% per level
        
        # Apply base effects with tier and level multipliers
        for key, value in base_effects.items():
            if hasattr(effects, key):
                # For percentages, multiply by tier
                if 'percent' in key or 'chance' in key or 'resistance' in key:
                    setattr(effects, key, value * tier_multiplier * level_multiplier)
                # For multipliers, apply tier bonus
                elif isinstance(value, (int, float)) and value > 0:
                    if value >= 1.0:  # Multiplier
                        setattr(effects, key, 1.0 + (value - 1.0) * tier_multiplier * level_multiplier)
                    else:  # Negative modifier
                        setattr(effects, key, value * tier_multiplier * level_multiplier)
                else:
                    setattr(effects, key, value)
        
        return effects
    
    def apply_to_cultivation(self, physique_id: str, base_speed: float, level: int = 1) -> float:
        """
        Apply physique effects to cultivation speed
        
        Formula: Tốc độ = (LinhCăn × HệSố_ThểChất × CảnhGiới × MôiTrường × 0.1)
        """
        effects = self.calculate_effects(physique_id, level)
        return base_speed * effects.cultivation_speed
    
    def apply_to_damage(self, physique_id: str, base_damage: float, level: int = 1) -> float:
        """
        Apply physique effects to damage
        
        Formula: DMG = (CơThể × VũKhí × KỹNăng × Buff_ThểChất)
        """
        effects = self.calculate_effects(physique_id, level)
        return base_damage * effects.attack_power
    
    def apply_to_defense(self, physique_id: str, base_defense: float, level: int = 1) -> float:
        """
        Apply physique effects to defense
        
        Formula: DEF = GiápCơBản × (1 + Buff_ThểChất)
        """
        effects = self.calculate_effects(physique_id, level)
        return base_defense * (1.0 + effects.defense_percent)
    
    def apply_to_hp(self, physique_id: str, base_hp: float, level: int = 1) -> float:
        """
        Apply physique effects to max HP
        
        Formula: HPmax = (ThểLực × 10) × (1 + HệSố_ThểChất)
        """
        effects = self.calculate_effects(physique_id, level)
        return base_hp * effects.hp_multiplier
    
    def apply_to_breakthrough(self, physique_id: str, base_chance: float, level: int = 1) -> float:
        """
        Apply physique effects to breakthrough chance
        
        Formula: BreakRate = CănCơ + MayMắn + Buff_ThểChất - TâmMa
        """
        effects = self.calculate_effects(physique_id, level)
        return min(0.95, base_chance + effects.breakthrough_chance)
    
    def get_all_effects_dict(self, physique_id: str, level: int = 1) -> Dict[str, Any]:
        """Get all effects as dictionary for JSON serialization"""
        effects = self.calculate_effects(physique_id, level)
        return {
            "defense_percent": effects.defense_percent,
            "attack_power": effects.attack_power,
            "hp_multiplier": effects.hp_multiplier,
            "cultivation_speed": effects.cultivation_speed,
            "crit_chance": effects.crit_chance,
            "crit_damage": effects.crit_damage,
            "dodge_chance": effects.dodge_chance,
            "hp_regen_percent": effects.hp_regen_percent,
            "lifesteal": effects.lifesteal,
            "armor_penetration": effects.armor_penetration,
            "movement_speed": effects.movement_speed,
            "attack_speed": effects.attack_speed,
            "qi_efficiency": effects.qi_efficiency,
            "breakthrough_chance": effects.breakthrough_chance,
            "luck_bonus": effects.luck_bonus,
            "perception_bonus": effects.perception_bonus,
        }
    
    def random_physique(self, element: Optional[str] = None, tier: Optional[str] = None) -> Optional[str]:
        """
        Get random physique ID
        
        Args:
            element: Filter by element (optional)
            tier: Filter by tier (optional)
        
        Returns:
            Random physique ID or None
        """
        import random
        
        candidates = list(self.physiques.keys())
        
        if element:
            candidates = [p['id'] for p in self.get_physiques_by_element(element)]
        
        if tier:
            candidates = [p['id'] for p in self.get_physiques_by_tier(tier) if p['id'] in candidates]
        
        if candidates:
            return random.choice(candidates)
        return None

