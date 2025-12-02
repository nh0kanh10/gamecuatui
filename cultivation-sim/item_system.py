"""
Item System - Xử lý Vật Phẩm & Tài Nguyên
Dựa trên thiết kế: Consumables, Materials, Currency
"""

from typing import Dict, Any, Optional, List
from enum import Enum


class ItemType(str, Enum):
    """Item types"""
    CURRENCY = "Currency"
    PILL = "Pill"
    MATERIAL = "Material"
    TALISMAN = "Talisman"


class ItemSystem:
    """
    Item System - Xử lý items, pills, materials, currency
    """
    
    def __init__(self, world_db):
        self.world_db = world_db
    
    def use_item(
        self,
        item_id: str,
        player_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sử dụng item và áp dụng hiệu ứng
        
        Returns:
            {
                "success": bool,
                "effect_applied": Dict,
                "toxicity_added": int,
                "message": str
            }
        """
        item = self.world_db.get_item(item_id)
        if not item:
            return {
                "success": False,
                "effect_applied": {},
                "toxicity_added": 0,
                "message": "Item not found"
            }
        
        item_type = item.get("type")
        effect = item.get("effect", {})
        
        result = {
            "success": True,
            "effect_applied": {},
            "toxicity_added": 0,
            "message": ""
        }
        
        if item_type == "Pill":
            # Apply pill effect
            target = effect.get("target")
            value = effect.get("value", 0)
            duration = effect.get("duration", "instant")
            
            if target == "spiritual_power":
                # Increase spiritual power
                current_sp = player_state.get("cultivation", {}).get("spiritual_power", 0)
                max_sp = player_state.get("cultivation", {}).get("max_spiritual_power", 100)
                new_sp = min(max_sp, current_sp + value)
                result["effect_applied"]["spiritual_power"] = new_sp - current_sp
                result["message"] = f"Tăng {value} linh khí"
            
            elif target == "breakthrough_chance":
                # Increase breakthrough chance
                result["effect_applied"]["breakthrough_chance_bonus"] = value
                result["message"] = f"Tăng {value*100}% cơ hội đột phá"
            
            elif target == "toxicity":
                # Reduce toxicity
                result["effect_applied"]["toxicity"] = value
                result["message"] = f"Giảm {abs(value)} độc tính"
            
            # Add toxicity
            toxicity = item.get("toxicity", 0)
            result["toxicity_added"] = toxicity
            if toxicity > 0:
                result["message"] += f" (Tích độc +{toxicity})"
        
        elif item_type == "Talisman":
            # Apply talisman effect
            action = effect.get("action")
            
            if action == "teleport_random":
                radius = effect.get("radius", 100)
                result["effect_applied"]["teleport"] = {
                    "radius": radius,
                    "unit": effect.get("unit", "li")
                }
                result["message"] = f"Dịch chuyển ngẫu nhiên trong bán kính {radius} dặm"
            
            elif action == "shield":
                damage_absorb = effect.get("damage_absorb", 200)
                duration = effect.get("duration", 3600)
                result["effect_applied"]["shield"] = {
                    "damage_absorb": damage_absorb,
                    "duration": duration
                }
                result["message"] = f"Tạo lá chắn hấp thụ {damage_absorb} sát thương"
        
        return result
    
    def get_item_value(self, item_id: str) -> int:
        """Get item value (for currency)"""
        item = self.world_db.get_item(item_id)
        if not item:
            return 0
        
        if item.get("type") == "Currency":
            return item.get("value", 0)
        
        return 0
    
    def get_materials_at_location(self, location_id: str) -> List[Dict[str, Any]]:
        """Get materials that can be found at a location"""
        materials = self.world_db.get_materials_by_location(location_id)
        return [
            {
                "id": m["id"],
                "name": m["name"],
                "type": m["type"],
                "element": m.get("element"),
                "grade": m.get("grade", 1),
                "lore": m.get("lore", "")
            }
            for m in materials
        ]
    
    def can_craft_artifact(
        self,
        artifact_id: str,
        inventory: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Check if player has enough materials to craft artifact
        
        Returns:
            {
                "can_craft": bool,
                "missing_materials": Dict[str, int],
                "required_materials": Dict[str, int]
            }
        """
        artifact = self.world_db.get_artifact(artifact_id)
        if not artifact:
            return {
                "can_craft": False,
                "missing_materials": {},
                "required_materials": {}
            }
        
        required = artifact.get("crafting_materials", [])
        if not required:
            return {
                "can_craft": False,
                "missing_materials": {},
                "required_materials": {},
                "reason": "Artifact cannot be crafted"
            }
        
        missing = {}
        required_dict = {}
        
        for material_id in required:
            required_dict[material_id] = required_dict.get(material_id, 0) + 1
            if inventory.get(material_id, 0) < required_dict[material_id]:
                missing[material_id] = required_dict[material_id] - inventory.get(material_id, 0)
        
        return {
            "can_craft": len(missing) == 0,
            "missing_materials": missing,
            "required_materials": required_dict
        }

