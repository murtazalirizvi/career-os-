#!/usr/bin/env python3
"""
Database migration script for Feature 3 Skill Arbitrage Hardening enhancements.

Adds the following columns:
  feature3marketsnapshot:
    - salary_currency: Currency for salary data (USD|PKR|GBP)
    - market_commentary_json: Gemini-generated market insights
  feature3gapsnapshot (Chunk 1 backfill):
    - ai_learning_path_json: Gemini-generated learning path
  feature4mocksession (Chunk 1 backfill):
    - ai_coaching_report_json: Gemini-generated coaching report

This migration is idempotent and safe to run multiple times.
"""

import sqlite3
import sys
from pathlib import Path


def migrate_feature3_hardening(db_path: str = "data/career_os.db") -> None:
    """
    Idempotent migration covering:
    - feature3marketsnapshot: salary_currency, market_commentary_json (Chunk 4)
    - feature3gapsnapshot: ai_learning_path_json (Chunk 1 backfill)
    - feature4mocksession: ai_coaching_report_json (Chunk 1 backfill)
    """
    print(f"Starting Feature 3 hardening migration on: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        changes_made = False

        # ── feature3marketsnapshot ────────────────────────────────────────────
        cursor.execute("PRAGMA table_info(feature3marketsnapshot)")
        columns = {row[1] for row in cursor.fetchall()}
        print(f"\nfeature3marketsnapshot columns: {sorted(columns)}")

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

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feature3_salary_currency 
            ON feature3marketsnapshot(salary_currency)
        """)
        print("✓ Index idx_feature3_salary_currency ensured")

        # ── feature3gapsnapshot (Chunk 1 backfill) ───────────────────────────
        cursor.execute("PRAGMA table_info(feature3gapsnapshot)")
        gap_columns = {row[1] for row in cursor.fetchall()}
        print(f"\nfeature3gapsnapshot columns: {sorted(gap_columns)}")

        if "ai_learning_path_json" not in gap_columns:
            print("Adding ai_learning_path_json column to feature3gapsnapshot...")
            cursor.execute("""
                ALTER TABLE feature3gapsnapshot 
                ADD COLUMN ai_learning_path_json TEXT DEFAULT '{}'
            """)
            print("✓ ai_learning_path_json column added")
            changes_made = True
        else:
            print("✓ ai_learning_path_json column already exists")

        # ── feature4mocksession (Chunk 1 backfill) ───────────────────────────
        cursor.execute("PRAGMA table_info(feature4mocksession)")
        session_columns = {row[1] for row in cursor.fetchall()}
        print(f"\nfeature4mocksession columns: {sorted(session_columns)}")

        if "ai_coaching_report_json" not in session_columns:
            print("Adding ai_coaching_report_json column to feature4mocksession...")
            cursor.execute("""
                ALTER TABLE feature4mocksession 
                ADD COLUMN ai_coaching_report_json TEXT DEFAULT '{}'
            """)
            print("✓ ai_coaching_report_json column added")
            changes_made = True
        else:
            print("✓ ai_coaching_report_json column already exists")

        # ── Commit ────────────────────────────────────────────────────────────
        conn.commit()

        # ── Verify ────────────────────────────────────────────────────────────
        print("\nVerifying migration...")

        cursor.execute("PRAGMA table_info(feature3marketsnapshot)")
        final_market = {row[1] for row in cursor.fetchall()}
        cursor.execute("PRAGMA table_info(feature3gapsnapshot)")
        final_gap = {row[1] for row in cursor.fetchall()}
        cursor.execute("PRAGMA table_info(feature4mocksession)")
        final_session = {row[1] for row in cursor.fetchall()}

        required = {
            "feature3marketsnapshot": {"salary_currency", "market_commentary_json"},
            "feature3gapsnapshot": {"ai_learning_path_json"},
            "feature4mocksession": {"ai_coaching_report_json"},
        }
        actuals = {
            "feature3marketsnapshot": final_market,
            "feature3gapsnapshot": final_gap,
            "feature4mocksession": final_session,
        }

        all_ok = True
        for table, needed in required.items():
            missing = needed - actuals[table]
            if missing:
                print(f"✗ {table}: missing columns {missing}")
                all_ok = False
            else:
                print(f"✓ {table}: all required columns present")

        if not all_ok:
            sys.exit(1)

        print(f"\n✓ Migration completed successfully!")
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
