from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Feature1Analysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: str = Field(index=True)
    job_category: str = Field(index=True)
    resume_filename: str
    resume_path: str
    version_number: int = Field(index=True)

    overall_score: float
    visual_score: float
    ats_score: float
    semantic_score: float
    benchmark_score: float

    eye_tracking_summary: str
    ats_summary: str
    semantic_summary: str
    benchmark_summary: str

    hotzones_json: str
    metrics_json: str
    recommendations_json: str
    ai_recommendations_json: str = Field(default="[]")  # 2.1: Gemini coaching recs
    raw_resume_text: str = Field(default="")  # 1.3/2.3: stored for cross-feature reuse

    created_at: datetime = Field(default_factory=utc_now, index=True)


class Feature1VersionTag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    analysis_id: int = Field(index=True, foreign_key="feature1analysis.id")
    candidate_id: str = Field(index=True)
    tag: str = Field(index=True)
    created_at: datetime = Field(default_factory=utc_now)


class Feature2InterviewAutopsy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: str = Field(index=True)
    company_name: str = Field(index=True)
    role_name: str = Field(index=True)
    interview_round: str = Field(index=True)
    lifecycle_stage: str = Field(index=True)
    challenge_question: str

    interview_outcome: str = Field(index=True)
    rejection_reason_hint: str = ""
    advanced_round_reached: bool = False

    ingestion_json: str
    technical_json: str
    behavioral_json: str
    strategic_actions_json: str
    analytics_snapshot_json: str
    score_json: str

    transcript_source: str = "voice_notes"
    raw_transcript_excerpt: str = ""
    ai_insights_json: str = Field(default="{}")  # 1.4: persisted Gemini autopsy

    # Chunk 3 enhancements
    interview_date: datetime = Field(default_factory=utc_now, index=True, description="Actual interview date (distinct from created_at)")
    company_stage: str = Field(default="scaleup", index=True, description="Company maturity: startup|scaleup|enterprise")
    transcription_status: str = Field(default="completed", index=True, description="Status: transcribing|completed|transcription_failed")
    assembly_transcript_id: Optional[str] = Field(default=None, index=True, description="AssemblyAI transcript ID for webhook correlation")

    created_at: datetime = Field(default_factory=utc_now, index=True)


class Feature2Reminder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    interview_id: int = Field(index=True, foreign_key="feature2interviewautopsy.id")
    candidate_id: str = Field(index=True)
    reminder_type: str = Field(index=True)
    scheduled_at: datetime = Field(index=True)
    message: str
    context_json: str
    is_sent: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=utc_now)


class Feature3MarketSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: str = Field(index=True)
    target_role: str = Field(index=True)
    region: str = Field(index=True)
    remote_only: bool = Field(default=False, index=True)

    jobs_json: str
    clustering_json: str
    demand_supply_json: str
    salary_map_json: str
    remote_market_json: str
    source_meta_json: str

    # Chunk 4 enhancements
    salary_currency: str = Field(default="USD", index=True, description="Currency for salary data: USD|PKR|GBP")
    market_commentary_json: str = Field(default="{}", description="Gemini-generated market insights")

    created_at: datetime = Field(default_factory=utc_now, index=True)


class Feature3GapSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    market_snapshot_id: int = Field(index=True, foreign_key="feature3marketsnapshot.id")
    candidate_id: str = Field(index=True)

    current_skills_json: str
    target_skills_json: str
    radar_chart_json: str
    roadmap_json: str
    niche_recommendations_json: str
    github_validation_json: str
    historical_gap_json: str

    match_score: float = Field(index=True)
    gap_to_top10_score: float
    ai_learning_path_json: str = Field(default="{}")  # 1.5: persisted Gemini learning path

    created_at: datetime = Field(default_factory=utc_now, index=True)


class Feature3SkillSprint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: str = Field(index=True)
    gap_snapshot_id: int = Field(index=True, foreign_key="feature3gapsnapshot.id")

    target_role: str = Field(index=True)
    primary_skill: str = Field(index=True)
    sprint_status: str = Field(default="active", index=True)

    day_plan_json: str
    mvp_prompt: str
    quiz_json: str
    resume_inject_json: str = "{}"

    started_at: datetime = Field(default_factory=utc_now, index=True)
    updated_at: datetime = Field(default_factory=utc_now, index=True)


class Feature3FutureInsight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: str = Field(index=True)
    market_snapshot_id: Optional[int] = Field(default=None, index=True, foreign_key="feature3marketsnapshot.id")

    obsolescence_json: str
    forecast_2027_json: str
    agentic_ai_score: float
    pivot_advice_json: str
    hiring_freeze_alert_json: str

    created_at: datetime = Field(default_factory=utc_now, index=True)


class Feature3RoiReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: str = Field(index=True)
    market_snapshot_id: Optional[int] = Field(default=None, index=True, foreign_key="feature3marketsnapshot.id")
    gap_snapshot_id: Optional[int] = Field(default=None, index=True, foreign_key="feature3gapsnapshot.id")

    impact_json: str
    callback_probability: float
    lifetime_value_delta: float
    path_comparison_json: str
    success_stories_json: str

    created_at: datetime = Field(default_factory=utc_now, index=True)


class Feature4MockSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: str = Field(index=True)
    role_name: str = Field(index=True)
    persona_key: str = Field(index=True)

    persona_profile_json: str
    config_json: str
    opening_questions_json: str

    realtime_summary_json: str
    transcript_json: str
    deep_logic_json: str
    coach_json: str
    synthesis_json: str
    ai_coaching_report_json: str = Field(default="{}")  # 1.6: persisted Gemini coaching report

    status: str = Field(default="active", index=True)
    created_at: datetime = Field(default_factory=utc_now, index=True)
    updated_at: datetime = Field(default_factory=utc_now, index=True)


class Feature4SessionTurn(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(index=True, foreign_key="feature4mocksession.id")
    turn_index: int = Field(index=True)
    question_type: str = Field(index=True)
    question_text: str
    answer_text: str

    realtime_json: str
    deep_logic_json: str
    whisper_hint: str
    next_question_json: str

    created_at: datetime = Field(default_factory=utc_now, index=True)


class Feature4SessionShare(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(index=True, foreign_key="feature4mocksession.id")
    share_token: str = Field(index=True, unique=True)
    expires_at: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=utc_now, index=True)


class Feature5NarrativeSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: str = Field(index=True)
    repo_subpath: str = Field(index=True, default=".")
    target_role: str = Field(index=True)
    tone: str = Field(index=True, default="deep_tech")
    status: str = Field(index=True, default="completed")

    deep_analysis_json: str
    narrative_json: str
    talk_track_json: str
    gap_analysis_json: str
    export_sync_json: str
    consistency_json: str

    created_at: datetime = Field(default_factory=utc_now, index=True)
    updated_at: datetime = Field(default_factory=utc_now, index=True)


class AnalyticsEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    event_name: str = Field(index=True)
    event_version: str = Field(default="1.0", index=True)
    occurred_at_utc: datetime = Field(default_factory=utc_now, index=True)

    user_id: str = Field(index=True)
    session_id: str = Field(index=True)
    platform: str = Field(default="web", index=True)
    feature_area: str = Field(index=True)

    resume_id: Optional[str] = Field(default=None, index=True)
    jd_id: Optional[str] = Field(default=None, index=True)
    application_id: Optional[str] = Field(default=None, index=True)
    interview_id: Optional[str] = Field(default=None, index=True)
    project_id: Optional[str] = Field(default=None, index=True)

    metadata_json: str = Field(default="{}")
    created_at: datetime = Field(default_factory=utc_now, index=True)


class ApplicationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    application_id: str = Field(index=True)

    company_name_normalized: str = Field(index=True)
    role_name_normalized: str = Field(index=True)
    channel: str = Field(index=True, default="job_board")
    status: str = Field(index=True, default="submitted")
    status_reason: str = Field(default="")

    created_at: datetime = Field(default_factory=utc_now, index=True)
    updated_at: datetime = Field(default_factory=utc_now, index=True)


class UserAccount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: str = ""
    password_hash: str
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=utc_now, index=True)
    updated_at: datetime = Field(default_factory=utc_now, index=True)


class UserSessionToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="useraccount.id")
    token_hash: str = Field(index=True, unique=True)
    label: str = "web"
    issued_at: datetime = Field(default_factory=utc_now, index=True)
    expires_at: datetime = Field(index=True)
    revoked_at: Optional[datetime] = Field(default=None, index=True)
