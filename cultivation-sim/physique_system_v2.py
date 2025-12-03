"""
Physique System V2 - Dựa trên cơ chế và prompt, không phải chỉ số AI viết
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class PhysiqueSystemV2:
    """Hệ thống thể chất với cơ chế gameplay thực tế"""
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize physique system"""
        if data_path is None:
            data_path = Path(__file__).parent / "data" / "physiques_gameplay.json"
        
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
    
    def get_ai_prompt(self, physique_id: str) -> str:
        """Get AI prompt for this physique"""
        physique = self.get_physique(physique_id)
        if not physique:
            return ""
        return physique.get('ai_prompt', '')
    
    def get_forbidden_words(self, physique_id: str) -> List[str]:
        """Get forbidden words for AI"""
        physique = self.get_physique(physique_id)
        if not physique:
            return []
        return physique.get('ai_behavior', {}).get('forbidden_words', [])
    
    def check_locks(self, physique_id: str, feature: str) -> bool:
        """
        Check if a feature is locked by this physique
        
        Returns:
            True if feature is locked (cannot use)
            False if feature is available
        """
        physique = self.get_physique(physique_id)
        if not physique:
            return False
        
        locks = physique.get('system_mechanics', {}).get('locks', [])
        return feature in locks
    
    def check_unlocks(self, physique_id: str, feature: str) -> bool:
        """
        Check if a feature is unlocked by this physique
        
        Returns:
            True if feature is unlocked (can use)
            False if feature is not available
        """
        physique = self.get_physique(physique_id)
        if not physique:
            return False
        
        unlocks = physique.get('system_mechanics', {}).get('unlocks', [])
        return feature in unlocks
    
    def get_modifiers(self, physique_id: str) -> Dict[str, Any]:
        """Get all modifiers for this physique"""
        physique = self.get_physique(physique_id)
        if not physique:
            return {}
        
        return physique.get('system_mechanics', {}).get('modifiers', {})
    
    def apply_cultivation_lock(self, physique_id: str) -> bool:
        """Check if cultivation is locked"""
        return self.check_locks(physique_id, 'cultivation_qi_absorption')
    
    def apply_cultivation_speed(self, physique_id: str, base_speed: float) -> float:
        """Apply cultivation speed modifier"""
        modifiers = self.get_modifiers(physique_id)
        multiplier = modifiers.get('cultivation_speed_multiplier', 1.0)
        return base_speed * multiplier
    
    def apply_enlightenment_rate(self, physique_id: str, base_rate: float) -> float:
        """Apply enlightenment rate modifier"""
        modifiers = self.get_modifiers(physique_id)
        multiplier = modifiers.get('enlightenment_rate_multiplier', 1.0)
        return base_rate * multiplier
    
    def apply_heart_demon_points(self, physique_id: str, base_points: int) -> int:
        """Add heart demon points per cultivation"""
        modifiers = self.get_modifiers(physique_id)
        points_per_cultivation = modifiers.get('heart_demon_points_per_cultivation', 0)
        return base_points + points_per_cultivation
    
    def check_heart_demon_threshold(self, physique_id: str, current_points: int) -> bool:
        """Check if heart demon threshold is reached"""
        modifiers = self.get_modifiers(physique_id)
        threshold = modifiers.get('heart_demon_threshold', 999)
        return current_points >= threshold
    
    def apply_hp_regen(self, physique_id: str, base_hp: float, current_hp: float) -> float:
        """Apply HP regeneration"""
        modifiers = self.get_modifiers(physique_id)
        regen_percent = modifiers.get('hp_regen_percent_per_3s', 0.0)
        if regen_percent > 0:
            return min(base_hp, current_hp + (base_hp * regen_percent))
        return current_hp
    
    def can_revive(self, physique_id: str, revives_this_week: int) -> bool:
        """Check if can revive this week"""
        modifiers = self.get_modifiers(physique_id)
        revives_per_week = modifiers.get('revive_per_week', 0)
        return revives_per_week > 0 and revives_this_week < revives_per_week
    
    def get_revive_hp(self, physique_id: str, base_hp: float) -> float:
        """Get HP after revive"""
        modifiers = self.get_modifiers(physique_id)
        revive_hp_percent = modifiers.get('revive_hp_percent', 0.3)
        return base_hp * revive_hp_percent
    
    def can_learn_technique(self, physique_id: str, technique_element: str) -> bool:
        """Check if can learn technique of this element"""
        modifiers = self.get_modifiers(physique_id)
        can_learn_all = modifiers.get('can_learn_all_techniques', False)
        if can_learn_all:
            return True
        
        # Check if technique element matches physique element
        physique = self.get_physique(physique_id)
        if not physique:
            return True  # Default: can learn
        
        physique_element = physique.get('element', '')
        if physique_element == 'Vô' or physique_element == 'Hỗn Độn':
            return True
        
        return technique_element == physique_element
    
    def get_technique_growth_multiplier(self, physique_id: str) -> float:
        """Get technique growth multiplier"""
        modifiers = self.get_modifiers(physique_id)
        return modifiers.get('technique_growth_multiplier', 1.0)
    
    def get_damage_reduction(self, physique_id: str) -> float:
        """Get damage reduction percent"""
        modifiers = self.get_modifiers(physique_id)
        return modifiers.get('damage_reduction_percent', 0.0)
    
    def get_heart_demon_resistance(self, physique_id: str) -> float:
        """Get heart demon resistance"""
        modifiers = self.get_modifiers(physique_id)
        return modifiers.get('heart_demon_resistance', 0.0)
    
    def get_all_physiques(self) -> List[Dict[str, Any]]:
        """Get all physiques"""
        return list(self.physiques.values())
    
    def random_physique(self, tier: Optional[str] = None) -> Optional[str]:
        """Get random physique ID"""
        import random
        
        candidates = list(self.physiques.keys())
        
        if tier:
            candidates = [
                p['id'] for p in self.physiques.values() 
                if p.get('tier') == tier
            ]
        
        if candidates:
            return random.choice(candidates)
        return None

