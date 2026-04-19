from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Feature3MarketSnapshotRequest(BaseModel):
	candidate_id: str = Field(min_length=2, max_length=120)
	target_role: str = Field(default="Software Engineer")
	region: str = Field(default="PK")
	remote_only: bool = Field(default=False)
	search_terms: List[str] = Field(default_factory=list)


class Feature3MarketSnapshotResponse(BaseModel):
	snapshot_id: int
	candidate_id: str
	target_role: str
	region: str
	jobs: List[Dict[str, Any]]
	tech_stack_clusters: Dict[str, List[str]]
	demand_supply_ratio: Dict[str, Dict[str, Any]]
	salary_to_skill_map: Dict[str, Dict[str, float]]
	remote_opportunity_filter: Dict[str, Any]
	source_meta: Dict[str, Any]
	created_at: datetime


class Feature3GapAnalysisRequest(BaseModel):
	candidate_id: str = Field(min_length=2, max_length=120)
	market_snapshot_id: int
	current_skills: List[str] = Field(default_factory=list)
	years_experience: float = Field(default=1.5, ge=0, le=40)
	github_username: str = Field(default="")


class Feature3GapAnalysisResponse(BaseModel):
	gap_snapshot_id: int
	candidate_id: str
	market_snapshot_id: int
	match_score: float
	gap_to_top10_score: float
	radar_chart: Dict[str, Any]
	roadmap_to_90: Dict[str, Any]
	niche_recommendations: List[Dict[str, Any]]
	github_project_validation: Dict[str, Any]
	historical_gap_tracking: Dict[str, Any]
	created_at: datetime


class Feature3SprintCreateRequest(BaseModel):
	candidate_id: str = Field(min_length=2, max_length=120)
	gap_snapshot_id: int
	target_role: str
	primary_skill: str = Field(min_length=2)


class Feature3SprintResponse(BaseModel):
	sprint_id: int
	candidate_id: str
	gap_snapshot_id: int
	target_role: str
	primary_skill: str
	sprint_status: str
	curated_day_plan: List[Dict[str, Any]]
	mvp_prompt: Dict[str, Any]
	quick_quiz: Dict[str, Any]
	resume_injector: Dict[str, Any]
	peer_group_tags: List[str]
	started_at: datetime
	updated_at: datetime


class Feature3QuizAttemptRequest(BaseModel):
	answers: List[str] = Field(default_factory=list)


class Feature3QuizAttemptResponse(BaseModel):
	sprint_id: int
	score: float
	passed: bool
	feedback: List[str]


class Feature3ResumeInjectorRequest(BaseModel):
	project_name: str = Field(default="Project")
	baseline_context: str = Field(default="")
	impact_metric_hint: str = Field(default="")


class Feature3ResumeInjectorResponse(BaseModel):
	sprint_id: int
	star_bullets: List[str]
	linkedin_snippet: str


class Feature3PeersResponse(BaseModel):
	sprint_id: int
	peer_matches: List[Dict[str, Any]]


class Feature3FutureInsightRequest(BaseModel):
	candidate_id: str = Field(min_length=2, max_length=120)
	current_skills: List[str] = Field(default_factory=list)
	market_snapshot_id: Optional[int] = None


class Feature3FutureInsightResponse(BaseModel):
	insight_id: int
	candidate_id: str
	obsolescence_tracker: List[Dict[str, Any]]
	forecast_2027: Dict[str, Any]
	agentic_ai_score: Dict[str, Any]
	industry_pivot_advice: Dict[str, Any]
	hiring_freeze_alert: Dict[str, Any]
	created_at: datetime


class Feature3RoiRequest(BaseModel):
	candidate_id: str = Field(min_length=2, max_length=120)
	market_snapshot_id: Optional[int] = None
	gap_snapshot_id: Optional[int] = None
	current_salary_usd: float = Field(default=12000, ge=0)
	target_path: str = Field(default="fullstack")


class Feature3RoiResponse(BaseModel):
	report_id: int
	candidate_id: str
	skill_impact: Dict[str, Any]
	callback_probability: Dict[str, Any]
	lifetime_value: Dict[str, Any]
	path_comparison: Dict[str, Any]
	success_stories: List[Dict[str, Any]]
	created_at: datetime


class Feature3HistoricalGapsResponse(BaseModel):
	candidate_id: str
	monthly_snapshots: List[Dict[str, Any]]
	trend: Dict[str, float]
