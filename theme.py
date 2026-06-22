"""
CAS360 / SipCheck – Nuclear Theme System v2
Default: dark. Toggle persists in st.session_state['theme'] ('dark' | 'light').
"""
import streamlit as st


def _c(theme: str) -> dict:
    if theme == 'light':
        return {
            'bg':       '#F8FAFC',
            'sidebar':  '#FFFFFF',
            'card':     '#FFFFFF',
            'card2':    '#F1F5F9',
            'border':   '#E2E8F0',
            'text':     '#0F172A',
            'text2':    '#475569',
            'text3':    '#64748B',
            'accent':   '#4F46E5',
            'success':  '#059669',
            'danger':   '#DC2626',
            'warning':  '#D97706',
            'input_bg': '#FFFFFF',
            'btn_bg':   '#4F46E5',
            'btn_text': '#FFFFFF',
            'tab_sel':  'rgba(79,70,229,0.12)',
        }
    return {
        'bg':       '#0F0F1A',
        'sidebar':  '#16162A',
        'card':     '#1E1E2E',
        'card2':    '#2A2A3E',
        'border':   '#2D2D44',
        'text':     '#F1F5F9',
        'text2':    '#CBD5E1',
        'text3':    '#94A3B8',
        'accent':   '#818CF8',
        'success':  '#34D399',
        'danger':   '#F87171',
        'warning':  '#FBBF24',
        'input_bg': '#1E1E2E',
        'btn_bg':   '#818CF8',
        'btn_text': '#0F0F1A',
        'tab_sel':  'rgba(129,140,248,0.15)',
    }


def apply_theme():
    """Nuclear theme injection. Call immediately after st.set_page_config()."""
    # Normalize any old capitalized values from previous sessions
    raw = st.session_state.get('theme', 'dark')
    if raw in ('Light', 'Dark'):
        raw = raw.lower()
        st.session_state['theme'] = raw
    theme = raw
    c = _c(theme)

    st.markdown(f"""<style>
/* ═══════════════════════════════════════════════════════════════════════
   NUCLEAR THEME – CAS360 SipCheck  ({theme} mode)
   Every rule uses !important. Compound selectors beat page-level CSS.
═══════════════════════════════════════════════════════════════════════ */

/* ── 0. Transitions ──────────────────────────────────────────────────── */
*, *::before, *::after {{
    transition: background-color 0.25s ease, color 0.25s ease,
                border-color 0.25s ease !important;
}}

/* ── 1. Root backgrounds ─────────────────────────────────────────────── */
html, body {{
    background: {c['bg']} !important;
    color: {c['text']} !important;
}}
html body .stApp,
html body [data-testid="stAppViewContainer"],
html body [data-testid="stMain"],
html body .main,
html body section.main,
html body .block-container,
html body [class*="css"] {{
    background: {c['bg']} !important;
}}
/* Kill aurora gradient in light mode */
html body .stApp {{
    background-image: none !important;
    animation: none !important;
    color: {c['text']} !important;
}}

/* ── 2. NUCLEAR TEXT — every element inside the app ─────────────────── */
html body .stApp *,
html body .main *,
html body section[data-testid="stSidebar"] *,
html body .block-container * {{
    color: {c['text']} !important;
}}

/* ── 3. Restore profit / loss / accent colors (after nuclear rule) ───── */
.up, .profit, [class*="gain"],
[data-testid="stMetricDelta"][data-direction="positive"],
[data-testid="stMetricDelta"][data-direction="positive"] * {{
    color: {c['success']} !important;
}}
.down, .loss, [class*="loss"],
[data-testid="stMetricDelta"][data-direction="negative"],
[data-testid="stMetricDelta"][data-direction="negative"] * {{
    color: {c['danger']} !important;
}}
.warn {{ color: {c['warning']} !important; }}
.pill.live, .pill.live * {{ color: {c['success']} !important; }}
.pill {{ color: {c['text2']} !important; }}

/* ── 4. Sidebar ──────────────────────────────────────────────────────── */
html body section[data-testid="stSidebar"],
html body section[data-testid="stSidebar"] > div,
html body section[data-testid="stSidebar"] > div:first-child {{
    background: {c['sidebar']} !important;
    border-right: 1px solid {c['border']} !important;
    backdrop-filter: none !important;
    box-shadow: none !important;
}}
/* Hide header band */
header[data-testid="stHeader"],
header[data-testid="stHeader"] *,
div[data-testid="stToolbar"] {{ background: transparent !important; }}
div[data-testid="stDecoration"] {{ display: none !important; }}
#MainMenu, footer {{ visibility: hidden !important; height: 0 !important; }}

/* ── 5. Cards / containers ───────────────────────────────────────────── */
html body div[data-testid="stMetric"] {{
    background: {c['card']} !important;
    border: 1px solid {c['border']} !important;
    border-radius: 12px !important;
}}
html body div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {c['card']} !important;
    border: 1px solid {c['border']} !important;
    border-radius: 12px !important;
}}
/* Dashboard custom card classes */
.card, .g-card, .sip-card, .kpi-card-custom,
.fund-card, .alert-card, .insight-card, .notice {{
    background: {c['card']} !important;
    border: 1px solid {c['border']} !important;
    color: {c['text']} !important;
}}
.card *, .g-card *, .sip-card *,
.fund-card *, .alert-card * {{
    color: {c['text']} !important;
}}
/* tab-bar used in dashboard */
.tab-bar, .tab-bar-wrap {{
    background: {c['card']} !important;
    border-bottom: 1px solid {c['border']} !important;
}}

/* ── 6. Buttons — fix disabled look ─────────────────────────────────── */
html body .stButton > button,
html body .stDownloadButton > button,
html body button[kind="primary"],
html body button[kind="secondary"] {{
    background: {c['btn_bg']} !important;
    color: {c['btn_text']} !important;
    border: 1px solid {c['accent']} !important;
    opacity: 1 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}}
html body .stButton > button:hover,
html body .stDownloadButton > button:hover {{
    opacity: 0.88 !important;
    box-shadow: 0 4px 14px -4px {c['accent']}66 !important;
}}
html body .stButton > button:disabled,
html body .stDownloadButton > button:disabled {{
    opacity: 0.45 !important;
}}
/* Sidebar buttons (nav, Add CAS, Logout, theme toggle) */
html body section[data-testid="stSidebar"] .stButton > button {{
    background: {c['card']} !important;
    color: {c['text']} !important;
    border: 1px solid {c['border']} !important;
    opacity: 1 !important;
}}
html body section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {c['accent']} !important;
    color: {c['btn_text']} !important;
    border-color: {c['accent']} !important;
}}

/* ── 7. Inputs / selects ─────────────────────────────────────────────── */
html body .stTextInput > div > div > input,
html body .stNumberInput > div > div > input,
html body .stTextArea > div > div > textarea,
html body input[type="text"],
html body input[type="password"],
html body input[type="number"],
html body input[type="email"] {{
    background: {c['input_bg']} !important;
    color: {c['text']} !important;
    border: 1px solid {c['border']} !important;
    border-radius: 8px !important;
}}
html body .stTextInput input::placeholder,
html body .stTextArea textarea::placeholder,
html body input::placeholder {{
    color: {c['text3']} !important;
    opacity: 1 !important;
}}
html body div[data-baseweb="select"] > div,
html body div[data-baseweb="select"] input {{
    background: {c['input_bg']} !important;
    color: {c['text']} !important;
    border-color: {c['border']} !important;
}}
div[data-baseweb="popover"], div[data-baseweb="menu"] {{
    background: {c['card']} !important;
    border: 1px solid {c['border']} !important;
}}
li[role="option"] {{
    background: {c['card']} !important;
    color: {c['text']} !important;
}}
li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
    background: {c['card2']} !important;
    color: {c['accent']} !important;
}}
span[data-baseweb="tag"] {{
    background: {c['card2']} !important;
    color: {c['accent']} !important;
}}

/* ── 8. File Uploader — fix disabled look ────────────────────────────── */
html body [data-testid="stFileUploader"],
html body [data-testid="stFileUploaderDropzone"] {{
    background: {c['card']} !important;
    border: 2px dashed {c['accent']} !important;
    border-radius: 10px !important;
    color: {c['text']} !important;
    opacity: 1 !important;
}}
html body [data-testid="stFileUploader"] *,
html body [data-testid="stFileUploaderDropzone"] * {{
    color: {c['text']} !important;
    opacity: 1 !important;
}}
html body [data-testid="stFileUploader"] button,
html body [data-testid="stFileUploaderDropzone"] button {{
    background: {c['accent']} !important;
    color: white !important;
    opacity: 1 !important;
    border: none !important;
}}

/* ── 9. Tabs ─────────────────────────────────────────────────────────── */
html body .stTabs [data-baseweb="tab-list"],
html body div[data-baseweb="tab-list"] {{
    background: {c['card']} !important;
    border-radius: 8px !important;
    border-bottom: 1px solid {c['border']} !important;
    gap: 4px !important;
}}
html body .stTabs button[data-baseweb="tab"],
html body button[data-baseweb="tab"] {{
    background: transparent !important;
    color: {c['text2']} !important;
    font-weight: 500 !important;
    border: none !important;
    border-radius: 6px !important;
}}
html body .stTabs button[aria-selected="true"],
html body button[data-baseweb="tab"][aria-selected="true"] {{
    background: {c['tab_sel']} !important;
    color: {c['accent']} !important;
    border-bottom: 2px solid {c['accent']} !important;
}}

/* ── 10. Tables / DataFrames ─────────────────────────────────────────── */
html body div[data-testid="stDataFrame"],
html body [data-testid="stTable"] {{
    background: {c['card']} !important;
    border: 1px solid {c['border']} !important;
    border-radius: 10px !important;
    overflow: hidden;
}}
html body .stDataFrame *,
html body [data-testid="stTable"] * {{
    color: {c['text']} !important;
}}
html body .stDataFrame thead tr,
html body .stDataFrame thead tr th {{
    background: {c['card2']} !important;
    font-weight: 600 !important;
    border-color: {c['border']} !important;
}}
html body .stDataFrame tbody tr:nth-child(even) {{
    background: {c['card2']} !important;
}}

/* ── 11. Expander ────────────────────────────────────────────────────── */
html body div[data-testid="stExpander"],
html body .streamlit-expanderHeader {{
    background: {c['card']} !important;
    border: 1px solid {c['border']} !important;
    border-radius: 10px !important;
}}
html body div[data-testid="stExpander"] summary,
html body div[data-testid="stExpander"] summary * {{
    color: {c['text']} !important;
}}

/* ── 12. Alert / notification boxes ─────────────────────────────────── */
html body div[data-testid="stAlert"],
html body [data-baseweb="notification"] {{
    background: {c['card']} !important;
    border-color: {c['border']} !important;
    color: {c['text']} !important;
}}

/* ── 13. Radio / Checkbox / Toggle ──────────────────────────────────── */
html body .stRadio *, html body .stCheckbox *,
html body .stToggle *, html body [data-testid="stRadio"] *,
html body [data-testid="stToggle"] * {{
    color: {c['text']} !important;
}}

/* ── 14. Custom HTML inline styles override ──────────────────────────── */
/* Fund names, SIP names, table rows with hardcoded dark colors */
[style*="color:#718096"], [style*="color: #718096"],
[style*="color:#6B7280"], [style*="color: #6B7280"],
[style*="color:#4A5568"], [style*="color: #4A5568"],
[style*="color:#9CA3AF"], [style*="color: #9CA3AF"],
[style*="color:#94A3B8"], [style*="color: #94A3B8"] {{
    color: {c['text2']} !important;
}}
[style*="color:#e2e8f0"], [style*="color: #e2e8f0"],
[style*="color:#E2E8F0"], [style*="color:#f0f0ff"],
[style*="color:#F8FAFC"], [style*="color: #F8FAFC"],
[style*="color:#f7fafc"], [style*="color:#f6ad55"] {{
    color: {c['text']} !important;
}}
/* Dark card backgrounds in inline styles */
[style*="background:#0c0f1a"], [style*="background: #0c0f1a"],
[style*="background:#0C0F1A"], [style*="background:#1a1f2e"],
[style*="background:#161b27"], [style*="background:#0d0d24"],
[style*="background:#07090f"], [style*="background:#0B0914"] {{
    background: {c['card']} !important;
    border: 1px solid {c['border']} !important;
}}
/* var(--bg2) used in SIP center */
[style*="var(--bg2)"] {{
    background: {c['card']} !important;
}}

/* ── 15. Badges / Pills ──────────────────────────────────────────────── */
[class*="badge"], [class*="chip"], [class*="tag"] {{
    background: {c['card2']} !important;
    border: 1px solid {c['border']} !important;
}}
/* Keep semantic badge colors */
.pill-gain, .sip-badge.live {{ background: {c['success']}1a !important; }}
.pill-loss, .sip-badge.dead {{ background: {c['danger']}1a   !important; }}
.pill-gain, .pill-gain * {{ color: {c['success']} !important; }}
.pill-loss, .pill-loss * {{ color: {c['danger']}   !important; }}

/* ── 16. Plotly charts – transparent, text readable ─────────────────── */
.js-plotly-plot, .plotly, .stPlotlyChart {{
    background: transparent !important;
}}

/* ── 17. Scrollbar ───────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {c['bg']} !important; }}
::-webkit-scrollbar-thumb {{
    background: {c['border']} !important; border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {c['accent']} !important; }}

/* ── 18. Mobile ──────────────────────────────────────────────────────── */
@media (max-width: 768px) {{
    html body .block-container {{ padding: 0.5rem !important; }}
    html body h1 {{ font-size: 22px !important; }}
    html body h2 {{ font-size: 18px !important; }}
    html body [data-testid="stMetricValue"] {{ font-size: 18px !important; }}
    html body [data-testid="stMetric"] {{ padding: 10px !important; }}
}}

/* ── 19. Dividers ────────────────────────────────────────────────────── */
hr {{ border-color: {c['border']} !important; }}

</style>""", unsafe_allow_html=True)


def theme_toggle_button():
    """Render the 🌙/☀️ button in the sidebar. Called from sidebar_v2.render_sidebar()."""
    # Normalize old capitalized values
    raw = st.session_state.get('theme', 'dark')
    if raw in ('Light', 'Dark'):
        raw = raw.lower()
        st.session_state['theme'] = raw
    is_dark = raw == 'dark'
    label = "☀️  Light Mode" if is_dark else "🌙  Dark Mode"
    if st.sidebar.button(label, key="__theme_toggle__", use_container_width=True):
        st.session_state['theme'] = 'light' if is_dark else 'dark'
        st.rerun()


# Convenience exports for LIGHT/DARK dicts (used by chart helpers)
LIGHT = _c('light')
DARK  = _c('dark')


def get_chart_theme() -> dict:
    """Return Plotly layout colors for the active theme."""
    theme = st.session_state.get('theme', 'dark')
    if theme in ('Light', 'light'):
        return {'bg': '#FFFFFF', 'paper': '#F8FAFC',
                'text': '#0F172A', 'grid': '#E2E8F0'}
    return {'bg': '#1E1E2E', 'paper': '#0F0F1A',
            'text': '#F1F5F9', 'grid': '#2D2D44'}
