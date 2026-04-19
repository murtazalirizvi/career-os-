# Requirements Document: Job Tracker Hardening

## Introduction

This document specifies the requirements for Job Tracker Hardening enhancements (Chunk 7). These improvements enhance the existing Job Tracker with six capabilities: pipeline stats endpoint, append-only notes history, core CRM fields (contact, email, URL), CSV export, priority field, and next-action date with due-today endpoint.

## Glossary

- **Job**: A job application record owned by a UserAccount
- **Pipeline**: The Kanban-style status flow: Wishlist → Applied → Interviewing → Offered → Rejected
- **Notes_History**: An append-only JSON array of timestamped notes (never overwritten)
- **Priority**: Job application urgency level: High | Medium | Low
- **Next_Action_Date**: The date by which the user should follow up on a job
- **Due_Today**: Jobs where next_action_date is today or in the past

## Requirements

### Requirement 1: Pipeline Stats Endpoint

**User Story:** As a job seeker, I want a summary of my pipeline counts, so that my dashboard can show a quick status widget without fetching all jobs.

#### Acceptance Criteria

1. THE system SHALL provide a GET /api/jobs/stats endpoint
2. THE response SHALL include total job count
3. THE response SHALL include counts broken down by status (Wishlist, Applied, Interviewing, Offered, Rejected)
4. THE response SHALL include counts broken down by priority (High, Medium, Low)
5. WHEN the user has no jobs, THE system SHALL return zeros for all counts
6. THE endpoint SHALL be protected by bearer token authentication

### Requirement 2: Append-Only Notes History

**User Story:** As a job seeker, I want a notes history that preserves all previous notes, so that I don't lose context when I update my notes.

#### Acceptance Criteria

1. THE Job model SHALL include a notes_history field storing a JSON array of timestamped entries
2. THE system SHALL provide a POST /api/jobs/{id}/notes endpoint to append a note
3. WHEN appending a note, THE system SHALL add a new entry with the note text and current UTC timestamp
4. THE notes_history SHALL never overwrite existing entries
5. THE job response SHALL include the full notes_history array
6. WHEN the job does not exist or belongs to another user, THE system SHALL return HTTP 404

### Requirement 3: Core CRM Fields

**User Story:** As a job seeker, I want to store contact information and job URL with each application, so that I have all relevant details in one place.

#### Acceptance Criteria

1. THE Job model SHALL include contact_name, contact_email, and job_url fields
2. THE job creation endpoint SHALL accept all three fields as optional parameters
3. THE job update endpoint SHALL accept all three fields as optional parameters
4. THE job response SHALL include all three fields
5. WHEN fields are not provided, THE system SHALL default to empty strings

### Requirement 4: CSV Export

**User Story:** As a job seeker, I want to export my job pipeline to a spreadsheet, so that I can analyze and share my application data.

#### Acceptance Criteria

1. THE system SHALL provide a GET /api/jobs/export endpoint
2. THE response SHALL be a downloadable CSV file named jobs_export.csv
3. THE CSV SHALL include all job fields: id, company, position, status, priority, date_applied, salary, contact_name, contact_email, job_url, next_action_date, notes, created_at, updated_at
4. THE endpoint SHALL be protected by bearer token authentication
5. WHEN the user has no jobs, THE system SHALL return an empty CSV with headers only

### Requirement 5: Priority Field

**User Story:** As a job seeker, I want to rank my applications by priority, so that I can focus on the most important ones first.

#### Acceptance Criteria

1. THE Job model SHALL include a priority field with allowed values: High, Medium, Low
2. THE job creation endpoint SHALL accept an optional priority parameter
3. WHEN priority is not provided, THE system SHALL default to "Medium"
4. THE job update endpoint SHALL accept an optional priority parameter
5. THE job response SHALL include the priority field
6. THE priority field SHALL be indexed for filtering

### Requirement 6: Next Action Date and Due Today

**User Story:** As a job seeker, I want to set follow-up dates and see which jobs need attention today, so that I never miss a follow-up.

#### Acceptance Criteria

1. THE Job model SHALL include a next_action_date field storing a date value
2. THE job creation and update endpoints SHALL accept an optional next_action_date parameter
3. THE system SHALL provide a GET /api/jobs/due-today endpoint
4. THE due-today endpoint SHALL return all jobs where next_action_date is today or earlier
5. WHEN next_action_date is not provided, THE system SHALL default to null
6. THE next_action_date field SHALL be indexed for efficient querying

### Requirement 7: Database Migration

**User Story:** As a database administrator, I want a migration script for new fields, so that existing data remains intact.

#### Acceptance Criteria

1. THE system SHALL provide a migration script adding all new columns to the job table
2. THE migration SHALL set notes_history to "[]" for existing records
3. THE migration SHALL set contact_name, contact_email, job_url to "" for existing records
4. THE migration SHALL set priority to "Medium" for existing records
5. THE migration SHALL set next_action_date to NULL for existing records
6. THE migration SHALL add indexes on priority and next_action_date
7. THE migration SHALL be idempotent and safe to run multiple times
