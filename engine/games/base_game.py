"""
Base Game Class
All game modes inherit from this class
Core principle: User makes decisions → AI (Gemini) responds
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from engine.core import get_entity_manager, get_db
from engine.ai import get_gemini_agent, GameContext, ContextBuilder
from engine.memory import get_memory_manager


class BaseGame(ABC):
    """
    Base class for all game modes.
    
    Core Flow:
    1. User input → AI processes → Response
    2. Each game mode has its own setup, prompts, and state management
    """
    
    def __init__(self, game_mode: str):
        self.game_mode = game_mode
        self.save_id: Optional[str] = None
        self.db_path: Optional[str] = None
        self.em = None
        self.context_builder: Optional[ContextBuilder] = None
        self.ai = get_gemini_agent()
        self.memory_manager = get_memory_manager()
        self.player_id: Optional[int] = None
        self.turn_count = 0
        
    def init_engine(self, db_path: str, save_id: str):
        """Initialize engine with specific DB"""
        self.db_path = db_path
        self.save_id = save_id
        
        # Reset global instances to ensure we use the new DB path
        import engine.core.database
        import engine.core.entity
        engine.core.database._db = None
        engine.core.entity._em = None
        
        self.em = get_entity_manager(get_db(db_path))
        self.context_builder = ContextBuilder(self.em)
    
    @abstractmethod
    def setup_world(self):
        """Create initial game world - must be implemented by each game mode"""
        pass
    
    @abstractmethod
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state - must be implemented by each game mode"""
        pass
    
    def process_turn(self, user_input: str) -> Dict[str, Any]:
        """
        Process one game turn
        Core flow: User input → AI → Response
        """
        self.turn_count += 1
        
        # 1. Build Context
        context = self.context_builder.build(self.player_id)
        
        # 2. AI Processing (Parse + Validate + Narrate)
        response = self.ai.process_turn(user_input, context, save_id=self.save_id)
        
        # 3. Apply State Updates
        updates = response.get('state_updates', {})
        self.apply_updates(updates)
        
        # 4. Save to memory
        if 'narrative' in response:
            self.memory_manager.remember_action(
                user_input=user_input,
                narrative=response['narrative'],
                save_id=self.save_id,
                entity_id=self.player_id,
                location_id=context.current_room_id,
                importance=0.6
            )
        
        return response
    
    def apply_updates(self, updates: dict):
        """Apply state updates from AI - can be overridden by game modes"""
        if not updates:
            return
        
        # Handle Movement (common to all games)
        if 'new_location_id' in updates:
            from engine.core import LocationComponent
            loc = self.em.get(self.player_id, LocationComponent)
            if loc:
                loc.room_id = updates['new_location_id']
                self.em.add(self.player_id, loc)
    
    def start_new_game(self, **kwargs) -> str:
        """Start a fresh game session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.save_id = f"{self.game_mode}_{timestamp}"
        db_path = f"data/saves/{self.save_id}.db"
        
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.init_engine(db_path, self.save_id)
        self.setup_world(**kwargs)
        
        return self.save_id
    
    def load_game(self, save_id: str):
        """Load an existing game session"""
        db_path = f"data/saves/{save_id}.db"
        
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Save file not found: {save_id}")
        
        self.save_id = save_id
        self.init_engine(db_path, save_id)
        
        # Find player
        self.player_id = self.em.find_player()
        if not self.player_id:
            raise ValueError("Player not found in save file")

