# ──────────────────────────────────────────────────────────────────
#  SipCheck v2.4 – WORLD-CLASS HOME / INTRO PAGE  (home_v2.py)
#  Place in PROJECT ROOT. Used by dashboard.py when no CAS uploaded.
#
#  Wiring (already in dashboard.py):
#     from home_v2 import render_home_v2
#     if not data_uploaded:
#         render_home_v2()
#
#  Brand:    SipCheck 📊
#  Tagline:  "Your CAS, decoded. In 6 seconds."
#  Theme:    Aurora glass (matches the rest of the portal)
#
#  Built to make a first-time visitor STOP and upload.
#  Zero AI · zero API · pure HTML + vanilla JS for the
#  animated number counter and typing tagline.
# ──────────────────────────────────────────────────────────────────
import streamlit as st
from ui_theme import inject_theme, C

VIOLET, CYAN, MINT, EMBER, AMBER = C["violet"], C["cyan"], C["mint"], C["ember"], C["amber"]
MUTED, INK, VOID, GLASS, BORDER = C["muted"], C["ink"], C["void"], C["glass"], C["border"]


def H(s: str) -> str:
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def render_home_v2():
    inject_theme()
    _inject_home_css()
    _render_hero()
    _render_stat_strip()
    _render_features()
    _render_how_it_works()
    _render_live_preview()
    _render_trust()
    _render_faq()
    _render_final_cta()


# ───────────────────────────────────────────────────────────────────
def _inject_home_css():
    st.markdown(H(f"""<style>
    /* hide streamlit chrome on intro */
    div[data-testid="stMainBlockContainer"] {{ padding-top: 0.5rem !important; }}

    /* ── LASER BEAM scroll progress (right edge) ─────────────────── */
    .scroll-beam {{
        position: fixed; top: 0; right: 12px;
        width: 2px; height: 100vh;
        background: linear-gradient(to bottom,
            rgba(139,92,246,0.05),
            rgba(139,92,246,0.12) 50%,
            rgba(34,211,238,0.05));
        z-index: 9999; pointer-events: none;
    }}
    .scroll-beam::before {{
        content:''; position: absolute; top: 0; left: -1px;
        width: 4px; height: 22%;
        background: linear-gradient(to bottom, transparent, {VIOLET} 30%, {CYAN} 70%, transparent);
        border-radius: 4px;
        box-shadow: 0 0 18px {VIOLET}, 0 0 36px {CYAN}66, 0 0 60px {VIOLET}33;
        transform: translateY(var(--scroll, 0%));
        transition: transform 0.08s linear;
    }}
    .scroll-beam::after {{
        content:''; position: absolute; left: -3px;
        width: 8px; height: 8px; border-radius: 50%;
        background: {CYAN}; box-shadow: 0 0 14px {CYAN}, 0 0 28px {VIOLET}88;
        top: calc(var(--scroll-y, 0%) - 4px);
        transition: top 0.08s linear;
    }}

    /* ── Reveal-on-scroll for sections ──────────────────────────── */
    .reveal {{
        opacity: 0; transform: translateY(40px);
        transition: opacity 0.9s cubic-bezier(0.22, 1, 0.36, 1),
                    transform 0.9s cubic-bezier(0.22, 1, 0.36, 1);
    }}
    .reveal.show {{ opacity: 1; transform: translateY(0); }}
    .reveal-delay-1 {{ transition-delay: 0.08s; }}
    .reveal-delay-2 {{ transition-delay: 0.16s; }}
    .reveal-delay-3 {{ transition-delay: 0.24s; }}
    .reveal-delay-4 {{ transition-delay: 0.32s; }}
    .reveal-delay-5 {{ transition-delay: 0.40s; }}
    .reveal-delay-6 {{ transition-delay: 0.48s; }}

    /* ── Parallax hero orbs ─────────────────────────────────────── */
    .hero-wrap {{ position:relative; padding: 1rem 0 3rem; overflow:hidden; }}
    .hero-orb-1, .hero-orb-2, .hero-orb-3 {{
        position:absolute; border-radius:50%; pointer-events:none;
        z-index:0; filter: blur(40px);
    }}
    .hero-orb-1 {{
        top:-100px; left:-80px; width:420px; height:420px;
        background: radial-gradient(circle, rgba(139,92,246,0.35), transparent 65%);
        animation: orbFloat1 16s ease-in-out infinite;
    }}
    .hero-orb-2 {{
        bottom:-120px; right:-100px; width:520px; height:520px;
        background: radial-gradient(circle, rgba(34,211,238,0.22), transparent 65%);
        animation: orbFloat2 22s ease-in-out infinite;
    }}
    .hero-orb-3 {{
        top:40%; left:55%; width:340px; height:340px;
        background: radial-gradient(circle, rgba(52,211,153,0.14), transparent 65%);
        animation: orbFloat3 19s ease-in-out infinite;
    }}
    @keyframes orbFloat1 {{
        0%,100% {{ transform: translate(0,0) scale(1); }}
        50% {{ transform: translate(50px,40px) scale(1.08); }}
    }}
    @keyframes orbFloat2 {{
        0%,100% {{ transform: translate(0,0) scale(1); }}
        50% {{ transform: translate(-60px,-30px) scale(1.1); }}
    }}
    @keyframes orbFloat3 {{
        0%,100% {{ transform: translate(0,0) scale(1); }}
        50% {{ transform: translate(-30px,50px) scale(0.92); }}
    }}

    .hero-grid {{
        position:relative; z-index:1;
        display:grid; grid-template-columns: 1.15fr 1fr;
        gap: 2.5rem; align-items:center;
    }}
    @media (max-width: 900px) {{ .hero-grid {{ grid-template-columns: 1fr; }} }}

    .badge-row {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom: 1.2rem; }}
    .badge {{
        display:inline-flex; align-items:center; gap:6px;
        font-size:0.7rem; font-weight:600; padding:5px 12px;
        border-radius:999px; font-family:'JetBrains Mono',monospace;
        backdrop-filter: blur(8px);
    }}
    .badge.free {{ background:rgba(52,211,153,0.14); color:{MINT}; border:1px solid rgba(52,211,153,0.3); }}
    .badge.priv {{ background:rgba(139,92,246,0.14); color:{VIOLET}; border:1px solid rgba(139,92,246,0.3); }}
    .badge.live {{ background:rgba(34,211,238,0.14); color:{CYAN}; border:1px solid rgba(34,211,238,0.3); }}
    .badge.live::before {{
        content:''; width:6px; height:6px; border-radius:50%; background:{CYAN};
        box-shadow:0 0 8px {CYAN}; animation: pulse 1.6s infinite;
    }}

    .hero-h1 {{
        font-family:'Space Grotesk',sans-serif;
        font-size: clamp(2rem, 5vw, 3.4rem);
        line-height: 1.05; letter-spacing: -0.025em;
        font-weight: 700; margin: 0 0 14px;
        color: {INK};
    }}
    .hero-h1 .grad {{
        background: linear-gradient(90deg, {VIOLET}, {CYAN}, {MINT});
        -webkit-background-clip: text; background-clip: text;
        color: transparent; background-size: 200% auto;
        animation: gradShift 4s linear infinite;
    }}
    @keyframes gradShift {{ to {{ background-position: 200% center; }} }}
    .hero-sub {{ font-size: 1.05rem; color: {MUTED}; line-height:1.65; margin: 0 0 1.6rem;
                  max-width: 540px; }}

    .cta-row {{ display:flex; gap:12px; flex-wrap:wrap; align-items:center; }}
    .cta-primary, .cta-ghost {{
        display:inline-flex; align-items:center; gap:8px;
        font-size:0.95rem; font-weight:600; padding:13px 26px;
        border-radius:12px; cursor:pointer; transition:all 0.25s;
        font-family: 'Inter',sans-serif; position: relative; overflow: hidden;
    }}
    .cta-primary {{
        background: linear-gradient(135deg, {VIOLET}, {CYAN});
        color: {INK}; border:none; box-shadow: 0 8px 24px -8px {VIOLET};
    }}
    .cta-primary::before {{
        content:''; position:absolute; top:0; left:-100%;
        width:100%; height:100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
        transition: left 0.6s;
    }}
    .cta-primary:hover {{ transform: translateY(-2px); box-shadow: 0 14px 36px -8px {VIOLET}; }}
    .cta-primary:hover::before {{ left: 100%; }}
    .cta-ghost {{
        background: transparent; color: {INK};
        border: 1px solid {BORDER};
    }}
    .cta-ghost:hover {{ border-color: {VIOLET}; color: {INK}; background:rgba(139,92,246,0.06); }}

    .trust-line {{ display:flex; gap:18px; margin-top: 1.4rem; flex-wrap:wrap;
                    font-size: 0.78rem; color: {C['faint']}; }}
    .trust-line span {{ display:inline-flex; align-items:center; gap:5px; }}

    /* ── Live Preview Tile w/ shimmer + animated ring ─────────────── */
    .preview-tile {{
        background: {GLASS}; backdrop-filter: blur(14px);
        border: 1px solid {BORDER}; border-radius: 18px;
        padding: 1.2rem 1.3rem; position:relative; overflow:hidden;
    }}
    .preview-tile::before {{
        content:''; position:absolute; inset:0; border-radius:18px; padding:1px;
        background: linear-gradient(135deg, rgba(139,92,246,0.5), transparent 50%, rgba(34,211,238,0.3));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
        pointer-events:none;
    }}
    .preview-tile::after {{
        content:''; position:absolute; top:-50%; left:-50%;
        width:60%; height:200%;
        background: linear-gradient(115deg, transparent, rgba(139,92,246,0.06), transparent);
        animation: shimmer 6s ease-in-out infinite;
        pointer-events:none;
    }}
    @keyframes shimmer {{
        0%,100% {{ transform: translateX(-100%) rotate(0deg); }}
        50% {{ transform: translateX(220%) rotate(0deg); }}
    }}

    /* Health score mini-ring */
    .mini-ring {{ display:flex; align-items:center; gap:14px; margin-bottom: 14px; }}
    .mini-ring-svg circle.fg {{
        stroke-dasharray: 0 264;
        animation: ringFill 1.6s cubic-bezier(0.22, 1, 0.36, 1) 0.5s forwards;
        filter: drop-shadow(0 0 6px {VIOLET});
    }}
    @keyframes ringFill {{ to {{ stroke-dasharray: 219 264; }} }}

    /* Asset bars rising */
    .asset-bar {{ height: 32px; border-radius: 6px; transform-origin: bottom;
                   animation: barRise 0.9s cubic-bezier(0.22, 1, 0.36, 1) both; }}
    @keyframes barRise {{ from {{ transform: scaleY(0); opacity: 0; }} to {{ transform: scaleY(1); opacity: 1; }} }}

    /* ── Live counter ────────────────────────────────────────────── */
    .counter-strip {{
        display:grid; grid-template-columns: repeat(4, 1fr);
        gap: 10px; padding: 1.4rem 0;
        border-top: 1px solid {BORDER}; border-bottom: 1px solid {BORDER};
        margin: 3rem 0;
    }}
    @media (max-width: 700px) {{ .counter-strip {{ grid-template-columns: repeat(2, 1fr); gap:18px; }} }}
    .counter-cell {{ text-align:center; }}
    .counter-num {{ font-family:'JetBrains Mono',monospace; font-size: 1.85rem;
                      font-weight:700; color:{INK}; line-height:1; }}
    .counter-num.grad {{ background: linear-gradient(90deg, {VIOLET}, {CYAN});
                          -webkit-background-clip:text; background-clip:text; color:transparent; }}
    .counter-lbl {{ font-size:0.66rem; color:{MUTED}; letter-spacing:0.1em;
                     text-transform:uppercase; margin-top:5px; }}

    /* ── Feature grid w/ aurora border on hover ─────────────────── */
    .feat-grid {{ display:grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }}
    @media (max-width: 900px) {{ .feat-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    @media (max-width: 600px) {{ .feat-grid {{ grid-template-columns: 1fr; }} }}

    .feat-card {{
        background: {GLASS}; backdrop-filter: blur(12px);
        border: 1px solid {BORDER}; border-radius: 14px;
        padding: 1.2rem 1.3rem;
        transition: transform .3s, border-color .3s, box-shadow .3s;
        position:relative; overflow:hidden;
    }}
    .feat-card::before {{
        content:''; position:absolute; inset:0; border-radius:14px;
        background: linear-gradient(135deg, transparent, rgba(139,92,246,0.12), transparent);
        opacity: 0; transition: opacity 0.3s; pointer-events:none;
    }}
    .feat-card:hover {{
        transform: translateY(-6px); border-color: rgba(139,92,246,0.45);
        box-shadow: 0 18px 50px -16px rgba(139,92,246,0.5);
    }}
    .feat-card:hover::before {{ opacity: 1; }}
    .feat-icon {{
        width:42px; height:42px; border-radius:12px;
        display:flex; align-items:center; justify-content:center;
        font-size:1.3rem; margin-bottom:14px;
        transition: transform 0.3s;
    }}
    .feat-card:hover .feat-icon {{ transform: scale(1.1) rotate(-3deg); }}
    .feat-title {{ font-size:1rem; font-weight:600; color:{INK}; margin: 0 0 6px;
                    font-family:'Space Grotesk',sans-serif; }}
    .feat-desc {{ font-size:0.82rem; color:{MUTED}; line-height:1.6; margin:0; }}

    /* Section heading */
    .sec-h {{
        font-family:'Space Grotesk',sans-serif; font-size: 1.6rem;
        font-weight: 700; letter-spacing: -0.02em; color:{INK};
        margin: 3rem 0 0.4rem; text-align:center;
    }}
    .sec-h .grad {{
        background: linear-gradient(90deg, {VIOLET}, {CYAN});
        -webkit-background-clip:text; background-clip:text; color:transparent;
    }}
    .sec-sub {{ text-align:center; color:{MUTED}; font-size:0.88rem;
                  margin-bottom: 1.8rem; }}

    /* How it works steps */
    .steps {{
        display:grid; grid-template-columns: repeat(4, 1fr); gap: 1px;
        background: {BORDER}; border: 1px solid {BORDER};
        border-radius: 16px; overflow:hidden; position: relative;
    }}
    @media (max-width: 800px) {{ .steps {{ grid-template-columns: repeat(2, 1fr); }} }}
    .step {{ background: {VOID}; padding: 1.4rem 1.3rem; transition: background .3s; position:relative; }}
    .step:hover {{ background: {GLASS}; }}
    .step-num {{
        width: 32px; height: 32px; border-radius: 50%;
        background: linear-gradient(135deg, {VIOLET}, {CYAN});
        display:flex; align-items:center; justify-content:center;
        font-family:'JetBrains Mono',monospace; font-weight:700;
        font-size:0.9rem; color: {INK}; margin-bottom: 12px;
        box-shadow: 0 4px 16px -4px {VIOLET};
        transition: transform 0.3s, box-shadow 0.3s;
    }}
    .step:hover .step-num {{ transform: scale(1.15); box-shadow: 0 6px 22px -4px {VIOLET}; }}
    .step-title {{ font-weight:600; font-size:0.95rem; color:{INK}; margin: 0 0 6px;
                     font-family:'Space Grotesk',sans-serif; }}
    .step-desc {{ font-size:0.78rem; color:{MUTED}; line-height:1.55; margin:0; }}

    /* FAQ */
    .faq-item {{
        background: {GLASS}; border: 1px solid {BORDER};
        border-radius: 12px; padding: 0; margin-bottom: 8px;
        overflow:hidden; transition: border-color .25s, background .25s;
    }}
    .faq-item:hover {{ border-color: rgba(139,92,246,0.35); background: rgba(139,92,246,0.04); }}
    .faq-item summary {{
        padding: 1rem 1.2rem; cursor:pointer; font-weight:600;
        font-size:0.92rem; color:{INK}; list-style:none;
        display:flex; align-items:center; justify-content:space-between;
    }}
    .faq-item summary::-webkit-details-marker {{ display:none; }}
    .faq-item summary::after {{
        content:'+'; font-size:1.4rem; color:{VIOLET}; font-weight:300;
        transition: transform .25s;
    }}
    .faq-item[open] summary::after {{ transform: rotate(45deg); }}
    .faq-body {{ padding: 0 1.2rem 1rem; font-size:0.86rem; color:{MUTED}; line-height:1.65; }}

    /* Trust strip */
    .trust-card {{
        background: linear-gradient(135deg, rgba(52,211,153,0.06), rgba(139,92,246,0.06));
        border: 1px solid rgba(52,211,153,0.25);
        border-radius: 16px; padding: 1.5rem 1.8rem;
        display:flex; gap:1.4rem; align-items:center; margin: 2rem 0;
    }}
    @media (max-width: 600px) {{ .trust-card {{ flex-direction:column; text-align:center; }} }}
    .trust-icon {{ font-size: 2.8rem; flex-shrink:0;
                    animation: shieldPulse 3s ease-in-out infinite; }}
    @keyframes shieldPulse {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.08); }} }}
    .trust-text h3 {{ margin: 0 0 6px; font-size:1.05rem; font-weight:700;
                       font-family:'Space Grotesk',sans-serif; color:{INK}; }}
    .trust-text p {{ margin:0; font-size:0.86rem; color:{MUTED}; line-height:1.65; }}

    /* Final CTA */
    .final-cta {{
        text-align:center; padding: 3.5rem 1rem 2rem; margin-top: 2rem;
        position:relative;
    }}
    .final-cta::before {{
        content:''; position:absolute; top:0; left:50%; transform:translateX(-50%);
        width: 60%; height: 1px;
        background: linear-gradient(90deg, transparent, {VIOLET}, transparent);
    }}
    .final-h2 {{ font-family:'Space Grotesk',sans-serif; font-size: 2.1rem;
                  font-weight:700; letter-spacing:-0.02em;
                  background: linear-gradient(90deg, {INK}, {CYAN});
                  -webkit-background-clip:text; background-clip:text; color:transparent;
                  margin: 0 0 10px; }}
    .final-sub {{ color:{MUTED}; font-size:0.95rem; margin: 0 0 1.6rem; }}

    .typing-cursor {{ display:inline-block; width:3px; height:1em;
                       background: {CYAN}; margin-left: 4px; vertical-align: -2px;
                       animation: blink 1s infinite; }}
    @keyframes blink {{ 50% {{ opacity:0; }} }}
    </style>"""), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
def _render_hero():
    ring_svg = H(f"""
    <svg class="mini-ring-svg" width="64" height="64" viewBox="0 0 84 84" style="transform:rotate(-90deg)">
    <defs>
    <linearGradient id="hgR" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="{VIOLET}"/><stop offset="100%" stop-color="{CYAN}"/>
    </linearGradient>
    </defs>
    <circle cx="42" cy="42" r="35" fill="none" stroke="rgba(139,92,246,0.15)" stroke-width="6"/>
    <circle class="fg" cx="42" cy="42" r="35" fill="none" stroke="url(#hgR)"
     stroke-width="6" stroke-linecap="round"/>
    </svg>""")

    bars_html = ""
    bar_data = [
        (VIOLET, 96, "Equity"),
        (CYAN,   72, "Gold"),
        (MINT,   54, "Hybrid"),
        (AMBER,  38, "Debt"),
        (VIOLET, 22, "Intl"),
    ]
    for i, (col, h, _) in enumerate(bar_data):
        bars_html += (f'<div class="asset-bar" style="background:linear-gradient(180deg,{col},{col}88);'
                      f'height:{h}px;animation-delay:{0.7 + i*0.12}s;"></div>')

    st.markdown(H(f"""
    <div class="hero-wrap">
    <div class="hero-orb-1"></div><div class="hero-orb-2"></div><div class="hero-orb-3"></div>
    <div class="hero-grid">

    <div class="reveal show">
    <div class="badge-row">
    <span class="badge free">✓ 100% free forever</span>
    <span class="badge priv">🔒 zero data stored</span>
    <span class="badge live">live NAVs</span>
    </div>
    <h1 class="hero-h1">Your CAS,<br/><span class="grad" id="typeword">decoded</span>.<br/>
    <span style="color:{MUTED};font-size:0.62em;font-weight:500;">In 6 seconds.</span></h1>
    <p class="hero-sub">SipCheck reads your Consolidated Account Statement and turns it into the
    dashboard CAMS forgot to build — live NAVs, health score, SIP watchdog, tax lens,
    rebalancer, and a 58-fund research desk.
    <b style="color:{INK};">No signup. No tracking. Nothing leaves your browser.</b></p>
    <div class="cta-row">
    <button class="cta-primary" onclick="window.scrollTo({{top: document.body.scrollHeight, behavior:'smooth'}});">↓  Upload CAS now</button>
    <a class="cta-ghost" href="#how">▶  See how it works</a>
    </div>
    <div class="trust-line">
    <span>⏱  6-second parse</span>
    <span>🔒  zero retention</span>
    <span>💳  no card · no email</span>
    <span>📱  mobile-ready</span>
    </div>
    </div>

    <div class="preview-tile reveal show reveal-delay-2">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <span style="font-size:0.62rem;letter-spacing:0.18em;color:{MUTED};font-weight:600;">LIVE PREVIEW · WHAT YOU'LL SEE</span>
    <span class="badge live" style="font-size:0.6rem;padding:3px 9px;">JUST NOW</span>
    </div>

    <div class="mini-ring">
    {ring_svg}
    <div>
    <div style="display:flex;align-items:baseline;gap:8px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:1.7rem;font-weight:700;color:{INK};">₹4,28,540</span>
    <span style="font-size:0.78rem;color:{MINT};font-weight:600;">▲ 14.2%</span>
    </div>
    <div style="font-size:0.66rem;color:{C['faint']};margin-top:2px;font-family:'JetBrains Mono',monospace;">
    Health <b style="color:{MINT};">A · 83</b> · wtd XIRR <b style="color:{MINT};">16.8%</b> · 7 funds
    </div>
    </div>
    </div>

    <div style="display:flex;align-items:flex-end;gap:6px;height:96px;margin:8px 0 12px;padding:8px 4px 0;
         border-top:1px solid rgba(139,92,246,0.1);border-bottom:1px solid rgba(139,92,246,0.1);">
    {bars_html}
    </div>

    <div style="background:rgba(248,113,113,0.08);border-left:3px solid {EMBER};
         padding:9px 11px;border-radius:8px;font-size:0.72rem;color:{INK};margin-bottom:6px;">
    <b style="color:{EMBER};">🔴 SIP overdue</b> · HDFC Small Cap · last debit 35 days ago
    </div>
    <div style="background:rgba(52,211,153,0.08);border-left:3px solid {MINT};
         padding:9px 11px;border-radius:8px;font-size:0.72rem;color:{INK};">
    <b style="color:{MINT};">✅ Goal probability</b> · 76% chance of ₹50L in 12 yrs
    </div>

    <div style="display:flex;justify-content:space-between;margin-top:12px;padding-top:10px;
         border-top:1px solid rgba(139,92,246,0.1);font-size:0.62rem;color:{MUTED};
         font-family:'JetBrains Mono',monospace;">
    <span>💰 Monthly SIP <b style="color:{INK};">₹12,500</b></span>
    <span>⚡ 9 active</span>
    </div>
    </div>
    </div>
    </div>

    <script>
    (function(){{
      const w = document.getElementById('typeword');
      if(!w) return;
      const words = ['decoded', 'understood', 'beautiful', 'alive'];
      let i = 0;
      setInterval(() => {{ i = (i + 1) % words.length; w.textContent = words[i]; }}, 2400);
    }})();
    </script>
    """), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
def _render_stat_strip():
    st.markdown(H(f"""
    <div class="counter-strip reveal">
    <div class="counter-cell"><div class="counter-num grad" data-target="3000" data-suffix="+">0</div>
    <div class="counter-lbl">CAS files parsed</div></div>
    <div class="counter-cell"><div class="counter-num" data-target="58">0</div>
    <div class="counter-lbl">funds tracked live</div></div>
    <div class="counter-cell"><div class="counter-num" data-target="6" data-suffix=" sec">0</div>
    <div class="counter-lbl">avg parse time</div></div>
    <div class="counter-cell"><div class="counter-num grad">₹0</div>
    <div class="counter-lbl">ever charged</div></div>
    </div>
    <script>
    (function(){{
      function runCounters(root) {{
        const els = root.querySelectorAll('.counter-num[data-target]:not(.done)');
        els.forEach(el => {{
          el.classList.add('done');
          const target = parseInt(el.dataset.target);
          const suffix = el.dataset.suffix || '';
          const start = Date.now(); const dur = 1600;
          function step() {{
            const t = Math.min(1, (Date.now()-start)/dur);
            const eased = 1 - Math.pow(1-t, 3);
            const val = Math.round(target * eased);
            el.textContent = (val >= 1000 ? val.toLocaleString('en-IN') : val) + suffix;
            if (t < 1) requestAnimationFrame(step);
          }}
          step();
        }});
      }}
      const strip = document.querySelector('.counter-strip');
      if (!strip) return;
      const io = new IntersectionObserver((entries) => {{
        entries.forEach(e => {{ if (e.isIntersecting) runCounters(strip); }});
      }}, {{ threshold: 0.3 }});
      io.observe(strip);
    }})();
    </script>
    """), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
def _render_features():
    feats = [
        ("🎯", VIOLET, "Health Score",
         "An A+ to D grade on diversification, returns, balance, and SIP discipline — your portfolio's report card in one number."),
        ("🔔", MINT, "SIP Watchdog",
         "Catches missed, overdue, and stopped SIPs automatically — with the exact rupee cost of every skipped instalment."),
        ("⚡", CYAN, "Live NAV Engine",
         "One click pulls today's NAV for every fund from AMFI. Your portfolio re-values instantly — no manual entry, ever."),
        ("🔮", AMBER, "Wealth Time Machine",
         "1,000 simulated futures show the odds of hitting your money goals — based on YOUR actual SIPs and returns."),
        ("⚖️", VIOLET, "Smart Rebalancer",
         "Pick a target mix (aggressive/balanced/conservative). Get the exact ₹ amount to add or trim per bucket."),
        ("🔬", CYAN, "58-Fund Research Desk",
         "Live CAGR, max drawdown, calendar returns, Direct vs Regular gap. Plus request any of 10,000+ schemes."),
    ]
    cards = "".join(H(f"""
    <div class="feat-card reveal reveal-delay-{(i % 6) + 1}">
    <div class="feat-icon" style="background:linear-gradient(135deg,{color}22,{color}11);
         border:1px solid {color}44;">{icon}</div>
    <div class="feat-title">{title}</div>
    <p class="feat-desc">{desc}</p>
    </div>""") for i, (icon, color, title, desc) in enumerate(feats))

    st.markdown(H(f"""
    <div class="sec-h reveal">Everything your CAS PDF <span class="grad">can't tell you</span></div>
    <div class="sec-sub reveal reveal-delay-1">Six features that turn a static statement into a living dashboard.</div>
    <div class="feat-grid">{cards}</div>
    """), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
def _render_how_it_works():
    st.markdown(H(f"""
    <div id="how" class="sec-h reveal">From PDF to <span class="grad">insight</span></div>
    <div class="sec-sub reveal reveal-delay-1">Four steps. Six seconds. Zero friction.</div>
    <div class="steps reveal">
    <div class="step">
    <div class="step-num">1</div>
    <div class="step-title">Request your CAS</div>
    <p class="step-desc">Get the Consolidated Account Statement from
    <b style="color:{INK};">CAMS</b> or <b style="color:{INK};">KFintech</b>.
    Arrives by email as a password-protected PDF.</p>
    </div>
    <div class="step">
    <div class="step-num">2</div>
    <div class="step-title">Drop &amp; unlock</div>
    <p class="step-desc">Upload the PDF here, enter your <b style="color:{INK};">PAN or DOB</b>
    as password. Parsing happens entirely in your browser tab.</p>
    </div>
    <div class="step">
    <div class="step-num">3</div>
    <div class="step-title">Instant dashboard</div>
    <p class="step-desc">Health score, holdings, SIPs, alerts, tax lens and
    rebalancer — all generated in seconds. No waiting, no signup.</p>
    </div>
    <div class="step">
    <div class="step-num">4</div>
    <div class="step-title">Refresh anytime</div>
    <p class="step-desc">One click pulls today's NAVs from AMFI.
    Your portfolio updates live, every market day.</p>
    </div>
    </div>"""), unsafe_allow_html=True)


def _render_live_preview():
    pass


# ───────────────────────────────────────────────────────────────────
def _render_trust():
    st.markdown(H(f"""
    <div class="trust-card reveal">
    <div class="trust-icon">🛡️</div>
    <div class="trust-text">
    <h3>Why investors trust SipCheck</h3>
    <p>Your CAS is parsed <b style="color:{INK};">entirely inside your browser tab</b>.
    We have no servers, no database, no analytics on your financial data. Close the tab
    and everything is gone. Zero signup. Zero tracking. Zero ads. Zero affiliate links.
    Built by an investor, for investors.</p>
    </div>
    </div>"""), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
def _render_faq():
    faqs = [
        ("Is my financial data safe?",
         "Yes — 100%. SipCheck has no backend that touches your portfolio. Your CAS PDF is "
         "parsed in your browser tab using Streamlit running locally in the session. When you "
         "close the tab, everything is wiped. Nothing is logged, stored, or sent."),
        ("Where do live NAVs come from?",
         "From <b>mfapi.in</b>, a free public mirror of the official AMFI India daily NAV file. "
         "We never see what you query — your browser talks to it directly."),
        ("Do I need to sign up or pay?",
         "No to both. SipCheck is 100% free forever. No card, no email, no Google sign-in. "
         "Just upload and use. We make no money from this — it's a personal project."),
        ("How accurate is the data?",
         "All numbers (units, invested amounts, transaction history) come straight from your "
         "CAS — which is the official source of truth from CAMS/KFintech. Returns, XIRR, and "
         "drawdowns are computed locally from that data."),
        ("Can I use this on my phone?",
         "Yes — SipCheck is fully mobile-responsive. Tabs scroll horizontally, cards stack, "
         "all touch targets are 44px+. Works in any modern browser."),
        ("What if my fund isn't in the 58-fund library?",
         "Use the <b>Request a Scheme</b> search in MF Report Pro — it searches all 10,000+ "
         "AMFI schemes and generates an instant report. If nothing matches, your request gets "
         "logged as 'available soon'."),
    ]
    items = "".join(H(f"""
    <details class="faq-item reveal reveal-delay-{(i % 6) + 1}">
    <summary>{q}</summary>
    <div class="faq-body">{a}</div>
    </details>""") for i, (q, a) in enumerate(faqs))
    st.markdown(H(f"""
    <div class="sec-h reveal">Common <span class="grad">questions</span></div>
    <div class="sec-sub reveal reveal-delay-1">The things every new visitor asks.</div>
    <div style="max-width:780px;margin:0 auto;">{items}</div>
    """), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────
def _render_final_cta():
    st.markdown(H(f"""
    <div class="final-cta reveal">
    <div class="final-h2">See your portfolio the way it really is.</div>
    <div class="final-sub">Free forever · No signup · 6 seconds to your first insight</div>
    <button class="cta-primary" style="font-size:1.05rem;padding:15px 36px;"
     onclick="window.scrollTo({{top: document.body.scrollHeight, behavior:'smooth'}});">
    ↓  Upload your CAS now
    </button>
    <div style="margin-top:1.4rem;font-size:0.7rem;color:{C['faint']};">
    SipCheck v2.4 · Built for Indian mutual fund investors · Data never leaves your device
    </div>
    </div>

    <!-- ── LASER BEAM SCROLL PROGRESS + REVEAL-ON-SCROLL ── -->
    <div class="scroll-beam"></div>

    <script>
    (function(){{
      // Laser beam scroll progress
      const beam = document.querySelector('.scroll-beam');
      if (beam) {{
        const update = () => {{
          const doc = document.documentElement;
          const max = (doc.scrollHeight - window.innerHeight) || 1;
          const pct = Math.min(100, Math.max(0, (window.scrollY / max) * 100));
          beam.style.setProperty('--scroll', (pct * 0.78) + '%');
          beam.style.setProperty('--scroll-y', pct + 'vh');
        }};
        window.addEventListener('scroll', update, {{ passive: true }});
        update();
      }}

      // Reveal sections as they enter viewport
      const reveal = (root) => {{
        const els = (root || document).querySelectorAll('.reveal:not(.show)');
        if (!els.length) return;
        const io = new IntersectionObserver((entries) => {{
          entries.forEach(e => {{
            if (e.isIntersecting) {{
              e.target.classList.add('show');
              io.unobserve(e.target);
            }}
          }});
        }}, {{ threshold: 0.12, rootMargin: '0px 0px -8% 0px' }});
        els.forEach(el => io.observe(el));
      }};
      reveal();
      setTimeout(reveal, 400);
      setTimeout(reveal, 1200);

      // Parallax orbs follow scroll subtly
      const o1 = document.querySelector('.hero-orb-1');
      const o2 = document.querySelector('.hero-orb-2');
      const o3 = document.querySelector('.hero-orb-3');
      if (o1 || o2 || o3) {{
        window.addEventListener('scroll', () => {{
          const y = window.scrollY;
          if (o1) o1.style.transform = `translateY(${{y * 0.15}}px)`;
          if (o2) o2.style.transform = `translateY(${{y * -0.1}}px)`;
          if (o3) o3.style.transform = `translateY(${{y * 0.2}}px)`;
        }}, {{ passive: true }});
      }}
    }})();
    </script>
    """), unsafe_allow_html=True)
