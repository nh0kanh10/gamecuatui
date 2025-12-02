"""
Database Layer - SQLite wrapper for component storage
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Type
from contextlib import contextmanager

from .components import COMPONENT_REGISTRY, get_component_class
from pydantic import BaseModel


class Database:
    """SQLite database manager for ECS"""
    
    def __init__(self, db_path: str = "data/world.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Create tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Entities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Components table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS components (
                    entity_id INTEGER NOT NULL,
                    component_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    PRIMARY KEY (entity_id, component_type),
                    FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_components_entity 
                ON components(entity_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_components_type 
                ON components(component_type)
            """)
    
    def create_entity(self, label: str = "") -> int:
        """Create a new entity and return its ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO entities (label) VALUES (?)", (label,))
            return cursor.lastrowid
    
    def delete_entity(self, entity_id: int):
        """Delete an entity and all its components"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
    
    def add_component(self, entity_id: int, component: BaseModel):
        """Add or update a component for an entity"""
        component_type = self._get_component_type(component)
        data_json = component.model_dump_json()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO components (entity_id, component_type, data)
                VALUES (?, ?, ?)
            """, (entity_id, component_type, data_json))
    
    def get_component(self, entity_id: int, component_class: Type[BaseModel]) -> Optional[BaseModel]:
        """Get a specific component from an entity"""
        component_type = self._class_to_type(component_class)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data FROM components
                WHERE entity_id = ? AND component_type = ?
            """, (entity_id, component_type))
            
            row = cursor.fetchone()
            if row:
                return component_class.model_validate_json(row['data'])
            return None
    
    def remove_component(self, entity_id: int, component_class: Type[BaseModel]):
        """Remove a component from an entity"""
        component_type = self._class_to_type(component_class)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM components
                WHERE entity_id = ? AND component_type = ?
            """, (entity_id, component_type))
    
    def get_all_components(self, entity_id: int) -> Dict[str, BaseModel]:
        """Get all components for an entity"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT component_type, data FROM components
                WHERE entity_id = ?
            """, (entity_id,))
            
            components = {}
            for row in cursor.fetchall():
                comp_type = row['component_type']
                comp_class = get_component_class(comp_type)
                if comp_class:
                    components[comp_type] = comp_class.model_validate_json(row['data'])
            
            return components
    
    def find_entities_with_component(self, component_class: Type[BaseModel]) -> List[int]:
        """Find all entity IDs that have a specific component"""
        component_type = self._class_to_type(component_class)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT entity_id FROM components
                WHERE component_type = ?
            """, (component_type,))
            
            return [row['entity_id'] for row in cursor.fetchall()]
    
    def find_entities_at_location(self, room_id: str) -> List[int]:
        """Find all entities in a specific room"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT entity_id FROM components
                WHERE component_type = 'location'
                AND json_extract(data, '$.room_id') = ?
            """, (room_id,))
            
            return [row['entity_id'] for row in cursor.fetchall()]
    
    def entity_exists(self, entity_id: int) -> bool:
        """Check if an entity exists"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM entities WHERE id = ?", (entity_id,))
            return cursor.fetchone() is not None
    
    def _get_component_type(self, component: BaseModel) -> str:
        """Get component type string from component instance"""
        class_name = component.__class__.__name__
        # Remove 'Component' suffix and lowercase
        return class_name.replace('Component', '').lower()
    
    def _class_to_type(self, component_class: Type[BaseModel]) -> str:
        """Convert component class to type string"""
        class_name = component_class.__name__
        return class_name.replace('Component', '').lower()
    
    def dump_all(self) -> Dict[str, Any]:
        """Dump entire database for save/backup"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all entities
            cursor.execute("SELECT id, label FROM entities")
            entities = {row['id']: row['label'] for row in cursor.fetchall()}
            
            # Get all components
            cursor.execute("SELECT entity_id, component_type, data FROM components")
            components = {}
            for row in cursor.fetchall():
                entity_id = row['entity_id']
                if entity_id not in components:
                    components[entity_id] = {}
                components[entity_id][row['component_type']] = json.loads(row['data'])
            
            return {
                "entities": entities,
                "components": components
            }
    
    def restore_all(self, data: Dict[str, Any]):
        """Restore database from dump"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM components")
            cursor.execute("DELETE FROM entities")
            
            # Restore entities
            for entity_id, label in data['entities'].items():
                cursor.execute("""
                    INSERT INTO entities (id, label) VALUES (?, ?)
                """, (entity_id, label))
            
            # Restore components
            for entity_id, comps in data['components'].items():
                for comp_type, comp_data in comps.items():
                    cursor.execute("""
                        INSERT INTO components (entity_id, component_type, data)
                        VALUES (?, ?, ?)
                    """, (entity_id, comp_type, json.dumps(comp_data)))


# Global database instance
_db = None

def get_db(db_path: str = "data/world.db") -> Database:
    """Get or create global database instance"""
    global _db
    if _db is None:
        _db = Database(db_path)
    return _db
