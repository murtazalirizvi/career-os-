#!/usr/bin/env python3
"""
Database migration script for Feature 5 Narrative Architect Hardening (Chunk 6).

Adds the following columns to feature5narrativesession table:
- resume_text: Persisted resume text for re-runs (6.4)
- jd_text: Persisted JD text for re-runs (6.6)

This migration is idempotent and safe to run multiple times.
"""

import sqlite3
import sys
from pathlib import Path


def migrate_feature5_hardening(db_path: str = "data/career_os.db") -> None:
    print(f"Starting Feature 5 hardening migration on: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(feature5narrativesession)")
        columns = {row[1] for row in cursor.fetchall()}
        print(f"Existing columns: {sorted(columns)}")

        changes_made = False

        if "resume_text" not in columns:
            print("Adding resume_text column...")
            cursor.execute("""
                ALTER TABLE feature5narrativesession
                ADD COLUMN resume_text TEXT DEFAULT ''
            """)
            print("✓ resume_text column added")
            changes_made = True
        else:
            print("✓ resume_text column already exists")

        if "jd_text" not in columns:
            print("Adding jd_text column...")
            cursor.execute("""
                ALTER TABLE feature5narrativesession
                ADD COLUMN jd_text TEXT DEFAULT ''
            """)
            print("✓ jd_text column added")
            changes_made = True
        else:
            print("✓ jd_text column already exists")

        conn.commit()

        # Verify
        cursor.execute("PRAGMA table_info(feature5narrativesession)")
        final = {row[1] for row in cursor.fetchall()}
        required = {"resume_text", "jd_text"}
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
    migrate_feature5_hardening(db_path)
