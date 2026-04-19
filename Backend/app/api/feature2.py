from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
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
        ai_insights=json.loads(row.ai_insights_json) if row.ai_insights_json else {},
        created_at=row.created_at,
        # Chunk 3 enhancements
        interview_date=row.interview_date,
        company_stage=row.company_stage,
        transcription_status=row.transcription_status,
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
        company_stage=req.company_stage,  # Chunk 3 enhancement
    )
    result = engine.run()

    # Chunk 3: Handle interview_date (default to now if not provided)
    interview_date = req.interview_date if req.interview_date else datetime.now(timezone.utc)

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
        ai_insights_json=json.dumps(result.get("ai_insights", {}), ensure_ascii=True),  # 1.4
        # Chunk 3 enhancements
        interview_date=interview_date,
        company_stage=req.company_stage,
        transcription_status="completed",  # For now, webhook mode will be added later
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


# Chunk 3: AI Regeneration Endpoint
@router.post("/interviews/{interview_id}/regenerate-ai")
def regenerate_ai_insights(interview_id: int, session: Session = Depends(get_session)):
    """Regenerate AI insights for an existing interview autopsy."""
    from ..analysis import gemini_client
    from ..schemas_feature2 import Feature2RegenerateAIResponse
    import re
    
    # 1. Retrieve existing autopsy
    row = session.get(Feature2InterviewAutopsy, interview_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Interview autopsy not found.")
    
    # 2. Check Gemini availability
    if not gemini_client.is_available():
        raise HTTPException(
            status_code=502,
            detail="Gemini API unavailable. Check GEMINI_API_KEY configuration."
        )
    
    # 3. Reconstruct context from stored data
    ingestion = json.loads(row.ingestion_json)
    technical = json.loads(row.technical_json)
    behavioral = json.loads(row.behavioral_json)
    
    # 4. Build regeneration prompt
    prompt = (
        f"You are a senior engineering interview coach. Analyze this interview debrief:\n\n"
        f"Interview round: {row.interview_round}\n"
        f"Company: {row.company_name} ({row.company_stage})\n"
        f"Role: {row.role_name}\n"
        f"Outcome: {row.interview_outcome}\n"
        f"Hardest question: {ingestion.get('challenge_question', 'unknown')}\n"
        f"Technical score: {technical.get('score', 0):.1f}/100\n"
        f"Behavioral score: {behavioral.get('score', 0):.1f}/100\n\n"
        f"Transcript excerpt:\n\"\"\"{row.raw_transcript_excerpt[:1500]}\"\"\"\n\n"
        "Provide a structured coaching response with these exact sections:\n"
        "DIAGNOSIS: (2 sentences on root cause of weak performance)\n"
        "PERFECT_ANSWER: (ideal 3-sentence answer to the hardest question)\n"
        "WEEK_PLAN: (3 specific daily actions for the next 3 days)\n"
        "MINDSET: (1 sentence reframe to build resilience)\n"
        "Keep each section concise and actionable."
    )
    
    # 5. Generate new AI insights
    raw_insights = gemini_client.generate(prompt, temperature=0.35, max_tokens=512)
    
    if not raw_insights:
        raise HTTPException(
            status_code=502,
            detail="Gemini API returned empty response"
        )
    
    # 6. Parse structured insights
    ai_insights: dict[str, str] = {}
    for section in ["DIAGNOSIS", "PERFECT_ANSWER", "WEEK_PLAN", "MINDSET"]:
        pattern = re.compile(rf"{section}:\s*(.*?)(?=(?:DIAGNOSIS|PERFECT_ANSWER|WEEK_PLAN|MINDSET):|$)", re.S)
        match = pattern.search(raw_insights)
        if match:
            ai_insights[section.lower()] = match.group(1).strip()
    
    # 7. Update database
    row.ai_insights_json = json.dumps(ai_insights, ensure_ascii=True)
    session.add(row)
    session.commit()
    session.refresh(row)
    
    return Feature2RegenerateAIResponse(
        interview_id=interview_id,
        ai_insights=ai_insights,
        regenerated_at=datetime.now(timezone.utc)
    )


# Chunk 3: Practice Drill Generation Endpoint
@router.post("/interviews/{interview_id}/practice-drill")
def generate_practice_drill(interview_id: int, session: Session = Depends(get_session)):
    """Generate targeted practice questions based on weakest dimension."""
    from ..analysis import gemini_client
    from ..schemas_feature2 import Feature2PracticeDrillResponse
    import re
    
    # 1. Retrieve autopsy
    row = session.get(Feature2InterviewAutopsy, interview_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Interview autopsy not found.")
    
    # 2. Check Gemini availability
    if not gemini_client.is_available():
        raise HTTPException(status_code=502, detail="Gemini API unavailable")
    
    # 3. Identify weakest dimension
    scores = json.loads(row.score_json)
    dimensions = {
        "technical": scores.get("technical_accuracy", 0.0),
        "behavioral": scores.get("behavioral_quality", 0.0),
        "strategic": scores.get("strategic_recovery_readiness", 0.0)
    }
    weakest = min(dimensions.items(), key=lambda x: x[1])
    weakness_category = weakest[0]
    weakness_score = weakest[1]
    
    # 4. Build practice drill prompt
    ingestion = json.loads(row.ingestion_json)
    challenge_question = ingestion.get("challenge_question", "unknown")
    
    if weakness_category == "technical":
        focus = "technical depth, system design trade-offs, and quantitative reasoning"
        format_hint = "Focus on architecture, scalability, and implementation details."
    elif weakness_category == "behavioral":
        focus = "STAR-format storytelling, impact quantification, and collaboration"
        format_hint = "Use STAR format: Situation, Task, Action, Result with metrics."
    else:  # strategic
        focus = "follow-up strategy, negotiation, and resilience"
        format_hint = "Focus on recovery tactics, clarification, and positioning."
    
    prompt = (
        f"You are an expert interview coach. Generate exactly 3 practice questions to improve {weakness_category} skills.\n\n"
        f"Context:\n"
        f"- Role: {row.role_name}\n"
        f"- Weakness: {weakness_category} (score: {weakness_score:.1f}/100)\n"
        f"- Recent challenge: {challenge_question}\n"
        f"- Focus areas: {focus}\n\n"
        f"Requirements:\n"
        f"1. Generate exactly 3 questions\n"
        f"2. {format_hint}\n"
        f"3. Questions should be progressively challenging\n"
        f"4. Each question should be realistic for a {row.role_name} interview\n\n"
        f"Format your response as:\n"
        f"QUESTION 1: [question text]\n"
        f"QUESTION 2: [question text]\n"
        f"QUESTION 3: [question text]"
    )
    
    # 5. Generate questions
    raw_response = gemini_client.generate(prompt, temperature=0.4, max_tokens=512)
    if not raw_response:
        raise HTTPException(status_code=502, detail="Gemini API failed")
    
    # 6. Parse questions
    questions = []
    for i in range(1, 4):
        pattern = re.compile(rf"QUESTION {i}:\s*(.*?)(?=QUESTION {i+1}:|$)", re.S)
        match = pattern.search(raw_response)
        if match:
            questions.append(match.group(1).strip())
    
    # Fallback if parsing fails
    if len(questions) < 3:
        lines = [line.strip() for line in raw_response.split('\n') if line.strip() and not line.strip().startswith('QUESTION')]
        questions = lines[:3]
    
    return Feature2PracticeDrillResponse(
        interview_id=interview_id,
        weakness_category=weakness_category,
        weakness_score=weakness_score,
        questions=questions[:3],  # Ensure exactly 3 questions
        generated_at=datetime.now(timezone.utc)
    )


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
        .order_by(Feature2InterviewAutopsy.interview_date.asc())  # Chunk 3: Order by interview_date instead of created_at
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
        .order_by(Feature2InterviewAutopsy.interview_date.asc())  # Chunk 3: Order by interview_date
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
        .order_by(Feature2InterviewAutopsy.interview_date.asc())  # Chunk 3: Order by interview_date
    )
    rows = list(session.exec(q).all())
    if not rows:
        raise HTTPException(status_code=404, detail="No interviews found for candidate.")

    report_path = write_feature2_journey_report(candidate_id, rows)
    return Feature2JourneyExportResponse(candidate_id=candidate_id, report_path=str(report_path), interview_count=len(rows))
