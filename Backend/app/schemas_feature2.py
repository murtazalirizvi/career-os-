from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Feature2CreateInterviewRequest(BaseModel):
    candidate_id: str = Field(min_length=2, max_length=120)
    interview_round: str = Field(default="tech", description="screening|tech|hr|manager")
    company_name: str = Field(default="Unknown")
    role_name: str = Field(default="Software Engineer")
    interview_notes: str = Field(default="", description="Voice-to-text debrief or raw notes")
    transcript_text: str = Field(default="", description="Optional plain transcript text")
    transcript_vtt: str = Field(default="", description="Optional VTT content")
    assembly_audio_url: str = Field(default="", description="Optional public audio URL for AssemblyAI transcription")
    use_assemblyai: bool = Field(default=False)
    culture_vibe: str = Field(default="neutral")
    interviewer_friendliness: int = Field(default=5, ge=1, le=10)
    hardest_question_hint: str = Field(default="")
    lifecycle_stage: str = Field(default="tech")
    technical_expectations: List[str] = Field(default_factory=list)
    interview_outcome: str = Field(default="rejected")
    rejection_reason_hint: str = Field(default="")
    advanced_round_reached: bool = Field(default=False)


class Feature2ScoreCard(BaseModel):
    technical_accuracy: float
    behavioral_quality: float
    strategic_recovery_readiness: float
    confidence_risk: float
    overall_autopsy_score: float


class Feature2InterviewResponse(BaseModel):
    interview_id: int
    candidate_id: str
    company_name: str
    role_name: str
    interview_round: str
    lifecycle_stage: str
    challenge_question: str
    score: Feature2ScoreCard
    ingestion: Dict[str, Any]
    technical: Dict[str, Any]
    behavioral: Dict[str, Any]
    strategic_actions: Dict[str, Any]
    analytics_snapshot: Dict[str, Any]
    created_at: datetime


class Feature2TrendPoint(BaseModel):
    interview_id: int
    created_at: datetime
    technical_accuracy: float
    behavioral_quality: float
    recovery_readiness: float
    overall_score: float


class Feature2TrendResponse(BaseModel):
    candidate_id: str
    points: List[Feature2TrendPoint]
    trend_summary: Dict[str, float]


class Feature2ForecastResponse(BaseModel):
    candidate_id: str
    readiness_score: float
    forecast_label: str
    expected_offer_window_weeks: int
    rationale: List[str]


class Feature2JourneyExportResponse(BaseModel):
    candidate_id: str
    report_path: str
    interview_count: int


class Feature2ReminderResponse(BaseModel):
    interview_id: int
    reminders: List[Dict[str, Any]]


class Feature2QuickDebriefRequest(BaseModel):
    debrief_text: str


class Feature2QuickDebriefResponse(BaseModel):
    extracted_hardest_question: str
    top_failure_themes: List[str]
    immediate_next_actions: List[str]
