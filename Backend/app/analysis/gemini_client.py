"""
Shared Gemini API client for Career OS.
Uses gemini-1.5-flash for low-latency, cost-effective inference.
All calls are non-blocking best-effort — if Gemini is unavailable,
callers fall back to their existing heuristic results.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx

_MODEL = "gemini-2.0-flash"
_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
_TIMEOUT = 20.0


def _api_key() -> str:
    return (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or ""
    ).strip()


def is_available() -> bool:
    return bool(_api_key())


def generate(prompt: str, temperature: float = 0.4, max_tokens: int = 1024) -> str:
    """
    Send a single prompt to Gemini and return the text response.
    Returns empty string on any failure so callers can fall back gracefully.
    """
    key = _api_key()
    if not key:
        return ""

    url = f"{_BASE_URL}/{_MODEL}:generateContent?key={key}"
    body: Dict[str, Any] = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            res = client.post(url, json=body)
            if res.status_code >= 400:
                return ""
            payload = res.json()
    except Exception:
        return ""

    parts: List[str] = []
    for candidate in payload.get("candidates", []):
        for part in (candidate.get("content") or {}).get("parts") or []:
            text = str(part.get("text") or "").strip()
            if text:
                parts.append(text)

    return "\n".join(parts).strip()


def generate_json(prompt: str, temperature: float = 0.2, max_tokens: int = 2048) -> str:
    """
    Ask Gemini to return JSON. Wraps the prompt with a JSON instruction.
    Returns the raw text — caller is responsible for json.loads().
    """
    json_prompt = (
        f"{prompt}\n\n"
        "IMPORTANT: Respond with valid JSON only. "
        "No markdown fences, no explanation text, just the JSON object."
    )
    return generate(json_prompt, temperature=temperature, max_tokens=max_tokens)
