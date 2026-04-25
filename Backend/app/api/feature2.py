"""
Feature 2: The Rebound - Post-Interview Autopsy Engine
Analyzes interview performance with technical accuracy, behavioral critique, and strategic recovery actions
Last Updated: April 25, 2026
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
import httpx
from sqlmodel import Session, select

from ..analysis import gemini_client
from ..analysis.feature2_engine import Feature2Engine, readiness_forecast, trend_from_rows
from ..db import get_session
from ..models import Feature2InterviewAutopsy, Feature2Reminder
from ..schemas_feature2 import (
    Feature2CreateInterviewRequest,
    Feature2ForecastResponse,
    Feature2InterviewResponse,
    Feature2JourneyExportResponse,
    Feature2PracticeDrillResponse,
    Feature2QuickDebriefRequest,
    Feature2QuickDebriefResponse,
    Feature2RegenerateAIResponse,
    Feature2ReminderResponse,
    Feature2ScoreCard,
    Feature2TrendPoint,
    Feature2TrendResponse,
)
from ..services.feature2_reporting import build_reminders, write_feature2_journey_report

logger = logging.getLogger("career_os.feature2")

router = APIRouter(prefix="/api/feature2", tags=["Feature 2: Rebound"])

# ─── Webhook rate-limiter (in-memory, sliding window) ────────────────────────
_webhook_rate_limits: Dict[str, List[datetime]] = defaultdict(list)
_rate_limit_lock = threading.Lock()


def _check_rate_limit(ip_address: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
    """Return True if request is allowed, False if rate limit exceeded."""
    with _rate_limit_lock:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=window_seconds)
        _webhook_rate_limits[ip_address] = [
            ts for ts in _webhook_rate_limits[ip_address] if ts > cutoff
        ]
        if len(_webhook_rate_limits[ip_address]) >= max_requests:
            return False
        _webhook_rate_limits[ip_address].append(now)
        return True


def _validate_assemblyai_signature(signature: str, body: bytes) -> bool:
    """Validate HMAC-SHA256 signature from AssemblyAI webhook."""
    secret = os.getenv("ASSEMBLYAI_WEBHOOK_SECRET", "").strip()
    if not secret:
        # If no secret configured, skip validation (dev mode)
        logger.warning("ASSEMBLYAI_WEBHOOK_SECRET not configured — skipping signature check")
        return True
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def _assemblyai_transcribe(audio_url: str, api_key: str) -> str:
    """Polling-based transcription (legacy / fallback)."""
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


def _assemblyai_submit_webhook(audio_url: str, api_key: str, webhook_url: str) -> str:
    """Submit audio to AssemblyAI with a webhook callback. Returns transcript_id immediately."""
    headers = {"authorization": api_key, "content-type": "application/json"}
    body = {"audio_url": audio_url, "webhook_url": webhook_url}
    with httpx.Client(timeout=15.0) as client:
        resp = client.post("https://api.assemblyai.com/v2/transcript", headers=headers, json=body)
        if resp.status_code >= 400:
            raise HTTPException(status_code=502, detail="AssemblyAI webhook submission failed.")
        transcript_id = (resp.json() or {}).get("id")
        if not transcript_id:
            raise HTTPException(status_code=502, detail="AssemblyAI did not return transcript id.")
    return transcript_id


def _assemblyai_fetch_transcript(transcript_id: str, api_key: str) -> str:
    """Fetch a completed transcript text from AssemblyAI by ID."""
    headers = {"authorization": api_key, "content-type": "application/json"}
    with httpx.Client(timeout=15.0) as client:
        resp = client.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers)
        if resp.status_code >= 400:
            raise RuntimeError(f"AssemblyAI fetch failed: {resp.status_code}")
        return str((resp.json() or {}).get("text") or "").strip()


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
    api_key = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
    transcript_text = req.transcript_text
    assembly_used = False

    # ── Webhook mode: submit audio and return immediately ──────────────────
    if (
        not transcript_text.strip()
        and req.assembly_audio_url.strip()
        and req.use_assemblyai
        and req.webhook_url
    ):
        if not api_key:
            raise HTTPException(status_code=400, detail="ASSEMBLYAI_API_KEY is not configured on server.")

        transcript_id = _assemblyai_submit_webhook(
            req.assembly_audio_url.strip(), api_key, req.webhook_url
        )
        interview_date = req.interview_date if req.interview_date else datetime.now(timezone.utc)

        # Create a stub record — analysis will be filled in by the webhook
        row = Feature2InterviewAutopsy(
            candidate_id=req.candidate_id,
            company_name=req.company_name,
            role_name=req.role_name,
            interview_round=req.interview_round,
            lifecycle_stage=req.lifecycle_stage or req.interview_round,
            challenge_question=req.hardest_question_hint or "Pending transcription",
            interview_outcome=req.interview_outcome,
            rejection_reason_hint=req.rejection_reason_hint,
            advanced_round_reached=req.advanced_round_reached,
            ingestion_json="{}",
            technical_json="{}",
            behavioral_json="{}",
            strategic_actions_json="{}",
            analytics_snapshot_json="{}",
            score_json=json.dumps({
                "technical_accuracy": 0.0,
                "behavioral_quality": 0.0,
                "strategic_recovery_readiness": 0.0,
                "confidence_risk": 0.0,
                "overall_autopsy_score": 0.0,
            }),
            transcript_source="assemblyai_webhook",
            raw_transcript_excerpt="",
            ai_insights_json="{}",
            interview_date=interview_date,
            company_stage=req.company_stage,
            transcription_status="transcribing",
            assembly_transcript_id=transcript_id,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        logger.info(f"Webhook mode: interview {row.id} created, awaiting transcript {transcript_id}")
        return _to_response(row)

    # ── Polling mode (legacy): block until transcript is ready ─────────────
    if not transcript_text.strip() and req.assembly_audio_url.strip() and req.use_assemblyai:
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
        company_stage=req.company_stage,
    )
    result = engine.run()

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
        ai_insights_json=json.dumps(result.get("ai_insights", {}), ensure_ascii=True),
        interview_date=interview_date,
        company_stage=req.company_stage,
        transcription_status="completed",
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
@router.post("/interviews/{interview_id}/regenerate-ai", response_model=Feature2RegenerateAIResponse)
def regenerate_ai_insights(interview_id: int, session: Session = Depends(get_session)):
    """Regenerate AI insights for an existing interview autopsy."""
    row = session.get(Feature2InterviewAutopsy, interview_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Interview autopsy not found.")

    if not gemini_client.is_available():
        raise HTTPException(status_code=502, detail="Gemini API unavailable. Check GEMINI_API_KEY configuration.")

    ingestion = json.loads(row.ingestion_json)
    technical = json.loads(row.technical_json)
    behavioral = json.loads(row.behavioral_json)

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

    raw_insights = gemini_client.generate(prompt, temperature=0.35, max_tokens=512)
    if not raw_insights:
        raise HTTPException(status_code=502, detail="Gemini API returned empty response")

    ai_insights: Dict[str, str] = {}
    for section in ["DIAGNOSIS", "PERFECT_ANSWER", "WEEK_PLAN", "MINDSET"]:
        match = re.compile(rf"{section}:\s*(.*?)(?=(?:DIAGNOSIS|PERFECT_ANSWER|WEEK_PLAN|MINDSET):|$)", re.S).search(raw_insights)
        if match:
            ai_insights[section.lower()] = match.group(1).strip()

    row.ai_insights_json = json.dumps(ai_insights, ensure_ascii=True)
    session.add(row)
    session.commit()
    session.refresh(row)
    logger.info(f"AI insights regenerated for interview {interview_id}")

    return Feature2RegenerateAIResponse(
        interview_id=interview_id,
        ai_insights=ai_insights,
        regenerated_at=datetime.now(timezone.utc),
    )


# Chunk 3: Practice Drill Generation Endpoint
@router.post("/interviews/{interview_id}/practice-drill", response_model=Feature2PracticeDrillResponse)
def generate_practice_drill(interview_id: int, session: Session = Depends(get_session)):
    """Generate targeted practice questions based on weakest dimension."""
    row = session.get(Feature2InterviewAutopsy, interview_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Interview autopsy not found.")

    if not gemini_client.is_available():
        raise HTTPException(status_code=502, detail="Gemini API unavailable")

    scores = json.loads(row.score_json)
    dimensions = {
        "technical": scores.get("technical_accuracy", 0.0),
        "behavioral": scores.get("behavioral_quality", 0.0),
        "strategic": scores.get("strategic_recovery_readiness", 0.0),
    }
    weakest = min(dimensions.items(), key=lambda x: x[1])
    weakness_category, weakness_score = weakest

    ingestion = json.loads(row.ingestion_json)
    challenge_question = ingestion.get("challenge_question", "unknown")

    if weakness_category == "technical":
        focus = "technical depth, system design trade-offs, and quantitative reasoning"
        format_hint = "Focus on architecture, scalability, and implementation details."
    elif weakness_category == "behavioral":
        focus = "STAR-format storytelling, impact quantification, and collaboration"
        format_hint = "Use STAR format: Situation, Task, Action, Result with metrics."
    else:
        focus = "follow-up strategy, negotiation, and resilience"
        format_hint = "Focus on recovery tactics, clarification, and positioning."

    prompt = (
        f"You are an expert interview coach. Generate exactly 3 practice questions to improve {weakness_category} skills.\n\n"
        f"Context:\n- Role: {row.role_name}\n- Weakness: {weakness_category} (score: {weakness_score:.1f}/100)\n"
        f"- Recent challenge: {challenge_question}\n- Focus areas: {focus}\n\n"
        f"Requirements:\n1. Generate exactly 3 questions\n2. {format_hint}\n"
        f"3. Questions should be progressively challenging\n4. Each question should be realistic for a {row.role_name} interview\n\n"
        f"Format your response as:\nQUESTION 1: [question text]\nQUESTION 2: [question text]\nQUESTION 3: [question text]"
    )

    raw_response = gemini_client.generate(prompt, temperature=0.4, max_tokens=512)
    if not raw_response:
        raise HTTPException(status_code=502, detail="Gemini API failed")

    questions: List[str] = []
    for i in range(1, 4):
        match = re.compile(rf"QUESTION {i}:\s*(.*?)(?=QUESTION {i + 1}:|$)", re.S).search(raw_response)
        if match:
            questions.append(match.group(1).strip())

    if len(questions) < 3:
        lines = [l.strip() for l in raw_response.split("\n") if l.strip() and not l.strip().upper().startswith("QUESTION")]
        questions = (questions + lines)[:3]

    logger.debug(f"Practice drill generated: {weakness_category} with {len(questions)} questions for interview {interview_id}")

    return Feature2PracticeDrillResponse(
        interview_id=interview_id,
        weakness_category=weakness_category,
        weakness_score=weakness_score,
        questions=questions[:3],
        generated_at=datetime.now(timezone.utc),
    )


# ─── Chunk 3.4: AssemblyAI Webhook Endpoint ──────────────────────────────────

def _run_analysis_and_update(row_id: int, transcript_text: str) -> None:
    """Background task: run full Feature2Engine analysis and update the DB record."""
    from ..db import engine as db_engine  # import here to avoid circular at module level

    with Session(db_engine) as session:
        row = session.get(Feature2InterviewAutopsy, row_id)
        if row is None:
            logger.error(f"Webhook background task: interview {row_id} not found")
            return

        try:
            eng = Feature2Engine(
                interview_notes="",
                transcript_text=transcript_text,
                transcript_vtt="",
                technical_expectations=[],
                culture_vibe=row.ingestion_json and json.loads(row.ingestion_json).get("culture_vibe", "neutral") or "neutral",
                interviewer_friendliness=5,
                interview_round=row.interview_round,
                lifecycle_stage=row.lifecycle_stage,
                hardest_question_hint=row.challenge_question if row.challenge_question != "Pending transcription" else "",
                advanced_round_reached=row.advanced_round_reached,
                rejection_reason_hint=row.rejection_reason_hint,
                interview_outcome=row.interview_outcome,
                company_stage=row.company_stage,
            )
            result = eng.run()

            row.transcription_status = "completed"
            row.raw_transcript_excerpt = transcript_text[:2000]
            row.challenge_question = result["ingestion"]["challenge_question"]
            row.lifecycle_stage = result["ingestion"]["lifecycle_stage"]
            row.ingestion_json = json.dumps(result["ingestion"], ensure_ascii=True)
            row.technical_json = json.dumps(result["technical"], ensure_ascii=True)
            row.behavioral_json = json.dumps(result["behavioral"], ensure_ascii=True)
            row.strategic_actions_json = json.dumps(result["strategic_actions"], ensure_ascii=True)
            row.analytics_snapshot_json = json.dumps(result["analytics_snapshot"], ensure_ascii=True)
            row.score_json = json.dumps(result["score"], ensure_ascii=True)
            row.ai_insights_json = json.dumps(result.get("ai_insights", {}), ensure_ascii=True)

            session.add(row)
            session.commit()
            logger.info(f"Webhook background task: interview {row_id} analysis complete")

        except Exception as exc:
            logger.error(f"Webhook background task failed for interview {row_id}: {exc}", exc_info=True)
            row.transcription_status = "transcription_failed"
            session.add(row)
            session.commit()


@router.post("/webhooks/assemblyai", tags=["Feature 2: Rebound"])
async def assemblyai_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    Receive AssemblyAI transcription completion webhook.

    AssemblyAI sends:
      POST /api/feature2/webhooks/assemblyai
      Header: X-AssemblyAI-Signature: <hmac-sha256-hex>
      Body: {"transcript_id": "...", "status": "completed"|"error", "text": "...", "error": "..."}
    """
    # 1. Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        logger.warning(f"Webhook rate limit exceeded from {client_ip}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Maximum 100 requests per minute.")

    # 2. Read raw body (needed for signature validation)
    body_bytes = await request.body()

    # 3. Validate signature
    signature = request.headers.get("X-AssemblyAI-Signature", "")
    if not _validate_assemblyai_signature(signature, body_bytes):
        logger.error(f"Webhook signature validation failed from IP {client_ip}")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 4. Parse payload
    try:
        payload: Dict[str, Any] = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    transcript_id = payload.get("transcript_id", "")
    status = payload.get("status", "")

    if not transcript_id:
        raise HTTPException(status_code=400, detail="Missing transcript_id in payload")

    # 5. Find the pending autopsy record
    stmt = select(Feature2InterviewAutopsy).where(
        Feature2InterviewAutopsy.assembly_transcript_id == transcript_id
    )
    row = session.exec(stmt).first()

    if row is None:
        logger.warning(f"Webhook received for unknown transcript_id: {transcript_id}")
        raise HTTPException(status_code=404, detail="Transcript not found")

    # 6. Handle completion vs error
    if status == "completed":
        transcript_text = payload.get("text") or ""
        if not transcript_text.strip():
            # Fetch from AssemblyAI directly if text not embedded in webhook
            api_key = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
            if api_key:
                try:
                    transcript_text = _assemblyai_fetch_transcript(transcript_id, api_key)
                except Exception as exc:
                    logger.error(f"Failed to fetch transcript {transcript_id}: {exc}")

        # Queue analysis as a background task so we return 200 immediately
        background_tasks.add_task(_run_analysis_and_update, row.id, transcript_text)
        logger.info(f"Webhook queued analysis for interview {row.id} (transcript {transcript_id})")

    elif status == "error":
        error_msg = payload.get("error", "Unknown AssemblyAI error")
        row.transcription_status = "transcription_failed"
        session.add(row)
        session.commit()
        logger.error(f"Transcription failed for transcript {transcript_id}: {error_msg}")

    else:
        # Unknown status — log and ignore
        logger.warning(f"Webhook received unknown status '{status}' for transcript {transcript_id}")

    return {"status": "received"}


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
