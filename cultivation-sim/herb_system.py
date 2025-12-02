"""
Herb System - Xử lý Thảo Dược
ECS System pattern
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from components import SpiritHerbComponent
from world_database import WorldDatabase


class HerbSystem:
    """
    Herb System - Xử lý growth, harvesting, preservation, alchemy
    """
    
    def __init__(self, world_db: WorldDatabase):
        self.world_db = world_db
    
    def calculate_potency(
        self,
        herb_component: SpiritHerbComponent
    ) -> float:
        """
        Calculate current potency
        
        Returns:
            Potency value
        """
        template = self.world_db.get_spirit_herb(herb_component.template_id)
        if not template:
            return 0.0
        
        return herb_component.calculate_potency(template)
    
    def get_tier(self, herb_component: SpiritHerbComponent) -> str:
        """Get herb tier based on age"""
        template = self.world_db.get_spirit_herb(herb_component.template_id)
        if not template:
            return "tier_mortal"
        
        return herb_component.get_tier(template)
    
    def harvest(
        self,
        herb_component: SpiritHerbComponent,
        player_level: int = 1
    ) -> Dict[str, Any]:
        """
        Harvest herb
        
        Returns:
            {
                "success": bool,
                "herb_id": str,
                "age": int,
                "potency": float,
                "tier": str,
                "yield": int  # Số lượng thu được
            }
        """
        if herb_component.harvested:
            return {
                "success": False,
                "message": "Herb đã được thu hoạch"
            }
        
        template = self.world_db.get_spirit_herb(herb_component.template_id)
        if not template:
            return {
                "success": False,
                "message": "Herb template not found"
            }
        
        # Calculate yield based on age and player level
        tier = herb_component.get_tier(template)
        base_yield = 1
        
        if tier == "tier_heavenly":
            base_yield = 3
        elif tier == "tier_earthly":
            base_yield = 2
        
        # Player level affects yield (higher level = better harvest)
        level_bonus = max(1, player_level // 10)
        yield_amount = base_yield * level_bonus
        
        # Mark as harvested
        herb_component.harvested = True
        herb_component.harvest_time = datetime.now().isoformat()
        
        # Calculate final potency
        potency = herb_component.calculate_potency(template)
        
        return {
            "success": True,
            "herb_id": herb_component.template_id,
            "age": herb_component.age,
            "potency": potency,
            "tier": tier,
            "yield": yield_amount,
            "origin_signature": herb_component.origin_signature
        }
    
    def apply_decay(
        self,
        herb_component: SpiritHerbComponent,
        days: int = 1,
        container_type: Optional[str] = None
    ):
        """
        Apply decay over time
        
        Args:
            days: Number of days passed
            container_type: Container type (if properly preserved)
        """
        template = self.world_db.get_spirit_herb(herb_component.template_id)
        if not template:
            return
        
        preservation = template.get("preservation", {})
        required_container = preservation.get("container_req", "")
        
        # Check if properly preserved
        if container_type == required_container:
            # No decay if properly preserved
            return
        
        # Apply decay
        herb_component.decay(template, days)
    
    def can_use_for_alchemy(
        self,
        herb_component: SpiritHerbComponent,
        pill_id: str
    ) -> bool:
        """Check if herb can be used to craft pill"""
        template = self.world_db.get_spirit_herb(herb_component.template_id)
        if not template:
            return False
        
        alchemy_uses = template.get("alchemy_uses", [])
        return pill_id in alchemy_uses
    
    def get_alchemy_bonus(
        self,
        herb_component: SpiritHerbComponent,
        pill_id: str
    ) -> Dict[str, Any]:
        """
        Get alchemy bonus from herb
        
        Returns:
            {
                "potency_bonus": float,
                "success_rate_bonus": float,
                "special_effects": List[str]
            }
        """
        template = self.world_db.get_spirit_herb(herb_component.template_id)
        if not template:
            return {
                "potency_bonus": 0.0,
                "success_rate_bonus": 0.0,
                "special_effects": []
            }
        
        potency = herb_component.calculate_potency(template)
        tier = herb_component.get_tier(template)
        
        # Calculate bonuses
        potency_bonus = potency * 0.1  # 10% of potency
        
        success_rate_bonus = 0.0
        if tier == "tier_heavenly":
            success_rate_bonus = 0.3
        elif tier == "tier_earthly":
            success_rate_bonus = 0.15
        elif tier == "tier_spirit":
            success_rate_bonus = 0.05
        
        # Origin signature bonus
        special_effects = []
        if herb_component.origin_signature:
            # Herbs from specific locations have special effects
            if "volcano" in herb_component.origin_signature.lower():
                special_effects.append("Fire_Affinity_Boost")
            elif "ice" in herb_component.origin_signature.lower():
                special_effects.append("Ice_Affinity_Boost")
        
        return {
            "potency_bonus": potency_bonus,
            "success_rate_bonus": success_rate_bonus,
            "special_effects": special_effects
        }
    
    def age_herb(self, herb_component: SpiritHerbComponent, years: int = 1):
        """Age herb (for growing herbs)"""
        herb_component.age += years
        
        # Recalculate potency
        template = self.world_db.get_spirit_herb(herb_component.template_id)
        if template:
            herb_component.potency = herb_component.calculate_potency(template)

