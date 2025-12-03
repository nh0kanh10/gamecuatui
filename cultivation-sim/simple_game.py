"""
SIMPLE CULTIVATION GAME - 200 Lines Version
Chỉ dùng Gemini API + basic conversation history
Không có Memory3Tier, ECS, WorldDB, hay bất cứ complexity nào

So sánh với game.py (795 lines) + toàn bộ systems (~5000 lines total)
"""

import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class SimpleCultivationGame:
    """
    Cultivation game đơn giản nhất có thể
    Chỉ cần:
    - Gemini API
    - Conversation history (list)
    - Character data (dict)
    """
    
    def __init__(self):
        # Setup Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Game state - chỉ cần 2 thứ này thôi!
        self.conversation_history: List[str] = []
        self.character: Dict[str, Any] = {
            "name": "",
            "age": 0,
            "gender": "",
            "talent": "",
            "race": "",
            "background": ""
        }
        
        # System prompt - đây là chìa khóa thành công!
        self.system_prompt = """
Bạn là AI storyteller cho game tu tiên (cultivation/xianxia).

WORLD SETTING:
- Thế giới tu tiên với 9 cảnh giới: Luyện Khí → Trúc Cơ → Kim Đan → Nguyên Anh → Hóa Thần → Luyện Hư → Hợp Thể → Đại Thừa → Đột Phá
- Tông môn: Thanh Vân Môn (chính phái), Quỷ Vương Tông (ma đạo), Băng Hà Cốc (trung lập)
- Locations: Làng Bình An, Núi Thanh Vân, Thành Thiên Nam, Sa Mạc Vô Tận
- Spirit stones là currency chính
- Pills, artifacts, spirit beasts, herbs đều quan trọng

RULES:
1. Mỗi turn = 1 năm trong game
2. Generate câu chuyện dựa trên lựa chọn của player
3. Luôn cho 4 lựa chọn cho năm tiếp theo
4. Track cultivation progress naturally trong narrative
5. Consequences của choices phải rõ ràng
6. Stay consistent với world setting

FORMAT:
Viết narrative tự nhiên, kể chuyện sinh động như novel.
Kết thúc với 4 CHOICES rõ ràng, đánh số 1-4.

IMPORTANT: 
- Nhớ context từ lịch sử trước đó
- Consistent với personality và choices đã chọn
- Progressive difficulty theo age
"""
    
    def create_character(
        self,
        name: str = "Lâm Tiêu",
        gender: str = "Nam",
        talent: str = "Bình thường",
        race: str = "Người",
        background: str = "Nông dân"
    ) -> Dict[str, Any]:
        """
        Tạo nhân vật mới
        Returns: {narrative, choices}
        """
        # Update character data
        self.character.update({
            "name": name,
            "age": 0,
            "gender": gender,
            "talent": talent,
            "race": race,
            "background": background
        })
        
        # Build prompt
        prompt = f"""{self.system_prompt}

TASK: Tạo background cho nhân vật mới sinh ra

CHARACTER:
- Tên: {name}
- Giới tính: {gender}
- Thiên phú: {talent}
- Chủng tộc: {race}
- Bối cảnh: {background}

Viết câu chuyện về lúc nhân vật mới sinh ra.
Describe gia đình, hoàn cảnh, dấu hiệu về thiên phú.
Kết thúc với 4 CHOICES cho năm đầu tiên (age 0->1).
"""
        
        # Call Gemini
        response = self.model.generate_content(prompt)
        narrative = response.text
        
        # Parse choices (simple regex hoặc string manipulation)
        choices = self._extract_choices(narrative)
        
        # Save to history
        self.conversation_history.append(f"[CHARACTER CREATION]\n{narrative}")
        
        return {
            "narrative": narrative,
            "choices": choices,
            "character": self.character.copy()
        }
    
    def process_choice(self, choice_index: int) -> Dict[str, Any]:
        """
        Xử lý lựa chọn của player
        Returns: {narrative, choices, age}
        """
        # Validate choice
        if not self.conversation_history:
            raise ValueError("No game started. Call create_character first.")
        
        # Get last choices from conversation
        last_response = self.conversation_history[-1]
        choices = self._extract_choices(last_response)
        
        if choice_index < 0 or choice_index >= len(choices):
            raise ValueError(f"Invalid choice index: {choice_index}")
        
        selected_choice = choices[choice_index]
        
        # Update age
        self.character["age"] += 1
        
        # Build context from recent history (last 10 turns)
        recent_history = "\n\n---\n\n".join(self.conversation_history[-10:])
        
        # Build prompt
        prompt = f"""{self.system_prompt}

CONTEXT (Recent History):
{recent_history}

CURRENT STATE:
- Name: {self.character['name']}
- Age: {self.character['age']}
- Gender: {self.character['gender']}
- Talent: {self.character['talent']}

PLAYER CHOICE:
{choice_index + 1}. {selected_choice}

TASK:
Viết câu chuyện cho năm tiếp theo dựa trên choice này.
Show consequences, character development, cultivation progress.
Kết thúc với 4 CHOICES mới cho năm sau.
"""
        
        # Call Gemini
        response = self.model.generate_content(prompt)
        narrative = response.text
        
        # Parse new choices
        new_choices = self._extract_choices(narrative)
        
        # Save to history
        self.conversation_history.append(
            f"[AGE {self.character['age']}] Choice: {selected_choice}\n{narrative}"
        )
        
        return {
            "narrative": narrative,
            "choices": new_choices,
            "age": self.character["age"],
            "character": self.character.copy()
        }
    
    def _extract_choices(self, text: str) -> List[str]:
        """
        Extract choices from narrative
        Simple parser - tìm lines bắt đầu với số
        """
        choices = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Check if line starts with number (1., 2., 3., 4.)
            if line and len(line) > 3 and line[0].isdigit() and line[1] in '.):':
                # Remove number prefix
                choice_text = line[2:].strip()
                if choice_text:
                    choices.append(choice_text)
        
        return choices[:4]  # Max 4 choices
    
    def get_state(self) -> Dict[str, Any]:
        """Get current game state"""
        return {
            "character": self.character.copy(),
            "turn_count": len(self.conversation_history),
            "last_narrative": self.conversation_history[-1] if self.conversation_history else ""
        }
    
    def save_to_file(self, filename: str = "simple_save.json"):
        """Save game to JSON file"""
        save_data = {
            "character": self.character,
            "conversation_history": self.conversation_history
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Game saved to {filename}")
    
    def load_from_file(self, filename: str = "simple_save.json"):
        """Load game from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        self.character = save_data["character"]
        self.conversation_history = save_data["conversation_history"]
        print(f"✅ Game loaded from {filename}")


# ============================================
# CLI Interface (for testing)
# ============================================

def main():
    """Simple CLI to test the game"""
    print("\n" + "="*60)
    print("🌟 SIMPLE CULTIVATION GAME")
    print("="*60 + "\n")
    
    game = SimpleCultivationGame()
    
    # Create character
    print("📝 Character Creation")
    name = input("Name (Enter for 'Lâm Tiêu'): ").strip() or "Lâm Tiêu"
    gender = input("Gender (Nam/Nữ, Enter for 'Nam'): ").strip() or "Nam"
    
    print("\nTalent options:")
    print("1. Thiên Linh Căn (Genius)")
    print("2. Bình thường (Normal)")
    print("3. Phế Vật (Trash)")
    talent_choice = input("Choose (1-3, Enter for 2): ").strip() or "2"
    talent_map = {"1": "Thiên Linh Căn", "2": "Bình thường", "3": "Phế Vật"}
    talent = talent_map.get(talent_choice, "Bình thường")
    
    print("\n⏳ Creating character...")
    result = game.create_character(name=name, gender=gender, talent=talent)
    
    print("\n" + "="*60)
    print("📖 STORY:")
    print("="*60)
    print(result["narrative"])
    
    # Game loop
    while True:
        print("\n" + "-"*60)
        print(f"📅 Current Age: {game.character['age']}")
        print("-"*60)
        
        choices = result.get("choices", [])
        if not choices:
            print("❌ No choices available. Game over?")
            break
        
        print("\n🎯 CHOICES:")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        # Get player input
        choice_input = input("\nYour choice (1-4, 's' to save, 'q' to quit): ").strip().lower()
        
        if choice_input == 'q':
            save = input("Save before quit? (y/n): ").strip().lower()
            if save == 'y':
                game.save_to_file()
            print("\n👋 Goodbye!")
            break
        
        if choice_input == 's':
            game.save_to_file()
            continue
        
        try:
            choice_idx = int(choice_input) - 1
            print("\n⏳ Processing...")
            result = game.process_choice(choice_idx)
            
            print("\n" + "="*60)
            print("📖 STORY:")
            print("="*60)
            print(result["narrative"])
            
        except ValueError as e:
            print(f"❌ Invalid choice: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()
