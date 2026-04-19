"""
Database migration script to add new fields to Feature1Analysis table.

This script adds:
- ai_recommendations_json (default: "[]")
- raw_resume_text (default: "")

These fields are required for Feature 1 Lens Engine Hardening enhancements.
"""

import sqlite3
from pathlib import Path

# Database path
ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
DATABASE_PATH = DATA_DIR / "career_os.db"

def migrate_database():
    """Add new columns to Feature1Analysis table if they don't exist."""
    
    if not DATABASE_PATH.exists():
        print(f"Database not found at {DATABASE_PATH}")
        print("No migration needed - database will be created with new schema")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(feature1analysis)")
        columns = [row[1] for row in cursor.fetchall()]
        
        migrations_applied = []
        
        # Add ai_recommendations_json if it doesn't exist
        if "ai_recommendations_json" not in columns:
            print("Adding ai_recommendations_json column...")
            cursor.execute("""
                ALTER TABLE feature1analysis 
                ADD COLUMN ai_recommendations_json TEXT DEFAULT '[]'
            """)
            migrations_applied.append("ai_recommendations_json")
        else:
            print("✓ ai_recommendations_json column already exists")
        
        # Add raw_resume_text if it doesn't exist
        if "raw_resume_text" not in columns:
            print("Adding raw_resume_text column...")
            cursor.execute("""
                ALTER TABLE feature1analysis 
                ADD COLUMN raw_resume_text TEXT DEFAULT ''
            """)
            migrations_applied.append("raw_resume_text")
        else:
            print("✓ raw_resume_text column already exists")
        
        # Commit changes
        conn.commit()
        
        if migrations_applied:
            print(f"\n✓ Migration completed successfully!")
            print(f"  Added columns: {', '.join(migrations_applied)}")
        else:
            print("\n✓ No migration needed - all columns already exist")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(feature1analysis)")
        columns = [row[1] for row in cursor.fetchall()]
        
        assert "ai_recommendations_json" in columns, "ai_recommendations_json column not found after migration"
        assert "raw_resume_text" in columns, "raw_resume_text column not found after migration"
        
        print("\n✓ Migration verified successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
