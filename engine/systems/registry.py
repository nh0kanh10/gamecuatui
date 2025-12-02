"""
Action Registry System
Decouples action definitions from execution logic
"""

from typing import Dict, Callable, Tuple, Optional, Type
from engine.ai.schemas import ActionProposal, ActionResult, ValidationError
from engine.core import EntityManager


# Type definitions for handlers
ValidatorFunc = Callable[[ActionProposal, int, EntityManager], Tuple[bool, Optional[ValidationError]]]
ExecutorFunc = Callable[[ActionProposal, int, EntityManager], ActionResult]


class ActionDefinition:
    """Defines a game action with its validator and executor"""
    def __init__(self, intent: str, validator: ValidatorFunc, executor: ExecutorFunc):
        self.intent = intent
        self.validator = validator
        self.executor = executor


class ActionRegistry:
    """Registry for all game actions"""
    
    def __init__(self):
        self._actions: Dict[str, ActionDefinition] = {}
    
    def register(self, definition: ActionDefinition):
        """Register a new action"""
        self._actions[definition.intent] = definition
    
    def get(self, intent: str) -> Optional[ActionDefinition]:
        """Get action definition by intent"""
        return self._actions.get(intent)
    
    def get_validator(self, intent: str) -> Optional[ValidatorFunc]:
        return self._actions[intent].validator if intent in self._actions else None
        
    def get_executor(self, intent: str) -> Optional[ExecutorFunc]:
        return self._actions[intent].executor if intent in self._actions else None


# Global instance
_action_registry = None

def get_action_registry() -> ActionRegistry:
    """Get or create global action registry"""
    global _action_registry
    if _action_registry is None:
        _action_registry = ActionRegistry()
    return _action_registry
