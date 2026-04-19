# Implementation Plan: Feature 2 Rebound Hardening

## Overview

This implementation plan adds six enhancements to the existing Feature 2 Interview Rebound system:
1. AI insights persistence in database
2. AI regeneration endpoint for on-demand insight refresh
3. Practice drill generation based on weakest dimension
4. AssemblyAI webhook support for async transcription
5. Interview date field for temporal tracking
6. Company stage field for context-aware scoring

All enhancements build upon the existing Python/FastAPI codebase and maintain backward compatibility.

## Tasks

- [ ] 1. Run database migration to add new fields
  - Create migration script `Backend/migrate_feature2_hardening.py`
  - Add `interview_date`, `company_stage`, `transcription_status`, `assembly_transcript_id` columns
  - Set default values for existing records (interview_date=created_at, company_stage="scaleup")
  - Create indexes on new fields for query performance
  - Make migration idempotent (safe to run multiple times)
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ] 2. Update database models with new fields
  - [ ] 2.1 Extend Feature2InterviewAutopsy model in `Backend/app/models.py`
    - Add `interview_date: datetime` field with index and default factory
    - Add `company_stage: str` field with index and default "scaleup"
    - Add `transcription_status: str` field with index and default "completed"
    - Add `assembly_transcript_id: Optional[str]` field with index
    - Update `ai_insights_json` field documentation
    - _Requirements: 1.2, 5.1, 6.1, 4.3_

  - [ ]* 2.2 Write unit tests for model field defaults
    - Test interview_date defaults to current UTC time
    - Test company_stage defaults to "scaleup"
    - Test transcription_status defaults to "completed"
    - _Requirements: 5.3, 6.3_

- [ ] 3. Update API schemas for new fields
  - [ ] 3.1 Extend Feature2CreateInterviewRequest in `Backend/app/schemas_feature2.py`
    - Add optional `interview_date: Optional[datetime]` field
    - Add `company_stage: str` field with pattern validation (startup|scaleup|enterprise)
    - Add optional `webhook_url: Optional[str]` field for async transcription
    - _Requirements: 5.2, 6.2, 4.2_

  - [ ] 3.2 Extend Feature2InterviewResponse in `Backend/app/schemas_feature2.py`
    - Add `interview_date: datetime` field
    - Add `company_stage: str` field
    - Add `transcription_status: str` field
    - Ensure `ai_insights` field always returns dict (not null)
    - _Requirements: 5.4, 6.7, 4.9, 1.6_

  - [ ] 3.3 Create new response schemas for regeneration and practice drills
    - Create `Feature2RegenerateAIResponse` with interview_id, ai_insights, regenerated_at
    - Create `Feature2PracticeDrillResponse` with interview_id, weakness_category, weakness_score, questions, generated_at
    - Create `Feature2WebhookPayload` for AssemblyAI webhook structure
    - _Requirements: 2.7, 3.7_

  - [ ]* 3.4 Write validation tests for new schemas
    - Test company_stage rejects invalid values
    - Test interview_date rejects future dates
    - Test webhook_url format validation
    - _Requirements: 6.2, 5.2_

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Enhance Feature2Engine with company stage scoring
  - [ ] 5.1 Update `_culture_vibe_score` method in `Backend/app/analysis/feature2_engine.py`
    - Add `company_stage` parameter with default "scaleup"
    - Apply +10 adjustment for startup when vibe is neutral/cold
    - Apply +10 adjustment for enterprise when vibe is friendly/neutral
    - _Requirements: 6.4, 6.5, 6.6_

  - [ ] 5.2 Add weakness identification method to Feature2Engine
    - Create `_identify_weakest_dimension` method
    - Compare technical_accuracy, behavioral_quality, strategic_recovery_readiness scores
    - Return dict with category (technical|behavioral|strategic) and score
    - _Requirements: 3.2_

  - [ ]* 5.3 Write unit tests for company stage scoring
    - **Property: Company stage adjustments are bounded**
    - **Validates: Requirements 6.5, 6.6**
    - Test startup gets +10 for neutral/cold vibes
    - Test enterprise gets +10 for friendly/neutral vibes
    - Test scaleup has no adjustment
    - Test score stays within 0-100 range

  - [ ]* 5.4 Write unit tests for weakness identification
    - Test identifies technical as weakest when technical_accuracy is lowest
    - Test identifies behavioral as weakest when behavioral_quality is lowest
    - Test identifies strategic as weakest when strategic_recovery_readiness is lowest
    - _Requirements: 3.2_

- [ ] 6. Implement AI regeneration endpoint
  - [ ] 6.1 Add regenerate-ai endpoint in `Backend/app/api/feature2.py`
    - Create POST `/api/feature2/interviews/{interview_id}/regenerate-ai` route
    - Retrieve existing autopsy record from database
    - Return 404 if interview not found
    - Check Gemini availability, return 502 if unavailable
    - _Requirements: 2.1, 2.2, 2.5, 2.6_

  - [ ] 6.2 Build regeneration prompt and call Gemini
    - Create `_build_regeneration_prompt` helper function
    - Reconstruct context from stored ingestion, technical, behavioral JSON
    - Call gemini_client.generate with temperature=0.35, max_tokens=512
    - Parse structured response (diagnosis, perfect_answer, week_plan, mindset)
    - _Requirements: 2.3, 2.4_

  - [ ] 6.3 Update database with new AI insights
    - Update `ai_insights_json` field with new insights
    - Commit changes to database
    - Return Feature2RegenerateAIResponse with updated insights
    - _Requirements: 2.4, 2.7_

  - [ ]* 6.4 Write integration tests for AI regeneration
    - Test successful regeneration with mocked Gemini
    - Test 404 response for non-existent interview
    - Test 502 response when Gemini unavailable
    - Test database update persists new insights
    - _Requirements: 2.5, 2.6, 2.7_

- [ ] 7. Implement practice drill generation endpoint
  - [ ] 7.1 Add practice-drill endpoint in `Backend/app/api/feature2.py`
    - Create POST `/api/feature2/interviews/{interview_id}/practice-drill` route
    - Retrieve autopsy record from database
    - Return 404 if interview not found
    - Check Gemini availability, return 502 if unavailable
    - _Requirements: 3.1, 3.8, 3.9_

  - [ ] 7.2 Identify weakness and build targeted prompt
    - Call `_identify_weakest_dimension` with scores from autopsy
    - Create `_build_practice_drill_prompt` helper function
    - Customize prompt based on weakness category (technical/behavioral/strategic)
    - Include role context and challenge question
    - _Requirements: 3.2, 3.4, 3.5, 3.6_

  - [ ] 7.3 Generate and parse practice questions
    - Call gemini_client.generate with temperature=0.4, max_tokens=512
    - Create `_parse_practice_questions` helper to extract 3 questions
    - Return Feature2PracticeDrillResponse with weakness info and questions
    - _Requirements: 3.3, 3.7_

  - [ ]* 7.4 Write integration tests for practice drills
    - Test technical weakness generates technical questions
    - Test behavioral weakness generates STAR-format questions
    - Test strategic weakness generates recovery questions
    - Test 404 for non-existent interview
    - Test 502 when Gemini unavailable
    - _Requirements: 3.4, 3.5, 3.6, 3.8, 3.9_

- [ ] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement AssemblyAI webhook endpoint
  - [ ] 9.1 Add webhook signature validation helper
    - Create `_validate_assemblyai_signature` function in `Backend/app/api/feature2.py`
    - Use HMAC-SHA256 with ASSEMBLYAI_WEBHOOK_SECRET environment variable
    - Use constant-time comparison to prevent timing attacks
    - Return False if secret not configured
    - _Requirements: 7.1, 7.2_

  - [ ] 9.2 Add rate limiting for webhook requests
    - Create `_check_rate_limit` function with in-memory tracking
    - Implement sliding window rate limiter (100 requests per minute per IP)
    - Use threading lock for thread-safe access
    - _Requirements: 7.6_

  - [ ] 9.3 Create webhook endpoint handler
    - Create POST `/api/feature2/webhooks/assemblyai` route
    - Validate signature from X-AssemblyAI-Signature header
    - Return 401 if signature invalid
    - Check rate limit, return 429 if exceeded
    - Parse webhook payload (transcript_id, status, text, error)
    - _Requirements: 4.1, 7.1, 7.6_

  - [ ] 9.4 Process webhook completion
    - Find autopsy record by assembly_transcript_id
    - Return 404 if transcript not found
    - Handle "completed" status: run full analysis with transcript
    - Handle "error" status: update transcription_status to "transcription_failed"
    - Update autopsy record with results
    - _Requirements: 4.4, 4.5, 4.6, 7.4_

  - [ ]* 9.5 Write integration tests for webhook endpoint
    - Test webhook with valid signature processes successfully
    - Test webhook with invalid signature returns 401
    - Test webhook for unknown transcript_id returns 404
    - Test rate limiting blocks excessive requests
    - Test completion status updates autopsy record
    - Test error status marks transcription as failed
    - _Requirements: 7.1, 7.2, 7.4, 7.6_

- [ ] 10. Update interview creation endpoint for webhook mode
  - [ ] 10.1 Modify create_interview_autopsy in `Backend/app/api/feature2.py`
    - Accept interview_date from request, default to utc_now() if None
    - Accept company_stage from request, default to "scaleup"
    - Accept webhook_url from request for async transcription
    - _Requirements: 5.2, 5.3, 6.2, 6.3, 4.2_

  - [ ] 10.2 Implement webhook-based transcription flow
    - When webhook_url provided with assembly_audio_url, use webhook mode
    - Register webhook URL with AssemblyAI transcription request
    - Create autopsy record with transcription_status="transcribing"
    - Store assembly_transcript_id for webhook correlation
    - Return immediately without waiting for transcription
    - _Requirements: 4.2, 4.3, 4.9_

  - [ ] 10.3 Pass company_stage to Feature2Engine
    - Update Feature2Engine instantiation to pass company_stage
    - Update engine.run() to use company_stage in culture scoring
    - Ensure ai_insights_json is always populated (empty dict if Gemini unavailable)
    - _Requirements: 6.4, 1.1, 1.4_

  - [ ] 10.4 Update database record creation
    - Set interview_date field from request or default
    - Set company_stage field from request or default
    - Set transcription_status based on mode (transcribing vs completed)
    - Set assembly_transcript_id when using webhook mode
    - _Requirements: 5.1, 6.1, 4.3_

  - [ ]* 10.5 Write integration tests for enhanced interview creation
    - Test interview creation with custom interview_date
    - Test interview_date defaults to current time when omitted
    - Test interview creation with company_stage
    - Test company_stage defaults to "scaleup" when omitted
    - Test webhook mode returns immediately with transcribing status
    - Test polling mode (existing behavior) still works
    - _Requirements: 5.2, 5.3, 6.2, 6.3, 4.9, 9.3_

- [ ] 11. Update interview retrieval endpoints
  - [ ] 11.1 Update `_to_response` helper in `Backend/app/api/feature2.py`
    - Include interview_date in response
    - Include company_stage in response
    - Include transcription_status in response
    - Ensure ai_insights returns empty dict instead of null
    - _Requirements: 5.4, 6.7, 1.3, 1.6_

  - [ ] 11.2 Update candidate trend endpoint for interview_date ordering
    - Modify `/candidate/{candidate_id}/trend` to support ordering by interview_date
    - Update query to use interview_date index for performance
    - _Requirements: 5.5_

  - [ ]* 11.3 Write integration tests for retrieval endpoints
    - Test get_interview_autopsy includes new fields
    - Test candidate_trend orders by interview_date
    - Test ai_insights returns empty dict for old records
    - _Requirements: 5.4, 5.5, 9.6_

- [ ] 12. Add error handling and logging
  - [ ] 12.1 Add graceful degradation for Gemini failures
    - Wrap all Gemini calls in try-except blocks
    - Log warnings when Gemini unavailable
    - Return empty dict for ai_insights when Gemini fails during creation
    - Return 502 with descriptive message for regeneration/practice drill failures
    - _Requirements: 1.4, 2.6, 3.9, 9.2_

  - [ ] 12.2 Add webhook failure logging
    - Log webhook signature validation failures with IP address
    - Log unknown transcript_id events
    - Log transcription errors from AssemblyAI
    - _Requirements: 7.4, 9.5_

  - [ ] 12.3 Add backward compatibility checks
    - Handle old autopsy records without ai_insights_json field
    - Handle old records without interview_date/company_stage fields
    - Ensure existing API clients work without providing new optional fields
    - _Requirements: 9.1, 9.3, 9.6, 9.7_

  - [ ]* 12.4 Write error handling tests
    - Test Gemini unavailable during interview creation returns empty ai_insights
    - Test regeneration with Gemini failure returns 502
    - Test practice drill with Gemini failure returns 502
    - Test webhook processing logs errors appropriately
    - _Requirements: 1.4, 2.6, 3.9, 9.2_

- [ ] 13. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Update environment configuration
  - [ ] 14.1 Document new environment variables
    - Add ASSEMBLYAI_WEBHOOK_SECRET to .env.example
    - Document webhook URL configuration in README
    - Add deployment checklist to DEPLOYMENT.md
    - _Requirements: 7.1, 7.5_

  - [ ] 14.2 Create deployment verification script
    - Script to verify new columns exist in database
    - Script to test webhook endpoint with sample payload
    - Script to verify Gemini integration for new endpoints
    - _Requirements: 8.6_

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- All enhancements maintain backward compatibility with existing clients
- Migration script must be run before deploying code changes
- Webhook mode is optional; existing polling-based transcription continues to work
- Company stage scoring adjustments are subtle (+10 points) to avoid dramatic score changes
- AI insights gracefully degrade to empty dict when Gemini unavailable
