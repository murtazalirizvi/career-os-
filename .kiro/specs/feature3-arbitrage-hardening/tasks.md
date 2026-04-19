# Implementation Plan: Feature 3 Skill Arbitrage Hardening

## Overview

This implementation plan adds six enhancements to the existing Feature 3 Skill Arbitrage system:
1. AI learning path persistence in database (already done in Chunk 1)
2. Composite full-run endpoint for complete analysis workflow
3. Gemini-powered market commentary
4. Salary currency support (USD/PKR/GBP)
5. Market snapshot caching (6-hour TTL, LRU eviction)
6. Trending skills endpoint

All enhancements build upon the existing Python/FastAPI codebase and maintain backward compatibility.

## Tasks

- [x] 1. Run database migration to add new fields
  - Created migration script `Backend/migrate_feature3_hardening.py`
  - Added `salary_currency`, `market_commentary_json` to Feature3MarketSnapshot
  - Added `ai_learning_path_json` to Feature3GapSnapshot (Chunk 1 backfill)
  - Added `ai_coaching_report_json` to Feature4MockSession (Chunk 1 backfill)
  - Set default values for existing records
  - Created indexes on new fields
  - Migration is idempotent
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 2. Update database models with new fields
  - [x] 2.1 Extend Feature3MarketSnapshot model in `Backend/app/models.py`
    - Added `salary_currency: str` field with index and default "USD"
    - Added `market_commentary_json: str` field with default "{}"
    - `ai_learning_path_json` already exists in Feature3GapSnapshot (from Chunk 1)
    - _Requirements: 4.1, 4.3, 3.6, 1.2_

  - [ ]* 2.2 Write unit tests for model field defaults (optional)

- [x] 3. Update API schemas for new fields
  - [x] 3.1 Extended Feature3MarketSnapshotRequest with `salary_currency` field
  - [x] 3.2 Extended Feature3MarketSnapshotResponse with `salary_currency` and `market_commentary`
  - [x] 3.3 Created new schemas: Feature3FullRunRequest, Feature3FullRunResponse,
        Feature3TrendingSkillItem, Feature3TrendingSkillsResponse
  - [ ]* 3.4 Write validation tests (optional)

- [x] 4. Implement market snapshot caching
  - [x] 4.1 Created MarketCache class with LRU OrderedDict, 6-hour TTL, threading.Lock
  - [x] 4.2 Integrated cache into market snapshot endpoint with (role, region, currency) key
  - [ ]* 4.3 Write unit tests for caching logic (optional)

- [x] 5. Implement currency conversion
  - [x] 5.1 Created `_convert_salary` and `_convert_salary_map` helpers with static rates
        (USD/PKR=278.5, USD/GBP=0.79)
  - [x] 5.2 Integrated into market snapshot endpoint — salaries stored and returned in target currency
  - [ ]* 5.3 Write unit tests (optional)

- [x] 6. Implement Gemini market commentary
  - [x] 6.1 Created `_generate_market_commentary` with Gemini prompt + heuristic fallback
  - [x] 6.2 Integrated into market snapshot endpoint — stored in market_commentary_json
  - [ ]* 6.3 Write integration tests (optional)

- [x] 7. Implement full-run composite endpoint
  - [x] 7.1 Created POST `/api/feature3/full-run` route
  - [x] 7.2 Orchestrates market → gap → sprint → ROI in sequence
  - [x] 7.3 Returns Feature3FullRunResponse with all results + execution_time_seconds
  - [x] 7.4 All four DB records created and linked
  - [ ]* 7.5 Write integration tests (optional)

- [x] 8. Implement trending skills endpoint
  - [x] 8.1 Created GET `/api/feature3/trending-skills` with optional days/limit params
  - [x] 8.2 Aggregates skills from tech_stack_clusters across recent snapshots
  - [x] 8.3 Sorts by growth_percentage, returns top N with job_count, avg_salary, currency
  - [ ]* 8.4 Write integration tests (optional)

- [x] 9. Update existing endpoints for new fields
  - [x] 9.1 Market snapshot creation: accepts salary_currency, generates commentary, stores both
  - [x] 9.2 Market snapshot GET: returns salary_currency and market_commentary
  - [x] 9.3 Gap snapshot: ai_learning_path_json included via existing schema field

- [x] 10. Add error handling and logging
  - [x] 10.1 Gemini failures fall back to heuristic commentary; logged via logger.error
  - [x] 10.2 Cache hits/misses/evictions logged via logger.info
  - [x] 10.3 Old records without new fields return empty defaults (salary_currency="USD", commentary="")

- [x] 11. Final integration and testing
  - [x] 11.1 All 59 tests passing (Feature 2, 3, auth, metrics, gemini, core)
  - [x] 11.2 Full workflow verified end-to-end via test_feature3_full_api_flow
  - [x] 11.3 Bug fixed: slowapi @limiter.limit decorator was stripping LoginRequest body
        annotation causing 422 on POST /api/auth/login — fixed with inline rate check

## Notes

- Tasks marked `*` are optional testing tasks skipped for MVP speed
- Caching is in-memory — lost on server restart (acceptable for MVP)
- Currency conversion uses static rates (PKR=278.5, GBP=0.79 per USD)
- Trending skills uses growth heuristic (mentions/day × 100)
- All enhancements maintain backward compatibility
- Migration script also backfills two Chunk 1 columns that were missing from DB
