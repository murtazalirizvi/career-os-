# Design Document: Feature 5 Narrative Architect Hardening

## Overview

Six enhancements to the Feature 5 Narrative Architect system: GitHub token support, narrative regeneration, Gemini STAR enhancement, resume_text storage, LinkedIn post generation, and jd_text storage.

## Key Design Decisions

- **Storage-First**: resume_text and jd_text are persisted as first-class columns so regeneration never requires re-submission
- **Regeneration Pattern**: The regenerate endpoint reuses `engine.build_full_session()` with stored data — no new engine methods needed
- **LinkedIn Post**: Gemini generates the post from narrative data; heuristic fallback uses stored LinkedIn sync data
- **Backward Compatibility**: All new fields default to empty string; existing sessions work unchanged

## New Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/feature5/sessions/{id}/regenerate-narrative` | Re-run with optional tone/role override |
| GET | `/api/feature5/sessions/{id}/linkedin-post` | Gemini LinkedIn post from session |

## Schema Changes

### Feature5NarrativeSession (models.py)
```python
resume_text: str = Field(default="")   # 6.4
jd_text: str = Field(default="")       # 6.6
```

### New Schemas (schemas_feature5.py)
```python
class Feature5RegenerateRequest(BaseModel):
    tone: Optional[str] = None
    target_role: Optional[str] = None

class Feature5RegenerateResponse(BaseModel):
    session_id: int
    narrative: Dict[str, Any]
    regenerated_at: datetime

class Feature5LinkedInPostResponse(BaseModel):
    session_id: int
    post_text: str
    character_count: int
    generated_at: datetime
```

## Migration Script

`Backend/migrate_feature5_hardening.py` — adds `resume_text` and `jd_text` columns to `feature5narrativesession`. Idempotent.

## Regeneration Flow

```
POST /sessions/{id}/regenerate-narrative
  → Load row from DB
  → Apply tone/role overrides (or keep existing)
  → Call engine.build_full_session(resume_text=row.resume_text, jd_text=row.jd_text, ...)
  → Update all JSON fields in DB
  → Return Feature5RegenerateResponse
```

## LinkedIn Post Flow

```
GET /sessions/{id}/linkedin-post
  → Load row from DB
  → Extract headline + project_description from export_sync.epic_5_5.linkedin_sync
  → Extract top STAR result from narrative.epic_5_2.star_summaries
  → If Gemini available: generate post with structured prompt
  → Else: build heuristic post from extracted data
  → Return Feature5LinkedInPostResponse
```
