# Feature1Analysis Schema Migration Guide

## Overview

This guide documents the database schema changes for Feature 1 Lens Engine Hardening (Task 2).

## Changes Made

### New Fields Added to `Feature1Analysis` Model

1. **`ai_recommendations_json`** (TEXT, default: `"[]"`)
   - Stores Gemini-powered AI coaching recommendations
   - JSON array of natural language coaching points
   - Maximum 5 recommendations per analysis
   - Requirements: 1.5, 3.1

2. **`raw_resume_text`** (TEXT, default: `""`)
   - Stores raw extracted resume text for cross-feature reuse
   - Maximum 8000 characters (truncated if longer)
   - Enables Feature 5 consistency checks
   - Requirements: 3.1, 3.2

## Migration Instructions

### For New Installations

No migration needed. The database will be created with the new schema automatically when running:

```bash
python -c "from app.db import create_db_and_tables; create_db_and_tables()"
```

### For Existing Databases

Run the migration script to add the new columns:

```bash
cd Backend
python migrate_feature1_schema.py
```

The script will:
- Check if columns already exist
- Add missing columns with default values
- Verify the migration was successful
- Preserve all existing data

### Migration Script Output

```
Adding ai_recommendations_json column...
Adding raw_resume_text column...

✓ Migration completed successfully!
  Added columns: ai_recommendations_json, raw_resume_text

✓ Migration verified successfully!
```

## Backward Compatibility

### Guaranteed Compatibility

✓ **Existing analyses continue to work** - All existing records automatically get default values:
  - `ai_recommendations_json = "[]"`
  - `raw_resume_text = ""`

✓ **Existing queries work unchanged** - All SELECT, INSERT, UPDATE queries continue to function

✓ **API responses remain compatible** - New fields are optional in responses

✓ **No data loss** - Migration is non-destructive and reversible

### Testing

Comprehensive unit tests verify backward compatibility:

```bash
cd Backend
python -m pytest tests/test_feature1_models.py -v
```

**Test Coverage:**
- Default value handling for new fields
- AI recommendations storage and retrieval
- Raw resume text storage and retrieval
- Text truncation to 8000 characters
- Backward compatible queries
- Empty value parsing
- Both fields populated simultaneously
- Timestamp handling

**All 8 tests pass ✓**

## Database Schema

### Before Migration

```sql
CREATE TABLE feature1analysis (
    id INTEGER PRIMARY KEY,
    candidate_id TEXT,
    job_category TEXT,
    resume_filename TEXT,
    resume_path TEXT,
    version_number INTEGER,
    overall_score REAL,
    visual_score REAL,
    ats_score REAL,
    semantic_score REAL,
    benchmark_score REAL,
    eye_tracking_summary TEXT,
    ats_summary TEXT,
    semantic_summary TEXT,
    benchmark_summary TEXT,
    hotzones_json TEXT,
    metrics_json TEXT,
    recommendations_json TEXT,
    created_at TIMESTAMP
);
```

### After Migration

```sql
CREATE TABLE feature1analysis (
    id INTEGER PRIMARY KEY,
    candidate_id TEXT,
    job_category TEXT,
    resume_filename TEXT,
    resume_path TEXT,
    version_number INTEGER,
    overall_score REAL,
    visual_score REAL,
    ats_score REAL,
    semantic_score REAL,
    benchmark_score REAL,
    eye_tracking_summary TEXT,
    ats_summary TEXT,
    semantic_summary TEXT,
    benchmark_summary TEXT,
    hotzones_json TEXT,
    metrics_json TEXT,
    recommendations_json TEXT,
    ai_recommendations_json TEXT DEFAULT '[]',  -- NEW
    raw_resume_text TEXT DEFAULT '',            -- NEW
    created_at TIMESTAMP
);
```

## Rollback Instructions

If you need to rollback the migration (not recommended):

```sql
-- Connect to the database
sqlite3 data/career_os.db

-- Remove the new columns (SQLite doesn't support DROP COLUMN directly)
-- You would need to recreate the table without these columns
-- This is complex and not recommended unless absolutely necessary
```

**Note:** Rollback is not recommended as it will lose any AI recommendations and raw text data stored after migration.

## Verification

After migration, verify the changes:

```python
from app.db import get_session
from app.models import Feature1Analysis
from sqlmodel import select

session = next(get_session())
analyses = session.exec(select(Feature1Analysis)).all()

# Check that all analyses have the new fields
for analysis in analyses:
    assert hasattr(analysis, 'ai_recommendations_json')
    assert hasattr(analysis, 'raw_resume_text')
    assert analysis.ai_recommendations_json == "[]"  # Default value
    assert analysis.raw_resume_text == ""            # Default value

print("✓ Migration verified successfully!")
```

## Next Steps

After successful migration:

1. ✓ Database schema updated
2. ✓ Backward compatibility verified
3. → Continue with Task 3: Implement LRU resume text caching
4. → Continue with Task 5: Enhance Feature1Engine with Gemini AI recommendations

## Support

If you encounter issues during migration:

1. Check that the database file exists at `Backend/data/career_os.db`
2. Ensure you have write permissions to the database file
3. Verify SQLite version supports ALTER TABLE ADD COLUMN
4. Review migration script output for error messages
5. Run the test suite to verify database integrity

## References

- **Spec:** `.kiro/specs/feature1-lens-hardening/`
- **Requirements:** `requirements.md` (1.5, 3.1, 3.2)
- **Design:** `design.md` (Database Schema Modifications section)
- **Tasks:** `tasks.md` (Task 2)
- **Tests:** `Backend/tests/test_feature1_models.py`
- **Migration Script:** `Backend/migrate_feature1_schema.py`
