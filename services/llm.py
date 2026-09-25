"""
Single point of contact with the LLM API. Every services/*.py file calls
call_llm() — nothing else in the app talks to the API directly.
"""
import os
import json
from typing import Type, TypeVar

from groq import Groq
from pydantic import BaseModel, ValidationError

from utils.validation import safe_json_parse

T = TypeVar("T", bound=BaseModel)

MODEL_NAME = "openai/gpt-oss-120b"

# Reasoning models (e.g. openai/gpt-oss-120b) spend part of the budget on
# internal reasoning tokens before emitting any content, so the limit has to
# cover reasoning + the JSON body (StrategyOutput/BrandConstitution are large).
MAX_COMPLETION_TOKENS = 3000

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to .env locally, or to "
                "Streamlit Cloud's Secrets when deployed."
            )
        _client = Groq(api_key=api_key)
    return _client


def _raw_call(system_prompt: str, user_prompt: str) -> str:
    client = _get_client()
    params = {
        "model": MODEL_NAME,
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "reasoning_effort": "low",
    }

    try:
        response = client.chat.completions.create(**params)
    except TypeError as e:
        # Older groq SDK versions don't know reasoning_effort.
        if "reasoning_effort" not in str(e):
            raise
        params.pop("reasoning_effort")
        response = client.chat.completions.create(**params)

    choice = response.choices[0]
    content = choice.message.content
    if not content:
        raise RuntimeError(
            f"Groq returned empty content (finish_reason={choice.finish_reason!r}, "
            f"completion_tokens={getattr(getattr(response, 'usage', None), 'completion_tokens', 'unknown')}). "
            "The token budget was likely consumed by reasoning before any content "
            "was emitted."
        )
    return content


def call_llm(system_prompt: str, user_prompt: str, schema: Type[T]) -> T:
    """
    Calls the LLM, parses the response as JSON, and validates it against
    `schema`. Retries once (with a corrective instruction appended) if the
    first attempt produces invalid JSON or fails schema validation.

    Raises RuntimeError if both attempts fail — callers in services/*.py
    are expected to catch this and fall back to utils/demo_data.py.
    """
    last_error: str = ""

    for attempt in range(2):
        prompt = user_prompt
        if attempt == 1:
            prompt = (
                user_prompt
                + f"\n\nYour previous response was invalid ({last_error}). "
                  "Return ONLY valid JSON matching the required schema. "
                  "No markdown fences, no commentary, no extra text."
            )

        try:
            raw_text = _raw_call(system_prompt, prompt)
        except Exception as e:
            last_error = f"API call failed: {e}"
            continue

        data = safe_json_parse(raw_text)
        if data is None:
            last_error = "response was not valid JSON"
            continue

        try:
            return schema(**data)
        except ValidationError as e:
            last_error = f"schema validation failed: {e}"
            continue

    raise RuntimeError(f"call_llm failed after 2 attempts: {last_error}")
