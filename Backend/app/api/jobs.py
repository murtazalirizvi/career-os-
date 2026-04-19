"""
Job Tracker API — CRUD endpoints protected by the existing session-token auth.

Routes
------
GET    /api/jobs            → list current user's jobs
POST   /api/jobs            → create a job
PATCH  /api/jobs/{job_id}   → partial update
DELETE /api/jobs/{job_id}   → delete
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlmodel import Session, select

from ..db import get_session
from ..models import UserAccount, UserSessionToken
from ..models_jobs import Job
from ..schemas_jobs import JobCreate, JobRead, JobUpdate

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


# ── Auth dependency (mirrors the pattern in api/auth.py) ─────────────────────

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
    """Resolve a Bearer token to a UserAccount or raise 401."""
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


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[JobRead])
def list_jobs(
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Job]:
    """Return all jobs belonging to the authenticated user."""
    jobs = session.exec(
        select(Job).where(Job.owner_id == current_user.id)
    ).all()
    return list(jobs)


@router.post("", response_model=JobRead, status_code=201)
def create_job(
    payload: JobCreate,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Job:
    job = Job(
        owner_id=current_user.id,
        company=payload.company,
        position=payload.position,
        status=payload.status,
        date_applied=payload.date_applied,
        salary=payload.salary,
        notes=payload.notes,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@router.patch("/{job_id}", response_model=JobRead)
def update_job(
    job_id: int,
    payload: JobUpdate,
    current_user: UserAccount = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Job:
    job = session.get(Job, job_id)
    if job is None or job.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    job.updated_at = _utc_now()

    session.add(job)
    session.commit()
    session.refresh(job)
    return job


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
