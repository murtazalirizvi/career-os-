"""
Job Tracker models — Job entity owned by a UserAccount.
Status follows the Kanban pipeline: Wishlist → Applied → Interviewing → Offered → Rejected.
"""
from __future__ import annotations

import enum
from datetime import date, datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(str, enum.Enum):
    wishlist = "Wishlist"
    applied = "Applied"
    interviewing = "Interviewing"
    offered = "Offered"
    rejected = "Rejected"


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(index=True, foreign_key="useraccount.id")

    company: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=200)
    status: JobStatus = Field(default=JobStatus.wishlist, index=True)

    date_applied: Optional[date] = Field(default=None)
    salary: Optional[str] = Field(default=None, max_length=80)   # free-form, e.g. "$120k–$140k"
    notes: Optional[str] = Field(default=None, max_length=2000)

    created_at: datetime = Field(default_factory=_utc_now, index=True)
    updated_at: datetime = Field(default_factory=_utc_now, index=True)
