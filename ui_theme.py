# ──────────────────────────────────────────────────────────────────
#  SipCheck – DESIGN SYSTEM  ("Aurora Glass")
#  Import this at the top of EVERY page:
#
#      from ui_theme import inject_theme, glass_kpi, page_header, section
#      inject_theme()
#
#  One file controls the entire look of the portal.
# ──────────────────────────────────────────────────────────────────
import streamlit as st

# ── Design tokens ──────────────────────────────────────────────────
C = {
    "void":    "#070714",
    "glass":   "rgba(17,17,48,0.55)",
    "border":  "rgba(139,92,246,0.16)",
    "violet":  "#8b5cf6",
    "cyan":    "#22d3ee",
    "mint":    "#34d399",
    "ember":   "#f87171",
    "amber":   "#fbbf24",
    "ink":     "#f0f0ff",
    "muted":   "#8b93a7",
    "faint":   "#3b4154",
}

def inject_theme():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600;700&display=swap');

#MainMenu, footer {{ visibility:hidden; height:0; }}

/* ── FIX: black band at top – make header fully transparent ────── */
header[data-testid="stHeader"] {{
    background: transparent !important;
    backdrop-filter: none !important;
}}
header[data-testid="stHeader"] * {{ background: transparent !important; }}
div[data-testid="stToolbar"] {{ background: transparent !important; }}
div[data-testid="stDecoration"] {{ display: none !important; }}
div[data-testid="stStatusWidget"] {{ background: transparent !important; }}

/* ── Aurora background ──────────────────────────────────────────── */
.stApp {{
    background:
        radial-gradient(900px 500px at 85% -10%, rgba(139,92,246,0.14), transparent 60%),
        radial-gradient(700px 450px at -10% 30%, rgba(34,211,238,0.08), transparent 55%),
        radial-gradient(800px 600px at 50% 110%, rgba(52,211,153,0.05), transparent 60%),
        {C['void']};
    color:{C['ink']};
    font-family:'Inter',sans-serif;
}}
@keyframes auroraDrift {{
    0%,100% {{ background-position: 0% 0%, 0% 0%, 0% 0%, 0 0; }}
    50%     {{ background-position: 3% 4%, -3% 2%, 2% -3%, 0 0; }}
}}
@media (prefers-reduced-motion: no-preference) {{
    .stApp {{ animation: auroraDrift 18s ease-in-out infinite; background-size: 120% 120%; }}
}}

section[data-testid="stSidebar"] {{
    background: rgba(7,7,20,0.85);
    backdrop-filter: blur(18px);
    border-right: 1px solid {C['border']};
}}
.block-container {{ padding: 1.4rem 2.2rem 3rem; max-width: 1500px; }}

h1,h2,h3, .display {{ font-family:'Space Grotesk',sans-serif; letter-spacing:-0.02em; }}
.num {{ font-family:'JetBrains Mono',monospace; font-feature-settings:'zero'; }}

/* ── Glass card ─────────────────────────────────────────────────── */
.g-card {{
    position:relative;
    background:{C['glass']};
    backdrop-filter: blur(14px);
    border:1px solid {C['border']};
    border-radius:16px;
    padding:1.1rem 1.3rem;
    transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
}}
.g-card:hover {{
    transform: translateY(-3px);
    border-color: rgba(139,92,246,0.45);
    box-shadow: 0 12px 40px -12px rgba(139,92,246,0.35);
}}
.g-card::before {{
    content:''; position:absolute; inset:0; border-radius:16px; padding:1px;
    background: linear-gradient(135deg, rgba(139,92,246,0.4), transparent 40%, transparent 60%, rgba(34,211,238,0.25));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude;
    pointer-events:none;
}}

/* ── KPI ────────────────────────────────────────────────────────── */
.kpi-label {{ font-size:0.68rem; font-weight:600; color:{C['muted']};
              text-transform:uppercase; letter-spacing:0.12em; margin-bottom:6px; }}
.kpi-value {{ font-family:'JetBrains Mono',monospace; font-size:1.55rem;
              font-weight:700; color:{C['ink']}; line-height:1.1; }}
.kpi-sub   {{ font-size:0.74rem; margin-top:6px; font-family:'JetBrains Mono',monospace; }}
.up   {{ color:{C['mint']};  }}
.down {{ color:{C['ember']}; }}
.warn {{ color:{C['amber']}; }}

@keyframes riseIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:none; }} }}
.rise {{ animation: riseIn .5s ease both; }}
.rise-1 {{ animation-delay:.05s }} .rise-2 {{ animation-delay:.12s }}
.rise-3 {{ animation-delay:.19s }} .rise-4 {{ animation-delay:.26s }}

/* ── Section header ─────────────────────────────────────────────── */
.sec {{
    display:flex; align-items:center; gap:10px;
    margin:1.8rem 0 0.9rem;
}}
.sec .tick {{ width:8px; height:8px; border-radius:2px; background:{C['violet']};
              box-shadow:0 0 12px {C['violet']}; transform:rotate(45deg); }}
.sec .t {{ font-family:'Space Grotesk',sans-serif; font-size:0.78rem; font-weight:600;
           color:{C['ink']}; text-transform:uppercase; letter-spacing:0.14em; }}
.sec .line {{ flex:1; height:1px;
              background:linear-gradient(90deg, {C['border']}, transparent); }}

/* ── Pills / badges ─────────────────────────────────────────────── */
.pill {{ display:inline-flex; align-items:center; gap:6px;
         font-size:0.68rem; font-weight:600; padding:3px 11px; border-radius:999px;
         border:1px solid {C['border']}; color:{C['muted']};
         font-family:'JetBrains Mono',monospace; }}
.pill.live {{ color:{C['mint']}; border-color:rgba(52,211,153,0.35); }}
.pill.live::before {{ content:''; width:6px; height:6px; border-radius:50%;
         background:{C['mint']}; box-shadow:0 0 8px {C['mint']};
         animation:pulse 1.6s infinite; }}
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.35}} }}

/* ── Page header ────────────────────────────────────────────────── */
.pg-h {{ font-family:'Space Grotesk',sans-serif; font-size:1.75rem; font-weight:700;
         background:linear-gradient(90deg,{C['ink']} 30%, {C['violet']} 80%, {C['cyan']});
         -webkit-background-clip:text; background-clip:text; color:transparent;
         margin-bottom:2px; }}
.pg-s {{ font-size:0.82rem; color:{C['muted']}; margin-bottom:1.4rem; }}

/* Streamlit widget polish */
.stButton>button {{
    background:linear-gradient(135deg, rgba(139,92,246,0.18), rgba(34,211,238,0.10));
    border:1px solid rgba(139,92,246,0.35); color:{C['ink']};
    border-radius:10px; font-weight:600; transition:all .2s;
}}
.stButton>button:hover {{ border-color:{C['violet']};
    box-shadow:0 0 22px -6px {C['violet']}; transform:translateY(-1px); }}
div[data-testid="stMetric"] {{ background:{C['glass']}; border:1px solid {C['border']};
    border-radius:14px; padding:0.8rem 1rem; }}

/* ── SIP Cards ──────────────────────────────────────────────────── */
.sip-grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap:14px; }}
.sip-card {{
    position:relative; background:{C['glass']}; backdrop-filter:blur(14px);
    border:1px solid {C['border']}; border-radius:16px; padding:1.1rem 1.2rem;
    transition:transform .25s ease, border-color .25s ease, box-shadow .25s ease;
    overflow:hidden;
}}
.sip-card:hover {{
    transform:translateY(-3px); border-color:rgba(139,92,246,0.45);
    box-shadow:0 12px 40px -12px rgba(139,92,246,0.35);
}}
.sip-card::after {{
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg, {C['violet']}, {C['cyan']});
}}
.sip-card.overdue::after {{ background:linear-gradient(90deg, {C['ember']}, {C['amber']}); }}
.sip-card.missed::after  {{ background:{C['ember']}; }}
.sip-name {{ font-size:0.82rem; font-weight:600; color:{C['ink']}; margin-bottom:6px;
             white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.sip-amt {{ font-family:'JetBrains Mono',monospace; font-size:1.35rem; font-weight:700;
            color:{C['ink']}; display:flex; align-items:center; gap:8px; }}
.sip-detail {{ display:grid; grid-template-columns:1fr 1fr; gap:4px 12px;
               margin-top:10px; font-size:0.72rem; color:{C['muted']}; }}
.sip-detail b {{ color:{C['ink']}; font-weight:600; }}
.sip-bar {{ height:6px; background:rgba(139,92,246,0.12); border-radius:3px;
            margin-top:12px; overflow:hidden; }}
.sip-bar-fill {{ height:100%; border-radius:3px;
                 background:linear-gradient(90deg, {C['violet']}, {C['mint']}); }}
.sip-bar-fill.bad {{ background:linear-gradient(90deg, {C['ember']}, {C['amber']}); }}
.sip-streak {{ font-size:0.65rem; color:{C['muted']}; margin-top:4px;
               font-family:'JetBrains Mono',monospace; }}
.sip-badge {{ display:inline-flex; align-items:center; gap:4px;
              font-size:0.62rem; font-weight:700; padding:2px 10px; border-radius:999px; }}
.sip-badge.live    {{ background:rgba(52,211,153,0.15); color:{C['mint']}; }}
.sip-badge.dead    {{ background:rgba(248,113,113,0.15); color:{C['ember']}; }}
.sip-badge.overdue {{ background:rgba(251,191,36,0.2);  color:{C['amber']}; }}
.sip-badge.missed  {{ background:rgba(248,113,113,0.2); color:{C['ember']}; }}

/* ── Alert banner ───────────────────────────────────────────────── */
.alert-banner {{
    display:flex; align-items:center; gap:14px; padding:0.8rem 1.2rem;
    border-radius:14px; margin-bottom:10px; border-left:4px solid;
    background:{C['glass']}; backdrop-filter:blur(14px);
}}
.alert-banner.critical {{ border-left-color:{C['ember']};
    background:rgba(248,113,113,0.06); }}
.alert-banner.warning  {{ border-left-color:{C['amber']};
    background:rgba(251,191,36,0.06); }}
.alert-banner.info     {{ border-left-color:{C['cyan']};
    background:rgba(34,211,238,0.06); }}
.alert-icon {{ font-size:1.6rem; flex-shrink:0; }}
.alert-body {{ flex:1; }}
.alert-title {{ font-size:0.82rem; font-weight:600; color:{C['ink']}; }}
.alert-sub   {{ font-size:0.72rem; color:{C['muted']}; margin-top:2px; }}

/* ── MOBILE RESPONSIVE ──────────────────────────────────────────── */
@media (max-width: 768px) {{
    .block-container {{ padding: 0.8rem 0.9rem 2rem !important; }}
    .pg-h {{ font-size: 1.3rem !important; }}
    .pg-s {{ font-size: 0.74rem !important; }}

    /* KPI cards — compact padding, smaller text */
    .kpi-value {{ font-size: 1.05rem !important; }}
    .kpi-label {{ font-size: 0.58rem !important; }}
    .kpi-sub   {{ font-size: 0.66rem !important; margin-top: 3px !important; }}
    .g-card {{ padding: 0.65rem 0.8rem !important; border-radius: 12px; }}
    .g-card:hover {{ transform: none; }}
    .g-card svg {{ width: 140px !important; height: 140px !important; }}
    .g-card > div:first-child {{ width: 140px !important; height: 140px !important; }}

    /* Stack Streamlit columns vertically — one per row on mobile */
    div[data-testid="stHorizontalBlock"] {{ flex-wrap: wrap !important; gap: 6px !important; }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        min-width: 100% !important; flex: none !important; width: 100% !important;
    }}

    .sec {{ margin: 1rem 0 0.6rem; }}
    .sec .t {{ font-size: 0.68rem !important; letter-spacing: 0.1em; }}
    .sip-grid {{ grid-template-columns: 1fr !important; }}
    .sip-card {{ padding: 0.7rem 0.85rem !important; }}
    .sip-amt {{ font-size: 1.05rem !important; }}
    .stTabs [data-baseweb="tab-list"] {{
        overflow-x: auto !important; flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch; padding: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        white-space: nowrap; padding: 6px 12px !important;
        font-size: 0.72rem !important;
    }}
    .pill {{ font-size: 0.6rem; padding: 2px 8px; }}
    .alert-banner {{ padding: 0.6rem 0.9rem; }}
    .alert-icon {{ font-size: 1.2rem; }}
    .stButton > button {{ min-height: 44px; font-size: 0.82rem; }}
    .js-plotly-plot {{ overflow: hidden !important; }}
}}

@media (max-width: 480px) {{
    .block-container {{ padding: 0.5rem 0.6rem 2rem !important; }}
    .pg-h {{ font-size: 1.1rem !important; }}
    .kpi-value {{ font-size: 0.95rem !important; }}
    .kpi-label {{ font-size: 0.55rem !important; }}
    .g-card {{ padding: 0.5rem 0.65rem !important; }}
    .sip-card {{ padding: 0.6rem 0.75rem !important; }}
}}
</style>
""", unsafe_allow_html=True)


def _H(s: str) -> str:
    """Collapse multi-line HTML into one line so Streamlit never treats indented lines as a code block."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def page_header(title: str, sub: str, live: bool = False):
    pill = '<span class="pill live">LIVE</span>' if live else ''
    st.markdown(_H(f'<div class="pg-h rise">{title} {pill}</div>'
                   f'<div class="pg-s rise rise-1">{sub}</div>'), unsafe_allow_html=True)


def section(title: str):
    st.markdown(_H(f'<div class="sec"><span class="tick"></span>'
                   f'<span class="t">{title}</span><span class="line"></span></div>'),
                unsafe_allow_html=True)


def glass_kpi(label: str, value: str, sub: str = "", tone: str = "", delay: int = 1):
    st.markdown(_H(f"""
    <div class="g-card rise rise-{delay}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub {tone}">{sub}</div>
    </div>"""), unsafe_allow_html=True)
