from pathlib import Path

from models.schemas import DiscoveryOutput
from services.llm import call_llm

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "discovery.txt"
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text()

_SYSTEM_PROMPT = (
    "You are Covenant's Discovery agent. You extract a structured brand "
    "brief from a rough idea. You always respond with valid JSON only."
)


def run_discovery(raw_idea: str) -> DiscoveryOutput:
    user_prompt = _PROMPT_TEMPLATE.format(raw_idea=raw_idea)
    return call_llm(_SYSTEM_PROMPT, user_prompt, DiscoveryOutput)
