# we are good - metrics and analytics API ready
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, delete, select

from ..db import get_session
from ..models import AnalyticsEvent, ApplicationLog
from ..schemas_metrics import (
    ApplicationLogIn,
    ApplicationLogOut,
    ApplicationStatusUpdateIn,
    AnalyticsEventIn,
    AnalyticsEventOut,
    AnalyticsIngestResponse,
    DashboardResponse,
    KpiSummaryResponse,
)

router = APIRouter(prefix="/api/metrics", tags=["Metrics & Tracking"])


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _safe_json(raw: str) -> Dict:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    return {}


def _event_counts(events: List[AnalyticsEvent]) -> Counter:
    return Counter(e.event_name for e in events)


def _unique_ids(events: List[AnalyticsEvent], event_name: str, field_name: str) -> set:
    found = set()
    for event in events:
        if event.event_name != event_name:
            continue
        value = getattr(event, field_name, None)
        if value:
            found.add(value)
    return found


def _compute_kpis(events: List[AnalyticsEvent], window_days: int, user_id: Optional[str]) -> KpiSummaryResponse:
    counts = _event_counts(events)

    unique_applications = _unique_ids(events, "application_logged", "application_id")
    unique_invitations = _unique_ids(events, "invitation_received", "application_id")

    if not unique_applications:
        unique_applications = {str(e.id) for e in events if e.event_name == "application_logged"}
    if not unique_invitations:
        unique_invitations = {str(e.id) for e in events if e.event_name == "invitation_received"}

    iir = (len(unique_invitations) / len(unique_applications)) if unique_applications else 0.0

    signed_up_users = {e.user_id for e in events if e.event_name == "user_signed_up"}
    analyzed_users = {e.user_id for e in events if e.event_name == "first_analysis_completed"}
    if not signed_up_users:
        signed_up_users = {e.user_id for e in events}
    activation = (len(analyzed_users) / len(signed_up_users)) if signed_up_users else 0.0

    viewed = counts.get("recommendation_viewed", 0)
    applied = counts.get("recommendation_applied", 0)
    adoption = (applied / viewed) if viewed else 0.0

    selected = counts.get("project_selected_for_narrative", 0)
    stars = counts.get("star_bullets_generated", 0)
    narrative_coverage = (stars / selected) if selected else 0.0

    first_app_times = sorted(e.occurred_at_utc for e in events if e.event_name == "application_logged")
    first_invite_times = sorted(e.occurred_at_utc for e in events if e.event_name == "invitation_received")
    time_to_first_invitation_days = None
    if first_app_times and first_invite_times:
        delta = first_invite_times[0] - first_app_times[0]
        time_to_first_invitation_days = round(delta.total_seconds() / 86400, 2)

    return KpiSummaryResponse(
        window_days=window_days,
        generated_at_utc=_utc_now(),
        user_id=user_id,
        interview_invitation_rate=round(iir, 4),
        activation_rate=round(activation, 4),
        recommendation_adoption_rate=round(adoption, 4),
        narrative_coverage=round(narrative_coverage, 4),
        time_to_first_invitation_days=time_to_first_invitation_days,
        counts={
            "events": len(events),
            "applications": len(unique_applications),
            "invitations": len(unique_invitations),
            "recommendation_viewed": viewed,
            "recommendation_applied": applied,
            "project_selected_for_narrative": selected,
            "star_bullets_generated": stars,
        },
    )


def _compute_reliability(events: List[AnalyticsEvent]) -> Dict:
    duplicates = 0
    seen = set()
    latencies = []

    for e in events:
        dedupe_key = (e.user_id, e.session_id, e.event_name, e.occurred_at_utc.isoformat())
        if dedupe_key in seen:
            duplicates += 1
        else:
            seen.add(dedupe_key)

        meta = _safe_json(e.metadata_json)
        latency = meta.get("processing_latency_ms")
        if isinstance(latency, (int, float)):
            latencies.append(float(latency))

    latencies.sort()
    p50 = latencies[len(latencies) // 2] if latencies else None
    p95 = latencies[int(len(latencies) * 0.95) - 1] if len(latencies) >= 1 else None

    return {
        "duplicate_event_rate": round((duplicates / len(events)), 4) if events else 0.0,
        "event_loss_rate": None,
        "analysis_latency_p50_ms": round(p50, 2) if p50 is not None else None,
        "analysis_latency_p95_ms": round(p95, 2) if p95 is not None else None,
    }


def _load_events(session: Session, window_days: int, user_id: Optional[str]) -> List[AnalyticsEvent]:
    since = _utc_now() - timedelta(days=max(1, window_days))
    stmt = select(AnalyticsEvent).where(AnalyticsEvent.occurred_at_utc >= since)
    if user_id:
        stmt = stmt.where(AnalyticsEvent.user_id == user_id)
    return list(session.exec(stmt).all())


def _append_event(
    session: Session,
    *,
    event_name: str,
    user_id: str,
    session_id: str,
    feature_area: str,
    metadata: Optional[Dict] = None,
    application_id: Optional[str] = None,
):
    row = AnalyticsEvent(
        event_name=event_name,
        event_version="1.0",
        occurred_at_utc=_utc_now(),
        user_id=user_id,
        session_id=session_id,
        platform="web",
        feature_area=feature_area,
        application_id=application_id,
        metadata_json=json.dumps(metadata or {}),
    )
    session.add(row)


@router.post("/events", response_model=AnalyticsIngestResponse)
def ingest_events(payload: List[AnalyticsEventIn], session: Session = Depends(get_session)):
    """
    Ingest analytics events with deduplication (8.6).
    Duplicate = same (user_id, session_id, event_name, occurred_at_utc minute bucket).
    """
    accepted = []
    skipped = 0

    # Build dedup key set from recent events in DB (last 5 minutes)
    from datetime import timedelta
    cutoff = _utc_now() - timedelta(minutes=5)
    recent = session.exec(
        select(AnalyticsEvent).where(AnalyticsEvent.occurred_at_utc >= cutoff)
    ).all()
    existing_keys = {
        (e.user_id, e.session_id, e.event_name,
         e.occurred_at_utc.replace(second=0, microsecond=0).isoformat())
        for e in recent
    }

    # Also deduplicate within the batch itself
    batch_keys: set = set()

    for item in payload:
        # Minute-bucket dedup key
        bucket = item.occurred_at_utc.replace(second=0, microsecond=0).isoformat()
        dedup_key = (item.user_id, item.session_id, item.event_name, bucket)

        if dedup_key in existing_keys or dedup_key in batch_keys:
            skipped += 1
            continue

        batch_keys.add(dedup_key)
        existing_keys.add(dedup_key)

        row = AnalyticsEvent(
            event_name=item.event_name,
            event_version=item.event_version,
            occurred_at_utc=item.occurred_at_utc,
            user_id=item.user_id,
            session_id=item.session_id,
            platform=item.platform,
            feature_area=item.feature_area,
            resume_id=item.resume_id,
            jd_id=item.jd_id,
            application_id=item.application_id,
            interview_id=item.interview_id,
            project_id=item.project_id,
            metadata_json=json.dumps(item.metadata_json),
        )
        session.add(row)
        accepted.append(row)

    session.commit()
    for row in accepted:
        session.refresh(row)

    return AnalyticsIngestResponse(
        accepted=len(accepted),
        rejected=skipped,
        events=[
            AnalyticsEventOut(
                event_id=row.id,
                event_name=row.event_name,
                occurred_at_utc=row.occurred_at_utc,
            )
            for row in accepted
        ],
    )


@router.get("/kpis", response_model=KpiSummaryResponse)
def kpis(
    window_days: int = Query(default=28, ge=1, le=365),
    user_id: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
):
    events = _load_events(session, window_days=window_days, user_id=user_id)
    return _compute_kpis(events, window_days=window_days, user_id=user_id)


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    window_days: int = Query(default=28, ge=1, le=365),
    user_id: Optional[str] = Query(default=None),
    session: Session = Depends(get_session),
):
    events = _load_events(session, window_days=window_days, user_id=user_id)
    kpi = _compute_kpis(events, window_days=window_days, user_id=user_id)

    counts = _event_counts(events)
    reliability = _compute_reliability(events)

    funnel = {
        "signed_up": counts.get("user_signed_up", 0),
        "first_analysis_completed": counts.get("first_analysis_completed", 0),
        "application_logged": counts.get("application_logged", 0),
        "invitation_received": counts.get("invitation_received", 0),
    }

    feature_impact = {
        "recommendation_adoption_rate": kpi.recommendation_adoption_rate,
        "narrative_exports": counts.get("narrative_exported", 0),
        "resume_exports": counts.get("resume_exported", 0),
    }

    return DashboardResponse(
        kpi_panel=kpi.model_dump(),
        funnel_panel=funnel,
        feature_impact_panel=feature_impact,
        reliability_panel=reliability,
    )


@router.post("/applications", response_model=ApplicationLogOut)
def log_application(payload: ApplicationLogIn, session: Session = Depends(get_session)):
    existing = session.exec(
        select(ApplicationLog).where(
            ApplicationLog.user_id == payload.user_id,
            ApplicationLog.application_id == payload.application_id,
        )
    ).first()

    if existing is None:
        row = ApplicationLog(
            user_id=payload.user_id,
            application_id=payload.application_id,
            company_name_normalized=payload.company_name_normalized,
            role_name_normalized=payload.role_name_normalized,
            channel=payload.channel,
            status="submitted",
        )
        session.add(row)
    else:
        row = existing

    _append_event(
        session,
        event_name="application_logged",
        user_id=payload.user_id,
        session_id=f"application-{payload.application_id}",
        feature_area="applications",
        metadata={
            "company_name_normalized": payload.company_name_normalized,
            "role_name_normalized": payload.role_name_normalized,
            "channel": payload.channel,
        },
        application_id=payload.application_id,
    )
    session.commit()
    session.refresh(row)

    return ApplicationLogOut(
        id=row.id,
        user_id=row.user_id,
        application_id=row.application_id,
        company_name_normalized=row.company_name_normalized,
        role_name_normalized=row.role_name_normalized,
        channel=row.channel,
        status=row.status,
        status_reason=row.status_reason,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.patch("/applications/{application_id}", response_model=ApplicationLogOut)
def update_application_status(application_id: str, payload: ApplicationStatusUpdateIn, user_id: str, session: Session = Depends(get_session)):
    row = session.exec(
        select(ApplicationLog).where(
            ApplicationLog.user_id == user_id,
            ApplicationLog.application_id == application_id,
        )
    ).first()
    if row is None:
        row = ApplicationLog(
            user_id=user_id,
            application_id=application_id,
            company_name_normalized="unknown",
            role_name_normalized="unknown",
            channel="job_board",
            status=payload.status,
            status_reason=payload.status_reason,
        )
        session.add(row)
    else:
        row.status = payload.status
        row.status_reason = payload.status_reason
        row.updated_at = _utc_now()

    if payload.status == "invited":
        event_name = "invitation_received"
    elif payload.status == "rejected":
        event_name = "rejection_logged"
    elif payload.status == "interview_scheduled":
        event_name = "interview_scheduled"
    elif payload.status == "offer":
        event_name = "offer_received"
    else:
        event_name = "application_status_updated"

    _append_event(
        session,
        event_name=event_name,
        user_id=user_id,
        session_id=f"application-{application_id}",
        feature_area="applications",
        metadata={"status": payload.status, "status_reason": payload.status_reason},
        application_id=application_id,
    )
    session.commit()
    session.refresh(row)

    return ApplicationLogOut(
        id=row.id,
        user_id=row.user_id,
        application_id=row.application_id,
        company_name_normalized=row.company_name_normalized,
        role_name_normalized=row.role_name_normalized,
        channel=row.channel,
        status=row.status,
        status_reason=row.status_reason,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/applications/{user_id}", response_model=List[ApplicationLogOut])
def list_applications(user_id: str, session: Session = Depends(get_session)):
    rows = list(
        session.exec(
            select(ApplicationLog)
            .where(ApplicationLog.user_id == user_id)
            .order_by(ApplicationLog.updated_at.desc())
        ).all()
    )

    return [
        ApplicationLogOut(
            id=row.id,
            user_id=row.user_id,
            application_id=row.application_id,
            company_name_normalized=row.company_name_normalized,
            role_name_normalized=row.role_name_normalized,
            channel=row.channel,
            status=row.status,
            status_reason=row.status_reason,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


@router.get("/users/{user_id}/export")
def export_user_metrics_data(user_id: str, session: Session = Depends(get_session)):
    events = list(
        session.exec(
            select(AnalyticsEvent)
            .where(AnalyticsEvent.user_id == user_id)
            .order_by(AnalyticsEvent.occurred_at_utc.desc())
        ).all()
    )
    applications = list(
        session.exec(
            select(ApplicationLog)
            .where(ApplicationLog.user_id == user_id)
            .order_by(ApplicationLog.updated_at.desc())
        ).all()
    )

    return {
        "user_id": user_id,
        "exported_at_utc": _utc_now(),
        "events": [
            {
                "id": e.id,
                "event_name": e.event_name,
                "event_version": e.event_version,
                "occurred_at_utc": e.occurred_at_utc,
                "session_id": e.session_id,
                "platform": e.platform,
                "feature_area": e.feature_area,
                "application_id": e.application_id,
                "metadata_json": _safe_json(e.metadata_json),
            }
            for e in events
        ],
        "applications": [
            {
                "id": a.id,
                "application_id": a.application_id,
                "company_name_normalized": a.company_name_normalized,
                "role_name_normalized": a.role_name_normalized,
                "channel": a.channel,
                "status": a.status,
                "status_reason": a.status_reason,
                "created_at": a.created_at,
                "updated_at": a.updated_at,
            }
            for a in applications
        ],
    }


@router.delete("/users/{user_id}")
def delete_user_metrics_data(user_id: str, session: Session = Depends(get_session)):
    events_deleted = session.exec(
        delete(AnalyticsEvent).where(AnalyticsEvent.user_id == user_id)
    )
    apps_deleted = session.exec(
        delete(ApplicationLog).where(ApplicationLog.user_id == user_id)
    )
    session.commit()

    return {
        "user_id": user_id,
        "deleted": True,
        "events_deleted": events_deleted.rowcount if hasattr(events_deleted, "rowcount") else None,
        "applications_deleted": apps_deleted.rowcount if hasattr(apps_deleted, "rowcount") else None,
    }
