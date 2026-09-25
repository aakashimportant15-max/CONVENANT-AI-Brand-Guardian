from pathlib import Path

from models.schemas import BrandConstitution, GuardianResult
from services.llm import call_llm
from utils.deterministic_checks import check_banned_phrases

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "guardian.txt"
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text()

_SYSTEM_PROMPT = (
    "You are Covenant's Guardian agent. You strictly check content against "
    "an already-locked brand constitution. You always respond with valid "
    "JSON only."
)


def run_guardian(constitution: BrandConstitution, user_content: str) -> GuardianResult:
    user_prompt = _PROMPT_TEMPLATE.format(
        constitution_json=constitution.model_dump_json(indent=2),
        user_content=user_content,
    )
    # GuardianResult.deterministic_flags defaults to [] since the LLM prompt
    # deliberately does not ask the model to fill that field in.
    result = call_llm(_SYSTEM_PROMPT, user_prompt, GuardianResult)

    # Deterministic layer: independent of the LLM's judgment, checked against
    # both the general lexicon and this org's own locked banned_words.
    flags = check_banned_phrases(user_content, extra_banned=constitution.banned_words)
    result.deterministic_flags = flags

    # If the LLM said PASS but the deterministic check caught something,
    # override to FAIL — the deterministic layer is the safety net and
    # should not be silently ignored.
    if result.verdict == "PASS" and flags:
        result.verdict = "FAIL"
        result.violated_rule = "banned_words (deterministic check)"
        result.explanation = (
            f"The deterministic scan flagged banned phrase(s): {', '.join(flags)}."
        )
        result.evidence_quote = flags[0]

    # The model sometimes fixes only the violation it cited first and leaves
    # another banned phrase inside its own rewrite. Same deterministic layer,
    # now applied to the rewrite: flag it rather than silently trusting it.
    if result.rewrite:
        rewrite_flags = check_banned_phrases(
            result.rewrite, extra_banned=constitution.banned_words
        )
        if rewrite_flags:
            result.why_rewrite_fits = (
                (result.why_rewrite_fits or "").rstrip()
                + f" NOTE: this rewrite still contains banned phrase(s): "
                  f"{', '.join(rewrite_flags)} — it needs a second pass."
            ).strip()

    return result
