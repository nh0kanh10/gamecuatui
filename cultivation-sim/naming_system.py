"""
Grammar-Based Naming System
Tạo tên theo ngữ pháp với foreshadowing
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import random
import json
from pathlib import Path


class NamingGrammar:
    """
    Grammar-based name generator
    Structure: [Số] + [Danh từ] + [Nguyên tố] + [Vũ khí/Loại]
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.numbers: List[str] = []
        self.nouns: List[str] = []
        self.elements: List[str] = []
        self.weapons: List[str] = []
        self.suffixes: List[str] = []
        self.traits: Dict[str, List[str]] = {}
        self.load_grammar()
    
    def load_grammar(self):
        """Load grammar rules from JSON"""
        grammar_file = self.data_dir / "naming_grammar.json"
        
        if grammar_file.exists():
            try:
                with open(grammar_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.numbers = data.get("numbers", [])
                    self.nouns = data.get("nouns", [])
                    self.elements = data.get("elements", [])
                    self.weapons = data.get("weapons", [])
                    self.suffixes = data.get("suffixes", [])
                    self.traits = data.get("traits", {})
            except Exception as e:
                print(f"❌ Error loading grammar: {e}")
        
        # Default values if file doesn't exist
        if not self.numbers:
            self.numbers = ["Cửu", "Vạn", "Thiên", "Vô", "Cực", "Thái", "Huyền", "Địa"]
        if not self.nouns:
            self.nouns = ["Thiên", "Địa", "Huyền", "Hoàng", "Vạn", "Cửu", "Vô", "Cực"]
        if not self.elements:
            self.elements = ["Lôi", "Hỏa", "Băng", "Phong", "Thổ", "Kim", "Mộc", "Thủy"]
        if not self.weapons:
            self.weapons = ["Kiếm", "Đao", "Thương", "Cung", "Quyền", "Chưởng", "Chỉ", "Trùy"]
        if not self.suffixes:
            self.suffixes = ["Thuật", "Quyết", "Công", "Pháp", "Kinh", "Điển"]
    
    def generate_skill_name(
        self,
        element: Optional[str] = None,
        weapon_type: Optional[str] = None,
        seed: Optional[int] = None
    ) -> str:
        """
        Generate skill name
        
        Structure: [Số] + [Danh từ] + [Nguyên tố] + [Vũ khí] + [Hậu tố]
        
        Example: "Cửu Thiên Lôi Kiếm Thuật"
        """
        rng = random.Random(seed) if seed else random
        
        number = rng.choice(self.numbers)
        noun = rng.choice(self.nouns)
        element_choice = element or rng.choice(self.elements)
        weapon_choice = weapon_type or rng.choice(self.weapons)
        suffix = rng.choice(self.suffixes)
        
        return f"{number} {noun} {element_choice} {weapon_choice} {suffix}"
    
    def generate_character_name(
        self,
        gender: str = "neutral",
        foreshadowing_trait: Optional[str] = None,
        seed: Optional[int] = None
    ) -> str:
        """
        Generate character name với foreshadowing
        
        Structure: [Họ] + [Tên]
        Foreshadowing: Tên phản ánh trait ẩn
        """
        rng = random.Random(seed) if seed else random
        
        # Surnames
        surnames = ["Lý", "Vương", "Trương", "Lưu", "Trần", "Dương", "Hoàng", "Chu"]
        
        # Given names by gender
        if gender == "male":
            given_names = ["Thiên", "Địa", "Huyền", "Vô", "Cực", "Thái", "Hạo", "Vân"]
        elif gender == "female":
            given_names = ["Linh", "Tuyết", "Vân", "Hoa", "Nguyệt", "Thủy", "Hương", "Di"]
        else:
            given_names = ["Thiên", "Địa", "Huyền", "Vô", "Cực", "Linh", "Tuyết", "Vân"]
        
        surname = rng.choice(surnames)
        given_name = rng.choice(given_names)
        
        # Apply foreshadowing
        if foreshadowing_trait and foreshadowing_trait in self.traits:
            trait_names = self.traits[foreshadowing_trait]
            if trait_names:
                given_name = rng.choice(trait_names)
        
        return f"{surname} {given_name}"
    
    def generate_sect_name(
        self,
        element: Optional[str] = None,
        seed: Optional[int] = None
    ) -> str:
        """
        Generate sect name
        
        Structure: [Tính từ] + [Danh từ] + [Hậu tố Tông/Môn]
        """
        rng = random.Random(seed) if seed else random
        
        adjectives = ["Thái", "Cực", "Vô", "Huyền", "Cửu", "Thiên", "Địa", "Vạn"]
        nouns = ["Thanh", "Huyền", "Linh", "Tiên", "Ma", "Kiếm", "Đao", "Pháp"]
        suffixes = ["Tông", "Môn", "Cung", "Phái", "Tông Môn"]
        
        adjective = rng.choice(adjectives)
        noun = rng.choice(nouns)
        suffix = rng.choice(suffixes)
        
        # Add element if specified
        if element:
            element_name = next((e for e in self.elements if element.lower() in e.lower()), None)
            if element_name:
                return f"{adjective} {element_name} {noun} {suffix}"
        
        return f"{adjective} {noun} {suffix}"
    
    def analyze_name_foreshadowing(self, name: str) -> List[str]:
        """
        Analyze name để tìm foreshadowing traits
        
        Returns:
            List of possible traits
        """
        traits = []
        name_lower = name.lower()
        
        # Check for trait keywords
        for trait, keywords in self.traits.items():
            for keyword in keywords:
                if keyword.lower() in name_lower:
                    traits.append(trait)
                    break
        
        # Check for element keywords
        for element in self.elements:
            if element.lower() in name_lower:
                traits.append(f"element_{element.lower()}")
        
        # Check for number keywords (power level)
        power_numbers = ["cửu", "vạn", "thiên", "vô", "cực"]
        for num in power_numbers:
            if num in name_lower:
                traits.append("high_power")
                break
        
        return traits


class NamingSystem:
    """
    Main Naming System
    """
    
    def __init__(self, data_dir: str = "data"):
        self.grammar = NamingGrammar(data_dir)
    
    def generate_skill_name(
        self,
        element: Optional[str] = None,
        weapon_type: Optional[str] = None,
        seed: Optional[int] = None
    ) -> str:
        """Generate skill name"""
        return self.grammar.generate_skill_name(element, weapon_type, seed)
    
    def generate_character_name(
        self,
        gender: str = "neutral",
        foreshadowing_trait: Optional[str] = None,
        seed: Optional[int] = None
    ) -> str:
        """Generate character name với foreshadowing"""
        return self.grammar.generate_character_name(gender, foreshadowing_trait, seed)
    
    def generate_sect_name(
        self,
        element: Optional[str] = None,
        seed: Optional[int] = None
    ) -> str:
        """Generate sect name"""
        return self.grammar.generate_sect_name(element, seed)
    
    def analyze_foreshadowing(self, name: str) -> List[str]:
        """Analyze name for foreshadowing"""
        return self.grammar.analyze_name_foreshadowing(name)

