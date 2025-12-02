"""
Action Execution System
Executes validated action proposals and updates game state
"""

import random
from typing import Tuple
from engine.core import (
    EntityManager, get_entity_manager,
    LocationComponent, StateComponent, StatsComponent, InventoryComponent,
    WeaponComponent, DialogueComponent
)
from engine.ai.schemas import ActionProposal, ActionResult


class ActionExecutor:
    """Executes validated actions and updates game state"""
    
    def __init__(self, em: EntityManager = None):
        self.em = em or get_entity_manager()
    
    def execute(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """
        Execute a validated action
        Assumes validation has already passed
        """
        executors = {
            "MOVE": self._execute_move,
            "TAKE": self._execute_take,
            "DROP": self._execute_drop,
            "OPEN": self._execute_open,
            "CLOSE": self._execute_close,
            "UNLOCK": self._execute_unlock,
            "ATTACK": self._execute_attack,
            "TALK": self._execute_talk,
            "EXAMINE": self._execute_examine,
            "EQUIP": self._execute_equip,
        }
        
        executor = executors.get(proposal.intent)
        if executor:
            return executor(proposal, actor_id)
        
        return ActionResult(
            success=False,
            action=proposal.intent,
            error_code="ERR_NOT_IMPLEMENTED",
            message=f"Action {proposal.intent} not implemented yet",
            actor_id=actor_id
        )
    
    def _execute_move(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """Execute movement"""
        direction = proposal.parameters.get("direction")
        location = self.em.get(actor_id, LocationComponent)
        
        # Calculate new position
        direction_map = {
            "north": (0, 1), "south": (0, -1),
            "east": (1, 0), "west": (-1, 0)
        }
        delta = direction_map[direction.lower()]
        
        old_x, old_y = location.x, location.y
        location.x += delta[0]
        location.y += delta[1]
        
        # Update
        self.em.add(actor_id, location)
        
        return ActionResult(
            success=True,
            action="MOVE",
            message=f"Moved {direction}",
            actor_id=actor_id,
            changes={
                "old_position": (old_x, old_y),
                "new_position": (location.x, location.y),
                "direction": direction
            }
        )
    
    def _execute_take(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """Execute taking item"""
        target_id = proposal.target_id
        target_name = self.em.get_name(target_id)
        
        # Add to inventory
        actor_inv = self.em.get(actor_id, InventoryComponent)
        actor_inv.items.append(target_id)
        self.em.add(actor_id, actor_inv)
        
        # Remove from world
        self.em.remove(target_id, LocationComponent)
        
        return ActionResult(
            success=True,
            action="TAKE",
            message=f"Picked up {target_name}",
            actor_id=actor_id,
            target_id=target_id,
            changes={"item_taken": target_id}
        )
    
    def _execute_drop(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """Execute dropping item"""
        target_id = proposal.target_id
        target_name = self.em.get_name(target_id)
        
        # Remove from inventory
        actor_inv = self.em.get(actor_id, InventoryComponent)
        actor_inv.items.remove(target_id)
        self.em.add(actor_id, actor_inv)
        
        # Add to world at actor's location
        actor_loc = self.em.get(actor_id, LocationComponent)
        self.em.add(target_id, LocationComponent(
            zone_id=actor_loc.zone_id,
            room_id=actor_loc.room_id,
            x=actor_loc.x,
            y=actor_loc.y
        ))
        
        return ActionResult(
            success=True,
            action="DROP",
            message=f"Dropped {target_name}",
            actor_id=actor_id,
            target_id=target_id,
            changes={"item_dropped": target_id}
        )
    
    def _execute_open(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """Execute opening"""
        target_id = proposal.target_id
        target_name = self.em.get_name(target_id)
        
        # Update state
        state = self.em.get(target_id, StateComponent)
        state.is_open = True
        self.em.add(target_id, state)
        
        return ActionResult(
            success=True,
            action="OPEN",
            message=f"Opened {target_name}",
            actor_id=actor_id,
            target_id=target_id,
            changes={"opened": target_id}
        )
    
    def _execute_close(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """Execute closing"""
        target_id = proposal.target_id
        target_name = self.em.get_name(target_id)
        
        state = self.em.get(target_id, StateComponent)
        state.is_open = False
        self.em.add(target_id, state)
        
        return ActionResult(
            success=True,
            action="CLOSE",
            message=f"Closed {target_name}",
            actor_id=actor_id,
            target_id=target_id,
            changes={"closed": target_id}
        )
    
    def _execute_unlock(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """Execute unlocking"""
        target_id = proposal.target_id
        target_name = self.em.get_name(target_id)
        
        state = self.em.get(target_id, StateComponent)
        state.is_locked = False
        self.em.add(target_id, state)
        
        return ActionResult(
            success=True,
            action="UNLOCK",
            message=f"Unlocked {target_name}",
            actor_id=actor_id,
            target_id=target_id,
            changes={"unlocked": target_id}
        )
    
    def _execute_attack(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """Execute attack"""
        target_id = proposal.target_id
        target_name = self.em.get_name(target_id)
        
        # Get actor stats
        actor_stats = self.em.get(actor_id, StatsComponent)
        actor_inv = self.em.get(actor_id, InventoryComponent)
        
        # Calculate damage
        base_damage = actor_stats.strength
        weapon_bonus = 0
        
        if actor_inv and actor_inv.equipped_weapon:
            weapon = self.em.get(actor_inv.equipped_weapon, WeaponComponent)
            if weapon:
                weapon_bonus = weapon.damage
        
        total_damage = base_damage + weapon_bonus
        damage = random.randint(max(1, total_damage - 2), total_damage + 2)
        
        # Apply damage
        target_stats = self.em.get(target_id, StatsComponent)
        target_stats.hp -= damage
        target_stats.hp = max(0, target_stats.hp)
        self.em.add(target_id, target_stats)
        
        # Check death
        target_died = target_stats.hp == 0
        if target_died:
            state = self.em.get(target_id, StateComponent) or StateComponent()
            state.is_dead = True
            self.em.add(target_id, state)
        
        return ActionResult(
            success=True,
            action="ATTACK",
            message=f"Attacked {target_name} for {damage} damage",
            actor_id=actor_id,
            target_id=target_id,
            changes={
                "damage_dealt": damage,
                "target_hp": target_stats.hp,
                "target_max_hp": target_stats.max_hp,
                "target_died": target_died
            }
        )
    
    def _execute_talk(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """Execute talking"""
        target_id = proposal.target_id
        target_name = self.em.get_name(target_id)
        
        dialogue = self.em.get(target_id, DialogueComponent)
        topic = proposal.parameters.get("topic")
        
        if topic and topic in dialogue.topics:
            response = dialogue.topics[topic]
        else:
            response = dialogue.greeting
        
        return ActionResult(
            success=True,
            action="TALK",
            message=f"{target_name} says: \"{response}\"",
            actor_id=actor_id,
            target_id=target_id,
            changes={"dialogue": response}
        )
    
    def _execute_examine(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """Execute examination"""
        target_id = proposal.target_id
        description = self.em.get_description(target_id)
        
        return ActionResult(
            success=True,
            action="EXAMINE",
            message=description,
            actor_id=actor_id,
            target_id=target_id,
            changes={}
        )
    
    def _execute_equip(self, proposal: ActionProposal, actor_id: int) -> ActionResult:
        """Execute equipping item"""
        target_id = proposal.target_id
        target_name = self.em.get_name(target_id)
        
        actor_inv = self.em.get(actor_id, InventoryComponent)
        
        # Equip weapon
        if self.em.has(target_id, WeaponComponent):
            actor_inv.equipped_weapon = target_id
            self.em.add(actor_id, actor_inv)
            
            return ActionResult(
                success=True,
                action="EQUIP",
                message=f"Equipped {target_name}",
                actor_id=actor_id,
                target_id=target_id,
                changes={"equipped_weapon": target_id}
            )
        
        return ActionResult(
            success=False,
            action="EQUIP",
            message="Can't equip that",
            actor_id=actor_id
        )


# Global instance
_executor = None

def get_action_executor(em: EntityManager = None) -> ActionExecutor:
    """Get or create global action executor"""
    global _executor
    if _executor is None:
        _executor = ActionExecutor(em)
    return _executor
