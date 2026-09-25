from pathlib import Path

from models.schemas import DiscoveryOutput, StrategyOutput
from services.llm import call_llm

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "strategy.txt"
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text()

_SYSTEM_PROMPT = (
    "You are Covenant's Strategist and Critic agent. You generate 3 "
    "meaningfully different brand directions and critique each one "
    "yourself. You always respond with valid JSON only."
)


def run_strategy(discovery: DiscoveryOutput) -> StrategyOutput:
    user_prompt = _PROMPT_TEMPLATE.format(
        discovery_json=discovery.model_dump_json(indent=2)
    )
    return call_llm(_SYSTEM_PROMPT, user_prompt, StrategyOutput)
