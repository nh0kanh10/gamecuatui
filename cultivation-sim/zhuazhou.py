"""
Zhuazhou (Lễ Chọn Đồ) - Character Creation System (Improved)
Dựa trên đánh giá: Diversity, synergy bonuses, rare items, stat mapping thống nhất
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Set
from enum import Enum
import random


class ZhuazhouItem(str, Enum):
    """Vật phẩm trong Lễ Thôi Nôi - mở rộng pool"""
    # Common items
    ANCIENT_BOOK = "Sách Cổ / Bút Lông"
    WOODEN_SWORD = "Kiếm Gỗ"
    GARLIC = "Củ Tỏi / Hành"
    HANDLE_EARTH = "Nắm Đất"
    GOLD_COIN = "Đồng Xu / Thỏi Vàng"
    RULER = "Thước Đo"
    STEAMED_BUN = "Bánh Bao / Đùi Gà"
    JADE_PENDANT = "Ngọc Bội"
    SPIRIT_HERB = "Linh Dược"
    MYSTIC_TOME = "Kinh Sách Thần Bí"
    # Rare items (tỉ lệ thấp)
    DRAGON_SCALE = "Vảy Rồng"  # Rare
    PHOENIX_FEATHER = "Lông Phượng"  # Rare
    IMMORTAL_PEACH = "Đào Tiên"  # Rare


class Trait(str, Enum):
    """Thiên phú (Traits) nhận được từ vật phẩm"""
    BOOKWORM = "Mọt Sách"
    SWORD_FANATIC = "Kiếm Si"
    CLEVER = "Khéo Léo"
    EARTH_SPIRIT = "Thổ Linh Căn"
    MERCHANT = "Thương Nhân"
    JUST = "Công Chính"
    GLUTTON = "Phàm Ăn"
    JADE_BLESSED = "Ngọc Phúc"
    HERB_MASTER = "Dược Sư"
    MYSTIC_SCHOLAR = "Học Giả Thần Bí"
    DRAGON_BLOOD = "Long Huyết"  # Rare
    PHOENIX_BLESSING = "Phượng Hoàng Chúc Phúc"  # Rare
    IMMORTAL_SEED = "Tiên Căn"  # Rare


class ItemCategory(str, Enum):
    """Phân loại vật phẩm để tính synergy"""
    SCHOLAR = "scholar"  # Sách, Kinh, Bút
    WARRIOR = "warrior"  # Kiếm, Vũ khí
    MERCHANT = "merchant"  # Vàng, Bàn tính
    NATURE = "nature"  # Đất, Linh dược
    MYSTIC = "mystic"  # Ngọc, Kinh sách thần bí
    RARE = "rare"  # Vảy Rồng, Lông Phượng, Đào Tiên


class ZhuazhouSystem(BaseModel):
    """
    Hệ thống Zhuazhou (Lễ Chọn Đồ) - Improved
    
    Cải tiến:
    - Stat mapping thống nhất với AttributesComponent (CON, INT, PER, LUK, CHA, KAR)
    - Synergy bonuses khi chọn vật phẩm cùng hệ
    - Rare items với tỉ lệ thấp
    - Max cap cho stat bonuses để tránh overpower
    """
    
    # Mapping vật phẩm -> Stats & Traits (thống nhất format)
    ITEM_MAPPING: Dict[str, Dict] = {
        # Common items
        ZhuazhouItem.ANCIENT_BOOK: {
            "stats": {"INT": 5, "CHA": 2},
            "trait": Trait.BOOKWORM,
            "category": ItemCategory.SCHOLAR,
            "trait_effect": {"learning_speed": 1.2, "description": "Tốc độ học kỹ năng +20%"}
        },
        ZhuazhouItem.WOODEN_SWORD: {
            "stats": {"CON": 3, "PER": 4},  # Thống nhất: CON thay STR, PER thay AGI
            "trait": Trait.SWORD_FANATIC,
            "category": ItemCategory.WARRIOR,
            "trait_effect": {"sword_damage": 1.15, "description": "Sát thương Kiếm đạo +15%"}
        },
        ZhuazhouItem.GARLIC: {
            "stats": {"INT": 3, "LUK": 3},
            "trait": Trait.CLEVER,
            "category": ItemCategory.NATURE,
            "trait_effect": {"crafting_success": 1.15, "description": "Tỉ lệ Luyện đan/Chế đồ +15%"}
        },
        ZhuazhouItem.HANDLE_EARTH: {
            "stats": {"CON": 5, "KAR": 2},  # Thêm KAR
            "trait": Trait.EARTH_SPIRIT,
            "category": ItemCategory.NATURE,
            "trait_effect": {"earth_cultivation": 1.3, "description": "Tốc độ tu luyện hệ Thổ +30%"}
        },
        ZhuazhouItem.GOLD_COIN: {
            "stats": {"CHA": 5, "LUK": 5},
            "trait": Trait.MERCHANT,
            "category": ItemCategory.MERCHANT,
            "trait_effect": {"trade_price": 0.9, "description": "Giá mua vật phẩm giảm 10%"}
        },
        ZhuazhouItem.RULER: {
            "stats": {"PER": 3, "KAR": 3},  # Thống nhất: KAR thay WILL
            "trait": Trait.JUST,
            "category": ItemCategory.SCHOLAR,
            "trait_effect": {"heart_demon_resistance": 1.2, "description": "Kháng Tâm ma +20%"}
        },
        ZhuazhouItem.STEAMED_BUN: {
            "stats": {"CON": 5, "PER": -2},  # Thống nhất: PER thay AGI
            "trait": Trait.GLUTTON,
            "category": ItemCategory.NATURE,
            "trait_effect": {"hp_regen": 1.1, "food_consumption": 1.5, "description": "Tốc độ hồi máu +10%, tiêu hao lương thực +50%"}
        },
        ZhuazhouItem.JADE_PENDANT: {
            "stats": {"LUK": 5, "KAR": 3},
            "trait": Trait.JADE_BLESSED,
            "category": ItemCategory.MYSTIC,
            "trait_effect": {"event_chance": 1.2, "description": "Tỉ lệ gặp sự kiện tốt +20%"}
        },
        ZhuazhouItem.SPIRIT_HERB: {
            "stats": {"INT": 3, "CON": 2},
            "trait": Trait.HERB_MASTER,
            "category": ItemCategory.NATURE,
            "trait_effect": {"alchemy_success": 1.25, "description": "Tỉ lệ Luyện đan thành công +25%"}
        },
        ZhuazhouItem.MYSTIC_TOME: {
            "stats": {"INT": 4, "KAR": 4},
            "trait": Trait.MYSTIC_SCHOLAR,
            "category": ItemCategory.MYSTIC,
            "trait_effect": {"comprehension": 1.3, "description": "Tốc độ hiểu kỹ thuật +30%"}
        },
        # Rare items (bonus lớn hơn)
        ZhuazhouItem.DRAGON_SCALE: {
            "stats": {"CON": 10, "KAR": 8},  # Bonus lớn
            "trait": Trait.DRAGON_BLOOD,
            "category": ItemCategory.RARE,
            "trait_effect": {"dragon_blood": 1.5, "description": "Long Huyết: Sức mạnh thể chất +50%, kháng lửa +30%"},
            "rarity": 0.05  # 5% chance
        },
        ZhuazhouItem.PHOENIX_FEATHER: {
            "stats": {"LUK": 10, "KAR": 10},  # Bonus lớn
            "trait": Trait.PHOENIX_BLESSING,
            "category": ItemCategory.RARE,
            "trait_effect": {"phoenix_blessing": 1.4, "description": "Phượng Hoàng Chúc Phúc: Khí vận +40%, tái sinh 1 lần"},
            "rarity": 0.05  # 5% chance
        },
        ZhuazhouItem.IMMORTAL_PEACH: {
            "stats": {"INT": 8, "KAR": 12},  # Bonus lớn
            "trait": Trait.IMMORTAL_SEED,
            "category": ItemCategory.RARE,
            "trait_effect": {"immortal_seed": 1.6, "description": "Tiên Căn: Tốc độ tu luyện +60%, tiềm năng vô hạn"},
            "rarity": 0.03  # 3% chance
        }
    }
    
    # Synergy bonuses (khi chọn 2+ items cùng category)
    SYNERGY_BONUSES: Dict[ItemCategory, Dict[str, float]] = {
        ItemCategory.SCHOLAR: {
            "INT": 3,  # +3 INT bonus
            "description": "Học giả: Ngộ tính +3"
        },
        ItemCategory.WARRIOR: {
            "CON": 3,  # +3 CON bonus
            "description": "Võ sĩ: Căn cốt +3"
        },
        ItemCategory.MERCHANT: {
            "CHA": 3,  # +3 CHA bonus
            "description": "Thương nhân: Mị lực +3"
        },
        ItemCategory.NATURE: {
            "KAR": 2,  # +2 KAR bonus
            "description": "Thiên nhiên: Cơ duyên +2"
        },
        ItemCategory.MYSTIC: {
            "LUK": 3,  # +3 LUK bonus
            "description": "Thần bí: Phúc duyên +3"
        },
        ItemCategory.RARE: {
            "KAR": 5,  # +5 KAR bonus (rare synergy)
            "description": "Thần vật: Cơ duyên +5"
        }
    }
    
    def generate_items(self, pool_size: int = 15) -> List[str]:
        """
        Sinh ngẫu nhiên items từ pool
        
        Cải tiến:
        - Có thể chọn từ pool lớn hơn (15+ items)
        - Rare items có tỉ lệ xuất hiện thấp
        """
        all_items = list(ZhuazhouItem)
        
        # Tách common và rare
        common_items = [item for item in all_items if item not in [
            ZhuazhouItem.DRAGON_SCALE,
            ZhuazhouItem.PHOENIX_FEATHER,
            ZhuazhouItem.IMMORTAL_PEACH
        ]]
        rare_items = [
            ZhuazhouItem.DRAGON_SCALE,
            ZhuazhouItem.PHOENIX_FEATHER,
            ZhuazhouItem.IMMORTAL_PEACH
        ]
        
        # Chọn items
        selected = []
        
        # 1-2 rare items (nếu may mắn)
        for rare_item in rare_items:
            if random.random() < self.ITEM_MAPPING[rare_item.value].get("rarity", 0.05):
                selected.append(rare_item.value)
        
        # Fill với common items
        random.shuffle(common_items)
        while len(selected) < pool_size:
            item = random.choice(common_items)
            if item not in selected:
                selected.append(item.value)
        
        random.shuffle(selected)
        return selected[:pool_size]
    
    def process_selection(
        self,
        selected_items: List[str],
        base_attributes: Dict[str, float]  # Thống nhất: float
    ) -> Dict[str, any]:
        """
        Xử lý lựa chọn 3 vật phẩm và tính toán stats + traits
        
        Cải tiến:
        - Synergy bonuses
        - Max cap cho stats
        - Scale phi tuyến cho late-game
        """
        
        if len(selected_items) != 3:
            raise ValueError("Phải chọn đúng 3 vật phẩm")
        
        # Start with base attributes
        final_attributes = base_attributes.copy()
        traits = []
        categories = []
        
        # Process each selected item
        for item_name in selected_items:
            if item_name not in self.ITEM_MAPPING:
                continue
            
            item_data = self.ITEM_MAPPING[item_name]
            
            # Add stats (thống nhất format: CON, INT, PER, LUK, CHA, KAR)
            for stat_name, stat_value in item_data["stats"].items():
                if stat_name in final_attributes:
                    final_attributes[stat_name] += stat_value
                else:
                    final_attributes[stat_name] = stat_value
            
            # Add trait
            trait = item_data["trait"]
            trait_effect = item_data["trait_effect"]
            traits.append({
                "name": trait.value,
                "effect": trait_effect,
                "item": item_name
            })
            
            # Track category
            categories.append(item_data.get("category"))
        
        # Calculate synergy bonuses
        synergy_bonuses = self._calculate_synergy(categories)
        for stat_name, bonus_value in synergy_bonuses.items():
            if stat_name in final_attributes:
                final_attributes[stat_name] += bonus_value
        
        # Clamp attributes to valid range (1-100) với max cap
        for key in final_attributes:
            final_attributes[key] = max(1.0, min(100.0, final_attributes[key]))
        
        # Generate narrative
        narrative = self._generate_narrative(selected_items, traits, synergy_bonuses)
        
        return {
            "final_attributes": final_attributes,
            "traits": traits,
            "synergy_bonuses": synergy_bonuses,
            "narrative": narrative
        }
    
    def _calculate_synergy(self, categories: List[Optional[ItemCategory]]) -> Dict[str, float]:
        """
        Tính synergy bonuses khi chọn 2+ items cùng category
        """
        bonuses = {}
        
        # Đếm số lượng mỗi category
        category_count = {}
        for cat in categories:
            if cat:
                category_count[cat] = category_count.get(cat, 0) + 1
        
        # Apply synergy nếu có 2+ items cùng category
        for cat, count in category_count.items():
            if count >= 2 and cat in self.SYNERGY_BONUSES:
                synergy_data = self.SYNERGY_BONUSES[cat]
                for stat_name, bonus_value in synergy_data.items():
                    if stat_name != "description":
                        bonuses[stat_name] = bonuses.get(stat_name, 0.0) + bonus_value
        
        return bonuses
    
    def _generate_narrative(
        self,
        selected_items: List[str],
        traits: List[Dict],
        synergy_bonuses: Dict[str, float]
    ) -> str:
        """
        Tạo narrative mô tả lễ thôi nôi (có variation)
        """
        
        item_descriptions = {
            ZhuazhouItem.ANCIENT_BOOK: "một cuốn sách cổ vàng úa",
            ZhuazhouItem.WOODEN_SWORD: "một thanh kiếm gỗ nhỏ xinh",
            ZhuazhouItem.GARLIC: "củ tỏi và hành tây",
            ZhuazhouItem.HANDLE_EARTH: "một nắm đất màu mỡ",
            ZhuazhouItem.GOLD_COIN: "đồng xu vàng sáng lấp lánh",
            ZhuazhouItem.RULER: "một cây thước đo gỗ",
            ZhuazhouItem.STEAMED_BUN: "bánh bao thơm phức",
            ZhuazhouItem.JADE_PENDANT: "một ngọc bội xanh biếc",
            ZhuazhouItem.SPIRIT_HERB: "cây linh dược tỏa hương",
            ZhuazhouItem.MYSTIC_TOME: "một cuốn kinh sách thần bí",
            ZhuazhouItem.DRAGON_SCALE: "một vảy rồng lấp lánh ánh vàng",  # Rare
            ZhuazhouItem.PHOENIX_FEATHER: "một lông phượng rực rỡ",  # Rare
            ZhuazhouItem.IMMORTAL_PEACH: "một quả đào tiên tỏa hương thần bí",  # Rare
        }
        
        descriptions = [item_descriptions.get(item, item) for item in selected_items]
        
        narrative = f"""
Gia đình bày mâm đồ vật trước mặt ngươi. Mười vật phẩm được sắp xếp cẩn thận.

Ngươi bò đến và chọn ba vật phẩm:
1. {descriptions[0]}
2. {descriptions[1]}
3. {descriptions[2]}

Gia đình vui mừng và giải thích ý nghĩa của từng vật phẩm. Ngươi nhận được:
"""
        
        for trait in traits:
            narrative += f"- {trait['name']}: {trait['effect']['description']}\n"
        
        # Synergy bonus narrative
        if synergy_bonuses:
            narrative += "\nĐặc biệt, các vật phẩm ngươi chọn có sự tương hợp:\n"
            for stat_name, bonus_value in synergy_bonuses.items():
                if stat_name != "description":
                    stat_display = {
                        "CON": "Căn Cốt",
                        "INT": "Ngộ Tính",
                        "PER": "Thần Thức",
                        "LUK": "Phúc Duyên",
                        "CHA": "Mị Lực",
                        "KAR": "Cơ Duyên"
                    }.get(stat_name, stat_name)
                    narrative += f"- {stat_display} +{bonus_value:.0f}\n"
        
        narrative += "\nĐây là dấu hiệu đầu tiên về tương lai của ngươi trong thế giới tu tiên."
        
        return narrative.strip()
