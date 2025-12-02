"""
Precondition Validation System
Validates action proposals before execution
This is the "gatekeeper" - ensures LLM proposals are physically valid
"""

from typing import Tuple, Optional, Dict, Any
from engine.core import (
    EntityManager, get_entity_manager,
    IdentityComponent, LocationComponent, StateComponent, StatsComponent,
    InventoryComponent, WeaponComponent, KeyComponent, DialogueComponent
)
from engine.ai.schemas import ActionProposal, ValidationError


class PreconditionSystem:
    """Validates actions against current game state"""
    
    def __init__(self, em: Optional[EntityManager] = None):
        self.em = em or get_entity_manager()
    
    def validate(self, proposal: ActionProposal, actor_id: int) -> Tuple[bool, Optional[ValidationError]]:
        """
        Validate an action proposal
        
        Returns:
            (is_valid, error_details)
        """
        # Route to specific validator based on intent
        validators = {
            "MOVE": self._validate_move,
            "TAKE": self._validate_take,
            "DROP": self._validate_drop,
            "OPEN": self._validate_open,
            "CLOSE": self._validate_close,
            "UNLOCK": self._validate_unlock,
            "ATTACK": self._validate_attack,
            "TALK": self._validate_talk,
            "EXAMINE": self._validate_examine,
            "USE": self._validate_use,
            "EQUIP": self._validate_equip,
        }
        
        validator = validators.get(proposal.intent)
        if not validator:
            return False, ValidationError(
                code="ERR_UNKNOWN_ACTION",
                message=f"Unknown action type: {proposal.intent}"
            )
        
        return validator(proposal, actor_id)
    
    def _validate_move(self, proposal: ActionProposal, actor_id: int) -> Tuple[bool, Optional[ValidationError]]:
        """Validate movement"""
        direction = proposal.parameters.get("direction")
        if not direction:
            return False, ValidationError(
                code="ERR_MISSING_PARAM",
                message="Movement requires a direction"
            )
        
        # Get actor location
        location = self.em.get(actor_id, LocationComponent)
        if not location:
            return False, ValidationError(
                code="ERR_NO_LOCATION",
                message="Actor has no location"
            )
        
        # Calculate new position
        new_x, new_y = location.x, location.y
        direction_map = {
            "north": (0, 1),
            "south": (0, -1),
            "east": (1, 0),
            "west": (-1, 0)
        }
        
        delta = direction_map.get(direction.lower())
        if not delta:
            return False, ValidationError(
                code="ERR_INVALID_DIRECTION",
                message=f"Invalid direction: {direction}",
                suggested_actions=["north", "south", "east", "west"]
            )
        
        new_x += delta[0]
        new_y += delta[1]
        
        # Check for obstacles at new position
        entities_at_pos = self._find_entities_at(location.room_id, new_x, new_y)
        for entity_id in entities_at_pos:
            state = self.em.get(entity_id, StateComponent)
            if state and not state.is_open and ("door" in self._get_tags(entity_id) or "wall" in self._get_tags(entity_id)):
                entity_name = self.em.get_name(entity_id)
                return False, ValidationError(
                    code="ERR_BLOCKED",
                    message=f"Path blocked by {entity_name}",
                    suggested_actions=[f"open {entity_name}", "go different direction"]
                )
        
        return True, None
    
    def _validate_take(self, proposal: ActionProposal, actor_id: int) -> Tuple[bool, Optional[ValidationError]]:
        """Validate taking an item"""
        target_id = proposal.target_id
        
        # Check target exists
        if not target_id or not self.em.exists(target_id):
            return False, ValidationError(
                code="ERR_NOT_FOUND",
                message="Can't find that item"
            )
        
        # Check actor has inventory
        actor_inv = self.em.get(actor_id, InventoryComponent)
        if not actor_inv:
            return False, ValidationError(
                code="ERR_NO_INVENTORY",
                message="You can't carry items"
            )
        
        # Check inventory not full
        if len(actor_inv.items) >= actor_inv.capacity:
            return False, ValidationError(
                code="ERR_INVENTORY_FULL",
                message="Your inventory is full",
                suggested_actions=["drop something first"]
            )
        
        # Check item is in same room
        actor_loc = self.em.get(actor_id, LocationComponent)
        target_loc = self.em.get(target_id, LocationComponent)
        
        if not target_loc:
            return False, ValidationError(
                code="ERR_NOT_TAKEABLE",
                message="You can't take that"
            )
        
        if target_loc.room_id != actor_loc.room_id:
            return False, ValidationError(
                code="ERR_TOO_FAR",
                message="That's too far away"
            )
        
        return True, None
    
    def _validate_open(self, proposal: ActionProposal, actor_id: int) -> Tuple[bool, Optional[ValidationError]]:
        """Validate opening something"""
        target_id = proposal.target_id
        
        # Check target exists
        if not target_id or not self.em.exists(target_id):
            return False, ValidationError(
                code="ERR_NOT_FOUND",
                message="There's nothing here to open"
            )
        
        # Check target has state component
        target_state = self.em.get(target_id, StateComponent)
        if not target_state:
            target_name = self.em.get_name(target_id)
            return False, ValidationError(
                code="ERR_CANT_OPEN",
                message=f"You can't open {target_name}"
            )
        
        # Check already open
        if target_state.is_open:
            target_name = self.em.get_name(target_id)
            return False, ValidationError(
                code="ERR_ALREADY_OPEN",
                message=f"{target_name} is already open"
            )
        
        # Check locked
        if target_state.is_locked:
            # Check if actor has key
            has_key = self._actor_has_key_for(actor_id, target_id)
            if not has_key:
                target_name = self.em.get_name(target_id)
                return False, ValidationError(
                    code="ERR_LOCKED_NO_KEY",
                    message=f"{target_name} is locked. You need a key.",
                    suggested_actions=["find a key", "try to break it"]
                )
        
        # Check same room
        actor_loc = self.em.get(actor_id, LocationComponent)
        target_loc = self.em.get(target_id, LocationComponent)
        
        if target_loc and target_loc.room_id != actor_loc.room_id:
            return False, ValidationError(
                code="ERR_TOO_FAR",
                message="That's too far away"
            )
        
        return True, None
    
    def _validate_attack(self, proposal: ActionProposal, actor_id: int) -> Tuple[bool, Optional[ValidationError]]:
        """Validate attack action"""
        target_id = proposal.target_id
        
        # Check target exists
        if not target_id or not self.em.exists(target_id):
            return False, ValidationError(
                code="ERR_NOT_FOUND",
                message="There's no one here to attack"
            )
        
        # Check target has stats (is attackable)
        target_stats = self.em.get(target_id, StatsComponent)
        if not target_stats:
            target_name = self.em.get_name(target_id)
            return False, ValidationError(
                code="ERR_INVALID_TARGET",
                message=f"You can't attack {target_name}"
            )
        
        # Check same room
        actor_loc = self.em.get(actor_id, LocationComponent)
        target_loc = self.em.get(target_id, LocationComponent)
        
        if target_loc.room_id != actor_loc.room_id:
            target_name = self.em.get_name(target_id)
            return False, ValidationError(
                code="ERR_TOO_FAR",
                message=f"{target_name} is not here",
                suggested_actions=["move closer"]
            )
        
        # Check target not already dead
        target_state = self.em.get(target_id, StateComponent)
        if target_state and target_state.is_dead:
            target_name = self.em.get_name(target_id)
            return False, ValidationError(
                code="ERR_ALREADY_DEAD",
                message=f"{target_name} is already dead"
            )
        
        return True, None
    
    def _validate_talk(self, proposal: ActionProposal, actor_id: int) -> Tuple[bool, Optional[ValidationError]]:
        """Validate talking to NPC"""
        target_id = proposal.target_id
        
        # Check target exists
        if not target_id or not self.em.exists(target_id):
            return False, ValidationError(
                code="ERR_NOT_FOUND",
                message="There's no one here to talk to"
            )
        
        # Check target can talk
        dialogue = self.em.get(target_id, DialogueComponent)
        if not dialogue:
            target_name = self.em.get_name(target_id)
            return False, ValidationError(
                code="ERR_CANT_TALK",
                message=f"{target_name} can't talk"
            )
        
        # Check same room
        actor_loc = self.em.get(actor_id, LocationComponent)
        target_loc = self.em.get(target_id, LocationComponent)
        
        if target_loc.room_id != actor_loc.room_id:
            target_name = self.em.get_name(target_id)
            return False, ValidationError(
                code="ERR_TOO_FAR",
                message=f"{target_name} is not here"
            )
        
        return True, None
    
    def _validate_examine(self, proposal: ActionProposal, actor_id: int) -> Tuple[bool, Optional[ValidationError]]:
        """Validate examining something - always succeeds if target exists"""
        target_id = proposal.target_id
        
        if not target_id or not self.em.exists(target_id):
            return False, ValidationError(
                code="ERR_NOT_FOUND",
                message="You don't see that here"
            )
        
        return True, None
    
    def _validate_use(self, proposal: ActionProposal, actor_id: int) -> Tuple[bool, Optional[ValidationError]]:
        """Validate using an item"""
        # Implementation depends on specific item mechanics
        # Placeholder for now
        return True, None
    
    def _validate_equip(self, proposal: ActionProposal, actor_id: int) -> Tuple[bool, Optional[ValidationError]]:
        """Validate equipping item"""
        target_id = proposal.target_id
        
        # Check actor has inventory
        actor_inv = self.em.get(actor_id, InventoryComponent)
        if not actor_inv:
            return False, ValidationError(
                code="ERR_NO_INVENTORY",
                message="You can't equip items"
            )
        
        # Check item in inventory
        if target_id not in actor_inv.items:
            return False, ValidationError(
                code="ERR_NOT_IN_INVENTORY",
                message="You don't have that item",
                suggested_actions=["check inventory"]
            )
        
        # Check item is equippable (has weapon or armor component)
        is_weapon = self.em.has(target_id, WeaponComponent)
        if not is_weapon:
            target_name = self.em.get_name(target_id)
            return False, ValidationError(
                code="ERR_NOT_EQUIPPABLE",
        
        if not target_id or not self.em.exists(target_id):
            return False, ValidationError(
                code="ERR_NOT_FOUND",
                message="There's nothing here to close"
            )
        
        target_state = self.em.get(target_id, StateComponent)
        if not target_state:
            return False, ValidationError(
                code="ERR_CANT_CLOSE",
                message="You can't close that"
            )
        
        if not target_state.is_open:
            target_name = self.em.get_name(target_id)
            return False, ValidationError(
                code="ERR_ALREADY_CLOSED",
                message=f"{target_name} is already closed"
            )
        
        return True, None
    
    def _validate_unlock(self, proposal: ActionProposal, actor_id: int) -> Tuple[bool, Optional[ValidationError]]:
        """Validate unlocking"""
        target_id = proposal.target_id
        
        if not target_id or not self.em.exists(target_id):
            return False, ValidationError(
                code="ERR_NOT_FOUND",
                message="There's nothing here to unlock"
            )
        
        target_state = self.em.get(target_id, StateComponent)
        if not target_state or not target_state.is_locked:
            target_name = self.em.get_name(target_id)
            return False, ValidationError(
                code="ERR_NOT_LOCKED",
                message=f"{target_name} is not locked"
            )
        
        # Check for key
        if not self._actor_has_key_for(actor_id, target_id):
            return False, ValidationError(
                code="ERR_NO_KEY",
                message="You don't have the right key",
                suggested_actions=["find a key"]
            )
        
        return True, None
    
    # Helper methods
    
    def _get_tags(self, entity_id: int) -> list:
        """Get entity tags"""
        identity = self.em.get(entity_id, IdentityComponent)
        return identity.tags if identity else []
    
    def _actor_has_key_for(self, actor_id: int, target_id: int) -> bool:
        """Check if actor has key for target"""
        actor_inv = self.em.get(actor_id, InventoryComponent)
        if not actor_inv:
            return False
        
        for item_id in actor_inv.items:
            key_comp = self.em.get(item_id, KeyComponent)
            if key_comp and target_id in key_comp.unlocks_door_ids:
                return True
        
        return False
    
    def _find_entities_at(self, room_id: str, x: int, y: int) -> list:
        """Find entities at specific coordinates"""
        entities_in_room = self.em.find_at_location(room_id)
        result = []
        
        for entity_id in entities_in_room:
            loc = self.em.get(entity_id, LocationComponent)
            if loc and loc.x == x and loc.y == y:
                result.append(entity_id)
        
        return result


# Global instance
_precondition_system = None

def get_precondition_system(em: Optional[EntityManager] = None) -> PreconditionSystem:
    """Get or create global precondition system"""
    global _precondition_system
    if _precondition_system is None:
        _precondition_system = PreconditionSystem(em)
    return _precondition_system
