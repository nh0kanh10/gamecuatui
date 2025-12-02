"""
Cultivation-specific components for Cultivation Simulator
Standalone version (không phụ thuộc engine/core)
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
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


class SpiritBeastComponent(BaseModel):
    """
    Spirit Beast instance component
    Based on Template + Instance pattern
    """
    template_id: str = Field(..., description="Reference to beast template")
    level: int = Field(default=1, ge=1, le=100, description="Current level")
    current_hp: int = Field(default=100, ge=0)
    max_hp: int = Field(default=100, gt=0)
    current_mp: int = Field(default=50, ge=0)
    max_mp: int = Field(default=50, gt=0)
    cultivation_realm: str = Field(default="Mortal", description="Current cultivation realm")
    cultivation_progress: float = Field(default=0.0, ge=0.0, le=100.0)
    mutations: Dict[str, float] = Field(default_factory=dict, description="Procedural mutations")
    bloodline_modifiers: List[Dict[str, Any]] = Field(default_factory=list)
    location_id: Optional[str] = None
    spawn_time: Optional[str] = None
    
    def calculate_stats(self, template: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate current stats based on template + level + mutations
        
        Formula: Stat = Base * (Growth ^ (Level - 1)) * Mutation_Multiplier
        """
        base_stats = template.get("combat_stats", {}).get("base", {})
        growth = template.get("combat_stats", {}).get("growth", {})
        
        stats = {}
        for stat_name in ["hp", "atk", "def", "spd", "mp"]:
            base = base_stats.get(stat_name, 0)
            growth_factor = growth.get(stat_name, 1.0)
            
            # Calculate: Base * (Growth ^ (Level - 1))
            calculated = base * (growth_factor ** (self.level - 1))
            
            # Apply mutations
            mutation_mult = self.mutations.get(stat_name, 1.0)
            stats[stat_name] = calculated * mutation_mult
        
        return stats
    
    def can_evolve(self, template: Dict[str, Any]) -> bool:
        """Check if can evolve to next form"""
        evolution_path = template.get("taxonomy", {}).get("evolution_path", [])
        if not evolution_path:
            return False
        
        # Check realm requirement
        max_realm = template.get("cultivation", {}).get("max_realm", "Mortal")
        return self.cultivation_realm == max_realm and self.cultivation_progress >= 100.0


class SpiritHerbComponent(BaseModel):
    """
    Spirit Herb instance component
    Based on Template + Instance pattern with age-based potency
    """
    template_id: str = Field(..., description="Reference to herb template")
    age: int = Field(default=1, ge=1, description="Age in years")
    potency: float = Field(default=10.0, ge=0.0, description="Current potency")
    potency_loss: float = Field(default=0.0, ge=0.0, le=1.0, description="Potency lost due to poor preservation")
    origin_signature: Optional[str] = Field(None, description="Origin location (affects alchemy)")
    harvested: bool = Field(default=False)
    harvest_time: Optional[str] = None
    
    def calculate_potency(self, template: Dict[str, Any]) -> float:
        """
        Calculate potency based on age and growth logic
        
        Formula depends on age_multiplier type:
        - Logarithmic: base * log10(age + 1)
        - Linear: base * age
        - Exponential: base * (1.1 ^ age)
        """
        import math
        
        base_potency = template.get("growth_logic", {}).get("base_potency", 10)
        age_multiplier_type = template.get("growth_logic", {}).get("age_multiplier", "Logarithmic")
        
        if age_multiplier_type == "Logarithmic":
            multiplier = math.log10(self.age + 1) + 1
        elif age_multiplier_type == "Linear":
            multiplier = self.age
        elif age_multiplier_type == "Exponential":
            multiplier = 1.1 ** (self.age / 100.0)  # Normalized
        else:
            multiplier = 1.0
        
        calculated_potency = base_potency * multiplier
        
        # Apply potency loss
        final_potency = calculated_potency * (1.0 - self.potency_loss)
        
        return final_potency
    
    def get_tier(self, template: Dict[str, Any]) -> str:
        """Get tier based on age thresholds"""
        thresholds = template.get("growth_logic", {}).get("thresholds", {})
        
        # Sort thresholds by age
        sorted_thresholds = sorted(
            [(int(k), v) for k, v in thresholds.items()],
            key=lambda x: x[0],
            reverse=True
        )
        
        for age_threshold, tier in sorted_thresholds:
            if self.age >= age_threshold:
                return tier
        
        return "tier_mortal"
    
    def decay(self, template: Dict[str, Any], days: int = 1):
        """Apply decay if not properly preserved"""
        decay_rate = template.get("preservation", {}).get("decay_rate", 0.05)
        self.potency_loss = min(1.0, self.potency_loss + decay_rate * days)

