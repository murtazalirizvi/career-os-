# Feature 2 API Examples

## Create Interview Autopsy

POST /api/feature2/interviews

```json
{
  "candidate_id": "candidate-001",
  "interview_round": "tech",
  "company_name": "Acme",
  "role_name": "Frontend Engineer",
  "interview_notes": "I froze on caching and database indexing question.",
  "transcript_text": "Interviewer: How would you optimize query latency? Candidate: I would definitely add cache...",
  "culture_vibe": "neutral",
  "interviewer_friendliness": 6,
  "lifecycle_stage": "tech",
  "technical_expectations": ["sql", "cache", "api"],
  "interview_outcome": "rejected",
  "rejection_reason_hint": "technical depth",
  "advanced_round_reached": false
}
```

## Candidate Trend

GET /api/feature2/candidate/candidate-001/trend

## Candidate Forecast

GET /api/feature2/candidate/candidate-001/forecast

## Career Journey Export

GET /api/feature2/candidate/candidate-001/career-journey-export
