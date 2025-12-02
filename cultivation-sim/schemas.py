"""
Pydantic Schemas for Cultivation Simulator
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
import json


class CharacterData(BaseModel):
    """Character creation data"""
    gender: str = Field(..., description="Giới tính: Nam hoặc Nữ")
    talent: str = Field(..., description="Thiên phú")
    race: str = Field(..., description="Chủng tộc")
    background: str = Field(..., description="Bối cảnh")


class GameState(BaseModel):
    """Game state"""
    save_id: str
    character_name: Optional[str] = None
    age: int = 0
    gender: Optional[str] = None
    talent: Optional[str] = None
    race: Optional[str] = None
    background: Optional[str] = None
    character_story: Optional[str] = None
    current_choices: List[str] = []
    turn_count: int = 0


class CultivationLLMResponse(BaseModel):
    """LLM response schema (same as engine version)"""
    narrative: str = Field(..., min_length=10, max_length=5000)
    choices: List[str] = Field(..., min_length=4, max_length=6)
    action_intent: str = Field(default="YEAR_PROGRESS")
    state_updates: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('choices')
    @classmethod
    def validate_choices(cls, v):
        """Ensure 4-6 choices"""
        if len(v) < 4:
            default = ["Tiếp tục tu luyện", "Nghỉ ngơi", "Khám phá", "Giao lưu"]
            v = v + default[len(v):4]
        return v[:6]
    
    @classmethod
    def parse_with_fallback(cls, raw_text: str) -> 'CultivationLLMResponse':
        """Parse with fallback"""
        import json
        text = raw_text.strip()
        
        # Extract JSON
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()
        
        # Try parsing
        try:
            data = json.loads(text)
            return cls(**data)
        except:
            return cls._create_fallback()
    
    @classmethod
    def _create_fallback(cls) -> 'CultivationLLMResponse':
        """Create fallback response"""
        return cls(
            narrative="Có lỗi xảy ra. Vui lòng thử lại.",
            choices=["Tiếp tục tu luyện", "Nghỉ ngơi", "Khám phá", "Giao lưu"],
            action_intent="ERROR",
            state_updates={}
        )


def create_fallback_response() -> Dict[str, Any]:
    """Create fallback response"""
    return {
        "narrative": "Có lỗi xảy ra. Vui lòng thử lại.",
        "choices": [
            "Tiếp tục tu luyện",
            "Nghỉ ngơi",
            "Khám phá",
            "Giao lưu"
        ],
        "action_intent": "ERROR",
        "state_updates": {}
    }

