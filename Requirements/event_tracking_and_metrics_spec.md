# Event Tracking and Metrics Spec: Career-OS v1

## 1. Purpose
Define event instrumentation and metric computation required to measure interview velocity and feature effectiveness.

## 2. Analytics Principles
- Track only events needed for product decisions and KPI measurement.
- Timestamp every event in UTC.
- Use immutable append-only event records.
- Keep PII minimal and separated where possible.

## 3. Core Entity IDs
- user_id
- session_id
- resume_id
- jd_id
- application_id
- interview_id
- project_id

## 4. Event Schema (Common Fields)
Each event should include:
- event_name
- event_version
- occurred_at_utc
- user_id
- session_id
- platform (web)
- feature_area
- metadata_json

## 5. Must-Have Events by Funnel Stage
## 5.1 Onboarding and Activation
- user_signed_up
- profile_completed
- first_resume_uploaded
- first_jd_uploaded
- first_analysis_completed

## 5.2 Resume Optimization (Feature 1)
- resume_analysis_requested
- resume_analysis_completed
- recommendation_viewed
- recommendation_applied
- resume_version_saved
- resume_exported

Recommended metadata:
- analysis_mode (deterministic, probabilistic, hybrid)
- score_total
- confidence_distribution
- top_issue_category
- processing_latency_ms

## 5.3 Narrative Architect (Feature 5)
- github_repo_connected
- project_selected_for_narrative
- star_bullets_generated
- claim_warning_shown
- narrative_exported

Recommended metadata:
- warning_count
- evidence_link_count
- narrative_tone

## 5.4 Skill-Arbitrage (Feature 3)
- market_snapshot_loaded
- skill_gap_viewed
- recommendation_generated
- recommendation_accepted

Recommended metadata:
- data_sources_used
- region
- target_role
- projected_fit_delta

## 5.5 Application and Outcome Tracking
- application_logged
- application_status_updated
- invitation_received
- interview_scheduled
- rejection_logged
- offer_received

Recommended metadata:
- company_name_normalized
- role_name_normalized
- channel (job board, referral, direct)
- status_reason

## 5.6 Rebound Lite (Feature 2)
- interview_debrief_started
- transcript_uploaded
- feedback_generated
- action_plan_created
- action_plan_completed

Recommended metadata:
- interview_round
- failure_theme
- confidence_score

## 6. Derived Metrics
## 6.1 North-Star
Interview Invitation Rate (IIR)
IIR = unique_invitations / unique_applications_logged

## 6.2 Supporting Metrics
- Activation Rate = users_with_first_analysis / signed_up_users
- Recommendation Adoption Rate = recommendations_applied / recommendations_viewed
- Time to First Invitation = first_invitation_at - first_application_at
- Narrative Coverage = projects_with_star / projects_selected

## 6.3 Reliability Metrics
- Event Loss Rate
- Duplicate Event Rate
- Latency p50/p95 for analysis endpoints

## 7. Cohort Logic
- Cohort filter for v1 reporting:
  - Experience band: 1-3 years
  - Unemployment duration: 6+ months
- Time window: rolling 28 days, with weekly snapshots.

## 8. Attribution Guidance
- Primary attribution: changes after recommendation adoption.
- Secondary attribution: changes after narrative export usage.
- Use caution with causal claims; report directional contribution unless controlled experiment exists.

## 9. Data Quality Rules
- Reject events with missing user_id, event_name, or occurred_at_utc.
- Enforce event_version for backward compatibility.
- Validate enum fields (status, feature_area, analysis_mode).

## 10. Privacy and Compliance Notes
- Avoid storing raw transcript text in analytics stream where not needed.
- Store only derived metrics for sensitive behavioral signals.
- Provide user-visible data controls for deletion and export.

## 11. Dashboard Minimums
- KPI panel: IIR, baseline vs current.
- Funnel panel: signup to first analysis to application logging.
- Feature impact panel: recommendation adoption vs invitation outcomes.
- Reliability panel: latency and error rates.
