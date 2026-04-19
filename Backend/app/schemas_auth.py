from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator
import re


class RegisterRequest(BaseModel):
    # candidate_id is optional — auto-derived from email if not supplied
    candidate_id: Optional[str] = Field(default=None, min_length=3, max_length=80)
    email: str = Field(min_length=5, max_length=200)
    full_name: str = Field(default="", max_length=120)
    password: str = Field(min_length=8, max_length=200)

    @field_validator("candidate_id", mode="before")
    @classmethod
    def derive_candidate_id(cls, v: Optional[str], info) -> str:
        """Auto-generate a safe candidate_id from email if not provided."""
        if v and str(v).strip():
            return str(v).strip()
        # Derive from email: take local part, strip special chars
        email = (info.data or {}).get("email", "") or ""
        local = email.split("@")[0] if "@" in email else email
        safe = re.sub(r"[^a-zA-Z0-9_-]", "-", local)[:40].strip("-") or "user"
        return safe


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=200)
    password: str = Field(min_length=8, max_length=200)


class RefreshRequest(BaseModel):
    access_token: str


class SessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class UserProfileResponse(BaseModel):
    user_id: int
    candidate_id: str
    email: str
    full_name: str
    is_active: bool


class LogoutRequest(BaseModel):
    access_token: str


class AuthEnvelope(BaseModel):
    user: UserProfileResponse
    session: Optional[SessionResponse] = None
