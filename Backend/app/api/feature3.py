from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

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
)

router = APIRouter(prefix="/api/feature3", tags=["Feature 3: Skill-Arbitrage"])


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
    payload = market_engine.build_market_snapshot(
        target_role=req.target_role,
        region=req.region,
        remote_only=req.remote_only,
        search_terms=req.search_terms,
    )

    row = Feature3MarketSnapshot(
        candidate_id=req.candidate_id,
        target_role=req.target_role,
        region=req.region,
        remote_only=req.remote_only,
        jobs_json=_dumps(payload["jobs"]),
        clustering_json=_dumps(payload["tech_stack_clusters"]),
        demand_supply_json=_dumps(payload["demand_supply_ratio"]),
        salary_map_json=_dumps(payload["salary_to_skill_map"]),
        remote_market_json=_dumps(payload["remote_opportunity_filter"]),
        source_meta_json=_dumps(payload["source_meta"]),
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
        created_at=row.created_at,
    )


@router.get("/market-snapshot/{snapshot_id}", response_model=Feature3MarketSnapshotResponse)
def get_market_snapshot(snapshot_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature3MarketSnapshot, snapshot_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 3 market snapshot not found.")

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
