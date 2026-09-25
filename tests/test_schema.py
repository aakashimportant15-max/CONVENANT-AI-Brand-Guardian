"""
Tests for every Pydantic model in models/schemas.py.

Valid instances come from utils/demo_data.py, which is already schema-valid,
so these tests stay in sync with the real pipeline data.
"""
import sys

import pytest
from pydantic import ValidationError

from models.schemas import (
    BrandConstitution,
    BrandDirection,
    DiscoveryOutput,
    GuardianResult,
    NamingOption,
    StrategyOutput,
)
from utils.demo_data import (
    DEMO_CONSTITUTION,
    DEMO_DISCOVERY,
    DEMO_GUARDIAN_FAIL,
    DEMO_GUARDIAN_PASS,
    DEMO_LOCKED_DIRECTION,
    DEMO_STRATEGY,
)

# (model name, valid demo instance, one required field to remove)
MODELS_AND_REQUIRED_FIELDS = [
    ("DiscoveryOutput", DEMO_DISCOVERY, "problem"),
    ("BrandDirection", DEMO_LOCKED_DIRECTION, "name"),
    ("StrategyOutput", DEMO_STRATEGY, "directions"),
    ("NamingOption", DEMO_CONSTITUTION.naming_options[0], "why"),
    ("BrandConstitution", DEMO_CONSTITUTION, "tagline"),
    ("GuardianResult", DEMO_GUARDIAN_FAIL, "verdict"),
]
MODEL_IDS = [case[0] for case in MODELS_AND_REQUIRED_FIELDS]


@pytest.mark.parametrize(
    "model_name, instance, required_field", MODELS_AND_REQUIRED_FIELDS, ids=MODEL_IDS
)
def test_valid_data_constructs_successfully(model_name, instance, required_field):
    model = type(instance)
    assert model.__name__ == model_name

    rebuilt = model(**instance.model_dump())

    assert isinstance(rebuilt, model)
    assert rebuilt.model_dump() == instance.model_dump()


@pytest.mark.parametrize(
    "model_name, instance, required_field", MODELS_AND_REQUIRED_FIELDS, ids=MODEL_IDS
)
def test_missing_required_field_raises_validation_error(
    model_name, instance, required_field
):
    model = type(instance)
    payload = instance.model_dump()
    assert required_field in payload

    del payload[required_field]

    with pytest.raises(ValidationError) as exc_info:
        model(**payload)
    assert required_field in str(exc_info.value)


def test_nested_models_round_trip():
    strategy = StrategyOutput(**DEMO_STRATEGY.model_dump())

    assert len(strategy.directions) == 3
    assert all(isinstance(d, BrandDirection) for d in strategy.directions)
    assert strategy.directions[1].name == DEMO_LOCKED_DIRECTION.name


def test_nested_model_rejects_wrong_item_shape():
    payload = DEMO_STRATEGY.model_dump()
    del payload["directions"][0]["sharper_alternative"]

    with pytest.raises(ValidationError):
        StrategyOutput(**payload)


def test_brand_constitution_parses_naming_options_from_dicts():
    constitution = BrandConstitution(**DEMO_CONSTITUTION.model_dump())

    assert all(isinstance(o, NamingOption) for o in constitution.naming_options)
    assert constitution.banned_words == DEMO_CONSTITUTION.banned_words


def test_guardian_result_defaults():
    result = GuardianResult(verdict="PASS")

    assert result.deterministic_flags == []
    assert result.violated_rule is None
    assert result.explanation is None
    assert result.evidence_quote is None
    assert result.rewrite is None
    assert result.why_rewrite_fits is None


def test_guardian_result_accepts_fail_payload_with_optional_fields():
    result = GuardianResult(**DEMO_GUARDIAN_FAIL.model_dump())

    assert result.verdict == "FAIL"
    assert result.deterministic_flags == DEMO_GUARDIAN_FAIL.deterministic_flags


@pytest.mark.parametrize("bad_verdict", ["MAYBE", "pass", "TRUE", ""])
def test_guardian_result_rejects_verdict_outside_literal(bad_verdict):
    with pytest.raises(ValidationError):
        GuardianResult(verdict=bad_verdict)


def test_demo_pass_and_fail_guardian_results_are_distinct():
    assert DEMO_GUARDIAN_PASS.verdict == "PASS"
    assert DEMO_GUARDIAN_PASS.deterministic_flags == []
    assert DEMO_GUARDIAN_FAIL.verdict == "FAIL"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
