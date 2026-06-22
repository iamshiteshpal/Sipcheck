"""
CAS360 / SipCheck – Theme System
Two functions exposed to every page:
    apply_theme()          – inject full CSS for the active theme
    theme_toggle_button()  – render the 🌙 / ☀️ button (called by sidebar_v2)

Uses html body compound selectors so specificity beats page-level !important rules.
Default theme: Light.
"""
import streamlit as st

# ── Color palettes ─────────────────────────────────────────────────────────────

LIGHT = {
    "bg":             "#F0F4FF",
    "sidebar":        "#E8EDFB",
    "primary":        "#4F46E5",
    "secondary":      "#06B6D4",
    "card":           "#FFFFFF",
    "text_primary":   "#1E1B4B",
    "text_secondary": "#6B7280",
    "success":        "#10B981",
    "warning":        "#F59E0B",
    "danger":         "#EF4444",
    "border":         "#E0E7FF",
}

DARK = {
    "bg":             "#0F0F1A",
    "sidebar":        "#1A1A2E",
    "primary":        "#818CF8",
    "secondary":      "#22D3EE",
    "card":           "#1E1E2E",
    "text_primary":   "#E2E8F0",
    "text_secondary": "#94A3B8",
    "success":        "#34D399",
    "warning":        "#FBBF24",
    "danger":         "#F87171",
    "border":         "#2D2D44",
}


def _get_theme() -> dict:
    if "theme" not in st.session_state:
        st.session_state["theme"] = "Light"
    return LIGHT if st.session_state["theme"] == "Light" else DARK


def apply_theme():
    """Inject comprehensive theme CSS. Call after render_sidebar() on every page."""
    t = _get_theme()
    is_light = st.session_state["theme"] == "Light"

    # Derived tokens
    btn_shadow   = "rgba(79,70,229,0.35)"   if is_light else "rgba(129,140,248,0.35)"
    focus_ring   = "rgba(79,70,229,0.18)"   if is_light else "rgba(129,140,248,0.18)"
    opt_hover    = "rgba(79,70,229,0.08)"   if is_light else "rgba(129,140,248,0.08)"
    tag_bg       = "rgba(79,70,229,0.12)"   if is_light else "rgba(129,140,248,0.12)"
    row_alt      = "#F5F7FF"                if is_light else "#1A1A2C"
    header_bg    = "#EEF2FF"                if is_light else "#16162A"
    input_bg     = "#FFFFFF"                if is_light else "#16162A"
    card_hover   = "#F8FAFF"                if is_light else "#25253A"
    sidebar_link = "rgba(79,70,229,0.07)"   if is_light else "rgba(129,140,248,0.07)"
    aurora       = ""                        if is_light else (
        "radial-gradient(900px 500px at 85% -10%,rgba(139,92,246,0.14),transparent 60%),"
        "radial-gradient(700px 450px at -10% 30%,rgba(34,211,238,0.08),transparent 55%),"
    )

    st.markdown(f"""<style>
/* ═══════════════════════════════════════════════════════════════════════════
   CAS360 Theme – {st.session_state['theme']} Mode
   Compound selectors (html body …) ensure higher specificity than page CSS.
═══════════════════════════════════════════════════════════════════════════ */

/* ── Transitions ──────────────────────────────────────────────────────────── */
html body .stApp,
html body section[data-testid="stSidebar"],
html body section[data-testid="stSidebar"] > div,
html body .block-container {{
    transition: background-color 0.3s ease, color 0.3s ease !important;
}}
input, textarea, button, select,
div[data-baseweb="select"] > div,
html body div[data-testid="stMetric"],
.g-card, .sip-card, .kpi-card-custom {{
    transition: background-color 0.3s ease, color 0.3s ease,
                border-color 0.3s ease, box-shadow 0.3s ease !important;
}}

/* ── App / page background ────────────────────────────────────────────────── */
html, body {{
    background: {t['bg']} !important;
}}
html body .stApp {{
    background: {aurora}{t['bg']} !important;
    color: {t['text_primary']} !important;
    background-attachment: fixed !important;
}}
html body [data-testid="stAppViewContainer"],
html body .main,
html body [data-testid="stMain"] {{
    background: {t['bg']} !important;
}}
html body .block-container {{
    background: transparent !important;
    color: {t['text_primary']} !important;
}}

/* ── Header / toolbar (always transparent) ───────────────────────────────── */
header[data-testid="stHeader"] {{
    background: transparent !important;
    backdrop-filter: none !important;
}}
header[data-testid="stHeader"] * {{ background: transparent !important; }}
div[data-testid="stToolbar"]   {{ background: transparent !important; }}
div[data-testid="stDecoration"] {{ display: none !important; }}
div[data-testid="stStatusWidget"] {{ background: transparent !important; }}
#MainMenu, footer {{ visibility: hidden !important; height: 0 !important; }}

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
html body section[data-testid="stSidebar"] {{
    background: {t['sidebar']} !important;
    border-right: 1px solid {t['border']} !important;
    backdrop-filter: none !important;
    box-shadow: none !important;
}}
html body section[data-testid="stSidebar"] > div {{
    background: {t['sidebar']} !important;
    border: none !important;
}}
html body section[data-testid="stSidebar"] p,
html body section[data-testid="stSidebar"] span:not([data-testid]),
html body section[data-testid="stSidebar"] label,
html body section[data-testid="stSidebar"] small {{
    color: {t['text_primary']} !important;
}}
html body section[data-testid="stSidebar"] a {{
    color: {t['text_secondary']} !important;
    border-left: 2px solid transparent !important;
}}
html body section[data-testid="stSidebar"] a:hover {{
    color: {t['primary']} !important;
    background: {sidebar_link} !important;
    border-left: 2px solid {t['primary']} !important;
}}
html body section[data-testid="stSidebar"] [aria-selected="true"],
html body section[data-testid="stSidebar"] a[aria-current] {{
    color: {t['primary']} !important;
    background: {tag_bg} !important;
    border-left: 2px solid {t['primary']} !important;
}}
/* Sidebar buttons (nav + toggle) */
html body section[data-testid="stSidebar"] .stButton > button {{
    background: {tag_bg} !important;
    color: {t['primary']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
}}
html body section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {t['primary']} !important;
    color: #ffffff !important;
    border-color: {t['primary']} !important;
}}

/* ── Text ─────────────────────────────────────────────────────────────────── */
html body p, html body li,
html body .stMarkdown, html body div[data-testid="stText"],
html body div[data-testid="stMarkdownContainer"] p,
html body div[data-testid="stMarkdownContainer"] li,
html body div[data-testid="stMarkdownContainer"] span {{
    color: {t['text_primary']} !important;
}}
html body h1, html body h2, html body h3,
html body h4, html body h5, html body h6 {{
    color: {t['text_primary']} !important;
}}
html body td, html body th {{ color: {t['text_primary']} !important; }}
.kpi-label, .pg-s {{
    color: {t['text_secondary']} !important;
}}
html body div[data-testid="stMetricLabel"],
html body div[data-testid="stMetricLabel"] * {{
    color: {t['text_secondary']} !important;
}}
.pg-h {{
    background: linear-gradient(
        90deg, {t['text_primary']} 30%, {t['primary']} 80%, {t['secondary']}
    ) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    color: transparent !important;
}}

/* ── Cards ────────────────────────────────────────────────────────────────── */
.g-card, .sip-card, .kpi-card-custom {{
    background: {t['card']} !important;
    border-color: {t['border']} !important;
    backdrop-filter: none !important;
}}
.g-card:hover, .sip-card:hover {{
    background: {card_hover} !important;
    border-color: {t['primary']} !important;
}}
.alert-banner {{
    background: {t['card']} !important;
    border-color: {t['border']} !important;
}}

/* ── Metric widgets ───────────────────────────────────────────────────────── */
html body div[data-testid="stMetric"] {{
    background: {t['card']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 14px !important;
}}
html body div[data-testid="stMetricValue"],
html body div[data-testid="stMetricValue"] * {{
    color: {t['text_primary']} !important;
}}
[data-testid="stMetricDelta"][data-direction="positive"],
[data-testid="stMetricDelta"][data-direction="positive"] * {{
    color: {t['success']} !important;
}}
[data-testid="stMetricDelta"][data-direction="negative"],
[data-testid="stMetricDelta"][data-direction="negative"] * {{
    color: {t['danger']} !important;
}}

/* ── Profit / loss ────────────────────────────────────────────────────────── */
.up, .profit   {{ color: {t['success']} !important; }}
.down, .loss   {{ color: {t['danger']}  !important; }}
.warn          {{ color: {t['warning']} !important; }}

/* ── Buttons (page-level) ─────────────────────────────────────────────────── */
html body .block-container .stButton > button {{
    background: linear-gradient(135deg, {t['primary']}, {t['secondary']}) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}}
html body .block-container .stButton > button:hover {{
    opacity: 0.88 !important;
    box-shadow: 0 6px 20px -4px {btn_shadow} !important;
    transform: translateY(-1px) !important;
}}
html body .block-container .stButton > button:active {{
    transform: translateY(0) !important;
}}

/* ── Text inputs ──────────────────────────────────────────────────────────── */
html body .stTextInput > div > div > input,
html body .stNumberInput > div > div > input,
html body .stTextArea > div > div > textarea {{
    background: {input_bg} !important;
    color: {t['text_primary']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 8px !important;
}}
html body .stTextInput > div > div > input:focus,
html body .stNumberInput > div > div > input:focus,
html body .stTextArea > div > div > textarea:focus {{
    border-color: {t['primary']} !important;
    box-shadow: 0 0 0 2px {focus_ring} !important;
}}
html body .stTextInput input::placeholder,
html body .stTextArea textarea::placeholder {{
    color: {t['text_secondary']} !important;
    opacity: 0.7 !important;
}}

/* ── Input / widget labels ────────────────────────────────────────────────── */
html body .stTextInput label,  html body .stNumberInput label,
html body .stTextArea label,   html body .stSelectbox label,
html body .stMultiSelect label, html body .stSlider label,
html body .stDateInput label,  html body .stCheckbox label,
html body .stRadio label,      html body .stFileUploader label {{
    color: {t['text_secondary']} !important;
    font-weight: 500 !important;
}}

/* ── Selectbox / Dropdown ─────────────────────────────────────────────────── */
html body div[data-baseweb="select"] > div,
html body div[data-baseweb="select"] input {{
    background: {input_bg} !important;
    color: {t['text_primary']} !important;
    border-color: {t['border']} !important;
}}
div[data-baseweb="popover"],
div[data-baseweb="menu"] {{
    background: {t['card']} !important;
    border: 1px solid {t['border']} !important;
    box-shadow: 0 8px 32px -8px rgba(0,0,0,0.18) !important;
}}
li[role="option"] {{
    background: {t['card']} !important;
    color: {t['text_primary']} !important;
}}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {{
    background: {opt_hover} !important;
    color: {t['primary']} !important;
}}
span[data-baseweb="tag"] {{
    background: {tag_bg} !important;
    color: {t['primary']} !important;
}}

/* ── Tabs ─────────────────────────────────────────────────────────────────── */
html body div[data-baseweb="tab-list"] {{
    background: {t['card']} !important;
    border-bottom: 1px solid {t['border']} !important;
}}
html body button[data-baseweb="tab"] {{
    background: transparent !important;
    color: {t['text_secondary']} !important;
    font-weight: 500 !important;
}}
html body button[data-baseweb="tab"][aria-selected="true"] {{
    color: {t['primary']} !important;
    background: transparent !important;
    border-bottom: 2px solid {t['primary']} !important;
}}

/* ── Tables / DataFrames ──────────────────────────────────────────────────── */
html body div[data-testid="stDataFrame"] {{
    border: 1px solid {t['border']} !important;
    border-radius: 10px !important;
    overflow: hidden;
}}
html body .stDataFrame thead tr th,
html body .stDataFrame thead tr {{
    background: {header_bg} !important;
    color: {t['text_primary']} !important;
    font-weight: 600 !important;
    border-color: {t['border']} !important;
}}
html body .stDataFrame tbody tr {{
    background: {t['card']} !important;
}}
html body .stDataFrame tbody tr:nth-child(even) {{
    background: {row_alt} !important;
}}
html body .stDataFrame tbody tr td {{
    color: {t['text_primary']} !important;
    border-color: {t['border']} !important;
}}

/* ── Expander ─────────────────────────────────────────────────────────────── */
html body div[data-testid="stExpander"] {{
    background: {t['card']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 10px !important;
}}
html body div[data-testid="stExpander"] summary,
html body div[data-testid="stExpander"] summary * {{
    color: {t['text_primary']} !important;
}}
html body div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
    background: {t['card']} !important;
}}

/* ── Alert boxes ──────────────────────────────────────────────────────────── */
html body div[data-testid="stAlert"] {{
    background: {t['card']} !important;
    border-color: {t['border']} !important;
    color: {t['text_primary']} !important;
}}

/* ── Checkbox / Radio ─────────────────────────────────────────────────────── */
html body .stCheckbox span, html body .stRadio span {{
    color: {t['text_primary']} !important;
}}

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr {{ border-color: {t['border']} !important; }}

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {t['bg']} !important; }}
::-webkit-scrollbar-thumb {{
    background: {t['border']} !important;
    border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {t['primary']} !important; }}

</style>""", unsafe_allow_html=True)


def theme_toggle_button():
    """Render 🌙 / ☀️ toggle button. Called inside sidebar_v2.render_sidebar()."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "Light"
    is_dark = st.session_state["theme"] == "Dark"
    label = "☀️  Light Mode" if is_dark else "🌙  Dark Mode"
    if st.button(label, key="__theme_toggle__", use_container_width=True):
        st.session_state["theme"] = "Light" if is_dark else "Dark"
        st.rerun()
