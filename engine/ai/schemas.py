"""
Pydantic Schemas for AI Communication
Defines structured formats for proposals and results
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List
from datetime import datetime


class ActionProposal(BaseModel):
    """
    Structured action proposed by AI
    Engine validates and executes if valid
    """
    intent: Literal[
        "MOVE", "TAKE", "DROP", "OPEN", "CLOSE",
        "UNLOCK", "LOCK", "EXAMINE", "TALK", "ATTACK",
        "USE", "EQUIP", "UNEQUIP", "SEARCH", "REST"
    ] = Field(description="Type of action")
    
    target_id: Optional[int] = Field(default=None, description="Entity ID of target")
    target_name: Optional[str] = Field(default=None, description="Name hint for entity resolution")
    
    tool_id: Optional[int] = Field(default=None, description="Entity ID of tool/weapon used")
    
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional parameters (direction, dialogue topic, etc.)"
    )


class ActionResult(BaseModel):
    """Result of action execution"""
    success: bool
    action: str
    error_code: Optional[str] = None
    message: str = Field(description="Human-readable result description")
    
    # Additional context for narrative generation
    actor_id: int
    target_id: Optional[int] = None
    changes: Dict[str, Any] = Field(default_factory=dict, description="State changes that occurred")
    
    timestamp: datetime = Field(default_factory=datetime.now)


class GameContext(BaseModel):
    """
    Context provided to AI for decision making
    Condensed snapshot of relevant game state
    """
    player_id: int
    player_name: str
    player_hp: int
    player_max_hp: int
    
    current_room_id: str
    room_description: str
    
    visible_entities: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Entities in current room"
    )
    
    inventory: List[Dict[str, Any]] = Field(default_factory=list)
    
    recent_events: List[str] = Field(
        default_factory=list,
        description="Recent action results for context"
    )


class ValidationError(BaseModel):
    """Detailed validation failure"""
    code: str = Field(description="Error code (ERR_NOT_FOUND, ERR_LOCKED, etc.)")
    message: str = Field(description="Human-readable error")
    suggested_actions: List[str] = Field(
        default_factory=list,
        description="What player could try instead"
    )
