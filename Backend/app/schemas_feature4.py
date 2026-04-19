from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Feature4CreateSessionRequest(BaseModel):
    candidate_id: str = Field(min_length=2, max_length=120)
    role_name: str = Field(default="Software Engineer")
    persona_mode: str = Field(default="blind", description="stone_faced|rushed_founder|non_tech_hr|deep_diver|blind")
    selected_persona: Optional[str] = None
    language: str = Field(default="english", description="english|hinglish")
    include_video: bool = Field(default=True)
    environment_theme: str = Field(default="zoom")


class Feature4SessionResponse(BaseModel):
    session_id: int
    candidate_id: str
    role_name: str
    persona: Dict[str, Any]
    opening_questions: List[Dict[str, Any]]
    realtime_summary: Dict[str, Any]
    status: str
    created_at: datetime


class Feature4TurnRequest(BaseModel):
    utterance: str = Field(min_length=1)
    response_latency_ms: int = Field(default=1200, ge=0, le=600000)
    audio_pitch_variance: float = Field(default=0.5, ge=0, le=2.0)
    silent_seconds: float = Field(default=0.0, ge=0, le=180.0)
    gaze_focus_ratio: float = Field(default=0.65, ge=0, le=1)


class Feature4TurnResponse(BaseModel):
    turn_id: int
    session_id: int
    realtime_signals: Dict[str, Any]
    deep_logic: Dict[str, Any]
    whisper_hint: str
    next_question: Dict[str, Any]
    updated_summary: Dict[str, Any]


class Feature4FinalizeResponse(BaseModel):
    session_id: int
    scorecard: Dict[str, float]
    transcript_breakdown: List[Dict[str, Any]]
    improvement_heatmap: Dict[str, Any]
    senior_answer_alternatives: List[Dict[str, str]]
    badges: Dict[str, Any]
    pass_status: Dict[str, Any]
    ai_coaching_report: Dict[str, Any] = {}   # 1.6: Gemini coaching report


class Feature4SynthesisRequest(BaseModel):
    voice_style: str = Field(default="calm")
    avatar_style: str = Field(default="mentor")
    language: str = Field(default="english")
    environment_theme: str = Field(default="zoom")


class Feature4SynthesisResponse(BaseModel):
    session_id: int
    low_latency_audio: Dict[str, Any]
    lip_sync_avatar: Dict[str, Any]
    environment_simulation: Dict[str, Any]
    multilingual_pack: Dict[str, Any]


class Feature4ShareResponse(BaseModel):
    session_id: int
    share_token: str
    expires_at: datetime
    review_url: str


class Feature4SharedSessionResponse(BaseModel):
    session_id: int
    persona: Dict[str, Any]
    scorecard: Dict[str, float]
    transcript_breakdown: List[Dict[str, Any]]
    badges: Dict[str, Any]
    generated_at: datetime


class Feature4HeatmapCompareResponse(BaseModel):
    candidate_id: str
    left_session: int
    right_session: int
    delta: Dict[str, float]
    narrative: List[str]


class Feature4SessionHistoryItem(BaseModel):
    session_id: int
    role_name: str
    persona_key: str
    status: str
    overall_score: Optional[float] = None
    created_at: datetime


class Feature4SessionHistoryResponse(BaseModel):
    candidate_id: str
    sessions: List[Feature4SessionHistoryItem]
