"""
Tests for check_banned_phrases() in utils/deterministic_checks.py.

This is the deterministic safety net behind the Guardian, so it is tested
against the real seed lexicon plus the demo Constitution's banned_words.
"""
import sys

import pytest

from utils.demo_data import DEMO_BAD_CONTENT, DEMO_CONSTITUTION, DEMO_GOOD_CONTENT
from utils.deterministic_checks import BANNED_LEXICON, check_banned_phrases

ALL_LEXICON_PHRASES = [
    phrase for phrases in BANNED_LEXICON.values() for phrase in phrases
]


def test_flags_sentence_containing_known_lexicon_phrase():
    flags = check_banned_phrases(DEMO_BAD_CONTENT)

    assert "inspiring example" in flags
    assert "overcame" in flags


def test_clean_sentence_returns_empty_list():
    assert check_banned_phrases(DEMO_GOOD_CONTENT) == []


def test_matching_is_case_insensitive():
    flags = check_banned_phrases("SHE IS AN INSPIRING EXAMPLE OF RESILIENCE.")

    assert flags == ["inspiring example"]


def test_mixed_case_extra_banned_is_matched():
    flags = check_banned_phrases(
        "A NINJA ROCKSTAR approach.", extra_banned=["Ninja Rockstar"]
    )

    assert flags == ["Ninja Rockstar"]


def test_extra_banned_is_merged_with_builtin_lexicon():
    text = "We offer a ninja rockstar service that is truly game-changing."

    flags = check_banned_phrases(text, extra_banned=["ninja rockstar"])

    assert "ninja rockstar" in flags
    assert "game-changing" in flags


def test_extra_banned_phrase_not_in_lexicon_is_only_found_via_extra_banned():
    text = "Our coaches are ninja rockstars."

    assert check_banned_phrases(text) == []
    assert check_banned_phrases(text, extra_banned=["ninja rockstar"]) == [
        "ninja rockstar"
    ]


def test_demo_constitution_banned_words_are_all_caught():
    extra = DEMO_CONSTITUTION.banned_words

    flags = check_banned_phrases(DEMO_BAD_CONTENT, extra_banned=extra)

    assert "overcame" in flags
    assert "inspiring example" in flags
    assert flags == check_banned_phrases(DEMO_BAD_CONTENT)
    assert not set(flags) - set(extra) - set(ALL_LEXICON_PHRASES)


def test_clean_sentence_with_extra_banned_returns_empty_list():
    assert check_banned_phrases(DEMO_GOOD_CONTENT, extra_banned=["ninja rockstar"]) == []


def test_duplicate_lexicon_and_extra_banned_phrase_reported_once():
    flags = check_banned_phrases("They overcame it.", extra_banned=["overcame"])

    assert flags == ["overcame"]


def test_repeated_occurrences_in_text_reported_once():
    flags = check_banned_phrases("overcame this, overcame that, overcame everything.")

    assert flags == ["overcame"]


def test_default_extra_banned_of_none_behaves_like_empty_list():
    assert check_banned_phrases(DEMO_BAD_CONTENT, extra_banned=None) == (
        check_banned_phrases(DEMO_BAD_CONTENT, extra_banned=[])
    )


@pytest.mark.parametrize("blank", ["", "   ", "\t\n"])
def test_blank_extra_banned_entries_are_ignored(blank):
    assert check_banned_phrases("Completely clean copy.", extra_banned=[blank]) == []


def test_whitespace_around_extra_banned_phrase_is_trimmed():
    flags = check_banned_phrases("A ninja rockstar approach.", extra_banned=["  ninja rockstar  "])

    assert flags == ["ninja rockstar"]


def test_matches_are_substring_based():
    assert "overcoming" in check_banned_phrases("She is overcoming ADHD every day.")


def test_phrase_split_across_words_is_not_matched():
    assert check_banned_phrases("They over came the obstacle.") == []


@pytest.mark.parametrize("phrase", ALL_LEXICON_PHRASES)
def test_every_lexicon_phrase_is_detected_in_a_sentence(phrase):
    flags = check_banned_phrases(f"Some context before {phrase} and after.")

    assert phrase in flags


def test_lexicon_has_no_empty_phrases():
    assert ALL_LEXICON_PHRASES
    assert all(phrase.strip() for phrase in ALL_LEXICON_PHRASES)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
