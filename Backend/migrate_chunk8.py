#!/usr/bin/env python3
"""
Database migration script for Chunk 8 — Cross-Feature & Infrastructure.

Adds the following:
- userprofile table: target_role, years_experience, current_skills_json (8.2)

This migration is idempotent and safe to run multiple times.
"""

import sqlite3
import sys
from pathlib import Path


def migrate_chunk8(db_path: str = "data/career_os.db") -> None:
    print(f"Starting Chunk 8 infrastructure migration on: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # ── UserProfile table (8.2) ───────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS userprofile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE REFERENCES useraccount(id),
                candidate_id TEXT NOT NULL,
                target_role TEXT DEFAULT '',
                years_experience REAL DEFAULT 0.0,
                current_skills_json TEXT DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_userprofile_user_id ON userprofile(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_userprofile_candidate_id ON userprofile(candidate_id)")
        print("✓ userprofile table ensured")

        conn.commit()
        print("\n✓ Chunk 8 migration completed successfully!")

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
    migrate_chunk8(db_path)
