from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AnalyticsEventIn(BaseModel):
    event_name: str = Field(min_length=3, max_length=120)
    event_version: str = Field(default="1.0", min_length=1, max_length=20)
    occurred_at_utc: datetime
    user_id: str = Field(min_length=1, max_length=120)
    session_id: str = Field(min_length=1, max_length=120)
    platform: Literal["web"] = "web"
    feature_area: str = Field(min_length=1, max_length=80)

    resume_id: Optional[str] = None
    jd_id: Optional[str] = None
    application_id: Optional[str] = None
    interview_id: Optional[str] = None
    project_id: Optional[str] = None

    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsEventOut(BaseModel):
    event_id: int
    event_name: str
    occurred_at_utc: datetime


class AnalyticsIngestResponse(BaseModel):
    accepted: int
    rejected: int
    events: List[AnalyticsEventOut]


class KpiSummaryResponse(BaseModel):
    window_days: int
    generated_at_utc: datetime
    user_id: Optional[str] = None

    interview_invitation_rate: float
    activation_rate: float
    recommendation_adoption_rate: float
    narrative_coverage: float
    time_to_first_invitation_days: Optional[float] = None

    counts: Dict[str, int]


class DashboardResponse(BaseModel):
    kpi_panel: Dict[str, Any]
    funnel_panel: Dict[str, Any]
    feature_impact_panel: Dict[str, Any]
    reliability_panel: Dict[str, Any]


class ApplicationLogIn(BaseModel):
    user_id: str = Field(min_length=1, max_length=120)
    application_id: str = Field(min_length=1, max_length=120)
    company_name_normalized: str = Field(min_length=1, max_length=120)
    role_name_normalized: str = Field(min_length=1, max_length=120)
    channel: str = Field(default="job_board", min_length=1, max_length=50)


class ApplicationStatusUpdateIn(BaseModel):
    status: str = Field(min_length=1, max_length=50)
    status_reason: str = Field(default="", max_length=400)


class ApplicationLogOut(BaseModel):
    id: int
    user_id: str
    application_id: str
    company_name_normalized: str
    role_name_normalized: str
    channel: str
    status: str
    status_reason: str
    created_at: datetime
    updated_at: datetime
