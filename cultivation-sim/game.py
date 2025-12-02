"""
Cultivation Simulator - Standalone Game
Tu Tiên Life Simulation
Enhanced với 3-tier Memory, ECS Systems, World Database
"""

import sqlite3
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json

from database import get_db, init_database
from agent import CultivationAgent
from memory_3tier import Memory3Tier
from schemas import CharacterData, GameState, CultivationComponent, ResourceComponent
from attributes import AttributesComponent
from world_database import WorldDatabase
from ecs_systems import CultivationSystem, RelationshipSystem, AIPlannerSystem, NeedsSystem
from artifact_system import ArtifactSystem
from item_system import ItemSystem


class CultivationSimulator:
    """
    Standalone Cultivation Simulator
    Enhanced với:
    - 3-tier Memory Architecture
    - ECS Systems (Cultivation, Relationship, AI Planner, Needs)
    - World Database integration
    - Attributes System
    """
    
    def __init__(self, save_id: str):
        self.save_id = save_id
        self.db_path = f"data/saves/{save_id}.db"
        
        # Initialize database
        init_database(self.db_path)
        self.db = get_db(self.db_path)
        
        # Initialize systems
        self.agent = CultivationAgent()
        self.memory = Memory3Tier(self.db_path, save_id)
        self.world_db = WorldDatabase("data")
        self.artifact_system = ArtifactSystem(self.world_db)
        self.item_system = ItemSystem(self.world_db)
        
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
        self.current_location_id: Optional[str] = None
        self.current_sect_id: Optional[str] = None
        
        # Components
        self.cultivation: CultivationComponent = CultivationComponent()
        self.resources: ResourceComponent = ResourceComponent()
        self.attributes: Optional[AttributesComponent] = None
        
        # ECS Systems (will be initialized after game state loaded)
        self.cultivation_system: Optional[CultivationSystem] = None
        self.relationship_system: Optional[RelationshipSystem] = None
        self.ai_planner: Optional[AIPlannerSystem] = None
        self.needs_system: Optional[NeedsSystem] = None
        
        # Game state dict (for ECS Systems)
        self.game_state: Dict[str, Any] = {}
        
        # Load from database if exists
        self._load_state()
        
        # Initialize ECS Systems
        self._init_ecs_systems()
    
    def _init_ecs_systems(self):
        """Initialize ECS Systems"""
        self.game_state = {
            "cultivation": self.cultivation.dict() if self.cultivation else {},
            "attributes": self.attributes.dict() if self.attributes else {},
            "resources": self.resources.dict() if self.resources else {},
            "location": self._get_location_data(),
            "needs": {"hunger": 100.0, "energy": 100.0, "social": 50.0},
            "nearby_entities": []
        }
        
        self.cultivation_system = CultivationSystem(self.game_state)
        self.relationship_system = RelationshipSystem(self.game_state)
        self.ai_planner = AIPlannerSystem(self.game_state, self.agent, self.memory)
        self.needs_system = NeedsSystem(self.game_state)
    
    def _get_location_data(self) -> Dict[str, Any]:
        """Get current location data from World Database"""
        # Get location from character state or default
        location_id = getattr(self, 'current_location_id', None) or "loc_village_01"
        
        location = self.world_db.get_location(location_id)
        if location:
            return {
                "location_id": location_id,
                "name": location.get("name", "Unknown"),
                "type": location.get("type", "Unknown"),
                "region": location.get("region", "Unknown"),
                "qi_density": location.get("qi_density", 1.0),
                "danger_level": location.get("danger_level", "Safe"),
                "services": location.get("services", []),
                "connected_to": location.get("connected_to", [])
            }
        
        # Default fallback
        return {
            "location_id": location_id,
            "name": "Unknown Location",
            "type": "Unknown",
            "region": "Unknown",
            "qi_density": 1.0,
            "danger_level": "Safe",
            "services": [],
            "connected_to": []
        }
    
    def _load_state(self):
        """Load game state from database"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT age, gender, talent, race, background, story, name, choices_json, 
                   cultivation_json, resources_json, attributes_json
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
            if row[10]:
                attributes_data = json.loads(row[10])
                self.attributes = AttributesComponent(**attributes_data)
    
    def _save_state(self):
        """Save game state to database"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO game_state 
            (save_id, age, gender, talent, race, background, story, name, choices_json, 
             cultivation_json, resources_json, attributes_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            json.dumps(self.cultivation.dict(), ensure_ascii=False) if self.cultivation else None,
            json.dumps(self.resources.dict(), ensure_ascii=False) if self.resources else None,
            json.dumps(self.attributes.dict(), ensure_ascii=False) if self.attributes else None,
            datetime.now().isoformat()
        ))
        self.db.commit()
    
    def character_creation(
        self,
        gender: str,
        talent: str,
        race: str,
        background: str
    ) -> Dict[str, Any]:
        """
        Character creation với World Database integration
        """
        self.character_gender = gender
        self.character_talent = talent
        self.character_race = race
        self.character_background = background
        
        # Get race data from World Database
        race_data = self.world_db.get_race(race)
        if race_data:
            base_stats = race_data.get("base_stats", {})
            self.attributes = AttributesComponent(**base_stats)
        else:
            self.attributes = AttributesComponent()  # Default
        
        # Get clan data from World Database
        clan_data = self.world_db.get_clan(background)
        if clan_data:
            starting_perks = clan_data.get("starting_perks", {})
            # Apply starting perks
            if "spirit_stones" in starting_perks:
                self.resources.spirit_stones = starting_perks["spirit_stones"]
            if "items" in starting_perks:
                for item_name, quantity in starting_perks["items"].items():
                    self.resources.add_material(item_name, quantity)
        
        # Set default location from World Database
        # Try to find a safe starting location
        all_locations = self.world_db.get_all_locations()
        safe_locations = [loc for loc in all_locations if loc.get("danger_level") == "Safe"]
        if safe_locations:
            self.current_location_id = safe_locations[0].get("id", "loc_village_01")
        else:
            self.current_location_id = "loc_village_01"
        
        # Call AI for character story
        character_data = {
            "age": 0,
            "gender": gender,
            "talent": talent,
            "race": race,
            "background": background,
            "attributes": self.attributes.dict() if self.attributes else {},
            "cultivation": self.cultivation.dict(),
            "resources": self.resources.dict(),
            "location_id": self.current_location_id
        }
        
        # Get memory context
        memory_context = self.memory.get_full_context()
        working_memory = self.memory.get_working_memory_context()
        
        response = self.agent.process_turn(
            character_data=character_data,
            memory_context=memory_context,
            working_memory=working_memory
        )
        
        self.character_story = response.get("narrative", "")
        self.character_name = response.get("character_name", "Người Chơi")
        self.current_choices = response.get("choices", [])
        
        # Save to memory
        self.memory.add_short_term(
            content=f"Character created: {self.character_name}, {gender}, {talent}, {race}, {background}",
            speaker="system"
        )
        self.memory.add_long_term(
            content=f"Character creation: {self.character_name} - {self.character_story}",
            memory_type="episodic",
            importance=0.9
        )
        
        self._save_state()
        
        return {
            "narrative": self.character_story,
            "character_name": self.character_name,
            "choices": self.current_choices
        }
    
    def process_year_turn(self, choice_index: int) -> Dict[str, Any]:
        """
        Xử lý một năm trong game
        
        Enhanced với:
        - ECS Systems tick
        - Memory updates
        - World Database context
        """
        
        if choice_index < 0 or choice_index >= len(self.current_choices):
            raise ValueError(f"Invalid choice index: {choice_index}")
        
        selected_choice = self.current_choices[choice_index]
        
        # Add to memory
        self.memory.add_short_term(
            content=selected_choice,
            speaker="player"
        )
        
        # Update working memory
        self.memory.set_working_memory(
            task_type="year_progress",
            task_data={"choice": selected_choice, "age": self.character_age},
            priority=8
        )
        
        # ECS Systems tick
        self._tick_ecs_systems()
        
        # Progress age
        self.character_age += 1
        
        # Build character data với World Database context
        location_data = self._get_location_data()
        sect_context = ""
        if self.current_sect_id:
            sect = self.world_db.get_sect(self.current_sect_id)
            if sect:
                sect_context = f"Tông môn: {sect['name']} ({sect['type']})"
        
        character_data = {
            "age": self.character_age,
            "gender": self.character_gender,
            "talent": self.character_talent,
            "race": self.character_race,
            "background": self.character_background,
            "story": self.character_story,
            "name": self.character_name,
            "attributes": self.attributes.dict() if self.attributes else {},
            "cultivation": self.cultivation.dict(),
            "resources": self.resources.dict(),
            "choices": self.current_choices,
            "location_id": location_data.get("location_id"),
            "location_name": location_data.get("name"),
            "sect_id": self.current_sect_id,
            "sect_context": sect_context
        }
        
        # Get memory context
        memory_context = self.memory.get_full_context(query=selected_choice)
        working_memory = self.memory.get_working_memory_context()
        
        # Call AI
        response = self.agent.process_turn(
            character_data=character_data,
            current_choice=choice_index,
            memory_context=memory_context,
            working_memory=working_memory
        )
        
        # Add AI response to memory
        self.memory.add_short_term(
            content=response.get("narrative", ""),
            speaker="ai"
        )
        
        # Update game state
        self._apply_state_updates(response.get("state_updates", {}))
        
        # Update choices
        self.current_choices = response.get("choices", [])
        
        # Complete working memory
        self.memory.complete_working_memory("year_progress")
        
        # Save state
        self._save_state()
        
        return {
            "narrative": response.get("narrative", ""),
            "choices": self.current_choices,
            "age": self.character_age
        }
    
    def _tick_ecs_systems(self):
        """Tick all ECS Systems"""
        # Update game state dict với latest data
        self.game_state["cultivation"] = self.cultivation.dict()
        self.game_state["attributes"] = self.attributes.dict() if self.attributes else {}
        self.game_state["resources"] = self.resources.dict()
        self.game_state["location"] = self._get_location_data()  # Update location từ World Database
        
        # Tick systems
        if self.cultivation_system:
            self.cultivation_system.tick(delta_time=1.0)
            # Update cultivation component từ game_state
            self.cultivation = CultivationComponent(**self.game_state["cultivation"])
        
        if self.needs_system:
            self.needs_system.tick(delta_time=1.0)
    
    def _apply_state_updates(self, updates: Dict[str, Any]):
        """Apply state updates from AI response"""
        # Update age
        if "age" in updates:
            self.character_age = updates["age"]
        
        # Update cultivation
        if "cultivation" in updates:
            cultivation_updates = updates["cultivation"]
            for key, value in cultivation_updates.items():
                if hasattr(self.cultivation, key):
                    setattr(self.cultivation, key, value)
        
        # Update resources
        if "resources" in updates:
            resource_updates = updates["resources"]
            if "spirit_stones" in resource_updates:
                self.resources.spirit_stones = resource_updates["spirit_stones"]
            if "pills" in resource_updates:
                for pill_name, quantity in resource_updates["pills"].items():
                    self.resources.add_pill(pill_name, quantity)
        
        # Update attributes
        if "attributes" in updates:
            attribute_updates = updates["attributes"]
            if self.attributes:
                for key, value in attribute_updates.items():
                    if hasattr(self.attributes, key):
                        setattr(self.attributes, key, value)
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state"""
        return {
            "age": self.character_age,
            "gender": self.character_gender,
            "talent": self.character_talent,
            "race": self.character_race,
            "background": self.character_background,
            "story": self.character_story,
            "name": self.character_name,
            "choices": self.current_choices,
            "cultivation": self.cultivation.dict() if self.cultivation else {},
            "resources": self.resources.dict() if self.resources else {},
            "attributes": self.attributes.dict() if self.attributes else {},
            "needs": self.game_state.get("needs", {}),
            "relationships": self.relationship_system.get_all_relationships("player") if self.relationship_system else {}
        }
