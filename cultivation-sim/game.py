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
import logging
import traceback

# Setup logging for game module
logger = logging.getLogger(__name__)

from database import get_db, init_database
from agent import CultivationAgent
from memory_3tier import Memory3Tier
from schemas import CharacterData, GameState
from components import CultivationComponent, ResourceComponent, SpiritBeastComponent, SpiritHerbComponent
from attributes import AttributesComponent
from world_database import WorldDatabase

# RAM Optimization (optional, for 32GB RAM systems)
try:
    from optimizations import OptimizedCultivationGame
    HAS_OPTIMIZATIONS = True
except ImportError:
    HAS_OPTIMIZATIONS = False
    OptimizedCultivationGame = None
from ecs_systems import CultivationSystem, RelationshipSystem, AIPlannerSystem, NeedsSystem
from artifact_system import ArtifactSystem
from item_system import ItemSystem
from spirit_beast_system import SpiritBeastSystem
from herb_system import HerbSystem
from procedural_spawn import ProceduralSpawner
from skill_system import SkillSystem
from economy_system import EconomySystem
from combat_system import CombatSystem
from breakthrough_enhanced import EnhancedBreakthroughSystem
from naming_system import NamingSystem
from social_graph_system import SocialGraphSystem, PersonalityFacets
from formation_system import FormationSystem, FormationNode, ElementType
from quest_generator import QuestGenerator
from physique_system_v2 import PhysiqueSystemV2 as PhysiqueSystem


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
        
        # Initialize systems (with error handling)
        try:
            logger.info(f"Initializing CultivationAgent for save_id: {save_id}")
            self.agent = CultivationAgent()
            logger.info("CultivationAgent initialized successfully")
        except (ValueError, Exception) as e:
            error_msg = f"Could not initialize CultivationAgent: {str(e)}\n{traceback.format_exc()}"
            logger.warning(error_msg)
            print(f"⚠️  Warning: Could not initialize CultivationAgent: {e}")
            print("   Game will continue but AI features may not work.")
            self.agent = None
        
        self.memory = Memory3Tier(self.db_path, save_id)
        
        # RAM Optimization (if available) - Initialize BEFORE WorldDatabase
        if HAS_OPTIMIZATIONS:
            try:
                # Use shared optimizations instance (singleton pattern)
                if not hasattr(CultivationSimulator, '_shared_optimizations'):
                    logger.info("Initializing RAM optimizations...")
                    CultivationSimulator._shared_optimizations = OptimizedCultivationGame()
                    logger.info("RAM optimizations initialized successfully")
                self.optimizations = CultivationSimulator._shared_optimizations
                logger.info("Using RAM-optimized database cache")
            except Exception as e:
                logger.warning(f"Could not initialize optimizations: {e}. Using standard mode.")
                self.optimizations = None
        else:
            self.optimizations = None
        
        # Initialize WorldDatabase WITH optimizations (for RAM cache)
        self.world_db = WorldDatabase("data", self.optimizations)
        
        self.artifact_system = ArtifactSystem(self.world_db)
        self.item_system = ItemSystem(self.world_db)
        self.beast_system = SpiritBeastSystem(self.world_db)
        self.herb_system = HerbSystem(self.world_db)
        self.spawner = ProceduralSpawner(self.world_db, seed=hash(save_id) % (2**31))
        
        # Advanced Systems
        self.skill_system = SkillSystem("data/skills")
        self.economy_system = EconomySystem("data")
        self.combat_system = CombatSystem()
        self.breakthrough_enhanced = EnhancedBreakthroughSystem()
        self.naming_system = NamingSystem("data")
        self.social_graph = SocialGraphSystem()
        self.formation_system = FormationSystem()
        self.quest_generator = QuestGenerator(self.agent, self.social_graph)
        
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
        
        # Initialize player in social graph
        if hasattr(self, 'social_graph') and self.social_graph:
            from social_graph_system import PersonalityFacets
            self.social_graph.add_entity("player", PersonalityFacets())
    
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
        
        # Check if attributes_json column exists
        cursor.execute("PRAGMA table_info(game_state)")
        columns = [row[1] for row in cursor.fetchall()]
        has_attributes = 'attributes_json' in columns
        
        # Build SELECT query based on available columns
        if has_attributes:
            cursor.execute("""
                SELECT age, gender, talent, race, background, story, name, choices_json, 
                       cultivation_json, resources_json, attributes_json
                FROM game_state
                WHERE save_id = ?
            """, (self.save_id,))
        else:
            cursor.execute("""
                SELECT age, gender, talent, race, background, story, name, choices_json, 
                       cultivation_json, resources_json
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
            if has_attributes and row[10]:
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
    
    def _new_game(
        self,
        player_name: str = "Người Tu Tiên",
        gender: str = "Nam",
        talent: str = "Bình thường",
        race: str = "Người",
        background: str = "Nông dân",
        physique_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initialize new game (wrapper for character_creation)
        """
        logger.info(f"Starting new game: player_name={player_name}, gender={gender}, talent={talent}, race={race}, background={background}")
        try:
            result = self.character_creation(gender, talent, race, background)
            logger.info("New game started successfully")
            return result
        except Exception as e:
            error_msg = f"Failed to start new game: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise
    
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
        logger.info(f"Character creation: gender={gender}, talent={talent}, race={race}, background={background}")
        
        try:
            self.character_gender = gender
            self.character_talent = talent
            self.character_race = race
            self.character_background = background
            
            # Get race data from World Database
            try:
                race_data = self.world_db.get_race(race)
                if race_data:
                    base_stats = race_data.get("base_stats", {})
                    self.attributes = AttributesComponent(**base_stats)
                    logger.info(f"Loaded race data for {race}: {base_stats}")
                else:
                    logger.warning(f"Race data not found for {race}, using defaults")
                    self.attributes = AttributesComponent()  # Default
            except Exception as e:
                error_msg = f"Error loading race data: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                self.attributes = AttributesComponent()  # Fallback to default
            
            # Get clan data from World Database
            try:
                clan_data = self.world_db.get_clan(background)
                if clan_data:
                    starting_perks = clan_data.get("starting_perks", {})
                    logger.info(f"Loaded clan data for {background}: {starting_perks}")
                    # Apply starting perks
                    if "spirit_stones" in starting_perks:
                        self.resources.spirit_stones = starting_perks["spirit_stones"]
                    if "items" in starting_perks:
                        for item_name, quantity in starting_perks["items"].items():
                            self.resources.add_material(item_name, quantity)
                else:
                    logger.warning(f"Clan data not found for {background}")
            except Exception as e:
                error_msg = f"Error loading clan data: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
            
            # Assign physique - use provided physique_id or random
            try:
                if physique_id:
                    # Use provided physique
                    physique_data = self.physique_system.get_physique(physique_id)
                    if physique_data:
                        self.character_physique = physique_id
                        self.physique_level = 1
                        logger.info(f"Assigned selected physique: {physique_data.get('name')} ({physique_data.get('tier')})")
                    else:
                        logger.warning(f"Physique ID {physique_id} not found, using random")
                        physique_id = None
                
                if not physique_id:
                    # Random physique based on talent/race
                    import random
                    elements = ["Kim", "Mộc", "Thủy", "Hỏa", "Thổ", "Linh"]
                    # Higher tier talents get better physiques
                    if "Thiên" in talent or "Thần" in talent:
                        tier_filter = random.choice(["Thần", "Dị", "Linh"])
                    elif "Địa" in talent or "Huyền" in talent:
                        tier_filter = random.choice(["Dị", "Linh"])
                    else:
                        tier_filter = "Linh"
                    
                    self.character_physique = self.physique_system.random_physique(
                        element=random.choice(elements),
                        tier=tier_filter
                    )
                    self.physique_level = 1
                    
                    if self.character_physique:
                        physique_data = self.physique_system.get_physique(self.character_physique)
                        logger.info(f"Assigned random physique: {physique_data.get('name')} ({physique_data.get('tier')})")
            except Exception as e:
                logger.warning(f"Error assigning physique: {e}")
                self.character_physique = None
            
            # Set default location from World Database
            try:
                all_locations = self.world_db.get_all_locations()
                safe_locations = [loc for loc in all_locations if loc.get("danger_level") == "Safe"]
                if safe_locations:
                    self.current_location_id = safe_locations[0].get("id", "loc_village_01")
                    logger.info(f"Selected starting location: {self.current_location_id}")
                else:
                    logger.warning("No safe locations found, using default")
                    self.current_location_id = "loc_village_01"
            except Exception as e:
                error_msg = f"Error selecting location: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
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
            try:
                memory_context = self.memory.get_full_context()
                working_memory = self.memory.get_working_memory_context()
                logger.info("Memory context retrieved successfully")
            except Exception as e:
                error_msg = f"Error getting memory context: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                memory_context = ""
                working_memory = ""
            
            # Check if agent is available
            if not self.agent:
                error_msg = "CultivationAgent not initialized. Please check GEMINI_API_KEY in .env file."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Call AI agent
            try:
                logger.info("Calling AI agent for character story...")
                response = self.agent.process_turn(
                    character_data=character_data,
                    memory_context=memory_context,
                    working_memory=working_memory
                )
                logger.info("AI agent response received successfully")
            except Exception as e:
                error_msg = f"Error calling AI agent: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                raise
            
            self.character_story = response.get("narrative", "")
            self.character_name = response.get("character_name", "Người Chơi")
            self.current_choices = response.get("choices", [])
            
            logger.info(f"Character created: {self.character_name}")
            
            # Save to memory
            try:
                self.memory.add_short_term(
                    content=f"Character created: {self.character_name}, {gender}, {talent}, {race}, {background}",
                    speaker="system"
                )
                self.memory.add_long_term(
                    content=f"Character creation: {self.character_name} - {self.character_story}",
                    memory_type="episodic",
                    importance=0.9
                )
            except Exception as e:
                error_msg = f"Error saving to memory: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
            
            # Save state
            try:
                self._save_state()
                logger.info("Game state saved successfully")
            except Exception as e:
                error_msg = f"Error saving game state: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
            
            return {
                "narrative": self.character_story,
                "character_name": self.character_name,
                "choices": self.current_choices
            }
        except Exception as e:
            error_msg = f"Character creation failed: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise
    
    def process_year_turn(self, choice_index: int) -> Dict[str, Any]:
        """
        Xử lý một năm trong game
        
        Enhanced với:
        - ECS Systems tick
        - Memory updates
        - World Database context
        """
        logger.info(f"Processing year turn: choice_index={choice_index}, age={self.character_age}")
        
        try:
            if choice_index < 0 or choice_index >= len(self.current_choices):
                error_msg = f"Invalid choice index: {choice_index} (valid range: 0-{len(self.current_choices)-1})"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            selected_choice = self.current_choices[choice_index]
            logger.info(f"Selected choice: {selected_choice}")
            
            # Add to memory
            try:
                self.memory.add_short_term(
                    content=selected_choice,
                    speaker="player"
                )
            except Exception as e:
                error_msg = f"Error adding to short-term memory: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
            
            # Update working memory
            try:
                self.memory.set_working_memory(
                    task_type="year_progress",
                    task_data={"choice": selected_choice, "age": self.character_age},
                    priority=8
                )
            except Exception as e:
                error_msg = f"Error setting working memory: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
            
            # ECS Systems tick - DISABLED: AI already overrides calculations
            # Removed for performance: AI response contains state_updates that override ECS calculations
            # If needed, can re-enable but currently redundant
            # try:
            #     self._tick_ecs_systems()
            #     logger.info("ECS systems ticked successfully")
            # except Exception as e:
            #     error_msg = f"Error ticking ECS systems: {str(e)}\n{traceback.format_exc()}"
            #     logger.error(error_msg)
            
            # Progress age
            self.character_age += 1
            logger.info(f"Character age updated to: {self.character_age}")
            
            # Build character data với World Database context
            try:
                location_data = self._get_location_data()
                sect_context = ""
                if self.current_sect_id:
                    sect = self.world_db.get_sect(self.current_sect_id)
                    if sect:
                        sect_context = f"Tông môn: {sect['name']} ({sect.get('type', 'Unknown')})"
                
                # Get attributes with physique
                attributes_dict = self._get_attributes_with_physique()
                
                character_data = {
                    "age": self.character_age,
                    "gender": self.character_gender,
                    "talent": self.character_talent,
                    "race": self.character_race,
                    "background": self.character_background,
                    "story": self.character_story,
                    "name": self.character_name,
                    "attributes": attributes_dict,
                    "cultivation": self.cultivation.dict(),
                    "resources": self.resources.dict(),
                    "choices": self.current_choices,
                    "location_id": location_data.get("location_id"),
                    "location_name": location_data.get("name"),
                    "sect_id": self.current_sect_id,
                    "sect_context": sect_context
                }
                logger.info("Character data built successfully")
            except Exception as e:
                error_msg = f"Error building character data: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                raise
            
            # Check if agent is available
            if not self.agent:
                error_msg = "CultivationAgent not initialized. Please check GEMINI_API_KEY in .env file."
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Get memory context
            try:
                memory_context = self.memory.get_full_context(query=selected_choice)
                working_memory = self.memory.get_working_memory_context()
                logger.info("Memory context retrieved successfully")
            except Exception as e:
                error_msg = f"Error getting memory context: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                memory_context = ""
                working_memory = ""
            
            # Call AI
            try:
                logger.info(f"Calling AI agent for year turn... Choice: {selected_choice}")
                
                # Store debug info
                self._last_ai_debug_info = {
                    "choice": selected_choice,
                    "choice_index": choice_index,
                    "age": self.character_age
                }
                
                response = self.agent.process_turn(
                    character_data=character_data,
                    current_choice=choice_index,
                    memory_context=memory_context,
                    working_memory=working_memory
                )
                
                # Update debug info with response
                if hasattr(self.agent, '_last_prompt'):
                    self._last_ai_debug_info['prompt'] = self.agent._last_prompt
                if hasattr(self.agent, '_last_ai_response'):
                    self._last_ai_debug_info['ai_raw_response'] = self.agent._last_ai_response
                if hasattr(self.agent, '_last_parsed_result'):
                    self._last_ai_debug_info['parsed_result'] = self.agent._last_parsed_result
                if hasattr(self.agent, '_last_error'):
                    self._last_ai_debug_info['error'] = self.agent._last_error
                
                logger.info(f"AI agent response received. Narrative: {response.get('narrative', '')[:100]}...")
                logger.info(f"Response keys: {list(response.keys())}")
                logger.info(f"Has narrative: {bool(response.get('narrative'))}, Narrative length: {len(response.get('narrative', ''))}")
            except Exception as e:
                error_msg = f"Error calling AI agent: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
                raise
            
            # Add AI response to memory
            try:
                self.memory.add_short_term(
                    content=response.get("narrative", ""),
                    speaker="ai"
                )
            except Exception as e:
                error_msg = f"Error adding AI response to memory: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
            
            # Update game state
            try:
                self._apply_state_updates(response.get("state_updates", {}))
                logger.info("Game state updated successfully")
            except Exception as e:
                error_msg = f"Error applying state updates: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
            
            # Update choices
            self.current_choices = response.get("choices", [])
            logger.info(f"Choices updated: {len(self.current_choices)} choices available")
            
            # Complete working memory
            try:
                self.memory.complete_working_memory("year_progress")
            except Exception as e:
                error_msg = f"Error completing working memory: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
            
            # Save state
            try:
                self._save_state()
                logger.info("Game state saved successfully")
            except Exception as e:
                error_msg = f"Error saving game state: {str(e)}\n{traceback.format_exc()}"
                logger.error(error_msg)
            
            logger.info(f"Year turn processed successfully: age={self.character_age}")
            return {
                "narrative": response.get("narrative", ""),
                "choices": self.current_choices,
                "age": self.character_age
            }
        except Exception as e:
            error_msg = f"Failed to process year turn: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise
    
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
            # Fix cultivation_age to be integer (convert from days if needed)
            cultivation_data = self.game_state["cultivation"].copy()
            if "cultivation_age" in cultivation_data:
                # Convert days to years (integer)
                if isinstance(cultivation_data["cultivation_age"], float):
                    cultivation_data["cultivation_age"] = int(cultivation_data["cultivation_age"])
            self.cultivation = CultivationComponent(**cultivation_data)
        
        if self.needs_system:
            self.needs_system.tick(delta_time=1.0)
    
    def _apply_state_updates(self, updates: Dict[str, Any]):
        """Apply state updates from AI response"""
        logger.info(f"Applying state updates: {updates}")
        
        # Update age
        if "age" in updates:
            new_age = updates["age"]
            if new_age != self.character_age:
                logger.info(f"Age updated: {self.character_age} -> {new_age}")
                self.character_age = new_age
        
        # Update cultivation
        if "cultivation" in updates:
            cultivation_updates = updates["cultivation"]
            logger.info(f"Cultivation updates: {cultivation_updates}")
            for key, value in cultivation_updates.items():
                if hasattr(self.cultivation, key):
                    old_value = getattr(self.cultivation, key)
                    setattr(self.cultivation, key, value)
                    logger.info(f"Cultivation.{key} updated: {old_value} -> {value}")
        
        # Update resources
        if "resources" in updates:
            resource_updates = updates["resources"]
            logger.info(f"Resource updates: {resource_updates}")
            if "spirit_stones" in resource_updates:
                old_stones = self.resources.spirit_stones
                self.resources.spirit_stones = resource_updates["spirit_stones"]
                logger.info(f"Spirit stones updated: {old_stones} -> {self.resources.spirit_stones}")
            if "pills" in resource_updates:
                for pill_name, quantity in resource_updates["pills"].items():
                    old_qty = self.resources.pills.get(pill_name, 0)
                    self.resources.add_pill(pill_name, quantity)
                    logger.info(f"Pill {pill_name} updated: {old_qty} -> {self.resources.pills.get(pill_name, 0)}")
            if "materials" in resource_updates:
                for mat_name, quantity in resource_updates["materials"].items():
                    old_qty = self.resources.materials.get(mat_name, 0)
                    self.resources.add_material(mat_name, quantity)
                    logger.info(f"Material {mat_name} updated: {old_qty} -> {self.resources.materials.get(mat_name, 0)}")
        
        # Update attributes
        if "attributes" in updates:
            attribute_updates = updates["attributes"]
            logger.info(f"Attribute updates: {attribute_updates}")
            if self.attributes:
                for key, value in attribute_updates.items():
                    if hasattr(self.attributes, key):
                        old_value = getattr(self.attributes, key)
                        setattr(self.attributes, key, value)
                        logger.info(f"Attribute.{key} updated: {old_value} -> {value}")
        
        # Apply physique effects to cultivation if physique exists
        if self.character_physique and 'cultivation' in updates:
            cultivation_updates = updates.get('cultivation', {})
            if 'spiritual_power' in cultivation_updates:
                base_speed = cultivation_updates.get('spiritual_power', 0)
                adjusted_speed = self.physique_system.apply_to_cultivation(
                    self.character_physique, 
                    base_speed, 
                    self.physique_level
                )
                cultivation_updates['spiritual_power'] = adjusted_speed
                logger.info(f"Applied physique cultivation bonus: {base_speed} -> {adjusted_speed}")
        
        # Force save after updates
        try:
            self._save_state()
            logger.info("State saved after updates")
        except Exception as e:
            logger.error(f"Error saving state after updates: {str(e)}")
    
    def _get_attributes_with_physique(self) -> Dict[str, Any]:
        """Get attributes dict with physique information"""
        attrs = self.attributes.dict() if self.attributes else {}
        
        # Add physique information
        if self.character_physique:
            physique_data = self.physique_system.get_physique(self.character_physique)
            if physique_data:
                attrs['physique_id'] = self.character_physique
                attrs['physique'] = physique_data.get('name', '')
                attrs['physique_level'] = self.physique_level
                attrs['physique_element'] = physique_data.get('element', '')
                attrs['physique_tier'] = physique_data.get('tier', '')
                attrs['physique_description'] = physique_data.get('description', '')
        
        return attrs
    
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
            "attributes": self._get_attributes_with_physique(),
            "needs": self._get_needs_safe(),
            "relationships": self._get_relationships_safe(),
            "location": self._get_location_data(),
            "sect_id": self.current_sect_id,
            "sect_context": self.game_state.get("sect_context", ""),
            # Advanced Systems
            "skills": self._get_available_skills(),
            "economy": self._get_economy_info(),
            "social_graph": self._get_social_graph_info(),
            "formations": self._get_formations_info(),
            "quests": self._get_quests_info(),
            "rewrite_destiny_perks": self.game_state.get("rewrite_destiny_perks", []),
            "tao_souls": self._get_tao_souls_info()
        }
    
    def _get_available_skills(self) -> List[Dict[str, Any]]:
        """Get available skills for player - only skills matching current realm"""
        # Get player cultivation realm
        realm = self.cultivation.realm if self.cultivation else "Mortal"
        realm_level = self.cultivation.realm_level if self.cultivation else 0
        
        # Only return skills that match current realm or have no realm requirement
        # At start (Luyện Khí Kỳ level 1), player should have NO skills
        available_skills = []
        
        # If player is still in early stages, return empty
        if realm == "Luyện Khí Kỳ" and realm_level < 3:
            return []  # No skills at the beginning
        
        for skill_id, skill in self.skill_system.skills.items():
            # Check realm requirement
            skill_realm_req = skill.realm_requirement
            if skill_realm_req:
                # Skill has realm requirement - check if player meets it
                if realm != skill_realm_req:
                    continue  # Skip skills that don't match realm
            
            # Player meets requirements, add skill
            skill_dict = skill.dict()
            skill_dict["id"] = skill_id
            available_skills.append(skill_dict)
        
        return available_skills
    
    def _get_economy_info(self) -> Dict[str, Any]:
        """Get economy information - Simplified: just return basic data"""
        # Simplified: Just return basic info, no complex calculations
        # AI will handle economy in narrative if needed
        try:
            # Get prices for common items (simple lookup)
            common_items = ["currency_spirit_stone_low", "currency_spirit_stone_mid"]
            prices = {}
            for item_id in common_items:
                # Simple lookup from world_db instead of complex economy system
                item = self.world_db.get_item(item_id)
                if item:
                    prices[item_id] = {"price": item.get("price", 0)}
            
            return {
                "prices": prices,
                "economic_cycle": getattr(self.economy_system, 'economic_cycle', 0) if hasattr(self.economy_system, 'economic_cycle') else 0,
                "active_auctions": 0  # Simplified: no complex auction tracking
            }
        except Exception as e:
            logger.warning(f"Error getting economy info: {e}")
            return {"prices": {}, "economic_cycle": 0, "active_auctions": 0}
    
    def _get_needs_safe(self) -> Dict[str, Any]:
        """Get needs safely, always return dict"""
        try:
            needs = self.game_state.get("needs")
            if needs is None:
                return {}
            if isinstance(needs, dict):
                return needs
            # If it's a component, convert to dict
            if hasattr(needs, 'dict'):
                return needs.dict()
            return {}
        except Exception as e:
            logger.warning(f"Error getting needs: {e}")
            return {}
    
    def _get_relationships_safe(self) -> Dict[str, Any]:
        """Get relationships safely, always return dict"""
        try:
            if self.relationship_system:
                relationships = self.relationship_system.get_all_relationships("player")
                # Ensure it's a dict, not None or other type
                if relationships is None:
                    return {}
                if isinstance(relationships, dict):
                    return relationships
                # If it's a list or other type, convert to dict
                if isinstance(relationships, list):
                    return {f"rel_{i}": rel for i, rel in enumerate(relationships)}
                # Fallback: try to convert to dict
                return dict(relationships) if hasattr(relationships, '__iter__') else {}
            return {}
        except Exception as e:
            logger.warning(f"Error getting relationships: {e}")
            return {}
    
    def _get_social_graph_info(self) -> Dict[str, Any]:
        """Get social graph information"""
        try:
            if self.social_graph:
                player_relationships = self.social_graph.get_all_relationships("player")
                player_centrality = self.social_graph.get_centrality("player")
                
                # Ensure relationships is a dict
                if not isinstance(player_relationships, dict):
                    player_relationships = {}
                
                return {
                    "relationships": player_relationships,
                    "centrality": player_centrality or 0,
                    "total_relationships": len(player_relationships) if isinstance(player_relationships, dict) else 0
                }
            return {"relationships": {}, "centrality": 0, "total_relationships": 0}
        except Exception as e:
            logger.warning(f"Error getting social graph info: {e}")
            return {"relationships": {}, "centrality": 0, "total_relationships": 0}
    
    def _get_formations_info(self) -> List[Dict[str, Any]]:
        """Get formations information - Simplified: just return data structures"""
        # Simplified: Just return formation data, no complex bonus calculations
        # AI will handle formation effects in narrative if needed
        try:
            formations = []
            if hasattr(self, 'formation_system') and self.formation_system:
                formation_dict = getattr(self.formation_system, 'formations', {})
                for formation_id, formation_data in formation_dict.items():
                    formations.append({
                        "id": formation_id,
                        "name": formation_data.get("name", formation_id),
                        "node_count": len(formation_data.get("nodes", {}))
                    })
            return formations
        except Exception as e:
            logger.warning(f"Error getting formations info: {e}")
            return []
    
    def _get_quests_info(self) -> Dict[str, Any]:
        """Get quests information - Simplified: just return basic data"""
        # Simplified: Just return quest data, no complex generation logic
        # AI will generate quests in narrative if needed
        try:
            if hasattr(self, 'quest_generator') and self.quest_generator:
                pending = getattr(self.quest_generator, 'pending_quests', [])
                active = list(getattr(self.quest_generator, 'active_quests', {}).values())
                completed = len(getattr(self.quest_generator, 'completed_quests', []))
                
                return {
                    "pending": [q.dict() if hasattr(q, 'dict') else q for q in pending],
                    "active": [q.dict() if hasattr(q, 'dict') else q for q in active],
                    "completed": completed
                }
            return {"pending": [], "active": [], "completed": 0}
        except Exception as e:
            logger.warning(f"Error getting quests info: {e}")
            return {"pending": [], "active": [], "completed": 0}
    
    def _get_tao_souls_info(self) -> List[Dict[str, Any]]:
        """Get Tao Souls information"""
        tao_souls = []
        for soul_id, soul in self.breakthrough_enhanced.tao_souls.items():
            tao_souls.append(soul.dict())
        return tao_souls
