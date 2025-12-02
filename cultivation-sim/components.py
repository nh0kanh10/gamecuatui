"""
Cultivation-specific components for Cultivation Simulator
Standalone version (không phụ thuộc engine/core)
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class CultivationComponent(BaseModel):
    """
    Cultivation realm and progress tracking
    For Xianxia/Tu Tiên games
    """
    realm: str = Field(
        default="Mortal",
        description="Current cultivation realm (e.g., 'Qi Refining', 'Foundation Building')"
    )
    realm_level: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Level within current realm (0-10)"
    )
    spiritual_power: int = Field(
        default=0,
        ge=0,
        description="Current spiritual power/qi"
    )
    max_spiritual_power: int = Field(
        default=100,
        gt=0,
        description="Maximum spiritual power for current realm"
    )
    breakthrough_progress: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Progress to next realm (0-100%)"
    )
    techniques: List[str] = Field(
        default_factory=list,
        description="Learned cultivation techniques"
    )
    pills_consumed: int = Field(
        default=0,
        ge=0,
        description="Total pills consumed"
    )
    spirit_stones: int = Field(
        default=0,
        ge=0,
        description="Spirit stones owned"
    )
    cultivation_age: int = Field(
        default=0,
        ge=0,
        description="Years spent cultivating"
    )
    
    def get_realm_tier(self) -> str:
        """Get realm tier category"""
        realm_lower = self.realm.lower()
        if "mortal" in realm_lower or "qi refining" in realm_lower:
            return "Mortal"
        elif "foundation" in realm_lower:
            return "Foundation"
        elif "core" in realm_lower:
            return "Core Formation"
        elif "nascent" in realm_lower or "soul" in realm_lower:
            return "Nascent Soul"
        elif "deity" in realm_lower or "immortal" in realm_lower:
            return "Immortal"
        return "Unknown"
    
    def can_breakthrough(self) -> bool:
        """Check if can breakthrough to next realm"""
        return (
            self.realm_level >= 10 and
            self.breakthrough_progress >= 100.0 and
            self.spiritual_power >= self.max_spiritual_power
        )


class ResourceComponent(BaseModel):
    """
    Cultivation resources (spirit stones, pills, materials)
    """
    spirit_stones: int = Field(
        default=0,
        ge=0,
        description="Spirit stones owned"
    )
    pills: Dict[str, int] = Field(
        default_factory=dict,
        description="Pills owned (name -> quantity)"
    )
    materials: Dict[str, int] = Field(
        default_factory=dict,
        description="Cultivation materials (name -> quantity)"
    )
    
    def add_pill(self, pill_name: str, quantity: int = 1):
        """Add pills"""
        if pill_name not in self.pills:
            self.pills[pill_name] = 0
        self.pills[pill_name] += quantity
    
    def consume_pill(self, pill_name: str, quantity: int = 1) -> bool:
        """Consume pills, returns True if successful"""
        if pill_name not in self.pills or self.pills[pill_name] < quantity:
            return False
        self.pills[pill_name] -= quantity
        if self.pills[pill_name] <= 0:
            del self.pills[pill_name]
        return True
    
    def add_material(self, material_name: str, quantity: int = 1):
        """Add materials"""
        if material_name not in self.materials:
            self.materials[material_name] = 0
        self.materials[material_name] += quantity
    
    def get_total_pills(self) -> int:
        """Get total number of pills"""
        return sum(self.pills.values())

