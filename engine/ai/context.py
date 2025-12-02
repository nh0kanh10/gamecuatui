"""
Context Builder System
Constructs AI context from ECS state and Memory
"""

from typing import List, Dict, Any, Optional
from engine.core import EntityManager, IdentityComponent, LocationComponent, InventoryComponent, StatsComponent
from engine.ai.schemas import GameContext


class ContextBuilder:
    """Builds GameContext from ECS state"""
    
    def __init__(self, entity_manager: EntityManager):
        self.em = entity_manager
    
    def build(self, player_id: int) -> GameContext:
        """Build full context for the player"""
        
        # Get player components
        stats = self.em.get(player_id, StatsComponent)
        location = self.em.get(player_id, LocationComponent)
        inventory = self.em.get(player_id, InventoryComponent)
        identity = self.em.get(player_id, IdentityComponent)
        
        # Get visible entities
        visible_entities = self._get_visible_entities(location.room_id, player_id)
        
        # Get inventory items
        inventory_items = self._get_inventory_items(inventory.items)
        
        return GameContext(
            player_id=player_id,
            player_name=identity.name,
            player_hp=stats.hp,
            player_max_hp=stats.max_hp,
            current_room_id=location.room_id,
            room_description=f"You are in the {location.room_id}.", # Placeholder for real description
            visible_entities=visible_entities,
            inventory=inventory_items
        )
    
    def _get_visible_entities(self, room_id: str, player_id: int) -> List[Dict[str, Any]]:
        """Get list of visible entities in the room"""
        entities = []
        entity_ids = self.em.find_at_location(room_id)
        
        for eid in entity_ids:
            if eid == player_id:
                continue
                
            identity = self.em.get(eid, IdentityComponent)
            if identity:
                entities.append({
                    'id': eid,
                    'name': identity.name,
                    'description': identity.description,
                    'type': identity.tags[0] if identity.tags else 'entity'
                })
        return entities

    def _get_inventory_items(self, item_ids: List[int]) -> List[Dict[str, Any]]:
        """Get details of items in inventory"""
        items = []
        for iid in item_ids:
            identity = self.em.get(iid, IdentityComponent)
            if identity:
                items.append({
                    'id': iid,
                    'name': identity.name,
                    'description': identity.description
                })
        return items
