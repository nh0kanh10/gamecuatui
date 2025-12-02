"""
Skill System với JSON Schema và Validator-Executor Pattern
Hỗ trợ modding và tùy biến kỹ năng vô hạn
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
from pathlib import Path


class SkillType(str, Enum):
    """Loại kỹ năng"""
    OFFENSIVE = "Offensive"
    DEFENSIVE = "Defensive"
    SUPPORT = "Support"
    MOVEMENT = "Movement"
    CULTIVATION = "Cultivation"


class ElementType(str, Enum):
    """Ngũ hành"""
    FIRE = "Fire"
    WATER = "Water"
    EARTH = "Earth"
    METAL = "Metal"
    WOOD = "Wood"
    NONE = "None"


class CastChecker(BaseModel):
    """
    Base class cho các checker trong validation chain
    """
    checker_type: str = Field(..., description="Type of checker (CooldownChecker, ManaCostChecker, etc.)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Checker parameters")
    
    def check(self, caster: Dict[str, Any], skill_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Check if condition is met
        
        Returns:
            (is_valid, error_message)
        """
        raise NotImplementedError


class CooldownChecker(CastChecker):
    """Check cooldown"""
    def check(self, caster: Dict[str, Any], skill_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        skill_id = skill_data.get("id")
        cooldown = skill_data.get("cooldown", 0)
        
        # Get last cast time from caster state
        last_cast = caster.get("skill_cooldowns", {}).get(skill_id, 0)
        current_time = caster.get("current_time", 0)
        
        if current_time - last_cast < cooldown:
            remaining = cooldown - (current_time - last_cast)
            return False, f"Kỹ năng đang trong thời gian hồi ({remaining}s còn lại)"
        
        return True, None


class ManaCostChecker(CastChecker):
    """Check mana/qi cost"""
    def check(self, caster: Dict[str, Any], skill_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        cost = skill_data.get("mana_cost", 0)
        current_mp = caster.get("current_mp", 0)
        
        if current_mp < cost:
            return False, f"Không đủ MP (cần {cost}, hiện có {current_mp})"
        
        return True, None


class ElementalEnvironmentChecker(CastChecker):
    """Check elemental environment compatibility"""
    def check(self, caster: Dict[str, Any], skill_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required_element = skill_data.get("element", ElementType.NONE)
        if required_element == ElementType.NONE:
            return True, None
        
        location = caster.get("location", {})
        location_elements = location.get("qi_affinity", [])
        
        if required_element.value not in location_elements:
            return False, f"Kỹ năng {required_element.value} không thể dùng ở đây (môi trường: {location_elements})"
        
        return True, None


class RealmRequirementChecker(CastChecker):
    """Check cultivation realm requirement"""
    def check(self, caster: Dict[str, Any], skill_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        required_realm = skill_data.get("realm_requirement", None)
        if not required_realm:
            return True, None
        
        caster_realm = caster.get("cultivation", {}).get("realm", "Mortal")
        
        # Simple realm comparison (có thể mở rộng với realm hierarchy)
        realm_order = ["Mortal", "Qi_Refining", "Foundation", "Golden_Core", "Nascent_Soul"]
        try:
            caster_index = realm_order.index(caster_realm)
            required_index = realm_order.index(required_realm)
            
            if caster_index < required_index:
                return False, f"Cần cảnh giới {required_realm} trở lên (hiện tại: {caster_realm})"
        except ValueError:
            # Unknown realm, allow for now
            pass
        
        return True, None


class SkillCastRequest(BaseModel):
    """
    Execution request sau khi validation chain pass
    """
    skill_id: str
    caster_id: str
    target_id: Optional[str] = None
    target_position: Optional[Dict[str, float]] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SkillDefinition(BaseModel):
    """
    Skill definition với JSON Schema validation
    """
    id: str = Field(..., description="Unique skill ID")
    name: str = Field(..., description="Skill name")
    type: SkillType = Field(..., description="Skill type")
    element: ElementType = Field(default=ElementType.NONE, description="Elemental affinity")
    
    # Validation chain
    validators: List[Dict[str, Any]] = Field(default_factory=list, description="List of checker definitions")
    
    # Execution parameters
    mana_cost: int = Field(default=0, ge=0, description="MP/Qi cost")
    cooldown: int = Field(default=0, ge=0, description="Cooldown in seconds")
    realm_requirement: Optional[str] = Field(None, description="Required cultivation realm")
    
    # Damage/Effect
    damage_formula: Optional[str] = Field(None, description="Damage formula (e.g., 'attack * 1.5')")
    effect_type: Optional[str] = Field(None, description="Effect type (Damage, Heal, Buff, Debuff)")
    effect_value: Optional[float] = Field(None, description="Effect value")
    
    # Projectile/Spawn
    spawn_projectile: bool = Field(default=False, description="Spawn projectile")
    projectile_speed: Optional[float] = Field(None, description="Projectile speed")
    on_hit_effect: Optional[Dict[str, Any]] = Field(None, description="Effect when projectile hits")
    
    # Metadata
    description: str = Field(default="", description="Skill description")
    lore: Optional[str] = Field(None, description="Skill lore")
    
    @validator('validators', pre=True)
    def parse_validators(cls, v):
        """Parse validator definitions"""
        if isinstance(v, list):
            return v
        return []


class SkillSystem:
    """
    Skill System với Validator-Executor pattern
    """
    
    def __init__(self, skills_dir: str = "data/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, SkillDefinition] = {}
        self.checker_registry: Dict[str, type] = {
            "CooldownChecker": CooldownChecker,
            "ManaCostChecker": ManaCostChecker,
            "ElementalEnvironmentChecker": ElementalEnvironmentChecker,
            "RealmRequirementChecker": RealmRequirementChecker,
        }
        self.load_skills()
    
    def load_skills(self):
        """Load skills from JSON files"""
        if not self.skills_dir.exists():
            self.skills_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for json_file in self.skills_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Handle array or single object
                    if isinstance(data, list):
                        for skill_data in data:
                            skill = SkillDefinition(**skill_data)
                            self.skills[skill.id] = skill
                    else:
                        skill = SkillDefinition(**data)
                        self.skills[skill.id] = skill
            except Exception as e:
                print(f"❌ Error loading skill from {json_file}: {e}")
    
    def validate_cast(
        self,
        skill_id: str,
        caster: Dict[str, Any]
    ) -> tuple[bool, Optional[str], Optional[SkillCastRequest]]:
        """
        Validate skill cast through validation chain
        
        Returns:
            (is_valid, error_message, cast_request)
        """
        skill = self.skills.get(skill_id)
        if not skill:
            return False, f"Skill {skill_id} not found", None
        
        # Run validation chain
        for validator_def in skill.validators:
            checker_type = validator_def.get("checker_type")
            checker_class = self.checker_registry.get(checker_type)
            
            if not checker_class:
                continue  # Skip unknown checkers
            
            checker = checker_class(
                checker_type=checker_type,
                params=validator_def.get("params", {})
            )
            
            is_valid, error_msg = checker.check(caster, skill.dict())
            if not is_valid:
                return False, error_msg, None
        
        # All validators passed, create cast request
        cast_request = SkillCastRequest(
            skill_id=skill_id,
            caster_id=caster.get("id", "unknown"),
            target_id=caster.get("target_id"),
            target_position=caster.get("target_position"),
            parameters={}
        )
        
        return True, None, cast_request
    
    def execute_cast(
        self,
        cast_request: SkillCastRequest,
        caster: Dict[str, Any],
        target: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute skill cast
        
        Returns:
            Result dict với damage, effects, etc.
        """
        skill = self.skills.get(cast_request.skill_id)
        if not skill:
            return {"success": False, "error": "Skill not found"}
        
        result = {
            "success": True,
            "skill_id": skill.id,
            "skill_name": skill.name,
            "damage": 0,
            "effects": []
        }
        
        # Calculate damage if applicable
        if skill.damage_formula and skill.effect_type == "Damage":
            damage = self._calculate_damage(skill.damage_formula, caster, target)
            result["damage"] = damage
        
        # Apply effects
        if skill.effect_type:
            effect = {
                "type": skill.effect_type,
                "value": skill.effect_value or 0
            }
            result["effects"].append(effect)
        
        # Spawn projectile if needed
        if skill.spawn_projectile:
            result["projectile"] = {
                "speed": skill.projectile_speed or 1.0,
                "on_hit": skill.on_hit_effect or {}
            }
        
        # Update cooldown
        if cast_request.caster_id in caster:
            if "skill_cooldowns" not in caster:
                caster["skill_cooldowns"] = {}
            caster["skill_cooldowns"][skill.id] = caster.get("current_time", 0)
        
        return result
    
    def _calculate_damage(
        self,
        formula: str,
        caster: Dict[str, Any],
        target: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate damage from formula string
        
        Simple formula evaluation (có thể mở rộng với eval hoặc AST)
        """
        # Simple replacement (có thể dùng eval hoặc safer parser)
        attack = caster.get("attack", 0)
        defense = target.get("defense", 0) if target else 0
        
        # Replace variables
        formula = formula.replace("attack", str(attack))
        formula = formula.replace("defense", str(defense))
        
        # Simple evaluation (WARNING: eval is unsafe, should use AST parser)
        try:
            damage = eval(formula)
            return max(0, float(damage))
        except:
            return 0.0
    
    def get_skill(self, skill_id: str) -> Optional[SkillDefinition]:
        """Get skill definition"""
        return self.skills.get(skill_id)
    
    def get_skills_by_type(self, skill_type: SkillType) -> List[SkillDefinition]:
        """Get all skills of a type"""
        return [s for s in self.skills.values() if s.type == skill_type]
    
    def get_skills_by_element(self, element: ElementType) -> List[SkillDefinition]:
        """Get all skills of an element"""
        return [s for s in self.skills.values() if s.element == element]

