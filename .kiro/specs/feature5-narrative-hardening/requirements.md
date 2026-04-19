# Requirements Document: Feature 5 Narrative Architect Hardening

## Introduction

This document specifies the requirements for Feature 5 Narrative Architect Hardening enhancements (Chunk 6). These improvements enhance the existing Narrative Architect system with six capabilities: GitHub token support, narrative regeneration endpoint, Gemini STAR story enhancement, resume text storage, LinkedIn post generation, and JD text storage.

## Glossary

- **Feature5_Engine**: The existing narrative generation engine that analyzes repos and builds career stories
- **Narrative_Session**: A stored session with deep analysis, STAR stories, talk tracks, and export bundles
- **STAR_Story**: Situation-Task-Action-Result format career story
- **LinkedIn_Post**: Ready-to-paste social media post derived from the narrative session
- **resume_text**: Candidate's resume stored for re-runs without re-submission
- **jd_text**: Job description stored for re-runs without re-submission
- **Regenerate**: Re-run narrative generation with optional tone/role override using stored data

## Requirements

### Requirement 1: GitHub Token Support

**User Story:** As a developer, I want GitHub API calls to use an authenticated token, so that I get 5000 requests/hour instead of 60.

#### Acceptance Criteria

1. THE system SHALL read GITHUB_TOKEN from environment variables
2. WHEN GITHUB_TOKEN is set, THE system SHALL include it in GitHub API request headers
3. WHEN GITHUB_TOKEN is not set, THE system SHALL fall back to unauthenticated requests
4. THE system SHALL log a warning when operating without a token

### Requirement 2: Narrative Regeneration Endpoint

**User Story:** As a job seeker, I want to regenerate my narrative with a different tone or role, so that I can tailor it without re-submitting all my data.

#### Acceptance Criteria

1. THE system SHALL provide a POST /api/feature5/sessions/{id}/regenerate-narrative endpoint
2. WHEN regenerating, THE system SHALL use stored resume_text and jd_text from the session
3. THE endpoint SHALL accept optional tone and target_role overrides
4. WHEN overrides are not provided, THE system SHALL use the session's existing values
5. THE system SHALL update all session fields (narrative, deep_analysis, talk_track, etc.) with regenerated content
6. WHEN the session does not exist, THE system SHALL return HTTP 404
7. THE response SHALL include the new narrative and regenerated_at timestamp

### Requirement 3: Gemini STAR Story Enhancement

**User Story:** As a job seeker, I want my STAR stories enhanced by Gemini, so that they sound authentic with real impact metrics.

#### Acceptance Criteria

1. WHEN generating STAR stories, THE system SHALL use Gemini to enhance template-filled stories
2. THE enhanced stories SHALL include specific impact metrics and authentic language
3. WHEN Gemini is unavailable, THE system SHALL return the heuristic STAR stories unchanged
4. THE enhancement SHALL be applied during the initial session creation

### Requirement 4: Resume Text Storage

**User Story:** As a job seeker, I want my resume text saved with the session, so that I can regenerate narratives without re-submitting my resume.

#### Acceptance Criteria

1. THE Narrative_Session SHALL include a resume_text field
2. WHEN creating a session, THE system SHALL persist the provided resume_text to the database
3. WHEN regenerating a narrative, THE system SHALL use the stored resume_text
4. THE resume_text field SHALL default to an empty string when not provided

### Requirement 5: LinkedIn Post Generation

**User Story:** As a job seeker, I want a ready-to-paste LinkedIn post from my session, so that I can share my work without writing from scratch.

#### Acceptance Criteria

1. THE system SHALL provide a GET /api/feature5/sessions/{id}/linkedin-post endpoint
2. WHEN Gemini is available, THE system SHALL generate a post using the session narrative
3. THE post SHALL include a hook, technical challenge, impact metrics, and hashtags
4. THE post SHALL be under 1300 characters
5. WHEN Gemini is unavailable, THE system SHALL return a heuristic post from stored narrative data
6. WHEN the session does not exist, THE system SHALL return HTTP 404

### Requirement 6: JD Text Storage

**User Story:** As a job seeker, I want my job description saved with the session, so that I can re-run the resume optimizer without re-submitting the JD.

#### Acceptance Criteria

1. THE Narrative_Session SHALL include a jd_text field
2. WHEN creating a session, THE system SHALL persist the provided jd_text to the database
3. WHEN regenerating a narrative, THE system SHALL use the stored jd_text
4. THE jd_text field SHALL default to an empty string when not provided

### Requirement 7: Database Migration

**User Story:** As a database administrator, I want a migration script for new fields, so that existing data remains intact.

#### Acceptance Criteria

1. THE system SHALL provide a migration script adding resume_text and jd_text columns to feature5narrativesession
2. THE migration SHALL set both fields to empty string for existing records
3. THE migration SHALL be idempotent and safe to run multiple times
