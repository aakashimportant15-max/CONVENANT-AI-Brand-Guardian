"""
Pydantic models for Covenant's 4-stage pipeline.
Keep these simple and flat — every LLM response is validated against these.
"""
from pydantic import BaseModel
from typing import Optional, Literal


class DiscoveryOutput(BaseModel):
    problem: str
    target_user: str
    served_population: str
    harm_risk_notes: str
    key_value: str
    constraints: str
    assumptions: list[str]


class BrandDirection(BaseModel):
    name: str
    positioning: str
    target_audience: str
    differentiator: str
    emotional_territory: str
    genericness_score: int
    harm_risk_score: int
    strengths: list[str]
    flaws: list[str]
    sharper_alternative: str


class StrategyOutput(BaseModel):
    directions: list[BrandDirection]


class NamingOption(BaseModel):
    name: str
    why: str


class BrandConstitution(BaseModel):
    traits: list[str]
    traits_to_avoid: list[str]
    naming_options: list[NamingOption]
    tagline: str
    audience_promise: str
    positioning_rule: str
    voice_do: list[str]
    voice_dont: list[str]
    banned_words: list[str]


class GuardianResult(BaseModel):
    verdict: Literal["PASS", "FAIL"]
    violated_rule: Optional[str] = None
    explanation: Optional[str] = None
    evidence_quote: Optional[str] = None
    rewrite: Optional[str] = None
    why_rewrite_fits: Optional[str] = None
    deterministic_flags: list[str] = []
