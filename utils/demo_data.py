"""
Hand-written, schema-valid example data for the full pipeline.
Two jobs:
1. "Use demo example" button — lets the whole app run with zero API calls,
   for a guaranteed-reliable live demo.
2. Fallback — if a live LLM call fails validation twice, the matching stage
   here is used so the app never crashes mid-flow.

Scenario used throughout: a coaching business run by and for neurodivergent adults.
"""
from models.schemas import (
    DiscoveryOutput,
    BrandDirection,
    StrategyOutput,
    NamingOption,
    BrandConstitution,
    GuardianResult,
)

DEMO_RAW_IDEA = "A coaching business run by and for neurodivergent adults."

DEMO_DISCOVERY = DiscoveryOutput(
    problem="Neurodivergent adults often receive career and life coaching designed "
            "around neurotypical norms, which frames their differences as deficits "
            "to fix rather than as a different operating style to design around.",
    target_user="Neurodivergent adults (ADHD, autistic, and other neurodivergent "
                 "profiles) seeking career or life coaching.",
    served_population="Neurodivergent adults, including those who have previously "
                       "experienced coaching or workplace feedback framed around "
                       "their diagnosis as a limitation.",
    harm_risk_notes="Deficit framing (e.g. 'overcame ADHD') and inspiration-porn "
                     "language (e.g. 'inspiring example') are both actively harmful "
                     "here — they recenter the narrative on triumph-over-condition "
                     "rather than on the client's actual agency and working style.",
    key_value="Coaching that designs around how a neurodivergent brain actually "
               "works, instead of coaching the client to mask or 'overcome' it.",
    constraints="Small, founder-led business; needs to sound credible to both "
                 "neurodivergent clients and neurotypical referral partners "
                 "(therapists, HR contacts) without losing authenticity to either.",
    assumptions=[
        "The founder and/or coaches are themselves neurodivergent.",
        "Clients are self-referred or referred by therapists, not mandated by employers.",
    ],
)

DEMO_DIRECTIONS = [
    BrandDirection(
        name="The Overcomer Frame (weak baseline)",
        positioning="Coaching that helps you overcome ADHD and unlock your potential.",
        target_audience="Neurodivergent adults seeking motivation.",
        differentiator="Founder has personally 'beaten' their own ADHD.",
        emotional_territory="Triumph, inspiration, struggle-to-success",
        genericness_score=9,
        harm_risk_score=9,
        strengths=["Emotionally familiar to a general audience"],
        flaws=[
            "Frames ADHD as an obstacle to defeat, not a different operating style",
            "Uses exactly the deficit language the served population finds harmful",
            "Interchangeable with almost any self-improvement coaching brand",
        ],
        sharper_alternative="Replace 'overcome ADHD' with 'work with how your brain "
                             "actually operates' — shifts the frame from deficit to design.",
    ),
    BrandDirection(
        name="Built Around You",
        positioning="Coaching that designs your systems around your actual brain, "
                     "not a neurotypical template.",
        target_audience="Neurodivergent adults who've been told to 'just try harder' "
                         "by prior coaching or workplaces.",
        differentiator="Systems-design approach, not motivation-based approach; "
                        "coach's own neurodivergence as lived credibility, not a "
                        "redemption story.",
        emotional_territory="Competence, agency, relief from masking",
        genericness_score=3,
        harm_risk_score=2,
        strengths=[
            "Centers agency and design, not deficit or triumph",
            "Differentiates clearly from generic productivity coaching",
            "Credible to both neurodivergent clients and referring professionals",
        ],
        flaws=["'Built Around You' could be sharpened to name the brain-first approach more directly"],
        sharper_alternative="Consider 'Coaching that starts with your brain, not a template' "
                             "for the tagline to make the design-first angle sharper.",
    ),
    BrandDirection(
        name="The Translator",
        positioning="We translate between how your brain works and how the world "
                     "expects you to work — so you don't have to mask.",
        target_audience="Neurodivergent adults navigating neurotypical workplaces.",
        differentiator="Frames the coach as a translator/bridge, not a fixer.",
        emotional_territory="Relief, clarity, reduced masking burden",
        genericness_score=4,
        harm_risk_score=3,
        strengths=["Strong, specific metaphor", "Names masking directly, which resonates"],
        flaws=["'Translator' framing could unintentionally imply the client's way is the 'foreign' one"],
        sharper_alternative="Reframe as translating the workplace's expectations to the "
                             "client, not the client's brain to the workplace.",
    ),
]

DEMO_STRATEGY = StrategyOutput(directions=DEMO_DIRECTIONS)

DEMO_LOCKED_DIRECTION = DEMO_DIRECTIONS[1]  # "Built Around You"

DEMO_CONSTITUTION = BrandConstitution(
    traits=["Direct", "Systems-minded", "Warm without being saccharine", "Credible", "Unapologetic"],
    traits_to_avoid=["Inspirational", "Clinical/cold", "Apologetic about neurodivergence"],
    naming_options=[
        NamingOption(name="Built Around You Coaching", why="States the core mechanism plainly."),
        NamingOption(name="Framewell", why="Signals 'working well within your own frame,' short and brandable."),
        NamingOption(name="Otherwise Coaching", why="Signals a different-by-design approach without clinical language."),
    ],
    tagline="Coaching that starts with your brain, not a template.",
    audience_promise="We will never ask you to overcome who you are — we'll help you "
                      "build systems around how you actually work.",
    positioning_rule="Every piece of content must center the client's agency and "
                      "design choices, never their diagnosis as an obstacle.",
    voice_do=[
        "Center the client's agency in every sentence about them",
        "Describe neurodivergence as a different operating style, not a limitation",
        "Use concrete, systems-based language over motivational language",
    ],
    voice_dont=[
        "Never frame neurodivergence as something to overcome or beat",
        "Never use inspiration-porn framing (e.g. 'inspiring example', 'against all odds')",
        "Never imply the client should mask or 'try harder' to fit neurotypical norms",
    ],
    banned_words=[
        "overcame", "overcoming ADHD", "despite their ADHD", "inspiring example",
        "unlock your potential", "game-changing", "suffers from",
    ],
)

DEMO_GUARDIAN_FAIL = GuardianResult(
    verdict="FAIL",
    violated_rule="voice_dont: Never frame neurodivergence as something to overcome or beat",
    explanation="This phrasing frames ADHD as an obstacle the client had to defeat, "
                "rather than describing how they built systems around how their brain works.",
    evidence_quote="overcame ADHD",
    rewrite="Meet Sam, who built a business by designing his workflow around how his "
            "brain actually works.",
    why_rewrite_fits="It centers Sam's agency and design choices instead of framing "
                      "ADHD as a deficit that was defeated.",
    deterministic_flags=["overcame", "inspiring example"],
)

DEMO_GUARDIAN_PASS = GuardianResult(
    verdict="PASS",
    deterministic_flags=[],
)

DEMO_BAD_CONTENT = ("Meet Sam — an inspiring example of someone who overcame ADHD "
                     "to build a business!")
DEMO_GOOD_CONTENT = ("Meet Sam, who built a business by designing his workflow "
                      "around how his brain actually works.")
