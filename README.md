# Covenant — AI Brand Constitution & Guardian

> **Turn a rough idea into a consistent brand — then keep every future message aligned with the rules that matter.**

Covenant is an AI-powered brand constitution and communication Guardian for organizations where **tone, dignity, identity, and respectful language matter**.

Instead of generating a brand once and leaving the team to maintain it manually, Covenant turns brand decisions into a **structured, enforceable communication system**. It guides an idea through discovery, strategic direction, constitution building, and ongoing content validation.

---

## ✨ What Covenant Does

Covenant takes a rough product, business, community, or organization idea and moves it through a four-stage AI workflow:

```text
Rough Idea
    ↓
01. Discovery
    ↓
02. Directions + Critique
    ↓
     USER LOCKS ONE DIRECTION
    ↓
03. Brand Constitution
    ↓
04. Guardian
    ↓
Mini Brand Kit
```

The important difference is that Covenant does **not** treat each AI call as an isolated generation task.

Every stage produces structured data that becomes context for the next stage. The selected strategic direction becomes the foundation of the Brand Constitution, and the Constitution becomes the rule set used by the Guardian.

---

# 🚀 Live Product

**Live Demo:**  
https://covenant-ai-brand-guardian.streamlit.app/

> If the custom URL is unavailable or changes, use the live Streamlit application URL provided by the deployment.

**Source Code:**  
https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian

---

# 🎯 The Problem

Founders, community builders, support organizations, and identity-led businesses often begin with a single rough idea.

The difficult part is not simply producing more marketing copy.

The difficult part is keeping communication:

- consistent
- specific
- aligned with the organization's identity
- respectful toward the people it serves
- understandable to new team members
- protected from generic AI language

Generic AI branding tools can easily fall back to phrases such as:

> "game-changing"

> "unlock your potential"

> "inspiring example"

In ordinary marketing, these phrases may simply feel generic.

For dignity-sensitive or identity-led organizations, however, language can also unintentionally introduce **deficit framing, stereotypes, or harmful assumptions**.

Covenant addresses this by turning strategic brand decisions into explicit communication rules that can be checked later.

---

# 💡 The Solution

Covenant creates a **Brand Constitution** from the user's selected strategic direction.

The Constitution captures things such as:

- brand traits
- traits to avoid
- naming directions
- tagline
- audience promise
- positioning rule
- voice guidelines
- do / don't rules
- banned phrases

The **Guardian** then checks future content against those rules.

Instead of returning only:

```text
This doesn't sound on-brand.
```

Covenant can return:

```text
FAIL

Violated Rule:
Avoid deficit framing.

Evidence:
"inspiring example"

Why:
The wording frames the person primarily through overcoming
a condition rather than their agency and work.

Suggested Rewrite:
...
```

The Guardian also performs a deterministic banned-phrase scan alongside the LLM judgment.

---

# 🧠 Why This Is More Than an AI Wrapper

Covenant's core value is the workflow and the state that moves through it.

### 1. Structured state between stages

Each stage produces structured JSON validated through Pydantic.

```text
DiscoveryOutput
      ↓
BrandDirection
      ↓
BrandConstitution
      ↓
GuardianResult
```

The next stage receives the previous stage's decisions as context.

---

### 2. AI critique before user selection

The strategy stage produces multiple directions and evaluates them using:

- genericness
- harm risk
- strengths
- flaws
- sharper alternatives

The user then chooses which direction to lock.

The system therefore supports a human decision instead of silently choosing a brand direction for the user.

---

### 3. Decisions become enforceable rules

The selected direction is not simply displayed and forgotten.

It becomes the foundation for the Brand Constitution.

The Constitution then becomes the Guardian's source of truth.

```text
Decision
   ↓
Constitution
   ↓
Rule
   ↓
Future Content Check
```

---

### 4. Hybrid AI + deterministic checking

The Guardian combines:

**LLM reasoning**

with

**deterministic Python checks**

The deterministic layer scans for configured banned phrases independently of the LLM.

This gives the system an additional predictable validation layer instead of relying entirely on model output.

---

# 🔄 Complete Product Workflow

## Step 1 — Idea

![Covenant Idea](https://raw.githubusercontent.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/main/scr/1.png)

The user starts with a rough idea.

Example:

> "A coaching business run by and for neurodivergent adults."

Covenant uses the idea as the starting point for the workflow.

The user can also load the built-in demo scenario without making an API call.

### Output

The idea is passed into the Discovery stage.

---

## Step 2 — Discovery

**Screenshot:** `scr/2.png`

The Discovery stage converts the rough idea into a structured problem and audience brief.

It identifies:

- problem
- target user
- served population
- harm-risk notes
- key value
- constraints
- assumptions

This creates a shared structured context for the strategic stage.

### AI Stage

```text
Rough Idea
    ↓
LLM Call #1
    ↓
DiscoveryOutput
```

---

## Step 3 — Directions + Critique

**Screenshots:**

- `scr/3.1.png`
- `scr/3.2.png`
- `scr/3.3.png`

Covenant generates **three distinct brand directions**.

Each direction contains:

- name
- positioning
- target audience
- differentiator
- emotional territory
- genericness score
- harm-risk score
- strengths
- flaws
- sharper alternative

The system critiques the generated directions before presenting them to the user.

### Human Decision Point

The user chooses one direction and locks it.

```text
3 AI-generated directions
          ↓
   Critique + scoring
          ↓
    Human selection
          ↓
    LOCKED DIRECTION
```

This is one of the most important interaction points in the product.

---

## Step 4 — Brand Constitution

**Screenshots:**

- `scr/4.png`
- `scr/4.2.png`

The locked direction becomes the input for Constitution generation.

The Constitution contains:

### Brand identity

- traits
- traits to avoid

### Positioning

- audience promise
- positioning rule

### Voice

- voice do
- voice don't

### Naming

- naming options
- tagline

### Safety / consistency

- banned words and phrases

### AI Stage

```text
Locked Brand Direction
        ↓
    LLM Call #3
        ↓
BrandConstitution
```

This Constitution becomes the rule set for the Guardian.

---

# 🛡️ Step 5 — Guardian

**Screenshots:**

- `scr/5.png`
- `scr/5.1.png`
- `scr/5.2.png`

The Guardian checks future content against the locked Brand Constitution.

The user can paste a piece of content and receive a structured validation result.

### PASS

If the content follows the Constitution:

```text
PASS
```

The system can show the supporting validation state.

### FAIL

If the content violates the Constitution, the Guardian provides:

- verdict
- violated rule
- explanation
- evidence quote
- suggested rewrite
- why the rewrite fits
- deterministic lexicon flags

---

# ⚡ Guardian Example

### Content being checked

> "Meet Sam — an inspiring example of someone who overcame ADHD and defeated his limitations through discipline."

The Guardian can identify language such as:

- `overcame`
- `inspiring example`
- `despite his`

and connect the result to the Constitution's communication rules.

Instead of only flagging the content, it proposes a rewrite that better centers the person's agency.

This is the central product demonstration:

```text
Brand Decision
      ↓
Brand Constitution
      ↓
Future Content
      ↓
Guardian
      ↓
Rule + Evidence + Explanation + Rewrite
```

---

# 🎨 Step 6 — Mini Brand Kit

**Screenshot:** `scr/6.png`

After the Constitution is generated, Covenant presents a compact Mini Brand Kit containing the key decisions created during the workflow.

The application also provides structured output that can be reviewed or downloaded.

---

# 🤖 AI Workflow

Covenant uses **four LLM calls** in the complete workflow.

```text
┌───────────────────────────────┐
│          ROUGH IDEA           │
└───────────────┬───────────────┘
                ↓
        ┌───────────────┐
        │ LLM CALL #1   │
        │  DISCOVERY    │
        └───────┬───────┘
                ↓
        DiscoveryOutput
                ↓
        ┌───────────────┐
        │ LLM CALL #2   │
        │  STRATEGIST   │
        │  + CRITIC     │
        └───────┬───────┘
                ↓
       3 Brand Directions
                ↓
          USER SELECTS
                ↓
        LOCKED DIRECTION
                ↓
        ┌───────────────┐
        │ LLM CALL #3   │
        │ CONSTITUTION  │
        └───────┬───────┘
                ↓
       Brand Constitution
                ↓
        ┌───────────────┐
        │ LLM CALL #4   │
        │   GUARDIAN    │
        └───────┬───────┘
                │
                ├───────────────┐
                ↓               ↓
         LLM Judgment    Deterministic
                         Phrase Scan
                │               │
                └───────┬───────┘
                        ↓
                 Guardian Result
                        ↓
                  Mini Brand Kit
```

---

# 🔍 Under the Hood

The application intentionally exposes the AI workflow instead of hiding everything behind a single "Generate Brand" button.

Each stage can show the structured context moving through the system.

This makes the architecture easier to inspect and demonstrates that the application is using a multi-stage workflow rather than performing one large prompt.

---

# 🏗️ Architecture

```text
                    Streamlit UI
                         │
                         ▼
                    app.py
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
          Services                Session
              │                    State
              │
      ┌───────┼────────┬───────────┐
      ▼       ▼        ▼           ▼
 Discovery Strategy Constitution Guardian
      │       │        │           │
      └───────┴────────┴───────────┘
                       │
                       ▼
                  services/llm.py
                       │
                       ▼
                    Groq API
                       │
                       ▼
                Structured JSON
                       │
                       ▼
                   Pydantic
```

Guardian validation additionally connects to:

```text
utils/deterministic_checks.py
```

for deterministic banned-phrase detection.

---

# 📁 Project Structure

```text
CONVENANT-AI-Brand-Guardian/
│
├── app.py
├── ui_theme.py
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md
│
├── .streamlit/
│   └── config.toml
│
├── models/
│   ├── __init__.py
│   └── schemas.py
│
├── prompts/
│   ├── constitution.txt
│   ├── discovery.txt
│   ├── guardian.txt
│   └── strategy.txt
│
├── services/
│   ├── __init__.py
│   ├── constitution.py
│   ├── discovery.py
│   ├── guardian.py
│   ├── llm.py
│   └── strategy.py
│
├── utils/
│   ├── __init__.py
│   ├── demo_data.py
│   ├── deterministic_checks.py
│   └── validation.py
│
├── tests/
│   ├── __init__.py
│   ├── test_constitution.py
│   ├── test_deterministic_checks.py
│   ├── test_discovery.py
│   ├── test_guardian.py
│   ├── test_llm.py
│   ├── test_schema.py
│   ├── test_strategy.py
│   └── test_validation.py
│
└── scr/
    ├── 1.png
    ├── 2.png
    ├── 3.1.png
    ├── 3.2.png
    ├── 3.3.png
    ├── 4.png
    ├── 4.2.png
    ├── 5.png
    ├── 5.1.png
    ├── 5.2.png
    └── 6.png
```

---

# 🖼️ Product Screenshots

## 01 — Idea

![Covenant Idea](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/1.png?raw=true)

---

## 02 — Discovery

![Covenant Discovery](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/2.png?raw=true)

---

## 03 — Brand Directions

### Direction overview

![Covenant Directions](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/3.1.png?raw=true)

### Direction details

![Covenant Direction Details](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/3.2.png?raw=true)

### Direction selection

![Covenant Direction Selection](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/3.3.png?raw=true)

---

## 04 — Brand Constitution

![Covenant Constitution](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/4.png?raw=true)

![Covenant Constitution Details](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/4.2.png?raw=true)

---

## 05 — Guardian

### Guardian overview

![Covenant Guardian](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/5.png?raw=true)

### Guardian validation

![Covenant Guardian Result](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/5.1.png?raw=true)

### Guardian evidence and rewrite

![Covenant Guardian Rewrite](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/5.2.png?raw=true)

---

## 06 — Mini Brand Kit

![Covenant Mini Brand Kit](https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian/blob/main/scr/6.png?raw=true)

---

# 🧰 Tech Stack

- **Python**
- **Streamlit**
- **Groq API**
- **Pydantic**
- **python-dotenv**
- **Pytest**
- Structured JSON workflows
- Session-state orchestration
- Deterministic Python validation

> The repository currently uses the Groq API for the LLM layer.

---

# 🔐 Environment Configuration

For local development, create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

A safe template is included as:

```text
.env.example
```

### Never commit your real `.env`

The API key must remain private.

For Streamlit Community Cloud, configure the key through:

**App settings → Secrets**

Use TOML:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

---

# 💻 Run Locally

## 1. Clone the repository

```bash
git clone https://github.com/aakashimportant15-max/CONVENANT-AI-Brand-Guardian.git
cd CONVENANT-AI-Brand-Guardian
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure the API key

Create `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## 5. Start Covenant

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 🧪 Testing

The project includes unit tests for the major application layers.

Run:

```bash
pytest
```

The test suite covers areas including:

- Pydantic schemas
- LLM service behavior
- Discovery
- Strategy
- Constitution
- Guardian
- Deterministic checks
- JSON validation

---

# 🧯 Reliability & Failure Handling

Covenant is designed to remain usable even when a live model call fails.

The LLM service includes:

- structured JSON parsing
- Pydantic validation
- retry behavior for invalid responses
- controlled error handling

The application also includes a complete demo dataset.

### Demo Mode

The **Use demo example** flow allows the complete product workflow to be demonstrated without making live API calls.

This is useful for:

- presentations
- judging
- development
- API outages
- rate limits
- reproducible demonstrations

---

# 📊 Structured Data Contracts

The application uses Pydantic schemas to keep the workflow structured.

Key objects include:

```text
DiscoveryOutput
BrandDirection
BrandConstitution
GuardianResult
```

This provides a defined contract between each stage instead of passing uncontrolled text throughout the application.

---

# 🛡️ Guardian Validation Model

The Guardian uses two complementary mechanisms.

### AI judgment

The LLM evaluates:

- constitution alignment
- tone
- communication rules
- contextual meaning
- potential violations

### Deterministic scan

Python checks configured phrases independently.

Conceptually:

```text
                   Content
                      │
             ┌────────┴────────┐
             ▼                 ▼
        LLM Guardian      Python Scanner
             │                 │
             └────────┬────────┘
                      ▼
               Guardian Result
```

This hybrid approach makes the Guardian more transparent than relying on a single model response.

---

# ⚠️ Current Limitations

This is an MVP and intentionally keeps the scope focused.

Current limitations include:

- Constitution is read-only after generation.
- Guardian checks one content input at a time.
- Genericness and harm-risk scores are model-generated assessments, not independently trained classifiers.
- The product does not currently include a database or authentication system.
- The visual brand stage is intentionally outside the current MVP scope.
- No multi-round agent debate is used.

---

# 🔮 Future Improvements

Potential extensions include:

- editable Constitution with re-validation
- Guardian history
- batch content checking
- team collaboration
- exportable brand kit
- visual identity direction
- additional deterministic policy checks
- organization-level rule libraries
- richer analytics around recurring communication violations

---

# 🏆 Hackathon Focus

Covenant was designed around a simple principle:

> **Don't just generate a brand. Turn the decisions behind the brand into rules that survive the next piece of content.**

The product focuses on six core ideas:

```text
Discover
   ↓
Position
   ↓
Choose
   ↓
Constitution
   ↓
Guard
   ↓
Deliver
```

The most important transition is:

```text
AI-generated decision
        ↓
Human-selected direction
        ↓
Structured constitution
        ↓
Enforceable communication rules
        ↓
Future content validation
```

---

# 👤 Contribution

**Role:** AI Product Developer / Full-Stack AI Builder

Key contributions:

- Designed the Covenant product concept and workflow.
- Designed the multi-stage AI architecture.
- Implemented structured Pydantic data contracts.
- Implemented the LLM service and validation flow.
- Built Discovery, Strategy, Constitution, and Guardian stages.
- Implemented deterministic phrase checking.
- Built the Streamlit interface and workflow state management.
- Added demo-mode and fallback behavior.
- Added automated tests for core services and validation.
- Deployed the working application through Streamlit Community Cloud.

---

# 📄 License

This project was created as a hackathon project and is provided for demonstration and evaluation purposes.
