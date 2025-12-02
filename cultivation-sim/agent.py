"""
Cultivation Agent - AI for Cultivation Simulator
Standalone version
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from pathlib import Path

from schemas import CharacterData, CultivationLLMResponse


class CultivationAgent:
    """AI agent for Cultivation Simulator"""
    
    def __init__(self, model_name: str = None):
        env_model = os.environ.get("GEMINI_MODEL")
        self.model_name = model_name or env_model or 'gemini-2.0-flash'
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        
        # Load prompt
        prompt_path = Path(__file__).parent / "data" / "prompts" / "master.md"
        if not prompt_path.exists():
            # Try parent directory (if running from root)
            prompt_path = Path(__file__).parent.parent / "data" / "prompts" / "cultivation_master.md"
        
        system_instruction = ""
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                system_instruction = f.read()
        else:
            system_instruction = """Bạn là Cultivation Master cho game tu tiên simulation.
            Nhiệm vụ: Tạo câu chuyện từ nhỏ đến lớn, đưa ra 4-6 lựa chọn mỗi năm."""
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        self.model = genai.GenerativeModel(
            self.model_name,
            safety_settings=safety_settings,
            system_instruction=system_instruction
        )
        self.chat = self.model.start_chat(history=[])
    
    def create_character(self, character_data: CharacterData) -> Dict[str, Any]:
        """Generate character background"""
        prompt = f"""
Tạo nhân vật với thông tin:
- Giới tính: {character_data.gender}
- Thiên phú: {character_data.talent}
- Chủng tộc: {character_data.race}
- Bối cảnh: {character_data.background}

Hãy tạo:
1. Tên nhân vật
2. Background story (gia đình, hoàn cảnh sinh ra)
3. 4-6 lựa chọn cho năm 1 tuổi

Format JSON:
{{
  "character_name": "Tên nhân vật",
  "narrative": "Background story...",
  "choices": ["Lựa chọn 1", "Lựa chọn 2", ...]
}}
"""
        try:
            response = self.chat.send_message(prompt)
            validated = CultivationLLMResponse.parse_with_fallback(response.text)
            data = validated.dict()
            
            # Add character_name if extracted
            if 'character_name' not in data:
                # Try to extract from narrative
                narrative = data.get('narrative', '')
                if "tên là" in narrative:
                    name_part = narrative.split("tên là")[1].split(".")[0].strip()
                    if len(name_part) < 50:
                        data['character_name'] = name_part
            
            return data
        except Exception as e:
            print(f"⚠️  Character creation error: {e}")
            from .schemas import create_fallback_response
            return create_fallback_response()
    
    def process_turn(
        self,
        user_input: str,
        character_data: Dict[str, Any],
        memory_context: str = "",
        save_id: str = "default"
    ) -> Dict[str, Any]:
        """Process a turn"""
        char_info = f"""
CHARACTER INFO:
- Age: {character_data.get('age', 0)}
- Gender: {character_data.get('gender', 'Unknown')}
- Talent: {character_data.get('talent', 'Unknown')}
- Race: {character_data.get('race', 'Unknown')}
- Background: {character_data.get('background', 'Unknown')}
"""
        
        prompt = f"""
{char_info}

RELEVANT MEMORIES:
{memory_context}

USER INPUT: "{user_input}"

QUAN TRỌNG: 
- Mô tả những gì xảy ra trong năm đó
- Đưa ra 4-6 lựa chọn cho năm tiếp theo
- KHÔNG kết thúc bằng câu hỏi tu từ

Format JSON:
{{
  "narrative": "Câu chuyện năm này...",
  "choices": ["Lựa chọn 1", "Lựa chọn 2", "Lựa chọn 3", "Lựa chọn 4"],
  "action_intent": "YEAR_PROGRESS",
  "state_updates": {{}}
}}
"""
        try:
            response = self.chat.send_message(prompt)
            validated = CultivationLLMResponse.parse_with_fallback(response.text)
            return validated.dict()
        except Exception as e:
            print(f"⚠️  Process turn error: {e}")
            from .schemas import create_fallback_response
            return create_fallback_response()

