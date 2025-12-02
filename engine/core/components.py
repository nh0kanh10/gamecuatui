"""
Component Definitions
All game data is stored in Components (pure data structures)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime


class IdentityComponent(BaseModel):
    """Basic identity information for any entity"""
    name: str = Field(description="Display name")
    description: str = Field(description="Detailed description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization (npc, item, weapon, etc.)")


class LocationComponent(BaseModel):
    """Position in the game world"""
    zone_id: str = Field(description="Zone/dungeon identifier")
    room_id: str = Field(description="Room identifier within zone")
    x: int = Field(default=0, description="X coordinate within room")
    y: int = Field(default=0, description="Y coordinate within room")


class StateComponent(BaseModel):
    """Physical state flags"""
    is_locked: bool = False
    is_open: bool = False
    is_broken: bool = False
    is_lit: bool = False
    is_hidden: bool = False
    is_dead: bool = False


class StatsComponent(BaseModel):
    """Character/creature statistics"""
    hp: int = Field(default=100, ge=0)
    max_hp: int = Field(default=100, gt=0)
    strength: int = Field(default=10, ge=1)
    intelligence: int = Field(default=10, ge=1)
    dexterity: int = Field(default=10, ge=1)
    level: int = Field(default=1, ge=1)
    xp: int = Field(default=0, ge=0)


class InventoryComponent(BaseModel):
    """Container for items"""
    items: List[int] = Field(default_factory=list, description="List of entity IDs")
    capacity: int = Field(default=20, gt=0)
    equipped_weapon: Optional[int] = Field(default=None, description="Entity ID of equipped weapon")
    equipped_armor: Optional[int] = Field(default=None, description="Entity ID of equipped armor")


class WeaponComponent(BaseModel):
    """Weapon properties"""
    damage: int = Field(default=5, ge=1)
    damage_type: Literal["slashing", "piercing", "bludgeoning", "magic"] = "slashing"
    range: int = Field(default=1, description="Attack range in tiles")
    durability: int = Field(default=100, ge=0, le=100)


class ArmorComponent(BaseModel):
    """Armor/protection properties"""
    defense: int = Field(default=5, ge=0)
    durability: int = Field(default=100, ge=0, le=100)


class DialogueComponent(BaseModel):
    """NPC conversation data"""
    greeting: str = Field(default="Hello, traveler.")
    farewell: str = Field(default="Farewell.")
    topics: Dict[str, str] = Field(default_factory=dict, description="Topic -> response mapping")
    quest_giver: bool = Field(default=False)


class AIComponent(BaseModel):
    """NPC behavior configuration"""
    behavior_type: Literal["passive", "aggressive", "defensive", "trader", "guard"] = "passive"
    aggro_range: int = Field(default=5, ge=0)
    patrol_path: List[Dict[str, int]] = Field(default_factory=list, description="List of {x, y} waypoints")
    home_position: Optional[Dict[str, int]] = None


class RelationComponent(BaseModel):
    """Relationship with player"""
    affinity: int = Field(default=0, ge=-100, le=100, description="Relationship score")
    is_hostile: bool = False
    is_ally: bool = False
    trust_level: int = Field(default=0, ge=0, le=10)


class QuestComponent(BaseModel):
    """Quest/task information"""
    quest_id: str
    title: str
    description: str
    objectives: List[str] = Field(default_factory=list)
    completed_objectives: List[bool] = Field(default_factory=list)
    is_completed: bool = False
    rewards: Dict[str, int] = Field(default_factory=dict, description="item_id -> quantity")


class KeyComponent(BaseModel):
    """Key that unlocks specific doors"""
    unlocks_door_ids: List[int] = Field(default_factory=list, description="Entity IDs of doors this key opens")


class ContainerComponent(BaseModel):
    """Container (chest, crate, etc.)"""
    items: List[int] = Field(default_factory=list)
    capacity: int = Field(default=50)
    requires_key: bool = False
    key_id: Optional[int] = None


class TimestampComponent(BaseModel):
    """Track creation/modification times"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Component Registry - for serialization/deserialization
COMPONENT_REGISTRY = {
    "identity": IdentityComponent,
    "location": LocationComponent,
    "state": StateComponent,
    "stats": StatsComponent,
    "inventory": InventoryComponent,
    "weapon": WeaponComponent,
    "armor": ArmorComponent,
    "dialogue": DialogueComponent,
    "ai": AIComponent,
    "relation": RelationComponent,
    "quest": QuestComponent,
    "key": KeyComponent,
    "container": ContainerComponent,
    "timestamp": TimestampComponent,
}


def get_component_class(component_type: str):
    """Get component class by type name"""
    return COMPONENT_REGISTRY.get(component_type)
