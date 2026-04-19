from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    candidate_id: str = Field(min_length=3, max_length=80)
    email: str = Field(min_length=5, max_length=200)
    full_name: str = Field(default="", max_length=120)
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=200)
    password: str = Field(min_length=8, max_length=200)


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
