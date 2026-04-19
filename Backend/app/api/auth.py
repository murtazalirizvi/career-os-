from __future__ import annotations

import hashlib
import os
import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session, select

from ..db import get_session
from ..models import UserAccount, UserSessionToken
from ..schemas_auth import (
    AuthEnvelope,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    SessionResponse,
    UserProfileResponse,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
limiter = Limiter(key_func=get_remote_address)

_SESSION_TTL_DAYS = 7
_REFRESH_WINDOW_DAYS = 1  # refresh allowed when < 1 day remaining


# ── Helpers ───────────────────────────────────────────────────────────────────

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _secret() -> str:
    return os.getenv("CAREER_OS_AUTH_SECRET", "career-os-dev-secret-change-me")


def _hash_password(password: str) -> str:
    return _pwd_ctx.hash(password)


def _verify_password(password: str, stored: str) -> bool:
    return _pwd_ctx.verify(password, stored)


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(f"{raw_token}:{_secret()}".encode("utf-8")).hexdigest()


def _make_session(user_id: int, db: Session, label: str = "web") -> SessionResponse:
    raw = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw)
    expires_at = _utc_now() + timedelta(days=_SESSION_TTL_DAYS)

    row = UserSessionToken(
        user_id=user_id,
        token_hash=token_hash,
        label=label,
        expires_at=expires_at,
    )
    db.add(row)
    db.commit()
    return SessionResponse(access_token=raw, expires_at=expires_at)


def _to_profile(user: UserAccount) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=user.id,
        candidate_id=user.candidate_id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
    )


def _unique_candidate_id(base: str, db: Session) -> str:
    """Ensure candidate_id is unique — append a short suffix if taken."""
    candidate = base
    for attempt in range(10):
        existing = db.exec(
            select(UserAccount).where(UserAccount.candidate_id == candidate)
        ).first()
        if not existing:
            return candidate
        candidate = f"{base}-{secrets.token_hex(3)}"
    return f"{base}-{secrets.token_hex(6)}"


def _resolve_token(authorization: str, db: Session) -> tuple[UserSessionToken, UserAccount]:
    """Shared token resolution used by /me and /refresh."""
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token.")

    raw = authorization.split(" ", 1)[1].strip()
    token_hash = _hash_token(raw)
    token = db.exec(
        select(UserSessionToken).where(UserSessionToken.token_hash == token_hash)
    ).first()

    if token is None or token.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Session is invalid or has been revoked.")

    if _as_utc(token.expires_at) < _utc_now():
        raise HTTPException(status_code=401, detail="Session has expired. Please log in again.")

    user = db.get(UserAccount, token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive.")

    return token, user


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=AuthEnvelope)
def register(payload: RegisterRequest, db: Session = Depends(get_session)):
    # candidate_id is auto-derived from email if not provided (handled in schema)
    base_id = payload.candidate_id or re.sub(
        r"[^a-zA-Z0-9_-]", "-", payload.email.split("@")[0]
    )[:40].strip("-") or "user"

    candidate_id = _unique_candidate_id(base_id, db)

    existing_email = db.exec(
        select(UserAccount).where(UserAccount.email == payload.email)
    ).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = UserAccount(
        candidate_id=candidate_id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=_hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    auth_session = _make_session(user.id, db)
    return AuthEnvelope(user=_to_profile(user), session=auth_session)


@router.post("/login", response_model=AuthEnvelope)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_session)):
    user = db.exec(
        select(UserAccount).where(UserAccount.email == payload.email)
    ).first()
    if not user or not user.is_active or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    auth_session = _make_session(user.id, db)
    user.updated_at = _utc_now()
    db.add(user)
    db.commit()

    return AuthEnvelope(user=_to_profile(user), session=auth_session)


@router.post("/refresh", response_model=AuthEnvelope)
def refresh(payload: RefreshRequest, db: Session = Depends(get_session)):
    """
    Extend a valid session without re-entering credentials.
    Issues a new token and revokes the old one.
    Works even if the token has already expired (within a 24h grace window).
    """
    token_hash = _hash_token(payload.access_token)
    token = db.exec(
        select(UserSessionToken).where(UserSessionToken.token_hash == token_hash)
    ).first()

    if token is None or token.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Token is invalid or already revoked.")

    # Allow refresh up to 24h after expiry (grace window)
    grace_deadline = _as_utc(token.expires_at) + timedelta(hours=24)
    if _utc_now() > grace_deadline:
        raise HTTPException(
            status_code=401,
            detail="Token expired beyond grace window. Please log in again.",
        )

    user = db.get(UserAccount, token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive.")

    # Revoke old token
    token.revoked_at = _utc_now()
    db.add(token)
    db.commit()

    # Issue fresh session
    new_session = _make_session(user.id, db, label="refreshed")
    return AuthEnvelope(user=_to_profile(user), session=new_session)


@router.get("/me", response_model=AuthEnvelope)
def me(authorization: str = Header(default=""), db: Session = Depends(get_session)):
    _, user = _resolve_token(authorization, db)
    return AuthEnvelope(user=_to_profile(user), session=None)


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_session)):
    token_hash = _hash_token(payload.access_token)
    token = db.exec(
        select(UserSessionToken).where(UserSessionToken.token_hash == token_hash)
    ).first()
    if token is None:
        return {"ok": True, "revoked": False}

    token.revoked_at = _utc_now()
    db.add(token)
    db.commit()
    return {"ok": True, "revoked": True}
