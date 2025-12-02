"""
Artifact System - Xử lý Pháp Bảo
Dựa trên thiết kế: 5 tiers, special mechanics, damage calculation
"""

from typing import Dict, Any, Optional
from enum import Enum


class ArtifactTier(str, Enum):
    """5 tiers of artifacts"""
    ARTIFACT = "Artifact"  # Pháp Khí
    SPIRIT_TOOL = "Spirit_Tool"  # Linh Khí
    MAGIC_TREASURE = "Magic_Treasure"  # Pháp Bảo
    ANCIENT_TREASURE = "Ancient_Treasure"  # Cổ Bảo
    HEAVENLY_TREASURE = "Heavenly_Treasure"  # Thông Thiên Linh Bảo


class ArtifactSystem:
    """
    Artifact System - Tính toán sát thương và hiệu ứng pháp bảo
    """
    
    def __init__(self, world_db):
        self.world_db = world_db
    
    def calculate_artifact_damage(
        self,
        player_stats: Dict[str, Any],
        artifact_id: str,
        target_defense: int = 0
    ) -> Dict[str, Any]:
        """
        Tính sát thương dựa trên chỉ số người chơi + chỉ số pháp bảo
        
        Returns:
            {
                "base_damage": int,
                "element_bonus": float,
                "qi_power": float,
                "special_bonus": float,
                "total_damage": int,
                "damage_breakdown": str
            }
        """
        artifact = self.world_db.get_artifact(artifact_id)
        if not artifact:
            return {
                "base_damage": 0,
                "element_bonus": 1.0,
                "qi_power": 0,
                "special_bonus": 0,
                "total_damage": 0,
                "damage_breakdown": "Artifact not found"
            }
        
        base_dmg = artifact.get("stats", {}).get("attack", 0)
        
        # Element bonus (Ngũ hành tương sinh)
        element_bonus = 1.0
        player_element = player_stats.get("element", "None")
        artifact_element = artifact.get("element", "None")
        
        if player_element == artifact_element:
            element_bonus = 1.2  # 20% bonus khi cùng element
        
        # Qi power bonus (từ cảnh giới)
        current_qi = player_stats.get("current_qi", 0)
        max_qi = player_stats.get("max_qi", 100)
        qi_ratio = current_qi / max_qi if max_qi > 0 else 0
        qi_power = qi_ratio * 10  # 10 dmg per 100% qi
        
        # Special mechanic bonus
        special_bonus = 0
        special_mechanic = artifact.get("special_mechanic")
        damage_breakdown_parts = []
        
        if special_mechanic == "Soul_Stacking":
            # Cộng thêm dmg dựa trên số linh hồn đã thu thập
            current_souls = artifact.get("current_souls", 0)
            special_bonus = current_souls * 0.5
            damage_breakdown_parts.append(f"Soul Stacking: +{special_bonus:.1f} dmg ({current_souls} souls)")
        
        elif special_mechanic == "Dragon_Slayer":
            # 3x damage against dragons
            target_type = player_stats.get("target_type", "normal")
            if target_type == "dragon":
                special_bonus = base_dmg * 2.0  # Additional 2x on top of base
                damage_breakdown_parts.append(f"Dragon Slayer: +{special_bonus:.1f} dmg vs dragons")
        
        # Calculate total damage
        element_dmg = base_dmg * element_bonus
        total_dmg = element_dmg + qi_power + special_bonus - target_defense
        
        # Build damage breakdown
        damage_breakdown = f"Base: {base_dmg}"
        if element_bonus > 1.0:
            damage_breakdown += f" × {element_bonus:.1f} (Element)"
        damage_breakdown += f" + {qi_power:.1f} (Qi Power)"
        if special_bonus > 0:
            damage_breakdown += f" + {special_bonus:.1f} (Special)"
        damage_breakdown += f" - {target_defense} (Defense) = {max(1, int(total_dmg))}"
        
        return {
            "base_damage": base_dmg,
            "element_bonus": element_bonus,
            "qi_power": qi_power,
            "special_bonus": special_bonus,
            "total_damage": max(1, int(total_dmg)),
            "damage_breakdown": damage_breakdown,
            "special_effects": self._get_special_effects(artifact)
        }
    
    def _get_special_effects(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Get special effects from artifact"""
        special_mechanic = artifact.get("special_mechanic")
        special_effect = artifact.get("special_effect", {})
        
        if not special_mechanic:
            return {}
        
        effects = {
            "mechanic": special_mechanic,
            "effect": special_effect
        }
        
        # Add heavenly law if present
        if artifact.get("tier") == "Heavenly_Treasure":
            effects["heavenly_law"] = artifact.get("heavenly_law", "")
        
        return effects
    
    def can_use_artifact(
        self,
        artifact_id: str,
        current_realm: str,
        attributes: Dict[str, float]
    ) -> Dict[str, Any]:
        """Check if player can use artifact"""
        return self.world_db.check_artifact_requirements(
            artifact_id, current_realm, attributes
        )
    
    def get_artifact_info(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Get full artifact information"""
        artifact = self.world_db.get_artifact(artifact_id)
        if not artifact:
            return None
        
        return {
            "id": artifact_id,
            "name": artifact.get("name"),
            "tier": artifact.get("tier"),
            "realm_requirement": artifact.get("realm_requirement"),
            "element": artifact.get("element"),
            "stats": artifact.get("stats", {}),
            "special_mechanic": artifact.get("special_mechanic"),
            "special_effect": artifact.get("special_effect", {}),
            "lore": artifact.get("lore", ""),
            "can_store_in_body": artifact.get("can_store_in_body", False),
            "cannot_upgrade": artifact.get("cannot_upgrade", False)
        }

