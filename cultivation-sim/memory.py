"""
Memory System for Cultivation Simulator
Standalone memory system (riêng biệt)
"""

import sqlite3
import json
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Import Vietnamese tokenizer if available
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from engine.memory.vietnamese_tokenizer import tokenize_vietnamese
    HAS_VIETNAMESE_TOKENIZER = True
except ImportError:
    HAS_VIETNAMESE_TOKENIZER = False


class CultivationMemory:
    """
    Memory system riêng cho Cultivation Simulator
    Sử dụng SQLite FTS5
    """
    
    def __init__(self, db_path: str, save_id: str):
        self.db_path = db_path
        self.save_id = save_id
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        """Initialize memory tables (already done in database.py, but ensure)"""
        cursor = self.db.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        self.db.commit()
    
    def add(self, content: str, memory_type: str = "episodic", importance: float = 0.5):
        """Add memory"""
        memory_id = f"{self.save_id}_{uuid.uuid4().hex}"
        
        cursor = self.db.cursor()
        try:
            # Insert content
            cursor.execute("""
                INSERT INTO memory_content (memory_id, content)
                VALUES (?, ?)
            """, (memory_id, content))
            
            # Insert metadata
            cursor.execute("""
                INSERT INTO memory_metadata 
                (memory_id, save_id, memory_type, importance, metadata_json)
                VALUES (?, ?, ?, ?, ?)
            """, (memory_id, self.save_id, memory_type, importance, None))
            
            # FTS5 will be synced by trigger
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"⚠️  Memory add error: {e}")
    
    def get_context(self, query: str, n_results: int = 5) -> str:
        """Get relevant context from memory"""
        cursor = self.db.cursor()
        
        # Sanitize query for FTS5
        query_safe = query.replace('"', '""')
        
        # Search with BM25 ranking
        cursor.execute("""
            SELECT 
                m.content,
                m.memory_type,
                md.importance,
                md.last_accessed
            FROM memory_fts m
            JOIN memory_metadata md ON m.memory_id = md.memory_id
            WHERE md.save_id = ?
            AND memory_fts MATCH ?
            ORDER BY bm25(memory_fts) DESC, md.importance DESC
            LIMIT ?
        """, (self.save_id, query_safe, n_results))
        
        rows = cursor.fetchall()
        if not rows:
            return ""
        
        # Format context
        context_parts = []
        for row in rows:
            context_parts.append(f"- {row['content'][:200]}...")
        
        return "\n".join(context_parts)
    
    def get_count(self) -> int:
        """Get total memory count"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM memory_metadata WHERE save_id = ?
        """, (self.save_id,))
        return cursor.fetchone()[0]
    
    def cleanup(self, max_memories: int = 1000):
        """Cleanup old low-importance memories"""
        from compaction import compaction_worker_for_save
        return compaction_worker_for_save(self.save_id)

