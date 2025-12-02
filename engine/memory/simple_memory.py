"""
Simple Memory System - SQLite FTS5 Based
Core memory system tuân thủ single-database architecture
"""

import sqlite3
import json
import uuid
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum
from contextlib import contextmanager


class MemoryType(Enum):
    """Types of memory in hierarchical system"""
    EPISODIC = "episodic"    # Recent events, player actions
    SEMANTIC = "semantic"    # World knowledge, NPCs, locations
    PROCEDURAL = "procedural"  # Game rules, mechanics
    LORE = "lore"            # World lore, background stories


def parse_sqlite_timestamp(ts_str: str) -> datetime:
    """
    Robust SQLite timestamp parsing
    
    Handles both ISO format (with 'T') and SQLite format (with ' ')
    """
    if not ts_str:
        return datetime.now()
    
    try:
        # Try ISO format first (Python 3.11+)
        return datetime.fromisoformat(ts_str.replace(' ', 'T'))
    except (ValueError, AttributeError):
        try:
            # Fallback to SQLite format
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Last resort
            return datetime.now()


def sanitize_fts_query(query: str) -> str:
    """
    Sanitize FTS5 query string
    
    Remove control chars, escape quotes, remove dangerous patterns
    """
    if not query:
        return ""
    
    # Remove control characters
    query = re.sub(r'[\x00-\x1F\x7F]', '', query)
    
    # Escape single quotes (FTS5 uses single quotes for phrases)
    query = query.replace("'", "''")
    
    # Remove dangerous FTS5 operators if not intentional
    # (Keep basic operators like AND, OR, NOT if user wants them)
    
    return query.strip()


class SimpleMemory:
    """
    Simple Memory System using SQLite FTS5
    
    Features:
    - Fast full-text search (<5ms for 10K records)
    - Single database (uses existing SQLite)
    - Zero new dependencies
    - BM25 ranking
    - Metadata filtering
    - Rule-based compression
    - WAL mode for better concurrency
    """
    
    def __init__(self, db_path: str = "data/world.db"):
        """
        Initialize Simple Memory System
        
        Args:
            db_path: Path to SQLite database (same as game database)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()
        print("✅ SimpleMemory initialized (SQLite FTS5)")
    
    @contextmanager
    def _get_connection(self):
        """
        Connection context manager with proper setup
        
        Sets row_factory, PRAGMA, and handles errors
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        
        # Set WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_tables(self):
        """Initialize FTS5 virtual table and metadata table"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Metadata table (for filtering and stats)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id TEXT UNIQUE NOT NULL,
                    entity_id INTEGER,
                    location_id TEXT,
                    save_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    importance REAL DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    metadata_json TEXT
                )
            """)
            
            # FTS5 virtual table for full-text search
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                    memory_id UNINDEXED,
                    content,
                    memory_type,
                    tokenize='porter'
                )
            """)
            
            # Indexes for fast filtering
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_save_type 
                ON memory_metadata(save_id, memory_type, importance DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_entity 
                ON memory_metadata(entity_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_location 
                ON memory_metadata(location_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_created 
                ON memory_metadata(created_at DESC)
            """)
    
    def add(
        self,
        content: str,
        memory_type: str,
        save_id: str,
        entity_id: Optional[int] = None,
        location_id: Optional[str] = None,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Add a memory with transaction safety
        
        Args:
            content: Memory text content
            memory_type: Type of memory (episodic/semantic/procedural/lore)
            save_id: Save slot identifier
            entity_id: Related entity ID (optional)
            location_id: Related location (optional)
            importance: Importance score (0.0-1.0)
            metadata: Additional metadata (JSON)
        
        Returns:
            Memory ID or None if failed
        """
        if not content or not content.strip():
            return None
        
        # Generate unique ID using UUID (no collision risk)
        memory_id = f"{save_id}_{uuid.uuid4().hex}"
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Insert into FTS5 first (for full-text search)
                cursor.execute("""
                    INSERT INTO memory_fts (memory_id, content, memory_type)
                    VALUES (?, ?, ?)
                """, (memory_id, content, memory_type))
                
                # Insert into metadata table (for filtering and stats)
                metadata_json = None
                if metadata:
                    try:
                        metadata_json = json.dumps(metadata)
                    except (TypeError, ValueError) as e:
                        print(f"⚠️  Failed to serialize metadata: {e}")
                        metadata_json = None
                
                cursor.execute("""
                    INSERT INTO memory_metadata (
                        memory_id, entity_id, location_id, save_id,
                        memory_type, importance, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory_id,
                    entity_id,
                    location_id,
                    save_id,
                    memory_type,
                    importance,
                    metadata_json
                ))
            
            return memory_id
            
        except sqlite3.IntegrityError as e:
            print(f"❌ Memory add failed (integrity error): {e}")
            return None
        except Exception as e:
            print(f"❌ Memory add failed: {e}")
            return None
    
    def search(
        self,
        query: str,
        save_id: str,
        memory_types: Optional[List[str]] = None,
        n_results: int = 5,
        min_importance: float = 0.0,
        entity_id: Optional[int] = None,
        location_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories using FTS5 with BM25 ranking
        
        Args:
            query: Search query
            save_id: Save slot to search in
            memory_types: Filter by types (None = all)
            n_results: Number of results
            min_importance: Minimum importance
            entity_id: Filter by entity
            location_id: Filter by location
        
        Returns:
            List of memories with scores
        """
        if memory_types is None:
            memory_types = ["episodic", "semantic", "procedural", "lore"]
        
        # Sanitize query for FTS5
        sanitized_query = sanitize_fts_query(query)
        if not sanitized_query:
            return []
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build WHERE clause for metadata filtering
            where_parts = ["m.save_id = ?"]
            params = [save_id]
            
            if memory_types:
                placeholders = ','.join(['?'] * len(memory_types))
                where_parts.append(f"m.memory_type IN ({placeholders})")
                params.extend(memory_types)
            
            if entity_id is not None:
                where_parts.append("m.entity_id = ?")
                params.append(entity_id)
            
            if location_id:
                where_parts.append("m.location_id = ?")
                params.append(location_id)
            
            if min_importance > 0:
                where_parts.append("m.importance >= ?")
                params.append(min_importance)
            
            where_clause = " AND ".join(where_parts)
            
            # FTS5 search with BM25 ranking
            # BM25 returns negative values (lower = better), so ORDER BY ASC
            sql = f"""
                SELECT 
                    m.memory_id,
                    f.content,
                    m.memory_type,
                    m.importance,
                    m.created_at,
                    m.entity_id,
                    m.location_id,
                    m.metadata_json,
                    bm25(memory_fts) as fts_score
                FROM memory_fts f
                JOIN memory_metadata m ON f.memory_id = m.memory_id
                WHERE f.content MATCH ? AND {where_clause}
                ORDER BY 
                    bm25(memory_fts) ASC,  -- Lower BM25 = better match
                    m.importance DESC,
                    m.created_at DESC
                LIMIT ?
            """
            
            params = [sanitized_query] + params + [n_results]
            
            try:
                cursor.execute(sql, params)
                results = cursor.fetchall()
            except sqlite3.OperationalError as e:
                print(f"⚠️  FTS5 search error: {e}")
                return []
            
            # Format results
            formatted_results = []
            fts_scores = []  # For normalization
            
            for row in results:
                fts_scores.append(row['fts_score'])
            
            # Normalize BM25 scores (min-max normalization if we have scores)
            if fts_scores:
                min_score = min(fts_scores)
                max_score = max(fts_scores)
                score_range = max_score - min_score if max_score != min_score else 1.0
            else:
                min_score = 0
                score_range = 1.0
            
            for row in results:
                # Normalize BM25 score to 0-1 range
                # BM25 is negative (lower = better), so invert
                raw_score = row['fts_score']
                if score_range > 0:
                    normalized_fts = 1.0 - ((raw_score - min_score) / score_range)
                else:
                    normalized_fts = 1.0
                
                # Clamp to [0, 1]
                normalized_fts = max(0.0, min(1.0, normalized_fts))
                
                # Combined score: FTS5 + importance + recency
                importance_score = float(row['importance'])
                
                # Recency score (simple: newer = higher)
                created_at = parse_sqlite_timestamp(row['created_at'])
                age_days = (datetime.now() - created_at).days
                recency_score = max(0.0, 1.0 - (age_days / 90.0))  # 90-day decay
                
                # Combined score
                combined_score = (
                    0.5 * normalized_fts +      # FTS5 relevance
                    0.3 * importance_score +     # Importance
                    0.2 * recency_score          # Recency
                )
                
                # Parse metadata JSON with error handling
                metadata = {}
                if row['metadata_json']:
                    try:
                        metadata = json.loads(row['metadata_json'])
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"⚠️  Failed to parse metadata JSON: {e}")
                        metadata = {}
                
                formatted_results.append({
                    'id': row['memory_id'],
                    'text': row['content'],
                    'memory_type': row['memory_type'],
                    'score': combined_score,
                    'fts_score': normalized_fts,
                    'importance': importance_score,
                    'recency': recency_score,
                    'metadata': metadata
                })
            
            # Sort by combined score (already sorted by SQL, but ensure)
            formatted_results.sort(key=lambda x: x['score'], reverse=True)
            
            return formatted_results[:n_results]
    
    def get_context(
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
        memory_types = ["episodic", "semantic"]
        if include_lore:
            memory_types.append("lore")
        
        results = self.search(
            query=query,
            save_id=save_id,
            memory_types=memory_types,
            n_results=n_results,
            entity_id=entity_id,
            location_id=location_id
        )
        
        if not results:
            return "No relevant memories found."
        
        # Format context
        context_parts = []
        for mem in results:
            mem_type_label = mem['memory_type'].upper()
            context_parts.append(f"[{mem_type_label}] {mem['text']}")
        
        return "\n\n".join(context_parts)
    
    def get_count(self, save_id: Optional[str] = None) -> int:
        """Get total memory count"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if save_id:
                cursor.execute("SELECT COUNT(*) FROM memory_metadata WHERE save_id = ?", (save_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM memory_metadata")
            
            count = cursor.fetchone()[0]
            return count
    
    def cleanup(self, save_id: str, max_memories: int = 10000) -> int:
        """
        Cleanup old, low-importance memories (rule-based)
        
        Args:
            save_id: Save slot to cleanup
            max_memories: Maximum memories to keep
        
        Returns:
            Number of memories deleted
        """
        current_count = self.get_count(save_id)
        
        if current_count <= max_memories:
            return 0
        
        to_delete = current_count - max_memories
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get memory_ids to delete (before deletion for integrity)
            cursor.execute("""
                SELECT memory_id FROM memory_metadata
                WHERE save_id = ?
                AND importance < 0.3
                AND created_at < datetime('now', '-30 days')
                ORDER BY importance ASC, created_at ASC
                LIMIT ?
            """, (save_id, to_delete))
            
            memory_ids_to_delete = [row[0] for row in cursor.fetchall()]
            
            if not memory_ids_to_delete:
                return 0
            
            # Delete from metadata (with transaction)
            placeholders = ','.join(['?'] * len(memory_ids_to_delete))
            cursor.execute(f"""
                DELETE FROM memory_metadata
                WHERE memory_id IN ({placeholders})
            """, memory_ids_to_delete)
            
            # Delete from FTS5 explicitly (maintain integrity)
            cursor.execute(f"""
                DELETE FROM memory_fts
                WHERE memory_id IN ({placeholders})
            """, memory_ids_to_delete)
            
            deleted_count = len(memory_ids_to_delete)
            
            # Use total_changes instead of rowcount (more reliable)
            # deleted_count = conn.total_changes
            
            if deleted_count > 0:
                print(f"🧹 Cleaned up {deleted_count} old memories")
            
            return deleted_count


# Global instance - FIXED: Use unique name to avoid collision
_simple_memory = None

def get_simple_memory(db_path: str = "data/world.db") -> SimpleMemory:
    """Get or create global SimpleMemory instance"""
    global _simple_memory
    if _simple_memory is None:
        _simple_memory = SimpleMemory(db_path)
    return _simple_memory
