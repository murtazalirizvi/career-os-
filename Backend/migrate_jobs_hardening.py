#!/usr/bin/env python3
"""
Database migration script for Job Tracker Hardening (Chunk 7).

Adds the following columns to the job table:
- notes_history: Append-only notes log with timestamps (7.2)
- contact_name: Contact person name (7.3)
- contact_email: Contact person email (7.3)
- job_url: URL of the job posting (7.3)
- priority: Job priority level High/Medium/Low (7.5)
- next_action_date: Date for follow-up action (7.6)

This migration is idempotent and safe to run multiple times.
"""

import sqlite3
import sys
from pathlib import Path


def migrate_jobs_hardening(db_path: str = "data/career_os.db") -> None:
    print(f"Starting Jobs hardening migration on: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(job)")
        columns = {row[1] for row in cursor.fetchall()}
        print(f"Existing columns: {sorted(columns)}")

        changes_made = False

        new_columns = [
            ("notes_history", "TEXT DEFAULT '[]'"),
            ("contact_name", "TEXT DEFAULT ''"),
            ("contact_email", "TEXT DEFAULT ''"),
            ("job_url", "TEXT DEFAULT ''"),
            ("priority", "TEXT DEFAULT 'Medium'"),
            ("next_action_date", "TEXT"),
        ]

        for col_name, col_def in new_columns:
            if col_name not in columns:
                print(f"Adding {col_name} column...")
                cursor.execute(f"ALTER TABLE job ADD COLUMN {col_name} {col_def}")
                print(f"✓ {col_name} column added")
                changes_made = True
            else:
                print(f"✓ {col_name} column already exists")

        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_priority ON job(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_next_action_date ON job(next_action_date)")
        print("✓ Indexes ensured")

        conn.commit()

        # Verify
        cursor.execute("PRAGMA table_info(job)")
        final = {row[1] for row in cursor.fetchall()}
        required = {"notes_history", "contact_name", "contact_email", "job_url", "priority", "next_action_date"}
        missing = required - final
        if missing:
            print(f"✗ Missing columns: {missing}")
            sys.exit(1)

        print(f"\n✓ Migration completed successfully!")
        if changes_made:
            print("  Changes were applied.")
        else:
            print("  No changes needed — already applied.")

    except sqlite3.Error as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/career_os.db"
    if not Path(db_path).exists():
        print(f"✗ Database file not found: {db_path}")
        sys.exit(1)
    migrate_jobs_hardening(db_path)
