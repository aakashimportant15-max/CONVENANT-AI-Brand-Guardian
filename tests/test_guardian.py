"""
Tests for run_guardian() in services/guardian.py.

Unlike the other stage tests, these exercise real logic: on top of the mocked
LLM verdict, run_guardian() always runs the deterministic banned-phrase scan —
on the user's content (overriding a PASS when it finds something) and on the
LLM's proposed rewrite (appending a "needs a second pass" note when the rewrite
itself still contains a banned phrase). The mocked GuardianResult is mutated in
place, so every test builds a fresh instance rather than reusing the
module-level demo objects.
"""
import sys
from unittest.mock import call

import pytest

from models.schemas import BrandConstitution, GuardianResult
from services import guardian
from services.guardian import run_guardian
from utils.demo_data import (
    DEMO_BAD_CONTENT,
    DEMO_CONSTITUTION,
    DEMO_GOOD_CONTENT,
)
from utils.deterministic_checks import BANNED_LEXICON, check_banned_phrases

LEXICON_PHRASES = [
    phrase for phrases in BANNED_LEXICON.values() for phrase in phrases
]

RULE_VIOLATED = (
    "voice_dont: Never imply the client should mask or 'try harder' to fit "
    "neurotypical norms"
)
CONTENT_THE_LEXICON_CANNOT_CATCH = (
    "Our clients just need to try harder to fit in, and the results follow."
)


# ---------------------------------------------------------------------------
# Override logic: LLM says PASS, deterministic layer catches a banned phrase
# ---------------------------------------------------------------------------


def test_llm_pass_is_overridden_to_fail_when_banned_phrase_is_present(mocker):
    llm_pass = GuardianResult(verdict="PASS")
    mock_call = mocker.patch.object(guardian, "call_llm", return_value=llm_pass)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert result is llm_pass
    assert result.verdict == "FAIL"
    assert result.violated_rule == "banned_words (deterministic check)"
    assert mock_call.call_count == 1


def test_override_populates_flags_from_lexicon_and_constitution(mocker):
    llm_pass = GuardianResult(verdict="PASS")
    mocker.patch.object(guardian, "call_llm", return_value=llm_pass)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert result.deterministic_flags == ["overcame", "inspiring example"]
    assert "overcame" in DEMO_CONSTITUTION.banned_words
    assert "inspiring example" in DEMO_CONSTITUTION.banned_words


def test_override_flags_are_real_matches_from_the_constitution_or_lexicon(mocker):
    llm_pass = GuardianResult(verdict="PASS")
    mocker.patch.object(guardian, "call_llm", return_value=llm_pass)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert result.deterministic_flags
    for flag in result.deterministic_flags:
        assert flag.lower() in DEMO_BAD_CONTENT.lower()
        assert flag in DEMO_CONSTITUTION.banned_words or flag in LEXICON_PHRASES


def test_override_sets_explanation_and_evidence_quote(mocker):
    llm_pass = GuardianResult(verdict="PASS")
    mocker.patch.object(guardian, "call_llm", return_value=llm_pass)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert result.explanation.startswith(
        "The deterministic scan flagged banned phrase(s):"
    )
    for flag in result.deterministic_flags:
        assert flag in result.explanation
    assert result.evidence_quote == result.deterministic_flags[0]


def test_override_fires_for_a_phrase_only_in_the_constitutions_banned_words(mocker):
    constitution = BrandConstitution(
        **{**DEMO_CONSTITUTION.model_dump(), "banned_words": ["ninja rockstar"]}
    )
    content = "Every ninja rockstar on our coaching team has lived experience."
    assert check_banned_phrases(content) == []

    llm_pass = GuardianResult(verdict="PASS")
    mocker.patch.object(guardian, "call_llm", return_value=llm_pass)

    result = run_guardian(constitution, content)

    assert result.verdict == "FAIL"
    assert result.deterministic_flags == ["ninja rockstar"]
    assert result.evidence_quote == "ninja rockstar"


def test_override_fires_when_llm_pass_carries_other_none_fields(mocker):
    llm_pass = GuardianResult(verdict="PASS", deterministic_flags=["invented by llm"])
    mocker.patch.object(guardian, "call_llm", return_value=llm_pass)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert result.verdict == "FAIL"
    assert "invented by llm" not in result.deterministic_flags


# ---------------------------------------------------------------------------
# Genuine PASS: nothing for the deterministic layer to catch
# ---------------------------------------------------------------------------


def test_genuine_pass_is_left_untouched(mocker):
    llm_pass = GuardianResult(verdict="PASS")
    mocker.patch.object(guardian, "call_llm", return_value=llm_pass)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_GOOD_CONTENT)

    assert result is llm_pass
    assert result.verdict == "PASS"
    assert result.deterministic_flags == []
    assert result.violated_rule is None
    assert result.explanation is None
    assert result.evidence_quote is None
    assert result.rewrite is None


def test_llm_pass_with_invented_flags_is_reset_by_the_deterministic_layer(mocker):
    llm_pass = GuardianResult(verdict="PASS", deterministic_flags=["invented by llm"])
    mocker.patch.object(guardian, "call_llm", return_value=llm_pass)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_GOOD_CONTENT)

    assert result.verdict == "PASS"
    assert result.deterministic_flags == []


# ---------------------------------------------------------------------------
# LLM FAIL: deterministic flags are recorded alongside the LLM's own verdict
# ---------------------------------------------------------------------------


def test_llm_fail_on_clean_content_keeps_llm_fields_and_empty_flags(mocker):
    llm_fail = GuardianResult(
        verdict="FAIL",
        violated_rule=RULE_VIOLATED,
        explanation="It implies the client must mask or try harder.",
        evidence_quote="try harder to fit in",
        rewrite="Our clients design ways of working that fit how they operate.",
        why_rewrite_fits="It centers the client's agency instead of masking.",
    )
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(DEMO_CONSTITUTION, CONTENT_THE_LEXICON_CANNOT_CATCH)

    assert result is llm_fail
    assert result.verdict == "FAIL"
    assert result.violated_rule == RULE_VIOLATED
    assert result.evidence_quote == "try harder to fit in"
    assert result.rewrite == llm_fail.rewrite
    assert result.deterministic_flags == []


def test_llm_fail_on_banned_content_keeps_llm_verdict_and_adds_flags(mocker):
    llm_fail = GuardianResult(
        verdict="FAIL",
        violated_rule=RULE_VIOLATED,
        explanation="Deficit framing.",
        evidence_quote="overcame ADHD",
    )
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert result.verdict == "FAIL"
    assert result.violated_rule == RULE_VIOLATED
    assert result.explanation == "Deficit framing."
    assert result.evidence_quote == "overcame ADHD"
    assert result.deterministic_flags == ["overcame", "inspiring example"]


def test_deterministic_flags_is_always_overwritten_by_the_python_check(mocker):
    llm_fail = GuardianResult(
        verdict="FAIL",
        deterministic_flags=["hallucinated", "hallucinated two"],
    )
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert result.deterministic_flags == ["overcame", "inspiring example"]


def test_llm_fail_with_empty_content_has_no_flags(mocker):
    llm_fail = GuardianResult(verdict="FAIL", violated_rule=RULE_VIOLATED)
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(DEMO_CONSTITUTION, "")

    assert result.verdict == "FAIL"
    assert result.deterministic_flags == []


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------


def test_prompt_carries_constitution_json_and_content(mocker):
    mock_call = mocker.patch.object(
        guardian, "call_llm", return_value=GuardianResult(verdict="PASS")
    )

    run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    system_prompt, user_prompt, schema = mock_call.call_args.args
    assert system_prompt == guardian._SYSTEM_PROMPT
    assert schema is GuardianResult
    assert user_prompt == guardian._PROMPT_TEMPLATE.format(
        constitution_json=DEMO_CONSTITUTION.model_dump_json(indent=2),
        user_content=DEMO_BAD_CONTENT,
    )
    assert DEMO_CONSTITUTION.model_dump_json(indent=2) in user_prompt
    assert DEMO_BAD_CONTENT in user_prompt
    assert "{constitution_json}" not in user_prompt
    assert "{user_content}" not in user_prompt


def test_prompt_content_reflects_the_actual_content_argument(mocker):
    mock_call = mocker.patch.object(
        guardian, "call_llm", return_value=GuardianResult(verdict="PASS")
    )

    run_guardian(DEMO_CONSTITUTION, DEMO_GOOD_CONTENT)

    user_prompt = mock_call.call_args.args[1]
    assert DEMO_GOOD_CONTENT in user_prompt
    assert DEMO_BAD_CONTENT not in user_prompt


def test_llm_is_called_exactly_once_per_invocation(mocker):
    mock_call = mocker.patch.object(
        guardian, "call_llm", return_value=GuardianResult(verdict="PASS")
    )

    run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert mock_call.call_args_list == [
        call(
            guardian._SYSTEM_PROMPT,
            guardian._PROMPT_TEMPLATE.format(
                constitution_json=DEMO_CONSTITUTION.model_dump_json(indent=2),
                user_content=DEMO_BAD_CONTENT,
            ),
            GuardianResult,
        )
    ]


def test_runtime_error_from_llm_propagates(mocker):
    mocker.patch.object(
        guardian, "call_llm", side_effect=RuntimeError("call_llm failed")
    )

    with pytest.raises(RuntimeError):
        run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)


# ---------------------------------------------------------------------------
# Rewrite re-check: the LLM's own rewrite is scanned for banned phrases too,
# since it can fix only the violation it cited first and leave another in place
# ---------------------------------------------------------------------------

REWRITE_STILL_DIRTY = (
    "Meet Sam — an inspiring example of a founder who designed a business "
    "around how his brain works!"
)


def test_rewrite_with_a_leftover_banned_phrase_is_flagged(mocker):
    llm_fail = GuardianResult(
        verdict="FAIL",
        violated_rule=RULE_VIOLATED,
        evidence_quote="overcame ADHD",
        rewrite=REWRITE_STILL_DIRTY,
        why_rewrite_fits="It removes the deficit framing.",
    )
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert "inspiring example" in result.why_rewrite_fits
    assert "second pass" in result.why_rewrite_fits


def test_rewrite_note_preserves_the_llms_original_justification(mocker):
    llm_fail = GuardianResult(
        verdict="FAIL",
        rewrite=REWRITE_STILL_DIRTY,
        why_rewrite_fits="It removes the deficit framing.",
    )
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert result.why_rewrite_fits.startswith("It removes the deficit framing.")
    assert result.why_rewrite_fits.endswith("it needs a second pass.")


def test_rewrite_note_names_every_leftover_phrase(mocker):
    llm_fail = GuardianResult(
        verdict="FAIL",
        rewrite="Sam overcame ADHD and is now a game-changing founder.",
        why_rewrite_fits="It fixes the framing.",
    )
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert "overcame" in result.why_rewrite_fits
    assert "game-changing" in result.why_rewrite_fits


def test_rewrite_note_is_added_when_why_rewrite_fits_is_none(mocker):
    llm_fail = GuardianResult(
        verdict="FAIL",
        rewrite=REWRITE_STILL_DIRTY,
        why_rewrite_fits=None,
    )
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert result.why_rewrite_fits.startswith("NOTE:")
    assert "inspiring example" in result.why_rewrite_fits


def test_clean_rewrite_leaves_why_rewrite_fits_untouched(mocker):
    llm_fail = GuardianResult(
        verdict="FAIL",
        violated_rule=RULE_VIOLATED,
        rewrite="Our clients design ways of working that fit how they operate.",
        why_rewrite_fits="It centers the client's agency instead of masking.",
    )
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(DEMO_CONSTITUTION, CONTENT_THE_LEXICON_CANNOT_CATCH)

    assert result.why_rewrite_fits == "It centers the client's agency instead of masking."
    assert "second pass" not in result.why_rewrite_fits


def test_rewrite_scan_also_uses_the_constitutions_own_banned_words(mocker):
    constitution = BrandConstitution(
        **{**DEMO_CONSTITUTION.model_dump(), "banned_words": ["ninja rockstar"]}
    )
    rewrite = "Every ninja rockstar on our coaching team brings lived experience."
    assert check_banned_phrases(rewrite) == []

    llm_fail = GuardianResult(
        verdict="FAIL",
        rewrite=rewrite,
        why_rewrite_fits="It keeps the team's credibility.",
    )
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(constitution, CONTENT_THE_LEXICON_CANNOT_CATCH)

    assert "ninja rockstar" in result.why_rewrite_fits
    assert "second pass" in result.why_rewrite_fits


def test_pass_verdict_without_a_rewrite_never_gets_a_note(mocker):
    llm_pass = GuardianResult(verdict="PASS")
    mocker.patch.object(guardian, "call_llm", return_value=llm_pass)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_GOOD_CONTENT)

    assert result.why_rewrite_fits is None


def test_rewrite_scan_does_not_alter_the_verdict_it_already_recorded(mocker):
    llm_fail = GuardianResult(
        verdict="FAIL",
        violated_rule=RULE_VIOLATED,
        evidence_quote="overcame ADHD",
        rewrite=REWRITE_STILL_DIRTY,
        why_rewrite_fits="It removes the deficit framing.",
    )
    mocker.patch.object(guardian, "call_llm", return_value=llm_fail)

    result = run_guardian(DEMO_CONSTITUTION, DEMO_BAD_CONTENT)

    assert result.verdict == "FAIL"
    assert result.violated_rule == RULE_VIOLATED
    assert result.evidence_quote == "overcame ADHD"
    assert result.rewrite == REWRITE_STILL_DIRTY
    assert result.deterministic_flags == ["overcame", "inspiring example"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
