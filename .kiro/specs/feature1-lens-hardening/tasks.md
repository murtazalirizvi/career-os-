# Implementation Plan: Feature 1 Lens Engine Hardening

## Overview

This implementation plan converts the Feature 1 Lens Engine Hardening design into actionable coding tasks. The plan follows a 4-week implementation schedule, building upon the existing Python-based Career OS backend to add Gemini AI integration, job description quality analysis, resume text caching, and enhanced API endpoints.

The implementation maintains backward compatibility while adding robust error handling for external AI service dependencies. All tasks build incrementally, ensuring the system remains functional throughout development.

## Tasks

- [x] 1. Enhance Gemini Client with robust error handling and JSON support
  - Implement timeout handling (20 seconds) and graceful fallback behavior
  - Add JSON response parsing capability with `generate_json()` method
  - Implement comprehensive error handling for HTTP failures, rate limiting, and malformed responses
  - _Requirements: 1.2, 1.6, 7.1, 7.5_

  - [ ]* 1.1 Write property test for Gemini API configuration consistency
    - **Property 2: Gemini API Configuration Consistency**
    - **Validates: Requirements 1.6**

  - [ ]* 1.2 Write unit tests for Gemini client error handling
    - Test timeout scenarios, HTTP error responses, and invalid JSON
    - Test graceful fallback when API key is missing or invalid
    - _Requirements: 1.2, 7.1_

- [x] 2. Extend database schema with new fields for AI recommendations and raw text
  - Add `ai_recommendations_json` field to Feature1Analysis model with default empty list
  - Add `raw_resume_text` field to Feature1Analysis model with default empty string
  - Ensure backward compatibility with existing analyses
  - _Requirements: 1.5, 3.1, 3.2_

  - [ ]* 2.1 Write property test for database persistence completeness
    - **Property 3: Database Persistence Completeness**
    - **Validates: Requirements 1.5**

  - [ ]* 2.2 Write unit tests for database schema migration
    - Test that existing analyses continue to function with new fields
    - Test default value handling for new fields
    - _Requirements: 1.5, 3.5_

- [x] 3. Implement LRU resume text caching system
  - Create `@lru_cache(maxsize=10)` decorator for `_cached_resume_text()` function
  - Implement cache key strategy using resume file path string
  - Add cache data serialization for text and layout blocks tuple
  - Integrate caching transparently into existing `_get_resume_text_and_blocks()` function
  - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [ ]* 3.1 Write property test for LRU cache eviction behavior
    - **Property 10: LRU Cache Eviction Behavior**
    - **Validates: Requirements 5.1, 5.4**

  - [ ]* 3.2 Write property test for cache lookup priority
    - **Property 11: Cache Lookup Priority**
    - **Validates: Requirements 5.2**

  - [ ]* 3.3 Write property test for cache round-trip consistency
    - **Property 14: Cache Round-Trip Consistency**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.5**

  - [ ]* 3.4 Write unit tests for cache error handling
    - Test cache failure fallback to direct PDF parsing
    - Test memory allocation errors and serialization failures
    - _Requirements: 7.3_

- [x] 4. Checkpoint - Ensure all infrastructure tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Enhance Feature1Engine with Gemini AI recommendations
  - Implement `_gemini_recommendations()` method to convert heuristic recommendations to natural language coaching
  - Integrate AI recommendations generation into main `run()` method
  - Add raw resume text extraction and truncation to 8000 characters
  - Ensure graceful fallback when Gemini is unavailable
  - _Requirements: 1.1, 1.3, 1.4, 3.2, 3.3_

  - [ ]* 5.1 Write property test for AI recommendation limit enforcement
    - **Property 1: AI Recommendation Limit Enforcement**
    - **Validates: Requirements 1.3**

  - [ ]* 5.2 Write property test for resume text truncation consistency
    - **Property 7: Resume Text Truncation Consistency**
    - **Validates: Requirements 3.2, 3.3**

  - [ ]* 5.3 Write unit tests for Feature1Engine AI integration
    - Test AI recommendations generation with mocked Gemini responses
    - Test fallback behavior when Gemini is unavailable
    - Test raw text extraction and storage
    - _Requirements: 1.1, 1.2, 3.1_

- [x] 6. Implement job description quality analyzer
  - Create `score_job_description()` function with scoring algorithm
  - Implement length penalty logic (30 points for <80 words, 15 points for <150 words)
  - Add technical skill detection using regex pattern matching
  - Implement structure and seniority validation checks
  - Add Gemini-powered AI feedback generation with 2-sentence critique
  - _Requirements: 2.1, 2.2, 2.4, 2.5, 2.6, 2.7_

  - [ ]* 6.1 Write property test for JD quality score range validation
    - **Property 4: JD Quality Score Range Validation**
    - **Validates: Requirements 2.2, 2.3**

  - [ ]* 6.2 Write property test for JD scoring rule application
    - **Property 5: JD Scoring Rule Application**
    - **Validates: Requirements 2.4, 2.5**

  - [ ]* 6.3 Write property test for technical skill detection accuracy
    - **Property 6: Technical Skill Detection Accuracy**
    - **Validates: Requirements 2.6**

  - [ ]* 6.4 Write unit tests for job description analyzer
    - Test scoring algorithm with various JD lengths and content
    - Test skill detection with known technical terms
    - Test AI feedback generation with mocked Gemini responses
    - _Requirements: 2.1, 2.6, 2.7_

- [x] 7. Create new API endpoints for enhanced functionality
  - Implement POST `/api/feature1/analyze-jd` endpoint with JDAnalyzeRequest/Response schemas
  - Implement GET `/api/feature1/candidate/{id}/latest` endpoint for latest analysis retrieval
  - Add comprehensive input validation and error handling
  - Ensure consistent response formats with existing endpoints
  - _Requirements: 2.1, 4.1, 4.2, 4.4, 7.2, 7.4_

  - [ ]* 7.1 Write property test for latest analysis version retrieval
    - **Property 8: Latest Analysis Version Retrieval**
    - **Validates: Requirements 4.2**

  - [ ]* 7.2 Write property test for API response format consistency
    - **Property 9: API Response Format Consistency**
    - **Validates: Requirements 4.4**

  - [ ]* 7.3 Write property test for error response validation
    - **Property 15: Error Response Validation**
    - **Validates: Requirements 7.2, 7.4**

  - [ ]* 7.4 Write unit tests for new API endpoints
    - Test JD analysis endpoint with various input scenarios
    - Test latest analysis endpoint with existing and missing data
    - Test error handling and HTTP status codes
    - _Requirements: 2.1, 4.1, 4.3, 7.2_

- [x] 8. Update existing analyze endpoint to use enhanced engine
  - Modify existing `/api/feature1/analyze` endpoint to store AI recommendations
  - Update response mapping to include `ai_recommendations` field
  - Ensure backward compatibility with existing client applications
  - Add raw resume text storage to analysis records
  - _Requirements: 1.5, 3.4, 3.5_

  - [ ]* 8.1 Write unit tests for enhanced analyze endpoint
    - Test that existing functionality remains unchanged
    - Test new AI recommendations field population
    - Test raw text storage and retrieval
    - _Requirements: 1.5, 3.4, 3.5_

- [x] 9. Checkpoint - Ensure all API tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Add comprehensive error handling and monitoring
  - Implement error logging for Gemini API failures without exposing internal details
  - Add input validation for PDF uploads (5MB limit, file type validation)
  - Implement graceful degradation for all external service dependencies
  - Add timeout handling for all external API calls
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ]* 10.1 Write unit tests for error handling scenarios
    - Test PDF upload validation and size limits
    - Test external service failure scenarios
    - Test input sanitization and validation
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 11. Integration testing and performance validation
  - [x] 11.1 Create integration tests for end-to-end workflows
    - Test complete resume analysis workflow with AI recommendations
    - Test JD analysis workflow with Gemini integration
    - Test caching effectiveness with repeated PDF processing
    - _Requirements: 5.1, 5.3, 6.1_

  - [ ]* 11.2 Write performance tests for caching system
    - Test cache hit/miss ratios with realistic workloads
    - Validate cache memory usage stays within bounds
    - Test concurrent access scenarios
    - _Requirements: 5.1, 5.4_

  - [x] 11.3 Create test fixtures and mock data
    - Set up test PDFs with known characteristics
    - Create mock Gemini API responses for consistent testing
    - Set up database fixtures with existing analysis data
    - _Requirements: All testing requirements_

- [x] 12. Final integration and deployment preparation
  - [x] 12.1 Update API documentation and schemas
    - Document new endpoints and request/response formats
    - Update existing endpoint documentation with new fields
    - Add error response documentation
    - _Requirements: 2.1, 4.1, 7.2_

  - [x] 12.2 Environment configuration and deployment setup
    - Document required environment variables (GEMINI_API_KEY)
    - Set up monitoring and alerting for external service failures
    - Configure logging levels and error tracking
    - _Requirements: 7.1, 7.4_

  - [x] 12.3 Final system validation
    - Run complete test suite including property-based tests
    - Validate backward compatibility with existing data
    - Test system behavior under various failure scenarios
    - _Requirements: All requirements_

- [x] 13. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples, edge cases, and error conditions
- Checkpoints ensure incremental validation and provide opportunities for user feedback
- The implementation maintains backward compatibility throughout all changes
- All external service integrations include graceful fallback mechanisms