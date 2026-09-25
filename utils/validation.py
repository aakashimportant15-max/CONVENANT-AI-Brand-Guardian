"""
Small helpers for safely parsing LLM text output into JSON.
"""
import json
import re


def safe_json_parse(text: str) -> dict | None:
    """
    Attempt to parse `text` as JSON. Strips common wrapping artifacts
    (markdown code fences, leading/trailing prose) before giving up.
    Returns None on failure instead of raising, so callers can decide
    whether to retry or fall back.
    """
    if not text:
        return None

    cleaned = text.strip()

    # Strip ```json ... ``` or ``` ... ``` fences if present.
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1)
    else:
        # Fall back to grabbing the first { ... last } span, in case the
        # model added stray commentary before/after the JSON object.
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end + 1]

    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        return None
