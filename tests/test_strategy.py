"""
Tests for run_strategy() in services/strategy.py.

Verifies the DiscoveryOutput is serialized to JSON and interpolated into the
prompt template, with call_llm mocked so no API call happens.
"""
import sys
from unittest.mock import patch

import pytest

from models.schemas import DiscoveryOutput, StrategyOutput
from services import strategy
from services.strategy import run_strategy
from utils.demo_data import DEMO_DISCOVERY, DEMO_STRATEGY


def test_run_strategy_returns_the_validated_llm_output():
    with patch.object(strategy, "call_llm", return_value=DEMO_STRATEGY) as mock_call:
        result = run_strategy(DEMO_DISCOVERY)

    assert result is DEMO_STRATEGY
    assert isinstance(result, StrategyOutput)
    assert len(result.directions) == 3
    mock_call.assert_called_once()


def test_run_strategy_passes_system_prompt_schema_and_prompt():
    with patch.object(strategy, "call_llm", return_value=DEMO_STRATEGY) as mock_call:
        run_strategy(DEMO_DISCOVERY)

    system_prompt, user_prompt, schema = mock_call.call_args.args
    assert system_prompt == strategy._SYSTEM_PROMPT
    assert schema is StrategyOutput
    assert isinstance(user_prompt, str) and user_prompt


def test_discovery_is_serialized_as_json_into_the_prompt():
    expected_json = DEMO_DISCOVERY.model_dump_json(indent=2)

    with patch.object(strategy, "call_llm", return_value=DEMO_STRATEGY) as mock_call:
        run_strategy(DEMO_DISCOVERY)

    user_prompt = mock_call.call_args.args[1]
    assert expected_json in user_prompt
    assert user_prompt == strategy._PROMPT_TEMPLATE.format(
        discovery_json=expected_json
    )


def test_discovery_json_placeholder_is_replaced_not_left_literal():
    with patch.object(strategy, "call_llm", return_value=DEMO_STRATEGY) as mock_call:
        run_strategy(DEMO_DISCOVERY)

    user_prompt = mock_call.call_args.args[1]
    assert "{discovery_json}" not in user_prompt
    assert user_prompt.count(DEMO_DISCOVERY.model_dump_json(indent=2)) == 1


def test_discovery_field_values_reach_the_prompt():
    with patch.object(strategy, "call_llm", return_value=DEMO_STRATEGY) as mock_call:
        run_strategy(DEMO_DISCOVERY)

    user_prompt = mock_call.call_args.args[1]
    assert DEMO_DISCOVERY.key_value in user_prompt
    assert DEMO_DISCOVERY.assumptions[0] in user_prompt


def test_modified_discovery_is_reflected_in_the_prompt():
    modified = DEMO_DISCOVERY.model_copy(
        update={"problem": "Uniquely-identifiable problem statement for this test."}
    )

    with patch.object(strategy, "call_llm", return_value=DEMO_STRATEGY) as mock_call:
        run_strategy(modified)

    user_prompt = mock_call.call_args.args[1]
    assert "Uniquely-identifiable problem statement for this test." in user_prompt
    assert modified.model_dump_json(indent=2) in user_prompt


def test_prompt_template_still_contains_the_placeholder():
    assert "{discovery_json}" in strategy._PROMPT_TEMPLATE


def test_llm_failure_propagates_runtime_error():
    with patch.object(
        strategy, "call_llm", side_effect=RuntimeError("call_llm failed")
    ) as mock_call:
        with pytest.raises(RuntimeError):
            run_strategy(DEMO_DISCOVERY)

    mock_call.assert_called_once()


def test_accepts_any_valid_discovery_instance():
    other = DiscoveryOutput(
        problem="p",
        target_user="t",
        served_population="s",
        harm_risk_notes="h",
        key_value="k",
        constraints="c",
        assumptions=["a"],
    )

    with patch.object(strategy, "call_llm", return_value=DEMO_STRATEGY) as mock_call:
        result = run_strategy(other)

    assert result is DEMO_STRATEGY
    assert '"problem": "p"' in mock_call.call_args.args[1]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
