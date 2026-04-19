# Career-OS Backend (Feature 1)

This backend implements Feature 1: Hiring Manager's Lens with full epic coverage:

- Visual hierarchy and heat-zone simulation.
- ATS parsing and structural integrity checks.
- Semantic matching and keyword diagnostics.
- Competitive benchmarking and percentile estimate.
- Export, versioning, comparison, job-category tagging, and readiness badge endpoint.

It also implements Feature 2: The Rebound (Post-Interview Autopsy):

- Interview data ingestion (voice notes, transcript text, and VTT parsing).
- Technical accuracy autopsy (semantic correctness, perfect response, false-confidence zones, depth-of-why, remedial links).
- Behavioral critique (filler words, answer length quality, STAR validation, question quality, tone heatmap).
- Strategic recovery actions (clarification email, follow-up cadence, negotiation scripts, code patch suggestions, resilience prompts).
- Aggregate growth analytics (trend, rejection category signals, readiness forecast, career journey export).

## Run

```powershell
cd Backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Key Endpoints

- `POST /api/feature1/analyze`
- `GET /api/feature1/versions/{candidate_id}`
- `GET /api/feature1/analysis/{analysis_id}`
- `GET /api/feature1/compare/{candidate_id}?left_version=1&right_version=2`
- `GET /api/feature1/heatmap/{analysis_id}`
- `GET /api/feature1/report/{analysis_id}`
- `POST /api/feature1/ready-to-apply/{analysis_id}`
- `POST /api/feature1/tag/{analysis_id}`

Feature 2 endpoints:

- `POST /api/feature2/interviews`
- `GET /api/feature2/interviews/{interview_id}`
- `POST /api/feature2/quick-debrief`
- `GET /api/feature2/candidate/{candidate_id}/trend`
- `GET /api/feature2/candidate/{candidate_id}/forecast`
- `GET /api/feature2/interviews/{interview_id}/reminders`
- `GET /api/feature2/interviews/{interview_id}/clarification-email`
- `GET /api/feature2/interviews/{interview_id}/negotiation-script`
- `GET /api/feature2/candidate/{candidate_id}/career-journey-export`

Feature 3 endpoints:

- `POST /api/feature3/market-snapshot`
- `GET /api/feature3/market-snapshot/{snapshot_id}`
- `POST /api/feature3/gap-analysis`
- `GET /api/feature3/gap-snapshot/{gap_snapshot_id}`
- `POST /api/feature3/sprint`
- `POST /api/feature3/sprint/{sprint_id}/quiz`
- `POST /api/feature3/sprint/{sprint_id}/resume-inject`
- `GET /api/feature3/sprint/{sprint_id}/peers`
- `POST /api/feature3/future-insights`
- `POST /api/feature3/roi-report`
- `GET /api/feature3/candidate/{candidate_id}/historical-gaps`

Feature 4 endpoints:

- `POST /api/feature4/sessions`
- `GET /api/feature4/sessions/{session_id}`
- `POST /api/feature4/sessions/{session_id}/turn`
- `POST /api/feature4/sessions/{session_id}/finalize`
- `POST /api/feature4/sessions/{session_id}/synthesis`
- `POST /api/feature4/sessions/{session_id}/share`
- `GET /api/feature4/share/{token}`
- `GET /api/feature4/candidate/{candidate_id}/heatmap-compare?left_session=1&right_session=2`

Feature 5 endpoints:

- `POST /api/feature5/sessions`
- `GET /api/feature5/sessions/{session_id}`
- `POST /api/feature5/sessions/{session_id}/consistency-check`
- `POST /api/feature5/sessions/{session_id}/export`
- `GET /api/feature5/sessions/{session_id}/case-study.pdf`
- `GET /api/feature5/sessions/{session_id}/portfolio-site`
- `GET /api/feature5/candidate/{candidate_id}/sessions`

Metrics and event tracking endpoints:

- `POST /api/metrics/events`
- `GET /api/metrics/kpis?window_days=28&user_id={candidate_id}`
- `GET /api/metrics/dashboard?window_days=28&user_id={candidate_id}`
- `POST /api/metrics/applications`
- `PATCH /api/metrics/applications/{application_id}?user_id={candidate_id}`
- `GET /api/metrics/applications/{candidate_id}`
- `GET /api/metrics/users/{candidate_id}/export`
- `DELETE /api/metrics/users/{candidate_id}`

Auth/session endpoints:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me` (requires `Authorization: Bearer <token>`)
- `POST /api/auth/logout`

Core loop orchestration endpoint:

- `GET /api/core/daily-plan/{candidate_id}`

## Optional API Keys

- `GEMINI_API_KEY` or `GOOGLE_API_KEY`: Enables optional AI narrative suggestion lines in Feature 5.
- `ASSEMBLYAI_API_KEY`: Enables optional audio-url transcription path in Feature 2 when `use_assemblyai=true`.
- `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` and `REED_API_KEY`: Enable live market ingestion in Feature 3.

## Notes

- Data is stored in SQLite at `Backend/data/career_os.db`.
- Reports are generated as markdown files in `Backend/data/reports`.
