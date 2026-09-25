"""
Tests for safe_json_parse() in utils/validation.py.

The contract: return a dict on success, return None (never raise) on failure,
after stripping markdown fences and stray prose around the JSON object.
"""
import sys

import pytest

from utils.validation import safe_json_parse

VALID_OBJECT = '{"problem": "career coaching", "assumptions": ["founder is ND"]}'


def test_parses_plain_json_string():
    assert safe_json_parse(VALID_OBJECT) == {
        "problem": "career coaching",
        "assumptions": ["founder is ND"],
    }


def test_parses_json_wrapped_in_json_fence():
    text = f"```json\n{VALID_OBJECT}\n```"

    assert safe_json_parse(text) == safe_json_parse(VALID_OBJECT)


def test_parses_json_wrapped_in_bare_fence():
    text = f"```\n{VALID_OBJECT}\n```"

    assert safe_json_parse(text) == safe_json_parse(VALID_OBJECT)


def test_parses_json_with_prose_before_and_after():
    text = (
        "Sure! Here is the JSON you asked for:\n"
        f"{VALID_OBJECT}\n"
        "Let me know if you want any changes."
    )

    assert safe_json_parse(text) == safe_json_parse(VALID_OBJECT)


def test_parses_json_with_prose_before_only():
    text = f"Here is the result:\n{VALID_OBJECT}"

    assert safe_json_parse(text) == safe_json_parse(VALID_OBJECT)


def test_parses_json_with_prose_after_only():
    text = f"{VALID_OBJECT}\nHope that helps!"

    assert safe_json_parse(text) == safe_json_parse(VALID_OBJECT)


def test_parses_json_with_fence_and_surrounding_prose():
    text = f"Certainly, here you go:\n```json\n{VALID_OBJECT}\n```\nAnything else?"

    assert safe_json_parse(text) == safe_json_parse(VALID_OBJECT)


def test_preserves_nested_structures_and_types():
    text = '{"directions": [{"name": "A", "genericness_score": 3}], "ok": true}'

    parsed = safe_json_parse(text)

    assert parsed["ok"] is True
    assert parsed["directions"][0]["genericness_score"] == 3


def test_keeps_braces_inside_string_values():
    text = '{"explanation": "use {braces} freely", "verdict": "PASS"}'

    parsed = safe_json_parse(text)

    assert parsed == {"explanation": "use {braces} freely", "verdict": "PASS"}


@pytest.mark.parametrize(
    "bad_text",
    [
        "I could not produce JSON for this request, sorry.",
        "Here is my answer: the brand should focus on agency.",
        "null",
        "undefined",
        "{'problem': 'single quotes are not valid json'}",
        '{"problem": "truncated"',
        "",
        "   \n\t  ",
        None,
    ],
)
def test_unparseable_text_returns_none_without_raising(bad_text):
    assert safe_json_parse(bad_text) is None


def test_exception_types_are_swallowed_for_text_spanning_braces():
    text = "Answer: {not json} and then more text."

    assert safe_json_parse(text) is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
