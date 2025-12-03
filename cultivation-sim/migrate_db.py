"""
Migration script to add attributes_json column to existing databases
"""
import sqlite3
from pathlib import Path

# Find all database files
db_dir = Path("data/saves")
if db_dir.exists():
    for db_file in db_dir.glob("*.db"):
        print(f"Migrating {db_file}...")
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Check if column exists
            cursor.execute("PRAGMA table_info(game_state)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'attributes_json' not in columns:
                # Add the missing column
                cursor.execute("ALTER TABLE game_state ADD COLUMN attributes_json TEXT")
                conn.commit()
                print(f"  ✅ Added attributes_json column")
            else:
                print(f"  ℹ️  Column already exists")
            
            conn.close()
        except Exception as e:
            print(f"  ❌ Error: {e}")

print("\n✅ Migration complete!")
