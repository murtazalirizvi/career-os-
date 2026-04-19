from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session, select

from ..db import get_session
from ..models import UserAccount, UserSessionToken
from ..schemas_auth import AuthEnvelope, LoginRequest, LogoutRequest, RegisterRequest, SessionResponse, UserProfileResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
limiter = Limiter(key_func=get_remote_address)


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


def _make_session(user_id: int, session: Session) -> SessionResponse:
    raw = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw)
    expires_at = _utc_now() + timedelta(days=7)

    row = UserSessionToken(
        user_id=user_id,
        token_hash=token_hash,
        label="web",
        expires_at=expires_at,
    )
    session.add(row)
    session.commit()
    return SessionResponse(access_token=raw, expires_at=expires_at)


def _to_profile(user: UserAccount) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=user.id,
        candidate_id=user.candidate_id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
    )


@router.post("/register", response_model=AuthEnvelope)
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    existing_candidate = session.exec(select(UserAccount).where(UserAccount.candidate_id == payload.candidate_id)).first()
    if existing_candidate:
        raise HTTPException(status_code=409, detail="Candidate ID already exists.")

    existing_email = session.exec(select(UserAccount).where(UserAccount.email == payload.email)).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already exists.")

    user = UserAccount(
        candidate_id=payload.candidate_id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=_hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    auth_session = _make_session(user.id, session)
    return AuthEnvelope(user=_to_profile(user), session=auth_session)


@router.post("/login", response_model=AuthEnvelope)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(UserAccount).where(UserAccount.email == payload.email)).first()
    if not user or not user.is_active or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    auth_session = _make_session(user.id, session)
    user.updated_at = _utc_now()
    session.add(user)
    session.commit()

    return AuthEnvelope(user=_to_profile(user), session=auth_session)


@router.get("/me", response_model=AuthEnvelope)
def me(authorization: str = Header(default=""), session: Session = Depends(get_session)):
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token.")

    raw = authorization.split(" ", 1)[1].strip()
    token_hash = _hash_token(raw)
    token = session.exec(select(UserSessionToken).where(UserSessionToken.token_hash == token_hash)).first()
    if token is None or token.revoked_at is not None or _as_utc(token.expires_at) < _utc_now():
        raise HTTPException(status_code=401, detail="Session is invalid or expired.")

    user = session.get(UserAccount, token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive.")

    return AuthEnvelope(user=_to_profile(user), session=None)


@router.post("/logout")
def logout(payload: LogoutRequest, session: Session = Depends(get_session)):
    token_hash = _hash_token(payload.access_token)
    token = session.exec(select(UserSessionToken).where(UserSessionToken.token_hash == token_hash)).first()
    if token is None:
        return {"ok": True, "revoked": False}

    token.revoked_at = _utc_now()
    session.add(token)
    session.commit()
    return {"ok": True, "revoked": True}
