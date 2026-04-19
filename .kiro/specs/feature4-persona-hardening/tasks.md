# Implementation Plan: Feature 4 Persona Coach Hardening

## Overview

Six enhancements to the Feature 4 Persona-Play mock interview system:
1. AI coaching report persistence (Chunk 1 backfill — already in model)
2. Simplified text-only turn endpoint
3. Gemini-powered dynamic follow-up questions per turn
4. Target company field for tailored questions
5. Study guide endpoint from session transcript
6. Language enforcement in all Gemini prompts

## Tasks

- [x] 1. Run database migration
  - Created `Backend/migrate_feature4_hardening.py`
  - Added `target_company` column to feature4mocksession (default "")
  - Added `language` column to feature4mocksession (default "english")
  - Created indexes on both new fields
  - Migration is idempotent
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 2. Update database model
  - Extended Feature4MockSession in `Backend/app/models.py`
  - Added `target_company: str` with index
  - Added `language: str` with index
  - `ai_coaching_report_json` already present from Chunk 1
  - _Requirements: 4.1, 6.1, 1.1_

- [x] 3. Update API schemas
  - Added `target_company` to Feature4CreateSessionRequest
  - Added `target_company` and `language` to Feature4SessionResponse
  - Created `Feature4TurnTextRequest` (utterance only)
  - Created `Feature4StudyGuideResponse` (session_id, role_name, target_company, sections, generated_at)
  - _Requirements: 4.2, 4.5, 2.2, 5.1_

- [x] 4. Update Feature4Engine — language enforcement
  - `opening_questions()` accepts `target_company` and `language`
  - `_gemini_opening_questions()` includes company context and language instruction in prompt
  - `_gemini_coaching_report()` accepts `language`, includes instruction in prompt
  - `finalize_feedback()` accepts and passes `language`
  - _Requirements: 6.2, 6.3, 6.4_

- [x] 5. Update Feature4Engine — Gemini next_question
  - `next_question()` accepts `utterance`, `role_name`, `target_company`, `language`
  - Calls `_gemini_next_question()` first when Gemini available and utterance non-empty
  - `_gemini_next_question()` generates contextual follow-up probing gaps in the answer
  - Falls back to hardcoded cycle when Gemini unavailable
  - Response includes `ai_generated: True` flag for Gemini questions
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 6. Update API — session creation and retrieval
  - `create_session` stores `target_company` and `language` in DB
  - `create_session` passes both to `engine.opening_questions()`
  - `get_session_details` returns `target_company` and `language`
  - `process_turn` passes `language` and `target_company` to `next_question()`
  - `finalize_session` passes `language` to `finalize_feedback()`
  - _Requirements: 4.3, 4.4, 4.5, 6.1_

- [x] 7. Implement turn-text endpoint (5.2)
  - Created `POST /api/feature4/sessions/{id}/turn-text`
  - Accepts only `utterance` text
  - Uses defaults: latency=1200ms, pitch=0.5, silence=0.0, gaze=0.65
  - Returns same `Feature4TurnResponse` as full turn endpoint
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 8. Implement study guide endpoint (5.5)
  - Created `GET /api/feature4/sessions/{id}/study-guide`
  - Builds transcript summary from stored turns
  - Calls Gemini with language-aware prompt
  - Parses sections: TOPICS_COVERED, WEAK_AREAS, RESOURCES, PRACTICE_QUESTIONS
  - Heuristic fallback when Gemini unavailable
  - Returns `Feature4StudyGuideResponse`
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 9. Final testing
  - All 59 tests passing
  - Existing Feature 4 tests (session flow, heatmap compare) pass unchanged
  - New endpoints verified via import check

## Notes

- `ai_coaching_report_json` was already in the model from Chunk 1; DB column was backfilled by `migrate_feature3_hardening.py`
- Language enforcement is prompt-level only — no translation layer needed
- Study guide uses `import re as _re` locally to avoid shadowing the module-level `re` import
- All Gemini calls have graceful fallbacks so sessions work fully without API key
