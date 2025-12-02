"""
Rule-Based Memory Compression
Simple, predictable compression without LLM
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from .simple_memory import SimpleMemory, parse_sqlite_timestamp


class CompressionRules:
    """
    Rule-based compression - no LLM, predictable behavior
    """
    
    @staticmethod
    def should_compress(memory: Dict[str, Any], age_days: int) -> bool:
        """
        Determine if a memory should be compressed/deleted
        
        Rules:
        1. Age > 30 days AND importance < 0.3 → Delete
        2. Age > 90 days AND importance < 0.5 → Delete
        3. Age > 180 days AND importance < 0.7 → Delete
        4. Never delete importance >= 0.8
        5. Never delete lore memories
        """
        importance = memory.get('importance', 0.5)
        memory_type = memory.get('memory_type', 'episodic')
        
        # Never delete lore
        if memory_type == 'lore':
            return False
        
        # Never delete critical memories
        if importance >= 0.8:
            return False
        
        # Rule 1: Old + low importance
        if age_days > 30 and importance < 0.3:
            return True
        
        # Rule 2: Very old + medium importance
        if age_days > 90 and importance < 0.5:
            return True
        
        # Rule 3: Extremely old + medium-high importance
        if age_days > 180 and importance < 0.7:
            return True
        
        return False
    
    @staticmethod
    def compress_memories(memory_system: SimpleMemory, save_id: str, max_memories: int = 10000):
        """
        Compress memories using rules
        
        Args:
            memory_system: SimpleMemory instance
            save_id: Save slot
            max_memories: Maximum memories to keep
        """
        current_count = memory_system.get_count(save_id)
        
        if current_count <= max_memories:
            return 0
        
        # Get all memories sorted by age and importance
        import sqlite3
        
        with memory_system._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT memory_id, importance, created_at, memory_type
                FROM memory_metadata
                WHERE save_id = ?
                ORDER BY importance ASC, created_at ASC
            """, (save_id,))
            
            memories = cursor.fetchall()
            
            # Apply compression rules
            to_delete = []
            for mem in memories:
                # Robust timestamp parsing
                created_at = parse_sqlite_timestamp(mem['created_at'])
                age_days = (datetime.now() - created_at).days
                
                mem_dict = {
                    'importance': mem['importance'],
                    'memory_type': mem['memory_type']
                }
                
                if CompressionRules.should_compress(mem_dict, age_days):
                    to_delete.append(mem['memory_id'])
                
                # Stop when we have enough to delete
                if len(to_delete) >= (current_count - max_memories):
                    break
            
            # Delete memories (with transaction integrity)
            if to_delete:
                placeholders = ','.join(['?'] * len(to_delete))
                
                # Delete from metadata
                cursor.execute(f"""
                    DELETE FROM memory_metadata
                    WHERE memory_id IN ({placeholders})
                """, to_delete)
                
                # Delete from FTS5 explicitly (maintain integrity)
                cursor.execute(f"""
                    DELETE FROM memory_fts
                    WHERE memory_id IN ({placeholders})
                """, to_delete)
                
                deleted = len(to_delete)  # Use count instead of rowcount
                
                if deleted > 0:
                    print(f"🗜️  Compressed {deleted} memories using rules")
                
                return deleted
        
        return 0

