<!-- we are good - v1 scope documented -->
# v1 Scope and Non-Goals: 8-Week Beta

## 1. Scope Principle
Build only what directly improves interview velocity for the Stagnant Specialist.

## 2. In-Scope Capabilities
## 2.1 Feature 1: Hiring Manager's Lens (Primary)
### In Scope
- Resume ingestion and parsing.
- Deterministic ATS checks:
  - Contact extraction validity.
  - Section hierarchy validation.
  - Parseability and text integrity.
- Semantic comparison against target JD.
- Probabilistic recruiter-style critique with confidence levels.
- Actionable rewrite suggestions and before/after diff view.
- Resume version history and role-tagging.

### Acceptance Criteria
- User can upload resume and JD and receive score + prioritized fixes.
- System returns confidence tier per probabilistic claim.
- User can apply edits and rerun analysis in under defined latency budget.

## 2.2 Feature 5: Narrative Architect (Core v1)
### In Scope
- GitHub repository metadata and file-structure ingestion.
- STAR bullet generation for selected projects.
- Employment-gap reframing suggestions.
- Claim-evidence soft warnings (advise only).
- Ready-to-paste outputs for resume and LinkedIn sections.

### Acceptance Criteria
- Generated bullets include problem-action-result framing.
- Claims without evidence are visibly flagged, not blocked.
- User can export selected narratives.

## 2.3 Feature 3: Skill-Arbitrage (Constrained v1)
### In Scope
- Data ingestion from Adzuna API, Reed.co.uk API, and GitHub Octoverse.
- Market demand trends for selected roles and regions.
- Personalized gap map from current profile to target role.
- One practical weekly upskill recommendation path.

### Acceptance Criteria
- Data source and refresh timestamp shown to user.
- Recommendations include transparent rationale.
- User can see projected role-fit delta after selected skills.

## 2.4 Feature 2: Rebound Lite
### In Scope
- Post-interview debrief input (manual and transcript upload).
- Technical and communication feedback summary.
- Action plan for next interview cycle.

### Acceptance Criteria
- User can log interview outcome and receive next-step plan.
- Trend view across recent interviews available.

## 3. Explicitly Out of Scope for v1
- HR/recruiter-facing dashboard or workflow.
- Full biometric analysis (gaze tracking, advanced tone inference).
- Voice avatar and lip-sync simulation.
- Hard-blocking narrative claims without evidence.
- LinkedIn/Indeed scraping bots.
- Multi-tenant enterprise controls.

## 4. Non-Goals
- Building a full ATS replacement.
- Guaranteeing job offers.
- Long-horizon labor forecasting with high certainty.
- Solving all persona segments at launch.

## 5. Product Boundaries
- Candidate-first experience only.
- Guidance is advisory and confidence-labeled.
- User remains final decision maker on edits and claims.

## 6. Technical Boundaries
- Monolithic FastAPI architecture.
- SQLite as beta datastore.
- Background tasks allowed, microservices not required.

## 7. Quality Bars
- Core flow completion without manual developer intervention.
- No blocker bugs in onboarding, resume analysis, or export paths.
- Basic security and privacy controls in place before cohort onboarding.

## 8. Exit Conditions for Beta-to-v1 Expansion
Expand scope only after:
- North-star metric trend is positive and stable.
- Cost per active user is within budget.
- User trust and recommendation usefulness remain high.
