"""
Pydantic / SQLModel schemas for the Job Tracker API.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .models_jobs import JobPriority, JobStatus


# ── Request bodies ────────────────────────────────────────────────────────────

class JobCreate(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=200)
    status: JobStatus = JobStatus.wishlist
    date_applied: Optional[date] = None
    salary: Optional[str] = Field(default=None, max_length=80)
    notes: Optional[str] = Field(default=None, max_length=2000)
    # Chunk 7 enhancements
    contact_name: str = Field(default="", max_length=200)
    contact_email: str = Field(default="", max_length=200)
    job_url: str = Field(default="", max_length=500)
    priority: JobPriority = JobPriority.medium
    next_action_date: Optional[date] = None


class JobUpdate(BaseModel):
    """All fields optional — PATCH semantics."""
    company: Optional[str] = Field(default=None, min_length=1, max_length=200)
    position: Optional[str] = Field(default=None, min_length=1, max_length=200)
    status: Optional[JobStatus] = None
    date_applied: Optional[date] = None
    salary: Optional[str] = Field(default=None, max_length=80)
    notes: Optional[str] = Field(default=None, max_length=2000)
    # Chunk 7 enhancements
    contact_name: Optional[str] = Field(default=None, max_length=200)
    contact_email: Optional[str] = Field(default=None, max_length=200)
    job_url: Optional[str] = Field(default=None, max_length=500)
    priority: Optional[JobPriority] = None
    next_action_date: Optional[date] = None


class JobAppendNoteRequest(BaseModel):
    """Append a timestamped note to notes_history."""
    note: str = Field(min_length=1, max_length=2000)


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
    # Chunk 7 enhancements
    notes_history: List[Dict[str, Any]] = []
    contact_name: str = ""
    contact_email: str = ""
    job_url: str = ""
    priority: str = "Medium"
    next_action_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Chunk 7: New response schemas ─────────────────────────────────────────────

class JobStatsResponse(BaseModel):
    """Pipeline counts per status (7.1)."""
    total: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]


class JobExportRow(BaseModel):
    """Single row in CSV export (7.4)."""
    id: int
    company: str
    position: str
    status: str
    priority: str
    date_applied: Optional[str]
    salary: Optional[str]
    contact_name: str
    contact_email: str
    job_url: str
    next_action_date: Optional[str]
    notes: Optional[str]
    created_at: str
