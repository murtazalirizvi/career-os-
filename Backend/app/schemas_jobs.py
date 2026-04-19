"""
Pydantic / SQLModel schemas for the Job Tracker API.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from .models_jobs import JobStatus


# ── Request bodies ────────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=200)
    status: JobStatus = JobStatus.wishlist
    date_applied: Optional[date] = None
    salary: Optional[str] = Field(default=None, max_length=80)
    notes: Optional[str] = Field(default=None, max_length=2000)


class JobUpdate(BaseModel):
    """All fields optional — PATCH semantics."""
    company: Optional[str] = Field(default=None, min_length=1, max_length=200)
    position: Optional[str] = Field(default=None, min_length=1, max_length=200)
    status: Optional[JobStatus] = None
    date_applied: Optional[date] = None
    salary: Optional[str] = Field(default=None, max_length=80)
    notes: Optional[str] = Field(default=None, max_length=2000)


# ── Response bodies ───────────────────────────────────────────────────────────

class JobRead(BaseModel):
    id: int
    owner_id: int
    company: str
    position: str
    status: JobStatus
    date_applied: Optional[date]
    salary: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
