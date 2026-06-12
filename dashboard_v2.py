# ──────────────────────────────────────────────────────────────────
#  CAS 360 v2.0 – MAIN DASHBOARD ENGINE  (dashboard_v2.py)
#  Place in PROJECT ROOT next to dashboard.py.
#
#  Wired via dashboard.py's render_dashboard:
#      def render_dashboard(data):
#          import dashboard_v2
#          dashboard_v2.render_v2(data)
#
#  100% local · no API · no internet needed beyond what 1.0 used.
# ──────────────────────────────────────────────────────────────────
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import math
from datetime import datetime

from ui_theme import inject_theme, glass_kpi, page_header, section, C

VIOLET, CYAN, MINT, EMBER, AMBER = C["violet"], C["cyan"], C["mint"], C["ember"], C["amber"]
MUTED, INK = C["muted"], C["ink"]

PLOT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED, size=11, family="Inter"),
            margin=dict(l=10, r=10, t=24, b=10))


def _H(s: str) -> str:
    """Collapse multi-line HTML to one line — prevents Streamlit treating
    4-space-indented lines as a code block."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


# ─────────────────────────────────────────────────────────────────────
#  SCORE ENGINE
# ─────────────────────────────────────────────────────────────────────
def compute_scores(data):
    holdings  = data.get("holdings", [])
    TV        = data.get("total_value", 0) or 1
    alloc_pct = data.get("alloc_pct", {})
    live_sips = data.get("live_sips", [])

    n       = len(holdings)
    weights = [h["value"] / TV for h in holdings] if holdings else [1.0]

    if 6 <= n <= 12: s_div = 100
    elif n < 6:      s_div = max(20, n / 6 * 90)
    else:            s_div = max(40, 100 - (n - 12) * 6)

    hhi   = sum(w * w for w in weights)
    ideal = 1 / max(n, 1)
    s_con = max(0, min(100, 100 - (hhi - ideal) * 400))

    xirrs = [(h.get("xirr") or 0, h["value"]) for h in holdings if h.get("xirr")]
    wx    = sum(x * v for x, v in xirrs) / sum(v for _, v in xirrs) if xirrs else 0
    s_ret = max(0, min(100, 50 + (wx - 12) * 5))

    s_bal = 100.0
    for cat, pct in (alloc_pct or {}).items():
        if pct > 75: s_bal -= (pct - 75) * 2
        if "gold" in cat.lower() and pct > 25: s_bal -= (pct - 25) * 2.5
    s_bal = max(0, s_bal)

    sip_monthly = sum(s.get("amount", 0) for s in (live_sips or []))
    s_sip       = max(0, min(100, (sip_monthly * 12) / TV * 100 * 2.2))

    subs = {"Diversification": round(s_div), "Concentration": round(s_con),
            "Returns": round(s_ret), "Category Balance": round(s_bal),
            "SIP Discipline": round(s_sip)}
    return round(sum(subs.values()) / 5), subs, wx, sip_monthly


def grade(s):
    return ("A+", MINT)  if s >= 85 else \
           ("A",  MINT)  if s >= 75 else \
           ("B",  CYAN)  if s >= 60 else \
           ("C",  AMBER) if s >= 45 else ("D", EMBER)


# ─────────────────────────────────────────────────────────────────────
#  MAIN ENTRY — called from dashboard.py's render_dashboard(data)
# ─────────────────────────────────────────────────────────────────────
def render_v2(data, live_data=None):
    inject_theme()

    holdings = sorted(data.get("holdings", []), key=lambda h: -h.get("value", 0))
    TV   = data.get("total_value",    0) or 1
    TI   = data.get("total_invested", 0) or 1
    PNL  = data.get("unrealized_pnl", TV - TI)
    name = data.get("investor_name", "Investor").split()[0].title()

    score, subs, wxirr, sip_monthly = compute_scores(data)
    g_letter, g_color = grade(score)

    # ── HERO: welcome + animated health ring ─────────────────────────
    page_header(f"Welcome back, {name} 👋",
                f"CAS statement · {data.get('statement_date', '')} · CAS 360 v2.0",
                live=True)

    circ = 2 * math.pi * 84
    dash = circ * score / 100

    bars = ""
    for k, v in subs.items():
        bc = grade(v)[1]
        bars += _H(f"""
        <div>
          <div style="display:flex;justify-content:space-between;font-size:0.72rem;margin-bottom:4px;">
            <span style="color:{MUTED}">{k}</span>
            <span class="num" style="color:{bc};font-weight:600">{v}</span>
          </div>
          <div style="height:5px;background:rgba(139,92,246,0.12);border-radius:3px;overflow:hidden;">
            <div style="height:100%;width:{v}%;border-radius:3px;
              background:linear-gradient(90deg,{VIOLET},{bc});
              box-shadow:0 0 8px {bc}66;"></div>
          </div>
        </div>""")

    hero = _H(f"""
    <div class="g-card rise" style="display:flex;align-items:center;gap:2.2rem;padding:1.6rem 2rem;flex-wrap:wrap;">
      <div style="position:relative;width:200px;height:200px;flex-shrink:0;">
        <svg width="200" height="200" viewBox="0 0 200 200" style="transform:rotate(-90deg)">
          <defs>
            <linearGradient id="ringG" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%"   stop-color="{VIOLET}"/>
              <stop offset="60%"  stop-color="{CYAN}"/>
              <stop offset="100%" stop-color="{MINT}"/>
            </linearGradient>
          </defs>
          <circle cx="100" cy="100" r="84" fill="none"
            stroke="rgba(139,92,246,0.12)" stroke-width="10"/>
          <circle cx="100" cy="100" r="84" fill="none"
            stroke="url(#ringG)" stroke-width="10" stroke-linecap="round"
            stroke-dasharray="{dash:.0f} {circ:.0f}"
            style="filter:drop-shadow(0 0 10px rgba(139,92,246,0.6));">
            <animate attributeName="stroke-dasharray"
              from="0 {circ:.0f}" to="{dash:.0f} {circ:.0f}"
              dur="1.4s" calcMode="spline" keySplines="0.22 1 0.36 1" fill="freeze"/>
          </circle>
          <circle cx="100" cy="16" r="5" fill="{CYAN}">
            <animateTransform attributeName="transform" type="rotate"
              from="0 100 100" to="{score*3.6:.0f} 100 100"
              dur="1.4s" calcMode="spline" keySplines="0.22 1 0.36 1" fill="freeze"/>
          </circle>
        </svg>
        <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
          <div class="num" style="font-size:2.6rem;font-weight:700;color:{INK};line-height:1;">{score}</div>
          <div style="font-size:0.65rem;letter-spacing:0.15em;color:{MUTED};margin-top:2px;">HEALTH SCORE</div>
          <div class="num" style="font-size:0.95rem;font-weight:700;color:{g_color};margin-top:4px;">GRADE {g_letter}</div>
        </div>
      </div>
      <div style="flex:1;min-width:300px;display:grid;grid-template-columns:1fr 1fr;gap:0.8rem 2rem;">
        {bars}
        <div style="align-self:end;">
          <span class="pill">wtd XIRR
            <b class="num" style="color:{MINT if wxirr>=12 else AMBER};margin-left:4px">{wxirr:.1f}%</b>
          </span>
          <span class="pill" style="margin-left:6px">{len(holdings)} funds</span>
        </div>
      </div>
    </div>""")
    st.markdown(hero, unsafe_allow_html=True)

    # ── KPI strip ─────────────────────────────────────────────────────
    pnl_pct = PNL / TI * 100 if TI else 0
    k1, k2, k3, k4 = st.columns(4)
    with k1: glass_kpi("Total Wealth",   f"₹{TV:,.0f}", f"invested ₹{TI:,.0f}", "", 1)
    with k2: glass_kpi("Unrealized P&L", f"₹{PNL:,.0f}",
                       f"{'▲' if PNL >= 0 else '▼'} {abs(pnl_pct):.2f}% all-time",
                       "up" if PNL >= 0 else "down", 2)
    with k3: glass_kpi("Weighted XIRR",  f"{wxirr:.2f}%", "benchmark 12.00%",
                       "up" if wxirr >= 12 else "warn", 3)
    with k4: glass_kpi("Monthly SIP",    f"₹{sip_monthly:,.0f}",
                       f"{len(data.get('live_sips', []))} active mandates", "up", 4)

    # ── WEALTH JOURNEY + ALLOCATION ───────────────────────────────────
    cL, cR = st.columns([1.6, 1])
    with cL:
        section("Wealth Journey")
        df = pd.DataFrame([{"fund": h["scheme"][:24],
                             "Invested": h["invested"],
                             "Current":  h["value"]} for h in holdings])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["fund"], y=df["Invested"], name="Invested",
            marker_color="rgba(139,92,246,0.45)",
            hovertemplate="₹%{y:,.0f}<extra>invested</extra>"))
        fig.add_trace(go.Bar(x=df["fund"], y=df["Current"], name="Current value",
            marker=dict(color=df["Current"],
                        colorscale=[[0, CYAN], [1, MINT]], showscale=False),
            hovertemplate="₹%{y:,.0f}<extra>current</extra>"))
        fig.update_layout(**PLOT, height=320, barmode="group",
            legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(tickangle=-30, gridcolor="rgba(0,0,0,0)", tickfont=dict(size=9)),
            yaxis=dict(gridcolor="rgba(139,92,246,0.08)",
                       tickprefix="₹", separatethousands=True))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cR:
        section("Asset Allocation")
        alloc = data.get("alloc_values", {})
        if alloc:
            fig = go.Figure(go.Pie(
                labels=list(alloc.keys()), values=list(alloc.values()), hole=0.66,
                marker=dict(colors=[VIOLET, AMBER, CYAN, MINT, EMBER],
                            line=dict(color=C["void"], width=3)),
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} · %{percent}<extra></extra>"))
            fig.add_annotation(text=f"<b>₹{TV:,.0f}</b>", showarrow=False,
                               font=dict(family="JetBrains Mono", size=15, color=INK))
            fig.update_layout(**PLOT, height=320,
                legend=dict(orientation="h", y=-0.1, bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── RISK RADAR + CONCENTRATION MAP ───────────────────────────────
    cA, cB = st.columns([1, 1.3])
    with cA:
        section("Risk Radar")
        axes, vals = list(subs.keys()), list(subs.values())
        fig = go.Figure(go.Scatterpolar(
            r=vals + vals[:1], theta=axes + axes[:1],
            fill="toself", line=dict(color=VIOLET, width=2),
            fillcolor="rgba(139,92,246,0.18)",
            hovertemplate="%{theta}: %{r}<extra></extra>"))
        fig.add_trace(go.Scatterpolar(
            r=[70] * 6, theta=axes + axes[:1], mode="lines",
            line=dict(color="rgba(52,211,153,0.45)", dash="dot", width=1),
            hoverinfo="skip"))
        fig.update_layout(**PLOT, height=320, showlegend=False,
            polar=dict(bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(range=[0, 100],
                    gridcolor="rgba(139,92,246,0.12)",
                    tickfont=dict(size=8, color=MUTED)),
                angularaxis=dict(gridcolor="rgba(139,92,246,0.12)",
                    tickfont=dict(size=10, color=INK))))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with cB:
        section("Concentration Map")
        df = pd.DataFrame([{
            "fund": h["scheme"][:34],
            "cat":  h.get("category", "Other"),
            "value": h["value"],
            "w":     h["value"] / TV * 100,
            "xirr":  h.get("xirr") or 0,
        } for h in holdings])
        fig = go.Figure(go.Treemap(
            labels=df["fund"], parents=df["cat"], values=df["value"],
            marker=dict(
                colors=df["xirr"],
                colorscale=[[0, EMBER], [0.5, "#1e2338"], [1, MINT]],
                cmid=10, line=dict(color=C["void"], width=2)),
            customdata=np.stack([df["w"], df["xirr"]], axis=-1),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "₹%{value:,.0f} · %{customdata[0]:.1f}% of portfolio<br>"
                "XIRR %{customdata[1]:.1f}%<extra></extra>"),
            textfont=dict(family="Inter", size=11, color=INK)))
        fig.update_layout(**PLOT, height=320)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── ADVISOR FLAGS ─────────────────────────────────────────────────
    laggards = [h for h in holdings
                if (h.get("xirr") or 99) < 8 and h["value"] > TV * 0.05]
    flags = []
    for h in holdings:
        w = h["value"] / TV * 100
        if w > 30:
            flags.append(f"⚠️ <b>{h['scheme'][:42]}</b> is <b>{w:.1f}%</b> of your portfolio — single-fund risk.")
    for cat, pct in data.get("alloc_pct", {}).items():
        if "gold" in cat.lower() and pct > 25:
            flags.append(f"⚠️ <b>{cat}</b> at <b>{pct:.1f}%</b> — above the 25% commodities comfort zone.")
    for h in laggards[:2]:
        flags.append(f"📉 <b>{h['scheme'][:42]}</b> XIRR is only <b>{h.get('xirr', 0):.1f}%</b> — review or switch.")
    if flags:
        section("Advisor Flags")
        for f in flags[:4]:
            st.markdown(_H(f"""
            <div class="g-card" style="padding:0.7rem 1rem;font-size:0.84rem;
              margin-bottom:6px;border-left:3px solid {AMBER};">{f}</div>"""),
                unsafe_allow_html=True)

    # ── SMART REBALANCER ──────────────────────────────────────────────
    section("Smart Rebalancer")
    st.caption("Pick a target mix — see the exact ₹ to add or trim per bucket.")
    preset = st.radio("Strategy",
        ["Aggressive 80/15/5", "Balanced 65/25/10", "Conservative 50/30/20", "Custom"],
        horizontal=True, label_visibility="collapsed", key="v2_rebalance")
    presets = {
        "Aggressive 80/15/5":    {"Equity Funds": 80, "Gold & Commodities": 15, "Debt / Hybrid": 5},
        "Balanced 65/25/10":     {"Equity Funds": 65, "Gold & Commodities": 25, "Debt / Hybrid": 10},
        "Conservative 50/30/20": {"Equity Funds": 50, "Gold & Commodities": 30, "Debt / Hybrid": 20},
    }
    if preset == "Custom":
        c1, c2, c3 = st.columns(3)
        eq = c1.slider("Equity %", 0, 100, 70, key="v2_eq")
        gd = c2.slider("Gold %",   0, 100 - eq, min(20, 100 - eq), key="v2_gd")
        tgt = {"Equity Funds": eq, "Gold & Commodities": gd, "Debt / Hybrid": 100 - eq - gd}
        c3.metric("Debt / Hybrid %", f"{100 - eq - gd}")
    else:
        tgt = presets[preset]

    cur  = {k: v / TV * 100 for k, v in data.get("alloc_values", {}).items()}
    rows = []
    for cat in sorted(set(list(cur.keys()) + list(tgt.keys()))):
        c_pct, t_pct = cur.get(cat, 0), tgt.get(cat, 0)
        rows.append((cat, c_pct, t_pct, (t_pct - c_pct) / 100 * TV))

    fig = go.Figure()
    fig.add_trace(go.Bar(y=[r[0] for r in rows], x=[r[1] for r in rows], orientation="h",
        name="Current",  marker_color="rgba(139,92,246,0.75)", width=0.32,
        hovertemplate="Current %{x:.1f}%<extra></extra>"))
    fig.add_trace(go.Bar(y=[r[0] for r in rows], x=[r[2] for r in rows], orientation="h",
        name="Target",   marker_color="rgba(34,211,238,0.55)", width=0.32,
        hovertemplate="Target %{x:.1f}%<extra></extra>"))
    fig.update_layout(**PLOT, height=200, barmode="group",
        legend=dict(orientation="h", y=1.18, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="rgba(139,92,246,0.1)", ticksuffix="%"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if rows:
        mcols = st.columns(len(rows))
        for col, (cat, c_pct, t_pct, move) in zip(mcols, rows):
            with col:
                verb = "Add" if move > 0 else "Trim" if move < 0 else "Hold"
                glass_kpi(cat, f"{verb} ₹{abs(move):,.0f}",
                          f"{c_pct:.1f}% → {t_pct:.0f}%",
                          "up" if move > 0 else "down" if move < 0 else "", 2)

    # ── WEALTH TIME MACHINE (Monte Carlo) ─────────────────────────────
    section("Wealth Time Machine · 1,000 simulated futures")
    m1, m2, m3, m4 = st.columns(4)
    years   = m1.slider("Horizon (years)", 1, 30, 10, key="v2_yrs")
    sip_amt = m2.number_input("Monthly SIP (₹)", 0, 1_000_000,
                              int(sip_monthly or 9000), step=500, key="v2_sip")
    exp_ret = m3.slider("Expected return %", 4.0, 20.0,
                        float(max(8.0, min(round(wxirr, 1), 16.0))), 0.5, key="v2_ret")
    vol     = m4.slider("Volatility %", 5.0, 30.0, 15.0, 0.5, key="v2_vol")

    W   = _monte_carlo(TV, sip_amt, years, exp_ret, vol)
    x   = np.arange(W.shape[1]) / 12
    p10, p50, p90 = np.percentile(W, [10, 50, 90], axis=0)
    inv_line = TV + sip_amt * np.arange(W.shape[1])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=p90, line=dict(width=0), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=x, y=p10, fill="tonexty",
        fillcolor="rgba(139,92,246,0.14)", line=dict(width=0),
        name="10–90% band", hoverinfo="skip"))
    for i in range(0, 60, 4):
        fig.add_trace(go.Scatter(x=x, y=W[i], mode="lines", showlegend=False, hoverinfo="skip",
            line=dict(color="rgba(34,211,238,0.07)", width=1)))
    fig.add_trace(go.Scatter(x=x, y=p50, name="Median path",
        line=dict(color=CYAN, width=2.5),
        hovertemplate="Yr %{x:.1f} · ₹%{y:,.0f}<extra>median</extra>"))
    fig.add_trace(go.Scatter(x=x, y=inv_line, name="Amount invested",
        line=dict(color=MUTED, width=1.5, dash="dot"),
        hovertemplate="Yr %{x:.1f} · ₹%{y:,.0f}<extra>invested</extra>"))
    fig.update_layout(**PLOT, height=350,
        legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title="Years", gridcolor="rgba(139,92,246,0.08)"),
        yaxis=dict(gridcolor="rgba(139,92,246,0.08)",
                   tickprefix="₹", separatethousands=True))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    r1, r2, r3 = st.columns(3)
    with r1: glass_kpi("Pessimistic (P10)", f"₹{p10[-1]:,.0f}", f"after {years} years",    "down", 1)
    with r2: glass_kpi("Median outcome",    f"₹{p50[-1]:,.0f}", f"vs ₹{inv_line[-1]:,.0f} invested", "up", 2)
    with r3: glass_kpi("Optimistic (P90)",  f"₹{p90[-1]:,.0f}",
                       f"{(p90[-1] / max(inv_line[-1], 1)):.1f}× of invested", "up", 3)
    st.caption("Range of simulated outcomes — an illustration, not a prediction or advice.")

    # ── ADVISOR VERDICT (rule engine, no API) ─────────────────────────
    section("Advisor Verdict")
    if st.button("✦ Generate written review", key="v2_verdict"):
        st.session_state["v2_review"] = _verdict_html(
            data, holdings, TV, wxirr, subs, sip_monthly, laggards)
    if "v2_review" in st.session_state:
        st.markdown(_H(f"""
        <div class="g-card" style="border-left:3px solid {VIOLET};">
          <div class="kpi-label" style="color:{VIOLET}">
            ✦ Advisor verdict · rule engine · {datetime.now().strftime('%d %b, %I:%M %p')}
          </div>
          {st.session_state['v2_review']}
        </div>"""), unsafe_allow_html=True)

    st.markdown(_H(f"""
    <div style="text-align:center;padding:2.5rem 0 1rem;color:{C['faint']};font-size:0.7rem;">
      CAS 360 v2.0 · runs fully on your device · scores are heuristics for self-review,
      not investment advice
    </div>"""), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _monte_carlo(start, sip, yrs, mu, sigma, paths=1000, seed=7):
    rng    = np.random.default_rng(seed)
    months = yrs * 12
    rets   = rng.normal(mu / 100 / 12, sigma / 100 / np.sqrt(12), size=(paths, months))
    w      = np.empty((paths, months + 1))
    w[:, 0] = start
    for t in range(months):
        w[:, t + 1] = (w[:, t] + sip) * (1 + rets[:, t])
    return w


def _verdict_html(data, holdings, TV, wxirr, subs, sip_monthly, laggards):
    strengths, risks, steps = [], [], []
    top    = holdings[0] if holdings else None
    top_w  = top["value"] / TV * 100 if top else 0
    gold_pct = next(
        (p for c, p in data.get("alloc_pct", {}).items() if "gold" in c.lower()), 0)

    if wxirr >= 14:
        strengths.append(
            f"Your money is compounding at a weighted XIRR of {wxirr:.1f}%, "
            f"comfortably ahead of the 12% long-term equity benchmark.")
    elif wxirr >= 10:
        strengths.append(
            f"Weighted XIRR of {wxirr:.1f}% is in a healthy band, "
            f"close to long-term market averages.")
    if subs["SIP Discipline"] >= 70:
        strengths.append(
            f"SIP discipline is strong — ₹{sip_monthly:,.0f} flows in every month, "
            f"smoothing out volatility automatically.")
    if 6 <= len(holdings) <= 12:
        strengths.append(
            f"{len(holdings)} funds is the sweet spot — diversified without becoming "
            f"impossible to track.")
    if subs["Concentration"] >= 70:
        strengths.append(
            "No single fund dominates the portfolio, so one bad scheme can't sink the ship.")

    if top and top_w > 30:
        risks.append(
            f"{top['scheme'][:45]} alone is {top_w:.1f}% of your wealth — "
            f"a stumble in this one fund hits everything.")
    if gold_pct > 25:
        risks.append(
            f"Gold & commodities at {gold_pct:.1f}% is above the usual 15–25% hedge zone; "
            f"gold protects but rarely compounds like equity.")
    if laggards:
        risks.append(
            f"{laggards[0]['scheme'][:45]} is dragging at "
            f"{laggards[0].get('xirr', 0):.1f}% XIRR — below even FD-level returns.")
    if subs["Category Balance"] < 55:
        risks.append(
            "The category mix is lopsided — most of the portfolio behaves the same "
            "way in a crash.")
    if len(holdings) > 12:
        risks.append(
            f"{len(holdings)} funds is over-diversified — many likely hold the same stocks.")
    if not risks:
        risks.append(
            "No major structural red flags — the main risk is simply staying invested "
            "through drawdowns.")

    if top and top_w > 30:
        steps.append(
            f"Direct your next few SIPs away from {top['scheme'][:35]} into smaller "
            f"holdings until it drops below ~25% weight.")
    elif laggards:
        steps.append(
            f"Set a 2-quarter watch on {laggards[0]['scheme'][:35]}; "
            f"if XIRR stays under 8%, switch to a category leader.")
    elif gold_pct > 25:
        steps.append(
            "Pause fresh gold purchases and let equity SIPs naturally rebalance "
            "the mix over 6–12 months.")
    else:
        steps.append(
            f"Keep the engine running — a 10% annual step-up on your "
            f"₹{sip_monthly:,.0f} SIP dramatically bends the wealth curve.")

    out = ""
    for s in strengths[:2]:
        out += _H(f"""
        <div style="display:flex;gap:10px;margin-bottom:10px;">
          <span style="color:{MINT};font-weight:700;">✓</span>
          <span style="font-size:0.88rem;line-height:1.6;color:{INK};">{s}</span>
        </div>""")
    for r in risks[:2]:
        out += _H(f"""
        <div style="display:flex;gap:10px;margin-bottom:10px;">
          <span style="color:{AMBER};font-weight:700;">!</span>
          <span style="font-size:0.88rem;line-height:1.6;color:{INK};">{r}</span>
        </div>""")
    out += _H(f"""
    <div style="display:flex;gap:10px;margin-top:14px;padding-top:12px;
      border-top:1px solid rgba(139,92,246,0.15);">
      <span style="color:{CYAN};font-weight:700;">→</span>
      <span style="font-size:0.88rem;line-height:1.6;color:{INK};">
        <b>Next step:</b> {steps[0]}
      </span>
    </div>""")
    return out
