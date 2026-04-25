"""
Feature 5: Narrative Architect - Portfolio & Story Generation Engine
Transforms GitHub projects into compelling interview stories and portfolio content
Last Updated: April 25, 2026
"""

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
        # Extract rich context for Gemini
        deep = _loads(row.deep_analysis_json).get("epic_5_1", {}) or {}
        arch_style = deep.get("architecture_mapping", {}).get("identified_style", "modular")
        sophistication = deep.get("sophistication_scoring", {}).get("score", 0)
        sophistication_tier = deep.get("sophistication_scoring", {}).get("tier", "intermediate")
        impact_metrics = (narrative.get("epic_5_2", {}) or {}).get("impact_metrics", [])
        problem_lines = (narrative.get("epic_5_2", {}) or {}).get("problem_solution_narrative", [])
        
        prompt = (
            f"Write a detailed, engaging LinkedIn post for a {row.target_role} showcasing real technical work.\n\n"
            f"PROJECT CONTEXT:\n"
            f"- Architecture: {arch_style}\n"
            f"- Sophistication score: {sophistication}/100 ({sophistication_tier})\n"
            f"- Headline: {headline}\n"
            f"- Project description: {project_desc[:400]}\n"
            f"- Problem solved: {problem_lines[0][:200] if problem_lines else 'N/A'}\n"
            f"- Top result: {top_result[:200]}\n"
            f"- Impact metrics: {', '.join(impact_metrics[:3]) if impact_metrics else 'N/A'}\n"
            f"- STAR stories: {len(star_summaries)} documented\n\n"
            "REQUIREMENTS — follow these exactly:\n"
            "1. HOOK (line 1): Start with a bold, curiosity-triggering statement or question. NOT 'I built' or 'Excited to share'. Use an insight, a surprising fact, or a relatable pain point.\n"
            "2. PROBLEM (2-3 lines): Describe the real problem this solves. Be specific. Use numbers if possible.\n"
            "3. SOLUTION (3-4 lines): Explain what you built and HOW. Mention the architecture, key technical decisions, and trade-offs you made. Show depth.\n"
            "4. RESULTS (2-3 lines): Quantify impact. Use metrics, percentages, time saved, or before/after comparisons.\n"
            "5. INSIGHT (1-2 lines): Share one genuine lesson or unexpected discovery from building this.\n"
            "6. CTA (1 line): End with a specific question that invites comments — not generic 'let's connect'.\n"
            "7. HASHTAGS: 5-7 specific, relevant hashtags on the last line.\n\n"
            "STYLE RULES:\n"
            "- Use emojis strategically (1-2 per section, not every line)\n"
            "- Write like a senior engineer talking to peers, not a recruiter\n"
            "- Avoid buzzwords: 'leverage', 'synergy', 'passionate', 'excited to share'\n"
            "- Be specific and technical — vague posts get ignored\n"
            "- Total length: 100-150 words maximum — tight, punchy, no fluff\n"
            "- Use line breaks between sections for readability\n\n"
            "Return ONLY the post text. No preamble, no 'Here is your post:', nothing extra."
        )
        try:
            post_text = gemini_client.generate(prompt, temperature=0.7, max_tokens=600)
            if not post_text or len(post_text.strip()) < 100:
                raise ValueError("Empty or too short response")
            post_text = post_text.strip()
            logger.info(f"LinkedIn post generated via Gemini for session {session_id}")
        except Exception as e:
            logger.warning(f"Gemini LinkedIn post failed for session {session_id}: {e}")
            post_text = None
    else:
        post_text = None

    # Heuristic fallback — rich, engaging LinkedIn post
    if not post_text:
        # Extract rich context from the session
        deep = _loads(row.deep_analysis_json).get("epic_5_1", {}) or {}
        arch_style = deep.get("architecture_mapping", {}).get("identified_style", "modular")
        sophistication = deep.get("sophistication_scoring", {}).get("score", 0)
        sophistication_tier = deep.get("sophistication_scoring", {}).get("tier", "intermediate")
        custom_logic = deep.get("logic_identification", {}).get("custom_logic_ratio", 0)
        
        star = star_summaries[:2] if len(star_summaries) >= 2 else star_summaries
        impact_metrics = (narrative.get("epic_5_2", {}) or {}).get("impact_metrics", [])
        problem_lines = (narrative.get("epic_5_2", {}) or {}).get("problem_solution_narrative", [])
        
        # Build the post with hooks, storytelling, and engagement
        hook = "💡 Ever wondered how to turn your GitHub projects into compelling interview stories?"
        if sophistication >= 80:
            hook = "🚀 Just shipped a production-grade system that solves a real problem engineers face every day."
        elif sophistication >= 60:
            hook = "⚡ Built something I'm genuinely proud of — and learned a ton in the process."
        
        # Problem statement
        problem = problem_lines[0] if problem_lines else "Developers struggle to articulate their technical work in interviews."
        
        # Solution with architecture details
        solution_parts = []
        solution_parts.append(f"Built a {arch_style} architecture")
        if custom_logic >= 70:
            solution_parts.append(f"with {custom_logic}% custom business logic")
        solution_parts.append(f"(sophistication: {sophistication_tier})")
        solution = " ".join(solution_parts) + "."
        
        # STAR stories with emojis
        star_section = ""
        if star:
            star_section = "\n\n📊 Key wins:\n"
            for i, s in enumerate(star[:2], 1):
                proj = s.get("project", "Component")
                action = s.get("action", "")
                result = s.get("result", "")
                if action and result:
                    star_section += f"\n{i}. {proj}: {action}\n   → {result}"
        
        # Impact metrics
        metrics_section = ""
        if impact_metrics:
            metrics_section = "\n\n" + " · ".join(impact_metrics[:2])
        
        # Technical depth callout
        tech_callout = ""
        if sophistication >= 75:
            tech_callout = f"\n\n🔧 Technical depth: {sophistication}/100 — production-ready patterns, error handling, and scalability considerations baked in."
        
        # Call to action
        cta = "\n\nWhat's the hardest part of your job search right now? Let's connect and share notes. 👇"
        
        # Hashtags
        role_tag = row.target_role.replace(" ", "").replace("-", "")
        hashtags = f"\n\n#{role_tag} #SoftwareEngineering #BuildInPublic #TechCareers #DeveloperJourney"
        
        post_text = hook + "\n\n" + problem + "\n\n" + solution + star_section + metrics_section + tech_callout + cta + hashtags
        
        # Trim if over 150 words
        words = post_text.split()
        if len(words) > 150:
            # Keep hook + first STAR + hashtags
            post_text = " ".join(words[:140]) + "...\n\n" + hashtags
        
        logger.info(f"LinkedIn post generated via rich heuristic for session {session_id}")

    return Feature5LinkedInPostResponse(
        session_id=session_id,
        post_text=post_text,
        character_count=len(post_text),
        generated_at=datetime.now(timezone.utc),
    )
