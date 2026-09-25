"""
Tests for run_constitution() in services/constitution.py.

Verifies both the locked BrandDirection and the DiscoveryOutput are serialized
into the prompt, with call_llm mocked.
"""
import sys
from unittest.mock import patch

import pytest

from models.schemas import BrandConstitution, BrandDirection, DiscoveryOutput
from services import constitution
from services.constitution import run_constitution
from utils.demo_data import (
    DEMO_CONSTITUTION,
    DEMO_DIRECTIONS,
    DEMO_DISCOVERY,
    DEMO_LOCKED_DIRECTION,
)


def test_run_constitution_returns_the_validated_llm_output():
    with patch.object(
        constitution, "call_llm", return_value=DEMO_CONSTITUTION
    ) as mock_call:
        result = run_constitution(DEMO_LOCKED_DIRECTION, DEMO_DISCOVERY)

    assert result is DEMO_CONSTITUTION
    assert isinstance(result, BrandConstitution)
    mock_call.assert_called_once()


def test_run_constitution_passes_system_prompt_and_schema():
    with patch.object(
        constitution, "call_llm", return_value=DEMO_CONSTITUTION
    ) as mock_call:
        run_constitution(DEMO_LOCKED_DIRECTION, DEMO_DISCOVERY)

    system_prompt, user_prompt, schema = mock_call.call_args.args
    assert system_prompt == constitution._SYSTEM_PROMPT
    assert schema is BrandConstitution
    assert isinstance(user_prompt, str) and user_prompt


def test_locked_direction_and_discovery_are_both_serialized_into_the_prompt():
    expected_direction_json = DEMO_LOCKED_DIRECTION.model_dump_json(indent=2)
    expected_discovery_json = DEMO_DISCOVERY.model_dump_json(indent=2)

    with patch.object(
        constitution, "call_llm", return_value=DEMO_CONSTITUTION
    ) as mock_call:
        run_constitution(DEMO_LOCKED_DIRECTION, DEMO_DISCOVERY)

    user_prompt = mock_call.call_args.args[1]
    assert expected_direction_json in user_prompt
    assert expected_discovery_json in user_prompt
    assert user_prompt == constitution._PROMPT_TEMPLATE.format(
        locked_direction_json=expected_direction_json,
        discovery_json=expected_discovery_json,
    )


def test_placeholders_are_replaced_not_left_literal():
    with patch.object(
        constitution, "call_llm", return_value=DEMO_CONSTITUTION
    ) as mock_call:
        run_constitution(DEMO_LOCKED_DIRECTION, DEMO_DISCOVERY)

    user_prompt = mock_call.call_args.args[1]
    assert "{locked_direction_json}" not in user_prompt
    assert "{discovery_json}" not in user_prompt


def test_locked_direction_field_values_reach_the_prompt():
    with patch.object(
        constitution, "call_llm", return_value=DEMO_CONSTITUTION
    ) as mock_call:
        run_constitution(DEMO_LOCKED_DIRECTION, DEMO_DISCOVERY)

    user_prompt = mock_call.call_args.args[1]
    assert DEMO_LOCKED_DIRECTION.name in user_prompt
    assert DEMO_LOCKED_DIRECTION.positioning in user_prompt


def test_a_different_locked_direction_changes_the_prompt():
    other_direction = DEMO_DIRECTIONS[2]

    with patch.object(
        constitution, "call_llm", return_value=DEMO_CONSTITUTION
    ) as mock_call:
        run_constitution(other_direction, DEMO_DISCOVERY)

    user_prompt = mock_call.call_args.args[1]
    assert other_direction.model_dump_json(indent=2) in user_prompt
    assert other_direction.model_dump_json(indent=2) != DEMO_LOCKED_DIRECTION.model_dump_json(
        indent=2
    )


def test_argument_order_is_locked_direction_then_discovery():
    direction = DEMO_DIRECTIONS[0]
    other_discovery = DEMO_DISCOVERY.model_copy(
        update={"key_value": "Distinct value used to prove argument order."}
    )

    with patch.object(
        constitution, "call_llm", return_value=DEMO_CONSTITUTION
    ) as mock_call:
        run_constitution(direction, other_discovery)

    user_prompt = mock_call.call_args.args[1]
    assert direction.model_dump_json(indent=2) in user_prompt
    assert "Distinct value used to prove argument order." in user_prompt
    assert other_discovery.model_dump_json(indent=2) in user_prompt


def test_prompt_template_still_contains_both_placeholders():
    assert "{locked_direction_json}" in constitution._PROMPT_TEMPLATE
    assert "{discovery_json}" in constitution._PROMPT_TEMPLATE


def test_llm_failure_propagates_runtime_error():
    with patch.object(
        constitution, "call_llm", side_effect=RuntimeError("call_llm failed")
    ) as mock_call:
        with pytest.raises(RuntimeError):
            run_constitution(DEMO_LOCKED_DIRECTION, DEMO_DISCOVERY)

    mock_call.assert_called_once()


def test_accepts_any_valid_models():
    direction = BrandDirection(
        name="Minimal",
        positioning="p",
        target_audience="t",
        differentiator="d",
        emotional_territory="e",
        genericness_score=1,
        harm_risk_score=1,
        strengths=["s"],
        flaws=["f"],
        sharper_alternative="a",
    )
    discovery = DiscoveryOutput(
        problem="p",
        target_user="t",
        served_population="s",
        harm_risk_notes="h",
        key_value="k",
        constraints="c",
        assumptions=["a"],
    )

    with patch.object(
        constitution, "call_llm", return_value=DEMO_CONSTITUTION
    ) as mock_call:
        result = run_constitution(direction, discovery)

    assert result is DEMO_CONSTITUTION
    assert '"name": "Minimal"' in mock_call.call_args.args[1]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
