"""
Simple Memory Manager - High-level interface
Wraps SimpleMemory with game-specific helpers
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .simple_memory import SimpleMemory, MemoryType, get_simple_memory
from .compression import CompressionRules


class SimpleMemoryManager:
    """
    High-level memory manager for game context
    
    Provides convenient methods for common memory operations
    """
    
    def __init__(self, memory_system: Optional[SimpleMemory] = None, db_path: str = "data/world.db"):
        self.memory = memory_system or get_simple_memory(db_path)
        self.db_path = db_path
    
    def remember_action(
        self,
        user_input: str,
        narrative: str,
        save_id: str,
        entity_id: Optional[int] = None,
        location_id: Optional[str] = None,
        importance: Optional[float] = None
    ):
        """
        Remember a player action and its outcome
        
        Args:
            user_input: What the player said/did
            narrative: AI-generated narrative response
            save_id: Save slot
            entity_id: Entity involved (if any)
            location_id: Location where action occurred
            importance: How important (None = auto-calculate)
        """
        # Combine input and narrative
        content = f"Player: {user_input}\nResult: {narrative}"
        
        # Auto-calculate importance if not provided
        if importance is None:
            importance = self._auto_importance(user_input, narrative, entity_id)
        
        self.memory.add(
            content=content,
            memory_type=MemoryType.EPISODIC.value,
            save_id=save_id,
            entity_id=entity_id,
            location_id=location_id,
            importance=importance,
            metadata={"action": True, "user_input": user_input[:100]}
        )
    
    def remember_npc_interaction(
        self,
        npc_name: str,
        dialogue: str,
        save_id: str,
        npc_id: int,
        location_id: Optional[str] = None,
        relationship_change: Optional[float] = None
    ):
        """Remember an NPC interaction"""
        content = f"NPC {npc_name}: {dialogue}"
        if relationship_change:
            content += f" (Relationship changed by {relationship_change:+.1f})"
        
        importance = 0.7 if relationship_change else 0.5
        
        self.memory.add(
            content=content,
            memory_type=MemoryType.EPISODIC.value,
            save_id=save_id,
            entity_id=npc_id,
            location_id=location_id,
            importance=importance,
            metadata={"npc_name": npc_name, "dialogue": True, "relationship_change": relationship_change}
        )
    
    def remember_combat(
        self,
        enemy_name: str,
        outcome: str,
        save_id: str,
        enemy_id: int,
        location_id: Optional[str] = None,
        player_damage: int = 0,
        enemy_damage: int = 0
    ):
        """Remember a combat encounter"""
        content = f"Combat with {enemy_name}: {outcome}"
        if player_damage > 0:
            content += f" (Player took {player_damage} damage)"
        if enemy_damage > 0:
            content += f" (Enemy took {enemy_damage} damage)"
        
        importance = 0.8 if "defeated" in outcome.lower() or "killed" in outcome.lower() else 0.6
        
        self.memory.add(
            content=content,
            memory_type=MemoryType.EPISODIC.value,
            save_id=save_id,
            entity_id=enemy_id,
            location_id=location_id,
            importance=importance,
            metadata={"combat": True, "enemy_name": enemy_name, "outcome": outcome}
        )
    
    def remember_location_discovery(
        self,
        location_name: str,
        description: str,
        save_id: str,
        location_id: str
    ):
        """Remember discovering a new location"""
        content = f"Discovered location: {location_name}\n{description}"
        
        self.memory.add(
            content=content,
            memory_type=MemoryType.SEMANTIC.value,
            save_id=save_id,
            location_id=location_id,
            importance=0.8,
            metadata={"location_name": location_name, "discovery": True}
        )
    
    def remember_item_acquisition(
        self,
        item_name: str,
        how_acquired: str,
        save_id: str,
        item_id: Optional[int] = None
    ):
        """Remember acquiring an item"""
        content = f"Acquired {item_name}: {how_acquired}"
        
        self.memory.add(
            content=content,
            memory_type=MemoryType.EPISODIC.value,
            save_id=save_id,
            entity_id=item_id,
            importance=0.5,
            metadata={"item_acquisition": True, "item_name": item_name}
        )
    
    def get_relevant_context(
        self,
        query: str,
        save_id: str,
        entity_id: Optional[int] = None,
        location_id: Optional[str] = None,
        include_lore: bool = True,
        n_results: int = 5
    ) -> str:
        """
        Get relevant context for AI prompt
        
        Args:
            query: What we're looking for
            save_id: Save slot
            entity_id: Filter by entity
            location_id: Filter by location
            include_lore: Include world lore
            n_results: Number of memories
        
        Returns:
            Formatted context string
        """
        return self.memory.get_context(
            query=query,
            save_id=save_id,
            entity_id=entity_id,
            location_id=location_id,
            include_lore=include_lore,
            n_results=n_results
        )
    
    def get_npc_memory(self, npc_name: str, save_id: str, npc_id: Optional[int] = None) -> str:
        """Get all memories about a specific NPC"""
        query = f"NPC {npc_name}"
        
        results = self.memory.search(
            query=query,
            save_id=save_id,
            entity_id=npc_id,
            n_results=10
        )
        
        if not results:
            return f"No memories about {npc_name}."
        
        memories = [mem['text'] for mem in results]
        return "\n".join(f"- {m}" for m in memories)
    
    def get_location_memory(self, location_name: str, save_id: str, location_id: Optional[str] = None) -> str:
        """Get all memories about a specific location"""
        query = f"location {location_name}"
        
        results = self.memory.search(
            query=query,
            save_id=save_id,
            location_id=location_id,
            n_results=10
        )
        
        if not results:
            return f"No memories about {location_name}."
        
        memories = [mem['text'] for mem in results]
        return "\n".join(f"- {m}" for m in memories)
    
    def _auto_importance(self, user_input: str, narrative: str, entity_id: Optional[int]) -> float:
        """Auto-calculate importance based on heuristics"""
        base = 0.2
        
        # NPC interaction
        if entity_id:
            base += 0.1
        
        # Combat keywords
        combat_keywords = ["attack", "fight", "kill", "defeat", "combat", "battle"]
        if any(kw in user_input.lower() or kw in narrative.lower() for kw in combat_keywords):
            base += 0.15
        
        # Item keywords
        item_keywords = ["take", "pick", "acquire", "get", "find", "discover"]
        if any(kw in user_input.lower() for kw in item_keywords):
            base += 0.1
        
        # Discovery keywords
        discovery_keywords = ["discover", "find", "explore", "enter", "open"]
        if any(kw in user_input.lower() for kw in discovery_keywords):
            base += 0.2
        
        return min(1.0, base)
    
    def cleanup(self, save_id: str, max_memories: int = 10000):
        """Cleanup old memories using rules"""
        CompressionRules.compress_memories(self.memory, save_id, max_memories)


# Global instance
_memory_manager = None

def get_memory_manager(db_path: str = "data/world.db") -> SimpleMemoryManager:
    """Get or create global SimpleMemoryManager"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = SimpleMemoryManager(db_path=db_path)
    return _memory_manager

