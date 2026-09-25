"""
Covenant design system.

Everything visual lives here: design tokens, the global stylesheet, inline SVG
icons and the small HTML builders the screens compose. app.py stays about flow
and data.

Colors are published as CSS custom properties (--cv-*), so the stylesheet below
is a plain string with no per-theme interpolation; only the token block is
generated per theme.
"""
from __future__ import annotations

import html

import streamlit as st

# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
LIGHT = {
    "bg": "#F8F9FF",
    "bg-glow": "#F1EDFF",
    "surface": "#FFFFFF",
    "surface-2": "#F5F3FF",
    "border": "#E6E8F0",
    "border-strong": "#D5D9E8",
    "text": "#11152F",
    "muted": "#68708A",
    "primary": "#5B4BFF",
    "primary-2": "#7C5CFF",
    "primary-ink": "#4338CA",
    "primary-soft": "#EDE9FF",
    "navy": "#0D1024",
    "navy-2": "#15152F",
    "on-navy": "#F4F5FF",
    "on-navy-muted": "#A9AFCB",
    "green": "#16A34A",
    "green-bg": "#F0FDF4",
    "green-ink": "#15803D",
    "amber": "#D97706",
    "amber-bg": "#FFFBEB",
    "amber-ink": "#B45309",
    "red": "#DC2626",
    "red-bg": "#FEF2F2",
    "red-ink": "#B91C1C",
    "shadow-card": "0 1px 2px rgba(17,21,47,.04), 0 6px 20px -10px rgba(17,21,47,.13)",
    "shadow-panel": "0 24px 60px -24px rgba(13,16,36,.45)",
    "shadow-primary": "0 8px 20px -10px rgba(91,75,255,.7)",
    "btn-from": "#7C5CFF",
    "btn-to": "#5B4BFF",
    # sidebar surface + the three wave layers painted at its bottom edge
    "side": "#FCFBFF",
    "side-blob-1": "rgba(124, 92, 255, .26)",
    "side-blob-2": "rgba(155, 133, 255, .30)",
    "side-blob-3": "rgba(91, 75, 255, .18)",
}

DARK = {
    "bg": "#0B0E1E",
    "bg-glow": "#141936",
    "surface": "#141834",
    "surface-2": "#1B2044",
    "border": "#272C4E",
    "border-strong": "#363C66",
    "text": "#ECEEFB",
    "muted": "#9AA1C4",
    "primary": "#7C6CFF",
    "primary-2": "#9B85FF",
    "primary-ink": "#C9BFFF",
    "primary-soft": "#232452",
    "navy": "#080B18",
    "navy-2": "#101430",
    "on-navy": "#F4F5FF",
    "on-navy-muted": "#A9AFCB",
    "green": "#4ADE80",
    "green-bg": "#12251A",
    "green-ink": "#86EFAC",
    "amber": "#FBBF24",
    "amber-bg": "#2A1F0A",
    "amber-ink": "#FCD34D",
    "red": "#F87171",
    "red-bg": "#2B1616",
    "red-ink": "#FCA5A5",
    "shadow-card": "0 1px 2px rgba(0,0,0,.45), 0 8px 24px -12px rgba(0,0,0,.7)",
    "shadow-panel": "0 24px 60px -24px rgba(0,0,0,.8)",
    "shadow-primary": "0 8px 20px -10px rgba(124,108,255,.55)",
    # Deliberately not the dark-mode accent: primary buttons carry white text,
    # and the lighter #7C6CFF ramp only reaches 3.9:1 against white.
    "btn-from": "#6350E8",
    "btn-to": "#4F3FE0",
    "side": "#11152E",
    "side-blob-1": "rgba(124, 108, 255, .22)",
    "side-blob-2": "rgba(99, 80, 232, .18)",
    "side-blob-3": "rgba(155, 133, 255, .14)",
}

# ---------------------------------------------------------------------------
# Icons (24x24 line icons, stroked with currentColor)
# ---------------------------------------------------------------------------
_ICONS = {
    "bulb": '<path d="M9.5 18h5M10.5 21h3M12 3a6 6 0 0 0-3.6 10.8c.4.3.6.7.6 1.2v1h6v-1c0-.5.2-.9.6-1.2A6 6 0 0 0 12 3z"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/>',
    "grid": '<rect x="3" y="3" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="3" width="7.5" height="7.5" rx="2"/><rect x="3" y="13.5" width="7.5" height="7.5" rx="2"/><rect x="13.5" y="13.5" width="7.5" height="7.5" rx="2"/>',
    "shield": '<path d="M12 3l7 2.8v5.7c0 4.5-2.9 7.9-7 9.5-4.1-1.6-7-5-7-9.5V5.8z"/>',
    "sparkle": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M18.4 15.6l.6 1.8 1.8.6-1.8.6-.6 1.8-.6-1.8-1.8-.6 1.8-.6z"/>',
    "refresh": '<path d="M20.5 12a8.5 8.5 0 1 1-2.6-6.1"/><path d="M20.5 4.5V11h-6.5"/>',
    "bolt": '<path d="M13 2.5L4.5 14H11l-1 7.5L19.5 10H13z"/>',
    "arrow-right": '<path d="M4 12h15"/><path d="M13.5 6.5L19 12l-5.5 5.5"/>',
    "lock": '<rect x="4.5" y="10" width="15" height="10.5" rx="2.6"/><path d="M8 10V7.2a4 4 0 0 1 8 0V10"/>',
    "check": '<path d="M20 6.5L9.5 17 4 11.5"/>',
    "check-circle": '<circle cx="12" cy="12" r="8.6"/><path d="M8.4 12.4l2.5 2.5 4.7-5"/>',
    "alert": '<circle cx="12" cy="12" r="8.6"/><path d="M12 7.8V13"/><path d="M12 16.3v.1"/>',
    "x-circle": '<circle cx="12" cy="12" r="8.6"/><path d="M15 9l-6 6M9 9l6 6"/>',
    "help": '<circle cx="12" cy="12" r="8.6"/><path d="M9.7 9.6a2.4 2.4 0 1 1 3.2 2.3c-.6.2-.9.8-.9 1.4v.3"/><path d="M12 16.4v.1"/>',
    "users": '<path d="M15.5 20v-1.6a3.9 3.9 0 0 0-3.9-3.9H7.4A3.9 3.9 0 0 0 3.5 18.4V20"/><circle cx="9.5" cy="7.2" r="3.6"/><path d="M21 20v-1.6a3.9 3.9 0 0 0-3-3.8"/><path d="M16 3.8a3.6 3.6 0 0 1 0 7"/>',
    "bar": '<path d="M6.5 20v-6.5"/><path d="M12 20V5"/><path d="M17.5 20v-9"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.4"/><circle cx="12" cy="12" r="1"/>',
    "star": '<path d="M12 3.6l2.6 5.2 5.8.9-4.2 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.2-4.1 5.8-.9z"/>',
    "compass": '<circle cx="12" cy="12" r="8.5"/><path d="M15.4 8.6l-2 5-5 2 2-5z"/>',
    "message": '<path d="M20 14.8a2.8 2.8 0 0 1-2.8 2.8H8.4L4 20.5V6.8A2.8 2.8 0 0 1 6.8 4h10.4A2.8 2.8 0 0 1 20 6.8z"/>',
    "tag": '<path d="M11.2 3.5H4.5v6.7l9 9a1.9 1.9 0 0 0 2.7 0l4-4a1.9 1.9 0 0 0 0-2.7z"/><circle cx="7.8" cy="7.8" r="1.1"/>',
    "ban": '<circle cx="12" cy="12" r="8.5"/><path d="M6.4 17.6l11.2-11.2"/>',
    "file": '<path d="M14 3.5H7.5a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2V8z"/><path d="M14 3.5V8h4.5"/>',
    "download": '<path d="M12 4v10"/><path d="M8 10.5l4 4 4-4"/><path d="M4.5 19.5h15"/>',
    "info": '<circle cx="12" cy="12" r="8.6"/><path d="M12 11v5.2"/><path d="M12 7.9v.1"/>',
    "quote": '<path d="M9.5 6.5C6.9 7.7 5.5 9.9 5.5 13v4.5h5V12H8.2c0-1.9.6-3.2 2.1-4z"/><path d="M18.5 6.5c-2.6 1.2-4 3.4-4 6.5v4.5h5V12h-2.3c0-1.9.6-3.2 2.1-4z"/>',
    "chevron-right": '<path d="M9.5 6l6 6-6 6"/>',
}

# The mark sits inside the gradient circle, so the glyph itself is white.
_LOGO_MARK = (
    '<svg viewBox="0 0 32 32" width="19" height="19" aria-hidden="true">'
    '<path d="M22.2 9.4a9.2 9.2 0 1 0 0 13.2" fill="none" stroke="#FFFFFF" '
    'stroke-width="4.2" stroke-linecap="round"/>'
    '<circle cx="23.4" cy="16" r="2.7" fill="#FFFFFF"/>'
    "</svg>"
)

STAGES = [
    ("input", "Idea", "bulb"),
    ("discovery", "Discovery", "search"),
    ("strategy", "Directions + Critique", "grid"),
    ("constitution", "Constitution", "shield"),
    ("guardian", "Guardian", "sparkle"),
]

STEP_SUBTITLES = {
    "input": "Your starting point",
    "discovery": "Understand & explore",
    "strategy": "Find the best direction",
    "constitution": "Your brand rules",
    "guardian": "Check & improve content",
}

FEATURES = [
    ("search", "Deep discovery", "Uncover your problem, audience, risks and unique value."),
    ("bulb", "Strategic directions", "Get three brand directions with AI critique."),
    ("shield", "Brand constitution", "Turn your chosen direction into clear, usable rules."),
    ("sparkle", "Guardian", "Check future content and get safer, on-brand rewrites."),
]

PANEL_BENEFITS = [
    ("users", "Clearer messaging", "Speak with confidence."),
    ("shield", "Safer and more inclusive", "Reduce harmful language."),
    ("bar", "Consistent across content", "Stay on brand, always."),
]

SIDE_FOOT = ("Turn your idea into a clear brand, a practical constitution, "
             "and consistent communication \u2014 with AI.")

# ---------------------------------------------------------------------------
# Stylesheet
# ---------------------------------------------------------------------------
_CSS = """
/* ---------- base ---------- */
html, body, [data-testid="stAppViewContainer"] { background: var(--cv-bg); }
[data-testid="stAppViewContainer"] {
  background-image: radial-gradient(760px 420px at 8% -6%, var(--cv-bg-glow) 0%, transparent 72%);
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMain"] { background: transparent; }
[data-testid="stMainBlockContainer"] {
  max-width: 1220px !important;
  margin: 0 auto !important;
  padding: 1.7rem 2.6rem 4.5rem !important;
}
[data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none; }
/* the native System / Light / Dark switcher lives in the main menu, and the
   design ships one fixed look; hiding the menu keeps it out of reach */
[data-testid="stMainMenu"], #MainMenu, [data-testid="stAppDeployButton"] { display: none !important; }

/* Streamlit fades the containers it is about to replace (opacity 1 -> .33 over
   1s, held back by a .5s delay). While a stage is in flight that leaves the old
   screen's tail sitting half-visible under the new one. Collapse the fade to a
   short one and delay it a little: quick reruns still swap without a flicker,
   slow ones never ghost. */
[data-testid="stElementContainer"] { transition: opacity .12s linear !important; }
[data-testid="stElementContainer"][data-stale="true"] {
  opacity: 0 !important;
  transition-delay: .25s !important;
}

/* st.expander is the only element Streamlit does not wrap in a
   stElementContainer, so it never carries data-stale: it fades to .33 and the
   old row stays on screen for the whole run. The app root publishes the script
   state instead, and this app grows expanders only out of finished stage
   output, so every expander visible mid-run is a leftover from the last render. */
[data-testid="stApp"][data-test-script-state="running"] [data-testid="stExpander"] {
  opacity: 0 !important;
  transition: opacity .12s linear .25s !important;
}

/* body type */
body, p, li, label, input, textarea, .stMarkdown, [data-testid="stWidgetLabel"] {
  font-family: var(--cv-font);
}
h1, h2, h3, h4, h5 { color: var(--cv-text); font-family: var(--cv-font); letter-spacing: -.022em; }
hr { border-color: var(--cv-border); margin: 1.6rem 0; }
a { color: var(--cv-primary); }

/* ---------- landing: make room for the fixed dark panel ---------- */
[data-testid="stMainBlockContainer"]:has(.cv-landing) {
  max-width: none !important;
  padding: 2.6rem 2.6rem 4.5rem !important;
  padding-right: calc(var(--cv-panel-w) + 3.2rem) !important;
}
/* the readable column never grows wider than a comfortable measure */
.st-key-cv-main { max-width: 1080px; margin: 0 auto; }
/* the toolbar sits over the dark panel, so its controls need light ink */
[data-testid="stAppViewContainer"]:has(.cv-landing) [data-testid="stHeader"] button,
[data-testid="stAppViewContainer"]:has(.cv-landing) [data-testid="stHeader"] a,
[data-testid="stAppViewContainer"]:has(.cv-landing) [data-testid="stToolbar"] svg {
  color: var(--cv-on-navy);
}

/* ---------- sidebar ---------- */
/* The waves at the bottom are painted as background layers on the section
   itself rather than as elements: the sidebar's inner content scrolls and every
   element wrapper is position:relative, so a decorative child would anchor to
   the wrong box. Backgrounds always sit behind the content, at any height. */
[data-testid="stSidebar"] {
  background-color: var(--cv-side);
  background-image:
    radial-gradient(86% 26% at 4% 106%, var(--cv-side-blob-1) 0%, var(--cv-side-blob-1) 12%, transparent 72%),
    radial-gradient(78% 24% at 78% 108%, var(--cv-side-blob-2) 0%, var(--cv-side-blob-2) 14%, transparent 72%),
    radial-gradient(62% 20% at 38% 114%, var(--cv-side-blob-3) 0%, var(--cv-side-blob-3) 16%, transparent 74%);
  background-repeat: no-repeat;
  border-right: 1px solid var(--cv-border);
  border-radius: 0 22px 22px 0;
  box-shadow: 12px 0 34px -28px rgba(13, 16, 36, .6);
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: 1.4rem 1.05rem 1.5rem; }
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding-top: .5rem; }

.cv-brand { display: flex; align-items: center; gap: .65rem; }
.cv-brand-mark {
  display: grid; place-items: center; flex: none;
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, var(--cv-btn-from), var(--cv-btn-to));
  box-shadow: 0 9px 18px -11px rgba(91, 75, 255, .95);
}
.cv-brand-name { font-size: 1.3rem; font-weight: 750; letter-spacing: -.03em; color: var(--cv-text); }
[data-testid="stMarkdownContainer"] .cv-brand-tag {
  margin: .8rem 0 0; font-size: .84rem; line-height: 1.55; color: var(--cv-muted);
}

/* step list: one connector line threaded through the circle centres */
.cv-steps { position: relative; display: flex; flex-direction: column; gap: .22rem; }
.cv-steps::before {
  content: ""; position: absolute; z-index: 0;
  left: calc(.55rem + 14px); top: 24px; bottom: 24px;
  width: 2px; border-radius: 2px; background: var(--cv-border-strong);
}
.cv-step {
  position: relative; display: flex; align-items: center; gap: .7rem;
  padding: .5rem .55rem; border-radius: 14px;
  font-size: .9rem; color: var(--cv-muted);
}
.cv-step-ico {
  display: grid; place-items: center; flex: none;
  width: 30px; height: 30px; border-radius: 50%;
  position: relative; z-index: 1;
  background: var(--cv-side); border: 1.5px solid var(--cv-border-strong);
  color: var(--cv-muted);
}
.cv-step-txt { display: flex; flex-direction: column; gap: .14rem; min-width: 0; }
.cv-step-label { font-size: .9rem; font-weight: 550; line-height: 1.25; }
.cv-step-sub { font-size: .755rem; line-height: 1.3; color: var(--cv-muted); }
.cv-step-chev { display: grid; place-items: center; flex: none; margin-left: auto; color: var(--cv-primary); }

.cv-step-done .cv-step-ico { background: var(--cv-primary-soft); border-color: transparent; color: var(--cv-primary); }
.cv-step-done .cv-step-label { color: var(--cv-text); font-weight: 650; }

.cv-step-active { background: var(--cv-primary-soft); }
.cv-step-active .cv-step-ico {
  background: linear-gradient(135deg, var(--cv-btn-from), var(--cv-btn-to));
  border-color: transparent; color: #fff;
  box-shadow: 0 9px 16px -11px rgba(91, 75, 255, .95);
}
.cv-step-active .cv-step-label { color: var(--cv-primary-ink); font-weight: 700; }
.cv-step-active .cv-step-sub { color: var(--cv-primary); opacity: .85; }

.cv-side-div { height: 1px; border-radius: 2px; background: var(--cv-border); }

.cv-side-foot {
  display: flex; gap: .6rem; align-items: flex-start;
  padding: .85rem .9rem;
  background: var(--cv-surface-2); border: 1px solid var(--cv-border);
  border-radius: 16px;
}
.cv-side-foot-ico { color: var(--cv-primary); flex: none; margin-top: .12rem; }
[data-testid="stMarkdownContainer"] .cv-side-foot p {
  margin: 0; font-size: .78rem; line-height: 1.5; color: var(--cv-muted);
}

/* sidebar buttons: roomy and deliberately different in weight */
[data-testid="stSidebar"] .stButton button {
  justify-content: flex-start; text-align: left;
  padding: .7rem .9rem; font-size: .89rem; font-weight: 600;
  border-radius: 13px;
}
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
[data-testid="stSidebar"] button[kind="primary"] { justify-content: space-between; }
/* the trailing arrow is two borders on a pseudo-element, so the sidebar needs
   no image asset for it */
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]::after,
[data-testid="stSidebar"] button[kind="primary"]::after {
  content: ""; flex: none; margin-left: auto;
  width: 10px; height: 10px; border-radius: 1px;
  border-top: 2px solid currentColor; border-right: 2px solid currentColor;
  transform: rotate(45deg) translate(-1px, 1px);
}

/* ---------- buttons ---------- */
.stButton button, .stDownloadButton button {
  font-family: var(--cv-font);
  border-radius: 11px; font-weight: 600; font-size: .9rem;
  border: 1px solid var(--cv-border) !important;
  background: var(--cv-surface) !important; color: var(--cv-text) !important;
  padding: .58rem 1.1rem;
  transition: background-color .16s ease, border-color .16s ease, box-shadow .16s ease, transform .16s ease;
}
.stButton button:hover, .stDownloadButton button:hover {
  border-color: var(--cv-primary) !important; color: var(--cv-primary) !important;
  background: var(--cv-surface) !important;
}
.stButton button:active, .stDownloadButton button:active { transform: translateY(1px); }
/* both the data-testid and the legacy kind attribute are matched: whichever
   Streamlit emits, the primary gradient wins over the base button rule */
button[data-testid="stBaseButton-primary"],
button[kind="primary"], button[kind="primaryFormSubmit"] {
  background: linear-gradient(135deg, var(--cv-btn-from), var(--cv-btn-to)) !important;
  border-color: transparent !important; color: #fff !important;
  box-shadow: var(--cv-shadow-primary);
}
button[data-testid="stBaseButton-primary"]:hover,
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {
  /* the generic hover rule above repaints the background with the surface
     colour, so the gradient has to be re-asserted here or the white label
     ends up on a white button */
  background: linear-gradient(135deg, var(--cv-btn-from), var(--cv-btn-to)) !important;
  border-color: transparent !important;
  color: #fff !important; box-shadow: var(--cv-shadow-primary);
  filter: brightness(1.07);
}
button[data-testid="stBaseButton-primary"]:disabled,
button[kind="primary"]:disabled,
button[data-testid="stBaseButton-primary"]:disabled:hover,
button[kind="primary"]:disabled:hover {
  background: var(--cv-border) !important; color: var(--cv-muted) !important;
  box-shadow: none; filter: none;
}
.stButton button:focus-visible, .stDownloadButton button:focus-visible {
  outline: 2px solid var(--cv-primary); outline-offset: 2px;
}

/* ---------- inputs ---------- */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-baseweb="textarea"], [data-baseweb="input"] {
  background: var(--cv-surface) !important;
  color: var(--cv-text) !important;
  font-family: var(--cv-font);
  font-size: .94rem; line-height: 1.6;
}
[data-baseweb="textarea"], [data-baseweb="input"] {
  border: 1px solid var(--cv-border) !important;
  border-radius: 12px !important;
}
[data-baseweb="textarea"]:focus-within, [data-baseweb="input"]:focus-within {
  border-color: var(--cv-primary) !important;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--cv-primary) 16%, transparent);
}
[data-testid="stTextArea"] textarea::placeholder { color: var(--cv-muted); opacity: .85; }
[data-testid="stTextArea"] [data-testid="InputInstructions"] { color: var(--cv-muted); font-size: .74rem; }
[data-testid="stWidgetLabel"] p { color: var(--cv-text); font-weight: 550; font-size: .9rem; }
[data-testid="stTooltipIcon"] svg { color: var(--cv-muted); }

/* ---------- cards (st.container keyed) ---------- */
[class*="st-key-cvcard-"] {
  background: var(--cv-surface);
  border: 1px solid var(--cv-border);
  border-radius: 18px;
  box-shadow: var(--cv-shadow-card);
  padding: 1.15rem 1.3rem 1.25rem;
}
.st-key-cvcard-idea { padding: 1.3rem 1.4rem 1.4rem; }
.st-key-cvcard-idea [data-testid="stTextArea"] { margin-top: .55rem; }
.st-key-cvcard-idea .stButton { margin-top: .2rem; }

/* ---------- expander (under the hood) ---------- */
[data-testid="stExpander"] details {
  border: 1px solid var(--cv-border) !important;
  border-radius: 14px !important;
  background: var(--cv-surface);
}
[data-testid="stExpander"] summary { font-weight: 550; font-size: .9rem; color: var(--cv-text); }
[data-testid="stExpander"] summary:hover { color: var(--cv-primary); }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] { background: transparent; }

/* ---------- radio as a choice card ---------- */
/* Kept because Streamlit renders radios in a few default places (data editor
   column menus, the settings popover) and the default look clashes. */
[data-testid="stRadio"] [role="radiogroup"] { gap: .55rem; }
[data-testid="stRadio"] label {
  border: 1px solid var(--cv-border);
  border-radius: 12px;
  padding: .65rem .9rem;
  background: var(--cv-surface);
  transition: border-color .16s ease, background-color .16s ease;
}
[data-testid="stRadio"] label:hover { border-color: var(--cv-primary); }
[data-testid="stRadio"] label:has(input:checked) {
  border-color: var(--cv-primary);
  background: var(--cv-primary-soft);
}

/* ---------- alerts, json, code ---------- */
[data-testid="stAlert"] {
  border-radius: 13px; border: 1px solid var(--cv-border);
  background: var(--cv-surface-2);
}
[data-testid="stAlert"] p { font-size: .9rem; }
[data-testid="stJson"], [data-testid="stCode"] pre, pre {
  border-radius: 13px; border: 1px solid var(--cv-border);
}
[data-testid="stCaptionContainer"] p { color: var(--cv-muted); font-size: .8rem; }

/* =====================================================================
   Landing hero
   ===================================================================== */
.cv-step-pill {
  display: inline-flex; align-items: center; gap: .4rem;
  background: var(--cv-primary-soft); color: var(--cv-primary-ink);
  border-radius: 999px; padding: .28rem .75rem;
  font-size: .72rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase;
}
/* Typography that lands on a real <h1>/<p>/<li> is scoped through the markdown
   container on purpose: Streamlit ships `.st-emotion-cache-<hash> p { font-size:
   inherit }` (and the same for headings), which outranks a plain class selector
   and would collapse these to the base 16px. One extra ancestor attribute gives
   the rule the class-level weight it needs to keep its own type scale. */
[data-testid="stMarkdownContainer"] .cv-hero-title {
  margin: .95rem 0 0; font-size: clamp(2.05rem, 3.5vw, 3.05rem);
  line-height: 1.07; font-weight: 800; letter-spacing: -.035em;
}
.cv-hero-title .cv-grad {
  background: linear-gradient(115deg, var(--cv-primary-2) 5%, var(--cv-primary) 50%, #4F46E5 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
[data-testid="stMarkdownContainer"] .cv-hero-sub {
  margin: .95rem 0 0; max-width: 52ch;
  color: var(--cv-muted); font-size: 1.02rem; line-height: 1.62;
}
.cv-section-title {
  margin: 2.5rem 0 .85rem; font-size: 1.05rem; font-weight: 700; letter-spacing: -.015em;
}

.cv-card-head { display: flex; align-items: center; gap: .5rem; }
.cv-card-ico {
  width: 28px; height: 28px; border-radius: 9px; flex: none;
  display: grid; place-items: center;
  background: var(--cv-primary-soft); color: var(--cv-primary);
}
.cv-card-title { font-size: .97rem; font-weight: 650; color: var(--cv-text); }
.cv-card-help { margin-left: auto; color: var(--cv-muted); display: grid; place-items: center; cursor: help; }

/* feature cards */
.cv-grid { display: grid; gap: .9rem; }
.cv-grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
/* two columns is the honest answer for the landing column width; four only fits
   once the viewport is wide enough to still give each card ~215px */
.cv-features { display: grid; gap: .9rem; grid-template-columns: repeat(2, minmax(0, 1fr)); }
@media (min-width: 1800px) { .cv-features { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
.cv-feature {
  background: var(--cv-surface); border: 1px solid var(--cv-border);
  border-radius: 16px; padding: 1.05rem 1.1rem;
  box-shadow: var(--cv-shadow-card);
  display: flex; flex-direction: column; gap: .5rem;
}
.cv-feature-ico {
  width: 34px; height: 34px; border-radius: 10px; flex: none;
  display: grid; place-items: center;
  background: var(--cv-primary-soft); color: var(--cv-primary);
}
.cv-feature-title { font-size: .92rem; font-weight: 650; color: var(--cv-text); }
.cv-feature-body { font-size: .84rem; line-height: 1.55; color: var(--cv-muted); }

/* insight cards (discovery) */
.cv-insight {
  background: var(--cv-surface); border: 1px solid var(--cv-border);
  border-radius: 15px; padding: .95rem 1.05rem;
  box-shadow: var(--cv-shadow-card);
}
.cv-insight-label {
  display: flex; align-items: center; gap: .42rem;
  font-size: .71rem; font-weight: 700; letter-spacing: .085em; text-transform: uppercase;
  color: var(--cv-muted);
}
.cv-insight-label svg { color: var(--cv-primary); }
.cv-insight-value { margin-top: .45rem; font-size: .93rem; line-height: 1.6; color: var(--cv-text); }
.cv-insight-wide { grid-column: 1 / -1; }
[data-testid="stMarkdownContainer"] .cv-insight-list {
  margin: .45rem 0 0; padding-left: 1.05rem;
  font-size: .93rem; line-height: 1.6; color: var(--cv-text);
}
.cv-insight-list li { margin-bottom: .2rem; }

/* scores */
.cv-score { display: flex; flex-direction: column; gap: .15rem; }
.cv-score-label { font-size: .73rem; font-weight: 650; letter-spacing: .06em; text-transform: uppercase; color: var(--cv-muted); }
.cv-score-value { font-size: 1.5rem; font-weight: 750; line-height: 1.2; }
.cv-score-good { color: var(--cv-green); }
.cv-score-warn { color: var(--cv-amber); }
.cv-score-bad { color: var(--cv-red); }

/* chips + pills */
.cv-chips { display: flex; flex-wrap: wrap; gap: .4rem; }
.cv-chip {
  display: inline-block; border-radius: 999px; padding: .22rem .68rem;
  font-size: .83rem; line-height: 1.5;
  background: var(--cv-surface-2); color: var(--cv-text);
  border: 1px solid var(--cv-border);
}
.cv-chip-primary { background: var(--cv-primary-soft); color: var(--cv-primary-ink); border-color: transparent; }
.cv-chip-red { background: var(--cv-red-bg); color: var(--cv-red-ink); border-color: transparent; }
.cv-chip-green { background: var(--cv-green-bg); color: var(--cv-green-ink); border-color: transparent; }
/* banned words: marked, never alarming */
.cv-chip-banned {
  display: inline-flex; align-items: center; gap: .32rem;
  background: var(--cv-surface-2); color: var(--cv-text);
}
.cv-chip-banned svg { color: var(--cv-muted); flex: none; }

.cv-rule { height: 1px; background: var(--cv-border); margin: 1.5rem 0; }
.cv-block { margin-top: 1.25rem; }
.cv-block .cv-insight-label { margin-bottom: .5rem; }

/* named list rows (naming options, direction detail) */
.cv-rows { display: flex; flex-direction: column; gap: .5rem; margin-top: .5rem; }
.cv-row {
  border: 1px solid var(--cv-border); border-radius: 12px;
  padding: .7rem .85rem; background: var(--cv-surface-2);
}
.cv-row-title { font-size: .9rem; font-weight: 650; color: var(--cv-text); }
.cv-row-body { font-size: .86rem; line-height: 1.55; color: var(--cv-muted); margin-top: .18rem; }

/* direction cards */
.cv-dir-head { display: flex; align-items: center; gap: .6rem; margin-bottom: .7rem; }
.cv-dir-name { font-size: 1.12rem; font-weight: 700; color: var(--cv-text); letter-spacing: -.02em; }
.cv-dir-flag {
  margin-left: auto; display: inline-flex; align-items: center; gap: .3rem;
  font-size: .74rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  color: var(--cv-primary-ink);
}
/* The chosen card carries a .cv-dir-flag; the card itself is Streamlit's own
   container, so :has() is how the flag reaches back up to restyle it. */
[class*="st-key-cvcard-dir"]:has(.cv-dir-flag) {
  border-color: var(--cv-primary) !important;
  box-shadow: var(--cv-shadow-primary);
}
.cv-dir-fields { display: flex; flex-direction: column; gap: .55rem; }
.cv-field-label {
  font-size: .7rem; font-weight: 700; letter-spacing: .085em; text-transform: uppercase;
  color: var(--cv-muted);
}
.cv-field-value { font-size: .92rem; line-height: 1.6; color: var(--cv-text); margin-top: .12rem; }
.cv-dir-actions { margin-top: 1rem; }
.cv-dir-scores { margin-top: .9rem; }
/* the card sits directly under the fields, so the button needs breathing room */
[class*="st-key-cvcard-dir"] .stButton { margin-top: 1.05rem; }

/* page header for stages 2-5 */
.cv-page-head { margin-bottom: 1.55rem; }
[data-testid="stMarkdownContainer"] .cv-page-title {
  margin: .8rem 0 0; font-size: clamp(1.7rem, 2.4vw, 2.2rem);
  font-weight: 780; letter-spacing: -.03em; line-height: 1.14;
}
[data-testid="stMarkdownContainer"] .cv-page-sub {
  margin: .6rem 0 0; color: var(--cv-muted); font-size: .97rem; line-height: 1.6; max-width: 62ch;
}

/* a brand tagline reads like a masthead, not like body copy */
[data-testid="stMarkdownContainer"] .cv-tagline {
  margin: .45rem 0 0; font-size: clamp(1.4rem, 2vw, 1.8rem); font-weight: 760;
  letter-spacing: -.03em; line-height: 1.22; color: var(--cv-text);
}
.cv-tagline-label { font-size: .7rem; font-weight: 700; letter-spacing: .11em;
  text-transform: uppercase; color: var(--cv-muted); }
[data-testid="stMarkdownContainer"] .cv-note {
  margin: .7rem 0 0; font-size: .82rem; line-height: 1.55; color: var(--cv-muted);
}

/* verdict */
.cv-verdict { border-left: 4px solid; border-radius: 14px; padding: 1rem 1.2rem; }
.cv-verdict-pass { background: var(--cv-green-bg); border-color: var(--cv-green); }
.cv-verdict-fail { background: var(--cv-red-bg); border-color: var(--cv-red); }
.cv-verdict-head { display: flex; align-items: center; gap: .5rem; font-size: 1rem; font-weight: 720; }
.cv-verdict-pass .cv-verdict-head { color: var(--cv-green-ink); }
.cv-verdict-fail .cv-verdict-head { color: var(--cv-red-ink); }
.cv-verdict-body { margin-top: .55rem; display: flex; flex-direction: column; gap: .4rem; }
.cv-verdict-k { font-size: .72rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; opacity: .75; }
.cv-verdict-v { font-size: .93rem; line-height: 1.6; color: var(--cv-text); }

/* rewrite card */
.cv-rewrite {
  border: 1px solid var(--cv-border); border-left: 4px solid var(--cv-primary);
  border-radius: 14px; padding: 1rem 1.15rem; background: var(--cv-surface);
  box-shadow: var(--cv-shadow-card);
}
.cv-rewrite-head {
  display: flex; align-items: center; gap: .45rem; margin-bottom: .45rem;
  font-size: .72rem; font-weight: 700; letter-spacing: .085em; text-transform: uppercase;
  color: var(--cv-primary);
}
.cv-rewrite-body { font-size: .97rem; line-height: 1.65; color: var(--cv-text); }
.cv-rewrite-note { margin-top: .55rem; font-size: .8rem; line-height: 1.55; color: var(--cv-muted); }

/* =====================================================================
   Dark brand panel
   ===================================================================== */
.cv-panel {
  position: fixed; top: 0; right: 0; bottom: 0; width: var(--cv-panel-w);
  display: flex; align-items: center; overflow: hidden;
  padding: 4.5rem 2.9rem;
  color: var(--cv-on-navy);
  background:
    radial-gradient(120% 78% at 78% 12%, #222A5C 0%, transparent 58%),
    linear-gradient(168deg, var(--cv-navy) 0%, var(--cv-navy-2) 52%, #1B1246 100%);
  border-top-left-radius: 44px; border-bottom-left-radius: 44px;
  box-shadow: var(--cv-shadow-panel);
  z-index: 1;
}
.cv-panel-inner { position: relative; z-index: 2; width: 100%; }
.cv-panel-eyebrow {
  font-size: .7rem; font-weight: 650; letter-spacing: .2em; text-transform: uppercase;
  color: var(--cv-on-navy-muted);
}
[data-testid="stMarkdownContainer"] .cv-panel-statement {
  margin: 1.15rem 0 0; font-family: var(--cv-serif);
  font-size: clamp(1.7rem, 2.2vw, 2.3rem); line-height: 1.24; font-weight: 400;
  letter-spacing: -.015em; color: var(--cv-on-navy);
}
[data-testid="stMarkdownContainer"] .cv-panel-statement em {
  font-style: italic;
  background: linear-gradient(100deg, #C4B5FD, #8B7BFF);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.cv-panel-benefits { margin-top: 2.1rem; display: flex; flex-direction: column; gap: 1.05rem; }
.cv-benefit { display: flex; gap: .8rem; align-items: flex-start; }
.cv-benefit-ico {
  width: 38px; height: 38px; border-radius: 50%; flex: none;
  display: grid; place-items: center;
  border: 1px solid rgba(244,245,255,.28); color: #D9D6FF;
  background: rgba(244,245,255,.05);
}
.cv-benefit-title { font-size: .92rem; font-weight: 650; color: var(--cv-on-navy); }
.cv-benefit-sub { font-size: .84rem; color: var(--cv-on-navy-muted); margin-top: .1rem; }
.cv-panel-orb {
  position: absolute; right: -22%; bottom: -20%; width: 30rem; height: 30rem;
  border-radius: 50%; z-index: 1; pointer-events: none;
  /* falls back to the panel navy at the rim so the orb reads as a glow
     instead of a hard-edged disc floating on the panel */
  background: radial-gradient(circle at 34% 28%, #E3DDFF 0%, #B7A3FF 17%, #7C5CFF 40%,
              #3B2A8C 66%, #16123C 84%, #0D1024 100%);
  box-shadow: 0 0 150px 60px rgba(124,92,255,.34), inset -30px -40px 90px rgba(8,11,24,.55);
  opacity: .88;
}
.cv-panel-orb::after {
  content: ""; position: absolute; inset: -18% ; border-radius: 50%;
  background: radial-gradient(circle at 60% 40%, rgba(124,92,255,.30), transparent 62%);
  filter: blur(28px);
}

/* =====================================================================
   Responsive
   ===================================================================== */
@media (max-width: 1280px) {
  [data-testid="stMainBlockContainer"]:has(.cv-landing) {
    max-width: 1220px !important;
    padding-right: 2.2rem !important;
  }
  .st-key-cv-main { max-width: none; }
  .cv-panel {
    position: static; width: auto; margin-top: 2.4rem;
    padding: 2.4rem 1.9rem; border-radius: 26px;
  }
  .cv-panel-orb { width: 20rem; height: 20rem; right: -14%; bottom: -26%; }
}
@media (max-width: 760px) {
  [data-testid="stMainBlockContainer"] { padding: 1.2rem 1.1rem 3rem !important; }
  [data-testid="stMainBlockContainer"]:has(.cv-landing) { padding-right: 1.1rem !important; }
  .cv-grid-2, .cv-features { grid-template-columns: 1fr; }
  .cv-panel { padding: 1.9rem 1.35rem; border-radius: 20px; }
  /* these two must carry the same ancestor prefix as their base rules, or the
     scoped base rule would win regardless of the media query */
  [data-testid="stMarkdownContainer"] .cv-panel-statement { font-size: 1.55rem; }
  [data-testid="stMarkdownContainer"] .cv-hero-title { font-size: 1.95rem; }
}
"""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def icon(name: str, size: int = 20, stroke: float = 1.7) -> str:
    body = _ICONS.get(name, _ICONS["info"])
    return (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


def inject_global_css(is_dark: bool) -> None:
    tokens = DARK if is_dark else LIGHT
    declarations = "\n".join(
        f"  --cv-{key.replace('_', '-')}: {value};" for key, value in tokens.items()
    )
    base = """  --cv-font: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --cv-serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, "Times New Roman", serif;
  --cv-panel-w: clamp(320px, 28vw, 470px);
  --cv-radius: 16px;"""
    st.markdown(
        f"<style>\n:root {{\n{declarations}\n{base}\n}}\n{_CSS}\n</style>",
        unsafe_allow_html=True,
    )


def markdown(html_str: str) -> None:
    st.markdown(html_str, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------
def sidebar_brand_html() -> str:
    return (
        f'<div class="cv-brand"><span class="cv-brand-mark">{_LOGO_MARK}</span>'
        '<span class="cv-brand-name">Covenant</span></div>'
        '<p class="cv-brand-tag">An AI brand constitution and Guardian that turns brand '
        "decisions into enforceable communication rules.</p>"
    )


def sidebar_steps_html(current_key: str) -> str:
    current = next(i for i, (key, _, _) in enumerate(STAGES) if key == current_key)
    rows = []
    for i, (key, label, icon_name) in enumerate(STAGES):
        if i < current:
            state, glyph = "done", icon("check", 15, 2.4)
        elif i == current:
            state, glyph = "active", icon(icon_name, 16, 1.9)
        else:
            state, glyph = "todo", icon(icon_name, 16, 1.8)
        chev = f'<span class="cv-step-chev">{icon("chevron-right", 15, 2.2)}</span>' if state == "active" else ""
        rows.append(
            f'<div class="cv-step cv-step-{state}">'
            f'<span class="cv-step-ico">{glyph}</span>'
            f'<span class="cv-step-txt">'
            f'<span class="cv-step-label">{esc(label)}</span>'
            f'<span class="cv-step-sub">{esc(STEP_SUBTITLES[key])}</span></span>'
            f"{chev}</div>"
        )
    return f'<nav class="cv-steps">{"".join(rows)}</nav>'


def sidebar_divider_html() -> str:
    return '<div class="cv-side-div"></div>'


def sidebar_footer_html() -> str:
    return (
        '<div class="cv-side-foot">'
        f'<span class="cv-side-foot-ico">{icon("sparkle", 16, 1.9)}</span>'
        f"<p>{esc(SIDE_FOOT)}</p></div>"
    )


def hero_html() -> str:
    return (
        '<div class="cv-landing">'
        '<span class="cv-step-pill">Step 1 of 5</span>'
        '<h1 class="cv-hero-title">Turn your idea into<br>'
        '<span class="cv-grad">a consistent brand</span></h1>'
        '<p class="cv-hero-sub">Covenant helps you build a brand constitution and '
        "Guardian that keeps your communication consistent, safe, and aligned \u2014 "
        "especially for organizations where tone, dignity, or identity matter.</p>"
        "</div>"
    )


def card_head_html(title: str, icon_name: str = "bulb", help_text: str = "") -> str:
    help_html = (
        f'<span class="cv-card-help" title="{esc(help_text)}">{icon("help", 16)}</span>'
        if help_text
        else ""
    )
    return (
        '<div class="cv-card-head">'
        f'<span class="cv-card-ico">{icon(icon_name, 16, 1.9)}</span>'
        f'<span class="cv-card-title">{esc(title)}</span>{help_html}</div>'
    )


def features_html() -> str:
    cards = "".join(
        f'<div class="cv-feature"><span class="cv-feature-ico">{icon(icon_name, 18, 1.9)}</span>'
        f'<div class="cv-feature-title">{esc(title)}</div>'
        f'<div class="cv-feature-body">{esc(body)}</div></div>'
        for icon_name, title, body in FEATURES
    )
    return f'<div class="cv-features">{cards}</div>'


def hero_panel_html() -> str:
    rows = "".join(
        f'<div class="cv-benefit"><span class="cv-benefit-ico">{icon(icon_name, 18, 1.8)}</span>'
        f'<div><div class="cv-benefit-title">{esc(title)}</div>'
        f'<div class="cv-benefit-sub">{esc(sub)}</div></div></div>'
        for icon_name, title, sub in PANEL_BENEFITS
    )
    return (
        '<div class="cv-panel"><div class="cv-panel-orb"></div>'
        '<div class="cv-panel-inner">'
        '<div class="cv-panel-eyebrow">A clearer brand<br>A safer tomorrow</div>'
        '<p class="cv-panel-statement">Better communication builds a '
        "<em>kinder</em> world.</p>"
        f'<div class="cv-panel-benefits">{rows}</div>'
        "</div></div>"
    )


def page_header_html(stage_key: str, title: str, subtitle: str = "") -> str:
    index = next(i for i, (key, _, _) in enumerate(STAGES) if key == stage_key) + 1
    sub = f'<p class="cv-page-sub">{esc(subtitle)}</p>' if subtitle else ""
    return (
        '<div class="cv-page-head">'
        f'<span class="cv-step-pill">Step {index} of {len(STAGES)}</span>'
        f'<h1 class="cv-page-title">{esc(title)}</h1>{sub}</div>'
    )


def section_title_html(text: str) -> str:
    return f'<div class="cv-section-title">{esc(text)}</div>'


def value_html(text) -> str:
    return f'<div class="cv-insight-value">{esc(text)}</div>'


def list_html(items) -> str:
    return '<ul class="cv-insight-list">' + "".join(
        f"<li>{esc(item)}</li>" for item in items
    ) + "</ul>"


def insight_card_html(icon_name: str, label: str, value, items=None, wide: bool = False) -> str:
    body = list_html(items) if items else value_html(value)
    cls = "cv-insight cv-insight-wide" if wide else "cv-insight"
    return (
        f'<div class="{cls}">'
        f'<div class="cv-insight-label">{icon(icon_name, 14, 2)}<span>{esc(label)}</span></div>'
        f"{body}</div>"
    )


def grid_html(blocks: list[str], columns: int = 2) -> str:
    return f'<div class="cv-grid cv-grid-{columns}">{"".join(blocks)}</div>'


def score_html(label: str, score: int) -> str:
    tone = "good" if score <= 3 else ("warn" if score <= 6 else "bad")
    return (
        '<div class="cv-score">'
        f'<span class="cv-score-label">{esc(label)}</span>'
        f'<span class="cv-score-value cv-score-{tone}">{int(score)}/10</span></div>'
    )


def chips_html(items, tone: str = "") -> str:
    cls = f"cv-chip cv-chip-{tone}" if tone else "cv-chip"
    return '<div class="cv-chips">' + "".join(
        f'<span class="{cls}">{esc(item)}</span>' for item in items
    ) + "</div>"


def rows_html(items) -> str:
    return '<div class="cv-rows">' + "".join(
        f'<div class="cv-row"><div class="cv-row-title">{esc(title)}</div>'
        f'<div class="cv-row-body">{esc(body)}</div></div>'
        for title, body in items
    ) + "</div>"


def field_html(label: str, value) -> str:
    return (
        f'<div><div class="cv-field-label">{esc(label)}</div>'
        f'<div class="cv-field-value">{esc(value)}</div></div>'
    )


def verdict_html(passed: bool, body_html: str = "") -> str:
    tone = "pass" if passed else "fail"
    head = "PASS" if passed else "FAIL"
    message = (
        "This content is consistent with the brand constitution."
        if passed
        else "This content violates the brand constitution."
    )
    glyph = icon("check-circle" if passed else "x-circle", 19, 2)
    body = f'<div class="cv-verdict-body">{body_html}</div>' if body_html else ""
    return (
        f'<div class="cv-verdict cv-verdict-{tone}">'
        f'<div class="cv-verdict-head">{glyph}<span>{head} \u2014 {message}</span></div>'
        f"{body}</div>"
    )


def verdict_field_html(label: str, value) -> str:
    return (
        f'<div><div class="cv-verdict-k">{esc(label)}</div>'
        f'<div class="cv-verdict-v">{esc(value)}</div></div>'
    )


def rewrite_html(text: str, note: str = "") -> str:
    note_html = f'<div class="cv-rewrite-note">{esc(note)}</div>' if note else ""
    return (
        '<div class="cv-rewrite">'
        f'<div class="cv-rewrite-head">{icon("sparkle", 15, 2)}<span>Suggested rewrite</span></div>'
        f'<div class="cv-rewrite-body">{esc(text)}</div>{note_html}</div>'
    )


def direction_head_html(direction, chosen: bool = False) -> str:
    flag = (
        f'<span class="cv-dir-flag">{icon("check-circle", 15, 2)}Chosen</span>'
        if chosen
        else ""
    )
    return (
        '<div class="cv-dir-head">'
        f'<span class="cv-dir-name">{esc(direction.name)}</span>{flag}</div>'
    )


def direction_body_html(direction, score_a: str, score_b: str) -> str:
    return (
        f'<div class="cv-dir-fields">'
        + field_html("Positioning", direction.positioning)
        + field_html("Target audience", direction.target_audience)
        + field_html("Differentiator", direction.differentiator)
        + field_html("Emotional territory", direction.emotional_territory)
        + "</div>"
        f'<div class="cv-grid cv-grid-2 cv-dir-scores">{score_a}{score_b}</div>'
    )


def block_html(label: str, body_html: str, icon_name: str = "") -> str:
    glyph = icon(icon_name, 14, 2) if icon_name else ""
    return (
        '<div class="cv-block">'
        f'<div class="cv-insight-label">{glyph}<span>{esc(label)}</span></div>'
        f"{body_html}</div>"
    )


def banned_chips_html(items) -> str:
    return '<div class="cv-chips">' + "".join(
        f'<span class="cv-chip cv-chip-banned">{icon("ban", 13, 1.9)}{esc(item)}</span>'
        for item in items
    ) + "</div>"


def tagline_html(text: str, label: str = "Tagline") -> str:
    return (
        f'<div class="cv-tagline-label">{esc(label)}</div>'
        f'<p class="cv-tagline">{esc(text)}</p>'
    )


def note_html(text: str) -> str:
    return f'<p class="cv-note">{esc(text)}</p>'


def rule_html() -> str:
    return '<div class="cv-rule"></div>'
