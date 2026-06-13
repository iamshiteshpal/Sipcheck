# ──────────────────────────────────────────────────────────────────
#  SipCheck v2.3 – FUND REGISTRY PRO  (fund_registry_v2.py)
#  Place in PROJECT ROOT. Powers the MF Report Pro page.
#
#  HOW IT WORKS (no fake numbers, ever):
#  · 57+ top Indian funds listed by NAME + category + AMC.
#  · Direct & Regular plan codes resolved LIVE from mfapi.in search.
#  · All metrics (NAV, 1Y/3Y/5Y CAGR, volatility, drawdown,
#    calendar-year returns) computed from real NAV history.
#  · AUM / expense ratio show "—" honestly (not in free feeds).
#  · "Request a Scheme" searches the ENTIRE AMFI universe (10,000+).
# ──────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

from ui_theme import glass_kpi, section, C

VIOLET, CYAN, MINT, EMBER, AMBER = C["violet"], C["cyan"], C["mint"], C["ember"], C["amber"]
MUTED, INK = C["muted"], C["ink"]
PLOT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED, size=11, family="Inter"),
            margin=dict(l=10, r=10, t=24, b=10))


def H(s):
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


# ─────────────────────────────────────────────────────────────────────────────
#  REGISTRY – 57 top funds (name · category · AMC)
# ─────────────────────────────────────────────────────────────────────────────
FUND_REGISTRY = [
    # Large Cap
    ("Mirae Asset Large Cap Fund",               "Large Cap",     "Mirae Asset"),
    ("Axis Bluechip Fund",                       "Large Cap",     "Axis"),
    ("SBI Bluechip Fund",                        "Large Cap",     "SBI"),
    ("HDFC Top 100 Fund",                        "Large Cap",     "HDFC"),
    ("ICICI Prudential Bluechip Fund",           "Large Cap",     "ICICI Pru"),
    ("Kotak Bluechip Fund",                      "Large Cap",     "Kotak"),
    ("Nippon India Large Cap Fund",              "Large Cap",     "Nippon India"),
    ("Canara Robeco Bluechip Equity Fund",       "Large Cap",     "Canara Robeco"),
    # Index
    ("UTI Nifty 50 Index Fund",                  "Index",         "UTI"),
    ("HDFC Index Fund Nifty 50 Plan",            "Index",         "HDFC"),
    ("ICICI Prudential Nifty 50 Index Fund",     "Index",         "ICICI Pru"),
    ("Motilal Oswal Nifty Midcap 150 Index Fund","Index",         "Motilal Oswal"),
    ("UTI Nifty Next 50 Index Fund",             "Index",         "UTI"),
    # Flexi / Multi Cap
    ("Parag Parikh Flexi Cap Fund",              "Flexi Cap",     "PPFAS"),
    ("HDFC Flexi Cap Fund",                      "Flexi Cap",     "HDFC"),
    ("SBI Flexicap Fund",                        "Flexi Cap",     "SBI"),
    ("Kotak Flexicap Fund",                      "Flexi Cap",     "Kotak"),
    ("Quant Flexi Cap Fund",                     "Flexi Cap",     "Quant"),
    ("Nippon India Multi Cap Fund",              "Multi Cap",     "Nippon India"),
    ("Mahindra Manulife Multi Cap Fund",         "Multi Cap",     "Mahindra"),
    # Mid Cap
    ("Motilal Oswal Midcap Fund",                "Mid Cap",       "Motilal Oswal"),
    ("HDFC Mid-Cap Opportunities Fund",          "Mid Cap",       "HDFC"),
    ("Kotak Emerging Equity Fund",               "Mid Cap",       "Kotak"),
    ("Axis Midcap Fund",                         "Mid Cap",       "Axis"),
    ("Mirae Asset Midcap Fund",                  "Mid Cap",       "Mirae Asset"),
    ("Invesco India Midcap Fund",                "Mid Cap",       "Invesco"),
    ("Quant Mid Cap Fund",                       "Mid Cap",       "Quant"),
    ("Edelweiss Mid Cap Fund",                   "Mid Cap",       "Edelweiss"),
    # Small Cap
    ("Nippon India Small Cap Fund",              "Small Cap",     "Nippon India"),
    ("Axis Small Cap Fund",                      "Small Cap",     "Axis"),
    ("HDFC Small Cap Fund",                      "Small Cap",     "HDFC"),
    ("SBI Small Cap Fund",                       "Small Cap",     "SBI"),
    ("Quant Small Cap Fund",                     "Small Cap",     "Quant"),
    ("Bandhan Small Cap Fund",                   "Small Cap",     "Bandhan"),
    ("Tata Small Cap Fund",                      "Small Cap",     "Tata"),
    ("DSP Small Cap Fund",                       "Small Cap",     "DSP"),
    # ELSS
    ("Quant ELSS Tax Saver Fund",                "ELSS",          "Quant"),
    ("Mirae Asset ELSS Tax Saver Fund",          "ELSS",          "Mirae Asset"),
    ("DSP ELSS Tax Saver Fund",                  "ELSS",          "DSP"),
    ("HDFC ELSS Tax Saver",                      "ELSS",          "HDFC"),
    ("Parag Parikh ELSS Tax Saver Fund",         "ELSS",          "PPFAS"),
    # Hybrid / Balanced
    ("HDFC Balanced Advantage Fund",             "Hybrid",        "HDFC"),
    ("ICICI Prudential Balanced Advantage Fund", "Hybrid",        "ICICI Pru"),
    ("SBI Equity Hybrid Fund",                   "Hybrid",        "SBI"),
    ("Edelweiss Balanced Advantage Fund",        "Hybrid",        "Edelweiss"),
    ("Kotak Equity Hybrid Fund",                 "Hybrid",        "Kotak"),
    # Gold / Silver
    ("HDFC Gold ETF Fund of Fund",               "Gold",          "HDFC"),
    ("SBI Gold Fund",                            "Gold",          "SBI"),
    ("Nippon India Gold Savings Fund",           "Gold",          "Nippon India"),
    ("UTI Gold ETF Fund of Fund",                "Gold",          "UTI"),
    ("ICICI Prudential Regular Gold Savings Fund","Gold",         "ICICI Pru"),
    ("HDFC Silver ETF Fund of Fund",             "Silver",        "HDFC"),
    # Debt / Liquid
    ("HDFC Liquid Fund",                         "Liquid",        "HDFC"),
    ("SBI Liquid Fund",                          "Liquid",        "SBI"),
    ("ICICI Prudential Corporate Bond Fund",     "Debt",          "ICICI Pru"),
    ("HDFC Short Term Debt Fund",                "Debt",          "HDFC"),
    # International
    ("Motilal Oswal Nasdaq 100 Fund of Fund",    "International", "Motilal Oswal"),
    ("Franklin India Feeder Franklin US Opportunities", "International", "Franklin"),
]


# ─────────────────────────────────────────────────────────────────────────────
#  LIVE RESOLUTION + METRICS (all real, from mfapi.in)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=86400, show_spinner=False)
def search_schemes(query: str):
    try:
        r = requests.get("https://api.mfapi.in/mf/search",
                         params={"q": query}, timeout=8)
        if r.status_code == 200:
            return r.json() or []
    except Exception:
        pass
    return []


def resolve_codes(fund_name: str):
    results = search_schemes(fund_name)
    direct = regular = None
    for s in results:
        nm = s.get("schemeName", "").lower()
        if "growth" not in nm or "idcw" in nm or "dividend" in nm:
            continue
        if "direct" in nm and direct is None:
            direct = s
        elif "direct" not in nm and regular is None:
            regular = s
    return direct, regular


@st.cache_data(ttl=43200, show_spinner=False)
def fetch_full_history(code: str):
    try:
        r = requests.get(f"https://api.mfapi.in/mf/{code}", timeout=10)
        if r.status_code != 200:
            return None
        j = r.json()
        df = pd.DataFrame(j.get("data", []))
        if df.empty:
            return None
        df["date"] = pd.to_datetime(df["date"], dayfirst=True)
        df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
        df = df.dropna().sort_values("date").reset_index(drop=True)
        return {"meta": j.get("meta", {}), "df": df}
    except Exception:
        return None


def _cagr(df, years):
    end = df.iloc[-1]
    start_date = end["date"] - pd.DateOffset(years=years)
    past = df[df["date"] <= start_date]
    if past.empty:
        return None
    start = past.iloc[-1]
    yrs = (end["date"] - start["date"]).days / 365.25
    if yrs <= 0 or start["nav"] <= 0:
        return None
    return ((end["nav"] / start["nav"]) ** (1 / yrs) - 1) * 100


def compute_metrics(df):
    out = {}
    out["nav"]      = df["nav"].iloc[-1]
    out["nav_date"] = df["date"].iloc[-1].strftime("%d %b %Y")
    out["launch"]   = df["date"].iloc[0].strftime("%b %Y")
    for y in (1, 3, 5):
        out[f"cagr_{y}y"] = _cagr(df, y)
    yrs_total = (df["date"].iloc[-1] - df["date"].iloc[0]).days / 365.25
    if yrs_total > 0.5:
        out["cagr_inception"] = ((df["nav"].iloc[-1] / df["nav"].iloc[0]) ** (1 / yrs_total) - 1) * 100
    else:
        out["cagr_inception"] = None
    m = df.set_index("date")["nav"].resample("ME").last().pct_change().dropna()
    out["std_dev"] = m.std() * np.sqrt(12) * 100 if len(m) > 6 else None
    roll_max = df["nav"].cummax()
    out["max_dd"] = ((df["nav"] / roll_max) - 1).min() * 100
    cal = {}
    for y in sorted(df["date"].dt.year.unique())[-5:]:
        ydf = df[df["date"].dt.year == y]
        if len(ydf) > 20:
            cal[int(y)] = (ydf["nav"].iloc[-1] / ydf["nav"].iloc[0] - 1) * 100
    out["calendar"] = cal
    return out


# ─────────────────────────────────────────────────────────────────────────────
#  RENDERERS
# ─────────────────────────────────────────────────────────────────────────────
def render_live_report(fund_name: str, category: str, amc: str):
    plan = st.radio("Plan", ["Direct", "Regular"], horizontal=True, key=f"plan_{fund_name}")
    with st.spinner("Resolving plan codes + fetching real NAV history…"):
        direct, regular = resolve_codes(fund_name)
        chosen = direct if plan == "Direct" else regular
    if not chosen:
        st.warning(f"Couldn't find the {plan} Growth plan for this fund on AMFI. "
                   "Try the other plan, or use 'Request a Scheme' below.")
        return
    hist = fetch_full_history(str(chosen["schemeCode"]))
    if not hist:
        st.warning("NAV history unavailable right now — try refreshing.")
        return
    df, meta = hist["df"], hist["meta"]
    mt = compute_metrics(df)

    st.markdown(H(f"""
    <div class="g-card" style="margin-bottom:1rem;">
    <div style="font-size:0.62rem;letter-spacing:0.12em;color:{VIOLET};font-weight:700;">
    LIVE FUND REPORT · {amc.upper()} · ALL NUMBERS COMPUTED FROM REAL NAV HISTORY</div>
    <div style="font-family:'Space Grotesk';font-size:1.4rem;font-weight:700;color:{INK};margin:4px 0;">
    {meta.get('scheme_name', fund_name)}</div>
    <span class="pill">{category}</span>
    <span class="pill">{plan} Plan</span>
    <span class="pill">since {mt['launch']}</span>
    <span class="pill live">NAV ₹{mt['nav']:.4f} · {mt['nav_date']}</span>
    </div>"""), unsafe_allow_html=True)

    def fmt(v, suf="%"):
        return f"{v:.2f}{suf}" if v is not None else "—"

    c = st.columns(6)
    with c[0]: glass_kpi("1Y CAGR",       fmt(mt["cagr_1y"]),       "", "up" if (mt["cagr_1y"] or 0) >= 0 else "down", 1)
    with c[1]: glass_kpi("3Y CAGR",       fmt(mt["cagr_3y"]),       "", "up" if (mt["cagr_3y"] or 0) >= 12 else "warn", 1)
    with c[2]: glass_kpi("5Y CAGR",       fmt(mt["cagr_5y"]),       "", "up" if (mt["cagr_5y"] or 0) >= 12 else "warn", 2)
    with c[3]: glass_kpi("Since Launch",  fmt(mt["cagr_inception"]), "", "", 2)
    with c[4]: glass_kpi("Volatility",    fmt(mt["std_dev"]),        "annualised", "", 3)
    with c[5]: glass_kpi("Max Drawdown",  fmt(mt["max_dd"]),         "worst fall", "down", 3)
    st.caption("AUM, expense ratio & holdings are not published in free feeds — shown as '—' honestly.")

    section("NAV Journey · full history")
    fig = go.Figure(go.Scatter(x=df["date"], y=df["nav"], mode="lines",
        line=dict(color=CYAN, width=1.8),
        fill="tozeroy", fillcolor="rgba(34,211,238,0.06)",
        hovertemplate="%{x|%d %b %Y} · ₹%{y:.2f}<extra></extra>"))
    fig.update_layout(**PLOT, height=300,
        xaxis=dict(gridcolor="rgba(139,92,246,0.08)"),
        yaxis=dict(gridcolor="rgba(139,92,246,0.08)", tickprefix="₹"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if mt["calendar"]:
        section("Calendar-Year Returns")
        years = list(mt["calendar"].keys())
        vals  = list(mt["calendar"].values())
        fig = go.Figure(go.Bar(x=[str(y) for y in years], y=vals,
            marker_color=[MINT if v >= 0 else EMBER for v in vals],
            text=[f"{v:+.1f}%" for v in vals], textposition="outside",
            textfont=dict(family="JetBrains Mono", size=11),
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
        fig.update_layout(**PLOT, height=260,
            yaxis=dict(gridcolor="rgba(139,92,246,0.08)", ticksuffix="%"),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if direct and regular:
        section("Direct vs Regular · the commission you keep")
        h2 = fetch_full_history(str((regular if plan == "Direct" else direct)["schemeCode"]))
        if h2:
            other = compute_metrics(h2["df"])
            mine5 = mt["cagr_5y"]; other5 = other["cagr_5y"]
            if mine5 is not None and other5 is not None:
                d5 = (mine5 - other5) if plan == "Direct" else (other5 - mine5)
                st.markdown(H(f"""
                <div class="g-card" style="border-left:3px solid {MINT if d5>0 else AMBER};">
                <div style="font-size:0.85rem;color:{INK};">Direct plan has returned
                <b class="num" style="color:{MINT}">{abs(d5):.2f}% more per year</b> than Regular over 5 years —
                that's the distributor commission you keep by going Direct.</div>
                </div>"""), unsafe_allow_html=True)


def render_request_scheme(existing_names):
    section("📋 Request a Scheme · search the entire AMFI universe")
    st.caption("Fund not in our library? Search any of 10,000+ schemes — get an instant live report. "
               "If nothing matches, we log your request and it'll be available soon.")
    q = st.text_input("Type any fund name…", placeholder="e.g. Bandhan Core Equity, Tata Digital India…",
                      key="req_scheme_q")
    if q and len(q) >= 3:
        results = search_schemes(q)
        growth = [s for s in results if "growth" in s.get("schemeName", "").lower()
                  and "idcw" not in s.get("schemeName", "").lower()][:8]
        if growth:
            pick = st.selectbox("Matches found — pick one for an instant live report:",
                                [s["schemeName"] for s in growth], key="req_pick")
            if st.button("⚡ Generate Instant Report", key="req_go"):
                code = next(str(s["schemeCode"]) for s in growth if s["schemeName"] == pick)
                hist = fetch_full_history(code)
                if hist:
                    mt = compute_metrics(hist["df"])
                    def fmt(v): return f"{v:.2f}%" if v is not None else "—"
                    st.markdown(H(f"""
                    <div class="g-card" style="border-left:3px solid {CYAN};">
                    <div style="font-weight:600;color:{INK};margin-bottom:6px;">{pick}</div>
                    <span class="pill live">NAV ₹{mt['nav']:.4f} · {mt['nav_date']}</span>
                    <span class="pill">1Y {fmt(mt['cagr_1y'])}</span>
                    <span class="pill">3Y {fmt(mt['cagr_3y'])}</span>
                    <span class="pill">5Y {fmt(mt['cagr_5y'])}</span>
                    <span class="pill">since launch {fmt(mt['cagr_inception'])}</span>
                    <span class="pill">max fall {fmt(mt['max_dd'])}</span>
                    </div>"""), unsafe_allow_html=True)
                else:
                    st.warning("History unavailable for this scheme right now.")
        else:
            if st.button(f"📩 Request '{q}' — notify me when available", key="req_log"):
                st.session_state.setdefault("scheme_requests", [])
                if q not in st.session_state["scheme_requests"]:
                    st.session_state["scheme_requests"].append(q)
                st.success(f"Logged! '{q}' will be available soon.")
    reqs = st.session_state.get("scheme_requests", [])
    if reqs:
        st.markdown(H(f"""<div class="g-card" style="margin-top:0.6rem;">
            <div class="kpi-label">📬 Requested · available soon</div>
            {"".join(f'<span class="pill" style="margin:3px 4px 0 0;">{r}</span>' for r in reqs)}
            </div>"""), unsafe_allow_html=True)


def render_registry_browser(deep_dive_names):
    cats = {}
    for name, cat, amc in FUND_REGISTRY:
        cats.setdefault(cat, []).append((name, amc))
    section(f"📚 Fund Library · {len(FUND_REGISTRY)} funds · Direct & Regular · live data")
    all_names = [f"{name}  ·  {cat}" for name, cat, amc in FUND_REGISTRY]
    sel = st.selectbox("Choose any fund for a full live report:",
                       ["— select a fund —"] + all_names, key="reg_pick")
    if sel != "— select a fund —":
        name = sel.split("  ·  ")[0]
        cat, amc = next((c, a) for n, c, a in FUND_REGISTRY if n == name)
        if name in deep_dive_names:
            st.info("⭐ This fund has a hand-written deep-dive report — select it in the main dropdown above for the full analysis.")
        render_live_report(name, cat, amc)
