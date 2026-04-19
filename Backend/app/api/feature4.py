from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..analysis.feature4_engine import Feature4PersonaPlayEngine, dump_json
from ..db import get_session
from ..models import Feature4MockSession, Feature4SessionShare, Feature4SessionTurn
from ..schemas_feature4 import (
    Feature4CreateSessionRequest,
    Feature4FinalizeResponse,
    Feature4HeatmapCompareResponse,
    Feature4SessionHistoryItem,
    Feature4SessionHistoryResponse,
    Feature4SessionResponse,
    Feature4ShareResponse,
    Feature4SharedSessionResponse,
    Feature4SynthesisRequest,
    Feature4SynthesisResponse,
    Feature4TurnRequest,
    Feature4TurnResponse,
)

router = APIRouter(prefix="/api/feature4", tags=["Feature 4: Persona-Play"])
engine = Feature4PersonaPlayEngine()


def _loads(text: str) -> Any:
    return json.loads(text)


@router.post("/sessions", response_model=Feature4SessionResponse)
def create_session(req: Feature4CreateSessionRequest, session: Session = Depends(get_session)):
    persona = engine.select_persona(req.persona_mode, req.selected_persona)
    opening = engine.opening_questions(persona, req.role_name)

    row = Feature4MockSession(
        candidate_id=req.candidate_id,
        role_name=req.role_name,
        persona_key=persona.key,
        persona_profile_json=dump_json(persona.__dict__),
        config_json=dump_json(
            {
                "persona_mode": req.persona_mode,
                "language": req.language,
                "include_video": req.include_video,
                "environment_theme": req.environment_theme,
            }
        ),
        opening_questions_json=dump_json(opening),
        realtime_summary_json=dump_json({}),
        transcript_json=dump_json([]),
        deep_logic_json=dump_json({}),
        coach_json=dump_json({}),
        synthesis_json=dump_json({}),
        status="active",
    )
    session.add(row)
    session.commit()
    session.refresh(row)

    return Feature4SessionResponse(
        session_id=row.id,
        candidate_id=row.candidate_id,
        role_name=row.role_name,
        persona=_loads(row.persona_profile_json),
        opening_questions=_loads(row.opening_questions_json),
        realtime_summary={},
        status=row.status,
        created_at=row.created_at,
    )


@router.get("/sessions/{session_id}", response_model=Feature4SessionResponse)
def get_session_details(session_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature4MockSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 4 session not found.")

    return Feature4SessionResponse(
        session_id=row.id,
        candidate_id=row.candidate_id,
        role_name=row.role_name,
        persona=_loads(row.persona_profile_json),
        opening_questions=_loads(row.opening_questions_json),
        realtime_summary=_loads(row.realtime_summary_json),
        status=row.status,
        created_at=row.created_at,
    )


@router.post("/sessions/{session_id}/turn", response_model=Feature4TurnResponse)
def process_turn(session_id: int, req: Feature4TurnRequest, session: Session = Depends(get_session)):
    row = session.get(Feature4MockSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 4 session not found.")

    persona_dict = _loads(row.persona_profile_json)
    persona = engine.select_persona(persona_dict.get("key", "stone_faced"), None)

    existing_turns: List[Dict[str, Any]] = _loads(row.transcript_json)
    qlist = _loads(row.opening_questions_json)
    current_question = qlist[len(existing_turns) % len(qlist)] if qlist else {"type": "baseline", "question": "Explain your recent project."}

    realtime = engine.analyze_realtime(
        utterance=req.utterance,
        response_latency_ms=req.response_latency_ms,
        audio_pitch_variance=req.audio_pitch_variance,
        silent_seconds=req.silent_seconds,
        gaze_focus_ratio=req.gaze_focus_ratio,
    )
    logic = engine.deep_logic_probe(persona, req.utterance)
    hint = engine.whisper_hint(realtime, logic)
    next_q = engine.next_question(persona, len(existing_turns), logic)

    turn_payload = {
        "question": current_question,
        "utterance": req.utterance,
        "realtime": realtime,
        "deep_logic": logic,
    }
    existing_turns.append(turn_payload)

    summary = engine.summarize_realtime([x["realtime"] for x in existing_turns])

    turn_row = Feature4SessionTurn(
        session_id=session_id,
        turn_index=len(existing_turns),
        question_type=current_question.get("type", "baseline"),
        question_text=current_question.get("question", ""),
        answer_text=req.utterance,
        realtime_json=dump_json(realtime),
        deep_logic_json=dump_json(logic),
        whisper_hint=hint,
        next_question_json=dump_json(next_q),
    )
    session.add(turn_row)

    row.transcript_json = dump_json(existing_turns)
    row.deep_logic_json = dump_json(logic)
    row.realtime_summary_json = dump_json(summary)
    row.updated_at = datetime.now(timezone.utc)
    session.add(row)
    session.commit()
    session.refresh(turn_row)

    return Feature4TurnResponse(
        turn_id=turn_row.id,
        session_id=session_id,
        realtime_signals=realtime,
        deep_logic=logic,
        whisper_hint=hint,
        next_question=next_q,
        updated_summary=summary,
    )


@router.post("/sessions/{session_id}/finalize", response_model=Feature4FinalizeResponse)
def finalize_session(session_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature4MockSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 4 session not found.")

    persona_dict = _loads(row.persona_profile_json)
    persona = engine.select_persona(persona_dict.get("key", "stone_faced"), None)

    turns = _loads(row.transcript_json)

    q = (
        select(Feature4MockSession)
        .where(Feature4MockSession.candidate_id == row.candidate_id, Feature4MockSession.id != row.id)
        .order_by(Feature4MockSession.created_at.desc())
    )
    prev_rows = list(session.exec(q).all())
    previous_summaries = [_loads(r.realtime_summary_json) for r in prev_rows if r.realtime_summary_json and r.realtime_summary_json != "{}"]

    payload = engine.finalize_feedback(persona, turns, previous_summaries)

    row.coach_json = dump_json(payload)
    row.ai_coaching_report_json = dump_json(payload.get("ai_coaching_report", {}))  # 1.6
    row.status = "completed"
    row.updated_at = datetime.now(timezone.utc)
    session.add(row)
    session.commit()

    return Feature4FinalizeResponse(session_id=session_id, **payload)


@router.post("/sessions/{session_id}/synthesis", response_model=Feature4SynthesisResponse)
def synthesize_session(session_id: int, req: Feature4SynthesisRequest, session: Session = Depends(get_session)):
    row = session.get(Feature4MockSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 4 session not found.")

    coach = _loads(row.coach_json) if row.coach_json and row.coach_json != "{}" else {}
    transcript_breakdown = coach.get("transcript_breakdown", [])

    payload = engine.synthesize_media(
        session_id=session_id,
        transcript_breakdown=transcript_breakdown,
        voice_style=req.voice_style,
        avatar_style=req.avatar_style,
        language=req.language,
        environment_theme=req.environment_theme,
    )

    row.synthesis_json = dump_json(payload)
    row.updated_at = datetime.now(timezone.utc)
    session.add(row)
    session.commit()

    return Feature4SynthesisResponse(**payload)


@router.post("/sessions/{session_id}/share", response_model=Feature4ShareResponse)
def share_session(session_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature4MockSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 4 session not found.")

    payload = engine.share_packet(session_id)
    share = Feature4SessionShare(
        session_id=session_id,
        share_token=payload["share_token"],
        expires_at=payload["expires_at"],
    )
    session.add(share)
    session.commit()

    return Feature4ShareResponse(
        session_id=session_id,
        share_token=payload["share_token"],
        expires_at=payload["expires_at"],
        review_url=payload["review_url"],
    )


@router.get("/share/{token}", response_model=Feature4SharedSessionResponse)
def open_shared(token: str, session: Session = Depends(get_session)):
    q = select(Feature4SessionShare).where(Feature4SessionShare.share_token == token)
    share = session.exec(q).first()
    if share is None:
        raise HTTPException(status_code=404, detail="Share token not found.")

    expires_at = share.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Share token expired.")

    row = session.get(Feature4MockSession, share.session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    coach = _loads(row.coach_json) if row.coach_json and row.coach_json != "{}" else {
        "scorecard": {},
        "transcript_breakdown": [],
        "badges": {},
    }

    return Feature4SharedSessionResponse(
        session_id=row.id,
        persona=_loads(row.persona_profile_json),
        scorecard=coach.get("scorecard", {}),
        transcript_breakdown=coach.get("transcript_breakdown", []),
        badges=coach.get("badges", {}),
        generated_at=row.updated_at,
    )


@router.get("/candidate/{candidate_id}/heatmap-compare", response_model=Feature4HeatmapCompareResponse)
def heatmap_compare(candidate_id: str, left_session: int, right_session: int, session: Session = Depends(get_session)):
    left = session.get(Feature4MockSession, left_session)
    right = session.get(Feature4MockSession, right_session)
    if left is None or right is None:
        raise HTTPException(status_code=404, detail="One or both sessions not found.")

    if left.candidate_id != candidate_id or right.candidate_id != candidate_id:
        raise HTTPException(status_code=400, detail="Sessions do not belong to candidate.")

    left_payload = _loads(left.coach_json) if left.coach_json and left.coach_json != "{}" else None
    right_payload = _loads(right.coach_json) if right.coach_json and right.coach_json != "{}" else None
    if left_payload is None or right_payload is None:
        raise HTTPException(status_code=400, detail="Finalize both sessions before comparison.")

    payload = engine.compare_heatmap(left_payload, right_payload, candidate_id, left_session, right_session)
    return Feature4HeatmapCompareResponse(**payload)


@router.get("/candidate/{candidate_id}/sessions", response_model=Feature4SessionHistoryResponse)
def candidate_sessions(candidate_id: str, session: Session = Depends(get_session)):
    q = (
        select(Feature4MockSession)
        .where(Feature4MockSession.candidate_id == candidate_id)
        .order_by(Feature4MockSession.created_at.desc())
    )
    rows = list(session.exec(q).all())

    items = []
    for row in rows:
        overall = None
        if row.coach_json and row.coach_json != "{}":
            try:
                overall = float((_loads(row.coach_json).get("scorecard", {}) or {}).get("overall"))
            except Exception:
                overall = None

        items.append(
            Feature4SessionHistoryItem(
                session_id=row.id,
                role_name=row.role_name,
                persona_key=row.persona_key,
                status=row.status,
                overall_score=overall,
                created_at=row.created_at,
            )
        )

    return Feature4SessionHistoryResponse(candidate_id=candidate_id, sessions=items)
