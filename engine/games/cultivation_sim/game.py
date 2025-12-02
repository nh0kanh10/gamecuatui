"""
Cultivation Simulator Game Mode
Tu Tiên Life Simulation - From birth to cultivation master
Features: Character creation, age progression, cultivation system
"""

from typing import Dict, Any, List, Optional
from engine.games.base_game import BaseGame
from engine.core import (
    LocationComponent, StatsComponent, IdentityComponent
)


class CultivationSimGame(BaseGame):
    """
    Cultivation Simulator - Tu Tiên Life Simulation
    
    Game Flow:
    1. Character Creation: Giới tính, Thiên phú, Chủng tộc, Bối cảnh
    2. AI generates character background and family
    3. Age 0: AI presents 4-6 choices, player selects
    4. AI continues story to next year
    5. Repeat until cultivation master or death
    """
    
    def __init__(self):
        super().__init__(game_mode="cultivation_sim")
        self.character_age = 0
        self.character_gender: Optional[str] = None
        self.character_talent: Optional[str] = None
        self.character_race: Optional[str] = None
        self.character_background: Optional[str] = None
        self.character_story: Optional[str] = None
        self.current_choices: List[str] = []
    
    def character_creation(self, gender: str, talent: str, race: str, background: str):
        """
        Character creation step
        AI will generate character background and family story
        """
        self.character_gender = gender
        self.character_talent = talent
        self.character_race = race
        self.character_background = background
        
        # AI will generate character story in setup_world
        return {
            "gender": gender,
            "talent": talent,
            "race": race,
            "background": background
        }
    
    def setup_world(self, **kwargs):
        """
        Create initial game world with character
        AI generates character background and family story
        """
        # Get character creation data
        char_data = kwargs.get('character', {})
        self.character_gender = char_data.get('gender', 'Nam')
        self.character_talent = char_data.get('talent', 'Thiên Linh Căn')
        self.character_race = char_data.get('race', 'Nhân Tộc')
        self.character_background = char_data.get('background', 'Gia Đình Tu Tiên')
        
        # Create player entity
        player_name = kwargs.get('player_name', 'Người Tu Tiên')
        self.player_id = self.em.create_player(player_name)
        
        # Set initial stats for cultivation
        stats = self.em.get(self.player_id, StatsComponent)
        if stats:
            stats.hp = 10  # Health
            stats.max_hp = 10
            # Add cultivation-specific stats
            stats.mana = 0  # Spiritual power
            stats.max_mana = 100
        self.em.add(self.player_id, stats)
        
        # Set location (birthplace)
        loc = self.em.get(self.player_id, LocationComponent)
        if loc:
            loc.room_id = "birthplace"
        else:
            loc = LocationComponent(room_id="birthplace")
        self.em.add(self.player_id, loc)
        
        # Set identity
        identity = self.em.get(self.player_id, IdentityComponent)
        if identity:
            identity.name = player_name
            identity.age = 0
        else:
            identity = IdentityComponent(name=player_name, age=0)
        self.em.add(self.player_id, identity)
        
        # Age starts at 0
        self.character_age = 0
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state"""
        if not self.player_id:
            return {}
        
        context = self.context_builder.build(self.player_id)
        
        return {
            "player_name": context.player_name,
            "age": self.character_age,
            "gender": self.character_gender,
            "talent": self.character_talent,
            "race": self.character_race,
            "background": self.character_background,
            "character_story": self.character_story,
            "current_choices": self.current_choices,
            "player_hp": context.player_hp,
            "player_max_hp": context.player_max_hp,
            "current_location": context.current_room_id,
            "room_description": context.room_description,
        }
    
    def process_year_turn(self, choice_index: int) -> Dict[str, Any]:
        """
        Process a year turn with player's choice
        AI continues story to next year
        """
        if not self.current_choices or choice_index < 0 or choice_index >= len(self.current_choices):
            from engine.ai.cultivation_schemas import CultivationLLMResponse
            fallback = CultivationLLMResponse._create_fallback_response()
            return fallback.dict()
        
        selected_choice = self.current_choices[choice_index]
        
        # Sanitize choice
        selected_choice = self._sanitize_input(selected_choice)
        
        # Build prompt for AI
        user_input = f"Lựa chọn {choice_index + 1}: {selected_choice}"
        
        # Process turn
        response = self.process_turn(user_input)
        
        # Age progresses
        self.character_age += 1
        
        # Update age in identity
        identity = self.em.get(self.player_id, IdentityComponent)
        if identity:
            identity.age = self.character_age
            self.em.add(self.player_id, identity)
        
        # Store new choices if provided
        if 'choices' in response and response['choices']:
            self.current_choices = response['choices'][:6]
        
        return response
    
    def _sanitize_input(self, user_input: str) -> str:
        """Sanitize user input to prevent prompt injection"""
        if not user_input:
            return ""
        
        # Remove prompt injection patterns
        dangerous_patterns = [
            "```", "---", "system:", "assistant:", "user:",
            "ignore previous", "forget", "new instructions",
            "system prompt", "role:", "you are now"
        ]
        
        text = user_input.lower()
        for pattern in dangerous_patterns:
            if pattern in text:
                # Remove the dangerous part
                user_input = user_input.replace(pattern, "", flags=1)
        
        # Limit length
        if len(user_input) > 500:
            user_input = user_input[:500]
        
        # Remove zero-width characters
        user_input = ''.join(char for char in user_input if ord(char) >= 32)
        
        return user_input.strip()
    
    def apply_updates(self, updates: dict):
        """Apply state updates from AI"""
        super().apply_updates(updates)  # Call base for movement
        
        if not updates:
            return
        
        # Handle age progression
        if 'age' in updates:
            self.character_age = updates['age']
        
        # Handle cultivation-specific updates
        if 'cultivation_realm' in updates:
            # Update cultivation realm
            pass
        
        if 'spiritual_power' in updates:
            stats = self.em.get(self.player_id, StatsComponent)
            if stats:
                stats.mana = updates.get('spiritual_power', stats.mana)
                self.em.add(self.player_id, stats)

