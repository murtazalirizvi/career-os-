from __future__ import annotations

import json
import re
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlmodel import Session, select

from ..analysis import gemini_client
from ..analysis.feature5_engine import Feature5NarrativeEngine, dump_json
from ..db import get_session
from ..models import Feature5NarrativeSession
from ..schemas_feature5 import (
    Feature5ConsistencyRequest,
    Feature5ConsistencyResponse,
    Feature5CreateSessionRequest,
    Feature5ExportRequest,
    Feature5ExportResponse,
    Feature5LinkedInPostResponse,
    Feature5PortfolioSiteResponse,
    Feature5RegenerateRequest,
    Feature5RegenerateResponse,
    Feature5SessionHistoryItem,
    Feature5SessionHistoryResponse,
    Feature5SessionResponse,
)

import logging
logger = logging.getLogger("career_os.feature5")

router = APIRouter(prefix="/api/feature5", tags=["Feature 5: Narrative Architect"])
engine = Feature5NarrativeEngine()


def _loads(text: str) -> Any:
    return json.loads(text)


@router.post("/sessions", response_model=Feature5SessionResponse)
def create_feature5_session(req: Feature5CreateSessionRequest, session: Session = Depends(get_session)):
    try:
        payload = engine.build_full_session(
            repo_subpath=req.repo_subpath,
            target_role=req.target_role,
            tone=req.tone,
            jd_text=req.jd_text,
            resume_text=req.resume_text,
            linkedin_text=req.linkedin_text,
            github_repo=req.github_repo,
            selected_projects=req.selected_projects,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    row = Feature5NarrativeSession(
        candidate_id=req.candidate_id,
        repo_subpath=req.repo_subpath,
        target_role=req.target_role,
        tone=req.tone,
        status="completed",
        deep_analysis_json=dump_json(payload["deep_analysis"]),
        narrative_json=dump_json(payload["narrative"]),
        talk_track_json=dump_json(payload["talk_track"]),
        gap_analysis_json=dump_json(payload["gap_analysis"]),
        export_sync_json=dump_json(payload["export_sync"]),
        consistency_json=dump_json(payload["consistency_check"]),
        # Chunk 6: persist for re-runs
        resume_text=req.resume_text or "",
        jd_text=req.jd_text or "",
    )
    session.add(row)
    session.commit()
    session.refresh(row)

    return Feature5SessionResponse(
        session_id=row.id,
        candidate_id=row.candidate_id,
        repo_subpath=row.repo_subpath,
        target_role=row.target_role,
        tone=row.tone,
        deep_analysis=_loads(row.deep_analysis_json),
        narrative=_loads(row.narrative_json),
        talk_track=_loads(row.talk_track_json),
        gap_analysis=_loads(row.gap_analysis_json),
        export_sync=_loads(row.export_sync_json),
        consistency_check=_loads(row.consistency_json),
        status=row.status,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/sessions/{session_id}", response_model=Feature5SessionResponse)
def get_feature5_session(session_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature5NarrativeSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 5 session not found.")

    return Feature5SessionResponse(
        session_id=row.id,
        candidate_id=row.candidate_id,
        repo_subpath=row.repo_subpath,
        target_role=row.target_role,
        tone=row.tone,
        deep_analysis=_loads(row.deep_analysis_json),
        narrative=_loads(row.narrative_json),
        talk_track=_loads(row.talk_track_json),
        gap_analysis=_loads(row.gap_analysis_json),
        export_sync=_loads(row.export_sync_json),
        consistency_check=_loads(row.consistency_json),
        status=row.status,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.post("/sessions/{session_id}/consistency-check", response_model=Feature5ConsistencyResponse)
def feature5_consistency_check(session_id: int, req: Feature5ConsistencyRequest, session: Session = Depends(get_session)):
    row = session.get(Feature5NarrativeSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 5 session not found.")

    narrative = _loads(row.narrative_json)
    consistency = engine.consistency_check(narrative, req.resume_text, req.linkedin_text)

    row.consistency_json = dump_json(consistency)
    row.updated_at = datetime.now(timezone.utc)
    session.add(row)
    session.commit()

    return Feature5ConsistencyResponse(session_id=session_id, consistency_check=consistency)


@router.post("/sessions/{session_id}/export", response_model=Feature5ExportResponse)
def feature5_export(session_id: int, req: Feature5ExportRequest, session: Session = Depends(get_session)):
    row = session.get(Feature5NarrativeSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 5 session not found.")

    export_sync = _loads(row.export_sync_json)
    bundle = engine.export_selected(export_sync, req.include_sections)

    return Feature5ExportResponse(
        session_id=session_id,
        exported_sections=bundle["exported_sections"],
        markdown_bundle=bundle["markdown_bundle"],
        payload=bundle["payload"],
    )


@router.get("/sessions/{session_id}/case-study.pdf")
def feature5_case_study_pdf(session_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature5NarrativeSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 5 session not found.")

    export_sync = _loads(row.export_sync_json)
    case_markdown = ((export_sync.get("epic_5_5") or {}).get("case_study_pdf") or {}).get("markdown", "")
    if not case_markdown:
        raise HTTPException(status_code=400, detail="Case study markdown is unavailable for this session.")

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    x = 42
    y = height - 44

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(x, y, f"Feature 5 Case Study - Session {session_id}")
    y -= 20
    pdf.setFont("Helvetica", 10)

    for raw in case_markdown.splitlines():
        line = re.sub(r"^#{1,6}\s*", "", raw).strip()
        line = line or " "
        while len(line) > 110:
            segment = line[:110]
            pdf.drawString(x, y, segment)
            y -= 14
            line = line[110:]
            if y < 56:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = height - 48
        pdf.drawString(x, y, line)
        y -= 14
        if y < 56:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = height - 48

    pdf.save()
    pdf_buffer.seek(0)

    file_name = f"feature5_case_study_s{session_id}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.get("/sessions/{session_id}/portfolio-site")
def feature5_portfolio_site(session_id: int, session: Session = Depends(get_session)):
    row = session.get(Feature5NarrativeSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 5 session not found.")

    narrative = _loads(row.narrative_json)
    export_sync = _loads(row.export_sync_json)
    star = (narrative.get("epic_5_2", {}) or {}).get("star_summaries", [])
    linked = (export_sync.get("epic_5_5", {}) or {}).get("linkedin_sync", {})

    cards = []
    for item in star[:3]:
        cards.append(
            f"<article class='card'><h3>{item.get('project','Project')}</h3><p><strong>S:</strong> {item.get('situation','')}</p><p><strong>T:</strong> {item.get('task','')}</p><p><strong>A:</strong> {item.get('action','')}</p><p><strong>R:</strong> {item.get('result','')}</p></article>"
        )

    html = f"""<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Portfolio Story Pack</title>
<style>body{{font-family:Arial,sans-serif;background:#f8fafc;color:#111827;margin:0}}main{{max-width:980px;margin:0 auto;padding:24px}}h1{{margin:0 0 8px}}.hero{{background:#111827;color:#fff;padding:20px;border-radius:14px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-top:16px}}.card{{border:1px solid #d1d5db;border-radius:12px;background:#fff;padding:12px}}</style></head>
<body><main><section class='hero'><h1>{linked.get('headline','Portfolio Story Pack')}</h1><p>{linked.get('project_description','')}</p></section><section class='grid'>{''.join(cards)}</section></main></body></html>"""

    readme = """# Portfolio Story Pack\n\n1. Open index.html locally to review your generated portfolio narrative.\n2. Deploy with one click using Netlify Drop: https://app.netlify.com/drop\n3. Or deploy on GitHub Pages / Vercel after pushing files to a repo.\n"""

    package_buffer = BytesIO()
    with ZipFile(package_buffer, mode="w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("index.html", html)
        zf.writestr("README.md", readme)
    package_buffer.seek(0)

    file_name = f"feature5_portfolio_site_s{session_id}.zip"
    return StreamingResponse(
        package_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.get("/candidate/{candidate_id}/sessions", response_model=Feature5SessionHistoryResponse)
def feature5_candidate_history(candidate_id: str, session: Session = Depends(get_session)):
    q = (
        select(Feature5NarrativeSession)
        .where(Feature5NarrativeSession.candidate_id == candidate_id)
        .order_by(Feature5NarrativeSession.created_at.desc())
    )
    rows = list(session.exec(q).all())

    items = []
    for row in rows:
        deep = _loads(row.deep_analysis_json)
        architecture = (deep.get("epic_5_1", {}) or {}).get("architecture_mapping", {})
        sophistication = (deep.get("epic_5_1", {}) or {}).get("sophistication_scoring", {})

        items.append(
            Feature5SessionHistoryItem(
                session_id=row.id,
                target_role=row.target_role,
                tone=row.tone,
                status=row.status,
                architecture_style=architecture.get("identified_style", "unknown"),
                sophistication_score=float(sophistication.get("score", 0.0) or 0.0),
                created_at=row.created_at,
            )
        )

    return Feature5SessionHistoryResponse(candidate_id=candidate_id, sessions=items)


# ─── Chunk 6.2: Regenerate narrative endpoint ────────────────────────────────

@router.post("/sessions/{session_id}/regenerate-narrative", response_model=Feature5RegenerateResponse)
def regenerate_narrative(
    session_id: int,
    req: Feature5RegenerateRequest,
    session: Session = Depends(get_session),
):
    """
    Re-run narrative generation with optional tone/role override.
    Uses stored resume_text and jd_text so the user doesn't need to re-submit.
    """
    row = session.get(Feature5NarrativeSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 5 session not found.")

    # Use overrides if provided, else keep stored values
    tone = req.tone or row.tone
    target_role = req.target_role or row.target_role

    try:
        payload = engine.build_full_session(
            repo_subpath=row.repo_subpath,
            target_role=target_role,
            tone=tone,
            jd_text=row.jd_text,
            resume_text=row.resume_text,
            linkedin_text="",
            github_repo="",
            selected_projects=None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Update stored fields
    row.tone = tone
    row.target_role = target_role
    row.narrative_json = dump_json(payload["narrative"])
    row.deep_analysis_json = dump_json(payload["deep_analysis"])
    row.talk_track_json = dump_json(payload["talk_track"])
    row.gap_analysis_json = dump_json(payload["gap_analysis"])
    row.export_sync_json = dump_json(payload["export_sync"])
    row.consistency_json = dump_json(payload["consistency_check"])
    row.updated_at = datetime.now(timezone.utc)
    session.add(row)
    session.commit()
    session.refresh(row)

    logger.info(f"Narrative regenerated for session {session_id} (tone={tone}, role={target_role})")

    return Feature5RegenerateResponse(
        session_id=session_id,
        narrative=payload["narrative"],
        regenerated_at=row.updated_at,
    )


# ─── Chunk 6.5: LinkedIn post endpoint ───────────────────────────────────────

@router.get("/sessions/{session_id}/linkedin-post", response_model=Feature5LinkedInPostResponse)
def get_linkedin_post(session_id: int, session: Session = Depends(get_session)):
    """
    Generate a ready-to-paste LinkedIn post from the narrative session.
    Uses Gemini when available; falls back to a structured heuristic post.
    """
    row = session.get(Feature5NarrativeSession, session_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feature 5 session not found.")

    narrative = _loads(row.narrative_json)
    export_sync = _loads(row.export_sync_json)

    # Extract key data for the post
    linked = (export_sync.get("epic_5_5", {}) or {}).get("linkedin_sync", {})
    headline = linked.get("headline", f"{row.target_role} | Building impactful systems")
    project_desc = linked.get("project_description", "")
    star_summaries = (narrative.get("epic_5_2", {}) or {}).get("star_summaries", [])
    top_result = ""
    if star_summaries:
        top_result = star_summaries[0].get("result", "")

    if gemini_client.is_available():
        prompt = (
            f"Write a LinkedIn post for a {row.target_role} showcasing their technical work.\n\n"
            f"Headline: {headline}\n"
            f"Project summary: {project_desc[:300]}\n"
            f"Top result: {top_result[:200]}\n\n"
            "Requirements:\n"
            "1. Start with a strong hook (1 sentence)\n"
            "2. Describe the technical challenge and solution (2-3 sentences)\n"
            "3. Quantify the impact with metrics\n"
            "4. End with a call-to-action or insight\n"
            "5. Add 3-5 relevant hashtags at the end\n"
            "6. Keep total length under 1300 characters\n"
            "Return ONLY the post text, no preamble."
        )
        try:
            post_text = gemini_client.generate(prompt, temperature=0.4, max_tokens=400)
            if not post_text or len(post_text.strip()) < 50:
                raise ValueError("Empty response")
            post_text = post_text.strip()
            logger.info(f"LinkedIn post generated via Gemini for session {session_id}")
        except Exception as e:
            logger.warning(f"Gemini LinkedIn post failed for session {session_id}: {e}")
            post_text = None
    else:
        post_text = None

    # Heuristic fallback
    if not post_text:
        result_line = f"Result: {top_result}" if top_result else "Delivered measurable impact."
        post_text = (
            f"🚀 {headline}\n\n"
            f"{project_desc[:280]}\n\n"
            f"{result_line}\n\n"
            f"Always looking to connect with engineers solving hard problems.\n\n"
            f"#{row.target_role.replace(' ', '')} #SoftwareEngineering #CareerGrowth"
        )
        logger.info(f"LinkedIn post generated via heuristic for session {session_id}")

    return Feature5LinkedInPostResponse(
        session_id=session_id,
        post_text=post_text,
        character_count=len(post_text),
        generated_at=datetime.now(timezone.utc),
    )
