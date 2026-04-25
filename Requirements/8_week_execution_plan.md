<!-- we are good - execution plan documented -->
# 8-Week Execution Plan: Lean Sprint (1-2 Developers)

## 1. Delivery Objective
Ship a usable beta that measurably increases interview invitation rate for Stagnant Specialists.

## 2. Team Model
- Solo mode: one full-stack developer with strict scope control.
- Duo mode: one backend/data owner + one frontend/product owner.

## 3. Weekly Plan
## Week 1: Foundation and Instrumentation
### Deliverables
- Monolithic FastAPI project skeleton.
- SQLite schema and migrations.
- Basic auth/session flow.
- Event tracking foundation for applications, invitations, and feature usage.
- Resume/JD upload endpoints and storage layer.

### Exit Criteria
- End-to-end request path works from UI to DB.
- Core analytics events persist reliably.

## Week 2: Feature 1 Deterministic Core
### Deliverables
- ATS parse checks.
- Contact and section hierarchy validation.
- Keyword differential baseline.
- Initial recommendation engine (rule-based).

### Exit Criteria
- User receives actionable checklist from uploaded resume + JD.

## Week 3: Feature 1 Probabilistic Layer
### Deliverables
- LLM-driven recruiter-style critique.
- Confidence labels per critique segment.
- Prioritized fix ranking.
- Before/after comparison view.

### Exit Criteria
- User can iterate and observe score/recommendation updates.

## Week 4: KPI Loop and Productization
### Deliverables
- Application tracker UI.
- Invitation logging flow.
- Interview velocity dashboard baseline.
- Cohort baseline calculation pipeline.

### Exit Criteria
- KPI can be monitored per user and cohort.

## Week 5: Feature 5 Narrative Architect Core
### Deliverables
- GitHub repo ingestion and project summarization.
- STAR bullet generation for top projects.
- Employment-gap reframing templates.
- Claim-evidence soft warning panel.

### Exit Criteria
- User exports narrative snippets for resume/LinkedIn.

## Week 6: Feature 3 Constrained Market Intelligence
### Deliverables
- Adzuna and Reed ingestion jobs.
- Octoverse trend integration.
- Personalized skill-gap map.
- Weekly skill recommendation card.

### Exit Criteria
- User sees market-aligned upskill guidance with rationale.

## Week 7: Feature 2 Rebound Lite
### Deliverables
- Post-interview debrief form and transcript input.
- Feedback summary and improvement plan.
- Trend view for recent interview outcomes.

### Exit Criteria
- User can close the loop after interview and get targeted next actions.

## Week 8: Hardening and Beta Launch
### Deliverables
- Bug fixing and latency optimization.
- Privacy, consent, and policy copy in product.
- Error handling and fallback UX.
- Pilot cohort onboarding and launch checklist.

### Exit Criteria
- Critical flows stable for beta cohort.
- North-star metric capture is fully operational.

## 4. Dependency Map
- Feature 1 depends on upload, parsing, and event telemetry from Weeks 1-2.
- Feature 5 depends on GitHub integration and content generation infra.
- Feature 3 depends on external API contracts and data normalization.
- Feature 2 depends on transcript ingestion and coaching templates.

## 5. Risk Register and Mitigation
- Scope expansion risk: enforce non-goals weekly.
- API volatility risk: implement retry and cached fallback responses.
- Model quality risk: add confidence labels and conservative phrasing.
- Analytics drift risk: validate event integrity every week.

## 6. Definition of Done (Beta)
- Candidate can onboard, optimize resume, generate narrative, track applications, and receive interview debrief guidance.
- System captures required events for invitation-rate KPI.
- Team can operate and debug without platform re-architecture.
