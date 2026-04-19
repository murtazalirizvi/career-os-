from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class CoreLoopSummaryResponse(BaseModel):
    candidate_id: str
    generated_at_utc: datetime

    readiness_score: float
    confidence_label: str

    latest_refs: Dict[str, Optional[int]]
    focus_today: List[str]
    blockers: List[str]
    next_actions: List[Dict[str, Any]]
    metrics_snapshot: Dict[str, Any]
