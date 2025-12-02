"""
Entity Manager - High-level interface for ECS operations
"""

from typing import Optional, List, Type, Dict, Any
from pydantic import BaseModel

from .database import Database, get_db
from .components import (
    IdentityComponent, LocationComponent, StateComponent, StatsComponent,
    InventoryComponent, WeaponComponent, DialogueComponent, AIComponent,
    TimestampComponent
)


class EntityManager:
    """Manages entities and their components"""
    
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()
    
    def create(self, label: str = "", **components) -> int:
        """
        Create a new entity with optional components
        
        Example:
            entity_id = em.create(
                "player",
                identity=IdentityComponent(name="Hero", description="A brave adventurer"),
                stats=StatsComponent(hp=100, strength=15)
            )
        """
        entity_id = self.db.create_entity(label)
        
        # Add timestamp
        self.db.add_component(entity_id, TimestampComponent())
        
        # Add provided components
        for comp_name, component in components.items():
            if isinstance(component, BaseModel):
                self.db.add_component(entity_id, component)
        
        return entity_id
    
    def delete(self, entity_id: int):
        """Delete an entity and all its components"""
        self.db.delete_entity(entity_id)
    
    def add(self, entity_id: int, component: BaseModel):
        """Add/update a component on an entity"""
        self.db.add_component(entity_id, component)
    
    def get(self, entity_id: int, component_class: Type[BaseModel]) -> Optional[BaseModel]:
        """Get a component from an entity"""
        return self.db.get_component(entity_id, component_class)
    
    def remove(self, entity_id: int, component_class: Type[BaseModel]):
        """Remove a component from an entity"""
        self.db.remove_component(entity_id, component_class)
    
    def has(self, entity_id: int, component_class: Type[BaseModel]) -> bool:
        """Check if entity has a component"""
        return self.db.get_component(entity_id, component_class) is not None
    
    def get_all(self, entity_id: int) -> Dict[str, BaseModel]:
        """Get all components for an entity"""
        return self.db.get_all_components(entity_id)
    
    def exists(self, entity_id: int) -> bool:
        """Check if entity exists"""
        return self.db.entity_exists(entity_id)
    
    def find_with(self, component_class: Type[BaseModel]) -> List[int]:
        """Find all entities that have a specific component"""
        return self.db.find_entities_with_component(component_class)
    
    def find_at_location(self, room_id: str) -> List[int]:
        """Find all entities in a room"""
        return self.db.find_entities_at_location(room_id)
    
    def get_name(self, entity_id: int) -> str:
        """Get entity's display name"""
        identity = self.get(entity_id, IdentityComponent)
        return identity.name if identity else f"Entity#{entity_id}"
    
    def get_description(self, entity_id: int) -> str:
        """Get entity's description"""
        identity = self.get(entity_id, IdentityComponent)
        return identity.description if identity else "An unknown entity."
    
    # Helper factories for common entities
    
    def create_player(self, name: str = "Player") -> int:
        """Create a player entity"""
        return self.create(
            "player",
            identity=IdentityComponent(
                name=name,
                description="A brave adventurer",
                tags=["player"]
            ),
            location=LocationComponent(
                zone_id="start",
                room_id="entrance"
            ),
            stats=StatsComponent(
                hp=100,
                max_hp=100,
                strength=10,
                intelligence=10,
                dexterity=10
            ),
            inventory=InventoryComponent(
                items=[],
                capacity=20
            )
        )
    
    def create_npc(self, name: str, room_id: str, behavior: str = "passive") -> int:
        """Create an NPC entity"""
        return self.create(
            f"npc_{name.lower().replace(' ', '_')}",
            identity=IdentityComponent(
                name=name,
                description=f"A {behavior} character",
                tags=["npc", behavior]
            ),
            location=LocationComponent(
                zone_id="start",
                room_id=room_id
            ),
            stats=StatsComponent(
                hp=50,
                strength=8
            ),
            dialogue=DialogueComponent(
                greeting=f"Hello, I am {name}.",
                farewell="Goodbye."
            ),
            ai=AIComponent(
                behavior_type=behavior
            )
        )
    
    def create_item(self, name: str, description: str, room_id: str) -> int:
        """Create a basic item"""
        return self.create(
            f"item_{name.lower().replace(' ', '_')}",
            identity=IdentityComponent(
                name=name,
                description=description,
                tags=["item"]
            ),
            location=LocationComponent(
                zone_id="start",
                room_id=room_id
            )
        )
    
    def create_weapon(self, name: str, damage: int, room_id: str) -> int:
        """Create a weapon"""
        entity_id = self.create(
            f"weapon_{name.lower().replace(' ', '_')}",
            identity=IdentityComponent(
                name=name,
                description=f"A weapon that deals {damage} damage",
                tags=["item", "weapon"]
            ),
            location=LocationComponent(
                zone_id="start",
                room_id=room_id
            ),
            weapon=WeaponComponent(
                damage=damage
            )
        )
        return entity_id
    
    def create_door(self, name: str, room_id: str, is_locked: bool = False) -> int:
        """Create a door"""
        return self.create(
            f"door_{name.lower().replace(' ', '_')}",
            identity=IdentityComponent(
                name=name,
                description="A sturdy door",
                tags=["door", "obstacle"]
            ),
            location=LocationComponent(
                zone_id="start",
                room_id=room_id
            ),
            state=StateComponent(
                is_locked=is_locked,
                is_open=False
            )
        )


# Global entity manager
_em = None

def get_entity_manager(db: Optional[Database] = None) -> EntityManager:
    """Get or create global entity manager"""
    global _em
    if _em is None:
        _em = EntityManager(db)
    return _em
