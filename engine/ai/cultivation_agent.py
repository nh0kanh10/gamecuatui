"""
Cultivation Agent - Specialized AI for Cultivation Simulator
Uses cultivation-specific prompt
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from pathlib import Path
from engine.ai.schemas import GameContext


class CultivationAgent:
    """AI agent specialized for Cultivation Simulator using Gemini 1.5 Flash"""
    
    def __init__(self, model_name: str = None):
        env_model = os.environ.get("GEMINI_MODEL")
        self.model_name = model_name or env_model or 'gemini-2.0-flash'
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables.")
            print("   Please set it in .env or your system environment.")
        
        genai.configure(api_key=api_key)
        
        # Load cultivation-specific prompt
        prompt_path = Path(__file__).parent.parent.parent / "data" / "prompts" / "cultivation_master.md"
        system_instruction = ""
        if prompt_path.exists():
            with open(prompt_path, 'r', encoding='utf-8') as f:
                system_instruction = f.read()
        else:
            # Fallback prompt
            system_instruction = """Bạn là Cultivation Master cho game tu tiên simulation.
            Nhiệm vụ: Tạo câu chuyện từ nhỏ đến lớn, đưa ra 4-6 lựa chọn mỗi năm.
            Bối cảnh: Xianxia (Tu Tiên) với các yếu tố trùng sinh, chuyển sinh, cultivation realms."""
        
        # Configure Safety Settings
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
        self._history_buffer = []
    
    def process_turn(self, user_input: str, context: GameContext, save_id: str = "default", 
                     character_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a turn for cultivation simulator
        Returns narrative and choices for next year
        """
        from engine.memory import get_memory_manager
        memory_manager = get_memory_manager()
        
        # Get relevant context
        memory_context = memory_manager.get_relevant_context(
            query=user_input,
            save_id=save_id,
            location_id=context.current_room_id,
            include_lore=True,
            n_results=5
        )
        
        # Build prompt with character data
        char_info = ""
        if character_data:
            char_info = f"""
CHARACTER INFO:
- Age: {character_data.get('age', 0)}
- Gender: {character_data.get('gender', 'Unknown')}
- Talent: {character_data.get('talent', 'Unknown')}
- Race: {character_data.get('race', 'Unknown')}
- Background: {character_data.get('background', 'Unknown')}
"""
        
        prompt = f"""
CURRENT STATE:
- Player: {context.player_name} (HP: {context.player_hp}/{context.player_max_hp})
- Location: {context.current_room_id}
- Description: {context.room_description}
{char_info}
RELEVANT MEMORIES (Context from past turns):
{memory_context}

USER INPUT: "{user_input}"

QUAN TRỌNG: 
- Khi player chọn một lựa chọn, mô tả những gì xảy ra trong năm đó
- Sau đó đưa ra 4-6 lựa chọn cho năm tiếp theo
- KHÔNG BAO GIỜ kết thúc bằng câu hỏi tu từ
- Cho thông tin cụ thể về những gì xảy ra

Generate the JSON response with format:
{{
  "narrative": "Câu chuyện năm này...",
  "choices": ["Lựa chọn 1", "Lựa chọn 2", "Lựa chọn 3", "Lựa chọn 4"],
  "action_intent": "YEAR_PROGRESS",
  "state_updates": {{"age": new_age, ...}}
}}
"""
        
        try:
            response = self.chat.send_message(prompt)
            
            # Clean up response text
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()
            
            data = json.loads(text)
            
            # Save to memory
            if 'narrative' in data:
                memory_manager.remember_action(
                    user_input=user_input,
                    narrative=data['narrative'],
                    save_id=save_id,
                    entity_id=context.player_id if hasattr(context, 'player_id') else None,
                    location_id=context.current_room_id,
                    importance=0.7
                )
            
            return data
            
        except Exception as e:
            print(f"⚠️  Cultivation Agent Error: {e}")
            return {
                "narrative": "Cultivation Master đang suy nghĩ... (AI Error)",
                "choices": ["Tiếp tục tu luyện", "Nghỉ ngơi", "Khám phá", "Giao lưu"],
                "action_intent": "ERROR",
                "state_updates": {}
            }


# Global instance
_cultivation_agent = None

def get_cultivation_agent() -> CultivationAgent:
    global _cultivation_agent
    if _cultivation_agent is None:
        _cultivation_agent = CultivationAgent()
    return _cultivation_agent

