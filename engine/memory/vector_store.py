"""
Vector Memory System (Legacy - Deprecated)
Stores and retrieves narrative history using ChromaDB

NOTE: This is deprecated. Use SimpleMemory (SQLite FTS5) instead.
"""

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None

import uuid
from typing import List, Dict, Any
from datetime import datetime

class VectorMemory:
    """Long-term memory using Vector Database (Legacy - Deprecated)"""
    
    def __init__(self, persist_path: str = "data/memory"):
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is not installed. "
                "This is a legacy module. Use SimpleMemory instead. "
                "If you need ChromaDB, install it: pip install chromadb"
            )
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name="game_narrative",
            metadata={"hnsw:space": "cosine"}
        )
        
    def add_memory(self, text: str, save_id: str, metadata: Dict[str, Any] = None):
        """Add a memory chunk"""
        if not text:
            return
            
        meta = metadata or {}
        meta['save_id'] = save_id
        meta['timestamp'] = datetime.now().isoformat()
        
        self.collection.add(
            documents=[text],
            metadatas=[meta],
            ids=[str(uuid.uuid4())]
        )
        
    def search_memory(self, query: str, save_id: str, n_results: int = 3) -> List[str]:
        """Search for relevant memories within a specific save slot"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"save_id": save_id} # Filter by save slot
        )
        
        if results and results['documents']:
            return results['documents'][0]
        return []

# Global instance - FIXED: Use unique name to avoid collision
_vector_memory = None

def get_vector_memory() -> VectorMemory:
    """Get or create global VectorMemory instance (legacy, deprecated)"""
    global _vector_memory
    if _vector_memory is None:
        _vector_memory = VectorMemory()
    return _vector_memory
