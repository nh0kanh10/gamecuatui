"""
Spirit Beast System - Xử lý Linh Thú
ECS System pattern
"""

from typing import Dict, List, Optional, Any
from components import SpiritBeastComponent
from world_database import WorldDatabase


class SpiritBeastSystem:
    """
    Spirit Beast System - Xử lý combat, growth, evolution
    """
    
    def __init__(self, world_db: WorldDatabase):
        self.world_db = world_db
    
    def calculate_combat_stats(
        self,
        beast_component: SpiritBeastComponent
    ) -> Dict[str, float]:
        """
        Calculate combat stats từ template + component
        
        Returns:
            {"hp": float, "atk": float, "def": float, "spd": float, "mp": float}
        """
        template = self.world_db.get_spirit_beast(beast_component.template_id)
        if not template:
            return {}
        
        return beast_component.calculate_stats(template)
    
    def take_damage(
        self,
        beast_component: SpiritBeastComponent,
        damage: int
    ) -> Dict[str, Any]:
        """
        Apply damage to beast
        
        Returns:
            {"hp_remaining": int, "is_dead": bool, "damage_taken": int}
        """
        damage_taken = min(damage, beast_component.current_hp)
        beast_component.current_hp -= damage_taken
        
        return {
            "hp_remaining": beast_component.current_hp,
            "is_dead": beast_component.current_hp <= 0,
            "damage_taken": damage_taken
        }
    
    def level_up(self, beast_component: SpiritBeastComponent):
        """Level up beast và update stats"""
        beast_component.level += 1
        
        # Update HP/MP based on new level
        template = self.world_db.get_spirit_beast(beast_component.template_id)
        if template:
            new_stats = beast_component.calculate_stats(template)
            beast_component.max_hp = int(new_stats.get("hp", beast_component.max_hp))
            beast_component.max_mp = int(new_stats.get("mp", beast_component.max_mp))
            
            # Heal to full
            beast_component.current_hp = beast_component.max_hp
            beast_component.current_mp = beast_component.max_mp
    
    def cultivate(self, beast_component: SpiritBeastComponent, qi_gain: float):
        """
        Beast tu luyện, tăng cultivation progress
        
        Args:
            qi_gain: Amount of qi gained
        """
        template = self.world_db.get_spirit_beast(beast_component.template_id)
        if not template:
            return
        
        cultivation_data = template.get("cultivation", {})
        if not cultivation_data.get("can_cultivate", False):
            return
        
        # Calculate cultivation speed
        cultivation_speed = cultivation_data.get("cultivation_speed", 1.0)
        effective_qi = qi_gain * cultivation_speed
        
        # Update progress
        beast_component.cultivation_progress += effective_qi
        
        # Check for realm breakthrough
        max_realm = cultivation_data.get("max_realm", "Mortal")
        if beast_component.cultivation_progress >= 100.0:
            # Can breakthrough (logic handled by breakthrough system)
            pass
    
    def can_evolve(self, beast_component: SpiritBeastComponent) -> bool:
        """Check if beast can evolve"""
        template = self.world_db.get_spirit_beast(beast_component.template_id)
        if not template:
            return False
        
        return beast_component.can_evolve(template)
    
    def evolve(self, beast_component: SpiritBeastComponent) -> Optional[str]:
        """
        Evolve beast to next form
        
        Returns:
            New template_id hoặc None
        """
        template = self.world_db.get_spirit_beast(beast_component.template_id)
        if not template:
            return None
        
        evolution_path = template.get("taxonomy", {}).get("evolution_path", [])
        if not evolution_path:
            return None
        
        # Evolve to first form in path
        new_template_id = evolution_path[0]
        beast_component.template_id = new_template_id
        
        # Reset cultivation progress
        beast_component.cultivation_progress = 0.0
        
        return new_template_id
    
    def apply_bloodline_modifiers(
        self,
        beast_component: SpiritBeastComponent
    ) -> Dict[str, float]:
        """
        Apply bloodline modifiers to stats
        
        Returns:
            Stat modifiers dict
        """
        modifiers = {}
        
        for bloodline_mod in beast_component.bloodline_modifiers:
            bloodline_name = bloodline_mod.get("bloodline", "")
            percentage = bloodline_mod.get("percentage", 0.0)
            
            # Get bloodline effects from template
            template = self.world_db.get_spirit_beast(beast_component.template_id)
            if not template:
                continue
            
            # Example: Dragon bloodline → +HP, +DEF
            if "Dragon" in bloodline_name:
                modifiers["hp"] = modifiers.get("hp", 1.0) + (percentage / 100.0 * 0.2)
                modifiers["def"] = modifiers.get("def", 1.0) + (percentage / 100.0 * 0.15)
            elif "Phoenix" in bloodline_name:
                modifiers["mp"] = modifiers.get("mp", 1.0) + (percentage / 100.0 * 0.25)
                modifiers["atk"] = modifiers.get("atk", 1.0) + (percentage / 100.0 * 0.1)
            elif "Qilin" in bloodline_name:
                modifiers["spd"] = modifiers.get("spd", 1.0) + (percentage / 100.0 * 0.3)
        
        return modifiers

