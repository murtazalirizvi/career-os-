from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Feature5CreateSessionRequest(BaseModel):
    candidate_id: str = Field(min_length=2, max_length=120)
    repo_subpath: str = Field(default=".")
    target_role: str = Field(default="Software Engineer")
    jd_text: str = Field(default="")
    resume_text: str = Field(default="")
    linkedin_text: str = Field(default="")
    github_repo: str = Field(default="", description="Optional public GitHub repo URL or owner/repo")
    tone: str = Field(default="deep_tech", description="deep_tech|business")
    selected_projects: Optional[List[str]] = None


class Feature5SessionResponse(BaseModel):
    session_id: int
    candidate_id: str
    repo_subpath: str
    target_role: str
    tone: str
    deep_analysis: Dict[str, Any]
    narrative: Dict[str, Any]
    talk_track: Dict[str, Any]
    gap_analysis: Dict[str, Any]
    export_sync: Dict[str, Any]
    consistency_check: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime


class Feature5ConsistencyRequest(BaseModel):
    resume_text: str = Field(default="")
    linkedin_text: str = Field(default="")


class Feature5ConsistencyResponse(BaseModel):
    session_id: int
    consistency_check: Dict[str, Any]


class Feature5ExportRequest(BaseModel):
    include_sections: List[str] = Field(default_factory=lambda: ["linkedin_sync", "resume_optimizer", "case_study_pdf"])


class Feature5ExportResponse(BaseModel):
    session_id: int
    exported_sections: List[str]
    markdown_bundle: str
    payload: Dict[str, Any]


class Feature5PortfolioSiteResponse(BaseModel):
    session_id: int
    file_name: str
    bytes_size: int


class Feature5SessionHistoryItem(BaseModel):
    session_id: int
    target_role: str
    tone: str
    status: str
    architecture_style: str
    sophistication_score: float
    created_at: datetime


class Feature5SessionHistoryResponse(BaseModel):
    candidate_id: str
    sessions: List[Feature5SessionHistoryItem]
