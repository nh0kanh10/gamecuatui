"""
Enhanced Breakthrough System với Rewrite Destiny và Tao Soul
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
import random
from breakthrough import BreakthroughMechanics, RealmTier, BreakthroughResult


class RewriteDestinyPerk(str, Enum):
    """Nghịch Thiên Cải Mệnh Perks"""
    BLOOD_TO_SHIELD = "blood_to_shield"  # Máu thành khiên
    DUAL_CULTIVATION = "dual_cultivation"  # Song tu nhiều hệ
    ELEMENTAL_FUSION = "elemental_fusion"  # Hợp nhất nguyên tố
    IMMORTAL_BODY = "immortal_body"  # Thân thể bất tử
    SOUL_SPLIT = "soul_split"  # Phân tách linh hồn
    TIME_DILATION = "time_dilation"  # Giãn nở thời gian
    REALITY_BEND = "reality_bend"  # Bẻ cong thực tại
    FATE_IGNORE = "fate_ignore"  # Bỏ qua số mệnh


class TaoSoulType(str, Enum):
    """Loại Đạo Hồn"""
    FIRE_TAO = "fire_tao"
    WATER_TAO = "water_tao"
    EARTH_TAO = "earth_tao"
    METAL_TAO = "metal_tao"
    WOOD_TAO = "wood_tao"
    SPACE_TAO = "space_tao"
    TIME_TAO = "time_tao"
    DESTRUCTION_TAO = "destruction_tao"
    CREATION_TAO = "creation_tao"


class TaoSoul(BaseModel):
    """Đạo Hồn"""
    soul_id: str
    soul_type: TaoSoulType
    purity: float = Field(default=1.0, ge=0.0, le=1.0, description="Độ tinh khiết (0-1)")
    power: int = Field(default=100, ge=0, description="Sức mạnh")
    element_affinity: List[str] = Field(default_factory=list, description="Nguyên tố tương hợp")
    domain_ability: Optional[str] = Field(None, description="Kỹ năng Lĩnh vực")
    lore: Optional[str] = Field(None, description="Lịch sử Đạo Hồn")


class RewriteDestinyPerkDefinition(BaseModel):
    """Định nghĩa Rewrite Destiny Perk"""
    perk_id: RewriteDestinyPerk
    name: str
    description: str
    effects: Dict[str, Any] = Field(default_factory=dict)
    requirements: Dict[str, Any] = Field(default_factory=dict)
    rarity: str = Field(default="common", description="Rarity: common, rare, legendary")


class EnhancedBreakthroughSystem:
    """
    Enhanced Breakthrough System với Rewrite Destiny và Tao Soul
    """
    
    def __init__(self):
        self.breakthrough_mechanics = BreakthroughMechanics()
        self.tao_souls: Dict[str, TaoSoul] = {}
        self.perk_definitions: Dict[RewriteDestinyPerk, RewriteDestinyPerkDefinition] = {}
        self._init_perk_definitions()
    
    def _init_perk_definitions(self):
        """Initialize perk definitions"""
        perks = [
            RewriteDestinyPerkDefinition(
                perk_id=RewriteDestinyPerk.BLOOD_TO_SHIELD,
                name="Huyết Hóa Thuẫn",
                description="Máu thành khiên, HP thấp tăng phòng thủ",
                effects={"defense_bonus_per_missing_hp": 0.1},
                rarity="rare"
            ),
            RewriteDestinyPerkDefinition(
                perk_id=RewriteDestinyPerk.DUAL_CULTIVATION,
                name="Song Tu",
                description="Tu luyện 2 hệ nguyên tố cùng lúc",
                effects={"dual_element_bonus": 1.5},
                rarity="legendary"
            ),
            RewriteDestinyPerkDefinition(
                perk_id=RewriteDestinyPerk.ELEMENTAL_FUSION,
                name="Nguyên Tố Hợp Nhất",
                description="Hợp nhất 2 nguyên tố thành nguyên tố mới",
                effects={"fusion_damage_bonus": 2.0},
                rarity="legendary"
            ),
            RewriteDestinyPerkDefinition(
                perk_id=RewriteDestinyPerk.IMMORTAL_BODY,
                name="Bất Tử Thân",
                description="Thân thể bất tử, không thể bị giết",
                effects={"immortality": True, "hp_regen": 10.0},
                rarity="legendary"
            ),
            RewriteDestinyPerkDefinition(
                perk_id=RewriteDestinyPerk.SOUL_SPLIT,
                name="Phân Hồn",
                description="Phân tách linh hồn, có thể tạo phân thân",
                effects={"clone_count": 1},
                rarity="rare"
            ),
            RewriteDestinyPerkDefinition(
                perk_id=RewriteDestinyPerk.TIME_DILATION,
                name="Thời Gian Giãn Nở",
                description="Làm chậm thời gian xung quanh",
                effects={"time_slow": 0.5},
                rarity="rare"
            ),
            RewriteDestinyPerkDefinition(
                perk_id=RewriteDestinyPerk.REALITY_BEND,
                name="Bẻ Cong Thực Tại",
                description="Thay đổi quy luật vật lý",
                effects={"reality_manipulation": True},
                rarity="legendary"
            ),
            RewriteDestinyPerkDefinition(
                perk_id=RewriteDestinyPerk.FATE_IGNORE,
                name="Nghịch Thiên",
                description="Bỏ qua số mệnh, tự tạo vận mệnh",
                effects={"fate_resistance": 1.0},
                rarity="legendary"
            ),
        ]
        
        for perk in perks:
            self.perk_definitions[perk.perk_id] = perk
    
    def attempt_breakthrough_with_perks(
        self,
        current_tier: RealmTier,
        target_tier: RealmTier,
        mental_state: float,
        modifiers: Dict[str, float],
        player_hp: int,
        max_hp: int,
        artifacts_defense: int = 0,
        consumables_shield: int = 0,
        willpower: float = 50.0,
        existing_perks: List[RewriteDestinyPerk] = None
    ) -> Dict[str, Any]:
        """
        Attempt breakthrough với Rewrite Destiny perks
        
        Returns:
            Breakthrough result với perks
        """
        existing_perks = existing_perks or []
        
        # Perform breakthrough
        result = self.breakthrough_mechanics.attempt_breakthrough(
            current_tier=current_tier,
            target_tier=target_tier,
            mental_state=mental_state,
            modifiers=modifiers,
            player_hp=player_hp,
            max_hp=max_hp,
            artifacts_defense=artifacts_defense,
            consumables_shield=consumables_shield,
            willpower=willpower
        )
        
        # If successful, roll for Rewrite Destiny perks
        if result["success"]:
            perks_rolled = self._roll_rewrite_destiny_perks(
                target_tier=target_tier,
                existing_perks=existing_perks
            )
            result["rewrite_destiny_perks"] = perks_rolled
        
        return result
    
    def _roll_rewrite_destiny_perks(
        self,
        target_tier: RealmTier,
        existing_perks: List[RewriteDestinyPerk]
    ) -> List[Dict[str, Any]]:
        """
        Roll for Rewrite Destiny perks
        
        Higher tier = more perks, better rarity
        """
        # Perk chance based on tier
        tier_perk_chance = {
            RealmTier.QI_REFINING: 0.0,  # No perks at low tier
            RealmTier.FOUNDATION: 0.1,
            RealmTier.GOLDEN_CORE: 0.3,
            RealmTier.NASCENT_SOUL: 0.5,
            RealmTier.SPIRIT_TRANSFORMATION: 0.7,
            RealmTier.BODY_FUSION: 0.9,
            RealmTier.GREAT_MULTIPLICATION: 1.0,
            RealmTier.IMMORTAL: 1.0,
            RealmTier.MAHAYANA: 1.0,
        }
        
        perk_chance = tier_perk_chance.get(target_tier, 0.0)
        
        if random.random() > perk_chance:
            return []
        
        # Roll 1-3 perks
        num_perks = random.randint(1, 3)
        perks_rolled = []
        
        # Filter available perks (not already owned)
        available_perks = [
            p for p in self.perk_definitions.values()
            if p.perk_id not in existing_perks
        ]
        
        # Weight by rarity
        rarity_weights = {
            "common": 0.5,
            "rare": 0.3,
            "legendary": 0.2
        }
        
        for _ in range(num_perks):
            if not available_perks:
                break
            
            # Weighted random
            weights = [rarity_weights.get(p.rarity, 0.1) for p in available_perks]
            selected = random.choices(available_perks, weights=weights, k=1)[0]
            
            perks_rolled.append({
                "perk_id": selected.perk_id.value,
                "name": selected.name,
                "description": selected.description,
                "effects": selected.effects,
                "rarity": selected.rarity
            })
            
            # Remove from available
            available_perks.remove(selected)
        
        return perks_rolled
    
    def collect_tao_soul(
        self,
        soul_type: TaoSoulType,
        purity: float = 1.0,
        power: int = 100
    ) -> TaoSoul:
        """
        Collect Tao Soul
        
        Returns:
            Tao Soul object
        """
        import uuid
        
        soul = TaoSoul(
            soul_id=str(uuid.uuid4()),
            soul_type=soul_type,
            purity=purity,
            power=power,
            element_affinity=[soul_type.value.replace("_tao", "").title()],
            domain_ability=self._get_domain_ability(soul_type),
            lore=self._get_tao_soul_lore(soul_type)
        )
        
        self.tao_souls[soul.soul_id] = soul
        return soul
    
    def _get_domain_ability(self, soul_type: TaoSoulType) -> str:
        """Get domain ability for soul type"""
        abilities = {
            TaoSoulType.FIRE_TAO: "Hỏa Vực",
            TaoSoulType.WATER_TAO: "Thủy Vực",
            TaoSoulType.EARTH_TAO: "Thổ Vực",
            TaoSoulType.METAL_TAO: "Kim Vực",
            TaoSoulType.WOOD_TAO: "Mộc Vực",
            TaoSoulType.SPACE_TAO: "Không Gian Vực",
            TaoSoulType.TIME_TAO: "Thời Gian Vực",
            TaoSoulType.DESTRUCTION_TAO: "Hủy Diệt Vực",
            TaoSoulType.CREATION_TAO: "Sáng Tạo Vực",
        }
        return abilities.get(soul_type, "Unknown Domain")
    
    def _get_tao_soul_lore(self, soul_type: TaoSoulType) -> str:
        """Get lore for soul type"""
        lore_map = {
            TaoSoulType.FIRE_TAO: "Đạo Hồn Hỏa, chứa sức mạnh thiêu đốt vạn vật.",
            TaoSoulType.WATER_TAO: "Đạo Hồn Thủy, nguồn gốc của sự sống và sự chết.",
            TaoSoulType.EARTH_TAO: "Đạo Hồn Thổ, nền tảng vững chắc của vạn vật.",
            TaoSoulType.METAL_TAO: "Đạo Hồn Kim, sắc bén và cứng rắn.",
            TaoSoulType.WOOD_TAO: "Đạo Hồn Mộc, sinh trưởng và phát triển.",
            TaoSoulType.SPACE_TAO: "Đạo Hồn Không Gian, vượt qua mọi khoảng cách.",
            TaoSoulType.TIME_TAO: "Đạo Hồn Thời Gian, điều khiển dòng chảy thời gian.",
            TaoSoulType.DESTRUCTION_TAO: "Đạo Hồn Hủy Diệt, sức mạnh phá hủy tất cả.",
            TaoSoulType.CREATION_TAO: "Đạo Hồn Sáng Tạo, nguồn gốc của vạn vật.",
        }
        return lore_map.get(soul_type, "Đạo Hồn bí ẩn.")
    
    def fuse_tao_souls(
        self,
        soul_ids: List[str]
    ) -> Optional[TaoSoul]:
        """
        Fuse multiple Tao Souls into one
        
        Returns:
            Fused Tao Soul hoặc None
        """
        if len(soul_ids) < 2:
            return None
        
        souls = [self.tao_souls.get(sid) for sid in soul_ids if sid in self.tao_souls]
        if len(souls) < 2:
            return None
        
        # Calculate fused properties
        total_purity = sum(s.purity for s in souls) / len(souls)
        total_power = sum(s.power for s in souls)
        all_elements = []
        for s in souls:
            all_elements.extend(s.element_affinity)
        
        # Determine fused type (simplified: use first soul type)
        fused_type = souls[0].soul_type
        
        # Create fused soul
        fused_soul = self.collect_tao_soul(
            soul_type=fused_type,
            purity=min(1.0, total_purity * 1.1),  # 10% purity bonus
            power=total_power
        )
        
        fused_soul.element_affinity = list(set(all_elements))  # Unique elements
        
        # Remove original souls
        for sid in soul_ids:
            if sid in self.tao_souls:
                del self.tao_souls[sid]
        
        return fused_soul

