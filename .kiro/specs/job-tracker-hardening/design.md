# Design Document: Job Tracker Hardening

## Overview

Six enhancements to the Job Tracker: pipeline stats, append-only notes history, CRM fields (contact/email/URL), CSV export, priority field, and next-action date with due-today endpoint.

## New Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/jobs/stats` | Pipeline counts by status and priority (7.1) |
| POST | `/api/jobs/{id}/notes` | Append timestamped note to history (7.2) |
| GET | `/api/jobs/export` | Download CSV of all jobs (7.4) |
| GET | `/api/jobs/due-today` | Jobs with next_action_date ≤ today (7.6) |

## Schema Changes

### Job Model (models_jobs.py)
```python
notes_history: str = Field(default="[]")        # JSON array of {note, timestamp}
contact_name: str = Field(default="")
contact_email: str = Field(default="")
job_url: str = Field(default="")
priority: str = Field(default="Medium", index=True)
next_action_date: Optional[date] = Field(default=None, index=True)
```

### New Enum
```python
class JobPriority(str, enum.Enum):
    high = "High"
    medium = "Medium"
    low = "Low"
```

### Updated Schemas
- `JobCreate` / `JobUpdate`: include all 6 new fields
- `JobRead`: includes all 6 new fields; `notes_history` returned as `List[Dict]`
- `JobStatsResponse`: `{total, by_status, by_priority}`
- `JobAppendNoteRequest`: `{note: str}`

## Notes History Format

```json
[
  {"note": "Applied via LinkedIn", "timestamp": "2026-04-19T10:30:00+00:00"},
  {"note": "Recruiter called, moving to tech round", "timestamp": "2026-04-22T14:00:00+00:00"}
]
```

## Migration Script

`Backend/migrate_jobs_hardening.py` — adds all 6 columns to the `job` table with appropriate defaults and indexes. Idempotent.

## Route Ordering Note

FastAPI matches routes in registration order. `/stats`, `/export`, and `/due-today` are registered **before** `/{job_id}` to prevent them being captured as job ID parameters.
