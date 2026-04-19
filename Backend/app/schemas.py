from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HeatZone(BaseModel):
    x: float
    y: float
    weight: float
    label: str


class Feature1ScoreBreakdown(BaseModel):
    overall: float
    visual_hierarchy: float
    ats_integrity: float
    semantic_match: float
    competitive_benchmark: float


class Feature1AnalysisResponse(BaseModel):
    analysis_id: int
    candidate_id: str
    version_number: int
    job_category: str
    score: Feature1ScoreBreakdown
    summaries: Dict[str, str]
    metrics: Dict[str, Any]
    hot_zones: List[HeatZone]
    recommendations: List[str]
    ready_to_apply: bool
    created_at: datetime


class Feature1VersionSummary(BaseModel):
    analysis_id: int
    version_number: int
    job_category: str
    overall_score: float
    created_at: datetime


class Feature1ComparisonResponse(BaseModel):
    candidate_id: str
    left_version: int
    right_version: int
    score_delta: Dict[str, float]
    recommendation_delta: Dict[str, List[str]]


class ReadyToApplyResponse(BaseModel):
    analysis_id: int
    eligible: bool
    score: float
    threshold: float = 90.0
    badge_label: Optional[str] = None


class Feature1ReportResponse(BaseModel):
    analysis_id: int
    report_path: str
    format: str = "md"


class AddVersionTagRequest(BaseModel):
    tag: str = Field(min_length=1, max_length=80)
