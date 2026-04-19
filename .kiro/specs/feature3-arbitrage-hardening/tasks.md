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

- [ ] 1. Run database migration to add new fields
  - Create migration script `Backend/migrate_feature3_hardening.py`
  - Add `salary_currency`, `market_commentary_json` columns to Feature3MarketSnapshot
  - Set default values for existing records (salary_currency="USD", market_commentary_json="{}")
  - Create indexes on new fields for query performance
  - Make migration idempotent (safe to run multiple times)
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [ ] 2. Update database models with new fields
  - [ ] 2.1 Extend Feature3MarketSnapshot model in `Backend/app/models.py`
    - Add `salary_currency: str` field with index and default "USD"
    - Add `market_commentary_json: str` field with default "{}"
    - Verify `ai_learning_path_json` already exists in Feature3GapSnapshot (from Chunk 1)
    - _Requirements: 4.1, 4.3, 3.6, 1.2_

  - [ ] 2.2 Write unit tests for model field defaults
    - Test salary_currency defaults to "USD"
    - Test market_commentary_json defaults to "{}"
    - _Requirements: 4.3, 3.6_

- [ ] 3. Update API schemas for new fields
  - [ ] 3.1 Extend Feature3MarketSnapshotRequest in `Backend/app/schemas_feature3.py`
    - Add `salary_currency: str` field with pattern validation (USD|PKR|GBP)
    - _Requirements: 4.2, 4.3_

  - [ ] 3.2 Extend Feature3MarketSnapshotResponse in `Backend/app/schemas_feature3.py`
    - Add `salary_currency: str` field
    - Add `market_commentary: str` field
    - _Requirements: 4.6, 3.6_

  - [ ] 3.3 Create new schemas for full-run and trending skills
    - Create `Feature3FullRunRequest` with all required parameters
    - Create `Feature3FullRunResponse` with composite results
    - Create `Feature3TrendingSkillItem` with skill stats
    - Create `Feature3TrendingSkillsResponse` with trending list
    - _Requirements: 2.3, 2.4, 6.4_

  - [ ] 3.4 Write validation tests for new schemas
    - Test salary_currency rejects invalid values
    - Test full-run request validation
    - _Requirements: 4.2_

- [ ] 4. Implement market snapshot caching
  - [ ] 4.1 Create MarketCache class in `Backend/app/api/feature3.py`
    - Implement LRU cache with OrderedDict
    - Add 6-hour TTL for cache entries
    - Implement thread-safe get/set methods with lock
    - Add cache hit/miss/eviction logging
    - _Requirements: 5.1, 5.2, 5.3, 5.5, 5.6_

  - [ ] 4.2 Integrate cache into market snapshot endpoint
    - Check cache before fetching market data
    - Store fresh data in cache after fetch
    - Use (target_role, region, salary_currency) as cache key
    - _Requirements: 5.1, 5.2, 5.4_

  - [ ] 4.3 Write unit tests for caching logic
    - Test cache hit returns cached data
    - Test cache miss fetches fresh data
    - Test cache expiration after 6 hours
    - Test LRU eviction when cache is full
    - Test thread safety with concurrent requests
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.7_

- [ ] 5. Implement currency conversion
  - [ ] 5.1 Create currency conversion helper in `Backend/app/api/feature3.py`
    - Implement `_convert_salary` function with static exchange rates
    - Support USD, PKR, GBP conversions
    - Add fallback to USD if conversion fails
    - _Requirements: 4.4, 4.5_

  - [ ] 5.2 Integrate currency conversion into market analysis
    - Convert salary data based on salary_currency parameter
    - Store converted salaries in market snapshot
    - Include currency in response
    - _Requirements: 4.4, 4.5, 4.6_

  - [ ] 5.3 Write unit tests for currency conversion
    - Test USD to PKR conversion
    - Test USD to GBP conversion
    - Test USD to USD (no conversion)
    - Test fallback on invalid currency
    - _Requirements: 4.4, 4.5_

- [ ] 6. Implement Gemini market commentary
  - [ ] 6.1 Create market commentary generator in `Backend/app/api/feature3.py`
    - Build Gemini prompt with market data
    - Call gemini_client.generate with temperature=0.3
    - Parse and clean commentary response
    - Implement heuristic fallback when Gemini unavailable
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ] 6.2 Integrate commentary into market snapshot endpoint
    - Generate commentary after market analysis
    - Store commentary in market_commentary_json field
    - Include commentary in response
    - _Requirements: 3.1, 3.6_

  - [ ] 6.3 Write integration tests for market commentary
    - Test commentary generation with mocked Gemini
    - Test heuristic fallback when Gemini unavailable
    - Test commentary includes specific numbers
    - _Requirements: 3.2, 3.4, 3.5_

- [ ] 7. Implement full-run composite endpoint
  - [ ] 7.1 Create full-run endpoint in `Backend/app/api/feature3.py`
    - Create POST `/api/feature3/full-run` route
    - Accept Feature3FullRunRequest parameters
    - _Requirements: 2.1, 2.3_

  - [ ] 7.2 Orchestrate four-step analysis
    - Step 1: Call market snapshot creation
    - Step 2: Call gap snapshot creation with market_snapshot_id
    - Step 3: Call skill sprint creation with gap_snapshot_id
    - Step 4: Call ROI report creation with both IDs
    - Track execution time for each step
    - _Requirements: 2.2, 2.7_

  - [ ] 7.3 Handle errors and return composite response
    - Catch errors at each step and return descriptive message
    - Return Feature3FullRunResponse with all results
    - Include total execution time
    - _Requirements: 2.4, 2.5, 2.7_

  - [ ] 7.4 Create database records for all analyses
    - Ensure all four records are created in database
    - Link records with foreign keys
    - _Requirements: 2.6_

  - [ ] 7.5 Write integration tests for full-run endpoint
    - Test successful full-run with mocked external APIs
    - Test error handling at each step
    - Test execution time is reasonable (<30s)
    - Test database records are created
    - _Requirements: 2.2, 2.5, 2.6, 2.7_

- [ ] 8. Implement trending skills endpoint
  - [ ] 8.1 Create trending skills endpoint in `Backend/app/api/feature3.py`
    - Create GET `/api/feature3/trending-skills` route
    - Accept optional days and limit parameters
    - _Requirements: 6.1, 6.7_

  - [ ] 8.2 Aggregate skill data from recent snapshots
    - Query market snapshots from last 30 days
    - Extract skills from jobs_json field
    - Count skill occurrences and calculate growth
    - Calculate average salary per skill
    - _Requirements: 6.2, 6.3, 6.4_

  - [ ] 8.3 Sort and return top trending skills
    - Sort skills by growth percentage
    - Return top 10 skills
    - Include job count, growth, and salary for each
    - Handle empty case (no recent snapshots)
    - _Requirements: 6.2, 6.4, 6.5, 6.6_

  - [ ] 8.4 Write integration tests for trending skills
    - Test trending calculation with sample data
    - Test sorting by growth percentage
    - Test limit parameter
    - Test empty case
    - Test execution time (<5s)
    - _Requirements: 6.2, 6.5, 6.6, 6.7_

- [ ] 9. Update existing endpoints for new fields
  - [ ] 9.1 Update market snapshot creation endpoint
    - Accept salary_currency parameter
    - Generate market commentary
    - Store new fields in database
    - Include new fields in response
    - _Requirements: 4.2, 3.1, 3.6, 4.6_

  - [ ] 9.2 Update gap snapshot retrieval endpoints
    - Ensure ai_learning_path_json is included in response
    - Handle old records without ai_learning_path_json
    - _Requirements: 1.3, 1.6_

  - [ ] 9.3 Write integration tests for updated endpoints
    - Test market snapshot with currency parameter
    - Test market snapshot includes commentary
    - Test gap snapshot includes learning path
    - _Requirements: 4.6, 3.6, 1.3_

- [ ] 10. Add error handling and logging
  - [ ] 10.1 Add graceful degradation for Gemini failures
    - Catch Gemini errors in commentary generation
    - Fall back to heuristic commentary
    - Log Gemini failures
    - _Requirements: 8.1, 8.4_

  - [ ] 10.2 Add cache operation logging
    - Log cache hits, misses, evictions
    - Log cache size and TTL
    - _Requirements: 5.6, 8.4_

  - [ ] 10.3 Add backward compatibility checks
    - Handle old records without new fields
    - Return empty defaults for missing fields
    - _Requirements: 8.5, 8.6, 8.7_

  - [ ] 10.4 Write error handling tests
    - Test Gemini failure fallback
    - Test old record retrieval
    - Test missing field defaults
    - _Requirements: 8.1, 8.5, 8.6_

- [ ] 11. Final integration and testing
  - [ ] 11.1 Run all Feature 3 tests
    - Ensure all existing tests still pass
    - Ensure new tests pass
    - _Requirements: All_

  - [ ] 11.2 Test full workflow end-to-end
    - Create market snapshot with currency
    - Create gap snapshot with learning path
    - Run full-run endpoint
    - Query trending skills
    - _Requirements: All_

  - [ ] 11.3 Update environment configuration
    - Document any new environment variables
    - Update README with new endpoints
    - _Requirements: 8.7_

## Notes

- Task 1 (migration) must be run before deploying code changes
- Caching is in-memory and will be lost on server restart (acceptable for MVP)
- Currency conversion uses static rates (can be enhanced with live API later)
- Trending skills analysis is simple growth heuristic (can be enhanced with ML later)
- All enhancements maintain backward compatibility with existing clients
- AI learning path persistence was already implemented in Chunk 1 (requirement 1)
