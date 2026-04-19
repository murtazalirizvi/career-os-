#!/usr/bin/env python3
"""
Database migration script for Feature 2 Rebound Hardening enhancements.

Adds the following columns to feature2interviewautopsy table:
- interview_date: Actual interview date (distinct from created_at)
- company_stage: Company maturity (startup|scaleup|enterprise)
- transcription_status: Status tracking for async transcription
- assembly_transcript_id: AssemblyAI transcript ID for webhook correlation

This migration is idempotent and safe to run multiple times.
"""

import sqlite3
import sys
from pathlib import Path


def migrate_feature2_hardening(db_path: str = "Backend/data/career_os.db") -> None:
    """
    Idempotent migration to add interview_date, company_stage,
    transcription_status, and assembly_transcript_id fields.
    """
    print(f"Starting Feature 2 hardening migration on: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(feature2interviewautopsy)")
        columns = {row[1] for row in cursor.fetchall()}
        print(f"Existing columns: {sorted(columns)}")
        
        changes_made = False
        
        # Add interview_date column
        if "interview_date" not in columns:
            print("Adding interview_date column...")
            # SQLite requires constant defaults, so we add nullable first then backfill
            cursor.execute("""
                ALTER TABLE feature2interviewautopsy 
                ADD COLUMN interview_date TEXT
            """)
            # Backfill with created_at for existing records
            cursor.execute("""
                UPDATE feature2interviewautopsy 
                SET interview_date = created_at 
                WHERE interview_date IS NULL
            """)
            print("✓ interview_date column added and backfilled from created_at")
            changes_made = True
        else:
            print("✓ interview_date column already exists")
        
        # Add company_stage column
        if "company_stage" not in columns:
            print("Adding company_stage column...")
            cursor.execute("""
                ALTER TABLE feature2interviewautopsy 
                ADD COLUMN company_stage TEXT DEFAULT 'scaleup'
            """)
            print("✓ company_stage column added with default 'scaleup'")
            changes_made = True
        else:
            print("✓ company_stage column already exists")
        
        # Add transcription_status column
        if "transcription_status" not in columns:
            print("Adding transcription_status column...")
            cursor.execute("""
                ALTER TABLE feature2interviewautopsy 
                ADD COLUMN transcription_status TEXT DEFAULT 'completed'
            """)
            print("✓ transcription_status column added with default 'completed'")
            changes_made = True
        else:
            print("✓ transcription_status column already exists")
        
        # Add assembly_transcript_id column
        if "assembly_transcript_id" not in columns:
            print("Adding assembly_transcript_id column...")
            cursor.execute("""
                ALTER TABLE feature2interviewautopsy 
                ADD COLUMN assembly_transcript_id TEXT
            """)
            print("✓ assembly_transcript_id column added")
            changes_made = True
        else:
            print("✓ assembly_transcript_id column already exists")
        
        # Create indexes
        print("\nCreating indexes...")
        
        indexes_to_create = [
            ("idx_feature2_interview_date", "interview_date"),
            ("idx_feature2_company_stage", "company_stage"),
            ("idx_feature2_transcription_status", "transcription_status"),
            ("idx_feature2_assembly_transcript_id", "assembly_transcript_id"),
        ]
        
        for index_name, column_name in indexes_to_create:
            try:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {index_name} 
                    ON feature2interviewautopsy({column_name})
                """)
                print(f"✓ Index {index_name} created")
            except sqlite3.Error as e:
                print(f"⚠ Index {index_name} creation warning: {e}")
        
        # Commit all changes
        conn.commit()
        
        # Verify migration
        print("\nVerifying migration...")
        cursor.execute("PRAGMA table_info(feature2interviewautopsy)")
        final_columns = {row[1] for row in cursor.fetchall()}
        
        required_columns = {"interview_date", "company_stage", "transcription_status", "assembly_transcript_id"}
        missing = required_columns - final_columns
        
        if missing:
            print(f"✗ Migration incomplete. Missing columns: {missing}")
            sys.exit(1)
        else:
            print("✓ All required columns present")
        
        # Verify indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='feature2interviewautopsy'")
        indexes = {row[0] for row in cursor.fetchall()}
        print(f"✓ Indexes created: {sorted(indexes)}")
        
        # Count existing records
        cursor.execute("SELECT COUNT(*) FROM feature2interviewautopsy")
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
    db_path = sys.argv[1] if len(sys.argv) > 1 else "Backend/data/career_os.db"
    
    # Verify database file exists
    if not Path(db_path).exists():
        print(f"✗ Database file not found: {db_path}")
        sys.exit(1)
    
    migrate_feature2_hardening(db_path)
