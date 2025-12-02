"""
Core ECS components
"""

from .components import *
from .database import Database, get_db
from .entity import EntityManager, get_entity_manager

__all__ = [
    # Database
    'Database',
    'get_db',
    
    # Entity Manager
    'EntityManager',
    'get_entity_manager',
    
    # Components
    'IdentityComponent',
    'LocationComponent',
    'StateComponent',
    'StatsComponent',
    'InventoryComponent',
    'WeaponComponent',
    'ArmorComponent',
    'DialogueComponent',
    'AIComponent',
    'RelationComponent',
    'QuestComponent',
    'KeyComponent',
    'ContainerComponent',
    'TimestampComponent',
    'COMPONENT_REGISTRY',
]
