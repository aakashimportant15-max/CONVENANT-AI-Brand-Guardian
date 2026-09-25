# Covenant

An AI brand constitution and Guardian that turns brand decisions into
enforceable communication rules — especially for organizations where tone,
dignity, or identity matter.

## The Problem

Founders and communicators for support groups, identity-led businesses, and
dignity-sensitive causes often start with one rough sentence. Generic AI
branding tools default to hype language ("game-changing," "unlock your
potential," "inspiring example") that isn't just weak in this context — it
can be actively harmful to the people the brand serves. Volunteers and staff
also turn over constantly, so even a good brand decision made once doesn't
stay consistent without something enforcing it later.

## The Solution

Covenant doesn't just generate a brand once. It runs the idea through a
4-stage AI pipeline that ends in a **locked, structured Brand Constitution**
— and then a **Guardian** checks any future content against that
constitution, citing the exact rule violated and proposing an on-brand
rewrite.

## Why This Is Different (not a wrapper)

- Every stage produces structured JSON, validated with Pydantic, that
  becomes the *input* to the next stage — nothing restarts from scratch.
- The Strategist critiques its own output (genericness + harm-risk scoring)
  before the user ever sees it.
- The user makes one meaningful decision: locking a direction. That
  decision becomes an enforceable rule set, not just a saved preference.
- The Guardian combines an LLM judgment with a deterministic banned-phrase
  scan, and cites the specific rule broken — not just "this sounds off."

## AI Workflow

```
Rough Idea
   |
   v
[LLM Call 1] Discovery -> DiscoveryOutput
   |
   v
[LLM Call 2] Strategist + Critic -> 3x BrandDirection (self-scored)
   |
   v
USER LOCKS ONE DIRECTION
   |
   v
[LLM Call 3] Constitution -> BrandConstitution
   |
   v
[LLM Call 4 + deterministic check] Guardian -> GuardianResult
   |
   v
Mini Brand Kit
```

Only 4 LLM calls total. Each stage's structured output is passed forward
as context to the next stage's prompt — visible in the "Under the Hood"
expander on every screen.

## Architecture

- `models/schemas.py` — Pydantic models for every stage's output
- `services/` — one function per stage (`run_discovery`, `run_strategy`,
  `run_constitution`, `run_guardian`), each calling `services/llm.py`
- `services/llm.py` — single point of contact with the LLM API; handles
  JSON parsing, schema validation, and one retry on failure
- `utils/deterministic_checks.py` — a banned-phrase lexicon checked with
  plain Python string matching, independent of the LLM
- `utils/demo_data.py` — a complete, hand-written example run used for the
  "Use demo example" button and as an automatic fallback if a live call fails
- `prompts/` — the four production prompts, one per stage
- `app.py` — the Streamlit UI and session-state orchestration

## Tech Stack

Python, Streamlit, Anthropic API (Claude), Pydantic, python-dotenv.
No database, no authentication, no RAG, no vector store, no agent framework.

## Project Structure

```
covenant/
├── app.py
├── requirements.txt
├── .env.example
├── models/schemas.py
├── services/{llm,discovery,strategy,constitution,guardian}.py
├── utils/{validation,deterministic_checks,demo_data}.py
└── prompts/{discovery,strategy,constitution,guardian}.txt
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate      # .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env           # then fill in your API key
```

## Environment Variables

- `ANTHROPIC_API_KEY` — required for live LLM calls. The app runs fully
  offline via the "Use demo example" button even without this set.

## Running Locally

```bash
streamlit run app.py
```

## Demo Mode

Click **"Use demo example"** in the sidebar (or on the input screen) at any
time. This loads a complete, valid run of all 4 stages for a real scenario
— a coaching business run by and for neurodivergent adults — with zero API
calls. This is also the automatic fallback if a live call fails twice.

## Deployment

Deployed on Streamlit Community Cloud. Set `ANTHROPIC_API_KEY` under
**App settings -> Secrets** as:

```toml
ANTHROPIC_API_KEY = "your_key_here"
```

## Example Walkthrough

Input: *"A coaching business run by and for neurodivergent adults."*

Guardian test: paste *"Meet Sam — an inspiring example of someone who
overcame ADHD to build a business!"* — Guardian returns **FAIL**, citing the
constitution's rule against deficit framing, quoting the offending phrase,
and rewriting it to center Sam's agency instead.

## Limitations

- Constitution is read-only once generated in this MVP (no in-app editing).
- Single-turn LLM judgment per stage — no multi-round debate.
- Genericness/harm-risk scores are the model's own self-assessment, not an
  independently trained classifier.

## Future Improvements

- Editable constitution with re-validation
- Guardian check history / batch-checking multiple pieces of content
- Exportable PDF brand kit
- Visual direction stage (typography, color, mood)
