"""
Shared Gemini API client for Career OS.
Uses gemini-2.0-flash for low-latency, cost-effective inference.
All calls are non-blocking best-effort — if Gemini is unavailable,
callers fall back to their existing heuristic results.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("career_os.gemini_client")

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
    
    Handles:
    - Connection timeouts (20 seconds)
    - HTTP errors (4xx, 5xx) including rate limiting (429)
    - Malformed JSON responses
    - Network failures
    """
    key = _api_key()
    if not key:
        logger.warning("Gemini API key not configured")
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
            
            # Handle specific HTTP error cases
            if res.status_code == 429:
                logger.error("Gemini API rate limit exceeded (429)")
                return ""
            elif res.status_code >= 500:
                logger.error(f"Gemini API server error: {res.status_code}")
                return ""
            elif res.status_code >= 400:
                logger.error(f"Gemini API client error: {res.status_code}")
                return ""
            
            # Parse JSON response
            try:
                payload = res.json()
            except json.JSONDecodeError as e:
                logger.error(f"Gemini API returned malformed JSON: {e}")
                return ""
                
    except httpx.TimeoutException:
        logger.error(f"Gemini API request timed out after {_TIMEOUT} seconds")
        return ""
    except httpx.NetworkError as e:
        logger.error(f"Gemini API network error: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error calling Gemini API: {e}")
        return ""

    # Extract text from response
    parts: List[str] = []
    try:
        for candidate in payload.get("candidates", []):
            content = candidate.get("content")
            if not content:
                continue
            for part in content.get("parts", []):
                text = str(part.get("text", "")).strip()
                if text:
                    parts.append(text)
    except (AttributeError, TypeError) as e:
        logger.error(f"Gemini API response structure unexpected: {e}")
        return ""

    return "\n".join(parts).strip()


def generate_json(prompt: str, temperature: float = 0.2, max_tokens: int = 2048) -> str:
    """
    Ask Gemini to return JSON. Wraps the prompt with a JSON instruction.
    Returns the raw text — caller is responsible for json.loads().
    
    Handles the same error cases as generate():
    - Connection timeouts
    - HTTP errors including rate limiting
    - Malformed responses
    - Network failures
    
    Returns empty string on any failure for graceful fallback.
    """
    json_prompt = (
        f"{prompt}\n\n"
        "IMPORTANT: Respond with valid JSON only. "
        "No markdown fences, no explanation text, just the JSON object."
    )
    return generate(json_prompt, temperature=temperature, max_tokens=max_tokens)
