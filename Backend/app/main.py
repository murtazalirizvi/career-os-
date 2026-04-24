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
from .api.metrics import router as metrics_router
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


@app.get("/api/me/dashboard")
def me_dashboard(request: Request) -> Dict[str, Any]:
    """
    Composite dashboard endpoint (8.3).
    Returns: auth user + latest Feature 1 analysis + job pipeline counts + readiness score.
    """
    from .models import (
        UserAccount, UserSessionToken,
        Feature1Analysis, Feature2InterviewAutopsy, Feature3GapSnapshot,
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
            pipeline[job.status.value] = pipeline.get(job.status.value, 0) + 1

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

        # Readiness score (simple average of available scores)
        scores = []
        if f1:
            scores.append(float(f1.overall_score))
        if f2:
            try:
                s = json.loads(f2.score_json).get("overall_autopsy_score")
                if s is not None:
                    scores.append(float(s))
            except Exception:
                pass
        if f3:
            scores.append(float(f3.match_score))
        readiness = round(sum(scores) / len(scores), 2) if scores else 0.0

        return {
            "user": {
                "candidate_id": user.candidate_id,
                "email": user.email,
                "full_name": user.full_name,
            },
            "latest_analysis": {
                "analysis_id": f1.id if f1 else None,
                "overall_score": float(f1.overall_score) if f1 else None,
                "created_at": f1.created_at.isoformat() if f1 else None,
            },
            "job_pipeline": pipeline,
            "total_jobs": len(jobs),
            "readiness_score": readiness,
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
