"""
Memory Compaction for Cultivation Simulator
"""

import sqlite3
from pathlib import Path

MAX_MEMORIES_PER_SAVE = 1000


def compaction_worker_for_save(save_id: str) -> int:
    """Compact memories for save"""
    # Find database file
    db_path = Path(f"data/saves/{save_id}.db")
    if not db_path.exists():
        return 0
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.memory_id, m.importance, m.last_accessed
            FROM memory_metadata m
            WHERE m.save_id = ?
            ORDER BY m.importance DESC, m.last_accessed DESC
        """, (save_id,))
        
        rows = cur.fetchall()
        if len(rows) <= MAX_MEMORIES_PER_SAVE:
            return 0
        
        # Delete low-importance memories
        drop = rows[MAX_MEMORIES_PER_SAVE:]
        deleted = 0
        
        for row in drop:
            mem_id = row['memory_id']
            cur.execute("DELETE FROM memory_fts WHERE memory_id = ?", (mem_id,))
            cur.execute("DELETE FROM memory_content WHERE memory_id = ?", (mem_id,))
            cur.execute("DELETE FROM memory_metadata WHERE memory_id = ?", (mem_id,))
            deleted += 1
        
        conn.commit()
        return deleted
    except Exception as e:
        conn.rollback()
        print(f"⚠️  Compaction error: {e}")
        return 0
    finally:
        conn.close()

