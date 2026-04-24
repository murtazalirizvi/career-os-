"""
Shared AI client for Career OS.
Priority order:
  1. Gemini 2.0 Flash  (if GEMINI_API_KEY / GOOGLE_API_KEY is set)
  2. OpenRouter free model  (if OPENROUTER_API_KEY is set)

All calls are non-blocking best-effort — callers fall back to heuristics
if both providers are unavailable or return errors.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

import httpx

logger = logging.getLogger("career_os.gemini_client")

# ── Provider config ───────────────────────────────────────────────────────────
_GEMINI_MODEL   = "gemini-2.0-flash"
_GEMINI_BASE    = "https://generativelanguage.googleapis.com/v1beta/models"

# Best free model on OpenRouter (no token cost, high context)
_OR_MODEL       = "meta-llama/llama-3.3-70b-instruct:free"
_OR_BASE        = "https://openrouter.ai/api/v1/chat/completions"

_TIMEOUT = 25.0


# ── Key helpers ───────────────────────────────────────────────────────────────

def _gemini_key() -> str:
    return (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()


def _openrouter_key() -> str:
    return (os.getenv("OPENROUTER_API_KEY") or "").strip()


def is_available() -> bool:
    """True if at least one AI provider is configured."""
    return bool(_gemini_key() or _openrouter_key())


# ── Gemini provider ───────────────────────────────────────────────────────────

def _call_gemini(prompt: str, temperature: float, max_tokens: int) -> str:
    key = _gemini_key()
    if not key:
        return ""

    url = f"{_GEMINI_BASE}/{_GEMINI_MODEL}:generateContent?key={key}"
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

        if res.status_code == 429:
            logger.warning("Gemini rate limit (429) — will try OpenRouter")
            return ""
        if res.status_code >= 400:
            logger.warning(f"Gemini HTTP {res.status_code} — will try OpenRouter")
            return ""

        payload = res.json()
    except httpx.TimeoutException:
        logger.warning("Gemini timeout — will try OpenRouter")
        return ""
    except Exception as e:
        logger.warning(f"Gemini error: {e} — will try OpenRouter")
        return ""

    parts: List[str] = []
    try:
        for candidate in payload.get("candidates", []):
            content = candidate.get("content") or {}
            for part in content.get("parts", []):
                text = str(part.get("text", "")).strip()
                if text:
                    parts.append(text)
    except Exception as e:
        logger.warning(f"Gemini response parse error: {e}")
        return ""

    return "\n".join(parts).strip()


# ── OpenRouter provider ───────────────────────────────────────────────────────

def _call_openrouter(prompt: str, temperature: float, max_tokens: int) -> str:
    key = _openrouter_key()
    if not key:
        return ""

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://career-os.app",
        "X-Title": "Career OS",
    }
    body: Dict[str, Any] = {
        "model": _OR_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            res = client.post(_OR_BASE, json=body, headers=headers)

        if res.status_code == 429:
            logger.error("OpenRouter rate limit (429)")
            return ""
        if res.status_code >= 400:
            logger.error(f"OpenRouter HTTP {res.status_code}: {res.text[:200]}")
            return ""

        payload = res.json()
    except httpx.TimeoutException:
        logger.error("OpenRouter timeout")
        return ""
    except Exception as e:
        logger.error(f"OpenRouter error: {e}")
        return ""

    try:
        return payload["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"OpenRouter response parse error: {e}")
        return ""


# ── Public API ────────────────────────────────────────────────────────────────

def generate(prompt: str, temperature: float = 0.4, max_tokens: int = 1024) -> str:
    """
    Generate text using Gemini first, OpenRouter as fallback.
    Returns empty string if both fail — callers handle gracefully.
    """
    # Try Gemini
    result = _call_gemini(prompt, temperature, max_tokens)
    if result:
        return result

    # Fallback to OpenRouter
    result = _call_openrouter(prompt, temperature, max_tokens)
    if result:
        logger.info("Used OpenRouter fallback successfully")
        return result

    logger.warning("All AI providers failed — returning empty string")
    return ""


def generate_json(prompt: str, temperature: float = 0.2, max_tokens: int = 2048) -> str:
    """
    Ask the AI to return JSON. Wraps prompt with JSON instruction.
    Returns raw text — caller is responsible for json.loads().
    """
    json_prompt = (
        f"{prompt}\n\n"
        "IMPORTANT: Respond with valid JSON only. "
        "No markdown fences, no explanation text, just the JSON object."
    )
    return generate(json_prompt, temperature=temperature, max_tokens=max_tokens)
