"""
Deterministic (non-AI) checks. Fast, reliable, zero-hallucination.
This is the safety net that works even if the LLM call fails or is slow.
"""
import re

# Seed lexicon: well-documented harmful/generic phrase categories.
# The Constitution's own banned_words list (from Call 3) is merged with this
# at Guardian time, so checks stay specific to the locked brand as well as
# these general red flags.
BANNED_LEXICON: dict[str, list[str]] = {
    "deficit_framing": [
        "overcame", "overcoming", "despite their", "despite his", "despite her",
        "suffers from", "afflicted with", "victim of", "struggles with",
    ],
    "inspiration_porn": [
        "inspiring example", "so inspiring", "against all odds",
        "never let it stop", "proves anything is possible",
    ],
    "startup_hype": [
        "game-changing", "game changer", "disrupt", "disruptive",
        "revolutionary", "unlock your potential", "seamless solution",
        "leverage synergies", "next-level",
    ],
    "paternalism": [
        "we're here to help you", "we know what's best", "for your own good",
    ],
}


def check_banned_phrases(text: str, extra_banned: list[str] | None = None) -> list[str]:
    """
    Case-insensitive substring scan of `text` against the seed lexicon plus
    any `extra_banned` phrases pulled from the org's own locked Constitution.
    Returns a flat list of matched phrases (originals, not lowercased) found.
    """
    hits: list[str] = []
    lowered = text.lower()

    all_phrases = [p for phrases in BANNED_LEXICON.values() for p in phrases]
    if extra_banned:
        all_phrases += extra_banned

    seen = set()
    for phrase in all_phrases:
        p = phrase.strip()
        if not p:
            continue
        pl = p.lower()
        if pl in lowered and pl not in seen:
            hits.append(p)
            seen.add(pl)

    return hits
