"""
Cultivation Simulator - Standalone Game
Tu Tiên Life Simulation
"""

import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json

from database import get_db, init_database
from agent import CultivationAgent
from memory import CultivationMemory
from schemas import CharacterData, GameState


class CultivationSimulator:
    """
    Standalone Cultivation Simulator
    Không phụ thuộc vào multi-game architecture
    """
    
    def __init__(self, save_id: str):
        self.save_id = save_id
        self.db_path = f"data/saves/{save_id}.db"
        
        # Initialize database
        init_database(self.db_path)
        self.db = get_db(self.db_path)
        
        # Initialize systems
        self.agent = CultivationAgent()
        self.memory = CultivationMemory(self.db_path, save_id)
        
        # Game state
        self.character_age = 0
        self.character_gender: Optional[str] = None
        self.character_talent: Optional[str] = None
        self.character_race: Optional[str] = None
        self.character_background: Optional[str] = None
        self.character_story: Optional[str] = None
        self.character_name: Optional[str] = None
        self.current_choices: List[str] = []
        self.turn_count = 0
        
        # Cultivation components
        self.cultivation: CultivationComponent = CultivationComponent()
        self.resources: ResourceComponent = ResourceComponent()
        
        # Load from database if exists
        self._load_state()
    
    def _load_state(self):
        """Load game state from database"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT age, gender, talent, race, background, story, name, choices_json, cultivation_json, resources_json
            FROM game_state
            WHERE save_id = ?
        """, (self.save_id,))
        
        row = cursor.fetchone()
        if row:
            self.character_age = row[0] or 0
            self.character_gender = row[1]
            self.character_talent = row[2]
            self.character_race = row[3]
            self.character_background = row[4]
            self.character_story = row[5]
            self.character_name = row[6]
            if row[7]:
                self.current_choices = json.loads(row[7])
            if row[8]:
                cultivation_data = json.loads(row[8])
                self.cultivation = CultivationComponent(**cultivation_data)
            if row[9]:
                resources_data = json.loads(row[9])
                self.resources = ResourceComponent(**resources_data)
    
    def _save_state(self):
        """Save game state to database"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO game_state 
            (save_id, age, gender, talent, race, background, story, name, choices_json, cultivation_json, resources_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.save_id,
            self.character_age,
            self.character_gender,
            self.character_talent,
            self.character_race,
            self.character_background,
            self.character_story,
            self.character_name,
            json.dumps(self.current_choices, ensure_ascii=False),
            json.dumps(self.cultivation.dict(), ensure_ascii=False),
            json.dumps(self.resources.dict(), ensure_ascii=False),
            datetime.now().isoformat()
        ))
        self.db.commit()
    
    def create_character(self, character_data: CharacterData) -> Dict[str, Any]:
        """
        Create character and generate background
        Returns: {narrative, choices, character_name}
        """
        # Store character data
        self.character_gender = character_data.gender
        self.character_talent = character_data.talent
        self.character_race = character_data.race
        self.character_background = character_data.background
        self.character_age = 0
        
        # Generate character background with AI
        response = self.agent.create_character(character_data)
        
        # Store generated story
        self.character_story = response['narrative']
        self.character_name = response.get('character_name', 'Người Tu Tiên')
        self.current_choices = response['choices']
        
        # Save to database
        self._save_state()
        
        return response
    
    def process_year_turn(self, choice_index: int) -> Dict[str, Any]:
        """
        Process a year turn with player's choice
        Returns: {narrative, choices, state_updates}
        """
        if not self.current_choices or choice_index < 0 or choice_index >= len(self.current_choices):
            from schemas import create_fallback_response
            return create_fallback_response()
        
        selected_choice = self.current_choices[choice_index]
        
        # Get character data
        char_data = {
            'age': self.character_age,
            'gender': self.character_gender,
            'talent': self.character_talent,
            'race': self.character_race,
            'background': self.character_background
        }
        
        # Get memory context
        memory_context = self.memory.get_context(
            query=selected_choice,
            n_results=5
        )
        
        # Process with AI
        response = self.agent.process_turn(
            user_input=f"Lựa chọn {choice_index + 1}: {selected_choice}",
            character_data=char_data,
            memory_context=memory_context,
            save_id=self.save_id
        )
        
        # Age progresses
        self.character_age += 1
        
        # Store new choices
        if 'choices' in response:
            self.current_choices = response['choices']
        
        # Save narrative to memory
        if 'narrative' in response:
            self.memory.add(
                content=response['narrative'],
                memory_type='episodic',
                importance=0.7
            )
        
        # Save state
        self._save_state()
        
        return response
    
    def get_game_state(self) -> GameState:
        """Get current game state"""
        return GameState(
            save_id=self.save_id,
            character_name=self.character_name or "Người Tu Tiên",
            age=self.character_age,
            gender=self.character_gender,
            talent=self.character_talent,
            race=self.character_race,
            background=self.character_background,
            character_story=self.character_story,
            current_choices=self.current_choices,
            turn_count=self.turn_count
        )

