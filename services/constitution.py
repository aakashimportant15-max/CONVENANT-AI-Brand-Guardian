from pathlib import Path

from models.schemas import DiscoveryOutput, BrandDirection, BrandConstitution
from services.llm import call_llm

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "constitution.txt"
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text()

_SYSTEM_PROMPT = (
    "You are Covenant's Constitution agent. You convert a locked brand "
    "direction into enforceable, mechanically-checkable rules. You always "
    "respond with valid JSON only."
)


def run_constitution(
    locked_direction: BrandDirection, discovery: DiscoveryOutput
) -> BrandConstitution:
    user_prompt = _PROMPT_TEMPLATE.format(
        locked_direction_json=locked_direction.model_dump_json(indent=2),
        discovery_json=discovery.model_dump_json(indent=2),
    )
    return call_llm(_SYSTEM_PROMPT, user_prompt, BrandConstitution)
