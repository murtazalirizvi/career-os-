from __future__ import annotations

import json
import os
import time
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
import httpx
from sqlmodel import Session, select

from ..analysis.feature2_engine import Feature2Engine, readiness_forecast, trend_from_rows
from ..db import get_session
from ..models import Feature2InterviewAutopsy, Feature2Reminder
from ..schemas_feature2 import (
    Feature2CreateInterviewRequest,
    Feature2ForecastResponse,
    Feature2InterviewResponse,
    Feature2JourneyExportResponse,
    Feature2QuickDebriefRequest,
    Feature2QuickDebriefResponse,
    Feature2ReminderResponse,
    Feature2ScoreCard,
    Feature2TrendPoint,
    Feature2TrendResponse,
)
from ..services.feature2_reporting import build_reminders, write_feature2_journey_report

router = APIRouter(prefix="/api/feature2", tags=["Feature 2: Rebound"])


def _assemblyai_transcribe(audio_url: str, api_key: str) -> str:
    headers = {"authorization": api_key, "content-type": "application/json"}
    with httpx.Client(timeout=20.0) as client:
        create = client.post("https://api.assemblyai.com/v2/transcript", headers=headers, json={"audio_url": audio_url})
        if create.status_code >= 400:
            raise HTTPException(status_code=502, detail="AssemblyAI transcription request failed.")
        transcript_id = (create.json() or {}).get("id")
        if not transcript_id:
            raise HTTPException(status_code=502, detail="AssemblyAI did not return transcript id.")

        for _ in range(35):
            poll = client.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
            if poll.status_code >= 400:
                raise HTTPException(status_code=502, detail="AssemblyAI polling failed.")
            payload = poll.json() or {}
            status = payload.get("status")
            if status == "completed":
                return str(payload.get("text") or "").strip()
            if status == "error":
                raise HTTPException(status_code=502, detail=f"AssemblyAI transcription error: {payload.get('error', 'unknown')}")
            time.sleep(0.7)

    raise HTTPException(status_code=504, detail="AssemblyAI transcription timed out.")


def _to_response(row: Feature2InterviewAutopsy) -> Feature2InterviewResponse:
    return Feature2InterviewResponse(
        interview_id=row.id,
        candidate_id=row.candidate_id,
        company_name=row.company_name,
        role_name=row.role_name,
        interview_round=row.interview_round,
        lifecycle_stage=row.lifecycle_stage,
        challenge_question=row.challenge_question,
        score=Feature2ScoreCard(**json.loads(row.score_json)),
        ingestion=json.loads(row.ingestion_json),
        technical=json.loads(row.technical_json),
        behavioral=json.loads(row.behavioral_json),
        strategic_actions=json.loads(row.strategic_actions_json),
        analytics_snapshot=json.loads(row.analytics_snapshot_json),
        created_at=row.created_at,
    )


@router.post("/interviews", response_model=Feature2InterviewResponse)
def create_interview_autopsy(req: Feature2CreateInterviewRequest, session: Session = Depends(get_session)):
    transcript_text = req.transcript_text
    assembly_used = False
    if not transcript_text.strip() and req.assembly_audio_url.strip() and req.use_assemblyai:
        api_key = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
        if not api_key:
            raise HTTPException(status_code=400, detail="ASSEMBLYAI_API_KEY is not configured on server.")
        transcript_text = _assemblyai_transcribe(req.assembly_audio_url.strip(), api_key)
        assembly_used = bool(transcript_text)

    engine = Feature2Engine(
        interview_notes=req.interview_notes,
        transcript_text=transcript_text,
        transcript_vtt=req.transcript_vtt,
        technical_expectations=req.technical_expectations,
        culture_vibe=req.culture_vibe,
        interviewer_friendliness=req.interviewer_friendliness,
        interview_round=req.interview_round,
        lifecycle_stage=req.lifecycle_stage,
        hardest_question_hint=req.hardest_question_hint,
        advanced_round_reached=req.advanced_round_reached,
        rejection_reason_hint=req.rejection_reason_hint,
        interview_outcome=req.interview_outcome,
    )
    result = engine.run()

    row = Feature2InterviewAutopsy(
        candidate_id=req.candidate_id,
        company_name=req.company_name,
        role_name=req.role_name,
        interview_round=req.interview_round,
        lifecycle_stage=result["ingestion"]["lifecycle_stage"],
        challenge_question=result["ingestion"]["challenge_question"],
        interview_outcome=req.interview_outcome,
        rejection_reason_hint=req.rejection_reason_hint,
        advanced_round_reached=req.advanced_round_reached,
        ingestion_json=json.dumps(result["ingestion"], ensure_ascii=True),
        technical_json=json.dumps(result["technical"], ensure_ascii=True),
        behavioral_json=json.dumps(result["behavioral"], ensure_ascii=True),
        strategic_actions_json=json.dumps(result["strategic_actions"], ensure_ascii=True),
        analytics_snapshot_json=json.dumps(result["analytics_snapshot"], ensure_ascii=True),
        score_json=json.dumps(result["score"], ensure_ascii=True),
        transcript_source="assemblyai" if assembly_used else "vtt" if req.transcript_vtt else "text" if transcript_text else "voice_notes",
        raw_transcript_excerpt=(transcript_text or req.transcript_vtt or req.interview_notes)[:2000],
    )

    session.add(row)
    session.commit()
    session.refresh(row)

    reminders = build_reminders(result["ingestion"], result["strategic_actions"])
    for item in reminders:
        reminder = Feature2Reminder(
            interview_id=row.id,
            candidate_id=row.candidate_id,
            reminder_type=item["type"],
            scheduled_at=datetime.fromisoformat(item["scheduled_at"]),
            message=item["message"],
            context_json=json.dumps(item, ensure_ascii=True),
        )
        session.add(reminder)
    session.commit()

    return _to_response(row)


@router.get("/interviews/{interview_id}", response_model=Feature2InterviewResponse)
def get_interview_autopsy(interview_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature2InterviewAutopsy, interview_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Interview autopsy not found.")
    return _to_response(row)


@router.post("/quick-debrief", response_model=Feature2QuickDebriefResponse)
def quick_debrief(req: Feature2QuickDebriefRequest):
    engine = Feature2Engine(
        interview_notes=req.debrief_text,
        transcript_text="",
        transcript_vtt="",
        technical_expectations=[],
        culture_vibe="neutral",
        interviewer_friendliness=5,
        interview_round="tech",
        lifecycle_stage="tech",
        hardest_question_hint="",
        advanced_round_reached=False,
        rejection_reason_hint="",
        interview_outcome="unknown",
    )
    result = engine.quick_debrief(req.debrief_text)
    return Feature2QuickDebriefResponse(**result)


@router.get("/candidate/{candidate_id}/trend", response_model=Feature2TrendResponse)
def candidate_trend(candidate_id: str, session: Session = Depends(get_session)):
    q = (
        select(Feature2InterviewAutopsy)
        .where(Feature2InterviewAutopsy.candidate_id == candidate_id)
        .order_by(Feature2InterviewAutopsy.created_at.asc())
    )
    rows = list(session.exec(q).all())
    payload = trend_from_rows(rows)

    points = [Feature2TrendPoint(**p) for p in payload["points"]]
    return Feature2TrendResponse(candidate_id=candidate_id, points=points, trend_summary=payload["trend_summary"])


@router.get("/candidate/{candidate_id}/forecast", response_model=Feature2ForecastResponse)
def candidate_forecast(candidate_id: str, session: Session = Depends(get_session)):
    q = (
        select(Feature2InterviewAutopsy)
        .where(Feature2InterviewAutopsy.candidate_id == candidate_id)
        .order_by(Feature2InterviewAutopsy.created_at.asc())
    )
    rows = list(session.exec(q).all())
    payload = readiness_forecast(rows)

    return Feature2ForecastResponse(candidate_id=candidate_id, **payload)


@router.get("/interviews/{interview_id}/reminders", response_model=Feature2ReminderResponse)
def interview_reminders(interview_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature2InterviewAutopsy, interview_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Interview autopsy not found.")

    q = (
        select(Feature2Reminder)
        .where(Feature2Reminder.interview_id == interview_id)
        .order_by(Feature2Reminder.scheduled_at.asc())
    )
    reminders = list(session.exec(q).all())

    payload = []
    for r in reminders:
        payload.append(
            {
                "id": r.id,
                "type": r.reminder_type,
                "scheduled_at": r.scheduled_at,
                "message": r.message,
                "context": json.loads(r.context_json),
            }
        )

    return Feature2ReminderResponse(interview_id=interview_id, reminders=payload)


@router.get("/interviews/{interview_id}/clarification-email")
def clarification_email(interview_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature2InterviewAutopsy, interview_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Interview autopsy not found.")

    strategic = json.loads(row.strategic_actions_json)
    return {"interview_id": interview_id, "clarification_email": strategic.get("clarification_email", "")}


@router.get("/interviews/{interview_id}/negotiation-script")
def negotiation_script(interview_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature2InterviewAutopsy, interview_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Interview autopsy not found.")

    strategic = json.loads(row.strategic_actions_json)
    return {"interview_id": interview_id, "negotiation_scripts": strategic.get("negotiation_scripts", {})}


@router.get("/candidate/{candidate_id}/career-journey-export", response_model=Feature2JourneyExportResponse)
def career_journey_export(candidate_id: str, session: Session = Depends(get_session)):
    q = (
        select(Feature2InterviewAutopsy)
        .where(Feature2InterviewAutopsy.candidate_id == candidate_id)
        .order_by(Feature2InterviewAutopsy.created_at.asc())
    )
    rows = list(session.exec(q).all())
    if not rows:
        raise HTTPException(status_code=404, detail="No interviews found for candidate.")

    report_path = write_feature2_journey_report(candidate_id, rows)
    return Feature2JourneyExportResponse(candidate_id=candidate_id, report_path=str(report_path), interview_count=len(rows))
