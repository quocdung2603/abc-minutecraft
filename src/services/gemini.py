"""
Gemini API service — audio analysis + JSON minutes generation.

Provides:
- build_model: create configured GenerativeModel (JSON output, custom temperature).
- generate_minutes: call Gemini with audio payload, auto-fallback through MODEL_FALLBACK_CHAIN,
  parse JSON, raise domain-specific exceptions on error.

Exception hierarchy (all have .error_code attribute):
  MinuteCraftError (base)
  ├── InvalidAPIKeyError  (error_code="INVALID_KEY")
  ├── RateLimitError     (error_code="RATE_LIMIT")
  ├── NetworkError       (error_code="NETWORK")
  ├── ModelNotFoundError (error_code="MODEL_NOT_FOUND")
  └── AudioTooLargeError (error_code="AUDIO_TOO_LARGE")
"""
import json
from typing import Optional, Union

import google.generativeai as genai
from google.generativeai.types import File as GeminiFile

from src.config import MODEL_FALLBACK_CHAIN


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class MinuteCraftError(Exception):
    def __init__(self, message: str, error_code: str = "UNKNOWN"):
        super().__init__(message)
        self.error_code = error_code


class InvalidAPIKeyError(MinuteCraftError):
    def __init__(self, message: str):
        super().__init__(message, error_code="INVALID_KEY")


class RateLimitError(MinuteCraftError):
    def __init__(self, message: str):
        super().__init__(message, error_code="RATE_LIMIT")


class NetworkError(MinuteCraftError):
    def __init__(self, message: str):
        super().__init__(message, error_code="NETWORK")


class ModelNotFoundError(MinuteCraftError):
    def __init__(self, message: str):
        super().__init__(message, error_code="MODEL_NOT_FOUND")


class AudioTooLargeError(MinuteCraftError):
    def __init__(self, message: str):
        super().__init__(message, error_code="AUDIO_TOO_LARGE")


# ---------------------------------------------------------------------------
# Error classifier
# ---------------------------------------------------------------------------

def _classify_error(exc: Exception) -> type[MinuteCraftError]:
    """Map raw exception → domain error class based on string content."""
    s = str(exc).lower()
    if any(kw in s for kw in ["api key", "api_key_invalid", "401", "403", "invalid credentials"]):
        return InvalidAPIKeyError
    if any(kw in s for kw in ["429", "rate", "quota", "resource_exhausted", "rate limit", "too many requests"]):
        return RateLimitError
    if any(kw in s for kw in ["too large", "size limit", "max size", "audio too large", "maximum file size"]):
        return AudioTooLargeError
    if any(kw in s for kw in ["timeout", "connection", "network", "econnrefused", "name or service not known"]):
        return NetworkError
    return MinuteCraftError


# ---------------------------------------------------------------------------
# Model builder
# ---------------------------------------------------------------------------

def build_model(model_name: str, temperature: float, system_instruction: str) -> genai.GenerativeModel:
    """Create GenerativeModel with JSON response mode and custom temperature/system instruction."""
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "temperature": temperature,
            "response_mime_type": "application/json",
        },
        system_instruction=system_instruction,
    )


# ---------------------------------------------------------------------------
# Core generation
# ---------------------------------------------------------------------------

def generate_minutes(
    audio_payload: Union[dict, GeminiFile],
    prompt: str,
    temperature: float,
    system_instruction: str,
    preferred_model: str,
) -> tuple[dict, str]:
    """
    Call Gemini API to analyze audio and produce a meeting-minutes JSON.

    Flow:
    1. Try preferred_model; on 404 → silent skip, try next in MODEL_FALLBACK_CHAIN.
    2. On 401/403/429/timeout → raise domain exception immediately (no further fallback).
    3. If all models fail → raise ModelNotFoundError.
    4. Parse JSON response and normalize to dict.

    Returns:
        (parsed_json_dict, actual_model_used)

    Raises:
        InvalidAPIKeyError, RateLimitError, NetworkError, AudioTooLargeError, ModelNotFoundError.
    """
    # Build deduplicated chain: preferred first, then fallback
    seen: set[str] = set()
    chain: list[str] = []
    for m in [preferred_model] + MODEL_FALLBACK_CHAIN:
        if m not in seen:
            seen.add(m)
            chain.append(m)

    response = None
    last_err: Optional[Exception] = None
    actual_model_used: Optional[str] = None

    for model_name in chain:
        try:
            model = build_model(model_name, temperature, system_instruction)
            response = model.generate_content([audio_payload, prompt])
            actual_model_used = model_name
            break
        except Exception as exc:  # noqa: BLE001
            err_str = str(exc).lower()
            # 404 / model-not-found → skip, try next model
            if any(kw in err_str for kw in ["404", "not found", "no longer available", "model not found"]):
                last_err = exc
                continue
            # Other errors → classify and raise immediately
            last_err = exc
            raise _classify_error(exc)(str(exc))

    if response is None or actual_model_used is None:
        raise ModelNotFoundError(f"No model in chain available: {chain}. Last error: {last_err}")

    # Strip markdown fences
    raw_text = response.text.strip()
    for fence in ("```json", "```"):
        if raw_text.startswith(fence):
            raw_text = raw_text[len(fence):]
    for fence in ("```",):
        if raw_text.endswith(fence):
            raw_text = raw_text[: -len(fence)]
    raw_text = raw_text.strip()

    # Parse JSON
    try:
        result: dict = json.loads(raw_text)
    except json.JSONDecodeError as jexc:
        raise MinuteCraftError(
            f"Cannot parse JSON from response: {raw_text[:200]}",
            error_code="PARSE_ERROR",
        ) from jexc

    # Normalize to dict
    if isinstance(result, list):
        result = result[0] if (result and isinstance(result[0], dict)) else {"summary": str(result)}
    elif not isinstance(result, dict):
        result = {"summary": str(result)}

    return result, actual_model_used
