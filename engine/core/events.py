"""
Event Bus System
Decouples systems by allowing them to publish and subscribe to events
"""

from typing import Dict, List, Callable, Any, Type
from pydantic import BaseModel
from collections import defaultdict


class GameEvent(BaseModel):
    """Base class for all game events"""
    pass


class EventBus:
    """Synchronous Event Bus"""
    
    def __init__(self):
        self._subscribers: Dict[Type[GameEvent], List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: Type[GameEvent], handler: Callable[[GameEvent], None]):
        """Subscribe a handler to an event type"""
        self._subscribers[event_type].append(handler)
    
    def publish(self, event: GameEvent):
        """Publish an event to all subscribers"""
        event_type = type(event)
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"⚠️ Error in event handler {handler.__name__}: {e}")

    def clear(self):
        """Clear all subscribers"""
        self._subscribers.clear()


# Global instance
_event_bus = None

def get_event_bus() -> EventBus:
    """Get or create global event bus"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
