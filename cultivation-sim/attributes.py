"""
Attributes System - S.P.E.C.I.A.L phiên bản Tiên hiệp (Refactored)
Dựa trên đánh giá: Exponential scaling, Realm tier multipliers, AI tags
"""

import math
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class AttributeType(str, Enum):
    """Loại chỉ số"""
    CON = "CON"  # Căn cốt (Constitution)
    INT = "INT"  # Ngộ tính (Intelligence)
    PER = "PER"  # Thần thức (Perception)
    LUK = "LUK"  # Phúc duyên (Luck)
    CHA = "CHA"  # Mị lực (Charisma)
    KAR = "KAR"  # Cơ duyên (Karma)


class RealmTier(int, Enum):
    """Cảnh giới - dùng int để so sánh dễ dàng"""
    MORTAL = 0
    QI_REFINING = 1      # Luyện Khí (Base x10)
    FOUNDATION = 2       # Trúc Cơ (Base x50)
    GOLDEN_CORE = 3      # Kim Đan (Base x200)
    NASCENT_SOUL = 4     # Nguyên Anh (Base x1000)
    SPIRIT_TRANSFORMATION = 5  # Hóa Thần (Base x5000)
    BODY_FUSION = 6      # Hợp Thể (Base x25000)
    GREAT_MULTIPLICATION = 7  # Đại Thừa (Base x100000)
    IMMORTAL = 8         # Tiên (Base x500000)
    MAHAYANA = 9         # Đại Thừa (Base x1000000)


class AttributesComponent(BaseModel):
    """
    Hệ thống chỉ số cốt lõi (S.P.E.C.I.A.L phiên bản Tiên hiệp)
    
    Cải tiến:
    - Sử dụng float cho tăng trưởng nhỏ giọt (0.1 điểm từ thuốc)
    - Exponential scaling cho INT (thiên tài gấp 20x người thường)
    - Realm tier multipliers cho HP (Nguyên Anh gấp 1000x Luyện Khí)
    - AI personality tags thay vì interpretation dài
    """
    
    # Core Attributes - dùng float để hỗ trợ tăng trưởng nhỏ giọt
    con: float = Field(default=10.0, ge=1.0, le=100.0, description="Căn cốt - HP, Tốc độ hồi phục")
    int: float = Field(default=10.0, ge=1.0, le=100.0, description="Ngộ tính - Tốc độ tu luyện, Chế tạo")
    per: float = Field(default=10.0, ge=1.0, le=100.0, description="Thần thức - Tầm nhìn, Phát hiện")
    luk: float = Field(default=10.0, ge=1.0, le=100.0, description="Phúc duyên - Drop rate, Crit, Sự kiện")
    cha: float = Field(default=10.0, ge=1.0, le=100.0, description="Mị lực - Giá mua bán, Thiện cảm")
    kar: float = Field(default=10.0, ge=1.0, le=100.0, description="Cơ duyên - Giới hạn cảnh giới (Hidden)")
    
    def get_all_attributes(self) -> Dict[str, float]:
        """Get tất cả attributes dưới dạng dict"""
        return {
            "CON": self.con,
            "INT": self.int,
            "PER": self.per,
            "LUK": self.luk,
            "CHA": self.cha,
            "KAR": self.kar
        }
    
    def get_attribute(self, attr_type: AttributeType) -> float:
        """Get giá trị của một attribute"""
        mapping = {
            AttributeType.CON: self.con,
            AttributeType.INT: self.int,
            AttributeType.PER: self.per,
            AttributeType.LUK: self.luk,
            AttributeType.CHA: self.cha,
            AttributeType.KAR: self.kar
        }
        return mapping.get(attr_type, 10.0)
    
    def set_attribute(self, attr_type: AttributeType, value: float):
        """Set giá trị của một attribute (với validation)"""
        value = max(1.0, min(100.0, value))
        if attr_type == AttributeType.CON:
            self.con = value
        elif attr_type == AttributeType.INT:
            self.int = value
        elif attr_type == AttributeType.PER:
            self.per = value
        elif attr_type == AttributeType.LUK:
            self.luk = value
        elif attr_type == AttributeType.CHA:
            self.cha = value
        elif attr_type == AttributeType.KAR:
            self.kar = value
    
    # --- DETERMINISTIC MATH (XIANXIA SCALING) ---
    
    def calculate_max_hp(self, realm: RealmTier = RealmTier.MORTAL) -> int:
        """
        HP = Base_Realm * (CON^1.5)
        
        CON đóng vai trò cấp số nhân, tạo sự chênh lệch lớn giữa 10 và 100.
        CON 10 = 31x modifier, CON 100 = 1000x modifier
        
        Realm multipliers:
        - MORTAL: 100
        - QI_REFINING: 1000 (x10)
        - FOUNDATION: 5000 (x50)
        - GOLDEN_CORE: 25000 (x200)
        - NASCENT_SOUL: 150000 (x1000)
        """
        realm_base_hp = {
            RealmTier.MORTAL: 100,
            RealmTier.QI_REFINING: 1000,
            RealmTier.FOUNDATION: 5000,
            RealmTier.GOLDEN_CORE: 25000,
            RealmTier.NASCENT_SOUL: 150000,
            RealmTier.SPIRIT_TRANSFORMATION: 750000,
            RealmTier.BODY_FUSION: 3750000,
            RealmTier.GREAT_MULTIPLICATION: 15000000,
            RealmTier.IMMORTAL: 75000000,
            RealmTier.MAHAYANA: 150000000,
        }
        
        base = realm_base_hp.get(realm, 100)
        # Công thức mũ 1.5: CON 10 = 31x, CON 100 = 1000x modifier
        modifier = (self.con ** 1.5) / 30
        
        return int(base * modifier)
    
    def calculate_cultivation_speed(self) -> float:
        """
        Tốc độ tu luyện dùng hàm mũ cơ số e (Exponential).
        
        INT 10 = 1.0x (Chuẩn)
        INT 50 = ~4.5x
        INT 100 = ~20.0x (Nhanh gấp 20 lần) -> Sự khác biệt thiên tài
        
        Thiên tài mất 1 năm Trúc Cơ, phế vật mất 100 năm.
        """
        # Base speed 1.0 at INT 10. Growth rate 0.033
        return math.exp(0.033 * (self.int - 10))
    
    def calculate_crafting_success_rate(self, base_rate: float = 0.5) -> float:
        """
        Tính tỉ lệ chế tạo thành công dựa trên INT
        Dùng logistic curve để tránh quá dễ ở late-game
        """
        # Logistic: 0.5 + sigmoid(INT - 10) * 0.4
        # Max: 0.9 (90%), Min: 0.1 (10%)
        sigmoid = 1 / (1 + math.exp(-0.1 * (self.int - 10)))
        return 0.1 + sigmoid * 0.4
    
    def calculate_detection_range(self, base_range: int = 10, realm: RealmTier = RealmTier.MORTAL) -> int:
        """
        Tính tầm nhìn (Fog of War) dựa trên PER và Realm
        """
        # Realm multiplier
        realm_multiplier = {
            RealmTier.MORTAL: 1.0,
            RealmTier.QI_REFINING: 2.0,
            RealmTier.FOUNDATION: 5.0,
            RealmTier.GOLDEN_CORE: 10.0,
            RealmTier.NASCENT_SOUL: 50.0,
        }.get(realm, 1.0)
        
        # PER modifier (logarithmic)
        per_modifier = 1.0 + math.log(self.per / 10.0 + 1) * 0.5
        
        return int(base_range * realm_multiplier * per_modifier)
    
    def calculate_crit_chance(self, base_crit: float = 0.05) -> float:
        """
        Tính tỉ lệ Crit dựa trên LUK
        Dùng square root để tránh quá mạnh
        """
        # LUK 10 = base, LUK 100 = base + 0.3 (30% crit)
        luk_bonus = math.sqrt(self.luk / 10.0 - 1.0) * 0.1
        return min(1.0, base_crit + luk_bonus)
    
    def calculate_trade_price_modifier(self) -> float:
        """
        Tính modifier giá mua bán dựa trên CHA
        CHA cao → Giá tốt hơn (giảm giá mua, tăng giá bán)
        """
        # CHA 10 = 1.0, CHA 100 = 0.1 (giảm 90% giá)
        return 1.0 - (self.cha - 10) * 0.01
    
    def calculate_initial_favorability(self) -> int:
        """
        Tính độ thiện cảm ban đầu dựa trên CHA
        """
        return int((self.cha - 10) * 2)
    
    def calculate_breakthrough_chance(self, base_chance: float) -> float:
        """
        KAR (Cơ duyên) và LUK (Phúc duyên) cứu vớt tỉ lệ đột phá.
        
        KAR 100 adds 30% chance flat. LUK 100 adds 10% chance.
        """
        bonus = (self.kar * 0.3 + self.luk * 0.1) / 100
        return min(0.95, base_chance + bonus)  # Cap at 95%
    
    def get_max_realm_limit(self) -> RealmTier:
        """
        Tính giới hạn cảnh giới tối đa dựa trên KAR (Hidden stat)
        """
        if self.kar >= 90:
            return RealmTier.MAHAYANA
        elif self.kar >= 70:
            return RealmTier.IMMORTAL
        elif self.kar >= 50:
            return RealmTier.NASCENT_SOUL
        elif self.kar >= 30:
            return RealmTier.GOLDEN_CORE
        elif self.kar >= 10:
            return RealmTier.FOUNDATION
        else:
            return RealmTier.QI_REFINING
    
    # --- GENERATIVE CONTEXT (AI PROMPT ENGINEERING) ---
    
    def get_ai_personality_tags(self) -> List[str]:
        """
        Trả về tags ngắn gọn để inject vào System Prompt của LLM
        
        Ví dụ: ['ngộ tính yêu nghiệt', 'thể chất yếu ớt', 'khí vận chi tử']
        """
        tags = []
        
        # INT Logic
        if self.int >= 90:
            tags.append("ngộ tính yêu nghiệt (học 1 hiểu 10)")
        elif self.int >= 70:
            tags.append("thông minh hơn người")
        elif self.int <= 20:
            tags.append("tư chất ngu dốt")
        
        # CON Logic
        if self.con >= 80:
            tags.append("thể chất cường tráng (khó bị đánh bại)")
        elif self.con <= 30:
            tags.append("thể chất yếu ớt (dễ bị tổn thương)")
        
        # PER Logic
        if self.per >= 80:
            tags.append("thần thức nhạy bén (khó bị bất ngờ)")
        elif self.per <= 30:
            tags.append("thần thức kém (dễ bị phục kích)")
        
        # LUK Logic
        if self.luk >= 90:
            tags.append("khí vận chi tử (đi đường nhặt bảo vật)")
        elif self.luk <= 20:
            tags.append("xui xẻo (hay gặp rủi ro)")
        
        # CHA Logic
        if self.cha >= 80:
            tags.append("dung mạo tiên nhân (ai gặp cũng thích)")
        elif self.cha <= 30:
            tags.append("dung mạo xấu xí (dễ bị ghét)")
        
        # KAR Logic
        if self.kar >= 90:
            tags.append("Con Cưng Của Trời (định mệnh)")
        elif self.kar <= 20:
            tags.append("cơ duyên kém (khó đột phá)")
        
        return tags
    
    def get_ai_context_string(self) -> str:
        """
        Tối ưu cho LLM đọc hiểu trạng thái cơ thể
        """
        tags = ", ".join(self.get_ai_personality_tags())
        cultivation_speed = self.calculate_cultivation_speed()
        
        return (
            f"Thông số cơ bản: [Căn Cốt: {self.con:.1f}][Ngộ Tính: {self.int:.1f}][Mị Lực: {self.cha:.1f}]. "
            f"Đánh giá tiềm năng: {tags}. "
            f"Tốc độ tu luyện thực tế: {cultivation_speed:.1f}x so với người thường."
        )
    
    # --- SYNERGY EFFECTS ---
    
    def calculate_hp_regen_modifier(self) -> float:
        """
        CON + INT tăng HP regen nhanh hơn
        Synergy: Thể chất + Trí tuệ = Hiểu cách hồi phục
        """
        base_regen = 1.0 + (self.con - 10) * 0.01
        synergy_bonus = (self.con * self.int) / 1000.0  # Max 10x synergy
        return base_regen + synergy_bonus
    
    def calculate_detection_crit_combo(self) -> float:
        """
        PER + LUK tăng detection crit combo
        Synergy: Nhạy bén + May mắn = Phát hiện điểm yếu
        """
        base_detection = 1.0
        synergy = (self.per * self.luk) / 500.0  # Max 20x synergy
        return base_detection + synergy
