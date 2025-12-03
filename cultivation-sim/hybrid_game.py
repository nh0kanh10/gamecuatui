"""
HYBRID CULTIVATION GAME
Kết hợp:
- Simple core từ simple_game.py (280 lines)
- World data từ complex version (GIỮ LẠI research!)
- Content templates (GIỮ LẠI design!)
- Naming system (GIỮ LẠI cool feature!)

Total: ~400 lines vs 5000+ complex
Value retained: 90%!
"""

import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class HybridCultivationGame:
    """
    Hybrid approach - best of both worlds!
    - Simple core (AI handles logic)
    - Rich world data (consistency) 
    - Content templates (quality content)
    - Naming system (cool feature)
    """
    
    def __init__(self, data_path: str = "data"):
        # Setup Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Game state (simple!)
        self.conversation_history: List[str] = []
        self.character: Dict[str, Any] = {
            "name": "",
            "age": 0,
            "gender": "",
            "talent": "",
            "race": "",
            "background": ""
        }
        
        # Load world data (REUSE complex data!)
        self.data_path = data_path
        self.world_data = self._load_world_data()
        self.content_templates = self._load_content_templates()
        
        # Optional: Naming system if available
        self.naming_system = None
        try:
            from naming_system import NamingSystem
            self.naming_system = NamingSystem(data_path)
        except:
            pass  # OK if not available
        
        # Build enhanced system prompt
        self.system_prompt = self._build_system_prompt()
    
    def _load_world_data(self) -> Dict[str, Any]:
        """Load world database (REUSE từ complex!)"""
        world = {}
        
        # Try load thử các files, OK nếu không có
        files = {
            'locations': 'world/locations.json',
            'sects': 'world/sects.json',
            'races': 'world/races.json',
            'clans': 'world/clans.json',
        }
        
        for key, path in files.items():
            full_path = os.path.join(self.data_path, path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    world[key] = json.load(f)
                print(f"✅ Loaded {key}: {len(world[key])} entries")
            except FileNotFoundError:
                world[key] = {}
                print(f"⚠️  {key} not found, using empty")
        
        return world
    
    def _load_content_templates(self) -> Dict[str, Any]:
        """Load content templates (REUSE từ complex!)"""
        templates = {}
        
        files = {
            'skills': 'skills/skills.json',
            'items': 'items/items.json',
        }
        
        for key, path in files.items():
            full_path = os.path.join(self.data_path, path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    templates[key] = json.load(f)
                print(f"✅ Loaded {key} templates: {len(templates[key])} entries")
            except FileNotFoundError:
                templates[key] = []
                print(f"⚠️  {key} templates not found")
        
        return templates
    
    def _build_system_prompt(self) -> str:
        """Build system prompt với world data"""
        
        # Try load master prompt (REUSE từ complex!)
        master_prompt_path = os.path.join(self.data_path, 'prompts/master.md')
        try:
            with open(master_prompt_path, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
                print("✅ Loaded master.md prompt")
        except FileNotFoundError:
            # Fallback basic prompt
            base_prompt = """
Bạn là AI storyteller cho game tu tiên (cultivation/xianxia).

WORLD SETTING:
- Thế giới tu tiên với các cảnh giới cultivation
- Tông môn, locations, NPCs
- Spirit stones, pills, artifacts, beasts

RULES:
1. Mỗi turn = 1 năm
2. Generate story based on player choice
3. Luôn kết thúc với 4 lựa chọn rõ ràng
4. Stay consistent với world setting
5. Progressive difficulty
"""
        
        # Inject world data
        prompt_parts = [base_prompt]
        
        # Add location references
        if self.world_data.get('locations'):
            locations_list = list(self.world_data['locations'].keys())[:15]
            prompt_parts.append(f"\nLOCATIONS (use these):\n{', '.join(locations_list)}")
        
        # Add sects
        if self.world_data.get('sects'):
            sects_list = list(self.world_data['sects'].keys())[:10]
            prompt_parts.append(f"\nSECTS (use these):\n{', '.join(sects_list)}")
        
        # Add races
        if self.world_data.get('races'):
            races_list = list(self.world_data['races'].keys())
            prompt_parts.append(f"\nRACES:\n{', '.join(races_list)}")
        
        # Add skill examples
        if self.content_templates.get('skills'):
            skills_sample = self.content_templates['skills'][:5]
            prompt_parts.append(f"\nSKILL EXAMPLES (use similar patterns):\n{json.dumps(skills_sample, ensure_ascii=False, indent=2)}")
        
        # Add item examples
        if self.content_templates.get('items'):
            items_sample = self.content_templates['items'][:5]
            prompt_parts.append(f"\nITEM EXAMPLES:\n{json.dumps(items_sample, ensure_ascii=False, indent=2)}")
        
        return "\n\n".join(prompt_parts)
    
    def create_character(
        self,
        name: Optional[str] = None,
        gender: str = "Nam",
        talent: str = "Bình thường",
        race: str = "Người",
        background: str = "Nông dân"
    ) -> Dict[str, Any]:
        """
        Create character với world data integration
        """
        # Auto-generate name nếu có naming system
        if not name and self.naming_system:
            name = self.naming_system.generate_character_name(gender)
        elif not name:
            name = "Người Chơi"
        
        # Update character
        self.character.update({
            "name": name,
            "age": 0,
            "gender": gender,
            "talent": talent,
            "race": race,
            "background": background
        })
        
        # Get race data nếu có
        race_info = ""
        if race in self.world_data.get('races', {}):
            race_data = self.world_data['races'][race]
            race_info = f"\nRace Details: {race_data.get('description', '')}"
        
        # Get clan data nếu có
        clan_info = ""
        if background in self.world_data.get('clans', {}):
            clan_data = self.world_data['clans'][background]
            clan_info = f"\nClan Details: {clan_data.get('description', '')}"
        
        # Build prompt
        prompt = f"""{self.system_prompt}

TASK: Create background for newborn character

CHARACTER:
- Name: {name}
- Gender: {gender}
- Talent: {talent}
- Race: {race}{race_info}
- Background: {background}{clan_info}

Write story about birth and early signs.
Use world data for consistency.
End with 4 CHOICES for first year (age 0→1).

FORMAT:
[Story narrative]

CHOICES:
1. [choice 1]
2. [choice 2]
3. [choice 3]
4. [choice 4]
"""
        
        # Call Gemini
        response = self.model.generate_content(prompt)
        narrative = response.text
        
        # Extract choices
        choices = self._extract_choices(narrative)
        
        # Save to history
        self.conversation_history.append(f"[CHARACTER CREATION]\n{narrative}")
        
        return {
            "narrative": narrative,
            "choices": choices,
            "character": self.character.copy(),
            "turn_count": len(self.conversation_history)
        }
    
    def process_choice(self, choice_index: int) -> Dict[str, Any]:
        """Process player choice"""
        if not self.conversation_history:
            raise ValueError("No game started")
        
        # Get last choices
        last_response = self.conversation_history[-1]
        choices = self._extract_choices(last_response)
        
        if choice_index < 0 or choice_index >= len(choices):
            raise ValueError(f"Invalid choice: {choice_index}")
        
        selected_choice = choices[choice_index]
        self.character["age"] += 1
        
        # Build context
        recent_history = "\n\n---\n\n".join(self.conversation_history[-10:])
        
        # Build prompt
        prompt = f"""{self.system_prompt}

CONTEXT (Recent events):
{recent_history}

CURRENT STATE:
- Name: {self.character['name']}
- Age: {self.character['age']}
- Gender: {self.character['gender']}
- Talent: {self.character['talent']}

PLAYER CHOICE:
{choice_index + 1}. {selected_choice}

TASK:
Continue story for this year based on choice.
Show consequences, character development, cultivation progress.
Use world data (locations, sects) for consistency.
End with 4 new CHOICES for next year.

FORMAT:
[Story narrative]

CHOICES:
1. [choice 1]
2. [choice 2]
3. [choice 3]
4. [choice 4]
"""
        
        # Call Gemini
        response = self.model.generate_content(prompt)
        narrative = response.text
        
        # Extract new choices
        new_choices = self._extract_choices(narrative)
        
        # Save to history
        self.conversation_history.append(
            f"[AGE {self.character['age']}] Choice: {selected_choice}\n{narrative}"
        )
        
        return {
            "narrative": narrative,
            "choices": new_choices,
            "age": self.character["age"],
            "character": self.character.copy(),
            "turn_count": len(self.conversation_history)
        }
    
    def _extract_choices(self, text: str) -> List[str]:
        """Extract choices from narrative (same as simple version)"""
        choices = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 3 and line[0].isdigit() and line[1] in '.):':
                choice_text = line[2:].strip()
                if choice_text:
                    choices.append(choice_text)
        
        return choices[:4]
    
    def get_state(self) -> Dict[str, Any]:
        """Get game state"""
        return {
            "character": self.character.copy(),
            "turn_count": len(self.conversation_history),
            "last_narrative": self.conversation_history[-1] if self.conversation_history else "",
            "world_data_loaded": {
                "locations": len(self.world_data.get('locations', {})),
                "sects": len(self.world_data.get('sects', {})),
                "races": len(self.world_data.get('races', {})),
            }
        }
    
    def save_to_file(self, filename: str = "hybrid_save.json"):
        """Save game"""
        save_data = {
            "character": self.character,
            "conversation_history": self.conversation_history,
            "version": "hybrid"
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved to {filename}")
    
    def load_from_file(self, filename: str = "hybrid_save.json"):
        """Load game"""
        with open(filename, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        self.character = save_data["character"]
        self.conversation_history = save_data["conversation_history"]
        print(f"✅ Loaded from {filename}")


# CLI for testing
def main():
    print("\n" + "="*60)
    print("🌟 HYBRID CULTIVATION GAME")
    print("="*60)
    print("Combining:")
    print("  - Simple core (AI logic)")
    print("  - World data (consistency)")
    print("  - Content templates (quality)")
    print("="*60 + "\n")
    
    game = HybridCultivationGame()
    
    # Character creation
    print("📝 Character Creation")
    name = input("Name (Enter for auto-generate): ").strip()
    if not name and game.naming_system:
        print("🎲 Auto-generating Chinese name...")
    gender = input("Gender (Nam/Nữ, Enter='Nam'): ").strip() or "Nam"
    
    print("\nTalent:")
    print("1. Thiên Linh Căn")
    print("2. Bình thường")
    print("3. Phế Vật")
    talent_choice = input("Choose (1-3, Enter=2): ").strip() or "2"
    talent_map = {"1": "Thiên Linh Căn", "2": "Bình thường", "3": "Phế Vật"}
    talent = talent_map.get(talent_choice, "Bình thường")
    
    print("\n⏳ Creating character...")
    result = game.create_character(name=name or None, gender=gender, talent=talent)
    
    print("\n" + "="*60)
    print("📖 STORY:")
    print("="*60)
    print(result["narrative"])
    
    # Game loop
    while True:
        print("\n" + "-"*60)
        print(f"📅 Age: {game.character['age']} | Turns: {result['turn_count']}")
        print("-"*60)
        
        choices = result.get("choices", [])
        if not choices:
            print("Game over?")
            break
        
        print("\n🎯 CHOICES:")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        choice_input = input("\nChoice (1-4, 's'=save, 'q'=quit): ").strip().lower()
        
        if choice_input == 'q':
            if input("Save? (y/n): ").lower() == 'y':
                game.save_to_file()
            break
        
        if choice_input == 's':
            game.save_to_file()
            continue
        
        try:
            idx = int(choice_input) - 1
            print("\n⏳ Processing...")
            result = game.process_choice(idx)
            
            print("\n" + "="*60)
            print("📖 STORY:")
            print("="*60)
            print(result["narrative"])
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
