"""
3-Tier Memory Architecture
Dựa trên báo cáo kỹ thuật: Short-term, Working, Long-term Memory
"""

import sqlite3
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from enum import Enum


class MemoryTier(str, Enum):
    """3-tier memory system"""
    SHORT_TERM = "short_term"  # 10-20 conversations gần nhất
    WORKING = "working"  # Current task/goal
    LONG_TERM = "long_term"  # Vector DB + Rolling Summary


class Memory3Tier:
    """
    3-Tier Memory Architecture
    
    Short-term: RAM (in-memory list, 10-20 conversations)
    Working: SQLite table (current task, goal)
    Long-term: SQLite FTS5 + Rolling Summary
    """
    
    def __init__(self, db_path: str, save_id: str):
        self.db_path = db_path
        self.save_id = save_id
        
        # Short-term: In-memory list (10-20 conversations)
        self.short_term_memory: List[Dict[str, Any]] = []
        self.max_short_term = 20
        
        # Initialize database
        self._init_tables()
    
    def _init_tables(self):
        """Initialize SQLite tables for Working and Long-term memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Working Memory table (current task/goal)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS working_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                task_data TEXT NOT NULL,
                priority INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Long-term Memory table (FTS5 for search)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS long_term_memory_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT UNIQUE NOT NULL,
                save_id TEXT NOT NULL,
                content TEXT NOT NULL,
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
            CREATE VIRTUAL TABLE IF NOT EXISTS long_term_memory_fts USING fts5(
                memory_id UNINDEXED,
                content,
                memory_type,
                tokenize='porter'
            )
        """)
        
        # Rolling Summary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rolling_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                save_id TEXT NOT NULL,
                summary_text TEXT NOT NULL,
                period_start TIMESTAMP NOT NULL,
                period_end TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Trigger to sync FTS5
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS long_term_memory_fts_insert
            AFTER INSERT ON long_term_memory_metadata
            BEGIN
                INSERT INTO long_term_memory_fts(memory_id, content, memory_type)
                VALUES (NEW.memory_id, NEW.content, NEW.memory_type);
            END
        """)
        
        conn.commit()
        conn.close()
    
    # --- SHORT-TERM MEMORY (In-memory) ---
    
    def add_short_term(self, content: str, speaker: str = "player", metadata: Optional[Dict] = None):
        """
        Thêm vào short-term memory (RAM)
        Tự động rollover khi vượt quá max_short_term
        """
        entry = {
            "content": content,
            "speaker": speaker,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.short_term_memory.append(entry)
        
        # Rollover: Nếu vượt quá max, chuyển oldest vào long-term
        if len(self.short_term_memory) > self.max_short_term:
            oldest = self.short_term_memory.pop(0)
            self._rollover_to_long_term(oldest)
    
    def get_short_term(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent short-term memories"""
        return self.short_term_memory[-limit:]
    
    def get_short_term_context(self) -> str:
        """Get short-term memory as context string for AI"""
        recent = self.get_short_term(10)
        context_parts = []
        
        for entry in recent:
            speaker = entry.get("speaker", "unknown")
            content = entry.get("content", "")
            context_parts.append(f"{speaker}: {content}")
        
        return "\n".join(context_parts)
    
    # --- WORKING MEMORY (SQLite) ---
    
    def set_working_memory(
        self,
        task_type: str,
        task_data: Dict[str, Any],
        priority: int = 5
    ):
        """
        Set working memory (current task/goal)
        
        Args:
            task_type: "cultivation", "quest", "relationship", etc.
            task_data: Task details
            priority: 1-10 (10 = highest)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Mark old tasks as completed
        cursor.execute("""
            UPDATE working_memory
            SET completed = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE save_id = ? AND task_type = ? AND completed = FALSE
        """, (self.save_id, task_type))
        
        # Insert new task
        cursor.execute("""
            INSERT INTO working_memory (save_id, task_type, task_data, priority)
            VALUES (?, ?, ?, ?)
        """, (self.save_id, task_type, json.dumps(task_data, ensure_ascii=False), priority))
        
        conn.commit()
        conn.close()
    
    def get_working_memory(self, task_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get current working memory (active tasks)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if task_type:
            cursor.execute("""
                SELECT task_type, task_data, priority, created_at
                FROM working_memory
                WHERE save_id = ? AND task_type = ? AND completed = FALSE
                ORDER BY priority DESC, created_at DESC
                LIMIT 1
            """, (self.save_id, task_type))
        else:
            cursor.execute("""
                SELECT task_type, task_data, priority, created_at
                FROM working_memory
                WHERE save_id = ? AND completed = FALSE
                ORDER BY priority DESC, created_at DESC
            """, (self.save_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "task_type": row[0],
                "task_data": json.loads(row[1]),
                "priority": row[2],
                "created_at": row[3]
            })
        
        conn.close()
        return results
    
    def complete_working_memory(self, task_type: str):
        """Mark working memory task as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE working_memory
            SET completed = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE save_id = ? AND task_type = ? AND completed = FALSE
        """, (self.save_id, task_type))
        
        conn.commit()
        conn.close()
    
    def get_working_memory_context(self) -> str:
        """Get working memory as context string for AI"""
        tasks = self.get_working_memory()
        
        if not tasks:
            return "Không có nhiệm vụ hiện tại."
        
        context_parts = ["Nhiệm vụ hiện tại:"]
        for task in tasks:
            task_type = task["task_type"]
            task_data = task["task_data"]
            priority = task["priority"]
            context_parts.append(f"- {task_type} (Ưu tiên {priority}): {json.dumps(task_data, ensure_ascii=False)}")
        
        return "\n".join(context_parts)
    
    # --- LONG-TERM MEMORY (SQLite FTS5) ---
    
    def add_long_term(
        self,
        content: str,
        memory_type: str = "episodic",
        importance: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Thêm vào long-term memory (FTS5)
        
        Returns:
            memory_id
        """
        memory_id = f"{self.save_id}_{uuid.uuid4().hex}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO long_term_memory_metadata 
            (memory_id, save_id, content, memory_type, importance, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            memory_id,
            self.save_id,
            content,
            memory_type,
            importance,
            json.dumps(metadata or {}, ensure_ascii=False) if metadata else None
        ))
        
        # Trigger sẽ tự động insert vào FTS5
        
        conn.commit()
        conn.close()
        
        return memory_id
    
    def search_long_term(
        self,
        query: str,
        limit: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search long-term memory using FTS5
        
        Returns:
            List of memories with relevance scores
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        fts_query = f'"{query}"'
        if memory_type:
            fts_query += f' AND memory_type:"{memory_type}"'
        
        # FTS5 search with BM25 ranking
        cursor.execute("""
            SELECT 
                ltm.memory_id,
                ltm.content,
                ltm.memory_type,
                ltm.importance,
                ltm.last_accessed,
                bm25(long_term_memory_fts) as score
            FROM long_term_memory_fts
            JOIN long_term_memory_metadata ltm ON long_term_memory_fts.memory_id = ltm.memory_id
            WHERE long_term_memory_fts MATCH ? AND ltm.save_id = ?
            ORDER BY bm25(long_term_memory_fts) ASC, ltm.importance DESC
            LIMIT ?
        """, (fts_query, self.save_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "memory_id": row[0],
                "content": row[1],
                "memory_type": row[2],
                "importance": row[3],
                "last_accessed": row[4],
                "relevance_score": row[5]
            })
            
            # Update access count
            cursor.execute("""
                UPDATE long_term_memory_metadata
                SET last_accessed = CURRENT_TIMESTAMP, access_count = access_count + 1
                WHERE memory_id = ?
            """, (row[0],))
        
        conn.commit()
        conn.close()
        
        return results
    
    def get_long_term_context(self, query: str, limit: int = 5) -> str:
        """Get long-term memory as context string for AI"""
        memories = self.search_long_term(query, limit=limit)
        
        if not memories:
            return "Không có ký ức liên quan."
        
        context_parts = ["Ký ức liên quan:"]
        for mem in memories:
            context_parts.append(f"- {mem['content']} (Quan trọng: {mem['importance']:.1f})")
        
        return "\n".join(context_parts)
    
    # --- ROLLING SUMMARY ---
    
    def create_rolling_summary(
        self,
        period_start: datetime,
        period_end: datetime,
        summary_text: str
    ):
        """
        Tạo rolling summary từ short-term memory
        
        Được gọi khi short-term memory đầy hoặc định kỳ
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO rolling_summary (save_id, summary_text, period_start, period_end)
            VALUES (?, ?, ?, ?)
        """, (
            self.save_id,
            summary_text,
            period_start.isoformat(),
            period_end.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_summary(self) -> Optional[Dict[str, Any]]:
        """Get latest rolling summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT summary_text, period_start, period_end, created_at
            FROM rolling_summary
            WHERE save_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (self.save_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "summary_text": row[0],
                "period_start": row[1],
                "period_end": row[2],
                "created_at": row[3]
            }
        
        return None
    
    # --- ROLLOVER LOGIC ---
    
    def _rollover_to_long_term(self, short_term_entry: Dict[str, Any]):
        """
        Chuyển short-term memory vào long-term khi đầy
        
        Có thể gọi AI để tạo summary trước khi lưu
        """
        content = short_term_entry.get("content", "")
        speaker = short_term_entry.get("speaker", "unknown")
        
        # Determine importance based on content
        importance = 0.5
        if any(keyword in content.lower() for keyword in ["chết", "tử", "giết", "thắng", "thất bại"]):
            importance = 0.8
        elif any(keyword in content.lower() for keyword in ["đột phá", "cảnh giới", "tông môn"]):
            importance = 0.7
        
        # Add to long-term
        self.add_long_term(
            content=f"{speaker}: {content}",
            memory_type="episodic",
            importance=importance,
            metadata=short_term_entry.get("metadata", {})
        )
    
    def trigger_rolling_summary(self, ai_summarizer=None):
        """
        Trigger rolling summary creation
        
        Nếu có AI summarizer, dùng AI để tạo summary
        Nếu không, tạo summary đơn giản
        """
        if len(self.short_term_memory) < 10:
            return  # Chưa đủ để tạo summary
        
        # Get period
        period_start = datetime.fromisoformat(self.short_term_memory[0]["timestamp"])
        period_end = datetime.fromisoformat(self.short_term_memory[-1]["timestamp"])
        
        # Create summary
        if ai_summarizer:
            # Use AI to create summary
            conversations = [f"{e['speaker']}: {e['content']}" for e in self.short_term_memory]
            summary = ai_summarizer.create_summary(conversations)
        else:
            # Simple summary
            summary = f"Tóm tắt {len(self.short_term_memory)} cuộc hội thoại từ {period_start.date()} đến {period_end.date()}"
        
        # Create rolling summary
        self.create_rolling_summary(period_start, period_end, summary)
        
        # Clear short-term (đã được summarize)
        self.short_term_memory = []
    
    # --- COMPREHENSIVE CONTEXT ---
    
    def get_full_context(self, query: Optional[str] = None) -> str:
        """
        Get full context từ cả 3 tiers cho AI prompt
        
        Returns:
            Combined context string
        """
        context_parts = []
        
        # 1. Latest summary
        summary = self.get_latest_summary()
        if summary:
            context_parts.append(f"=== TÓM TẮT GẦN ĐÂY ===\n{summary['summary_text']}\n")
        
        # 2. Working memory
        working = self.get_working_memory_context()
        context_parts.append(f"=== NHIỆM VỤ HIỆN TẠI ===\n{working}\n")
        
        # 3. Short-term (recent conversations)
        short_term = self.get_short_term_context()
        context_parts.append(f"=== HỘI THOẠI GẦN ĐÂY ===\n{short_term}\n")
        
        # 4. Long-term (relevant memories)
        if query:
            long_term = self.get_long_term_context(query, limit=5)
            context_parts.append(f"=== KÝ ỨC LIÊN QUAN ===\n{long_term}\n")
        
        return "\n".join(context_parts)

