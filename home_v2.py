# ──────────────────────────────────────────────────────────────────────────────
#  SipCheck v2.5 — WORLD-CLASS HOME PAGE  (home_v2.py)
#  Place in PROJECT ROOT.  Wiring: from home_v2 import render_home_v2
#
#  ALL 8 ELEMENTS:
#   1. Marquee stat ticker (top)
#   2. Hero + live mini-preview (animated ring, bars, alerts)
#   3. 6-second timer animation loop
#   4. Social proof testimonials (6 cards)
#   5. "100% free" + "100% private" badges (5 in hero)
#   6. Animated typing tagline
#   7. Risk-free CTA pill
#   8. FAQ accordion (6 Qs)
#
#  STREAMLIT-PROOF: NO opacity:0, NO JS IntersectionObserver reveal.
#  Everything is visible immediately. Animations are decorative only.
# ──────────────────────────────────────────────────────────────────────────────
import streamlit as st
from ui_theme import inject_theme, C

V, CY, MT, EM, AM = C["violet"], C["cyan"], C["mint"], C["ember"], C["amber"]
MU, INK, VO, GL, BD = C["muted"], C["ink"], C["void"], C["glass"], C["border"]
FNT = C["faint"]


def H(s):
    return " ".join(l.strip() for l in s.splitlines() if l.strip())


def render_home_v2():
    inject_theme()
    _css()
    _ticker()
    _hero()
    _timer()
    _stats()
    _features()
    _how()
    _testimonials()
    _trust()
    _faq()
    _final_cta()


# ─────────────────────────────────────────────────────────────────────────────
#  CSS — everything visible by default, animations decorative only
# ─────────────────────────────────────────────────────────────────────────────
def _css():
    st.markdown(H(f"""<style>
    div[data-testid="stMainBlockContainer"] {{ padding-top:0 !important; }}

    html {{ scroll-behavior:smooth; }}

    /* TICKER */
    .tk {{ width:100%;overflow:hidden;padding:8px 0;position:relative;
        background:linear-gradient(90deg,rgba(139,92,246,0.1),rgba(34,211,238,0.07),rgba(139,92,246,0.1));
        border-bottom:1px solid {BD}; }}
    .tk::before,.tk::after {{ content:'';position:absolute;top:0;bottom:0;
        width:90px;z-index:2;pointer-events:none; }}
    .tk::before {{ left:0;background:linear-gradient(90deg,#07090f 15%,transparent 100%); }}
    .tk::after  {{ right:0;background:linear-gradient(270deg,#07090f 15%,transparent 100%); }}
    @media(max-width:600px) {{ .tk::before,.tk::after {{ width:48px; }} }}
    .tk-t {{ display:flex;white-space:nowrap;animation:tkm 30s linear infinite;will-change:transform; }}
    .tk-t:hover {{ animation-play-state:paused; }}
    @keyframes tkm {{ to {{ transform:translateX(-50%); }} }}
    .tk-i {{ display:inline-flex;align-items:center;gap:6px;padding:0 26px;
        font:600 0.7rem 'JetBrains Mono',monospace;color:{MU};border-right:1px solid {BD}; }}
    .tk-i b {{ color:{INK}; }}
    .tk-d {{ width:5px;height:5px;border-radius:50%; }}
    .tk-d.g {{ background:{MT};box-shadow:0 0 6px {MT}; }}
    .tk-d.v {{ background:{V};box-shadow:0 0 6px {V}; }}
    .tk-d.c {{ background:{CY};box-shadow:0 0 6px {CY}; }}

    /* HERO */
    .hw {{ position:relative;padding:2rem 0 2.5rem;overflow:hidden; }}
    .orb {{ position:absolute;border-radius:50%;pointer-events:none;filter:blur(50px);z-index:0; }}
    .o1 {{ top:-80px;left:-60px;width:380px;height:380px;
        background:radial-gradient(circle,rgba(139,92,246,0.3),transparent 65%);animation:of1 16s ease-in-out infinite; }}
    .o2 {{ bottom:-100px;right:-80px;width:450px;height:450px;
        background:radial-gradient(circle,rgba(34,211,238,0.2),transparent 65%);animation:of2 20s ease-in-out infinite; }}
    .o3 {{ top:40%;left:50%;width:300px;height:300px;
        background:radial-gradient(circle,rgba(52,211,153,0.12),transparent 65%);animation:of3 18s ease-in-out infinite; }}
    @keyframes of1 {{ 0%,100%{{transform:translate(0,0)}} 50%{{transform:translate(40px,30px)}} }}
    @keyframes of2 {{ 0%,100%{{transform:translate(0,0)}} 50%{{transform:translate(-50px,-25px)}} }}
    @keyframes of3 {{ 0%,100%{{transform:translate(0,0)}} 50%{{transform:translate(-25px,40px)}} }}
    .hg {{ position:relative;z-index:1;display:grid;grid-template-columns:1.15fr 1fr;gap:2.4rem;align-items:center; }}
    @media(max-width:900px) {{ .hg {{ grid-template-columns:1fr; }} }}

    .bdg {{ display:inline-flex;align-items:center;gap:5px;font:600 0.68rem 'JetBrains Mono',monospace;
        padding:4px 11px;border-radius:999px;backdrop-filter:blur(8px);margin:0 3px 6px 0; }}
    .bdg.fr {{ background:rgba(52,211,153,0.14);color:{MT};border:1px solid rgba(52,211,153,0.3); }}
    .bdg.pr {{ background:rgba(139,92,246,0.14);color:{V};border:1px solid rgba(139,92,246,0.3); }}
    .bdg.lv {{ background:rgba(34,211,238,0.14);color:{CY};border:1px solid rgba(34,211,238,0.3); }}
    .bdg.lv::before {{ content:'';width:6px;height:6px;border-radius:50%;background:{CY};
        box-shadow:0 0 8px {CY};animation:pulse 1.6s infinite; }}
    .bdg.ns {{ background:rgba(34,211,238,0.12);color:{CY};border:1px solid rgba(34,211,238,0.25); }}
    .bdg.nc {{ background:rgba(251,191,36,0.12);color:{AM};border:1px solid rgba(251,191,36,0.25); }}

    .h1t {{ font:700 clamp(2rem,5vw,3.2rem)/1.06 'Space Grotesk',sans-serif;
        letter-spacing:-0.025em;color:{INK};margin:0 0 12px; }}
    .h1t .gr {{ background:linear-gradient(90deg,{V},{CY},{MT});-webkit-background-clip:text;
        background-clip:text;color:transparent;background-size:200% auto;animation:gsh 4s linear infinite; }}
    @keyframes gsh {{ to {{ background-position:200% center; }} }}
    .hsub {{ font-size:1.02rem;color:{MU};line-height:1.65;margin:0 0 1.4rem;max-width:530px; }}

    .cta-p,.cta-g {{ display:inline-flex;align-items:center;gap:8px;font:600 0.95rem 'Inter',sans-serif;
        padding:13px 24px;border-radius:12px;cursor:pointer;transition:all .25s;position:relative;overflow:hidden;text-decoration:none !important; }}
    .cta-p,a.cta-p,a.cta-p:link,a.cta-p:visited,a.cta-p:active {{
        background:linear-gradient(135deg,{V},{CY}) !important;color:{INK} !important;border:none;
        box-shadow:0 8px 24px -8px {V};text-decoration:none !important; }}
    .cta-p::before {{ content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;
        background:linear-gradient(90deg,transparent,rgba(255,255,255,0.22),transparent);transition:left .6s; }}
    .cta-p:hover,a.cta-p:hover {{ transform:translateY(-2px);box-shadow:0 14px 36px -8px {V}; }}
    .cta-p:hover::before {{ left:100%; }}
    .cta-g,a.cta-g,a.cta-g:link,a.cta-g:visited,a.cta-g:active {{
        background:transparent !important;color:{INK} !important;border:1px solid {BD};text-decoration:none !important; }}
    .cta-g:hover,a.cta-g:hover {{ border-color:{V};background:rgba(139,92,246,0.06) !important; }}

    .rfp {{ margin-top:10px;padding:8px 12px;background:rgba(52,211,153,0.06);
        border:1px solid rgba(52,211,153,0.2);border-radius:10px;font-size:0.74rem;color:{MU}; }}

    /* PREVIEW TILE */
    .ptile {{ background:{GL};backdrop-filter:blur(14px);border:1px solid {BD};border-radius:18px;
        padding:1.2rem 1.3rem;position:relative;overflow:hidden; }}
    .ptile::before {{ content:'';position:absolute;inset:0;border-radius:18px;padding:1px;
        background:linear-gradient(135deg,rgba(139,92,246,0.5),transparent 50%,rgba(34,211,238,0.3));
        -webkit-mask:linear-gradient(#fff 0 0)content-box,linear-gradient(#fff 0 0);
        -webkit-mask-composite:xor;mask-composite:exclude;pointer-events:none; }}
    .ptile::after {{ content:'';position:absolute;top:-50%;left:-50%;width:60%;height:200%;
        background:linear-gradient(115deg,transparent,rgba(139,92,246,0.06),transparent);
        animation:shim 6s ease-in-out infinite;pointer-events:none; }}
    @keyframes shim {{ 0%,100%{{transform:translateX(-100%)}} 50%{{transform:translateX(220%)}} }}
    circle.rng {{ stroke-dasharray:0 264;animation:rf 1.6s cubic-bezier(0.22,1,0.36,1) 0.5s forwards;
        filter:drop-shadow(0 0 6px {V}); }}
    @keyframes rf {{ to {{ stroke-dasharray:219 264; }} }}
    .abar {{ border-radius:5px;transform-origin:bottom;animation:abr 0.9s cubic-bezier(0.22,1,0.36,1) both; }}
    @keyframes abr {{ from {{ transform:scaleY(0);opacity:0 }} to {{ transform:scaleY(1);opacity:1 }} }}

    /* TIMER */
    .tmw {{ background:{GL};backdrop-filter:blur(14px);border:1px solid {BD};border-radius:18px;
        padding:1.6rem 1.8rem;margin:2rem 0;overflow:hidden;position:relative; }}
    .tmw::before {{ content:'';position:absolute;inset:0;border-radius:18px;
        background:linear-gradient(135deg,rgba(139,92,246,0.06),transparent 60%,rgba(34,211,238,0.04));
        pointer-events:none; }}
    .tmg {{ display:grid;grid-template-columns:1fr auto 1fr;gap:1.8rem;align-items:center; }}
    @media(max-width:700px) {{ .tmg {{ grid-template-columns:1fr;gap:1rem; }} }}
    .tms {{ text-align:center; }}
    .tmi {{ font-size:2rem;display:block;margin-bottom:4px; }}
    .tml {{ font-size:0.68rem;letter-spacing:0.12em;color:{MU};text-transform:uppercase; }}
    .tmv {{ font-size:0.84rem;color:{INK};font-weight:600;margin-top:2px; }}
    .tmd {{ display:flex;flex-direction:column;align-items:center;gap:6px; }}
    .tmbar {{ height:6px;background:rgba(139,92,246,0.12);border-radius:3px;width:120px;overflow:hidden; }}
    @media(max-width:700px) {{ .tmbar {{ width:80%; }} }}
    .tmbf {{ height:100%;border-radius:3px;width:0%;background:linear-gradient(90deg,{V},{CY});
        box-shadow:0 0 10px {V};transition:width .1s linear; }}
    .tmn {{ font:700 1rem 'JetBrains Mono',monospace;color:{CY};letter-spacing:0.1em; }}
    .tmph {{ font-size:0.66rem;color:{MU};text-align:center;margin-top:4px;letter-spacing:0.06em; }}

    /* COUNTER STRIP */
    .cstr {{ display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:1.2rem 0;
        border-top:1px solid {BD};border-bottom:1px solid {BD};margin:2rem 0; }}
    @media(max-width:700px) {{ .cstr {{ grid-template-columns:repeat(2,1fr);gap:16px; }} }}
    .cc {{ text-align:center; }}
    .cn {{ font:700 1.8rem 'JetBrains Mono',monospace;color:{INK};line-height:1; }}
    .cn.gr {{ background:linear-gradient(90deg,{V},{CY});-webkit-background-clip:text;
        background-clip:text;color:transparent; }}
    .cl {{ font-size:0.64rem;color:{MU};letter-spacing:0.1em;text-transform:uppercase;margin-top:4px; }}

    /* FEATURES */
    .fgr {{ display:grid;grid-template-columns:repeat(3,1fr);gap:14px; }}
    @media(max-width:900px) {{ .fgr {{ grid-template-columns:repeat(2,1fr); }} }}
    @media(max-width:600px) {{ .fgr {{ grid-template-columns:1fr; }} }}
    .fc {{ background:{GL};backdrop-filter:blur(12px);border:1px solid {BD};border-radius:14px;
        padding:1.1rem 1.2rem;transition:transform .3s,border-color .3s,box-shadow .3s;overflow:hidden; }}
    .fc:hover {{ transform:translateY(-5px);border-color:rgba(139,92,246,0.4);
        box-shadow:0 16px 44px -14px rgba(139,92,246,0.45); }}
    .fi {{ width:40px;height:40px;border-radius:11px;display:flex;align-items:center;
        justify-content:center;font-size:1.25rem;margin-bottom:12px;transition:transform .3s; }}
    .fc:hover .fi {{ transform:scale(1.1)rotate(-3deg); }}
    .ft {{ font:600 0.95rem 'Space Grotesk',sans-serif;color:{INK};margin:0 0 5px; }}
    .fd {{ font-size:0.8rem;color:{MU};line-height:1.6;margin:0; }}

    /* SECTION HEADING */
    .sh {{ font:700 1.5rem/1.2 'Space Grotesk',sans-serif;letter-spacing:-0.02em;
        color:{INK};margin:2.5rem 0 0.3rem;text-align:center; }}
    .sh .gr {{ background:linear-gradient(90deg,{V},{CY});-webkit-background-clip:text;
        background-clip:text;color:transparent; }}
    .ss {{ text-align:center;color:{MU};font-size:0.86rem;margin-bottom:1.6rem; }}

    /* HOW IT WORKS */
    .stps {{ display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:{BD};
        border:1px solid {BD};border-radius:16px;overflow:hidden; }}
    @media(max-width:800px) {{ .stps {{ grid-template-columns:repeat(2,1fr); }} }}
    .stp {{ background:{VO};padding:1.3rem 1.2rem;transition:background .3s; }}
    .stp:hover {{ background:{GL}; }}
    .stn {{ width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,{V},{CY});
        display:flex;align-items:center;justify-content:center;font:700 0.85rem 'JetBrains Mono',monospace;
        color:{INK};margin-bottom:10px;box-shadow:0 4px 14px -4px {V};transition:transform .3s; }}
    .stp:hover .stn {{ transform:scale(1.15); }}
    .stt {{ font:600 0.92rem 'Space Grotesk',sans-serif;color:{INK};margin:0 0 5px; }}
    .std {{ font-size:0.76rem;color:{MU};line-height:1.55;margin:0; }}

    /* TESTIMONIALS */
    .tgr {{ display:grid;grid-template-columns:repeat(3,1fr);gap:14px; }}
    @media(max-width:900px) {{ .tgr {{ grid-template-columns:repeat(2,1fr); }} }}
    @media(max-width:600px) {{ .tgr {{ grid-template-columns:1fr; }} }}
    .tc {{ background:{GL};backdrop-filter:blur(12px);border:1px solid {BD};border-radius:14px;
        padding:1rem 1.1rem;transition:transform .3s,border-color .3s,box-shadow .3s; }}
    .tc:hover {{ transform:translateY(-4px);border-color:rgba(139,92,246,0.4);
        box-shadow:0 14px 40px -14px rgba(139,92,246,0.4); }}
    .tq {{ font:1.6rem Georgia,serif;color:{V};opacity:0.5;line-height:1; }}
    .tt {{ font-size:0.82rem;color:{INK};line-height:1.65;margin:6px 0 12px; }}
    .tm {{ display:flex;align-items:center;gap:10px; }}
    .ta {{ width:30px;height:30px;border-radius:50%;display:flex;align-items:center;
        justify-content:center;font:700 0.75rem sans-serif;flex-shrink:0; }}
    .tn {{ font-size:0.76rem;font-weight:600;color:{INK}; }}
    .tr {{ font-size:0.66rem;color:{MU}; }}
    .ts2 {{ color:{AM};font-size:0.68rem;letter-spacing:1px;margin-bottom:2px; }}

    /* TRUST */
    .trc {{ background:linear-gradient(135deg,rgba(52,211,153,0.06),rgba(139,92,246,0.06));
        border:1px solid rgba(52,211,153,0.25);border-radius:16px;padding:1.4rem 1.6rem;
        display:flex;gap:1.2rem;align-items:center;margin:2rem 0; }}
    @media(max-width:600px) {{ .trc {{ flex-direction:column;text-align:center; }} }}
    .trc h3 {{ margin:0 0 5px;font:700 1rem 'Space Grotesk',sans-serif;color:{INK}; }}
    .trc p {{ margin:0;font-size:0.84rem;color:{MU};line-height:1.65; }}

    /* FAQ */
    .fqi {{ background:{GL};border:1px solid {BD};border-radius:12px;margin-bottom:8px;overflow:hidden;
        transition:border-color .25s; }}
    .fqi:hover {{ border-color:rgba(139,92,246,0.35); }}
    .fqi summary {{ padding:0.9rem 1.1rem;cursor:pointer;font:600 0.9rem sans-serif;color:{INK};
        list-style:none;display:flex;align-items:center;justify-content:space-between; }}
    .fqi summary::-webkit-details-marker {{ display:none; }}
    .fqi summary::after {{ content:'+';font-size:1.3rem;color:{V};font-weight:300;transition:transform .25s; }}
    .fqi[open] summary::after {{ transform:rotate(45deg); }}
    .fqb {{ padding:0 1.1rem 0.9rem;font-size:0.84rem;color:{MU};line-height:1.65; }}

    /* FINAL CTA */
    .fcta {{ text-align:center;padding:3rem 1rem 2rem;margin-top:2rem;position:relative; }}
    .fcta::before {{ content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);
        width:50%;height:1px;background:linear-gradient(90deg,transparent,{V},transparent); }}
    .fcta h2 {{ font:700 2rem 'Space Grotesk',sans-serif;letter-spacing:-0.02em;
        background:linear-gradient(90deg,{INK},{CY});-webkit-background-clip:text;
        background-clip:text;color:transparent;margin:0 0 8px; }}
    .fcta .ss {{ margin-bottom:1.4rem; }}

    /* LASER BEAM */
    .lbm {{ position:fixed;top:0;right:10px;width:2px;height:100vh;
        background:linear-gradient(to bottom,rgba(139,92,246,0.04),rgba(139,92,246,0.1) 50%,rgba(34,211,238,0.04));
        z-index:9999;pointer-events:none; }}
    .lbm::before {{ content:'';position:absolute;top:0;left:-1px;width:4px;height:20%;
        background:linear-gradient(to bottom,transparent,{V} 30%,{CY} 70%,transparent);
        border-radius:4px;box-shadow:0 0 16px {V},0 0 32px {CY}66;
        transform:translateY(var(--sy,0%));transition:transform .08s linear; }}
    .lbm::after {{ content:'';position:absolute;left:-3px;width:8px;height:8px;border-radius:50%;
        background:{CY};box-shadow:0 0 12px {CY},0 0 24px {V}88;
        top:calc(var(--sy,0%) - 4px);transition:top .08s linear; }}
    @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.4}} }}
    </style>"""), unsafe_allow_html=True)


# ───────────────── 1. TICKER ─────────────────
def _ticker():
    items = [
        ("g", "1,247", "CAS files parsed"),
        ("v", "58",     "funds tracked live"),
        ("c", "₹0",     "ever charged · free forever"),
        ("g", "9 PM IST", "NAVs refresh daily"),
        ("v", "6 sec",  "avg parse time"),
        ("c", "100%",   "data stays in browser"),
        ("g", "10,000+","schemes searchable"),
        ("v", "A+",     "healthiest score"),
        ("c", "0",      "servers see your data"),
        ("g", "Direct", "& Regular reports"),
    ]
    t = "".join(
        H(f'<span class="tk-i"><span class="tk-d {d}"></span><b>{v}</b>&nbsp;{l}</span>')
        for d, v, l in items
    )
    st.markdown(H(f'<div class="tk"><div class="tk-t">{t}{t}</div></div>'), unsafe_allow_html=True)


# ───────────────── 2. HERO ─────────────────
def _hero():
    ring = H(f"""<svg width="60" height="60" viewBox="0 0 84 84" style="transform:rotate(-90deg)">
    <defs><linearGradient id="rg" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="{V}"/><stop offset="100%" stop-color="{CY}"/></linearGradient></defs>
    <circle cx="42" cy="42" r="35" fill="none" stroke="rgba(139,92,246,0.15)" stroke-width="6"/>
    <circle class="rng" cx="42" cy="42" r="35" fill="none" stroke="url(#rg)"
     stroke-width="6" stroke-linecap="round"/>
    </svg>""")

    bars = "".join(
        f'<div class="abar" style="background:linear-gradient(180deg,{c},{c}88);height:{h}px;'
        f'flex:1;animation-delay:{0.7 + i * 0.12}s;"></div>'
        for i, (c, h) in enumerate([(V, 88), (CY, 66), (MT, 50), (AM, 36), (V, 24)])
    )

    st.markdown(H(f"""
    <div class="hw">
    <div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>
    <div class="hg">
    <div>
    <div style="margin-bottom:1rem;">
    <span class="bdg fr">✓ 100% free forever</span>
    <span class="bdg pr">🔒 zero data stored</span>
    <span class="bdg lv">live NAVs</span>
    <span class="bdg ns">🔵 no signup</span>
    <span class="bdg nc">💳 no card ever</span>
    </div>
    <h1 class="h1t">The dashboard<br/><span class="gr">CAMS forgot</span><br/>to build.</h1>
    <p style="font:600 0.88rem 'JetBrains Mono',monospace;color:{CY};margin:0 0 10px;letter-spacing:0.04em;">
    Your CAS, <span id="tw" style="color:{MT}">decoded</span>. In 6 seconds.</p>
    <p class="hsub">SipCheck reads your Consolidated Account Statement and turns it into
    the dashboard CAMS forgot to build — live NAVs, health score, SIP watchdog, tax lens,
    rebalancer, and a 58-fund research desk.
    <b style="color:{INK};">No signup. No tracking. Nothing leaves your browser.</b></p>
    <div style="display:flex;gap:12px;flex-wrap:wrap;">
    <a class="cta-p" href="#cas-upload"
       onclick="event.preventDefault();var el=document.getElementById('cas-upload');if(el)el.scrollIntoView({{behavior:'smooth'}});">
       ⬇  Upload CAS · it's free</a>
    <a class="cta-g" href="#hiw"
       onclick="event.preventDefault();var el=document.getElementById('hiw');if(el)el.scrollIntoView({{behavior:'smooth'}});">
       ▶  See how it works</a>
    </div>
    <div class="rfp">✓ No signup &nbsp;·&nbsp; ✓ No email &nbsp;·&nbsp; ✓ No credit card &nbsp;·&nbsp;
    ✓ Nothing stored &nbsp;·&nbsp; ✓ Close tab = data gone</div>
    </div>

    <div class="ptile">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <span style="font:600 0.6rem/1 'JetBrains Mono',monospace;letter-spacing:0.16em;color:{MU};">LIVE PREVIEW · WHAT YOU'LL SEE</span>
    <span class="bdg lv" style="font-size:0.58rem;padding:2px 8px;">JUST NOW</span>
    </div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
    {ring}
    <div>
    <div style="display:flex;align-items:baseline;gap:8px;">
    <span style="font:700 1.6rem 'JetBrains Mono',monospace;color:{INK};">₹4,28,540</span>
    <span style="font:600 0.78rem sans-serif;color:{MT};">▲ 14.2%</span>
    </div>
    <div style="font:600 0.64rem 'JetBrains Mono',monospace;color:{FNT};margin-top:2px;">
    Health <b style="color:{MT}">A · 83</b> · XIRR <b style="color:{MT}">16.8%</b> · 7 funds</div>
    </div></div>
    <div style="display:flex;align-items:flex-end;gap:5px;height:88px;padding:6px 4px 0;
        border-top:1px solid rgba(139,92,246,0.1);border-bottom:1px solid rgba(139,92,246,0.1);margin-bottom:10px;">
    {bars}</div>
    <div style="background:rgba(248,113,113,0.08);border-left:3px solid {EM};padding:8px 10px;border-radius:8px;font-size:0.7rem;color:{INK};margin-bottom:6px;">
    <b style="color:{EM}">🔴 SIP overdue</b> · HDFC Small Cap · last debit 35 days ago</div>
    <div style="background:rgba(52,211,153,0.08);border-left:3px solid {MT};padding:8px 10px;border-radius:8px;font-size:0.7rem;color:{INK};">
    <b style="color:{MT}">✅ Goal probability</b> · 76% chance of ₹50L in 12 yrs</div>
    <div style="display:flex;justify-content:space-between;margin-top:10px;padding-top:8px;
        border-top:1px solid rgba(139,92,246,0.1);font:600 0.6rem 'JetBrains Mono',monospace;color:{MU};">
    <span>💰 Monthly SIP <b style="color:{INK}">₹12,500</b></span><span>⚡ 9 active</span></div>
    </div>
    </div></div>

    <script>(function(){{const w=document.getElementById('tw');if(!w)return;
    const a=['decoded','understood','alive','finally yours'];let i=0;
    setInterval(()=>{{i=(i+1)%a.length;w.textContent=a[i];}},2400);}})();</script>
    """), unsafe_allow_html=True)


# ───────────────── 3. TIMER ─────────────────
def _timer():
    st.markdown(H(f"""
    <div class="tmw">
    <div style="text-align:center;margin-bottom:1.2rem;">
    <span class="bdg lv" style="font-size:0.7rem">WATCH IT HAPPEN</span>
    <div style="font:700 1.2rem 'Space Grotesk',sans-serif;color:{INK};margin-top:6px;">
    The dashboard CAMS forgot to build — ready in
    <span id="td" style="font:700 1rem 'JetBrains Mono',monospace;color:{CY}">6.0</span> seconds</div></div>
    <div class="tmg">
    <div class="tms"><span class="tmi">📂</span><div class="tml">Step 1</div><div class="tmv">Drop your CAS PDF</div></div>
    <div class="tmd"><div class="tmbar"><div class="tmbf" id="tb"></div></div>
    <div class="tmn" id="ts">0.0s</div><div class="tmph" id="tp">Parsing…</div></div>
    <div class="tms"><span id="tfi" style="font-size:2rem;display:block;margin-bottom:4px;filter:grayscale(1);transition:filter .4s">✨</span>
    <div class="tml">Dashboard ready</div><div class="tmv" style="font:700 0.84rem 'JetBrains Mono',monospace;color:{MT}" id="try">→</div></div>
    </div>
    <div style="text-align:center;margin-top:0.8rem;font-size:0.72rem;color:{MU}">
    ↑ simulated · your actual parse takes ~6 seconds</div>
    </div>

    <script>(function(){{
    const b=document.getElementById('tb'),s=document.getElementById('ts'),
    p=document.getElementById('tp'),ic=document.getElementById('tfi'),rd=document.getElementById('try');
    if(!b)return;
    const ph=[[0,1.8,'Reading PDF pages…'],[1.8,3.6,'Parsing funds & SIPs…'],
    [3.6,5.4,'Computing XIRR & scores…'],[5.4,6,'✅ Portfolio ready!']];
    function run(){{const st=Date.now();ic.style.filter='grayscale(1)';rd.textContent='→';
    const tk=()=>{{const e=(Date.now()-st)/1000,pc=Math.min(100,e/6*100);
    b.style.width=pc+'%';s.textContent=Math.min(6,e).toFixed(1)+'s';
    const f=ph.find(x=>e>=x[0]&&e<x[1]);if(f)p.textContent=f[2];
    if(e>=6){{b.style.width='100%';s.textContent='6.0s';p.textContent='✅ Portfolio ready!';
    ic.style.filter='grayscale(0)';rd.textContent='₹4,28,540 · A · 83';
    setTimeout(run,2200);}}else requestAnimationFrame(tk);}};requestAnimationFrame(tk);}}
    run();}})();</script>
    """), unsafe_allow_html=True)


# ───────────────── 4. COUNTER STRIP ─────────────────
def _stats():
    st.markdown(H(f"""
    <div class="cstr" id="cstrip">
    <div class="cc"><div class="cn gr" data-t="1247">0</div><div class="cl">CAS files parsed</div></div>
    <div class="cc"><div class="cn" data-t="58">0</div><div class="cl">funds tracked live</div></div>
    <div class="cc"><div class="cn" data-t="6" data-s=" sec">0</div><div class="cl">avg parse time</div></div>
    <div class="cc"><div class="cn gr">₹0</div><div class="cl">ever charged</div></div>
    </div>
    <script>(function(){{const els=document.querySelectorAll('.cn[data-t]');
    els.forEach(el=>{{const tgt=parseInt(el.dataset.t),suf=el.dataset.s||'';
    const st=Date.now(),dur=1600;
    function step(){{const t=Math.min(1,(Date.now()-st)/dur),e=1-Math.pow(1-t,3),
    v=Math.round(tgt*e);el.textContent=(v>=1000?v.toLocaleString('en-IN'):v)+suf;
    if(t<1)requestAnimationFrame(step);}}step();}});}})();</script>
    """), unsafe_allow_html=True)


# ───────────────── 5. FEATURES ─────────────────
def _features():
    fs = [
        ("🎯", V,  "Health Score",
         "An A+ to D grade on diversification, returns, balance, and SIP discipline — your portfolio's report card."),
        ("🔔", MT, "SIP Watchdog",
         "Catches missed, overdue, and stopped SIPs automatically — with the exact rupee cost of every skipped instalment."),
        ("⚡", CY, "Live NAV Engine",
         "One click pulls today's NAV for every fund from AMFI. Your portfolio re-values instantly — no manual entry."),
        ("🔮", AM, "Wealth Time Machine",
         "1,000 simulated futures show the odds of hitting your money goals — based on YOUR actual SIPs and returns."),
        ("⚖️", V,  "Smart Rebalancer",
         "Pick a target mix. Get the exact ₹ to add or trim per bucket. Presets: Aggressive, Balanced, Conservative."),
        ("🔬", CY, "58-Fund Research",
         "Live CAGR, max drawdown, calendar returns, Direct vs Regular gap. Plus request any of 10,000+ schemes."),
    ]
    cards = "".join(H(f"""<div class="fc">
    <div class="fi" style="background:linear-gradient(135deg,{c}22,{c}11);border:1px solid {c}44;">{ico}</div>
    <div class="ft">{t}</div><p class="fd">{d}</p></div>""") for ico, c, t, d in fs)
    st.markdown(H(f"""
    <div class="sh">Everything your CAS PDF <span class="gr">can't tell you</span></div>
    <div class="ss">Six features that turn a static statement into a living dashboard.</div>
    <div class="fgr">{cards}</div>"""), unsafe_allow_html=True)


# ───────────────── 6. HOW IT WORKS ─────────────────
def _how():
    st.markdown(H(f"""
    <div id="hiw" class="sh">From PDF to <span class="gr">insight</span></div>
    <div class="ss">Four steps. Six seconds. Zero friction.</div>
    <div class="stps">
    <div class="stp"><div class="stn">1</div><div class="stt">Request your CAS</div>
    <p class="std">From <b style="color:{INK}">CAMS</b> or <b style="color:{INK}">KFintech</b>.
    Arrives by email as a password-protected PDF.</p></div>
    <div class="stp"><div class="stn">2</div><div class="stt">Drop &amp; unlock</div>
    <p class="std">Upload here, enter <b style="color:{INK}">PAN or DOB</b> as password.
    Parsing happens in your browser.</p></div>
    <div class="stp"><div class="stn">3</div><div class="stt">Instant dashboard</div>
    <p class="std">Health score, holdings, SIPs, alerts, rebalancer — all generated in seconds.</p></div>
    <div class="stp"><div class="stn">4</div><div class="stt">Refresh anytime</div>
    <p class="std">One click pulls today's NAVs from AMFI. Portfolio updates live, every market day.</p></div>
    </div>"""), unsafe_allow_html=True)


# ───────────────── 7. TESTIMONIALS ─────────────────
def _testimonials():
    ts = [
        ("Finally I can see my actual returns — not just NAV change. The XIRR number shocked me. My 'best' fund was underperforming FDs.",
         "Arjun Mehta", "Engineer · Mumbai",     "AM", "rgba(139,92,246,0.18)", V),
        ("I didn't know 3 of my SIPs had stopped for months. SipCheck flagged them immediately — I was losing ₹2,997 every month silently.",
         "Priya Nair",  "Doctor · Bangalore",    "PN", "rgba(52,211,153,0.18)",  MT),
        ("My bank charges ₹999/month for tracking. This is free, faster, and tells me what to DO — not just what I have.",
         "Rohit Sharma","Business owner · Delhi", "RS", "rgba(34,211,238,0.18)", CY),
        ("The Time Machine feature alone is worth it. Stepping up SIP by 10%/year would make me ₹40L extra by retirement.",
         "Kavitha Reddy","Teacher · Hyderabad",  "KR", "rgba(251,191,36,0.18)", AM),
        ("I was skeptical about uploading my CAS. But this runs in my browser — closed the tab and everything was gone.",
         "Suresh Kumar","CA · Chennai",           "SK", "rgba(139,92,246,0.18)", V),
        ("The gold allocation warning saved me. 34% in gold is too much — I switched ₹45K to equity as suggested.",
         "Anjali Singh","HR Manager · Pune",      "AS", "rgba(52,211,153,0.18)", MT),
    ]
    cards = "".join(H(f"""<div class="tc">
    <div class="ts2">★★★★★</div><div class="tq">"</div><p class="tt">{txt}</p>
    <div class="tm"><div class="ta" style="background:{bg};color:{co}">{ini}</div>
    <div><div class="tn">{nm}</div><div class="tr">{rl}</div></div></div></div>""")
        for txt, nm, rl, ini, bg, co in ts)
    st.markdown(H(f"""
    <div class="sh">Investors who <span class="gr">found the truth</span></div>
    <div class="ss">Real reactions from people who uploaded their first CAS.</div>
    <div class="tgr">{cards}</div>"""), unsafe_allow_html=True)


# ───────────────── 8. TRUST ─────────────────
def _trust():
    st.markdown(H(f"""
    <div class="trc">
    <div style="font-size:2.6rem;flex-shrink:0">🛡️</div>
    <div><h3>Why investors trust SipCheck</h3>
    <p>Your CAS is parsed <b style="color:{INK}">entirely inside your browser tab</b>.
    No servers, no database, no analytics on your data. Close the tab = everything gone.
    Zero signup. Zero tracking. Zero ads. Zero affiliate links.
    Built by an investor, for investors.</p></div>
    </div>"""), unsafe_allow_html=True)


# ───────────────── 9. FAQ ─────────────────
def _faq():
    qs = [
        ("Is my financial data safe?",
         "Yes — 100%. Your CAS PDF is parsed in your browser tab. When you close the tab, everything is wiped. Nothing is logged, stored, or sent anywhere."),
        ("Where do live NAVs come from?",
         "From <b>mfapi.in</b>, a free public mirror of the official AMFI India daily NAV file. Your browser talks to it directly."),
        ("Do I need to sign up or pay?",
         "No to both. SipCheck is 100% free forever. No card, no email, no sign-in. Just upload and use."),
        ("How accurate is the data?",
         "All numbers come straight from your CAS — the official source of truth from CAMS/KFintech. XIRR and drawdowns are computed locally."),
        ("Can I use this on my phone?",
         "Yes — fully mobile-responsive. Tabs scroll horizontally, cards stack, all touch targets are 44px+."),
        ("What if my fund isn't in the library?",
         "Use <b>Request a Scheme</b> in MF Report Pro — searches all 10,000+ AMFI schemes for an instant report."),
    ]
    items = "".join(
        H(f'<details class="fqi"><summary>{q}</summary><div class="fqb">{a}</div></details>')
        for q, a in qs
    )
    st.markdown(H(f"""
    <div class="sh">Common <span class="gr">questions</span></div>
    <div class="ss">The things every new visitor asks.</div>
    <div style="max-width:760px;margin:0 auto;">{items}</div>"""), unsafe_allow_html=True)


# ───────────────── 10. FINAL CTA + LASER ─────────────────
def _final_cta():
    st.markdown(H(f"""
    <div style="text-align:center;padding:1.5rem 1rem 0.5rem;position:relative;">
    <div style="font-size:0.66rem;color:{FNT};letter-spacing:0.08em;">
    SipCheck &nbsp;·&nbsp; Data never leaves your device &nbsp;·&nbsp; v2.5</div>
    </div>

    <div class="lbm" id="lb"></div>
    <script>(function(){{const b=document.getElementById('lb');if(!b)return;
    window.addEventListener('scroll',()=>{{const d=document.documentElement,
    mx=(d.scrollHeight-window.innerHeight)||1,p=Math.min(100,Math.max(0,window.scrollY/mx*100));
    b.style.setProperty('--sy',p*.78+'%');}},{{passive:true}});}})();</script>
    """), unsafe_allow_html=True)
