#!/usr/bin/env python3
"""
Database migration script for Feature 4 Persona Coach Hardening (Chunk 5).

Adds the following columns to feature4mocksession table:
- target_company: Company name for tailored interview questions
- language: Session language (english|hinglish) — already stored in config_json
  but now a first-class indexed field for filtering

Note: ai_coaching_report_json was already added by migrate_feature3_hardening.py

This migration is idempotent and safe to run multiple times.
"""

import sqlite3
import sys
from pathlib import Path


def migrate_feature4_hardening(db_path: str = "data/career_os.db") -> None:
    print(f"Starting Feature 4 hardening migration on: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(feature4mocksession)")
        columns = {row[1] for row in cursor.fetchall()}
        print(f"Existing columns: {sorted(columns)}")

        changes_made = False

        if "target_company" not in columns:
            print("Adding target_company column...")
            cursor.execute("""
                ALTER TABLE feature4mocksession
                ADD COLUMN target_company TEXT DEFAULT ''
            """)
            print("✓ target_company column added")
            changes_made = True
        else:
            print("✓ target_company column already exists")

        if "language" not in columns:
            print("Adding language column...")
            cursor.execute("""
                ALTER TABLE feature4mocksession
                ADD COLUMN language TEXT DEFAULT 'english'
            """)
            print("✓ language column added")
            changes_made = True
        else:
            print("✓ language column already exists")

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feature4_target_company
            ON feature4mocksession(target_company)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feature4_language
            ON feature4mocksession(language)
        """)
        print("✓ Indexes ensured")

        conn.commit()

        # Verify
        cursor.execute("PRAGMA table_info(feature4mocksession)")
        final = {row[1] for row in cursor.fetchall()}
        required = {"target_company", "language", "ai_coaching_report_json"}
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
    migrate_feature4_hardening(db_path)
