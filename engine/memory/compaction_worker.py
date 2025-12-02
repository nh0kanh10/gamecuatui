"""
Memory Compaction Worker
Keeps memory count under limit by removing low-importance memories
"""

import sqlite3
from pathlib import Path
from typing import List, Tuple
import json

MAX_MEMORIES_PER_SAVE = 1000
SIMILARITY_THRESHOLD = 0.8  # For merging similar memories (future)


def compaction_worker_for_save(save_id: str) -> int:
    """
    Compact memories for a specific save
    Returns number of memories deleted
    """
    db_path = Path(f"data/saves/{save_id}.db")
    if not db_path.exists():
        return 0
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        cur = conn.cursor()
        
        # Get all memories ordered by importance and last_accessed
        cur.execute("""
            SELECT 
                m.memory_id,
                c.content,
                m.importance,
                m.last_accessed,
                m.access_count
            FROM memory_metadata m
            JOIN memory_content c ON m.memory_id = c.memory_id
            ORDER BY m.importance DESC, m.last_accessed DESC
        """)
        
        rows = cur.fetchall()
        total_memories = len(rows)
        
        if total_memories <= MAX_MEMORIES_PER_SAVE:
            return 0  # No compaction needed
        
        # Keep top N by importance
        keep = rows[:MAX_MEMORIES_PER_SAVE]
        drop = rows[MAX_MEMORIES_PER_SAVE:]
        
        # Delete low-importance memories
        drop_ids = [row['memory_id'] for row in drop]
        deleted_count = 0
        
        for mem_id in drop_ids:
            try:
                # Delete from FTS5 (will cascade)
                cur.execute("DELETE FROM memory_fts WHERE memory_id = ?", (mem_id,))
                # Delete from content
                cur.execute("DELETE FROM memory_content WHERE memory_id = ?", (mem_id,))
                # Delete from metadata
                cur.execute("DELETE FROM memory_metadata WHERE memory_id = ?", (mem_id,))
                deleted_count += 1
            except Exception as e:
                print(f"⚠️  Error deleting memory {mem_id}: {e}")
        
        conn.commit()
        return deleted_count
        
    except Exception as e:
        conn.rollback()
        print(f"⚠️  Compaction error for {save_id}: {e}")
        return 0
    finally:
        conn.close()


def merge_similar_memories(save_id: str, similarity_threshold: float = SIMILARITY_THRESHOLD):
    """
    Future: Merge similar memories using fuzzy matching
    For now, just a placeholder
    """
    # TODO: Implement similarity-based merging
    # Options:
    # 1. Use difflib.SequenceMatcher for text similarity
    # 2. Use sentence-transformers for semantic similarity
    # 3. Use OpenAI embeddings for clustering
    pass


def get_memory_stats(save_id: str) -> dict:
    """Get memory statistics for a save"""
    db_path = Path(f"data/saves/{save_id}.db")
    if not db_path.exists():
        return {"total": 0, "over_limit": False}
    
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM memory_metadata")
        total = cur.fetchone()[0]
        
        return {
            "total": total,
            "over_limit": total > MAX_MEMORIES_PER_SAVE,
            "limit": MAX_MEMORIES_PER_SAVE
        }
    except Exception:
        return {"total": 0, "over_limit": False}
    finally:
        conn.close()

