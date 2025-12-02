"""
Breakthrough Mechanics - Công thức đột phá cảnh giới (Refactored)
Dựa trên đánh giá: Tuple keys, Tribulation shield/artifact, Golden Core grade
"""

from pydantic import BaseModel, Field
from typing import Dict, Tuple, Optional, List
from enum import Enum
import random
import math


class RealmTier(str, Enum):
    """Cảnh giới lớn - dùng string để match với World Bible"""
    QI_REFINING = "Qi_Refining"
    FOUNDATION = "Foundation"
    GOLDEN_CORE = "Golden_Core"
    NASCENT_SOUL = "Nascent_Soul"
    SPIRIT_TRANSFORMATION = "Spirit_Transformation"
    BODY_FUSION = "Body_Fusion"
    GREAT_MULTIPLICATION = "Great_Multiplication"
    IMMORTAL = "Immortal"
    MAHAYANA = "Mahayana"


class BreakthroughResult(str, Enum):
    """Kết quả đột phá"""
    SUCCESS = "success"  # Thành công mỹ mãn
    PARTIAL_SUCCESS = "partial_success"  # Thành công nhưng phẩm chất thấp (Cho Kim Đan)
    FORCED_SUCCESS = "forced_success"  # Độ kiếp thành công (bị thương)
    FAILURE_SURVIVED = "failure_survived"  # Độ kiếp thất bại, nhưng sống (Phế tu vi)
    FAILURE_DEATH = "failure_death"  # Thân tử đạo tiêu


class GoldenCoreGrade(int, Enum):
    """Phẩm chất Kim Đan (1-9)"""
    GRADE_1 = 1  # Nhất Phẩm (Hoàn hảo)
    GRADE_2 = 2
    GRADE_3 = 3
    GRADE_4 = 4
    GRADE_5 = 5  # Trung bình
    GRADE_6 = 6
    GRADE_7 = 7
    GRADE_8 = 8
    GRADE_9 = 9  # Cửu Phẩm (Phế)


class BreakthroughMechanics(BaseModel):
    """
    Cơ chế đột phá cảnh giới với công thức toán học
    
    Cải tiến:
    - Dùng Tuple (RealmTier, RealmTier) làm key thay vì string
    - Tribulation với shield/artifact system
    - Golden Core grade system (1-9 phẩm)
    - Exponential damage scaling
    """
    
    # Base success rates - dùng Tuple làm key để an toàn
    BASE_RATES: Dict[Tuple[RealmTier, RealmTier], float] = {
        (RealmTier.QI_REFINING, RealmTier.FOUNDATION): 0.50,
        (RealmTier.FOUNDATION, RealmTier.GOLDEN_CORE): 0.30,
        (RealmTier.GOLDEN_CORE, RealmTier.NASCENT_SOUL): 0.10,
        (RealmTier.NASCENT_SOUL, RealmTier.SPIRIT_TRANSFORMATION): 0.05,
        (RealmTier.SPIRIT_TRANSFORMATION, RealmTier.BODY_FUSION): 0.02,
        (RealmTier.BODY_FUSION, RealmTier.GREAT_MULTIPLICATION): 0.01,
        (RealmTier.GREAT_MULTIPLICATION, RealmTier.IMMORTAL): 0.005,
        (RealmTier.IMMORTAL, RealmTier.MAHAYANA): 0.001,
    }
    
    def calculate_success_rate(
        self,
        current_tier: RealmTier,
        target_tier: RealmTier,
        mental_state: float,  # 0-100
        modifiers: Dict[str, float],  # {'pills': 0.1, 'feng_shui': 0.05, 'heart_demon': -0.2, 'karma': -0.1}
    ) -> float:
        """
        Tính toán tỉ lệ đột phá thành công
        
        Args:
            current_tier: Cảnh giới hiện tại
            target_tier: Cảnh giới mục tiêu
            mental_state: Tâm cảnh (0-100)
            modifiers: Dict các modifier (bonus/penalty)
        
        Returns:
            Success rate (0.01 - 0.95)
        """
        # Get base rate
        key = (current_tier, target_tier)
        base = self.BASE_RATES.get(key, 0.01)
        
        # Tính tổng bonus
        bonus = (mental_state / 100) * 0.2  # Max 20% từ tâm cảnh
        bonus += modifiers.get('pills', 0.0)
        bonus += modifiers.get('feng_shui', 0.0)
        bonus += modifiers.get('element_synergy', 0.0)
        
        # Tính penalty (Tâm ma + Nghiệp chướng)
        penalty = modifiers.get('heart_demon', 0.0)
        penalty += modifiers.get('karma', 0.0)
        penalty += modifiers.get('killing_innocents', 0.0)
        
        # Willpower resistance (giảm penalty)
        willpower_resistance = modifiers.get('willpower_resistance', 0.0)
        penalty = max(0.0, penalty - willpower_resistance)
        
        # Final calculation với logistic curve để tránh quá predictable
        linear_rate = base * (1 + bonus) - penalty
        # Logistic curve: smoother transition
        final_rate = 1 / (1 + math.exp(-10 * (linear_rate - 0.5)))
        
        return max(0.01, min(0.95, final_rate))
    
    def trigger_tribulation(
        self,
        player_hp: int,
        max_hp: int,
        realm_tier: RealmTier,
        artifacts_defense: int = 0,  # Chỉ số phòng thủ của pháp bảo/trận pháp
        consumables_shield: int = 0,  # Các loại bùa hộ mệnh dùng 1 lần
        willpower: float = 50.0,  # Ý chí (giảm chance tử vong)
    ) -> Dict[str, any]:
        """
        Mô phỏng Lôi Kiếp: Damage phải trừ vào Shield/Artifact trước khi vào HP thịt
        
        Cải tiến:
        - Shield system (artifact + consumable)
        - Shield bị hao mòn sau mỗi đợt
        - Damage tăng dần theo đợt
        - Exponential damage scaling theo realm
        """
        
        # Tính realm base damage (exponential scaling)
        realm_damage_base = {
            RealmTier.QI_REFINING: 100,
            RealmTier.FOUNDATION: 500,
            RealmTier.GOLDEN_CORE: 2500,
            RealmTier.NASCENT_SOUL: 12500,
            RealmTier.SPIRIT_TRANSFORMATION: 62500,
            RealmTier.BODY_FUSION: 312500,
            RealmTier.GREAT_MULTIPLICATION: 1562500,
            RealmTier.IMMORTAL: 7812500,
            RealmTier.MAHAYANA: 39062500,
        }
        
        base_damage = realm_damage_base.get(realm_tier, 100)
        
        # Số đợt sấm sét (3-9 đợt, tăng theo realm)
        realm_strikes = {
            RealmTier.QI_REFINING: (3, 5),
            RealmTier.FOUNDATION: (4, 6),
            RealmTier.GOLDEN_CORE: (5, 7),
            RealmTier.NASCENT_SOUL: (6, 8),
            RealmTier.SPIRIT_TRANSFORMATION: (7, 9),
            RealmTier.BODY_FUSION: (8, 10),
            RealmTier.GREAT_MULTIPLICATION: (9, 11),
            RealmTier.IMMORTAL: (10, 12),
            RealmTier.MAHAYANA: (12, 15),
        }
        
        min_strikes, max_strikes = realm_strikes.get(realm_tier, (3, 5))
        num_strikes = random.randint(min_strikes, max_strikes)
        
        log = []
        total_dmg_taken = 0
        current_hp = player_hp
        current_shield = artifacts_defense + consumables_shield
        
        for i in range(num_strikes):
            # Damage dao động +- 20% và tăng dần theo từng đợt
            # Đợt sau mạnh hơn đợt trước (1 + i * 0.1)
            strike_power = int(base_damage * random.uniform(0.9, 1.3) * (1 + i * 0.1))
            
            # Shield gánh damage trước
            damage_to_shield = min(strike_power, current_shield)
            damage_to_flesh = max(0, strike_power - current_shield)
            
            # Shield bị hao mòn sau mỗi đợt (Artifact bị nứt)
            current_shield = max(0, int(current_shield * 0.8))
            current_shield -= damage_to_shield
            current_shield = max(0, current_shield)
            
            current_hp -= damage_to_flesh
            total_dmg_taken += damage_to_flesh
            
            log.append({
                "strike": i + 1,
                "strike_power": strike_power,
                "shield_absorbed": damage_to_shield,
                "damage_taken": damage_to_flesh,
                "remaining_shield": current_shield,
                "remaining_hp": current_hp
            })
            
            if current_hp <= 0:
                return {
                    "result": BreakthroughResult.FAILURE_DEATH,
                    "log": log,
                    "total_damage": total_dmg_taken,
                    "narrative": "Không chịu nổi lôi kiếp, hồn phi phách tán. Đạo đồ dừng lại ở đây."
                }
        
        # Nếu sống sót qua hết các đợt
        # Tính chance tử vong dựa trên willpower
        survival_chance = 0.5 + (willpower / 100) * 0.3  # 50-80%
        
        if random.random() < survival_chance:
            # Forced Success
            return {
                "result": BreakthroughResult.FORCED_SUCCESS,
                "final_hp": max(1, int(current_hp * 0.1)),  # 10% HP
                "total_damage": total_dmg_taken,
                "log": log,
                "debuff": "Trọng thương",  # -50% cultivation speed
                "narrative": f"Thân thể cháy đen nhưng đạo cơ vẫn còn. Chúc mừng đạo hữu độ kiếp thành công! Nhận {total_dmg_taken} sát thương, còn {current_hp} HP."
            }
        else:
            # Failure but survived (Phế tu vi)
            return {
                "result": BreakthroughResult.FAILURE_SURVIVED,
                "final_hp": max(1, int(max_hp * 0.1)),  # 10% HP
                "total_damage": total_dmg_taken,
                "log": log,
                "debuff": "Phế tu vi",  # Giảm cảnh giới xuống 1 bậc
                "narrative": f"May mắn sống sót nhưng tu vi bị phế, giảm xuống cảnh giới thấp hơn. Nhận {total_dmg_taken} sát thương."
            }
    
    def attempt_breakthrough(
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
    ) -> Dict[str, any]:
        """
        Hàm Facade kết nối logic - Thực hiện đột phá
        
        Returns:
            {
                "result": BreakthroughResult,
                "success": bool,
                "golden_core_grade": Optional[GoldenCoreGrade],  # Chỉ cho Golden Core
                "tribulation": Optional[Dict],  # Nếu có Lôi Kiếp
                "narrative": str
            }
        """
        
        # 1. Tính tỷ lệ
        success_rate = self.calculate_success_rate(
            current_tier=current_tier,
            target_tier=target_tier,
            mental_state=mental_state,
            modifiers=modifiers
        )
        
        # 2. Roll RNG
        roll = random.random()
        
        if roll <= success_rate:
            # Success
            # Xử lý đặc biệt cho Kim Đan (Golden Core)
            if target_tier == RealmTier.GOLDEN_CORE:
                # Grade dựa trên việc roll dư bao nhiêu
                # Ví dụ: Rate 80%, Roll ra 10% -> Dư 70% -> Kim Đan Nhất Phẩm
                excess = success_rate - roll
                grade_value = int(excess * 9) + 1  # 1-9
                grade_value = max(1, min(9, grade_value))
                grade = GoldenCoreGrade(grade_value)
                
                if grade_value <= 3:
                    narrative = f"Đột phá thành công! Kim Đan {grade_value} Phẩm - Phẩm chất hoàn hảo!"
                elif grade_value <= 6:
                    narrative = f"Đột phá thành công! Kim Đan {grade_value} Phẩm - Phẩm chất tốt."
                else:
                    narrative = f"Đột phá thành công! Kim Đan {grade_value} Phẩm - Phẩm chất thấp, cần tu luyện thêm."
                
                return {
                    "result": BreakthroughResult.PARTIAL_SUCCESS if grade_value > 6 else BreakthroughResult.SUCCESS,
                    "success": True,
                    "golden_core_grade": grade,
                    "tribulation": None,
                    "narrative": narrative
                }
            
            return {
                "result": BreakthroughResult.SUCCESS,
                "success": True,
                "golden_core_grade": None,
                "tribulation": None,
                "narrative": f"Đột phá thành công! Tu vi tăng lên cảnh giới {target_tier.value}."
            }
        
        # 3. Nếu Fail -> Gọi Lôi Kiếp
        tribulation_result = self.trigger_tribulation(
            player_hp=player_hp,
            max_hp=max_hp,
            realm_tier=target_tier,
            artifacts_defense=artifacts_defense,
            consumables_shield=consumables_shield,
            willpower=willpower
        )
        
        return {
            "result": tribulation_result["result"],
            "success": tribulation_result["result"] in [BreakthroughResult.FORCED_SUCCESS, BreakthroughResult.SUCCESS],
            "golden_core_grade": None,
            "tribulation": tribulation_result,
            "narrative": tribulation_result["narrative"]
        }
