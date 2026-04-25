import os
import uuid
from pathlib import Path

# Load .env file if present (before any other imports that read env vars)
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _key, _, _val = _line.partition("=")
            os.environ.setdefault(_key.strip(), _val.strip())

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlmodel import Session, select

from .api.jobs import router as jobs_router
from .api.feature1 import router as feature1_router
from .api.feature2 import router as feature2_router
from .api.feature3 import router as feature3_router
from .api.feature4 import router as feature4_router
from .api.feature5 import router as feature5_router
from .api.metrics import build_dashboard_metrics, router as metrics_router
from .api.auth import router as auth_router
from .api.core import router as core_router
from .db import create_db_and_tables, engine as db_engine
from . import models_jobs  # noqa: F401 — ensures Job table is registered with SQLModel metadata

logger = logging.getLogger("career_os")

app = FastAPI(
    title="Career-OS Backend",
    version="0.1.0",
    description="AI-powered career intelligence platform.",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_raw = os.getenv(
    "ALLOWED_ORIGINS",
    "*"
)
ALLOWED_ORIGINS = [o.strip() for o in _raw.split(",") if o.strip()]
# When using wildcard, credentials must be False
allow_credentials = "*" not in ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 1.7: Global exception handler ────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    import traceback
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "code": "INTERNAL_ERROR"},
    )


# ── 8.5: X-Request-ID + 1.8/8.7: Security headers ───────────────────────────
@app.middleware("http")
async def add_security_and_request_id(request: Request, call_next):
    # Honour incoming X-Request-ID or generate a new one
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    response = await call_next(request)

    # 8.5: Tracing header
    response.headers["X-Request-ID"] = request_id

    # 1.8 / 8.7: Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com https://fonts.googleapis.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src *;"
    )
    return response


# ── 8.4: Write-endpoint rate limiter (shared instance) ───────────────────────
write_limiter = Limiter(key_func=get_remote_address)


@app.on_event("startup")
def on_startup() -> None:
    # Ensure data directories exist before creating DB tables
    from pathlib import Path
    Path("/app/data/uploads").mkdir(parents=True, exist_ok=True)
    Path("/app/data/reports").mkdir(parents=True, exist_ok=True)
    create_db_and_tables()


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok", "version": "0.1.0"}


# ── 8.3: Composite /api/me/dashboard endpoint ────────────────────────────────
def _resolve_bearer(authorization: str) -> Optional[str]:
    """Return raw token from Authorization header or None."""
    if authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return None


def _hash_token(raw: str) -> str:
    secret = os.getenv("CAREER_OS_AUTH_SECRET", "career-os-dev-secret-change-me")
    return hashlib.sha256(f"{raw}:{secret}".encode()).hexdigest()


def _safe_json_dict(raw: Optional[str]) -> Dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return round(float(value), 2)
    except Exception:
        return None


def _safe_json_list(raw: Optional[str]) -> list:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else []


def _readiness_label(score: float) -> str:
    if score >= 85:
        return "Ready to Apply"
    if score >= 70:
        return "Strong Candidate"
    if score >= 50:
        return "Building Momentum"
    return "Needs More Signal"


def _readiness_tone(score: float) -> str:
    if score >= 85:
        return "success"
    if score >= 70:
        return "info"
    if score >= 50:
        return "warning"
    return "danger"


@app.get("/api/me/dashboard")
def me_dashboard(request: Request) -> Dict[str, Any]:
    """
    Composite dashboard endpoint (8.3).
    Returns: auth user + latest Feature 1 analysis + job pipeline counts + readiness score.
    """
    from .models import (
        AnalyticsEvent,
        Feature1Analysis,
        Feature2InterviewAutopsy,
        Feature3GapSnapshot,
        UserAccount,
        UserSessionToken,
    )
    from .models_jobs import Job

    authorization = request.headers.get("Authorization", "")
    raw_token = _resolve_bearer(authorization)
    if not raw_token:
        return JSONResponse(status_code=401, content={"detail": "Missing bearer token."})

    token_hash = _hash_token(raw_token)

    with Session(db_engine) as session:
        token = session.exec(
            select(UserSessionToken).where(UserSessionToken.token_hash == token_hash)
        ).first()

        if token is None or token.revoked_at is not None:
            return JSONResponse(status_code=401, content={"detail": "Invalid or revoked session."})

        now = datetime.now(timezone.utc)
        expires = token.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < now:
            return JSONResponse(status_code=401, content={"detail": "Session expired."})

        user = session.get(UserAccount, token.user_id)
        if user is None or not user.is_active:
            return JSONResponse(status_code=401, content={"detail": "User not found."})

        # Latest Feature 1 analysis
        f1 = session.exec(
            select(Feature1Analysis)
            .where(Feature1Analysis.candidate_id == user.candidate_id)
            .order_by(Feature1Analysis.created_at.desc())
        ).first()

        # Job pipeline counts
        jobs = session.exec(
            select(Job).where(Job.owner_id == user.id)
        ).all()
        pipeline: Dict[str, int] = {}
        for job in jobs:
            status_key = getattr(job.status, "value", str(job.status))
            pipeline[status_key] = pipeline.get(status_key, 0) + 1

        # Latest interview score
        f2 = session.exec(
            select(Feature2InterviewAutopsy)
            .where(Feature2InterviewAutopsy.candidate_id == user.candidate_id)
            .order_by(Feature2InterviewAutopsy.created_at.desc())
        ).first()

        # Latest gap score
        f3 = session.exec(
            select(Feature3GapSnapshot)
            .where(Feature3GapSnapshot.candidate_id == user.candidate_id)
            .order_by(Feature3GapSnapshot.created_at.desc())
        ).first()

        # Optional analytics signals that power the dashboard chart and recent activity feed.
        analytics = build_dashboard_metrics(session, user_id=user.candidate_id, window_days=30)

        interview_score_json = _safe_json_dict(f2.score_json) if f2 else {}
        latest_f1_metrics = _safe_json_dict(f1.metrics_json) if f1 else {}
        latest_f1_recommendations = _safe_json_list(f1.recommendations_json if f1 else None)
        latest_f1_ai_recommendations = _safe_json_list(f1.ai_recommendations_json if f1 else None)

        component_specs = [
            {
                "key": "resume",
                "label": "Resume analysis",
                "weight": 0.5,
                "score": _safe_float(f1.overall_score) if f1 else None,
                "available": f1 is not None,
                "summary": (
                    f"ATS {_safe_float(f1.ats_score) or 0}% · Visual {_safe_float(f1.visual_score) or 0}% · Semantic {_safe_float(f1.semantic_score) or 0}%"
                    if f1
                    else "Not available yet"
                ),
                "source": {
                    "analysis_id": f1.id if f1 else None,
                    "version_number": f1.version_number if f1 else None,
                    "created_at": f1.created_at.isoformat() if f1 else None,
                },
            },
            {
                "key": "interview",
                "label": "Interview performance",
                "weight": 0.3,
                "score": _safe_float(interview_score_json.get("overall_autopsy_score")),
                "available": f2 is not None and _safe_float(interview_score_json.get("overall_autopsy_score")) is not None,
                "summary": (
                    f"Technical {_safe_float(interview_score_json.get('technical_accuracy')) or 0}% · Behavioral {_safe_float(interview_score_json.get('behavioral_quality')) or 0}%"
                    if f2
                    else "Not available yet"
                ),
                "source": {
                    "interview_id": f2.id if f2 else None,
                    "created_at": f2.created_at.isoformat() if f2 else None,
                },
            },
            {
                "key": "market",
                "label": "Skill/market fit",
                "weight": 0.2,
                "score": _safe_float(f3.match_score) if f3 else None,
                "available": f3 is not None,
                "summary": (
                    f"Match {_safe_float(f3.match_score) or 0}% · Gap to top 10 {_safe_float(f3.gap_to_top10_score) or 0}%"
                    if f3
                    else "Not available yet"
                ),
                "source": {
                    "gap_snapshot_id": f3.id if f3 else None,
                    "created_at": f3.created_at.isoformat() if f3 else None,
                },
            },
        ]

        available_weight = sum(component["weight"] for component in component_specs if component["available"] and component["score"] is not None)
        readiness_score = 0.0
        if available_weight:
            weighted_total = sum(
                float(component["score"]) * float(component["weight"])
                for component in component_specs
                if component["available"] and component["score"] is not None
            )
            readiness_score = round(weighted_total / available_weight, 2)

        readiness_components = []
        for component in component_specs:
            normalized_weight = round(component["weight"] / available_weight, 4) if available_weight and component["available"] and component["score"] is not None else 0.0
            contribution = round(float(component["score"]) * normalized_weight, 2) if component["score"] is not None and normalized_weight else 0.0
            readiness_components.append({
                **component,
                "normalized_weight": normalized_weight,
                "contribution": contribution,
            })

        snapshot_chart_data = [
            {"label": "Resume", "value": _safe_float(f1.overall_score) if f1 else 0.0, "available": bool(f1)},
            {"label": "Interview", "value": _safe_float(interview_score_json.get("overall_autopsy_score")) or 0.0, "available": bool(f2 and interview_score_json.get("overall_autopsy_score") is not None)},
            {"label": "Market fit", "value": _safe_float(f3.match_score) if f3 else 0.0, "available": bool(f3)},
        ]

        latest_analysis = {
            "analysis_id": f1.id if f1 else None,
            "version_number": f1.version_number if f1 else None,
            "candidate_id": user.candidate_id,
            "job_category": f1.job_category if f1 else None,
            "overall_score": _safe_float(f1.overall_score) if f1 else None,
            "ready_to_apply": bool(f1.overall_score >= 90.0) if f1 else False,
            "status": "Ready to Apply" if f1 and f1.overall_score >= 90.0 else ("In Progress" if f1 else "Not available yet"),
            "created_at": f1.created_at.isoformat() if f1 else None,
            "summary": f1.ats_summary if f1 else "No resume analysis yet.",
            "score_breakdown": {
                "visual_hierarchy": _safe_float(f1.visual_score) if f1 else None,
                "ats_integrity": _safe_float(f1.ats_score) if f1 else None,
                "semantic_match": _safe_float(f1.semantic_score) if f1 else None,
                "competitive_benchmark": _safe_float(f1.benchmark_score) if f1 else None,
            },
            "summaries": {
                "visual": f1.eye_tracking_summary if f1 else None,
                "ats": f1.ats_summary if f1 else None,
                "semantic": f1.semantic_summary if f1 else None,
                "benchmark": f1.benchmark_summary if f1 else None,
            },
            "metrics": latest_f1_metrics,
            "recommendations": latest_f1_recommendations,
            "ai_recommendations": latest_f1_ai_recommendations,
        }

        interview_analysis = {
            "interview_id": f2.id if f2 else None,
            "candidate_id": user.candidate_id,
            "company_name": f2.company_name if f2 else None,
            "role_name": f2.role_name if f2 else None,
            "interview_round": f2.interview_round if f2 else None,
            "created_at": f2.created_at.isoformat() if f2 else None,
            "overall_score": _safe_float(interview_score_json.get("overall_autopsy_score")),
            "score_breakdown": {
                "technical_accuracy": _safe_float(interview_score_json.get("technical_accuracy")),
                "behavioral_quality": _safe_float(interview_score_json.get("behavioral_quality")),
                "strategic_recovery_readiness": _safe_float(interview_score_json.get("strategic_recovery_readiness")),
            },
            "summary": f2.rejection_reason_hint if f2 else None,
        }

        market_analysis = {
            "gap_snapshot_id": f3.id if f3 else None,
            "candidate_id": user.candidate_id,
            "match_score": _safe_float(f3.match_score) if f3 else None,
            "gap_to_top10_score": _safe_float(f3.gap_to_top10_score) if f3 else None,
            "created_at": f3.created_at.isoformat() if f3 else None,
            "summary": "Market-fit data will appear after Skill Arbitrage runs." if not f3 else "Market-fit snapshot loaded.",
        }

        next_actions = []
        if f1 is None:
            next_actions.append({"label": "Run Feature 1 resume analysis", "view": "lens-engine", "priority": 1})
        elif f1.overall_score < 90:
            next_actions.append({"label": "Review resume recommendations", "view": "lens-engine", "priority": 1})
        if f2 is None:
            next_actions.append({"label": "Capture interview debrief", "view": "rebound", "priority": 2})
        if f3 is None:
            next_actions.append({"label": "Run skill-gap analysis", "view": "arbitrage", "priority": 3})
        if not next_actions:
            next_actions.append({"label": "You are ready to apply - keep the pipeline active", "view": "job-tracker", "priority": 1})

        next_actions = sorted(next_actions, key=lambda item: item["priority"])

        activity_trend = analytics.get("activity_trend", [])
        dashboard_metrics = {
            **analytics,
            "chart_data": activity_trend,
            "snapshot_chart_data": snapshot_chart_data,
        }

        if activity_trend and not any(point.get("events", 0) for point in activity_trend):
            dashboard_metrics["chart_data"] = snapshot_chart_data

        status_indicators = {
            "ready_to_apply": readiness_score >= 85,
            "resume_ready": bool(f1),
            "interview_ready": bool(f2),
            "market_ready": bool(f3),
            "dashboard_state": "ready" if readiness_score >= 85 else ("building" if any(component["available"] for component in readiness_components) else "empty"),
        }

        # Readiness score (simple average of available scores)
        readiness = readiness_score

        return {
            "user": {
                "user_id": user.id,
                "candidate_id": user.candidate_id,
                "email": user.email,
                "full_name": user.full_name,
            },
            "readiness_score": readiness,
            "readiness": {
                "score": readiness,
                "label": _readiness_label(readiness),
                "tone": _readiness_tone(readiness),
                "formula": "Normalized weighted average: resume 50%, interview 30%, market fit 20%. Missing components are renormalized across available signals.",
                "components": readiness_components,
            },
            "latest_analysis": latest_analysis,
            "interview_analysis": interview_analysis,
            "market_analysis": market_analysis,
            "job_pipeline": pipeline,
            "total_jobs": len(jobs),
            "analytics": dashboard_metrics,
            "next_actions": next_actions,
            "status_indicators": status_indicators,
            "generated_at": now.isoformat(),
        }


app.include_router(jobs_router)
app.include_router(feature1_router)
app.include_router(feature2_router)
app.include_router(feature3_router)
app.include_router(feature4_router)
app.include_router(feature5_router)
app.include_router(metrics_router)
app.include_router(auth_router)
app.include_router(core_router)

# ── Static frontend (Railway single-service deployment) ───────────────────────
# In the Railway image, Frontend is copied to /Frontend.
# Wrapped in try/except so a missing dir never crashes startup.
_frontend_dir = Path("/Frontend")
if not _frontend_dir.exists():
    _frontend_dir = Path(__file__).resolve().parent.parent.parent / "Frontend"

if _frontend_dir.exists():
    try:
        app.mount("/static", StaticFiles(directory=str(_frontend_dir)), name="static")
        logger.info(f"Frontend static files mounted from {_frontend_dir}")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")

    @app.get("/", include_in_schema=False)
    def serve_index():
        _idx = _frontend_dir / "index.html"
        if _idx.exists():
            return FileResponse(str(_idx))
        return JSONResponse({"status": "ok", "message": "Career OS API"})

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        # Never intercept API routes — let them 404 naturally
        if full_path.startswith("api/") or full_path == "health" or full_path == "docs" or full_path == "openapi.json":
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        file_path = _frontend_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        _idx = _frontend_dir / "index.html"
        if _idx.exists():
            return FileResponse(str(_idx))
        return JSONResponse({"status": "ok", "message": "Career OS API"})
else:
    logger.info("Frontend directory not found — serving API only")
