"""
Tests for run_discovery() in services/discovery.py.

call_llm is mocked at the services.discovery boundary, so the prompt the stage
builds is asserted directly and nothing touches the network.
"""
import sys
from unittest.mock import patch

import pytest

from models.schemas import DiscoveryOutput
from services import discovery
from services.discovery import run_discovery
from utils.demo_data import DEMO_DISCOVERY, DEMO_RAW_IDEA

CUSTOM_IDEA = "A tool that maps wheelchair-accessible routes for tourists in Tbilisi."


def test_run_discovery_returns_the_validated_llm_output():
    with patch.object(discovery, "call_llm", return_value=DEMO_DISCOVERY) as mock_call:
        result = run_discovery(CUSTOM_IDEA)

    assert result is DEMO_DISCOVERY
    assert isinstance(result, DiscoveryOutput)
    mock_call.assert_called_once()


def test_run_discovery_passes_system_prompt_schema_and_interpolated_idea():
    with patch.object(discovery, "call_llm", return_value=DEMO_DISCOVERY) as mock_call:
        run_discovery(CUSTOM_IDEA)

    assert mock_call.call_count == 1
    system_prompt, user_prompt, schema = mock_call.call_args.args
    assert system_prompt == discovery._SYSTEM_PROMPT
    assert schema is DiscoveryOutput
    assert CUSTOM_IDEA in user_prompt


def test_raw_idea_replaces_the_placeholder_exactly():
    with patch.object(discovery, "call_llm", return_value=DEMO_DISCOVERY) as mock_call:
        run_discovery(CUSTOM_IDEA)

    user_prompt = mock_call.call_args.args[1]
    assert "{raw_idea}" not in user_prompt
    assert user_prompt == discovery._PROMPT_TEMPLATE.format(raw_idea=CUSTOM_IDEA)
    assert user_prompt.count(CUSTOM_IDEA) == 1


def test_demo_idea_is_interpolated_too():
    with patch.object(discovery, "call_llm", return_value=DEMO_DISCOVERY) as mock_call:
        run_discovery(DEMO_RAW_IDEA)

    user_prompt = mock_call.call_args.args[1]
    assert DEMO_RAW_IDEA in user_prompt
    assert user_prompt == discovery._PROMPT_TEMPLATE.format(raw_idea=DEMO_RAW_IDEA)


def test_multiline_idea_is_interpolated_verbatim():
    idea = "A coaching service.\nSecond line with details.\nThird line."

    with patch.object(discovery, "call_llm", return_value=DEMO_DISCOVERY) as mock_call:
        run_discovery(idea)

    user_prompt = mock_call.call_args.args[1]
    assert idea in user_prompt


def test_llm_failure_propagates_runtime_error():
    with patch.object(
        discovery, "call_llm", side_effect=RuntimeError("call_llm failed")
    ) as mock_call:
        with pytest.raises(RuntimeError):
            run_discovery(CUSTOM_IDEA)

    mock_call.assert_called_once()


def test_prompt_template_still_contains_the_idea_placeholder():
    assert "{raw_idea}" in discovery._PROMPT_TEMPLATE


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
