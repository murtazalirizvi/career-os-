# Implementation Plan: Job Tracker Hardening

## Overview

Six enhancements to the Job Tracker:
1. Pipeline stats endpoint
2. Append-only notes history
3. Core CRM fields (contact_name, contact_email, job_url)
4. CSV export endpoint
5. Priority field (High/Medium/Low)
6. Next action date + due-today endpoint

## Tasks

- [x] 1. Run database migration
  - Created `Backend/migrate_jobs_hardening.py`
  - Added notes_history (default "[]"), contact_name, contact_email, job_url (default ""),
    priority (default "Medium"), next_action_date (default NULL) to job table
  - Created indexes on priority and next_action_date
  - Migration is idempotent
  - _Requirements: 7.1–7.7_

- [x] 2. Update Job model
  - Extended Job in `Backend/app/models_jobs.py`
  - Added JobPriority enum (High/Medium/Low)
  - Added all 6 new fields with appropriate defaults and indexes
  - _Requirements: 2.1, 3.1, 5.1, 6.1_

- [x] 3. Update schemas
  - JobCreate and JobUpdate include all 6 new fields
  - JobRead returns notes_history as List[Dict] (parsed from JSON)
  - Added JobStatsResponse (total, by_status, by_priority)
  - Added JobAppendNoteRequest (note: str)
  - _Requirements: 2.5, 3.4, 4.3, 5.5_

- [x] 4. Implement stats endpoint (7.1)
  - Created GET /api/jobs/stats
  - Returns total count + breakdown by status and priority
  - Protected by bearer token auth
  - _Requirements: 1.1–1.6_

- [x] 5. Implement append-note endpoint (7.2)
  - Created POST /api/jobs/{id}/notes
  - Appends {note, timestamp} to notes_history JSON array
  - Never overwrites existing entries
  - Returns updated JobRead
  - _Requirements: 2.1–2.6_

- [x] 6. Add CRM fields to create/update (7.3)
  - contact_name, contact_email, job_url on JobCreate and JobUpdate
  - Stored in DB, returned in JobRead
  - Default to empty string when not provided
  - _Requirements: 3.1–3.5_

- [x] 7. Implement CSV export (7.4)
  - Created GET /api/jobs/export
  - Streams CSV with all job fields
  - Content-Disposition: attachment; filename=jobs_export.csv
  - _Requirements: 4.1–4.5_

- [x] 8. Add priority field (7.5)
  - JobPriority enum: High/Medium/Low
  - Default: Medium
  - Included in stats breakdown
  - _Requirements: 5.1–5.6_

- [x] 9. Implement due-today endpoint (7.6)
  - Created GET /api/jobs/due-today
  - Returns jobs where next_action_date <= today and is not null
  - _Requirements: 6.1–6.6_

- [x] 10. Final testing
  - All 59 tests passing
  - Existing job tracker tests pass unchanged

## Notes

- Routes /stats, /export, /due-today registered before /{job_id} to avoid FastAPI path conflicts
- notes_history is stored as JSON string in SQLite; parsed to List[Dict] in _job_to_read()
- priority stored as plain string (not enum) in DB for SQLite compatibility
- CSV export uses Python's built-in csv module, no extra dependencies
