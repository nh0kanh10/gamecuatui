"""
Last Voyage Game Mode
Post-apocalyptic survival RPG
"""

from typing import Dict, Any
from engine.games.base_game import BaseGame
from engine.core import (
    LocationComponent, StatsComponent, InventoryComponent,
    IdentityComponent, DialogueComponent, StateComponent
)


class LastVoyageGame(BaseGame):
    """Last Voyage - Post-apocalyptic survival RPG"""
    
    def __init__(self):
        super().__init__(game_mode="last_voyage")
    
    def setup_world(self, **kwargs):
        """Create initial game world"""
        # Player
        self.player_id = self.em.create_player("Hero")
        
        # NPCs
        guard_id = self.em.create_npc("Old Guard", "entrance", "passive")
        guard_dialogue = self.em.get(guard_id, DialogueComponent)
        guard_dialogue.greeting = "Welcome, traveler. Beware the dungeon ahead."
        self.em.add(guard_id, guard_dialogue)
        
        goblin_id = self.em.create_npc("Goblin", "entrance", "aggressive")
        goblin_stats = self.em.get(goblin_id, StatsComponent)
        goblin_stats.hp = 15
        goblin_stats.max_hp = 15
        self.em.add(goblin_id, goblin_stats)
        
        # Items
        self.em.create_weapon("Iron Sword", damage=12, room_id="entrance")
        self.em.create_item("Torch", "A flickering torch", room_id="entrance")
        
        # Door
        self.em.create_door("Heavy Door", "entrance", is_locked=False)
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state"""
        if not self.player_id:
            return {}
        
        context = self.context_builder.build(self.player_id)
        
        return {
            "player_hp": context.player_hp,
            "player_max_hp": context.player_max_hp,
            "player_name": context.player_name,
            "current_room": context.current_room_id,
            "room_description": context.room_description,
            "inventory": context.inventory,
            "visible_entities": context.visible_entities,
        }
    
    def apply_updates(self, updates: dict):
        """Apply state updates from AI"""
        super().apply_updates(updates)  # Call base for movement
        
        if not updates:
            return
        
        # Handle HP changes (Last Voyage specific)
        if 'target_hp_change' in updates:
            entities = self.em.find_at_location("entrance")
            for eid in entities:
                name = self.em.get_name(eid)
                if "Goblin" in name:
                    stats = self.em.get(eid, StatsComponent)
                    if stats:
                        stats.hp += updates['target_hp_change']
                        stats.hp = max(0, stats.hp)
                        self.em.add(eid, stats)
                        
                        if stats.hp == 0:
                            state = self.em.get(eid, StateComponent) or StateComponent()
                            state.is_dead = True
                            self.em.add(eid, state)
                    break

