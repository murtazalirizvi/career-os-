#!/usr/bin/env python3
"""
Fix missing ai_insights_json column from Chunk 1.
This should have been added before Chunk 3.
"""

import sqlite3
import sys
from pathlib import Path


def fix_missing_column(db_path: str = "Backend/data/career_os.db") -> None:
    """Add ai_insights_json column if missing."""
    print(f"Checking database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(feature2interviewautopsy)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if "ai_insights_json" not in columns:
            print("Adding missing ai_insights_json column...")
            cursor.execute("""
                ALTER TABLE feature2interviewautopsy 
                ADD COLUMN ai_insights_json TEXT DEFAULT '{}'
            """)
            conn.commit()
            print("✓ ai_insights_json column added")
        else:
            print("✓ ai_insights_json column already exists")
        
        # Verify
        cursor.execute("PRAGMA table_info(feature2interviewautopsy)")
        columns = {row[1] for row in cursor.fetchall()}
        
        if "ai_insights_json" in columns:
            print("✓ Verification successful")
        else:
            print("✗ Verification failed")
            sys.exit(1)
            
    except sqlite3.Error as e:
        print(f"✗ Error: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "Backend/data/career_os.db"
    
    if not Path(db_path).exists():
        print(f"✗ Database file not found: {db_path}")
        sys.exit(1)
    
    fix_missing_column(db_path)
