from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import (
    ApplicationLog,
    Feature1Analysis,
    Feature2InterviewAutopsy,
    Feature3GapSnapshot,
    Feature3MarketSnapshot,
    Feature5NarrativeSession,
)
from ..schemas_core import CoreLoopSummaryResponse

router = APIRouter(prefix="/api/core", tags=["Core Loop"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _latest(session: Session, model, candidate_id: str):
    stmt = select(model).where(model.candidate_id == candidate_id).order_by(model.created_at.desc())
    return session.exec(stmt).first()


def _latest_gap_for_candidate(session: Session, candidate_id: str) -> Optional[Feature3GapSnapshot]:
    stmt = select(Feature3GapSnapshot).where(Feature3GapSnapshot.candidate_id == candidate_id).order_by(Feature3GapSnapshot.created_at.desc())
    return session.exec(stmt).first()


def _readiness_score(feature1: Optional[Feature1Analysis], feature2: Optional[Feature2InterviewAutopsy], feature3: Optional[Feature3GapSnapshot], feature5: Optional[Feature5NarrativeSession]) -> float:
    parts = []
    if feature1:
        parts.append(float(feature1.overall_score))
    if feature2:
        try:
            score = json.loads(feature2.score_json).get("overall_autopsy_score")
            if score is not None:
                parts.append(float(score))
        except json.JSONDecodeError:
            pass
    if feature3:
        parts.append(float(feature3.match_score))
    if feature5:
        try:
            consistency = json.loads(feature5.consistency_json).get("consistency_score")
            if consistency is not None:
                parts.append(float(consistency))
        except json.JSONDecodeError:
            pass

    if not parts:
        return 0.0
    return round(sum(parts) / len(parts), 2)


def _label(score: float) -> str:
    if score >= 85:
        return "high"
    if score >= 65:
        return "medium"
    if score >= 40:
        return "low"
    return "critical"


@router.get("/daily-plan/{candidate_id}", response_model=CoreLoopSummaryResponse)
def daily_plan(candidate_id: str, session: Session = Depends(get_session)):
    latest_f1 = _latest(session, Feature1Analysis, candidate_id)
    latest_f2 = _latest(session, Feature2InterviewAutopsy, candidate_id)
    latest_f3 = _latest_gap_for_candidate(session, candidate_id)
    latest_f5 = _latest(session, Feature5NarrativeSession, candidate_id)

    app_rows = list(
        session.exec(
            select(ApplicationLog)
            .where(ApplicationLog.user_id == candidate_id)
            .order_by(ApplicationLog.updated_at.desc())
        ).all()
    )

    blockers: List[str] = []
    focus: List[str] = []
    actions: List[Dict] = []

    if not latest_f1:
        blockers.append("No resume analysis yet")
        actions.append({"priority": 1, "title": "Run Feature 1 analysis", "reason": "Need ATS and semantic baseline before optimization."})
    else:
        if latest_f1.overall_score < 80:
            focus.append("Improve resume score above 80")
            actions.append({"priority": 1, "title": "Apply top 3 resume recommendations", "reason": "Fastest lever for callback lift."})

    if not latest_f5:
        blockers.append("Narrative artifacts missing")
        actions.append({"priority": 2, "title": "Run Feature 5 narrative architect", "reason": "Needed for STAR and interview storytelling."})
    else:
        focus.append("Keep narrative exports synchronized")

    if not latest_f3:
        blockers.append("No market-fit gap map")
        actions.append({"priority": 2, "title": "Run Feature 3 arbitrage", "reason": "Identify highest ROI weekly skill move."})
    elif latest_f3.match_score < 70:
        focus.append("Close role-fit gap with sprint")
        actions.append({"priority": 2, "title": "Complete one skill sprint checkpoint", "reason": "Directly improves role-fit score."})

    if not latest_f2:
        actions.append({"priority": 3, "title": "Run Feature 2 debrief after each interview", "reason": "Prevents repeated failure patterns."})

    submitted = sum(1 for row in app_rows if row.status in {"submitted", "invited", "interview_scheduled", "offer"})
    invited = sum(1 for row in app_rows if row.status in {"invited", "interview_scheduled", "offer"})
    iir = round((invited / submitted), 4) if submitted else 0.0

    if submitted < 5:
        focus.append("Increase weekly applications")
        actions.append({"priority": 3, "title": "Log at least 5 targeted applications/week", "reason": "Higher sample size stabilizes interview velocity."})

    score = _readiness_score(latest_f1, latest_f2, latest_f3, latest_f5)

    return CoreLoopSummaryResponse(
        candidate_id=candidate_id,
        generated_at_utc=_utc_now(),
        readiness_score=score,
        confidence_label=_label(score),
        latest_refs={
            "feature1_analysis_id": latest_f1.id if latest_f1 else None,
            "feature2_interview_id": latest_f2.id if latest_f2 else None,
            "feature3_gap_snapshot_id": latest_f3.id if latest_f3 else None,
            "feature5_session_id": latest_f5.id if latest_f5 else None,
        },
        focus_today=list(dict.fromkeys(focus))[:5],
        blockers=blockers,
        next_actions=sorted(actions, key=lambda x: x["priority"])[:6],
        metrics_snapshot={
            "applications_logged": submitted,
            "invitations_received": invited,
            "interview_invitation_rate": iir,
        },
    )
