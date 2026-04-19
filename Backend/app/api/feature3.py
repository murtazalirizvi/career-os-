from __future__ import annotations

import json
import logging
import threading
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..analysis import gemini_client
from ..analysis.feature3_engine import FutureEngine, MarketIntelligenceEngine, RoiEngine, SkillGapEngine, SprintEngine
from ..db import get_session
from ..models import (
    Feature3FutureInsight,
    Feature3GapSnapshot,
    Feature3MarketSnapshot,
    Feature3RoiReport,
    Feature3SkillSprint,
)
from ..schemas_feature3 import (
    Feature3FullRunRequest,
    Feature3FullRunResponse,
    Feature3FutureInsightRequest,
    Feature3FutureInsightResponse,
    Feature3GapAnalysisRequest,
    Feature3GapAnalysisResponse,
    Feature3HistoricalGapsResponse,
    Feature3MarketSnapshotRequest,
    Feature3MarketSnapshotResponse,
    Feature3PeersResponse,
    Feature3QuizAttemptRequest,
    Feature3QuizAttemptResponse,
    Feature3ResumeInjectorRequest,
    Feature3ResumeInjectorResponse,
    Feature3RoiRequest,
    Feature3RoiResponse,
    Feature3SprintCreateRequest,
    Feature3SprintResponse,
    Feature3TrendingSkillItem,
    Feature3TrendingSkillsResponse,
)

logger = logging.getLogger("career_os.feature3")

router = APIRouter(prefix="/api/feature3", tags=["Feature 3: Skill-Arbitrage"])


# ─── Chunk 4: Market Snapshot Caching ────────────────────────────────────────

class MarketCache:
    """In-memory LRU cache for market snapshots with 6-hour TTL."""
    
    def __init__(self, max_size: int = 50, ttl_hours: int = 6):
        self.cache: OrderedDict[Tuple, Tuple[Dict[str, Any], datetime]] = OrderedDict()
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.lock = threading.Lock()
    
    def get(self, key: Tuple) -> Optional[Dict[str, Any]]:
        """Get cached entry if exists and not expired."""
        with self.lock:
            if key in self.cache:
                entry, timestamp = self.cache[key]
                if datetime.now(timezone.utc) - timestamp < self.ttl:
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    logger.info(f"Cache HIT: {key}")
                    return entry
                else:
                    # Expired
                    del self.cache[key]
                    logger.info(f"Cache EXPIRED: {key}")
            logger.info(f"Cache MISS: {key}")
            return None
    
    def set(self, key: Tuple, value: Dict[str, Any]) -> None:
        """Store entry in cache with current timestamp."""
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Evict least recently used
                evicted_key = next(iter(self.cache))
                del self.cache[evicted_key]
                logger.info(f"Cache EVICT: {evicted_key}")
            
            self.cache[key] = (value, datetime.now(timezone.utc))
            logger.info(f"Cache SET: {key}")


# Global cache instance
_market_cache = MarketCache()


# ─── Chunk 4: Currency Conversion ────────────────────────────────────────────

def _convert_salary(amount_usd: float, target_currency: str) -> float:
    """Convert USD salary to target currency using static exchange rates."""
    if target_currency == "USD":
        return amount_usd
    
    # Static fallback rates (updated periodically)
    FALLBACK_RATES = {
        "PKR": 278.5,  # 1 USD = 278.5 PKR
        "GBP": 0.79,   # 1 USD = 0.79 GBP
    }
    
    rate = FALLBACK_RATES.get(target_currency, 1.0)
    return amount_usd * rate


def _convert_salary_map(salary_map: Dict[str, Dict[str, float]], target_currency: str) -> Dict[str, Dict[str, float]]:
    """Convert all salaries in salary map to target currency."""
    if target_currency == "USD":
        return salary_map
    
    converted = {}
    for skill, data in salary_map.items():
        converted[skill] = {
            key: _convert_salary(value, target_currency) if isinstance(value, (int, float)) else value
            for key, value in data.items()
        }
    return converted


# ─── Chunk 4: Gemini Market Commentary ───────────────────────────────────────

def _generate_market_commentary(
    target_role: str,
    region: str,
    job_count: int,
    avg_salary: float,
    currency: str,
    top_skills: List[str]
) -> str:
    """Generate natural language market commentary using Gemini."""
    if not gemini_client.is_available():
        # Fallback heuristic commentary
        return (
            f"{target_role} market in {region}: {job_count} jobs found. "
            f"Average salary: {avg_salary:.0f} {currency}. "
            f"Top skills: {', '.join(top_skills[:3])}."
        )
    
    prompt = (
        f"You are a career market analyst. Summarize this job market data in 3-5 sentences:\n\n"
        f"Role: {target_role}\n"
        f"Region: {region}\n"
        f"Job postings: {job_count}\n"
        f"Average salary: {avg_salary:.0f} {currency}\n"
        f"Top required skills: {', '.join(top_skills[:5])}\n\n"
        "Provide insights on:\n"
        "1. Market demand (high/moderate/low)\n"
        "2. Salary competitiveness\n"
        "3. Key skill requirements\n"
        "4. Opportunities for candidates\n"
        "Keep it concise and actionable."
    )
    
    try:
        commentary = gemini_client.generate(prompt, temperature=0.3, max_tokens=256)
        return commentary.strip() if commentary else ""
    except Exception as e:
        logger.error(f"Gemini market commentary failed: {e}")
        return (
            f"{target_role} market in {region}: {job_count} jobs found. "
            f"Average salary: {avg_salary:.0f} {currency}. "
            f"Top skills: {', '.join(top_skills[:3])}."
        )


# ─── Engine Instances ─────────────────────────────────────────────────────────

market_engine = MarketIntelligenceEngine()
gap_engine = SkillGapEngine()
sprint_engine = SprintEngine()
future_engine = FutureEngine()
roi_engine = RoiEngine()


def _loads(text: str) -> Any:
    return json.loads(text)


def _dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True)


@router.post("/market-snapshot", response_model=Feature3MarketSnapshotResponse)
def create_market_snapshot(req: Feature3MarketSnapshotRequest, session: Session = Depends(get_session)):
    # Chunk 4: Check cache first
    cache_key = (req.target_role, req.region, req.salary_currency)
    cached_payload = _market_cache.get(cache_key)
    
    if cached_payload:
        payload = cached_payload
    else:
        # Fetch fresh market data
        payload = market_engine.build_market_snapshot(
            target_role=req.target_role,
            region=req.region,
            remote_only=req.remote_only,
            search_terms=req.search_terms,
        )
        # Store in cache
        _market_cache.set(cache_key, payload)
    
    # Chunk 4: Convert salaries to target currency
    salary_map = _convert_salary_map(payload["salary_to_skill_map"], req.salary_currency)
    
    # Chunk 4: Generate market commentary
    jobs = payload["jobs"]
    job_count = len(jobs)
    
    # Calculate average salary from converted salary map
    all_salaries = []
    for skill_data in salary_map.values():
        if "avg" in skill_data:
            all_salaries.append(skill_data["avg"])
    avg_salary = sum(all_salaries) / len(all_salaries) if all_salaries else 0.0
    
    # Extract top skills
    top_skills = list(payload["tech_stack_clusters"].keys())[:5] if payload["tech_stack_clusters"] else []
    
    market_commentary = _generate_market_commentary(
        target_role=req.target_role,
        region=req.region,
        job_count=job_count,
        avg_salary=avg_salary,
        currency=req.salary_currency,
        top_skills=top_skills
    )

    row = Feature3MarketSnapshot(
        candidate_id=req.candidate_id,
        target_role=req.target_role,
        region=req.region,
        remote_only=req.remote_only,
        jobs_json=_dumps(payload["jobs"]),
        clustering_json=_dumps(payload["tech_stack_clusters"]),
        demand_supply_json=_dumps(payload["demand_supply_ratio"]),
        salary_map_json=_dumps(salary_map),  # Store converted salaries
        remote_market_json=_dumps(payload["remote_opportunity_filter"]),
        source_meta_json=_dumps(payload["source_meta"]),
        salary_currency=req.salary_currency,
        market_commentary_json=_dumps({"commentary": market_commentary}),
    )

    session.add(row)
    session.commit()
    session.refresh(row)

    return Feature3MarketSnapshotResponse(
        snapshot_id=row.id,
        candidate_id=row.candidate_id,
        target_role=row.target_role,
        region=row.region,
        jobs=_loads(row.jobs_json),
        tech_stack_clusters=_loads(row.clustering_json),
        demand_supply_ratio=_loads(row.demand_supply_json),
        salary_to_skill_map=_loads(row.salary_map_json),
        remote_opportunity_filter=_loads(row.remote_market_json),
        source_meta=_loads(row.source_meta_json),
        salary_currency=row.salary_currency,
        market_commentary=market_commentary,
        created_at=row.created_at,
    )


@router.get("/market-snapshot/{snapshot_id}", response_model=Feature3MarketSnapshotResponse)
def get_market_snapshot(snapshot_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature3MarketSnapshot, snapshot_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 3 market snapshot not found.")

    # Chunk 4: Extract market commentary
    commentary_data = _loads(row.market_commentary_json) if row.market_commentary_json else {}
    market_commentary = commentary_data.get("commentary", "")

    return Feature3MarketSnapshotResponse(
        snapshot_id=row.id,
        candidate_id=row.candidate_id,
        target_role=row.target_role,
        region=row.region,
        jobs=_loads(row.jobs_json),
        tech_stack_clusters=_loads(row.clustering_json),
        demand_supply_ratio=_loads(row.demand_supply_json),
        salary_to_skill_map=_loads(row.salary_map_json),
        remote_opportunity_filter=_loads(row.remote_market_json),
        source_meta=_loads(row.source_meta_json),
        salary_currency=row.salary_currency,
        market_commentary=market_commentary,
        created_at=row.created_at,
    )


@router.post("/gap-analysis", response_model=Feature3GapAnalysisResponse)
def create_gap_analysis(req: Feature3GapAnalysisRequest, session: Session = Depends(get_session)):
    market_row = session.get(Feature3MarketSnapshot, req.market_snapshot_id)
    if market_row is None:
        raise HTTPException(status_code=404, detail="Feature 3 market snapshot not found.")

    market_payload = {
        "jobs": _loads(market_row.jobs_json),
        "demand_supply_ratio": _loads(market_row.demand_supply_json),
        "salary_to_skill_map": _loads(market_row.salary_map_json),
        "remote_opportunity_filter": _loads(market_row.remote_market_json),
    }

    q = (
        select(Feature3GapSnapshot)
        .where(Feature3GapSnapshot.candidate_id == req.candidate_id)
        .order_by(Feature3GapSnapshot.created_at.asc())
    )
    history_rows = list(session.exec(q).all())

    payload = gap_engine.build_gap_analysis(
        current_skills=req.current_skills,
        years_experience=req.years_experience,
        market_snapshot=market_payload,
        github_username=req.github_username,
        historical_rows=history_rows,
    )

    row = Feature3GapSnapshot(
        market_snapshot_id=req.market_snapshot_id,
        candidate_id=req.candidate_id,
        current_skills_json=_dumps(payload["current_skills"]),
        target_skills_json=_dumps(payload["target_skills"]),
        radar_chart_json=_dumps(payload["radar_chart"]),
        roadmap_json=_dumps(payload["roadmap_to_90"]),
        niche_recommendations_json=_dumps(payload["niche_recommendations"]),
        github_validation_json=_dumps(payload["github_project_validation"]),
        historical_gap_json=_dumps(payload["historical_gap_tracking"]),
        match_score=payload["match_score"],
        gap_to_top10_score=payload["gap_to_top10_score"],
        ai_learning_path_json=_dumps(payload.get("ai_learning_path", {})),  # 1.5
    )
    session.add(row)
    session.commit()
    session.refresh(row)

    return Feature3GapAnalysisResponse(
        gap_snapshot_id=row.id,
        candidate_id=row.candidate_id,
        market_snapshot_id=row.market_snapshot_id,
        match_score=row.match_score,
        gap_to_top10_score=row.gap_to_top10_score,
        radar_chart=_loads(row.radar_chart_json),
        roadmap_to_90=_loads(row.roadmap_json),
        niche_recommendations=_loads(row.niche_recommendations_json),
        github_project_validation=_loads(row.github_validation_json),
        historical_gap_tracking=_loads(row.historical_gap_json),
        ai_learning_path=_loads(row.ai_learning_path_json) if row.ai_learning_path_json else {},
        created_at=row.created_at,
    )


@router.get("/gap-snapshot/{gap_snapshot_id}", response_model=Feature3GapAnalysisResponse)
def get_gap_snapshot(gap_snapshot_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature3GapSnapshot, gap_snapshot_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 3 gap snapshot not found.")

    return Feature3GapAnalysisResponse(
        gap_snapshot_id=row.id,
        candidate_id=row.candidate_id,
        market_snapshot_id=row.market_snapshot_id,
        match_score=row.match_score,
        gap_to_top10_score=row.gap_to_top10_score,
        radar_chart=_loads(row.radar_chart_json),
        roadmap_to_90=_loads(row.roadmap_json),
        niche_recommendations=_loads(row.niche_recommendations_json),
        github_project_validation=_loads(row.github_validation_json),
        historical_gap_tracking=_loads(row.historical_gap_json),
        ai_learning_path=_loads(row.ai_learning_path_json) if row.ai_learning_path_json else {},
        created_at=row.created_at,
    )


@router.post("/sprint", response_model=Feature3SprintResponse)
def create_skill_sprint(req: Feature3SprintCreateRequest, session: Session = Depends(get_session)):
    gap_row = session.get(Feature3GapSnapshot, req.gap_snapshot_id)
    if gap_row is None:
        raise HTTPException(status_code=404, detail="Feature 3 gap snapshot not found.")

    payload = sprint_engine.build_sprint(primary_skill=req.primary_skill, target_role=req.target_role)

    row = Feature3SkillSprint(
        candidate_id=req.candidate_id,
        gap_snapshot_id=req.gap_snapshot_id,
        target_role=req.target_role,
        primary_skill=req.primary_skill.lower(),
        sprint_status="active",
        day_plan_json=_dumps(payload["curated_day_plan"]),
        mvp_prompt=_dumps(payload["mvp_prompt"]),
        quiz_json=_dumps(payload["quick_quiz"]),
        resume_inject_json=_dumps(payload["resume_injector"]),
    )
    session.add(row)
    session.commit()
    session.refresh(row)

    return Feature3SprintResponse(
        sprint_id=row.id,
        candidate_id=row.candidate_id,
        gap_snapshot_id=row.gap_snapshot_id,
        target_role=row.target_role,
        primary_skill=row.primary_skill,
        sprint_status=row.sprint_status,
        curated_day_plan=_loads(row.day_plan_json),
        mvp_prompt=_loads(row.mvp_prompt),
        quick_quiz=_loads(row.quiz_json),
        resume_injector=_loads(row.resume_inject_json),
        peer_group_tags=payload["peer_group_tags"],
        started_at=row.started_at,
        updated_at=row.updated_at,
    )


@router.post("/sprint/{sprint_id}/quiz", response_model=Feature3QuizAttemptResponse)
def attempt_sprint_quiz(sprint_id: int, req: Feature3QuizAttemptRequest, session: Session = Depends(get_session)):
    row = session.get(Feature3SkillSprint, sprint_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 3 sprint not found.")

    quiz = _loads(row.quiz_json)
    result = sprint_engine.evaluate_quiz(quiz=quiz, answers=req.answers)

    attempt = {
        "last_attempt": {
            "answers_count": len(req.answers),
            "score": result["score"],
            "passed": result["passed"],
            "feedback": result["feedback"],
            "attempted_at": datetime.now(timezone.utc).isoformat(),
        },
        **quiz,
    }
    row.quiz_json = _dumps(attempt)
    row.updated_at = datetime.now(timezone.utc)
    if result["passed"]:
        row.sprint_status = "checkpoint-passed"

    session.add(row)
    session.commit()

    return Feature3QuizAttemptResponse(sprint_id=sprint_id, **result)


@router.post("/sprint/{sprint_id}/resume-inject", response_model=Feature3ResumeInjectorResponse)
def sprint_resume_inject(sprint_id: int, req: Feature3ResumeInjectorRequest, session: Session = Depends(get_session)):
    row = session.get(Feature3SkillSprint, sprint_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 3 sprint not found.")

    payload = sprint_engine.resume_inject(
        skill=row.primary_skill,
        project_name=req.project_name,
        baseline_context=req.baseline_context,
        impact_metric_hint=req.impact_metric_hint,
    )

    row.resume_inject_json = _dumps(payload)
    row.updated_at = datetime.now(timezone.utc)
    session.add(row)
    session.commit()

    return Feature3ResumeInjectorResponse(sprint_id=sprint_id, **payload)


@router.get("/sprint/{sprint_id}/peers", response_model=Feature3PeersResponse)
def sprint_peers(sprint_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature3SkillSprint, sprint_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 3 sprint not found.")

    q = (
        select(Feature3SkillSprint)
        .where(
            Feature3SkillSprint.primary_skill == row.primary_skill,
            Feature3SkillSprint.id != row.id,
            Feature3SkillSprint.sprint_status.in_(["active", "checkpoint-passed"]),
        )
        .order_by(Feature3SkillSprint.started_at.desc())
    )
    peers = list(session.exec(q).all())

    payload = [
        {
            "sprint_id": p.id,
            "candidate_id": p.candidate_id,
            "target_role": p.target_role,
            "status": p.sprint_status,
            "started_at": p.started_at,
        }
        for p in peers[:20]
    ]

    return Feature3PeersResponse(sprint_id=sprint_id, peer_matches=payload)


@router.post("/future-insights", response_model=Feature3FutureInsightResponse)
def create_future_insights(req: Feature3FutureInsightRequest, session: Session = Depends(get_session)):
    market_payload: Dict[str, Any] | None = None
    if req.market_snapshot_id is not None:
        market_row = session.get(Feature3MarketSnapshot, req.market_snapshot_id)
        if market_row is None:
            raise HTTPException(status_code=404, detail="Feature 3 market snapshot not found.")
        market_payload = {
            "jobs": _loads(market_row.jobs_json),
            "remote_opportunity_filter": _loads(market_row.remote_market_json),
        }

    payload = future_engine.build_future_insights(current_skills=req.current_skills, market_snapshot=market_payload)

    row = Feature3FutureInsight(
        candidate_id=req.candidate_id,
        market_snapshot_id=req.market_snapshot_id,
        obsolescence_json=_dumps(payload["obsolescence_tracker"]),
        forecast_2027_json=_dumps(payload["forecast_2027"]),
        agentic_ai_score=payload["agentic_ai_score"]["score"],
        pivot_advice_json=_dumps(payload["industry_pivot_advice"]),
        hiring_freeze_alert_json=_dumps(payload["hiring_freeze_alert"]),
    )
    session.add(row)
    session.commit()
    session.refresh(row)

    return Feature3FutureInsightResponse(
        insight_id=row.id,
        candidate_id=row.candidate_id,
        obsolescence_tracker=_loads(row.obsolescence_json),
        forecast_2027=_loads(row.forecast_2027_json),
        agentic_ai_score=payload["agentic_ai_score"],
        industry_pivot_advice=_loads(row.pivot_advice_json),
        hiring_freeze_alert=_loads(row.hiring_freeze_alert_json),
        created_at=row.created_at,
    )


@router.post("/roi-report", response_model=Feature3RoiResponse)
def create_roi_report(req: Feature3RoiRequest, session: Session = Depends(get_session)):
    market_payload: Dict[str, Any] | None = None
    gap_payload: Dict[str, Any] | None = None

    if req.market_snapshot_id is not None:
        market_row = session.get(Feature3MarketSnapshot, req.market_snapshot_id)
        if market_row is None:
            raise HTTPException(status_code=404, detail="Feature 3 market snapshot not found.")
        market_payload = {"jobs": _loads(market_row.jobs_json)}

    if req.gap_snapshot_id is not None:
        gap_row = session.get(Feature3GapSnapshot, req.gap_snapshot_id)
        if gap_row is None:
            raise HTTPException(status_code=404, detail="Feature 3 gap snapshot not found.")
        gap_payload = {
            "match_score": gap_row.match_score,
            "gap_to_top10_score": gap_row.gap_to_top10_score,
        }

    payload = roi_engine.build_roi(
        current_salary_usd=req.current_salary_usd,
        target_path=req.target_path,
        gap_snapshot=gap_payload,
        market_snapshot=market_payload,
    )

    row = Feature3RoiReport(
        candidate_id=req.candidate_id,
        market_snapshot_id=req.market_snapshot_id,
        gap_snapshot_id=req.gap_snapshot_id,
        impact_json=_dumps(payload["skill_impact"]),
        callback_probability=payload["callback_probability"]["probability"],
        lifetime_value_delta=payload["lifetime_value"]["five_year_value_delta_usd"],
        path_comparison_json=_dumps(payload["path_comparison"]),
        success_stories_json=_dumps(payload["success_stories"]),
    )

    session.add(row)
    session.commit()
    session.refresh(row)

    return Feature3RoiResponse(
        report_id=row.id,
        candidate_id=row.candidate_id,
        skill_impact=_loads(row.impact_json),
        callback_probability=payload["callback_probability"],
        lifetime_value=payload["lifetime_value"],
        path_comparison=_loads(row.path_comparison_json),
        success_stories=_loads(row.success_stories_json),
        created_at=row.created_at,
    )


@router.get("/candidate/{candidate_id}/historical-gaps", response_model=Feature3HistoricalGapsResponse)
def candidate_historical_gaps(candidate_id: str, session: Session = Depends(get_session)):
    q = (
        select(Feature3GapSnapshot)
        .where(Feature3GapSnapshot.candidate_id == candidate_id)
        .order_by(Feature3GapSnapshot.created_at.asc())
    )
    rows = list(session.exec(q).all())

    if not rows:
        return Feature3HistoricalGapsResponse(
            candidate_id=candidate_id,
            monthly_snapshots=[],
            trend={"monthly_delta": 0.0, "confidence": 0.1},
        )

    monthly = {}
    for row in rows:
        key = f"{row.created_at.year}-{row.created_at.month:02d}"
        monthly.setdefault(key, []).append(float(row.match_score))

    snapshots = []
    for month, scores in sorted(monthly.items()):
        snapshots.append({"month": month, "avg_match_score": round(sum(scores) / len(scores), 2), "samples": len(scores)})

    delta = 0.0 if len(snapshots) < 2 else snapshots[-1]["avg_match_score"] - snapshots[0]["avg_match_score"]
    confidence = min(0.95, 0.25 + len(snapshots) * 0.12)

    return Feature3HistoricalGapsResponse(
        candidate_id=candidate_id,
        monthly_snapshots=snapshots,
        trend={"monthly_delta": round(delta, 2), "confidence": round(confidence, 2)},
    )


# ─── Chunk 4: Full-Run Composite Endpoint ────────────────────────────────────

@router.post("/full-run", response_model=Feature3FullRunResponse)
def full_run_analysis(
    req: Feature3FullRunRequest,
    session: Session = Depends(get_session)
):
    """
    Execute complete skill arbitrage analysis in one call:
    1. Market snapshot
    2. Gap analysis
    3. Skill sprint
    4. ROI report
    """
    start_time = time.time()
    
    try:
        # Step 1: Market Analysis
        logger.info(f"Full-run: Starting market analysis for {req.candidate_id}")
        market_req = Feature3MarketSnapshotRequest(
            candidate_id=req.candidate_id,
            target_role=req.target_role,
            region=req.region,
            remote_only=req.remote_only,
            search_terms=[],
            salary_currency=req.salary_currency
        )
        market_response = create_market_snapshot(market_req, session)
        
        # Step 2: Gap Analysis
        logger.info(f"Full-run: Starting gap analysis for {req.candidate_id}")
        gap_req = Feature3GapAnalysisRequest(
            candidate_id=req.candidate_id,
            market_snapshot_id=market_response.snapshot_id,
            current_skills=req.current_skills,
            years_experience=req.years_experience,
            github_username=req.github_username
        )
        gap_response = create_gap_analysis(gap_req, session)
        
        # Step 3: Skill Sprint
        logger.info(f"Full-run: Starting skill sprint for {req.candidate_id}")
        # Determine primary skill: use provided or pick top gap skill
        primary_skill = req.primary_skill_for_sprint
        if not primary_skill:
            # Extract top gap skill from roadmap
            roadmap = gap_response.roadmap_to_90
            if roadmap and "skills_to_acquire" in roadmap and roadmap["skills_to_acquire"]:
                primary_skill = roadmap["skills_to_acquire"][0]
            else:
                primary_skill = "Python"  # Fallback
        
        sprint_req = Feature3SprintCreateRequest(
            candidate_id=req.candidate_id,
            gap_snapshot_id=gap_response.gap_snapshot_id,
            target_role=req.target_role,
            primary_skill=primary_skill
        )
        sprint_response = create_skill_sprint(sprint_req, session)
        
        # Step 4: ROI Report
        logger.info(f"Full-run: Starting ROI report for {req.candidate_id}")
        roi_req = Feature3RoiRequest(
            candidate_id=req.candidate_id,
            market_snapshot_id=market_response.snapshot_id,
            gap_snapshot_id=gap_response.gap_snapshot_id,
            current_salary_usd=req.current_salary_usd,
            target_path=req.target_path
        )
        roi_response = create_roi_report(roi_req, session)
        
        execution_time = time.time() - start_time
        logger.info(f"Full-run: Completed for {req.candidate_id} in {execution_time:.2f}s")
        
        return Feature3FullRunResponse(
            market_snapshot=market_response,
            gap_snapshot=gap_response,
            skill_sprint=sprint_response,
            roi_report=roi_response,
            execution_time_seconds=round(execution_time, 2)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Full-run analysis failed for {req.candidate_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Full-run analysis failed: {str(e)}"
        )


# ─── Chunk 4: Trending Skills Endpoint ───────────────────────────────────────

@router.get("/trending-skills", response_model=Feature3TrendingSkillsResponse)
def get_trending_skills(
    days: int = 30,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """
    Analyze trending skills across recent market snapshots.
    Returns top skills by growth rate.
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Fetch recent market snapshots
    stmt = (
        select(Feature3MarketSnapshot)
        .where(Feature3MarketSnapshot.created_at >= cutoff_date)
        .order_by(Feature3MarketSnapshot.created_at.desc())
    )
    snapshots = list(session.exec(stmt).all())
    
    if not snapshots:
        return Feature3TrendingSkillsResponse(
            trending_skills=[],
            analysis_period_days=days,
            snapshot_count=0
        )
    
    # Aggregate skill counts across snapshots
    skill_stats: Dict[str, Dict[str, Any]] = {}
    
    for snapshot in snapshots:
        jobs = _loads(snapshot.jobs_json)
        salary_map = _loads(snapshot.salary_map_json)
        
        # Extract skills from tech stack clusters
        clusters = _loads(snapshot.clustering_json)
        for cluster_name, skills in clusters.items():
            for skill in skills:
                if skill not in skill_stats:
                    skill_stats[skill] = {
                        "count": 0,
                        "salaries": [],
                        "first_seen": snapshot.created_at,
                        "last_seen": snapshot.created_at,
                        "currency": snapshot.salary_currency
                    }
                skill_stats[skill]["count"] += 1
                
                # Get salary data for this skill
                if skill in salary_map and "avg" in salary_map[skill]:
                    skill_stats[skill]["salaries"].append(salary_map[skill]["avg"])
                
                skill_stats[skill]["last_seen"] = max(
                    skill_stats[skill]["last_seen"],
                    snapshot.created_at
                )
    
    # Calculate growth and average salary
    trending = []
    for skill, stats in skill_stats.items():
        if stats["count"] < 3:  # Filter out rare skills
            continue
        
        # Simple growth heuristic: mentions per day
        days_active = (stats["last_seen"] - stats["first_seen"]).days + 1
        growth_rate = (stats["count"] / days_active) * 100  # mentions per day * 100
        
        avg_salary = (
            sum(stats["salaries"]) / len(stats["salaries"])
            if stats["salaries"]
            else 0.0
        )
        
        trending.append(
            Feature3TrendingSkillItem(
                skill_name=skill,
                job_count=stats["count"],
                growth_percentage=round(growth_rate, 2),
                average_salary=round(avg_salary, 2),
                currency=stats["currency"]
            )
        )
    
    # Sort by growth rate and limit
    trending.sort(key=lambda x: x.growth_percentage, reverse=True)
    
    logger.info(f"Trending skills: Found {len(trending)} skills, returning top {limit}")
    
    return Feature3TrendingSkillsResponse(
        trending_skills=trending[:limit],
        analysis_period_days=days,
        snapshot_count=len(snapshots)
    )
