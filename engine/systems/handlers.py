"""
Core Action Handlers
Standalone functions for validating and executing actions.
Registered with ActionRegistry.
"""

from typing import Tuple, Optional
from engine.core import (
    EntityManager, LocationComponent, InventoryComponent, 
    StateComponent, IdentityComponent, StatsComponent
)
from engine.ai.schemas import ActionProposal, ActionResult, ValidationError
from engine.core.events import get_event_bus, GameEvent

# --- Events ---

class MoveEvent(GameEvent):
    entity_id: int
    from_room: str
    to_room: str

class TakeEvent(GameEvent):
    entity_id: int
    item_id: int
    item_name: str

# --- MOVE Action ---

def validate_move(proposal: ActionProposal, actor_id: int, em: EntityManager) -> Tuple[bool, Optional[ValidationError]]:
    direction = proposal.parameters.get("direction")
    if not direction:
        return False, ValidationError(message="Direction is required for MOVE action.")
    
    # In a real implementation, we would check the map graph here.
    # For now, we assume all moves are valid if direction is specified, 
    # or we could check if a door exists in that direction.
    
    # Simplified check: Just ensure direction is valid string
    valid_directions = ["north", "south", "east", "west", "up", "down"]
    if direction.lower() not in valid_directions:
        return False, ValidationError(message=f"Invalid direction: {direction}")

    return True, None

def execute_move(proposal: ActionProposal, actor_id: int, em: EntityManager) -> ActionResult:
    direction = proposal.parameters.get("direction")
    loc = em.get(actor_id, LocationComponent)
    
    old_room = loc.room_id
    
    # Simple map logic for demo (can be replaced with real map system)
    # For now, just change room_id based on direction string to simulate movement
    # In reality, this should query a MapSystem
    
    # Hack for demo: "north" from "entrance" -> "hallway"
    new_room = old_room # Default to stay
    
    if old_room == "entrance" and direction == "north":
        new_room = "hallway"
    elif old_room == "hallway" and direction == "south":
        new_room = "entrance"
    else:
        return ActionResult(
            action="MOVE",
            success=False,
            message=f"You can't go {direction} from here."
        )
        
    # Update component
    loc.room_id = new_room
    em.add(actor_id, loc) # Save change
    
    # Publish event
    bus = get_event_bus()
    bus.publish(MoveEvent(entity_id=actor_id, from_room=old_room, to_room=new_room))
    
    return ActionResult(
        action="MOVE",
        success=True,
        message=f"You moved {direction} to {new_room}.",
        changes={"old_room": old_room, "new_room": new_room}
    )

# --- TAKE Action ---

def validate_take(proposal: ActionProposal, actor_id: int, em: EntityManager) -> Tuple[bool, Optional[ValidationError]]:
    target_id = proposal.target_id
    if not target_id:
        return False, ValidationError(message="Target is required for TAKE action.")
    
    # Check if entity exists
    if not em.get(target_id, IdentityComponent):
        return False, ValidationError(message="Target entity not found.", code="ERR_NOT_FOUND")
    
    # Check if entity is at same location
    actor_loc = em.get(actor_id, LocationComponent)
    target_loc = em.get(target_id, LocationComponent)
    
    if not target_loc or target_loc.room_id != actor_loc.room_id:
        return False, ValidationError(message="Target is not here.", code="ERR_WRONG_LOCATION")
    
    # Check if entity is "takeable" (has no Stats/AI, is not fixed)
    # For simplicity, assume anything with Identity and Location that isn't a Door/NPC is takeable
    # Better: Add 'ItemComponent' or 'TakeableComponent'
    # Current logic: If it has Stats (NPC) or State (Door), can't take
    if em.get(target_id, StatsComponent):
        return False, ValidationError(message="You can't take that!", code="ERR_INVALID_TARGET")
        
    return True, None

def execute_take(proposal: ActionProposal, actor_id: int, em: EntityManager) -> ActionResult:
    target_id = proposal.target_id
    
    # Remove Location component (it's now in inventory)
    em.remove(target_id, LocationComponent)
    
    # Add to inventory
    inv = em.get(actor_id, InventoryComponent)
    inv.items.append(target_id)
    em.add(actor_id, inv)
    
    item_name = em.get_name(target_id)
    
    # Publish event
    bus = get_event_bus()
    bus.publish(TakeEvent(entity_id=actor_id, item_id=target_id, item_name=item_name))
    
    return ActionResult(
        action="TAKE",
        success=True,
        message=f"You picked up the {item_name}.",
        changes={"added_to_inventory": item_name}
    )

# --- Registration ---

def register_core_actions():
    from engine.systems.registry import get_action_registry, ActionDefinition
    
    registry = get_action_registry()
    
    registry.register(ActionDefinition("MOVE", validate_move, execute_move))
    registry.register(ActionDefinition("TAKE", validate_take, execute_take))
    
    print("✅ Core actions registered (MOVE, TAKE)")
