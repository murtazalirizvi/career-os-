from __future__ import annotations

import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from ..analysis.feature1_engine import Feature1Engine, dump_json
from ..db import get_session
from ..models import Feature1Analysis, Feature1VersionTag
from ..schemas import (
    AddVersionTagRequest,
    Feature1AnalysisResponse,
    Feature1ComparisonResponse,
    Feature1ReportResponse,
    Feature1VersionSummary,
    HeatZone,
    ReadyToApplyResponse,
)
from ..services.reporting import write_markdown_report
from ..services.storage import save_upload

router = APIRouter(prefix="/api/feature1", tags=["Feature 1: Hiring Manager Lens"])


def _next_version_number(session: Session, candidate_id: str) -> int:
    q = select(Feature1Analysis).where(Feature1Analysis.candidate_id == candidate_id).order_by(Feature1Analysis.version_number.desc())
    latest = session.exec(q).first()
    if latest is None:
        return 1
    return latest.version_number + 1


def _to_response(row: Feature1Analysis) -> Feature1AnalysisResponse:
    metrics = json.loads(row.metrics_json)
    hot_zones = [HeatZone(**item) for item in json.loads(row.hotzones_json)]
    recommendations = json.loads(row.recommendations_json)

    return Feature1AnalysisResponse(
        analysis_id=row.id,
        candidate_id=row.candidate_id,
        version_number=row.version_number,
        job_category=row.job_category,
        score={
            "overall": row.overall_score,
            "visual_hierarchy": row.visual_score,
            "ats_integrity": row.ats_score,
            "semantic_match": row.semantic_score,
            "competitive_benchmark": row.benchmark_score,
        },
        summaries={
            "visual": row.eye_tracking_summary,
            "ats": row.ats_summary,
            "semantic": row.semantic_summary,
            "benchmark": row.benchmark_summary,
        },
        metrics=metrics,
        hot_zones=hot_zones,
        recommendations=recommendations,
        ready_to_apply=row.overall_score >= 90.0,
        created_at=row.created_at,
    )


@router.post("/analyze", response_model=Feature1AnalysisResponse)
def analyze_resume(
    candidate_id: str = Form(...),
    job_category: str = Form("frontend"),
    job_description: str = Form(...),
    resume_pdf: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    if not (resume_pdf.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported for Feature 1 analysis.")

    saved = save_upload(resume_pdf, candidate_id)

    engine = Feature1Engine(
        resume_pdf_path=saved,
        job_description=job_description,
        job_category=job_category,
    )
    result = engine.run()

    version_number = _next_version_number(session, candidate_id)
    row = Feature1Analysis(
        candidate_id=candidate_id,
        job_category=job_category,
        resume_filename=resume_pdf.filename or saved.name,
        resume_path=str(saved),
        version_number=version_number,
        overall_score=result["score"]["overall"],
        visual_score=result["score"]["visual_hierarchy"],
        ats_score=result["score"]["ats_integrity"],
        semantic_score=result["score"]["semantic_match"],
        benchmark_score=result["score"]["competitive_benchmark"],
        eye_tracking_summary=result["summaries"]["visual"],
        ats_summary=result["summaries"]["ats"],
        semantic_summary=result["summaries"]["semantic"],
        benchmark_summary=result["summaries"]["benchmark"],
        hotzones_json=dump_json(result["hot_zones"]),
        metrics_json=dump_json(result["metrics"]),
        recommendations_json=dump_json(result["recommendations"]),
    )

    session.add(row)
    session.commit()
    session.refresh(row)

    return _to_response(row)


@router.get("/versions/{candidate_id}", response_model=List[Feature1VersionSummary])
def list_versions(candidate_id: str, session: Session = Depends(get_session)):
    q = (
        select(Feature1Analysis)
        .where(Feature1Analysis.candidate_id == candidate_id)
        .order_by(Feature1Analysis.version_number.desc())
    )
    rows = list(session.exec(q).all())
    return [
        Feature1VersionSummary(
            analysis_id=row.id,
            version_number=row.version_number,
            job_category=row.job_category,
            overall_score=row.overall_score,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/analysis/{analysis_id}", response_model=Feature1AnalysisResponse)
def get_analysis(analysis_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature1Analysis, analysis_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return _to_response(row)


@router.get("/compare/{candidate_id}", response_model=Feature1ComparisonResponse)
def compare_versions(
    candidate_id: str,
    left_version: int,
    right_version: int,
    session: Session = Depends(get_session),
):
    q = select(Feature1Analysis).where(
        Feature1Analysis.candidate_id == candidate_id,
        Feature1Analysis.version_number.in_([left_version, right_version]),
    )
    rows = list(session.exec(q).all())
    if len(rows) != 2:
        raise HTTPException(status_code=404, detail="Could not find both versions for comparison.")

    left = next(r for r in rows if r.version_number == left_version)
    right = next(r for r in rows if r.version_number == right_version)

    score_delta = {
        "overall": round(right.overall_score - left.overall_score, 2),
        "visual_hierarchy": round(right.visual_score - left.visual_score, 2),
        "ats_integrity": round(right.ats_score - left.ats_score, 2),
        "semantic_match": round(right.semantic_score - left.semantic_score, 2),
        "competitive_benchmark": round(right.benchmark_score - left.benchmark_score, 2),
    }

    left_recs = set(json.loads(left.recommendations_json))
    right_recs = set(json.loads(right.recommendations_json))

    return Feature1ComparisonResponse(
        candidate_id=candidate_id,
        left_version=left_version,
        right_version=right_version,
        score_delta=score_delta,
        recommendation_delta={
            "resolved": sorted(left_recs - right_recs),
            "new": sorted(right_recs - left_recs),
            "persisting": sorted(left_recs.intersection(right_recs)),
        },
    )


@router.post("/ready-to-apply/{analysis_id}", response_model=ReadyToApplyResponse)
def ready_to_apply(analysis_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature1Analysis, analysis_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    eligible = row.overall_score >= 90.0
    return ReadyToApplyResponse(
        analysis_id=analysis_id,
        eligible=eligible,
        score=row.overall_score,
        badge_label="Ready to Apply" if eligible else None,
    )


@router.get("/heatmap/{analysis_id}")
def get_heatmap(analysis_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature1Analysis, analysis_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return json.loads(row.hotzones_json)


@router.get("/report/{analysis_id}", response_model=Feature1ReportResponse)
def export_report(analysis_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature1Analysis, analysis_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    payload = _to_response(row).model_dump()
    report_path = write_markdown_report(analysis_id=analysis_id, payload=payload)

    return Feature1ReportResponse(analysis_id=analysis_id, report_path=str(report_path), format="md")


@router.post("/tag/{analysis_id}")
def add_version_tag(analysis_id: int, req: AddVersionTagRequest, session: Session = Depends(get_session)):
    row = session.get(Feature1Analysis, analysis_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    tag = Feature1VersionTag(
        analysis_id=analysis_id,
        candidate_id=row.candidate_id,
        tag=req.tag,
    )
    session.add(tag)
    session.commit()

    return {"ok": True, "analysis_id": analysis_id, "tag": req.tag}
