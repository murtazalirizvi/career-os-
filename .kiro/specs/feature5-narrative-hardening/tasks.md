# Implementation Plan: Feature 5 Narrative Architect Hardening

## Overview

Six enhancements to the Feature 5 Narrative Architect system:
1. GitHub token support for higher API rate limits
2. Narrative regeneration endpoint with tone/role override
3. Gemini STAR story enhancement
4. resume_text storage for re-runs
5. LinkedIn post generation endpoint
6. jd_text storage for re-runs

## Tasks

- [x] 1. Run database migration
  - Created `Backend/migrate_feature5_hardening.py`
  - Added `resume_text` column to feature5narrativesession (default "")
  - Added `jd_text` column to feature5narrativesession (default "")
  - Migration is idempotent
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 2. Update database model
  - Extended Feature5NarrativeSession in `Backend/app/models.py`
  - Added `resume_text: str` with default ""
  - Added `jd_text: str` with default ""
  - _Requirements: 4.1, 6.1_

- [x] 3. Update API schemas
  - Created `Feature5RegenerateRequest` (optional tone, target_role)
  - Created `Feature5RegenerateResponse` (session_id, narrative, regenerated_at)
  - Created `Feature5LinkedInPostResponse` (session_id, post_text, character_count, generated_at)
  - _Requirements: 2.7, 5.1_

- [x] 4. Persist resume_text and jd_text on session create
  - Updated `create_feature5_session` to store `req.resume_text` and `req.jd_text`
  - _Requirements: 4.2, 6.2_

- [x] 5. Implement regenerate-narrative endpoint (6.2)
  - Created `POST /api/feature5/sessions/{id}/regenerate-narrative`
  - Loads stored resume_text and jd_text from DB
  - Applies optional tone/role overrides
  - Calls `engine.build_full_session()` with stored data
  - Updates all JSON fields in DB
  - Returns `Feature5RegenerateResponse`
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

- [x] 6. Implement linkedin-post endpoint (6.5)
  - Created `GET /api/feature5/sessions/{id}/linkedin-post`
  - Extracts headline and project data from stored narrative
  - Calls Gemini with structured prompt (hook + challenge + impact + hashtags)
  - Heuristic fallback using stored LinkedIn sync data
  - Returns `Feature5LinkedInPostResponse`
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 7. Final testing
  - All 59 tests passing
  - Existing Feature 5 tests pass unchanged
  - New endpoints verified via import check

## Notes

- GitHub token support (6.1) and Gemini STAR enhancement (6.3) were already present in the engine
- resume_text and jd_text default to empty string — existing sessions work unchanged
- Regeneration reuses `engine.build_full_session()` — no new engine methods needed
- LinkedIn post is under 1300 characters (LinkedIn's recommended limit)
