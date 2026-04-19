# Requirements Document: Feature 4 Persona Coach Hardening

## Introduction

This document specifies the requirements for Feature 4 Persona Coach Hardening enhancements (Chunk 5). These improvements enhance the existing Persona-Play mock interview system with six capabilities: AI coaching report persistence, simplified text-only turn endpoint, Gemini-powered dynamic follow-up questions, target company field, study guide generation, and language enforcement in Gemini prompts.

## Glossary

- **Feature4_Engine**: The existing mock interview engine that processes turns and generates coaching feedback
- **Mock_Session**: A stored interview session with persona, transcript, and coaching data
- **Persona**: An interviewer archetype (stone_faced, rushed_founder, non_tech_hr, deep_diver)
- **Turn**: A single question-answer exchange in a mock interview session
- **AI_Coaching_Report**: Gemini-generated coaching feedback with strengths, gaps, rewrites, and next focus
- **Study_Guide**: A Gemini-generated learning plan derived from the session transcript
- **Target_Company**: The company name used to tailor interview questions to specific interview styles
- **Language**: Session language setting (english|hinglish) enforced in all Gemini prompts

## Requirements

### Requirement 1: AI Coaching Report Persistence

**User Story:** As a job seeker, I want my Gemini coaching report saved to the database, so that I can retrieve it after the session without re-running the AI.

#### Acceptance Criteria

1. WHEN the session is finalized, THE system SHALL persist the AI coaching report to the ai_coaching_report_json column
2. THE coaching report SHALL contain strengths, critical_gaps, best_answer_rewrite, and next_session_focus sections
3. WHEN retrieving a finalized session, THE system SHALL include the persisted coaching report in the response
4. WHEN Gemini is unavailable, THE system SHALL store an empty JSON object
5. THE ai_coaching_report field SHALL be populated for all new sessions without breaking existing functionality

### Requirement 2: Simplified Turn-Text Endpoint

**User Story:** As a frontend developer, I want a text-only turn endpoint, so that the browser doesn't need to measure audio/video signals.

#### Acceptance Criteria

1. THE system SHALL provide a POST /api/feature4/sessions/{id}/turn-text endpoint
2. THE turn-text endpoint SHALL accept only the utterance text field
3. WHEN using turn-text, THE system SHALL apply sensible defaults for all signal parameters (latency=1200ms, pitch=0.5, silence=0.0, gaze=0.65)
4. THE turn-text endpoint SHALL return the same Feature4TurnResponse as the full turn endpoint
5. THE existing full turn endpoint SHALL continue to work unchanged

### Requirement 3: Gemini-Powered Next Question

**User Story:** As a job seeker, I want follow-up questions based on my actual answer, so that the mock interview feels more realistic.

#### Acceptance Criteria

1. WHEN processing a turn, THE system SHALL attempt to generate a Gemini-powered follow-up question
2. THE Gemini follow-up SHALL probe a gap or assumption in the candidate's answer
3. THE follow-up question SHALL match the current persona's style and pressure level
4. WHEN Gemini is unavailable, THE system SHALL fall back to the hardcoded question cycle
5. THE generated question SHALL be specific to the role and target company context
6. THE response SHALL include an ai_generated flag when the question was Gemini-generated

### Requirement 4: Target Company Field

**User Story:** As a job seeker, I want to specify the target company, so that interview questions are tailored to that company's interview style.

#### Acceptance Criteria

1. THE Mock_Session SHALL include a target_company field
2. THE session creation endpoint SHALL accept an optional target_company parameter
3. WHEN target_company is provided, THE system SHALL include it in Gemini prompts for opening questions and follow-ups
4. WHEN target_company is not provided, THE system SHALL default to an empty string
5. THE session response SHALL include target_company in the response
6. THE target_company field SHALL be indexed for filtering sessions by company

### Requirement 5: Study Guide Endpoint

**User Story:** As a job seeker, I want a study guide generated from my session, so that I know exactly what to prepare before my next interview.

#### Acceptance Criteria

1. THE system SHALL provide a GET /api/feature4/sessions/{id}/study-guide endpoint
2. THE study guide SHALL include: topics covered, weak areas, learning resources, and practice questions
3. WHEN Gemini is available, THE system SHALL generate the study guide using the session transcript
4. WHEN Gemini is unavailable, THE system SHALL return a heuristic study guide based on scorecard data
5. THE study guide SHALL be language-aware (english or hinglish based on session language)
6. WHEN the session does not exist, THE system SHALL return HTTP 404

### Requirement 6: Language Enforcement

**User Story:** As a Hinglish-speaking candidate, I want all AI responses in Hinglish, so that I can practice in my natural communication style.

#### Acceptance Criteria

1. THE Mock_Session SHALL store the language field as a first-class indexed column
2. WHEN language is "hinglish", ALL Gemini prompts SHALL include explicit Hinglish instructions
3. WHEN language is "english", ALL Gemini prompts SHALL use English
4. THE language enforcement SHALL apply to: opening questions, follow-up questions, and coaching reports
5. THE language field SHALL default to "english" when not provided

### Requirement 7: Database Migration

**User Story:** As a database administrator, I want a migration script for new fields, so that existing data remains intact.

#### Acceptance Criteria

1. THE system SHALL provide a migration script adding target_company and language columns to feature4mocksession
2. THE migration SHALL set target_company to "" for existing records
3. THE migration SHALL set language to "english" for existing records
4. THE migration SHALL add indexes on both new fields
5. THE migration SHALL be idempotent and safe to run multiple times
