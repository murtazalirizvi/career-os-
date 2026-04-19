# Design Document: Feature 4 Persona Coach Hardening

## Overview

Six enhancements to the Feature 4 Persona-Play mock interview system: AI coaching report persistence, simplified text-only turn endpoint, Gemini-powered dynamic follow-up questions, target company field, study guide generation, and language enforcement in all Gemini prompts.

## Key Design Decisions

- **Language-First Prompting**: All Gemini calls include an explicit language instruction block so Hinglish responses are consistent
- **Graceful Degradation**: Every Gemini call has a heuristic fallback — sessions work fully offline
- **Backward Compatibility**: Existing `/turn` endpoint unchanged; `/turn-text` is additive
- **DB-First**: `target_company` and `language` are first-class indexed columns, not buried in `config_json`

## New Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/feature4/sessions/{id}/turn-text` | Text-only turn, browser-friendly defaults |
| GET | `/api/feature4/sessions/{id}/study-guide` | Gemini study guide from transcript |

## Schema Changes

### Feature4MockSession (models.py)
```python
target_company: str = Field(default="", index=True)
language: str = Field(default="english", index=True)
```

### Feature4CreateSessionRequest (schemas_feature4.py)
```python
target_company: str = Field(default="")
```

### Feature4SessionResponse (schemas_feature4.py)
```python
target_company: str = ""
language: str = "english"
```

### New Schemas
```python
class Feature4TurnTextRequest(BaseModel):
    utterance: str

class Feature4StudyGuideResponse(BaseModel):
    session_id: int
    role_name: str
    target_company: str
    sections: Dict[str, Any]  # topics_covered, weak_areas, resources, practice_questions
    generated_at: datetime
```

## Engine Changes (feature4_engine.py)

### opening_questions()
- Accepts `target_company` and `language` parameters
- Passes both to `_gemini_opening_questions()`
- Gemini prompt includes company context and language instruction

### next_question()
- Accepts `utterance`, `role_name`, `target_company`, `language`
- Tries `_gemini_next_question()` first when Gemini available
- Falls back to hardcoded cycle

### _gemini_coaching_report()
- Accepts `language` parameter
- Prompt includes explicit language instruction

### finalize_feedback()
- Accepts `language` parameter, passes to coaching report

## Migration Script

`Backend/migrate_feature4_hardening.py` — adds `target_company` and `language` columns to `feature4mocksession` with indexes. Idempotent.
