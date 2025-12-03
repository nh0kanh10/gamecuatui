"""
World Bible - Hard Facts về thế giới (Enhanced)
Dựa trên đánh giá: Better validation, auto-correct, realm hierarchy
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Set, Any
from enum import Enum
from pathlib import Path
import json


class RealmTier(str, Enum):
    """Realm tier enum để match với BreakthroughMechanics"""
    QI_REFINING = "Qi_Refining"
    FOUNDATION = "Foundation"
    GOLDEN_CORE = "Golden_Core"
    NASCENT_SOUL = "Nascent_Soul"
    SPIRIT_TRANSFORMATION = "Spirit_Transformation"
    BODY_FUSION = "Body_Fusion"
    GREAT_MULTIPLICATION = "Great_Multiplication"
    IMMORTAL = "Immortal"
    MAHAYANA = "Mahayana"


class WorldBible(BaseModel):
    """
    World Bible chứa các facts bất biến về thế giới
    
    Cải tiến:
    - Realm hierarchy để validate abilities theo tier
    - Auto-correct logic cho các lỗi đơn giản
    - Better validation cho stats, pills, artifacts
    - Integration với BreakthroughMechanics
    """
    
    # World Rules
    world_rules: Dict[str, Any] = Field(default_factory=lambda: {
        "max_realm": "Mahayana",
        "resurrection": "impossible",
        "flying_requires": "Foundation",  # Bay được từ Trúc Cơ trở lên
        "teleportation": "impossible",
        "time_travel": "impossible",
        "immortality": "requires_Immortal_realm",
    })
    
    # Realm System với hierarchy
    realms: List[Dict[str, Any]] = Field(default_factory=lambda: [
        {
            "name": "Qi_Refining",
            "display": "Luyện Khí",
            "tier": 1,  # Thêm tier để so sánh
            "levels": 13,
            "lifespan": (100, 120),
            "abilities": ["Talismans", "5-10x strength"],
            "next": "Foundation"
        },
        {
            "name": "Foundation",
            "display": "Trúc Cơ",
            "tier": 2,
            "levels": 4,
            "lifespan": (200, 250),
            "abilities": ["Divine Sense", "Sword Flight", "Fasting"],
            "next": "Golden_Core"
        },
        {
            "name": "Golden_Core",
            "display": "Kim Đan",
            "tier": 3,
            "levels": 4,
            "lifespan": (500, 800),
            "abilities": ["Golden Core", "Longevity", "Soul Projection"],
            "next": "Nascent_Soul"
        },
        {
            "name": "Nascent_Soul",
            "display": "Nguyên Anh",
            "tier": 4,
            "levels": 4,
            "lifespan": (2000, 5000),
            "abilities": ["Nascent Soul", "Soul Separation", "Reincarnation"],
            "next": "Spirit_Transformation"
        },
        {
            "name": "Spirit_Transformation",
            "display": "Hóa Thần",
            "tier": 5,
            "levels": 4,
            "lifespan": (10000, 50000),
            "abilities": ["Spirit Transformation", "Divine Sense Range"],
            "next": "Body_Fusion"
        },
        {
            "name": "Body_Fusion",
            "display": "Hợp Thể",
            "tier": 6,
            "levels": 4,
            "lifespan": (100000, 1000000),
            "abilities": ["Body Fusion", "Immortality"],
            "next": "Great_Multiplication"
        },
        {
            "name": "Great_Multiplication",
            "display": "Đại Thừa",
            "tier": 7,
            "levels": 4,
            "lifespan": (1000000, "infinite"),
            "abilities": ["Great Multiplication", "World Creation"],
            "next": "Immortal"
        },
        {
            "name": "Immortal",
            "display": "Tiên",
            "tier": 8,
            "levels": 4,
            "lifespan": "immortal",
            "abilities": ["True Immortality", "Reality Manipulation"],
            "next": "Mahayana"
        },
        {
            "name": "Mahayana",
            "display": "Đại Thừa",
            "tier": 9,
            "levels": 4,
            "lifespan": "transcendent",
            "abilities": ["Transcendence", "Universe Creation"],
            "next": None
        }
    ])
    
    # Cultivation Rules
    cultivation_rules: Dict[str, Any] = Field(default_factory=lambda: {
        "breakthrough_never_guaranteed": True,
        "tribulation_on_failure": True,
        "death_on_tribulation_failure": True,
        "cultivation_crippled_on_failure": True,
        "max_breakthrough_attempts": None,
    })
    
    # Social Rules
    social_rules: Dict[str, Any] = Field(default_factory=lambda: {
        "killing_innocents_penalty": True,
        "karma_affects_realm_limit": True,
        "relationships_matter": True,
        "sect_hierarchy": True,
    })
    
    # Item Rules
    item_rules: Dict[str, Any] = Field(default_factory=lambda: {
        "artifacts_have_history": True,
        "pills_have_side_effects": True,
        "weapons_can_break": True,
        "spirit_stones_are_currency": True,
    })
    
    def get_realm_by_name(self, realm_name: str) -> Optional[Dict[str, Any]]:
        """Get realm data by name"""
        return next((r for r in self.realms if r["name"] == realm_name), None)
    
    def get_realm_tier(self, realm_name: str) -> Optional[int]:
        """Get realm tier number"""
        realm = self.get_realm_by_name(realm_name)
        return realm.get("tier") if realm else None
    
    def can_use_ability(self, realm_name: str, ability: str) -> bool:
        """
        Check if realm can use ability (với hierarchy check)
        
        Cải tiến: Check theo tier, không chỉ exact match
        """
        realm = self.get_realm_by_name(realm_name)
        if not realm:
            return False
        
        # Check exact abilities
        if ability in realm.get("abilities", []):
            return True
        
        # Check hierarchy: abilities từ realm thấp hơn cũng có thể dùng
        current_tier = realm.get("tier", 0)
        for r in self.realms:
            if r.get("tier", 0) <= current_tier and ability in r.get("abilities", []):
                return True
        
        return False
    
    def get_pre_prompt_text(self) -> str:
        """Tạo text để chèn vào AI prompt"""
        text = """
=== WORLD BIBLE - HARD FACTS ===

CHỈ ĐƯỢC SỬ DỤNG THÔNG TIN TRONG PHẦN NÀY.
NẾU KHÔNG BIẾT, HÃY TRẢ LỜI "KHÔNG BIẾT".
KHÔNG ĐƯỢC BỊA ĐẶT.

World Rules:
"""
        for key, value in self.world_rules.items():
            text += f"- {key}: {value}\n"
        
        text += "\nRealm System (Hierarchy):\n"
        for realm in self.realms:
            text += f"- Tier {realm['tier']}: {realm['display']} ({realm['name']}): {realm['levels']} levels\n"
            text += f"  Abilities: {', '.join(realm['abilities'])}\n"
        
        text += "\nCultivation Rules:\n"
        for key, value in self.cultivation_rules.items():
            text += f"- {key}: {value}\n"
        
        text += "\nSocial Rules:\n"
        for key, value in self.social_rules.items():
            text += f"- {key}: {value}\n"
        
        text += "\nItem Rules:\n"
        for key, value in self.item_rules.items():
            text += f"- {key}: {value}\n"
        
        text += "\n=== END WORLD BIBLE ===\n"
        
        return text
    
    def verify_output(self, ai_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kiểm tra AI output có vi phạm World Bible không
        
        Cải tiến:
        - Check realm hierarchy
        - Auto-correct các lỗi đơn giản
        - Check stats, pills, artifacts
        """
        violations = []
        corrected = ai_output.copy()
        
        # Check realm claims
        if "realm" in ai_output:
            realm_name = ai_output["realm"]
            valid_realms = [r["name"] for r in self.realms]
            if realm_name not in valid_realms:
                violations.append(f"Invalid realm: {realm_name}")
                # Auto-correct: tìm realm gần nhất
                if "Qi" in realm_name or "Refining" in realm_name:
                    corrected["realm"] = "Qi_Refining"
                elif "Foundation" in realm_name or "Trúc" in realm_name:
                    corrected["realm"] = "Foundation"
                elif "Golden" in realm_name or "Core" in realm_name or "Kim" in realm_name:
                    corrected["realm"] = "Golden_Core"
        
        # Check abilities với hierarchy
        if "abilities" in ai_output:
            current_realm = corrected.get("realm", "Qi_Refining")
            claimed_abilities = ai_output["abilities"]
            invalid_abilities = []
            
            for ability in claimed_abilities:
                if not self.can_use_ability(current_realm, ability):
                    invalid_abilities.append(ability)
                    violations.append(f"Ability '{ability}' not available at {current_realm}")
            
            # Auto-correct: remove invalid abilities
            if invalid_abilities:
                corrected["abilities"] = [a for a in claimed_abilities if a not in invalid_abilities]
        
        # Check world rules violations
        if "action" in ai_output:
            action = ai_output["action"].lower()
            current_realm = corrected.get("realm", "Qi_Refining")
            
            if "fly" in action or "bay" in action:
                required_realm = self.world_rules.get("flying_requires", "Foundation")
                realm_tier = self.get_realm_tier(current_realm)
                required_tier = self.get_realm_tier(required_realm)
                
                if realm_tier and required_tier and realm_tier < required_tier:
                    violations.append(f"Cannot fly before {required_realm} realm")
                    # Auto-correct: reject action
                    corrected["action"] = "walk"  # Thay bằng đi bộ
            
            if "teleport" in action or "dịch chuyển" in action:
                violations.append("Teleportation is impossible")
                corrected["action"] = "move"  # Thay bằng di chuyển thường
            
            if "resurrect" in action or "sống lại" in action:
                violations.append("Resurrection is impossible")
                corrected["action"] = None  # Reject action
        
        # Check stats consistency
        if "stats" in ai_output:
            stats = ai_output["stats"]
            valid_stats = ["CON", "INT", "PER", "LUK", "CHA", "KAR"]
            invalid_stats = [s for s in stats.keys() if s not in valid_stats]
            
            if invalid_stats:
                violations.append(f"Invalid stats: {invalid_stats}")
                # Auto-correct: remove invalid stats
                corrected["stats"] = {k: v for k, v in stats.items() if k in valid_stats}
        
        # Check pills/artifacts (nếu có)
        if "use_item" in ai_output:
            item_name = ai_output.get("use_item", "")
            # TODO: Check against item database
            # For now, just log
            pass
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "corrected": corrected if violations else None
        }
    
    @classmethod
    def load_from_file(cls, file_path: str) -> "WorldBible":
        """Load World Bible từ JSON file"""
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        return cls()
    
    def save_to_file(self, file_path: str):
        """Save World Bible ra JSON file"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.dict(), f, ensure_ascii=False, indent=2)
