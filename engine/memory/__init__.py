"""
Memory package - Simple Memory System (SQLite FTS5)
Tuân thủ single-database architecture
"""
from .simple_memory import SimpleMemory, MemoryType, get_simple_memory
from .memory_manager_simple import SimpleMemoryManager, get_memory_manager
from .compression import CompressionRules

# Legacy imports (for backward compatibility, deprecated)
# VectorMemory requires ChromaDB which is not installed by default
try:
    from .vector_store import VectorMemory, get_vector_memory
except (ImportError, AttributeError):
    VectorMemory = None
    get_vector_memory = None

__all__ = [
    # Core Simple Memory System
    'SimpleMemory',
    'MemoryType',
    'get_simple_memory',
    'SimpleMemoryManager',
    'get_memory_manager',
    'CompressionRules',
    # Legacy (deprecated)
    'VectorMemory',
    'get_vector_memory'
]
