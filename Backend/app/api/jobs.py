"""
we are good - job tracker API routes working

Job Tracker API — CRUD + Chunk 7 enhancements.

Routes
------
GET    /api/jobs                    → list current user's jobs
POST   /api/jobs                    → create a job
PATCH  /api/jobs/{job_id}           → partial update
DELETE /api/jobs/{job_id}           → delete
GET    /api/jobs/stats              → pipeline counts per status (7.1)
POST   /api/jobs/{job_id}/notes     → append timestamped note (7.2)
GET    /api/jobs/export             → CSV export (7.4)
GET    /api/jobs/due-today          → jobs with next_action_date = today (7.6)
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from datetime import date, datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from ..db import get_session
from ..models import UserAccount, UserSessionToken
from ..models_jobs import Job, JobStatus
from ..schemas_jobs import (
    JobAppendNoteRequest,
    JobCreate,
    JobRead,
    JobStatsResponse,
    JobUpdate,
)

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


# ── Auth dependency ───────────────────────────────────────────────────────────

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _secret() -> str:
    return os.getenv("CAREER_OS_AUTH_SECRET", "career-os-dev-secret-change-me")


def _hash_token(raw: str) -> str:
    return hashlib.sha256(f"{raw}:{_secret()}".encode()).hexdigest()


def get_current_user(
    authorization: str = Header(default=""),
    session: Session = Depends(get_session),
) -> UserAccount:
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token.")

    raw = authorization.split(" ", 1)[1].strip()
    token_hash = _hash_token(raw)

    token = session.exec(
        select(UserSessionToken).where(UserSessionToken.token_hash == token_hash)
    ).first()

    if (
        token is None
        or token.revoked_at is not None
        or _as_utc(token.expires_at) < _utc_now()
    ):
        raise HTTPException(status_code=401, detail="Session is invalid or expired.")

    user = session.get(UserAccount, token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive.")

    return user


def _job_to_read(job: Job) -> JobRead:
    """Convert Job ORM object to JobRead, parsing notes_history JSON."""
    try:
        notes_history = json.loads(job.notes_history) if job.notes_history else []
    except (json.JSONDecodeError, TypeError):
        notes_history = []

    return JobRead(
        id=job.id,
        owner_id=job.owner_id,
        company=job.company,
        position=job.position,
        status=job.status,
        date_applied=job.date_applied,
        salary=job.salary,
        notes=job.notes,
        notes_history=notes_history,
        contact_name=job.contact_name or "",
        contact_email=job.contact_email or "",
        job_url=job.job_url or "",
        priority=job.priority or "Medium",
        next_action_date=job.next_action_date,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


# ── Core CRUD ─────────────────────────────────────────────────────────────────

@router.get("", response_model=List[JobRead])
def list_jobs(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[JobRead]:
    jobs = session.exec(
        select(Job).where(Job.owner_id == current_user.id)
    ).all()
    return [_job_to_read(j) for j in jobs]


@router.post("", response_model=JobRead, status_code=201)
def create_job(
    payload: JobCreate,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> JobRead:
    job = Job(
        owner_id=current_user.id,
        company=payload.company,
        position=payload.position,
        status=payload.status,
        date_applied=payload.date_applied,
        salary=payload.salary,
        notes=payload.notes,
        notes_history="[]",
        contact_name=payload.contact_name,
        contact_email=payload.contact_email,
        job_url=payload.job_url,
        priority=payload.priority.value if payload.priority else "Medium",
        next_action_date=payload.next_action_date,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return _job_to_read(job)


@router.patch("/{job_id}", response_model=JobRead)
def update_job(
    job_id: int,
    payload: JobUpdate,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> JobRead:
    job = session.get(Job, job_id)
    if job is None or job.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "priority" and value is not None:
            setattr(job, field, value.value if hasattr(value, "value") else value)
        else:
            setattr(job, field, value)
    job.updated_at = _utc_now()

    session.add(job)
    session.commit()
    session.refresh(job)
    return _job_to_read(job)


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response:
    job = session.get(Job, job_id)
    if job is None or job.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found.")

    session.delete(job)
    session.commit()
    return Response(status_code=204)


# ── Chunk 7.1: Stats endpoint ─────────────────────────────────────────────────

@router.get("/stats", response_model=JobStatsResponse)
def get_job_stats(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> JobStatsResponse:
    """Return pipeline counts per status and priority."""
    jobs = session.exec(
        select(Job).where(Job.owner_id == current_user.id)
    ).all()

    by_status: dict = {s.value: 0 for s in JobStatus}
    by_priority: dict = {"High": 0, "Medium": 0, "Low": 0}

    for job in jobs:
        by_status[job.status.value] = by_status.get(job.status.value, 0) + 1
        p = job.priority or "Medium"
        by_priority[p] = by_priority.get(p, 0) + 1

    return JobStatsResponse(
        total=len(jobs),
        by_status=by_status,
        by_priority=by_priority,
    )


# ── Chunk 7.2: Append note endpoint ──────────────────────────────────────────

@router.post("/{job_id}/notes", response_model=JobRead)
def append_note(
    job_id: int,
    payload: JobAppendNoteRequest,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> JobRead:
    """Append a timestamped note to notes_history (append-only log)."""
    job = session.get(Job, job_id)
    if job is None or job.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found.")

    try:
        history = json.loads(job.notes_history) if job.notes_history else []
    except (json.JSONDecodeError, TypeError):
        history = []

    history.append({
        "note": payload.note,
        "timestamp": _utc_now().isoformat(),
    })

    job.notes_history = json.dumps(history, ensure_ascii=True)
    job.updated_at = _utc_now()
    session.add(job)
    session.commit()
    session.refresh(job)
    return _job_to_read(job)


# ── Chunk 7.4: CSV export endpoint ───────────────────────────────────────────

@router.get("/export")
def export_jobs_csv(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    """Export all jobs as a CSV file."""
    jobs = session.exec(
        select(Job).where(Job.owner_id == current_user.id)
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "id", "company", "position", "status", "priority",
        "date_applied", "salary", "contact_name", "contact_email",
        "job_url", "next_action_date", "notes", "created_at", "updated_at",
    ])

    for job in jobs:
        writer.writerow([
            job.id,
            job.company,
            job.position,
            job.status.value,
            job.priority or "Medium",
            str(job.date_applied) if job.date_applied else "",
            job.salary or "",
            job.contact_name or "",
            job.contact_email or "",
            job.job_url or "",
            str(job.next_action_date) if job.next_action_date else "",
            job.notes or "",
            job.created_at.isoformat(),
            job.updated_at.isoformat(),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=jobs_export.csv"},
    )


# ── Chunk 7.6: Due-today endpoint ─────────────────────────────────────────────

@router.get("/due-today", response_model=List[JobRead])
def get_due_today(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[JobRead]:
    """Return jobs where next_action_date is today or overdue."""
    today = date.today()
    jobs = session.exec(
        select(Job).where(
            Job.owner_id == current_user.id,
            Job.next_action_date <= today,
            Job.next_action_date != None,  # noqa: E711
        )
    ).all()
    return [_job_to_read(j) for j in jobs]
