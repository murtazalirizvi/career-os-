#!/usr/bin/env python3
"""
Database migration script for Feature 3 Skill Arbitrage Hardening enhancements.

Adds the following columns to feature3marketsnapshot table:
- salary_currency: Currency for salary data (USD|PKR|GBP)
- market_commentary_json: Gemini-generated market insights

This migration is idempotent and safe to run multiple times.
"""

import sqlite3
import sys
from pathlib import Path


def migrate_feature3_hardening(db_path: str = "data/career_os.db") -> None:
    """
    Idempotent migration to add salary_currency and market_commentary_json fields.
    """
    print(f"Starting Feature 3 hardening migration on: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(feature3marketsnapshot)")
        columns = {row[1] for row in cursor.fetchall()}
        print(f"Existing columns: {sorted(columns)}")
        
        changes_made = False
        
        # Add salary_currency column
        if "salary_currency" not in columns:
            print("Adding salary_currency column...")
            cursor.execute("""
                ALTER TABLE feature3marketsnapshot 
                ADD COLUMN salary_currency TEXT DEFAULT 'USD'
            """)
            print("✓ salary_currency column added with default 'USD'")
            changes_made = True
        else:
            print("✓ salary_currency column already exists")
        
        # Add market_commentary_json column
        if "market_commentary_json" not in columns:
            print("Adding market_commentary_json column...")
            cursor.execute("""
                ALTER TABLE feature3marketsnapshot 
                ADD COLUMN market_commentary_json TEXT DEFAULT '{}'
            """)
            print("✓ market_commentary_json column added with default '{}'")
            changes_made = True
        else:
            print("✓ market_commentary_json column already exists")
        
        # Create indexes
        print("\nCreating indexes...")
        
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feature3_salary_currency 
                ON feature3marketsnapshot(salary_currency)
            """)
            print("✓ Index idx_feature3_salary_currency created")
        except sqlite3.Error as e:
            print(f"⚠ Index idx_feature3_salary_currency creation warning: {e}")
        
        # Commit all changes
        conn.commit()
        
        # Verify migration
        print("\nVerifying migration...")
        cursor.execute("PRAGMA table_info(feature3marketsnapshot)")
        final_columns = {row[1] for row in cursor.fetchall()}
        
        required_columns = {"salary_currency", "market_commentary_json"}
        missing = required_columns - final_columns
        
        if missing:
            print(f"✗ Migration incomplete. Missing columns: {missing}")
            sys.exit(1)
        else:
            print("✓ All required columns present")
        
        # Verify indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='feature3marketsnapshot'")
        indexes = {row[0] for row in cursor.fetchall()}
        print(f"✓ Indexes created: {sorted(indexes)}")
        
        # Count existing records
        cursor.execute("SELECT COUNT(*) FROM feature3marketsnapshot")
        count = cursor.fetchone()[0]
        print(f"\n✓ Migration completed successfully!")
        print(f"  Total records in table: {count}")
        
        if changes_made:
            print("  Changes were applied to the database.")
        else:
            print("  No changes needed - migration was already applied.")
        
    except sqlite3.Error as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    # Support custom database path from command line
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/career_os.db"
    
    # Verify database file exists
    if not Path(db_path).exists():
        print(f"✗ Database file not found: {db_path}")
        sys.exit(1)
    
    migrate_feature3_hardening(db_path)
