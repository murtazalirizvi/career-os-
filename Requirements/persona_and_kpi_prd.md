<!-- we are good - persona and KPI PRD documented -->
# Persona and KPI PRD: Career-OS v1 Beta

## 1. Product Intent
Career-OS v1 helps the Stagnant Specialist (1-3 years experience, unemployed for 6-12+ months) convert application silence into interview momentum.

Primary outcome: increase interview invitation rate from near 0% to 15-20% within the pilot period.

## 2. Launch Persona Definition
### Persona Name
Stagnant Specialist

### Profile
- Experience: 1-3 years in software engineering or adjacent technical roles.
- Employment status: long-term unemployed, typically 6-12+ months.
- Typical history: one prior role, internships, or freelance/project-heavy background.
- Current challenge: portfolio and resume no longer map to market demand and interview expectations.

### Jobs-To-Be-Done
- Help me understand why I am not getting interview responses.
- Help me reshape my resume and project story for current hiring expectations.
- Help me prioritize the smallest set of actions that increase callback probability quickly.

### Emotional Context
- High anxiety from repeated rejection or silence.
- Reduced confidence in communication of technical value.
- Fear that employment gap is interpreted as low ability.

## 3. Problem Statement
The Stagnant Specialist is often not failing because of zero skill, but because of weak market signaling:
- Resume structure and semantics are not recruiter-friendly.
- Experience is not narrated as outcomes and trade-offs.
- Skills are not aligned with current market demand.

## 4. Product Hypothesis
If Career-OS delivers probabilistic recruiter-like resume critique, evidence-backed project narratives, and market-aligned skill guidance, then users will increase interview invitations and regain measurable job-search momentum.

## 5. Success Metrics
## 5.1 North-Star Metric
Interview Invitation Rate (IIR)

Formula:
IIR = invitations / applications_submitted

Target:
- Baseline cohort median near 0-5%.
- v1 target median 15-20% within defined pilot window.

## 5.2 Secondary Metrics
- Time to first invitation (days from onboarding).
- Resume score delta after edits (initial vs latest).
- Application consistency (applications/week).
- Narrative completeness score (projects with STAR + evidence linkage).

## 5.3 Guardrail Metrics
- Recommendation acceptance rate (users applying suggested edits).
- False-confidence reports (user flags that guidance felt misleading).
- AI spend per active user.
- Latency p95 for resume analysis and narrative generation.

## 6. Metric Definitions
### Invitation
Any inbound recruiter or hiring action explicitly advancing candidate toward interview, including:
- Recruiter outreach for screening call.
- Direct screening invitation.
- Online assessment linked to active application.

Do not count generic acknowledgments or automated receipt emails.

### Application Submitted
A deliberate user-reported submission to a distinct role posting.

### Active User (Weekly)
A user who performs at least one high-intent action in a week:
- Upload resume.
- Run resume analysis.
- Generate or revise narrative.
- Log application outcome.

## 7. Cohort and Measurement Window
- Initial beta cohort: Stagnant Specialist users only.
- Measurement window: rolling 28-day intervals.
- Compare each user to own baseline where possible.

## 8. v1 Feature Contribution to KPI
- Feature 1 (Hiring Manager's Lens): primary lever for invitation lift.
- Feature 5 (Narrative Architect): secondary lever for stronger profile quality and interview readiness.
- Feature 3 (Skill-Arbitrage): medium-term lever for increasing role-fit over time.
- Feature 2 (Rebound lite): retention and post-interview learning loop.
- Feature 4 biometrics: excluded from v1 KPI path.

## 9. Assumptions
- Users can self-report applications and invitations reliably enough for beta analytics.
- Probabilistic critique with confidence labels improves trust versus deterministic pass/fail only.
- API-based market data (Adzuna, Reed, Octoverse) is sufficient to produce actionable trends.

## 10. Open Risks
- Attribution complexity: invitation lift may be affected by market seasonality.
- Self-reported data quality variance.
- Overly optimistic AI suggestions could reduce trust.

## 11. Release Criteria
Beta is considered successful if all conditions are met:
- Median IIR reaches at least 15% in the qualified cohort.
- No critical privacy incidents.
- p95 analysis latency is within acceptable product threshold.
- Recommendation trust score remains above predefined threshold in user feedback.
