"""
Database for Cultivation Simulator
Standalone SQLite database
"""

import sqlite3
from pathlib import Path
from typing import Optional

_db_instances = {}


def get_db(db_path: str) -> sqlite3.Connection:
    """Get database connection (singleton per path)"""
    if db_path not in _db_instances:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        _db_instances[db_path] = conn
    return _db_instances[db_path]


def init_database(db_path: str):
    """Initialize database tables"""
    conn = get_db(db_path)
    cursor = conn.cursor()
    
    # Game state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_state (
                save_id TEXT PRIMARY KEY,
                age INTEGER DEFAULT 0,
                gender TEXT,
                talent TEXT,
                race TEXT,
                background TEXT,
                story TEXT,
                name TEXT,
                choices_json TEXT,
                cultivation_json TEXT,
                resources_json TEXT,
                attributes_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    # Memory tables (riêng cho cultivation sim)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_content (
            memory_id TEXT PRIMARY KEY,
            content TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id TEXT UNIQUE REFERENCES memory_content(memory_id),
            save_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            importance REAL DEFAULT 0.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            access_count INTEGER DEFAULT 0,
            metadata_json TEXT
        )
    """)
    
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
            memory_id UNINDEXED,
            content,
            memory_type,
            tokenize='porter'
        )
    """)
    
    # Trigger to sync FTS5
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS memory_content_ai 
        AFTER INSERT ON memory_content
        BEGIN
            INSERT INTO memory_fts(memory_id, content, memory_type)
            VALUES (
                NEW.memory_id,
                NEW.content,
                COALESCE((SELECT memory_type FROM memory_metadata WHERE memory_id = NEW.memory_id), 'episodic')
            );
        END;
    """)
    
    conn.commit()

