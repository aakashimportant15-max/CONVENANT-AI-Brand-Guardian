"""
Tests for call_llm() in services/llm.py.

The only function that touches the network is _raw_call(), so every test here
patches it — no test in this suite ever reaches the Groq API.
"""
import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from models.schemas import DiscoveryOutput
from services import llm
from services.llm import call_llm
from utils.demo_data import DEMO_DISCOVERY

SYSTEM_PROMPT = "You are Covenant's Discovery agent."
USER_PROMPT = "Extract a brand brief from this idea."
VALID_JSON = json.dumps(DEMO_DISCOVERY.model_dump())
INVALID_SCHEMA_JSON = json.dumps({"wrong_field": "wrong value", "another": 1})


def test_first_attempt_success_parses_and_validates():
    with patch.object(llm, "_raw_call", return_value=VALID_JSON) as raw_call:
        result = call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert isinstance(result, DiscoveryOutput)
    assert result.model_dump() == DEMO_DISCOVERY.model_dump()
    raw_call.assert_called_once_with(SYSTEM_PROMPT, USER_PROMPT)


def test_first_attempt_success_accepts_fenced_json_without_retrying():
    fenced = f"```json\n{VALID_JSON}\n```"

    with patch.object(llm, "_raw_call", return_value=fenced) as raw_call:
        result = call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert result.problem == DEMO_DISCOVERY.problem
    assert raw_call.call_count == 1


def test_invalid_json_triggers_exactly_one_retry_and_succeeds():
    with patch.object(
        llm, "_raw_call", side_effect=["I'm sorry, here is prose not JSON.", VALID_JSON]
    ) as raw_call:
        result = call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert isinstance(result, DiscoveryOutput)
    assert result.key_value == DEMO_DISCOVERY.key_value
    assert raw_call.call_count == 2

    first_system, first_user = raw_call.call_args_list[0].args
    second_system, second_user = raw_call.call_args_list[1].args
    assert first_system == second_system == SYSTEM_PROMPT
    assert first_user == USER_PROMPT
    assert second_user.startswith(USER_PROMPT)
    assert "previous response was invalid" in second_user
    assert "not valid JSON" in second_user


def test_schema_validation_failure_triggers_retry_and_succeeds():
    with patch.object(
        llm, "_raw_call", side_effect=[INVALID_SCHEMA_JSON, VALID_JSON]
    ) as raw_call:
        result = call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert isinstance(result, DiscoveryOutput)
    assert raw_call.call_count == 2
    retry_user = raw_call.call_args_list[1].args[1]
    assert "schema validation failed" in retry_user
    assert "Return ONLY valid JSON" in retry_user


def test_both_attempts_invalid_raises_runtime_error_after_two_calls():
    with patch.object(
        llm, "_raw_call", side_effect=["not json", "still not json"]
    ) as raw_call:
        with pytest.raises(RuntimeError, match="call_llm failed after 2 attempts"):
            call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert raw_call.call_count == 2


def test_both_attempts_failing_schema_validation_raises_runtime_error():
    with patch.object(
        llm, "_raw_call", side_effect=[INVALID_SCHEMA_JSON, INVALID_SCHEMA_JSON]
    ) as raw_call:
        with pytest.raises(RuntimeError, match="schema validation failed"):
            call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert raw_call.call_count == 2


def test_api_exception_is_retried_then_raises_runtime_error():
    with patch.object(llm, "_raw_call", side_effect=RuntimeError("groq is down")) as raw_call:
        with pytest.raises(RuntimeError, match="call_llm failed after 2 attempts"):
            call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert raw_call.call_count == 2
    retry_user = raw_call.call_args_list[1].args[1]
    assert "API call failed" in retry_user
    assert "groq is down" in retry_user


def test_first_attempt_api_exception_second_attempt_succeeds():
    with patch.object(
        llm, "_raw_call", side_effect=[RuntimeError("transient"), VALID_JSON]
    ) as raw_call:
        result = call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert isinstance(result, DiscoveryOutput)
    assert raw_call.call_count == 2


def test_empty_response_triggers_retry():
    with patch.object(llm, "_raw_call", side_effect=["", VALID_JSON]) as raw_call:
        result = call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert isinstance(result, DiscoveryOutput)
    assert raw_call.call_count == 2


def test_no_retry_when_first_attempt_is_valid():
    with patch.object(llm, "_raw_call", return_value=VALID_JSON) as raw_call:
        call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert raw_call.call_count == 1


def test_retry_prompt_never_replaces_the_original_user_prompt():
    with patch.object(llm, "_raw_call", side_effect=["nope", "nope"]) as raw_call:
        with pytest.raises(RuntimeError):
            call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    for call in raw_call.call_args_list:
        assert call.args[1].startswith(USER_PROMPT)
        assert call.args[0] == SYSTEM_PROMPT


def test_get_client_raises_without_api_key_and_makes_no_call(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(llm, "_client", None)

    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        llm._get_client()


def test_get_client_is_lazy_and_reused(monkeypatch):
    sentinel = object()
    monkeypatch.setattr(llm, "_client", sentinel)

    assert llm._get_client() is sentinel


# ---------------------------------------------------------------------------
# _raw_call(): request parameters, empty-content handling, reasoning_effort
# fallback. The Groq client itself is faked, so no request leaves the process.
# ---------------------------------------------------------------------------


def _fake_response(content, finish_reason="stop", completion_tokens=42):
    response = MagicMock()
    response.choices[0].message.content = content
    response.choices[0].finish_reason = finish_reason
    response.usage.completion_tokens = completion_tokens
    return response


def _fake_client(*side_effects):
    client = MagicMock()
    client.chat.completions.create.side_effect = list(side_effects)
    return client


def test_raw_call_requests_completion_tokens_and_low_reasoning_effort():
    client = _fake_client(_fake_response("{}"))

    with patch.object(llm, "_get_client", return_value=client):
        result = llm._raw_call("sys", "user")

    assert result == "{}"
    client.chat.completions.create.assert_called_once_with(
        model=llm.MODEL_NAME,
        max_completion_tokens=llm.MAX_COMPLETION_TOKENS,
        messages=[
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "user"},
        ],
        reasoning_effort="low",
    )


def test_token_budget_is_large_enough_for_full_schema_outputs():
    assert llm.MAX_COMPLETION_TOKENS >= 3000


def test_raw_call_falls_back_when_sdk_rejects_reasoning_effort():
    type_error = TypeError(
        "Completions.create() got an unexpected keyword argument 'reasoning_effort'"
    )
    client = _fake_client(type_error, _fake_response(VALID_JSON))

    with patch.object(llm, "_get_client", return_value=client):
        result = llm._raw_call("sys", "user")

    assert result == VALID_JSON
    assert client.chat.completions.create.call_count == 2
    first = client.chat.completions.create.call_args_list[0].kwargs
    second = client.chat.completions.create.call_args_list[1].kwargs
    assert first["reasoning_effort"] == "low"
    assert "reasoning_effort" not in second
    assert first["max_completion_tokens"] == second["max_completion_tokens"] == 3000
    assert first["messages"] == second["messages"]


def test_raw_call_does_not_swallow_unrelated_type_errors():
    client = _fake_client(TypeError("messages must be a list of dicts"))

    with patch.object(llm, "_get_client", return_value=client):
        with pytest.raises(TypeError, match="messages must be a list"):
            llm._raw_call("sys", "user")

    assert client.chat.completions.create.call_count == 1


def test_raw_call_raises_on_empty_content_budget_eaten_by_reasoning():
    client = _fake_client(
        _fake_response("", finish_reason="length", completion_tokens=2000)
    )

    with patch.object(llm, "_get_client", return_value=client):
        with pytest.raises(RuntimeError, match="empty content") as exc_info:
            llm._raw_call("sys", "user")

    assert "length" in str(exc_info.value)
    assert "2000" in str(exc_info.value)


def test_raw_call_raises_on_none_content():
    client = _fake_client(_fake_response(None, finish_reason="length"))

    with patch.object(llm, "_get_client", return_value=client):
        with pytest.raises(RuntimeError, match="empty content"):
            llm._raw_call("sys", "user")


def test_call_llm_retries_after_empty_content_from_the_api():
    client = _fake_client(
        _fake_response("", finish_reason="length"),
        _fake_response(VALID_JSON),
    )

    with patch.object(llm, "_get_client", return_value=client):
        result = call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert isinstance(result, DiscoveryOutput)
    assert result.model_dump() == DEMO_DISCOVERY.model_dump()
    assert client.chat.completions.create.call_count == 2
    retry_prompt = client.chat.completions.create.call_args_list[1].kwargs["messages"][1][
        "content"
    ]
    assert "empty content" in retry_prompt


def test_call_llm_raises_when_content_stays_empty_on_both_attempts():
    client = _fake_client(
        _fake_response("", finish_reason="length"),
        _fake_response("", finish_reason="length"),
    )

    with patch.object(llm, "_get_client", return_value=client):
        with pytest.raises(RuntimeError, match="call_llm failed after 2 attempts"):
            call_llm(SYSTEM_PROMPT, USER_PROMPT, DiscoveryOutput)

    assert client.chat.completions.create.call_count == 2


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
