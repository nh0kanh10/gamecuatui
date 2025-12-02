"""
Cultivation Agent - AI Agent cho Cultivation Simulator
Enhanced với World Bible và World Database integration
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

from schemas import CultivationLLMResponse, CharacterCreationResponse
from world_bible import WorldBible
from world_database import WorldDatabase

load_dotenv()


class CultivationAgent:
    """
    AI Agent cho Cultivation Simulator
    
    Enhanced với:
    - World Bible integration (consistency control)
    - World Database context (sects, techniques, locations)
    - 3-tier Memory context
    - Structured output validation
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        
        # Load World Bible
        self.world_bible = WorldBible.load_from_file("data/world_bible.json")
        if not Path("data/world_bible.json").exists():
            # Create default if not exists
            self.world_bible.save_to_file("data/world_bible.json")
        
        # Load World Database
        self.world_db = WorldDatabase("data")
        
        # Load system instruction
        prompt_path = Path("data/prompts/master.md")
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                system_instruction = f.read()
        else:
            system_instruction = self._get_default_system_instruction()
        
        # Enhance system instruction với World Bible
        system_instruction = self._enhance_system_instruction(system_instruction)
        
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            system_instruction=system_instruction,
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )
    
    def _get_default_system_instruction(self) -> str:
        """Default system instruction nếu không có file"""
        return """
Bạn là Cultivation Master, điều khiển thế giới tu tiên.

Nhiệm vụ:
- Tạo narrative phong phú, sống động
- Đưa ra 4-6 lựa chọn cho người chơi
- Tuân thủ World Bible (hard facts)
- Sử dụng World Database context (sects, techniques, locations)

Format output: JSON với narrative, choices, action_intent, state_updates.
"""
    
    def _enhance_system_instruction(self, base_instruction: str) -> str:
        """Enhance system instruction với World Bible"""
        world_bible_text = self.world_bible.get_pre_prompt_text()
        
        enhanced = f"""
{base_instruction}

{world_bible_text}

QUAN TRỌNG:
- CHỈ sử dụng thông tin từ World Bible và World Database
- KHÔNG bịa đặt facts về realms, abilities, locations
- Nếu không biết, trả lời "Không biết"
"""
        return enhanced
    
    def process_turn(
        self,
        character_data: Dict[str, Any],
        current_choice: Optional[int] = None,
        memory_context: Optional[str] = None,
        working_memory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Xử lý một lượt chơi
        
        Enhanced với:
        - Memory context (3-tier)
        - Working memory (current tasks)
        - World Database context (location, sect, etc.)
        """
        
        # Build prompt với full context
        prompt = self._build_prompt(
            character_data=character_data,
            current_choice=current_choice,
            memory_context=memory_context,
            working_memory=working_memory
        )
        
        # Call AI
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse JSON
            result = self._parse_response(text, character_data)
            
            # Verify với World Bible
            verification = self.world_bible.verify_output(result)
            if not verification["valid"]:
                print(f"⚠️ World Bible violations: {verification['violations']}")
                if verification.get("corrected"):
                    result = verification["corrected"]
            
            return result
        
        except Exception as e:
            print(f"❌ AI Error: {e}")
            return self._create_fallback_response(character_data)
    
    def _build_prompt(
        self,
        character_data: Dict[str, Any],
        current_choice: Optional[int] = None,
        memory_context: Optional[str] = None,
        working_memory: Optional[str] = None
    ) -> str:
        """Build prompt với full context"""
        
        # Character info
        age = character_data.get("age", 0)
        gender = character_data.get("gender", "Unknown")
        talent = character_data.get("talent", "Unknown")
        race = character_data.get("race", "Unknown")
        background = character_data.get("background", "Unknown")
        story = character_data.get("story", "")
        
        # Cultivation info
        cultivation = character_data.get("cultivation", {})
        realm = cultivation.get("realm", "Mortal")
        realm_level = cultivation.get("realm_level", 0)
        
        # Attributes
        attributes = character_data.get("attributes", {})
        from attributes import AttributesComponent
        if attributes:
            attrs = AttributesComponent(**attributes)
            ai_context = attrs.get_ai_context_string()
        else:
            ai_context = "Attributes not available"
        
        # Location context từ World Database
        location_id = character_data.get("location_id")
        location_context = ""
        if location_id:
            location = self.world_db.get_location(location_id)
            if location:
                # Get regional culture
                culture = self.world_db.get_culture_by_location(location_id)
                culture_info = ""
                if culture:
                    culture_info = f"""
Văn hóa vùng: {culture.get('name', 'Unknown')} - {culture.get('vibe', 'Unknown')}
Quy tắc xã hội: {json.dumps(culture.get('social_rules', {}), ensure_ascii=False)}
Đặc điểm văn hóa: {', '.join([t.get('effect', '') for t in culture.get('cultural_traits', [])[:3]])}
"""
                
                location_context = f"""
Địa điểm: {location['name']} ({location.get('region', 'Unknown')})
Loại: {location.get('type', 'Unknown')}
Mật độ linh khí: {location.get('qi_density', 1.0)}x
Dịch vụ: {', '.join(location.get('services', []))}
Nguy hiểm: {location.get('danger_level', 'Unknown')}
Kết nối: {', '.join([self.world_db.get_location(lid).get('name', lid) for lid in location.get('connected_to', []) if self.world_db.get_location(lid)])}
{culture_info}
"""
        
        # Sect context từ World Database
        sect_id = character_data.get("sect_id")
        sect_context = character_data.get("sect_context", "")
        if not sect_context and sect_id:
            sect = self.world_db.get_sect(sect_id)
            if sect:
                sect_context = f"""
Tông môn: {sect['name']} ({sect.get('type', 'Unknown')})
Triết lý: {sect.get('description', '')}
Kỹ thuật độc quyền: {', '.join(sect.get('exclusive_techniques', []))}
Yêu cầu: {json.dumps(sect.get('requirements', {}), ensure_ascii=False)}
"""
        
        # Race context từ World Database
        race_id = character_data.get("race")
        race_context = ""
        if race_id:
            race = self.world_db.get_race(race_id)
            if race:
                race_context = f"""
Chủng tộc: {race.get('name', race_id)}
Mô tả: {race.get('description', '')}
Đặc điểm: {', '.join(race.get('traits', []))}
"""
        
        # Build full prompt
        prompt = f"""
=== CHARACTER DATA ===
Tuổi: {age}
Giới tính: {gender}
Thiên phú: {talent}
Chủng tộc: {race}
Bối cảnh: {background}
Câu chuyện: {story}

=== CULTIVATION ===
Cảnh giới: {realm} (Level {realm_level})
Tu vi: {cultivation.get('spiritual_power', 0)}/{cultivation.get('max_spiritual_power', 100)}
Tiến độ đột phá: {cultivation.get('breakthrough_progress', 0.0)}%

=== ATTRIBUTES ===
{ai_context}

=== LOCATION ===
{location_context}

=== SECT ===
{sect_context}

=== RACE ===
{race_context}

=== MEMORY ===
{memory_context or "Không có ký ức"}

=== WORKING MEMORY ===
{working_memory or "Không có nhiệm vụ"}

=== CURRENT ACTION ===
"""
        
        if current_choice is not None:
            choices = character_data.get("choices", [])
            if 0 <= current_choice < len(choices):
                prompt += f"Người chơi chọn: {choices[current_choice]}\n"
        else:
            prompt += "Người chơi đang chờ lựa chọn.\n"
        
        prompt += """
=== INSTRUCTIONS ===
1. Tạo narrative mô tả những gì xảy ra (cụ thể, không đặt câu hỏi tu từ)
2. Đưa ra 4-6 lựa chọn cho năm tiếp theo
3. Xác định action_intent và state_updates

Format JSON:
{
    "narrative": "Mô tả cụ thể...",
    "choices": ["Lựa chọn 1", "Lựa chọn 2", ...],
    "action_intent": "YEAR_PROGRESS",
    "state_updates": {
        "age": 1,
        "cultivation": {...},
        "resources": {...}
    }
}
"""
        
        return prompt
    
    def _parse_response(self, text: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response với fallback"""
        # Try to extract JSON
        try:
            # Remove markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            data = json.loads(text)
            
            # Validate với Pydantic schema
            try:
                response = CultivationLLMResponse(**data)
                return response.dict()
            except Exception as e:
                print(f"⚠️ Schema validation error: {e}")
                return self._create_fallback_response(character_data, data)
        
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            return self._create_fallback_response(character_data)
    
    def _create_fallback_response(
        self,
        character_data: Dict[str, Any],
        partial_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Tạo fallback response khi AI fail"""
        age = character_data.get("age", 0)
        
        if partial_data:
            # Use partial data if available
            narrative = partial_data.get("narrative", f"Năm {age} trôi qua...")
            choices = partial_data.get("choices", [])
        else:
            narrative = f"Năm {age} trôi qua một cách bình thường."
            choices = [
                "Tiếp tục tu luyện",
                "Đi khám phá",
                "Tìm tông môn",
                "Nghỉ ngơi"
            ]
        
        # Ensure 4-6 choices
        while len(choices) < 4:
            choices.append(f"Lựa chọn {len(choices) + 1}")
        choices = choices[:6]
        
        return {
            "narrative": narrative,
            "choices": choices,
            "action_intent": "YEAR_PROGRESS",
            "state_updates": {
                "age": age + 1
            }
        }
    
    async def plan_action(self, prompt: str) -> Dict[str, Any]:
        """
        AI Planning method cho AIPlannerSystem
        
        Returns:
            {
                "thought_process": str,
                "emotional_state": str,
                "decision": {...}
            }
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        
        except Exception as e:
            print(f"❌ AI Planning error: {e}")
            return {
                "thought_process": "Không có suy nghĩ đặc biệt",
                "emotional_state": "Calm",
                "decision": {
                    "action_type": "rest",
                    "target_id": None,
                    "dialogue_content": None
                }
            }
    
    async def create_summary(self, conversations: List[str]) -> str:
        """
        Tạo summary từ conversations (cho Rolling Summary)
        """
        prompt = f"""
Tóm tắt các cuộc hội thoại sau đây, tập trung vào:
- Thay đổi quan hệ
- Thông tin mới học được
- Lời hứa hẹn
- Sự kiện quan trọng

Conversations:
{chr(10).join(conversations)}

Tóm tắt ngắn gọn (20-30 từ):
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Summary error: {e}")
            return f"Tóm tắt {len(conversations)} cuộc hội thoại"
