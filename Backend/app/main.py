import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .api.jobs import router as jobs_router
from .api.feature1 import router as feature1_router
from .api.feature2 import router as feature2_router
from .api.feature3 import router as feature3_router
from .api.feature4 import router as feature4_router
from .api.feature5 import router as feature5_router
from .api.metrics import router as metrics_router
from .api.auth import router as auth_router
from .api.core import router as core_router
from .db import create_db_and_tables
from . import models_jobs  # noqa: F401 — ensures Job table is registered with SQLModel metadata

app = FastAPI(
    title="Career-OS Backend",
    version="0.1.0",
    description="Feature 1 implementation for Hiring Manager's Lens.",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5500")
ALLOWED_ORIGINS = [o.strip() for o in _raw.split(",") if o.strip()]
allow_credentials = "*" not in ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(jobs_router)
app.include_router(feature1_router)
app.include_router(feature2_router)
app.include_router(feature3_router)
app.include_router(feature4_router)
app.include_router(feature5_router)
app.include_router(metrics_router)
app.include_router(auth_router)
app.include_router(core_router)
