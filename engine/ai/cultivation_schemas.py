"""
Pydantic Schemas for Cultivation Simulator LLM Responses
Strict validation to prevent parsing crashes and injection attacks
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Annotated
from pydantic import StringConstraints
import json


class CultivationLLMResponse(BaseModel):
    """
    Strict schema for Cultivation Simulator LLM responses
    Prevents parsing crashes and undefined state
    """
    
    narrative: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Narrative text describing what happened this year"
    )
    
    choices: List[str] = Field(
        ...,
        min_length=4,
        max_length=6,
        description="List of 4-6 choices for next year"
    )
    
    action_intent: str = Field(
        default="YEAR_PROGRESS",
        description="Action intent, should be YEAR_PROGRESS for normal turns"
    )
    
    state_updates: Dict[str, Any] = Field(
        default_factory=dict,
        description="State updates (age, cultivation_realm, etc.)"
    )
    
    @field_validator('narrative')
    @classmethod
    def validate_narrative(cls, v):
        """Sanitize narrative text"""
        if not v or not v.strip():
            raise ValueError("Narrative cannot be empty")
        # Remove potential prompt injection patterns
        v = v.replace("```", "").replace("---", "")
        # Limit length
        if len(v) > 5000:
            v = v[:5000] + "..."
        return v.strip()
    
    @field_validator('choices')
    @classmethod
    def validate_choices(cls, v):
        """Validate and sanitize choices"""
        if not v:
            raise ValueError("Choices list cannot be empty")
        
        # Ensure 4-6 choices
        if len(v) < 4:
            # Pad with default choices
            default_choices = [
                "Tiếp tục tu luyện",
                "Nghỉ ngơi",
                "Khám phá",
                "Giao lưu"
            ]
            v = v + default_choices[len(v):4]
        elif len(v) > 6:
            v = v[:6]
        
        # Sanitize each choice
        sanitized = []
        for choice in v:
            if not choice or not choice.strip():
                continue
            # Remove prompt injection patterns
            choice = choice.replace("```", "").replace("---", "")
            # Limit length
            if len(choice) > 200:
                choice = choice[:200]
            sanitized.append(choice.strip())
        
        # Ensure at least 4 valid choices
        if len(sanitized) < 4:
            sanitized = sanitized + [
                "Tiếp tục tu luyện",
                "Nghỉ ngơi",
                "Khám phá",
                "Giao lưu"
            ][:4 - len(sanitized)]
        
        return sanitized[:6]
    
    @field_validator('state_updates')
    @classmethod
    def validate_state_updates(cls, v):
        """Validate state updates"""
        if not isinstance(v, dict):
            return {}
        
        # Whitelist allowed keys
        allowed_keys = {
            'age', 'cultivation_realm', 'spiritual_power', 
            'new_location_id', 'hp', 'max_hp', 'mana', 'max_mana'
        }
        
        # Filter out unknown keys
        filtered = {k: v for k, v in v.items() if k in allowed_keys}
        
        # Validate types
        if 'age' in filtered and not isinstance(filtered['age'], int):
            filtered.pop('age', None)
        if 'spiritual_power' in filtered and not isinstance(filtered['spiritual_power'], (int, float)):
            filtered.pop('spiritual_power', None)
        
        return filtered
    
    @classmethod
    def parse_with_fallback(cls, raw_text: str, max_retries: int = 3) -> 'CultivationLLMResponse':
        """
        Parse LLM response with fallback handling
        Handles JSON parsing errors, malformed responses, and hallucinations
        """
        # Clean up raw text
        text = raw_text.strip()
        
        # Try to extract JSON
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
        
        # Try to find JSON object
        if text.startswith("{"):
            # Find matching closing brace
            brace_count = 0
            end_idx = -1
            for i, char in enumerate(text):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            if end_idx > 0:
                text = text[:end_idx]
        
        # Try parsing JSON
        for attempt in range(max_retries):
            try:
                data = json.loads(text)
                # Validate with Pydantic
                return cls(**data)
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    # Try to fix common JSON errors
                    text = text.replace("'", '"')  # Single to double quotes
                    text = text.replace("None", "null")  # Python None
                    text = text.replace("True", "true")  # Python True
                    text = text.replace("False", "false")  # Python False
                    continue
                else:
                    # Last attempt failed, use fallback
                    return cls._create_fallback_response()
            except Exception as e:
                # Pydantic validation error or other error
                if attempt < max_retries - 1:
                    # Try to extract what we can
                    try:
                        data = json.loads(text)
                        # Try to fix missing fields
                        if 'narrative' not in data:
                            data['narrative'] = "Có lỗi xảy ra khi tạo câu chuyện..."
                        if 'choices' not in data or not data['choices']:
                            data['choices'] = [
                                "Tiếp tục tu luyện",
                                "Nghỉ ngơi",
                                "Khám phá",
                                "Giao lưu"
                            ]
                        return cls(**data)
                    except:
                        pass
                return cls._create_fallback_response()
        
        # All attempts failed
        return cls._create_fallback_response()
    
    @classmethod
    def _create_fallback_response(cls) -> 'CultivationLLMResponse':
        """Create a safe fallback response when parsing fails"""
        return cls(
            narrative="Có lỗi xảy ra khi tạo câu chuyện. Vui lòng thử lại.",
            choices=[
                "Tiếp tục tu luyện",
                "Nghỉ ngơi",
                "Khám phá",
                "Giao lưu"
            ],
            action_intent="ERROR",
            state_updates={}
        )


class CharacterCreationResponse(BaseModel):
    """Schema for character creation response"""
    
    narrative: str = Field(
        ...,
        min_length=50,
        max_length=2000,
        description="Character background story"
    )
    
    choices: List[str] = Field(
        ...,
        min_length=4,
        max_length=6,
        description="Initial choices for age 1"
    )
    
    character_name: Optional[str] = Field(
        None,
        max_length=50,
        description="Generated character name"
    )
    
    @classmethod
    def parse_with_fallback(cls, raw_text: str) -> 'CharacterCreationResponse':
        """Parse character creation response with fallback"""
        try:
            # Try to extract JSON
            text = raw_text.strip()
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
            
            data = json.loads(text)
            
            # Extract character name from narrative if not provided
            if 'character_name' not in data and 'narrative' in data:
                # Try to extract name (first sentence usually contains name)
                narrative = data['narrative']
                if "tên là" in narrative:
                    name_part = narrative.split("tên là")[1].split(".")[0].strip()
                    if len(name_part) < 50:
                        data['character_name'] = name_part
            
            return cls(**data)
        except Exception:
            # Fallback
            return cls(
                narrative="Ngươi được sinh ra trong một gia đình tu tiên. Cuộc hành trình bắt đầu...",
                choices=[
                    "Tập trung phát triển thể chất",
                    "Nghe các trưởng lão kể chuyện",
                    "Chơi đùa với các đứa trẻ khác",
                    "Quan sát cha mẹ tu luyện"
                ],
                character_name=None
            )

