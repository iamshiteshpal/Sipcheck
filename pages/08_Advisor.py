# ──────────────────────────────────────────────────────────────────
#  CAS 360 v2.0 – AI ADVISOR  (pages/08_Advisor.py)
#  Reads the SAME session data dashboard.py creates
#  (st.session_state.profiles[active]), falls back to demo data.
#
#  Features:
#   1. Portfolio Health Score – animated orbital ring (0-100 + grade)
#   2. Five sub-scores: Diversification · Concentration · Returns ·
#      Category Balance · SIP Discipline
#   3. Risk Radar
#   4. Concentration treemap + auto-generated warnings
#   5. Smart Rebalancing engine (exact Rs. to move, per category)
#   6. Monte Carlo wealth simulator – 1,000 future paths, fan chart
#   7. Rule-engine written portfolio review (no API needed)
# ──────────────────────────────────────────────────────────────────
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os, math
from datetime import datetime

st.set_page_config(page_title="Advisor · CAS 360", page_icon="🧠", layout="wide")

# ── theme (shared 2.0 design system) ──────────────────────────────
try:
    from ui_theme import inject_theme, glass_kpi, page_header, section, C
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ui_theme import inject_theme, glass_kpi, page_header, section, C

inject_theme()

VIOLET, CYAN, MINT, EMBER, AMBER = C["violet"], C["cyan"], C["mint"], C["ember"], C["amber"]
MUTED, INK = C["muted"], C["ink"]

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=MUTED, size=11, family="Inter"),
    margin=dict(l=10, r=10, t=24, b=10),
)

# ─────────────────────────────────────────────────────────────────
#  DATA – reuse the dashboard's parsed CAS, else demo
# ─────────────────────────────────────────────────────────────────
def get_portfolio():
    active = st.session_state.get("active")
    profiles = st.session_state.get("profiles", {})
    if active and active in profiles:
        return profiles[active], True

    demo_holdings = [
        dict(scheme="Motilal Oswal Midcap Fund",        value=98000, invested=85000, xirr=21.4, category="Equity Funds"),
        dict(scheme="Parag Parikh Flexi Cap Fund",      value=45200, invested=42000, xirr=14.2, category="Equity Funds"),
        dict(scheme="HDFC Gold ETF Fund of Fund",       value=41800, invested=30500, xirr=18.9, category="Gold & Commodities"),
        dict(scheme="SBI Gold Fund",                    value=40100, invested=29500, xirr=17.8, category="Gold & Commodities"),
        dict(scheme="HDFC Small Cap Fund",              value=28900, invested=27500, xirr=9.1,  category="Equity Funds"),
        dict(scheme="Kotak Large Cap Fund",             value=20400, invested=19500, xirr=8.4,  category="Equity Funds"),
        dict(scheme="Invesco India Midcap Fund",        value=7100,  invested=6500,  xirr=12.6, category="Equity Funds"),
        dict(scheme="HDFC Silver ETF Fund of Fund",     value=7064,  invested=6500,  xirr=11.2, category="Gold & Commodities"),
    ]
    tv = sum(h["value"] for h in demo_holdings)
    ti = sum(h["invested"] for h in demo_holdings)
    alloc = {}
    for h in demo_holdings:
        alloc[h["category"]] = alloc.get(h["category"], 0) + h["value"]
    return dict(
        investor_name="Sanjay", statement_date="22 MAY 2026",
        total_value=tv, total_invested=ti, unrealized_pnl=tv - ti,
        holdings=demo_holdings, alloc_values=alloc,
        alloc_pct={k: v / tv * 100 for k, v in alloc.items()},
        live_sips=[{"amount": 8999.57}] * 9,
    ), False


data, is_real = get_portfolio()
holdings = sorted(data.get("holdings", []), key=lambda h: -h.get("value", 0))
TV = data.get("total_value", 0) or 1
TI = data.get("total_invested", 0) or 1
PNL = data.get("unrealized_pnl", TV - TI)

# ─────────────────────────────────────────────────────────────────
#  HEALTH SCORE ENGINE – five sub-scores, each 0-100
# ─────────────────────────────────────────────────────────────────
def compute_scores(holdings, alloc_pct, live_sips):
    n = len(holdings)
    weights = [h["value"] / TV for h in holdings] if holdings else [1.0]

    # 1) Diversification – fund count, sweet spot 6-12
    if   n >= 6 and n <= 12: s_div = 100
    elif n < 6:              s_div = max(20, n / 6 * 90)
    else:                    s_div = max(40, 100 - (n - 12) * 6)

    # 2) Concentration – Herfindahl index of fund weights
    hhi = sum(w * w for w in weights)
    ideal = 1 / max(n, 1)
    s_con = max(0, min(100, 100 - (hhi - ideal) * 400))

    # 3) Returns – weighted XIRR vs 12% benchmark
    xirrs = [(h.get("xirr") or 0, h["value"]) for h in holdings if h.get("xirr")]
    wx = sum(x * v for x, v in xirrs) / sum(v for _, v in xirrs) if xirrs else 0
    s_ret = max(0, min(100, 50 + (wx - 12) * 5))

    # 4) Category balance – penalise any bucket > 75% or commodities > 25%
    s_bal = 100.0
    for cat, pct in (alloc_pct or {}).items():
        if pct > 75: s_bal -= (pct - 75) * 2
        if "gold" in cat.lower() and pct > 25: s_bal -= (pct - 25) * 2.5
    s_bal = max(0, s_bal)

    # 5) SIP discipline – active SIP flow vs portfolio size (annualised %)
    sip_monthly = sum(s.get("amount", 0) for s in (live_sips or []))
    flow = (sip_monthly * 12) / TV * 100
    s_sip = max(0, min(100, flow * 2.2))

    subs = {
        "Diversification":  round(s_div),
        "Concentration":    round(s_con),
        "Returns":          round(s_ret),
        "Category Balance": round(s_bal),
        "SIP Discipline":   round(s_sip),
    }
    total = round(sum(subs.values()) / 5)
    return total, subs, wx, hhi, sip_monthly


score, subs, wxirr, hhi, sip_monthly = compute_scores(
    holdings, data.get("alloc_pct", {}), data.get("live_sips", []))


def grade(s):
    return ("A+", MINT)  if s >= 85 else \
           ("A",  MINT)  if s >= 75 else \
           ("B",  CYAN)  if s >= 60 else \
           ("C",  AMBER) if s >= 45 else \
           ("D",  EMBER)


g_letter, g_color = grade(score)

# ─────────────────────────────────────────────────────────────────
#  HERO – orbital ring (the 2.0 signature element)
# ─────────────────────────────────────────────────────────────────
demo_note = "" if is_real else " · demo data — upload a CAS to go live"
page_header(
    "Advisor Intelligence",
    f"Portfolio intelligence for {data.get('investor_name', 'Investor')} · "
    f"CAS {data.get('statement_date', '')}{demo_note}",
    live=is_real,
)

circumference = 2 * math.pi * 84
dash = circumference * score / 100

sub_bars = "".join(f"""
    <div>
      <div style="display:flex;justify-content:space-between;font-size:0.72rem;margin-bottom:4px;">
        <span style="color:{MUTED}">{k}</span>
        <span class="num" style="color:{grade(v)[1]};font-weight:600">{v}</span>
      </div>
      <div style="height:5px;background:rgba(139,92,246,0.12);border-radius:3px;overflow:hidden;">
        <div style="height:100%;width:{v}%;border-radius:3px;
             background:linear-gradient(90deg,{VIOLET},{grade(v)[1]});
             box-shadow:0 0 8px {grade(v)[1]}66;"></div>
      </div>
    </div>""" for k, v in subs.items())

ring_html = f"""
<div class="g-card rise" style="display:flex;align-items:center;gap:2.2rem;padding:1.6rem 2rem;">
  <div style="position:relative;width:200px;height:200px;flex-shrink:0;">
    <svg width="200" height="200" viewBox="0 0 200 200" style="transform:rotate(-90deg)">
      <defs>
        <linearGradient id="ringG" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{VIOLET}"/><stop offset="60%" stop-color="{CYAN}"/>
          <stop offset="100%" stop-color="{MINT}"/>
        </linearGradient>
      </defs>
      <circle cx="100" cy="100" r="84" fill="none" stroke="rgba(139,92,246,0.12)" stroke-width="10"/>
      <circle cx="100" cy="100" r="84" fill="none" stroke="url(#ringG)" stroke-width="10"
        stroke-linecap="round" stroke-dasharray="{dash:.0f} {circumference:.0f}"
        style="filter:drop-shadow(0 0 10px rgba(139,92,246,0.6));">
        <animate attributeName="stroke-dasharray" from="0 {circumference:.0f}"
                 to="{dash:.0f} {circumference:.0f}" dur="1.4s"
                 calcMode="spline" keySplines="0.22 1 0.36 1" fill="freeze"/>
      </circle>
      <circle cx="100" cy="16" r="5" fill="{CYAN}">
        <animateTransform attributeName="transform" type="rotate"
          from="0 100 100" to="{score * 3.6:.0f} 100 100" dur="1.4s"
          calcMode="spline" keySplines="0.22 1 0.36 1" fill="freeze"/>
      </circle>
    </svg>
    <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
      <div class="num" style="font-size:2.6rem;font-weight:700;color:{INK};line-height:1;">{score}</div>
      <div style="font-size:0.65rem;letter-spacing:0.15em;color:{MUTED};margin-top:2px;">HEALTH SCORE</div>
      <div class="num" style="font-size:0.95rem;font-weight:700;color:{g_color};margin-top:4px;">GRADE {g_letter}</div>
    </div>
  </div>
  <div style="flex:1;display:grid;grid-template-columns:1fr 1fr;gap:0.55rem 2rem;">
    {sub_bars}
    <div style="align-self:end;">
      <span class="pill">wtd XIRR <b class="num" style="color:{MINT if wxirr >= 12 else AMBER};margin-left:4px">{wxirr:.1f}%</b></span>
      <span class="pill" style="margin-left:6px">{len(holdings)} funds</span>
    </div>
  </div>
</div>"""
st.markdown(ring_html, unsafe_allow_html=True)

# ── KPI strip ──────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
pnl_pct = PNL / TI * 100 if TI else 0
with k1: glass_kpi("Total Wealth",     f"₹{TV:,.0f}",       f"invested ₹{TI:,.0f}", "", 1)
with k2: glass_kpi("Unrealized P&L",   f"₹{PNL:,.0f}",
                   f"{'▲' if PNL >= 0 else '▼'} {abs(pnl_pct):.2f}% all-time",
                   "up" if PNL >= 0 else "down", 2)
with k3: glass_kpi("Weighted XIRR",    f"{wxirr:.2f}%",     "benchmark 12.00%",
                   "up" if wxirr >= 12 else "warn", 3)
with k4: glass_kpi("Monthly SIP Flow", f"₹{sip_monthly:,.0f}",
                   f"{len(data.get('live_sips', []))} active mandates", "up", 4)

# ─────────────────────────────────────────────────────────────────
#  RISK RADAR  +  CONCENTRATION TREEMAP
# ─────────────────────────────────────────────────────────────────
left, right = st.columns([1, 1.3])

with left:
    section("Risk Radar")
    axes = list(subs.keys())
    vals = list(subs.values())
    fig = go.Figure(go.Scatterpolar(
        r=vals + vals[:1], theta=axes + axes[:1], fill="toself",
        line=dict(color=VIOLET, width=2),
        fillcolor="rgba(139,92,246,0.18)",
        hovertemplate="%{theta}: %{r}<extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[70] * 6, theta=axes + axes[:1], mode="lines",
        line=dict(color="rgba(52,211,153,0.45)", dash="dot", width=1),
        hoverinfo="skip", name="healthy line",
    ))
    fig.update_layout(**PLOT_LAYOUT, height=330, showlegend=False,
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], gridcolor="rgba(139,92,246,0.12)",
                            tickfont=dict(size=8, color=MUTED)),
            angularaxis=dict(gridcolor="rgba(139,92,246,0.12)",
                             tickfont=dict(size=10, color=INK))))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with right:
    section("Concentration Map")
    df = pd.DataFrame([{
        "fund": h["scheme"][:34],
        "cat":  h.get("category", "Other"),
        "value": h["value"],
        "w":    h["value"] / TV * 100,
        "xirr": h.get("xirr") or 0,
    } for h in holdings])
    fig = go.Figure(go.Treemap(
        labels=df["fund"], parents=df["cat"],
        values=df["value"],
        marker=dict(
            colors=df["xirr"],
            colorscale=[[0, EMBER], [0.5, "#1e2338"], [1, MINT]],
            cmid=10,
            line=dict(color="#070714", width=2),
        ),
        customdata=np.stack([df["w"], df["xirr"]], axis=-1),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "₹%{value:,.0f} · %{customdata[0]:.1f}% of portfolio"
            "<br>XIRR %{customdata[1]:.1f}%<extra></extra>"
        ),
        textfont=dict(family="Inter", size=11, color=INK),
    ))
    fig.update_layout(**PLOT_LAYOUT, height=330)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Auto-warnings
warnings = []
for h in holdings:
    w = h["value"] / TV * 100
    if w > 30:
        warnings.append(f"⚠️ **{h['scheme'][:40]}** is **{w:.1f}%** of your portfolio — single-fund risk.")
for cat, pct in data.get("alloc_pct", {}).items():
    if "gold" in cat.lower() and pct > 25:
        warnings.append(f"⚠️ **{cat}** at **{pct:.1f}%** — commodities above the 25% comfort zone.")
laggards = [h for h in holdings if (h.get("xirr") or 99) < 8 and h["value"] > TV * 0.05]
for h in laggards[:2]:
    warnings.append(f"📉 **{h['scheme'][:40]}** XIRR is only **{h.get('xirr', 0):.1f}%** — review or switch.")

if warnings:
    section("Advisor Flags")
    for w in warnings[:4]:
        # convert **bold** markers to HTML
        txt = w
        for _ in range(2):
            txt = txt.replace("**", "<b>", 1).replace("**", "</b>", 1)
        st.markdown(
            f'<div class="g-card" style="padding:0.7rem 1rem;font-size:0.84rem;'
            f'margin-bottom:6px;border-left:3px solid {AMBER};">{txt}</div>',
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────────
#  SMART REBALANCER
# ─────────────────────────────────────────────────────────────────
section("Smart Rebalancer")
st.caption("Pick a target mix — the engine computes the exact ₹ to move per bucket.")

preset = st.radio(
    "Strategy",
    ["Aggressive 80/15/5", "Balanced 65/25/10", "Conservative 50/30/20", "Custom"],
    horizontal=True, label_visibility="collapsed",
)
targets = {
    "Aggressive 80/15/5":    {"Equity Funds": 80, "Gold & Commodities": 15, "Debt / Hybrid": 5},
    "Balanced 65/25/10":     {"Equity Funds": 65, "Gold & Commodities": 25, "Debt / Hybrid": 10},
    "Conservative 50/30/20": {"Equity Funds": 50, "Gold & Commodities": 30, "Debt / Hybrid": 20},
}
if preset == "Custom":
    c1, c2, c3 = st.columns(3)
    eq = c1.slider("Equity %", 0, 100, 70)
    gd = c2.slider("Gold %", 0, 100 - eq, min(20, 100 - eq))
    tgt = {"Equity Funds": eq, "Gold & Commodities": gd, "Debt / Hybrid": 100 - eq - gd}
    c3.metric("Debt / Hybrid %", f"{100 - eq - gd}")
else:
    tgt = targets[preset]

cur = {k: v / TV * 100 for k, v in data.get("alloc_values", {}).items()}
all_cats = sorted(set(list(cur.keys()) + list(tgt.keys())))
rows = []
for cat in all_cats:
    c_pct, t_pct = cur.get(cat, 0), tgt.get(cat, 0)
    move = (t_pct - c_pct) / 100 * TV
    rows.append((cat, c_pct, t_pct, move))

fig = go.Figure()
fig.add_trace(go.Bar(
    y=[r[0] for r in rows], x=[r[1] for r in rows], orientation="h",
    name="Current", marker_color="rgba(139,92,246,0.75)", width=0.32,
    hovertemplate="Current %{x:.1f}%<extra></extra>",
))
fig.add_trace(go.Bar(
    y=[r[0] for r in rows], x=[r[2] for r in rows], orientation="h",
    name="Target", marker_color="rgba(34,211,238,0.55)", width=0.32,
    hovertemplate="Target %{x:.1f}%<extra></extra>",
))
fig.update_layout(**PLOT_LAYOUT, height=210, barmode="group",
    legend=dict(orientation="h", y=1.15, bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="rgba(139,92,246,0.1)", ticksuffix="%"),
    yaxis=dict(gridcolor="rgba(0,0,0,0)"))
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

mv_cols = st.columns(len(rows)) if rows else []
for col, (cat, c_pct, t_pct, move) in zip(mv_cols, rows):
    with col:
        tone = "up" if move > 0 else "down" if move < 0 else ""
        verb = "Add" if move > 0 else "Trim" if move < 0 else "Hold"
        glass_kpi(cat, f"{verb} ₹{abs(move):,.0f}", f"{c_pct:.1f}% → {t_pct:.0f}%", tone, 2)

# ─────────────────────────────────────────────────────────────────
#  MONTE CARLO WEALTH SIMULATOR
# ─────────────────────────────────────────────────────────────────
section("Wealth Time Machine · Monte Carlo")
mc1, mc2, mc3, mc4 = st.columns(4)
years   = mc1.slider("Horizon (years)", 1, 30, 10)
sip_amt = mc2.number_input("Monthly SIP (₹)", 0, 1_000_000, int(sip_monthly or 9000), step=500)
exp_ret = mc3.slider("Expected return %", 4.0, 20.0, max(8.0, min(round(wxirr, 1), 16.0)), 0.5)
vol     = mc4.slider("Volatility %", 5.0, 30.0, 15.0, 0.5)


@st.cache_data(show_spinner=False)
def monte_carlo(start, sip, yrs, mu, sigma, paths=1000, seed=7):
    rng = np.random.default_rng(seed)
    months = yrs * 12
    m_mu, m_sg = mu / 100 / 12, sigma / 100 / np.sqrt(12)
    rets = rng.normal(m_mu, m_sg, size=(paths, months))
    w = np.empty((paths, months + 1))
    w[:, 0] = start
    for t in range(months):
        w[:, t + 1] = (w[:, t] + sip) * (1 + rets[:, t])
    return w


W = monte_carlo(TV, sip_amt, years, exp_ret, vol)
x = np.arange(W.shape[1]) / 12
p10, p50, p90 = np.percentile(W, [10, 50, 90], axis=0)
invested_line = TV + sip_amt * np.arange(W.shape[1])

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=p90, line=dict(width=0), hoverinfo="skip", showlegend=False))
fig.add_trace(go.Scatter(
    x=x, y=p10, fill="tonexty", fillcolor="rgba(139,92,246,0.14)",
    line=dict(width=0), name="10-90% band", hoverinfo="skip",
))
for i in range(0, 60, 4):
    fig.add_trace(go.Scatter(
        x=x, y=W[i], mode="lines", showlegend=False, hoverinfo="skip",
        line=dict(color="rgba(34,211,238,0.07)", width=1),
    ))
fig.add_trace(go.Scatter(
    x=x, y=p50, name="Median path",
    line=dict(color=CYAN, width=2.5),
    hovertemplate="Yr %{x:.1f} · ₹%{y:,.0f}<extra>median</extra>",
))
fig.add_trace(go.Scatter(
    x=x, y=invested_line, name="Amount invested",
    line=dict(color=MUTED, width=1.5, dash="dot"),
    hovertemplate="Yr %{x:.1f} · ₹%{y:,.0f}<extra>invested</extra>",
))
fig.update_layout(**PLOT_LAYOUT, height=360,
    legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(title="Years", gridcolor="rgba(139,92,246,0.08)"),
    yaxis=dict(gridcolor="rgba(139,92,246,0.08)", tickprefix="₹", separatethousands=True))
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

r1, r2, r3 = st.columns(3)
with r1: glass_kpi("Pessimistic (P10)", f"₹{p10[-1]:,.0f}", f"after {years} years", "down", 1)
with r2: glass_kpi("Median outcome",    f"₹{p50[-1]:,.0f}", f"vs ₹{invested_line[-1]:,.0f} invested", "up", 2)
with r3: glass_kpi("Optimistic (P90)",  f"₹{p90[-1]:,.0f}", f"{(p90[-1] / invested_line[-1]):.1f}× of invested", "up", 3)

st.caption("Simulation of 1,000 random market paths — an illustration of the range of outcomes, not a prediction or advice.")

# ─────────────────────────────────────────────────────────────────
#  ADVISOR VERDICT – built-in rule engine, 100% local, NO API needed
# ─────────────────────────────────────────────────────────────────
section("Advisor Verdict")


def rule_engine_review():
    strengths, risks, steps = [], [], []
    top = holdings[0] if holdings else None
    top_w = top["value"] / TV * 100 if top else 0

    # strengths
    if wxirr >= 14:
        strengths.append(
            f"Your money is compounding at a weighted XIRR of {wxirr:.1f}%, "
            "comfortably ahead of the 12% long-term equity benchmark.")
    elif wxirr >= 10:
        strengths.append(
            f"Weighted XIRR of {wxirr:.1f}% is in a healthy band, "
            "close to long-term market averages.")
    if subs["SIP Discipline"] >= 70:
        strengths.append(
            f"SIP discipline is strong — ₹{sip_monthly:,.0f} flows in every month, "
            "which smooths out market volatility automatically.")
    if 6 <= len(holdings) <= 12:
        strengths.append(
            f"{len(holdings)} funds is the sweet spot — "
            "diversified without becoming impossible to track.")
    if subs["Concentration"] >= 70:
        strengths.append(
            "No single fund dominates the portfolio, "
            "so one bad scheme can't sink the ship.")

    # risks
    if top and top_w > 30:
        risks.append(
            f"{top['scheme'][:45]} alone is {top_w:.1f}% of your wealth — "
            "a stumble in this one fund hits the whole portfolio.")
    gold_pct = next(
        (p for c, p in data.get("alloc_pct", {}).items() if "gold" in c.lower()), 0)
    if gold_pct > 25:
        risks.append(
            f"Gold & commodities at {gold_pct:.1f}% is above the usual 15–25% hedge zone; "
            "gold protects but rarely compounds like equity.")
    if laggards:
        risks.append(
            f"{laggards[0]['scheme'][:45]} is dragging at "
            f"{laggards[0].get('xirr', 0):.1f}% XIRR — below even FD-level returns.")
    if subs["Category Balance"] < 55:
        risks.append(
            "The category mix is lopsided — "
            "most of the portfolio behaves the same way in a crash.")
    if len(holdings) > 12:
        risks.append(
            f"{len(holdings)} funds is over-diversified — "
            "many likely hold the same stocks, adding paperwork without adding safety.")
    if not risks:
        risks.append(
            "No major structural red flags — "
            "the main risk is simply staying invested through drawdowns.")

    # next step
    if top and top_w > 30:
        steps.append(
            f"Direct your next few SIPs away from {top['scheme'][:35]} into your "
            "smaller holdings until it drops below ~25% weight.")
    elif laggards:
        steps.append(
            f"Set a 2-quarter watch on {laggards[0]['scheme'][:35]}; "
            "if XIRR stays under 8%, switch to a category leader.")
    elif gold_pct > 25:
        steps.append(
            "Pause fresh gold purchases and let equity SIPs naturally "
            "rebalance the mix over the next 6–12 months.")
    else:
        steps.append(
            f"Keep the engine running — a step-up of just 10% on your "
            f"₹{sip_monthly:,.0f} SIP each year dramatically bends the wealth curve.")

    return strengths[:2], risks[:2], steps[0]


if st.button("✦ Generate written review"):
    s_list, r_list, next_step = rule_engine_review()
    blocks = "".join(
        f'<div style="display:flex;gap:10px;margin-bottom:10px;">'
        f'<span style="color:{MINT};font-weight:700;">✓</span>'
        f'<span style="font-size:0.88rem;line-height:1.6;color:{INK};">{s}</span></div>'
        for s in s_list)
    blocks += "".join(
        f'<div style="display:flex;gap:10px;margin-bottom:10px;">'
        f'<span style="color:{AMBER};font-weight:700;">!</span>'
        f'<span style="font-size:0.88rem;line-height:1.6;color:{INK};">{r}</span></div>'
        for r in r_list)
    blocks += (
        f'<div style="display:flex;gap:10px;margin-top:14px;padding-top:12px;'
        f'border-top:1px solid rgba(139,92,246,0.15);">'
        f'<span style="color:{CYAN};font-weight:700;">→</span>'
        f'<span style="font-size:0.88rem;line-height:1.6;color:{INK};">'
        f'<b>Next step:</b> {next_step}</span></div>')
    st.session_state["ai_review"] = blocks

if "ai_review" in st.session_state:
    st.markdown(f"""
    <div class="g-card" style="border-left:3px solid {VIOLET};">
        <div class="kpi-label" style="color:{VIOLET}">
            ✦ Advisor verdict · rule engine · {datetime.now().strftime('%d %b, %I:%M %p')}
        </div>
        {st.session_state['ai_review']}
    </div>""", unsafe_allow_html=True)

st.markdown(
    f'<div style="text-align:center;padding:2.5rem 0 1rem;color:{C["faint"]};font-size:0.7rem;">'
    "CAS 360 v2.0 · Advisor Intelligence · runs fully on your device, no API · "
    "scores are heuristics for self-review, not investment advice"
    "</div>",
    unsafe_allow_html=True,
)
