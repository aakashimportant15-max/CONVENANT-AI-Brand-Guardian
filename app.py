"""
Covenant — an AI brand constitution and Guardian that turns brand decisions
into enforceable communication rules, especially for organizations where
tone, dignity, or identity matter.

5-screen flow: Idea -> Discovery -> Directions+Critique -> Constitution -> Guardian

All visual design lives in ui_theme.py; this file is flow and data.
"""
import json

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from models.schemas import DiscoveryOutput, BrandDirection, BrandConstitution
from services.discovery import run_discovery
from services.strategy import run_strategy
from services.constitution import run_constitution
from services.guardian import run_guardian
from utils import demo_data as demo
import ui_theme as ui

st.set_page_config(page_title="Covenant", page_icon="\U0001F4DC", layout="wide")

# Layer 2 of the theme; layer 1 is .streamlit/config.toml. st.context.theme.type
# is documented to lag one rerun behind a manual theme switch and then correct
# itself, which is fine here because every color is a CSS variable.
ui.inject_global_css(st.context.theme.type == "dark")

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
DEFAULTS = {
    "stage": "input",
    "raw_idea": None,
    "discovery": None,
    "strategy": None,
    "direction_choice": None,
    "locked_direction": None,
    "constitution": None,
    "guardian_result": None,
    "guardian_content": None,
    "guardian_autocheck": False,
    "error": None,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_all():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


def load_demo_example():
    st.session_state.raw_idea = demo.DEMO_RAW_IDEA
    st.session_state.discovery = demo.DEMO_DISCOVERY
    st.session_state.strategy = demo.DEMO_STRATEGY
    st.session_state.direction_choice = demo.DEMO_LOCKED_DIRECTION.name
    st.session_state.locked_direction = demo.DEMO_LOCKED_DIRECTION
    st.session_state.constitution = demo.DEMO_CONSTITUTION
    st.session_state.guardian_result = None
    st.session_state.guardian_content = None
    st.session_state.stage = "guardian"


def use_demo_violation():
    """on_click callback: runs before the rerun, so the textarea below is
    rendered already holding the demo text when the check fires."""
    st.session_state.guardian_content = demo.DEMO_BAD_CONTENT
    st.session_state.guardian_autocheck = True


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    ui.markdown(ui.sidebar_brand_html())
    ui.markdown(ui.sidebar_steps_html(st.session_state.stage))
    ui.markdown(ui.sidebar_divider_html())
    if st.button("Use demo example", type="primary", width="stretch",
                 icon=":material/bolt:"):
        load_demo_example()
        st.rerun()
    if st.button("Reset", width="stretch", icon=":material/restart_alt:"):
        reset_all()
        st.rerun()
    ui.markdown(ui.sidebar_footer_html())


def under_the_hood(title: str, input_data, output_data, passed_forward: str):
    with st.expander(f"Under the Hood — {title}"):
        st.markdown("**Input:**")
        st.write(input_data)
        st.markdown("**AI output (raw JSON):**")
        if hasattr(output_data, "model_dump"):
            st.json(output_data.model_dump())
        else:
            st.json(output_data)
        st.markdown(f"**Passed forward:** {passed_forward}")


def run_stage_safely(fn, *args, fallback):
    """Runs an LLM-backed stage function; on failure, uses `fallback` data
    and shows a subtle notice instead of crashing the app."""
    try:
        return fn(*args), False
    except Exception as e:
        st.session_state.error = str(e)
        return fallback, True


def show_error():
    if st.session_state.error:
        st.info(st.session_state.error)
        st.session_state.error = None


# ---------------------------------------------------------------------------
# SCREEN 1 — Idea Input
# ---------------------------------------------------------------------------
if st.session_state.stage == "input":
    with st.container(key="cv-main"):
        ui.markdown(ui.hero_html())

        with st.container(key="cvcard-idea"):
            ui.markdown(ui.card_head_html(
                "Your idea", "bulb",
                "One or two sentences is plenty — Discovery expands it into a "
                "problem, an audience and the harm risks.",
            ))
            raw_idea = st.text_area(
                "Your idea",
                key="idea_input",
                placeholder="e.g. A coaching business run by and for neurodivergent adults.",
                height=110,
                max_chars=300,
                label_visibility="collapsed",
            )
            analyze_col, demo_col = st.columns(2)
            with analyze_col:
                analyze_clicked = st.button("Analyze \u2192", type="primary", width="stretch")
            with demo_col:
                demo_clicked = st.button("Try the demo example instead", width="stretch")

        ui.markdown(ui.features_html())

    if demo_clicked:
        load_demo_example()
        st.rerun()

    if analyze_clicked:
        if not raw_idea or not raw_idea.strip():
            st.warning("Please enter an idea first.")
        else:
            st.session_state.raw_idea = raw_idea.strip()
            with st.spinner("Running Discovery — extracting the real problem, "
                             "audience, and harm risks..."):
                result, used_fallback = run_stage_safely(
                    run_discovery, st.session_state.raw_idea,
                    fallback=demo.DEMO_DISCOVERY,
                )
            st.session_state.discovery = result
            if used_fallback:
                st.session_state.error = (
                    "Live Discovery call failed — using a reference example "
                    "for this step so you can keep going."
                )
            st.session_state.stage = "discovery"
            st.rerun()

    ui.markdown(ui.hero_panel_html())

# ---------------------------------------------------------------------------
# SCREEN 2 — Discovery
# ---------------------------------------------------------------------------
elif st.session_state.stage == "discovery":
    d: DiscoveryOutput = st.session_state.discovery
    with st.container(key="cv-main"):
        ui.markdown(ui.page_header_html(
            "discovery", "Discovery",
            "What the idea actually is, who it serves, and where the harm risks sit.",
        ))
        show_error()

        ui.markdown(ui.grid_html([
            ui.insight_card_html("target", "Problem", d.problem),
            ui.insight_card_html("users", "Target user", d.target_user),
            ui.insight_card_html("star", "Key value", d.key_value),
            ui.insight_card_html("users", "Served population", d.served_population),
            ui.insight_card_html("alert", "Harm risk notes", d.harm_risk_notes),
            ui.insight_card_html("lock", "Constraints", d.constraints),
            ui.insight_card_html("compass", "Assumptions", None, items=d.assumptions, wide=True),
        ], columns=2))

        under_the_hood(
            "Discovery",
            input_data=st.session_state.raw_idea,
            output_data=d,
            passed_forward="Full DiscoveryOutput \u2192 Strategist + Critic",
        )

        if st.button("Continue \u2192", type="primary"):
            with st.spinner("Running Strategist + Critic — generating 3 divergent "
                             "directions and self-critiquing each one..."):
                result, used_fallback = run_stage_safely(
                    run_strategy, d, fallback=demo.DEMO_STRATEGY
                )
            st.session_state.strategy = result
            if used_fallback:
                st.session_state.error = (
                    "Live Strategy call failed — using a reference example for "
                    "this step so you can keep going."
                )
            st.session_state.stage = "strategy"
            st.rerun()

# ---------------------------------------------------------------------------
# SCREEN 3 — 3 Brand Directions + Critique
# ---------------------------------------------------------------------------
elif st.session_state.stage == "strategy":
    directions = st.session_state.strategy.directions
    chosen = st.session_state.direction_choice

    with st.container(key="cv-main"):
        ui.markdown(ui.page_header_html(
            "strategy", "Three directions this brand could take",
            "Each one is generated to be genuinely different from the others, then "
            "critiqued by a second pass. Choose the one that fits.",
        ))
        show_error()

        for i, direction in enumerate(directions):
            is_chosen = chosen == direction.name
            with st.container(key=f"cvcard-dir-{i}"):
                ui.markdown(ui.direction_head_html(direction, is_chosen))
                ui.markdown(ui.direction_body_html(
                    direction,
                    ui.score_html("Genericness", direction.genericness_score),
                    ui.score_html("Harm risk", direction.harm_risk_score),
                ))
                ui.markdown(ui.grid_html([
                    ui.block_html("Strengths", ui.chips_html(direction.strengths), "check-circle"),
                    ui.block_html("Flaws", ui.list_html(direction.flaws), "alert"),
                ], columns=2))
                ui.markdown(ui.block_html(
                    "Sharper alternative",
                    ui.value_html(direction.sharper_alternative), "bolt",
                ))
                if st.button(
                    "Chosen — click to unselect" if is_chosen else "Choose this direction",
                    key=f"choose-{i}",
                    type="primary" if is_chosen else "secondary",
                ):
                    st.session_state.direction_choice = None if is_chosen else direction.name
                    st.rerun()

        under_the_hood(
            "Strategist + Critic",
            input_data=st.session_state.discovery,
            output_data=st.session_state.strategy,
            passed_forward="Locked BrandDirection \u2192 Constitution",
        )

        ui.markdown(ui.rule_html())
        lock_col, note_col = st.columns([1, 2])
        with lock_col:
            lock_clicked = st.button(
                "Lock this direction \u2192", type="primary",
                width="stretch", disabled=chosen is None,
            )
        with note_col:
            ui.markdown(ui.note_html(
                f"Selected: {chosen}" if chosen else
                "Choose a direction above to unlock the next step."
            ))

    if lock_clicked:
        locked: BrandDirection = next(d for d in directions if d.name == chosen)
        st.session_state.locked_direction = locked
        with st.spinner("Running Constitution — converting the locked "
                         "direction into enforceable rules..."):
            result, used_fallback = run_stage_safely(
                run_constitution, locked, st.session_state.discovery,
                fallback=demo.DEMO_CONSTITUTION,
            )
        st.session_state.constitution = result
        if used_fallback:
            st.session_state.error = (
                "Live Constitution call failed — using a reference example "
                "for this step so you can keep going."
            )
        st.session_state.stage = "constitution"
        st.rerun()

# ---------------------------------------------------------------------------
# SCREEN 4 — Brand Constitution
# ---------------------------------------------------------------------------
elif st.session_state.stage == "constitution":
    c: BrandConstitution = st.session_state.constitution
    with st.container(key="cv-main"):
        ui.markdown(ui.page_header_html(
            "constitution", "Brand constitution",
            "The rules that turn a direction into everyday writing decisions.",
        ))
        show_error()

        with st.container(key="cvcard-constitution"):
            ui.markdown(ui.tagline_html(c.tagline))
            ui.markdown(ui.rule_html())
            ui.markdown(ui.grid_html([
                ui.block_html("Audience promise", ui.value_html(c.audience_promise), "users"),
                ui.block_html("Positioning rule", ui.value_html(c.positioning_rule), "target"),
            ], columns=2))

        with st.container(key="cvcard-language"):
            ui.markdown(ui.grid_html([
                ui.block_html("Brand traits", ui.chips_html(c.traits, "primary"), "star"),
                ui.block_html("Traits to avoid", ui.chips_html(c.traits_to_avoid), "ban"),
            ], columns=2))
            ui.markdown(ui.grid_html([
                ui.block_html("Voice — do", ui.list_html(c.voice_do), "check"),
                ui.block_html("Voice — don't", ui.list_html(c.voice_dont), "x-circle"),
            ], columns=2))
            ui.markdown(ui.block_html(
                "Naming options",
                ui.rows_html([(n.name, n.why) for n in c.naming_options]), "tag",
            ))
            ui.markdown(ui.block_html(
                "Banned words and phrases",
                ui.banned_chips_html(c.banned_words), "ban",
            ))

        under_the_hood(
            "Constitution",
            input_data=st.session_state.locked_direction,
            output_data=c,
            passed_forward="Full BrandConstitution \u2192 Guardian",
        )

        if st.button("Continue to Guardian \u2192", type="primary"):
            st.session_state.stage = "guardian"
            st.rerun()

# ---------------------------------------------------------------------------
# SCREEN 5 — Guardian + Mini Brand Kit
# ---------------------------------------------------------------------------
elif st.session_state.stage == "guardian":
    # set by the demo-violation button; consumed here so it fires exactly once
    autorun = st.session_state.pop("guardian_autocheck", False)

    with st.container(key="cv-main"):
        ui.markdown(ui.page_header_html(
            "guardian", "Guardian",
            "Paste anything you are about to publish and check it against the "
            "locked constitution.",
        ))
        show_error()

        with st.container(key="cvcard-guardian"):
            ui.markdown(ui.card_head_html(
                "Content to check", "message",
                "A post, an email, a landing page headline — Guardian checks the "
                "wording, not the intent you had in mind.",
            ))
            content = st.text_area(
                "Content to check",
                value=st.session_state.guardian_content or "",
                placeholder=demo.DEMO_BAD_CONTENT,
                height=110,
                label_visibility="collapsed",
            )
            check_col, demo_col = st.columns(2)
            with check_col:
                check_clicked = st.button("Check content", type="primary", width="stretch")
            with demo_col:
                st.button("Try the demo violation", width="stretch",
                          on_click=use_demo_violation)

        gr = st.session_state.guardian_result
        if (check_clicked or autorun) and content.strip():
            st.session_state.guardian_content = content
            try:
                with st.spinner("Running Guardian — checking content against the "
                                 "locked constitution..."):
                    gr = run_guardian(st.session_state.constitution, content)
            except Exception:
                gr = demo.DEMO_GUARDIAN_FAIL
                st.info("Live Guardian call failed — showing a reference result.")
            st.session_state.guardian_result = gr

        if gr:
            if gr.verdict == "PASS":
                ui.markdown(ui.verdict_html(True))
            else:
                ui.markdown(ui.verdict_html(False, "".join([
                    ui.verdict_field_html("Violated rule", gr.violated_rule or "—"),
                    ui.verdict_field_html("Evidence", f"\u201c{gr.evidence_quote or ''}\u201d"),
                    ui.verdict_field_html("Why", gr.explanation or ""),
                ])))
            if gr.rewrite:
                ui.markdown(ui.rewrite_html(gr.rewrite, gr.why_rewrite_fits or ""))
            if gr.deterministic_flags:
                ui.markdown(ui.block_html(
                    "Deterministic lexicon also flagged",
                    ui.banned_chips_html(gr.deterministic_flags), "alert",
                ))

            under_the_hood(
                "Guardian",
                input_data={"content": st.session_state.guardian_content},
                output_data=gr,
                passed_forward="Terminal stage — feeds the Mini Brand Kit below",
            )

        ui.markdown(ui.rule_html())
        ui.markdown(ui.section_title_html("Mini Brand Kit"))
        kit = {
            "idea": st.session_state.raw_idea,
            "discovery": st.session_state.discovery.model_dump() if st.session_state.discovery else None,
            "locked_direction": st.session_state.locked_direction.model_dump() if st.session_state.locked_direction else None,
            "constitution": st.session_state.constitution.model_dump() if st.session_state.constitution else None,
            "last_guardian_check": gr.model_dump() if gr else None,
        }
        with st.expander("View full Mini Brand Kit (JSON)"):
            st.json(kit)
        st.download_button(
            "Download Mini Brand Kit (JSON)",
            data=json.dumps(kit, indent=2),
            file_name="covenant_brand_kit.json",
            mime="application/json",
        )
