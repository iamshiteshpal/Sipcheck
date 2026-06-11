# ──────────────────────────────────────────────────────────────────
#  CAS 360 – 2.0 DESIGN SYSTEM  ("Aurora Glass")
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
    "void":    "#070714",   # page background (deeper than 1.0's #0d0d24)
    "glass":   "rgba(17,17,48,0.55)",
    "border":  "rgba(139,92,246,0.16)",
    "violet":  "#8b5cf6",   # brand – kept from 1.0
    "cyan":    "#22d3ee",   # NEW aurora accent
    "mint":    "#34d399",   # gains
    "ember":   "#f87171",   # losses
    "amber":   "#fbbf24",   # warnings
    "ink":     "#f0f0ff",
    "muted":   "#8b93a7",
    "faint":   "#3b4154",
}

def inject_theme():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600;700&display=swap');

#MainMenu, footer, header[data-testid="stHeader"] {{ visibility:hidden; height:0; }}

/* ── Aurora background: animated gradient mesh ─────────────────── */
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

/* every number in the portal is mono – money deserves precision */
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

/* ── KPI ──────────────────────────────────────────────────────────*/
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

/* ── Section header (evolved from your 1.0 .section-title) ──────── */
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

/* ── Pills / badges ────────────────────────────────────────────── */
.pill {{ display:inline-flex; align-items:center; gap:6px;
         font-size:0.68rem; font-weight:600; padding:3px 11px; border-radius:999px;
         border:1px solid {C['border']}; color:{C['muted']};
         font-family:'JetBrains Mono',monospace; }}
.pill.live {{ color:{C['mint']}; border-color:rgba(52,211,153,0.35); }}
.pill.live::before {{ content:''; width:6px; height:6px; border-radius:50%;
         background:{C['mint']}; box-shadow:0 0 8px {C['mint']};
         animation:pulse 1.6s infinite; }}
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.35}} }}

/* ── Page header ─────────────────────────────────────────────────*/
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
</style>
""", unsafe_allow_html=True)


def page_header(title: str, sub: str, live: bool = False):
    pill = '<span class="pill live">LIVE</span>' if live else ''
    st.markdown(f'<div class="pg-h rise">{title} {pill}</div>'
                f'<div class="pg-s rise rise-1">{sub}</div>', unsafe_allow_html=True)


def section(title: str):
    st.markdown(f'<div class="sec"><span class="tick"></span>'
                f'<span class="t">{title}</span><span class="line"></span></div>',
                unsafe_allow_html=True)


def glass_kpi(label: str, value: str, sub: str = "", tone: str = "", delay: int = 1):
    st.markdown(f"""
    <div class="g-card rise rise-{delay}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub {tone}">{sub}</div>
    </div>""", unsafe_allow_html=True)
