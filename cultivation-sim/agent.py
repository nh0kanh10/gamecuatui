"""
Cultivation Agent - AI Agent cho Cultivation Simulator
Enhanced với World Bible và World Database integration
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import logging

from schemas import CultivationLLMResponse, CharacterCreationResponse
from world_bible import WorldBible
from world_database import WorldDatabase

logger = logging.getLogger(__name__)

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
        
        # Use free tier model by default, can override with GEMINI_MODEL env var
        # Priority: GEMINI_MODEL env var > gemini-1.5-flash (free tier, fast)
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        # Fallback chain: prioritize FAST models for real-time gameplay
        fallback_models = [
            model_name,  # Try requested first (gemini-2.5-flash)
            "gemini-2.5-flash",      # Fast, stable (if not already selected)
            "gemini-2.0-flash-001",  # Fast, stable 2.0 version
            "gemini-2.0-flash",      # Fast 2.0 flash
            "gemini-flash-latest",   # Latest fast flash
            "gemini-1.5-flash",      # Fast free tier fallback
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        fallback_models = [m for m in fallback_models if not (m in seen or seen.add(m))]
        
        model_initialized = False
        for model_to_try in fallback_models:
            try:
                self.model = genai.GenerativeModel(
                    model_name=model_to_try,
                    system_instruction=system_instruction,
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ],
                    generation_config={
                        "temperature": 0.7,  # Balanced creativity
                        "top_p": 0.95,      # Nucleus sampling (matches model default)
                        "top_k": 64,        # Top-k sampling (matches gemini-2.5 default)
                        "max_output_tokens": 3072,  # Balanced: enough for complete JSON, still fast
                    }
                )
                logger.info(f"✅ Using Gemini model: {model_to_try}")
                model_initialized = True
                break
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize {model_to_try}: {str(e)[:100]}")
                continue
        
        if not model_initialized:
            raise ValueError("Failed to initialize any Gemini model. Check API key and quota.")
        
        # Initialize rate limiting
        self._last_request_time = 0
    
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
        
        age = character_data.get("age", 0)
        
        # Character creation (age 0) uses different prompt
        if age == 0 and current_choice is None:
            return self.process_character_creation(character_data, memory_context, working_memory)
        
        # Build prompt với full context
        prompt = self._build_prompt(
            character_data=character_data,
            current_choice=current_choice,
            memory_context=memory_context,
            working_memory=working_memory
        )
        
        # Store prompt for debug
        self._last_prompt = prompt
        self._last_ai_response = None
        self._last_parsed_result = None
        self._last_error = None
        
        # Optimize prompt length if too long (reduce token usage)
        prompt_length = len(prompt)
        if prompt_length > 30000:  # ~7500 tokens (safety limit)
            logger.warning(f"Prompt very long ({prompt_length} chars), truncating memory context...")
            # Truncate memory context if too long
            if memory_context and len(memory_context) > 10000:
                memory_context = memory_context[:10000] + "\n[... memory truncated ...]"
                prompt = self._build_prompt(
                    character_data=character_data,
                    current_choice=current_choice,
                    memory_context=memory_context,
                    working_memory=working_memory
                )
                logger.info(f"Prompt optimized to {len(prompt)} chars")
        
        # Optimize prompt length if too long (reduce token usage)
        prompt_length = len(prompt)
        if prompt_length > 30000:  # ~7500 tokens (safety limit)
            logger.warning(f"Prompt very long ({prompt_length} chars), truncating memory context...")
            # Truncate memory context if too long
            if memory_context and len(memory_context) > 10000:
                memory_context = memory_context[:10000] + "\n[... memory truncated ...]"
                prompt = self._build_prompt(
                    character_data=character_data,
                    current_choice=current_choice,
                    memory_context=memory_context,
                    working_memory=working_memory
                )
                logger.info(f"Prompt optimized to {len(prompt)} chars")
        
        # Check AI cache first (if optimizations available)
        text = None
        if hasattr(self, '_optimizations') and self._optimizations:
            cached_response = self._optimizations.ai_cache.get(prompt)
            if cached_response:
                logger.info("✅ AI cache HIT! Using cached response")
                print(f"✅ Cache HIT! Using cached response (instant!)")
                text = cached_response
        
        # Call AI with retry logic for rate limits (only if not cached)
        if text is None:
            max_retries = 3
            retry_delay = 3  # Start with 3 seconds
            
            for attempt in range(max_retries):
                try:
                    print(f"🤖 Calling AI (attempt {attempt + 1}/{max_retries}) with choice: {current_choice}, age: {character_data.get('age')}")
                    print(f"📋 Prompt length: {len(prompt)} chars")
                    if attempt == 0:  # Only print preview on first attempt
                        print(f"📋 Prompt preview (last 500 chars): ...{prompt[-500:]}")
                    
                    response = self.model.generate_content(prompt)
                    text = response.text.strip()
                    break  # Success, exit retry loop
                except Exception as e:
                    error_str = str(e)
                
                # Check if it's a quota/rate limit error
                if "429" in error_str or "ResourceExhausted" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        # Extract retry delay from error if available
                        import re
                        delay_match = re.search(r'retry in ([\d.]+)s', error_str, re.IGNORECASE)
                        if delay_match:
                            retry_delay = float(delay_match.group(1)) + 1  # Add 1 second buffer
                        else:
                            retry_delay = retry_delay * 2  # Exponential backoff
                        
                        print(f"⚠️ Rate limit/quota exceeded. Waiting {retry_delay:.1f}s before retry {attempt + 2}/{max_retries}...")
                        logger.warning(f"Rate limit error (attempt {attempt + 1}): {error_str[:200]}")
                        import time
                        time.sleep(retry_delay)
                        continue
                    else:
                        # Last attempt failed
                        print(f"❌ Rate limit error after {max_retries} attempts. Using fallback response.")
                        logger.error(f"Rate limit error after all retries: {error_str[:500]}")
                        self._last_error = error_str
                        return self._create_fallback_response(character_data)
                else:
                    # Other error, don't retry
                    raise
        
        # If we got here without text, something went wrong
        if text is None:
            print(f"❌ Failed to get AI response after {max_retries} attempts. Using fallback.")
            return self._create_fallback_response(character_data)
        
        # Store raw response for debug
        self._last_ai_response = text
        
        # Cache response if optimizations available
        if hasattr(self, '_optimizations') and self._optimizations:
            try:
                self._optimizations.ai_cache.set(prompt, text)
            except Exception as e:
                logger.warning(f"Could not cache AI response: {e}")
        
        # Log raw response for debugging
        print(f"📝 AI Raw Response (first 1000 chars): {text[:1000]}...")
        print(f"📝 AI Raw Response length: {len(text)} chars")
        print(f"📝 AI Raw Response (last 500 chars): ...{text[-500:]}")
        
        # Parse JSON
        try:
            result = self._parse_response(text, character_data)
            
            # Store parsed result for debug
            self._last_parsed_result = result
            
            # Log parsed result
            narrative_preview = result.get('narrative', '')[:200]
            print(f"✅ Parsed result narrative (first 200 chars): {narrative_preview}...")
            print(f"✅ Parsed result narrative length: {len(result.get('narrative', ''))}")
            print(f"✅ Is this fallback? {len(result.get('narrative', '')) == 222 or 'tiếp tục tu luyện tại' in result.get('narrative', '')}")
            
            # Verify với World Bible
            verification = self.world_bible.verify_output(result)
            if not verification["valid"]:
                print(f"⚠️ World Bible violations: {verification['violations']}")
                if verification.get("corrected"):
                    result = verification["corrected"]
            
            return result
        
        except Exception as e:
            print(f"❌ AI Error: {e}")
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Character data: age={character_data.get('age')}, choice={current_choice}")
            print(f"❌ This error will cause fallback response to be used")
            
            # Store error for debug
            self._last_error = f"{str(e)}\n{error_trace}"
            
            logger.error(f"AI Error in process_turn: {str(e)}\n{error_trace}")
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
        
        # Get physique context and prompt
        physique_context = ""
        physique_id = attributes.get('physique_id') if attributes else None
        if physique_id and hasattr(self, '_game_instance') and self._game_instance:
            try:
                physique_system = getattr(self._game_instance, 'physique_system', None)
                if physique_system:
                    physique_data = physique_system.get_physique(physique_id)
                    if physique_data:
                        physique_name = physique_data.get('name', '')
                        physique_desc = physique_data.get('description', '')
                        physique_prompt = physique_system.get_ai_prompt(physique_id)
                        forbidden_words = physique_system.get_forbidden_words(physique_id)
                        
                        physique_context = f"""
Thể Chất: {physique_name}
Mô tả: {physique_desc}

⚠️ QUAN TRỌNG - PROMPT CHO THỂ CHẤT:
{physique_prompt}
"""
                        if forbidden_words:
                            physique_context += f"\n❌ KHÔNG ĐƯỢC dùng các từ: {', '.join(forbidden_words)}"
            except Exception as e:
                logger.warning(f"Error getting physique context: {e}")
        
        if not physique_context:
            physique_context = "Không có thể chất đặc biệt"
        
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
        
        # Get talent AI effect if available
        talent_ai_effect = ""
        try:
            import json
            from pathlib import Path
            talents_path = Path("data/talents_ai_friendly.json")
            if talents_path.exists():
                with open(talents_path, 'r', encoding='utf-8') as f:
                    talents_list = json.load(f)
                    for t in talents_list:
                        if t.get('name') == talent:
                            talent_ai_effect = t.get('ai_effect', '')
                            break
        except Exception as e:
            logger.warning(f"Error loading talent AI effect: {e}")
        
        # Build full prompt
        prompt = f"""
=== CHARACTER DATA ===
Tuổi: {age}
Giới tính: {gender}
Thiên phú: {talent}{f" ({talent_ai_effect})" if talent_ai_effect else ""}
Chủng tộc: {race}
Bối cảnh: {background}
Câu chuyện: {story}

=== CULTIVATION ===
Cảnh giới: {realm} (Level {realm_level})
Tu vi: {cultivation.get('spiritual_power', 0)}/{cultivation.get('max_spiritual_power', 100)}
Tiến độ đột phá: {cultivation.get('breakthrough_progress', 0.0)}%

=== ATTRIBUTES ===
{ai_context}

=== PHYSIQUE (THỂ CHẤT) ===
{physique_context}

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
        
        selected_choice_text = ""
        if current_choice is not None:
            choices = character_data.get("choices", [])
            if 0 <= current_choice < len(choices):
                selected_choice_text = choices[current_choice]
                prompt += f"""
=== NGƯỜI CHƠI ĐÃ CHỌN ===
Lựa chọn số {current_choice + 1}: "{selected_choice_text}"

⚠️⚠️⚠️ QUAN TRỌNG NHẤT ⚠️⚠️⚠️
Narrative PHẢI mô tả CỤ THỂ những gì xảy ra khi người chơi thực hiện lựa chọn "{selected_choice_text}".

VÍ DỤ CỤ THỂ:
- Nếu chọn "Tiếp tục tu luyện" → Mô tả: "Bạn ngồi xuống, nhắm mắt, bắt đầu điều khiển linh khí trong cơ thể. Dòng linh khí chảy qua các kinh mạch, bạn cảm nhận được sự tăng trưởng từng chút một. Sau nhiều tháng tu luyện, tu vi của bạn đã tăng lên..."

- Nếu chọn "Đi khám phá" → Mô tả: "Bạn quyết định rời khỏi nơi ở, bước chân ra ngoài khám phá. Bạn đi qua những con đường nhỏ, leo lên đồi, xuống thung lũng. Trong một hang động, bạn phát hiện..."

- Nếu chọn "Tìm kiếm tông môn" → Mô tả: "Bạn bắt đầu hành trình tìm kiếm tông môn. Bạn hỏi thăm người dân, đi theo những con đường lớn. Sau nhiều ngày, bạn đến được cổng một tông môn..."

- Nếu chọn "Nghỉ ngơi" → Mô tả: "Bạn quyết định nghỉ ngơi, không tu luyện. Bạn ngồi dưới gốc cây, nhìn ngắm cảnh vật xung quanh. Trong lúc nghỉ ngơi, bạn suy ngẫm về..."

KHÔNG ĐƯỢC viết chung chung như "tiếp tục tu luyện" mà PHẢI mô tả CỤ THỂ từng hành động, từng bước đi, từng sự kiện xảy ra.
"""
        else:
            prompt += "Người chơi đang chờ lựa chọn.\n"
        
        prompt += f"""
=== INSTRUCTIONS ===
QUAN TRỌNG: Tạo narrative CỤ THỂ và ĐA DẠNG cho năm thứ {age + 1}. KHÔNG được lặp lại "năm X trôi qua một cách bình thường".

1. NARRATIVE PHẢI:
   - DỰA VÀO LỰA CHỌN "{selected_choice_text if selected_choice_text else 'của người chơi'}" để tạo narrative phù hợp
   - Mô tả TỪNG BƯỚC, TỪNG HÀNH ĐỘNG cụ thể (bước đi, ngồi xuống, nhắm mắt, leo lên, xuống, gặp gỡ, nói chuyện...)
   - Mô tả CẢNH VẬT, ĐỊA ĐIỂM cụ thể (hang động, rừng cây, con đường, ngôi làng...)
   - Mô tả NGƯỜI GẶP, CUỘC TRÒ CHUYỆN nếu có
   - Mô tả KẾT QUẢ, THAY ĐỔI cụ thể (tìm được gì, học được gì, tu vi tăng bao nhiêu...)
   - Mỗi lựa chọn PHẢI dẫn đến narrative HOÀN TOÀN KHÁC NHAU
   - Dài ít nhất 5-7 câu, mô tả chi tiết từng bước

2. CHOICES:
   - Đưa ra 4-6 lựa chọn ĐA DẠNG cho năm tiếp theo
   - Mỗi lựa chọn phải dẫn đến narrative KHÁC NHAU
   - Không được lặp lại các lựa chọn giống nhau

3. STATE_UPDATES (BẮT BUỘC):
   - PHẢI cập nhật cultivation (spiritual_power tăng, breakthrough_progress thay đổi)
   - PHẢI cập nhật resources (spirit_stones, pills, materials thay đổi)
   - PHẢI cập nhật attributes nếu có thay đổi
   - Mỗi năm phải có thay đổi về stats

VÍ DỤ NARRATIVE TỐT CHO "ĐI KHÁM PHÁ":
"Năm thứ 2, bạn quyết định rời khỏi làng để khám phá thế giới xung quanh. Bạn bước đi trên con đường đất nhỏ, đi qua những cánh đồng lúa xanh mướt. Sau vài giờ đi bộ, bạn đến một khu rừng rậm. Trong rừng, bạn nghe thấy tiếng nước chảy. Bạn đi theo tiếng nước và phát hiện ra một thác nước nhỏ. Phía sau thác nước, bạn nhìn thấy một hang động ẩn khuất. Bạn cẩn thận bước vào, trong hang động tối tăm, bạn tìm thấy một viên đan dược cổ xưa còn sót lại trên một tảng đá. Sau khi sử dụng, tu vi của bạn tăng lên đáng kể."

VÍ DỤ NARRATIVE TỐT CHO "TIẾP TỤC TU LUYỆN":
"Năm thứ 2, bạn quyết định dành toàn bộ thời gian để tu luyện. Mỗi sáng, bạn ngồi xuống trên tảng đá phẳng, nhắm mắt, bắt đầu điều khiển linh khí trong cơ thể. Bạn cảm nhận dòng linh khí chảy qua các kinh mạch, từ đan điền lên đỉnh đầu rồi quay trở lại. Sau nhiều tháng tu luyện không ngừng nghỉ, bạn đã có thể điều khiển linh khí một cách thuần thục hơn. Tu vi của bạn tăng lên đáng kể, đạt được Luyện Khí Kỳ cấp 2. Bạn cảm thấy sức mạnh trong cơ thể tăng lên rõ rệt."

VÍ DỤ NARRATIVE TỆ (KHÔNG ĐƯỢC):
"Năm 2 trôi qua một cách bình thường."
"Người Tu Tiên tiếp tục tu luyện tại Làng Thanh Thủy. Với thiên phú Thiên Linh Căn, bạn đã có những tiến bộ trong việc cảm nhận và điều khiển linh khí. Mỗi ngày trôi qua đều mang lại những hiểu biết mới về thế giới tu tiên."

Format JSON:
{{
    "narrative": "Mô tả CỤ THỂ và ĐA DẠNG về những gì xảy ra trong năm...",
    "choices": ["Lựa chọn 1", "Lựa chọn 2", "Lựa chọn 3", "Lựa chọn 4"],
    "action_intent": "YEAR_PROGRESS",
    "state_updates": {{
        "age": {age + 1},
        "cultivation": {{
            "spiritual_power": <tăng lên>,
            "breakthrough_progress": <thay đổi>,
            "realm_level": <có thể tăng>
        }},
        "resources": {{
            "spirit_stones": <thay đổi>,
            "pills": {{"<tên đan>": <số lượng>}},
            "materials": {{"<tên vật liệu>": <số lượng>}}
        }},
        "attributes": {{
            <cập nhật nếu có>
        }}
    }}
}}
"""
        
        return prompt
    
    def process_character_creation(
        self,
        character_data: Dict[str, Any],
        memory_context: Optional[str] = None,
        working_memory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process character creation (age 0) - different from year progress
        """
        gender = character_data.get("gender", "Nam")
        talent = character_data.get("talent", "Bình thường")
        race = character_data.get("race", "Người")
        background = character_data.get("background", "Nông dân")
        location_name = character_data.get("location_name", "làng quê")
        
        prompt = f"""
=== CHARACTER CREATION ===
Bạn đang tạo câu chuyện khởi đầu cho một nhân vật tu tiên MỚI SINH (0 tuổi).

Thông tin nhân vật:
- Giới tính: {gender}
- Thiên phú: {talent}
- Chủng tộc: {race}
- Bối cảnh: {background}
- Nơi sinh: {location_name}

QUAN TRỌNG:
- Nhân vật MỚI SINH (0 tuổi), chưa thể tu luyện
- Tạo câu chuyện về thời thơ ấu, gia đình, môi trường sống
- Mô tả thiên phú {talent} thể hiện như thế nào từ nhỏ
- Tạo tên nhân vật phù hợp với bối cảnh {background}
- Đưa ra 4-6 lựa chọn cho năm đầu tiên (1 tuổi) - những hoạt động phù hợp với trẻ nhỏ

VÍ DỤ NARRATIVE TỐT:
"Bạn được sinh ra trong một gia đình {background} tại {location_name}. Ngay từ khi còn nhỏ, với thiên phú {talent}, bạn đã thể hiện những dấu hiệu đặc biệt - có thể cảm nhận được dòng linh khí nhẹ nhàng xung quanh, dù chưa hiểu đó là gì. Gia đình bạn nhận thấy tiềm năng và bắt đầu chuẩn bị cho bạn con đường tu tiên từ sớm."

Format JSON:
{{
    "narrative": "Câu chuyện về thời thơ ấu, KHÔNG có tu luyện vì mới sinh...",
    "character_name": "Tên nhân vật phù hợp",
    "choices": ["Lựa chọn 1", "Lựa chọn 2", "Lựa chọn 3", "Lựa chọn 4"],
    "action_intent": "CHARACTER_CREATION",
    "state_updates": {{
        "age": 0
    }}
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            print(f"📝 Character Creation AI Response (first 200 chars): {text[:200]}...")
            
            # Parse JSON
            try:
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                
                data = json.loads(text)
                
                # Validate
                from schemas import CharacterCreationResponse
                try:
                    response_obj = CharacterCreationResponse(**data)
                    result = response_obj.dict()
                    
                    # Ensure character_name exists
                    if "character_name" not in result or not result["character_name"]:
                        result["character_name"] = "Người Tu Tiên"
                    
                    return result
                except Exception as e:
                    print(f"⚠️ Character creation schema error: {e}")
                    # Use partial data if available
                    return {
                        "narrative": data.get("narrative", ""),
                        "character_name": data.get("character_name", "Người Tu Tiên"),
                        "choices": data.get("choices", ["Tiếp tục lớn lên", "Quan sát thế giới xung quanh", "Chơi với các trẻ khác", "Nghe kể chuyện tu tiên"]),
                        "action_intent": "CHARACTER_CREATION",
                        "state_updates": {"age": 0}
                    }
            except json.JSONDecodeError as e:
                print(f"⚠️ Character creation JSON parse error: {e}")
                print(f"Raw text (first 1000 chars): {text[:1000]}")
                print(f"Raw text length: {len(text)}")
                
                # Try to extract and fix incomplete JSON
                import re
                # Try to find JSON object and fix if incomplete
                if "```json" in text or "```" in text:
                    # Extract from markdown
                    if "```json" in text:
                        extracted = text.split("```json")[1].split("```")[0].strip()
                    else:
                        extracted = text.split("```")[1].split("```")[0].strip()
                else:
                    extracted = text.strip()
                
                # Try to fix incomplete JSON by finding the last complete object
                try:
                    # Find the last complete closing brace
                    last_brace = extracted.rfind('}')
                    if last_brace > 0:
                        # Try to parse up to the last complete brace
                        candidate = extracted[:last_brace + 1]
                        # Try to find the opening brace
                        first_brace = candidate.find('{')
                        if first_brace >= 0:
                            candidate = candidate[first_brace:]
                            data = json.loads(candidate)
                            print(f"✅ Fixed incomplete JSON by truncating to last complete object")
                        else:
                            raise
                    else:
                        raise
                except:
                    # If all else fails, use fallback
                    print(f"❌ Could not fix JSON, using fallback")
                    raise
        
        except Exception as e:
            print(f"❌ Character creation AI error: {e}")
            import traceback
            traceback.print_exc()
            # Create appropriate fallback for character creation
            return {
                "narrative": f"Bạn được sinh ra trong một gia đình {background} tại {location_name}. Với thiên phú {talent}, bạn đã thể hiện những dấu hiệu đặc biệt ngay từ khi còn nhỏ, dù chưa hiểu về thế giới tu tiên.",
                "character_name": "Người Tu Tiên",
                "choices": [
                    "Lớn lên và quan sát thế giới",
                    "Nghe kể chuyện về tu tiên",
                    "Chơi với các trẻ khác trong làng",
                    "Quan sát người lớn tu luyện"
                ],
                "action_intent": "CHARACTER_CREATION",
                "state_updates": {"age": 0}
            }
    
    def _parse_response(self, text: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response với fallback"""
        # Try to extract JSON
        try:
            original_text = text
            # Remove markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # Try to find JSON object in text - improved parsing
            import re
            # First try to extract JSON from markdown code blocks
            if "```json" in text or "```" in text:
                # Already extracted above, try parsing directly
                try:
                    data = json.loads(text)
                except:
                    # If that fails, try to find the largest JSON object
                    # Match balanced braces
                    brace_count = 0
                    start_idx = -1
                    best_match = None
                    best_length = 0
                    
                    for i, char in enumerate(text):
                        if char == '{':
                            if brace_count == 0:
                                start_idx = i
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0 and start_idx != -1:
                                candidate = text[start_idx:i+1]
                                if len(candidate) > best_length:
                                    try:
                                        json.loads(candidate)  # Test if valid
                                        best_match = candidate
                                        best_length = len(candidate)
                                    except:
                                        pass
                    
                    if best_match:
                        data = json.loads(best_match)
                    else:
                        raise json.JSONDecodeError("No valid JSON found", text, 0)
            else:
                # No markdown, try parsing whole text
                data = json.loads(text)
            
            # Validate với Pydantic schema
            try:
                response = CultivationLLMResponse(**data)
                result = response.dict()
                
                # Ensure state_updates exists and has minimum required fields
                if "state_updates" not in result or not result["state_updates"]:
                    result["state_updates"] = {}
                
                # Ensure age is updated
                current_age = character_data.get("age", 0)
                if "age" not in result["state_updates"]:
                    result["state_updates"]["age"] = current_age + 1
                
                # Ensure cultivation updates exist (at minimum, spiritual_power should increase)
                if "cultivation" not in result["state_updates"]:
                    current_cultivation = character_data.get("cultivation", {})
                    current_sp = current_cultivation.get("spiritual_power", 0)
                    current_max_sp = current_cultivation.get("max_spiritual_power", 100)
                    result["state_updates"]["cultivation"] = {
                        "spiritual_power": min(current_sp + 10, current_max_sp),  # Small progress
                        "breakthrough_progress": current_cultivation.get("breakthrough_progress", 0.0) + 1.0
                    }
                
                return result
            except Exception as e:
                print(f"⚠️ Schema validation error: {e}")
                import traceback
                traceback.print_exc()
                print(f"⚠️ Partial data available: {data}")
                print(f"⚠️ Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Try to use partial data if it has narrative
                if data and isinstance(data, dict) and data.get("narrative") and len(data.get("narrative", "")) > 50:
                    print(f"✅ Using partial data narrative (bypassing schema validation): {data.get('narrative')[:200]}...")
                    # Ensure state_updates exists
                    state_updates = data.get("state_updates", {})
                    if not state_updates:
                        current_age = character_data.get("age", 0)
                        state_updates = {"age": current_age + 1}
                    
                    return {
                        "narrative": data.get("narrative", ""),
                        "choices": data.get("choices", []),
                        "action_intent": data.get("action_intent", "YEAR_PROGRESS"),
                        "state_updates": state_updates
                    }
                
                print(f"❌ Cannot use partial data, using fallback")
                return self._create_fallback_response(character_data, data)
        
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            print(f"⚠️ Raw text that failed to parse (first 1000 chars): {text[:1000]}...")
            print(f"⚠️ Raw text length: {len(text)}")
            
            # Try to extract JSON manually if it's embedded in text
            import re
            json_match = re.search(r'\{[^{}]*"narrative"[^{}]*\}', text, re.DOTALL)
            if json_match:
                try:
                    extracted_json = json_match.group(0)
                    print(f"✅ Found JSON-like structure, trying to parse: {extracted_json[:200]}...")
                    data = json.loads(extracted_json)
                    if data.get("narrative") and len(data.get("narrative", "")) > 50:
                        print(f"✅ Successfully extracted narrative from text")
                        return {
                            "narrative": data.get("narrative", ""),
                            "choices": data.get("choices", []),
                            "action_intent": data.get("action_intent", "YEAR_PROGRESS"),
                            "state_updates": data.get("state_updates", {"age": character_data.get("age", 0) + 1})
                        }
                except:
                    pass
            
            import traceback
            traceback.print_exc()
            return self._create_fallback_response(character_data)
    
    def _create_fallback_response(
        self,
        character_data: Dict[str, Any],
        partial_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Tạo fallback response khi AI fail"""
        age = character_data.get("age", 0)
        name = character_data.get("name", "Người Tu Tiên")
        talent = character_data.get("talent", "Bình thường")
        location_name = character_data.get("location_name", "làng quê")
        
        if partial_data:
            # Use partial data if available
            narrative = partial_data.get("narrative", "")
            choices = partial_data.get("choices", [])
            
            # If narrative is empty or generic, create a better one
            if not narrative or "trôi qua một cách bình thường" in narrative or "trôi qua" in narrative.lower():
                if age == 0:
                    narrative = f"{name} được sinh ra trong một gia đình tại {location_name}. Với thiên phú {talent}, bạn đã thể hiện những dấu hiệu đặc biệt ngay từ khi còn nhỏ, dù chưa hiểu về thế giới tu tiên."
                else:
                    narrative = f"{name} tiếp tục hành trình tu tiên. Với thiên phú {talent}, bạn đã có những tiến bộ nhỏ trong việc cảm nhận linh khí xung quanh tại {location_name}. Mỗi ngày trôi qua đều mang lại những bài học mới về thế giới tu tiên."
        else:
            # Create a more interesting fallback narrative
            if age == 0:
                narrative = f"{name} được sinh ra trong một gia đình tại {location_name}. Với thiên phú {talent}, bạn đã thể hiện những dấu hiệu đặc biệt ngay từ khi còn nhỏ - có thể cảm nhận được dòng linh khí nhẹ nhàng xung quanh, dù chưa hiểu đó là gì. Gia đình bạn nhận thấy tiềm năng và bắt đầu chuẩn bị cho bạn con đường tu tiên từ sớm."
            else:
                narrative = f"{name} tiếp tục tu luyện tại {location_name}. Với thiên phú {talent}, bạn đã có những tiến bộ trong việc cảm nhận và điều khiển linh khí. Mỗi ngày trôi qua đều mang lại những hiểu biết mới về thế giới tu tiên."
            
            choices = [
                "Tiếp tục tu luyện",
                "Đi khám phá khu vực xung quanh",
                "Tìm kiếm tông môn để gia nhập",
                "Nghỉ ngơi và suy ngẫm"
            ]
        
        # Ensure 4-6 choices
        while len(choices) < 4:
            choices.append(f"Lựa chọn {len(choices) + 1}")
        choices = choices[:6]
        
        # Get current cultivation state
        cultivation = character_data.get("cultivation", {})
        current_sp = cultivation.get("spiritual_power", 0)
        current_max_sp = cultivation.get("max_spiritual_power", 100)
        current_bp = cultivation.get("breakthrough_progress", 0.0)
        
        return {
            "narrative": narrative,
            "choices": choices,
            "action_intent": "YEAR_PROGRESS",
            "state_updates": {
                "age": age + 1,
                "cultivation": {
                    "spiritual_power": min(current_sp + 10, current_max_sp),  # Small progress
                    "breakthrough_progress": min(current_bp + 1.0, 100.0)
                },
                "resources": {
                    "spirit_stones": character_data.get("resources", {}).get("spirit_stones", 0) + 5  # Small gain
                }
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
