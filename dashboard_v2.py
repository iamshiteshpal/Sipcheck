# ──────────────────────────────────────────────────────────────────
#  SipCheck – FULL DASHBOARD ENGINE  (dashboard_v2.py)
#  Place in PROJECT ROOT next to dashboard.py.
#
#  WHAT'S NEW IN v2.2
#   · FIXED: black header band gone on every page
#   · NEW — SIP Watchdog: auto-detects missed/overdue/stopped SIPs
#     🔴 Missed (45+ days) · 🟡 Overdue (5–45 days) · ⛔ Inactive (120+)
#   · NEW — Premium SIP Cards: every mandate gets a glass card with
#     amount, status badge, day/last/next/yearly, streak bar
#   · NEW — Realized P&L: 5th KPI + Realized table in My Portfolio
#   · NEW — Full mobile-responsive CSS (tabs scroll, KPIs scale, etc.)
#   · CLEANED: "How to use" only on Smart Rebalancer + Time Machine
#
#  Wiring inside dashboard.py:
#
#      def render_dashboard(data):
#          import dashboard_v2
#          dashboard_v2.render_app(
#              data,
#              legacy={
#                  "transactions": render_transactions,
#                  "alerts":       render_alerts,
#                  "analytics":    render_mf_analytics,
#              })
# ──────────────────────────────────────────────────────────────────
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import math
from datetime import datetime, timedelta

from ui_theme import inject_theme, glass_kpi, page_header, section, C

VIOLET, CYAN, MINT, EMBER, AMBER = C["violet"], C["cyan"], C["mint"], C["ember"], C["amber"]
MUTED, INK = C["muted"], C["ink"]

PLOT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED, size=11, family="Inter"),
            margin=dict(l=10, r=10, t=24, b=10))

DONUT_COLORS = [VIOLET, AMBER, CYAN, MINT, "#3b82f6", EMBER,
                "#f472b6", "#a3e635", "#fb923c", "#818cf8"]

AMC_MAP = {
    "hdfc": "HDFC", "sbi": "SBI", "icici": "ICICI Pru", "axis": "Axis",
    "kotak": "Kotak", "nippon": "Nippon India", "uti": "UTI", "dsp": "DSP",
    "motilal": "Motilal Oswal", "mirae": "Mirae Asset", "parag": "Parag Parikh",
    "ppfas": "Parag Parikh", "invesco": "Invesco", "bandhan": "Bandhan",
    "tata": "Tata", "aditya": "ABSL", "birla": "ABSL", "franklin": "Franklin",
    "quant": "Quant", "edelweiss": "Edelweiss", "canara": "Canara Robeco",
    "lic": "LIC MF", "sundaram": "Sundaram", "hsbc": "HSBC", "iti": "ITI",
    "whiteoak": "WhiteOak", "jm": "JM Financial", "navi": "Navi", "groww": "Groww",
}


def H(s: str) -> str:
    """Collapse HTML to one line so Streamlit never shows it as raw code."""
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def _g(d, *keys, default=None):
    """Defensive getter — returns the first key that exists in dict d."""
    for k in keys:
        if isinstance(d, dict) and d.get(k) not in (None, ""):
            return d[k]
    return default


def howto(text: str):
    with st.expander("ℹ️  How to use this"):
        st.markdown(text)


def amc_of(scheme: str) -> str:
    s = (scheme or "").lower()
    for pre, name in AMC_MAP.items():
        if s.startswith(pre):
            return name
    return (scheme or "Other").split()[0].title()


# ─────────────────────────────────────────────────────────────────
#  SIP MISS DETECTION ENGINE
# ─────────────────────────────────────────────────────────────────
DATE_FMTS = ["%d %b %Y", "%d-%b-%Y", "%d %B %Y", "%Y-%m-%d", "%d/%m/%Y",
             "%d %b, %Y", "%d-%m-%Y"]


def _parse_date(s):
    if not s:
        return None
    if isinstance(s, datetime):
        return s
    s = str(s).strip()
    for fmt in DATE_FMTS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def detect_sip_misses(sips, today=None):
    """Returns list of dicts with miss status per SIP.
    status: 'on_track' | 'overdue' | 'missed' | 'inactive'

    Priority: parser's own flags (status/missed_last_month/days_since_last)
    are trusted first because next_date is recalculated from today() at
    parse time and would always appear future-dated otherwise.
    """
    today = today or datetime.now()
    results = []
    for s in (sips or []):
        name         = str(_g(s, "scheme", "name", "fund", default="SIP"))
        amt          = _g(s, "amount", "sip_amount", default=0) or 0
        # parser uses "dom" (int day-of-month) and "day_label" ("25th")
        day          = _g(s, "dom", "day", "sip_day", default="") or _g(s, "day_label", default="")
        last         = _parse_date(_g(s, "last_date", "last", "last_seen", default=""))
        days_since   = int(_g(s, "days_since_last", default=0) or 0)
        missed_flag  = bool(s.get("missed_last_month", False))
        parser_st    = str(_g(s, "status", default="")).strip().lower()

        # ── Step 1: trust the parser's own classification ──────────
        if parser_st == "inactive":
            status       = "inactive"
            days_over    = days_since
            expected_str = "—"
        elif missed_flag:
            status       = "missed"
            days_over    = max(0, days_since - 30)
            expected_str = ((last + timedelta(days=30)).strftime("%d %b %Y")
                            if last else "—")
        else:
            # ── Step 2: date-math fallback for live SIPs ───────────
            try:
                d = int(str(day).replace("th", "").replace("st", "").replace(
                    "nd", "").replace("rd", "").strip())
            except (ValueError, TypeError):
                d = 0

            if last is None:
                status = "inactive"; days_over = 0; expected_str = "—"
            else:
                if d:
                    m = last.month + 1 if last.month < 12 else 1
                    y = last.year + (1 if last.month == 12 else 0)
                    try:
                        expected = last.replace(year=y, month=m, day=min(d, 28))
                    except Exception:
                        expected = last + timedelta(days=32)
                else:
                    expected = last + timedelta(days=32)

                days_over    = (today - expected).days
                expected_str = expected.strftime("%d %b %Y")

                if days_over > 120:   status = "inactive"
                elif days_over > 45:  status = "missed"
                elif days_over > 5:   status = "overdue"
                else:                 status = "on_track"

        total_months = hit_months = 0
        if last:
            first_possible = _parse_date(_g(s, "first_date", "first", default=""))
            if not first_possible:
                first_possible = last - timedelta(days=180)
            total_months = max(1, round((today - first_possible).days / 30.44))
            hit_months   = min(max(1, round((last - first_possible).days / 30.44)) + 1,
                               total_months)

        results.append({
            "name": name, "amount": amt, "day": day,
            "last_date": last.strftime("%d %b %Y") if last else "—",
            "next_due":  _g(s, "next_date", "next_due", "next", default=expected_str),
            "status": status, "days_overdue": max(0, days_over),
            "expected_str": expected_str,
            "total_months": total_months, "hit_months": hit_months,
            "yearly": round(amt * 12),
            "raw": s,
        })
    return results


# ─────────────────────────────────────────────────────────────────
#  REALIZED P&L ENGINE — finds booked profit from redeemed positions
# ─────────────────────────────────────────────────────────────────
def get_realized(data):
    """Returns (realized_total, closed_positions_list_or_None).
    Checks several possible keys so it works with the existing parser."""
    for k in ("realized_pnl", "realised_pnl", "realized", "booked_pnl",
              "realized_gain", "realised_gain"):
        v = data.get(k)
        if isinstance(v, (int, float)):
            closed = (data.get("closed_positions") or data.get("redeemed") or
                      data.get("exited") or data.get("closed"))
            return float(v), closed

    closed = None
    for k in ("closed_positions", "closed", "redeemed", "exited",
              "closed_holdings", "redeemed_positions"):
        v = data.get(k)
        if isinstance(v, list) and v:
            closed = v
            break
    if closed:
        total = 0.0
        for c in closed:
            p = _g(c, "pnl", "realized_pnl", "profit", "gain", default=None)
            if p is None:
                redeem = _g(c, "redeemed_amount", "redeemed", "redemption_value",
                            "sold_value", default=0) or 0
                inv = _g(c, "invested", "cost", "book_cost", default=0) or 0
                p = redeem - inv
            total += p or 0
        return total, closed

    zero_units = [h for h in data.get("holdings", [])
                  if (h.get("units") or 0) == 0 and h.get("invested")]
    if zero_units:
        total = sum(h.get("pnl", 0) or 0 for h in zero_units)
        return total, zero_units

    return 0.0, None


# ─────────────────────────────────────────────────────────────────
#  LIVE NAV ENGINE  (free mfapi.in · no key · cached 15 min)
# ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def fetch_live_nav(amfi_code: str):
    try:
        r = requests.get(f"https://api.mfapi.in/mf/{amfi_code}/latest", timeout=6)
        if r.status_code == 200:
            d = r.json().get("data", [])
            if d:
                return {"nav": float(d[0]["nav"]), "date": d[0]["date"]}
    except Exception:
        pass
    return None


def apply_live_navs(holdings):
    """Returns (holdings_with_live, live_total, nav_date, hit_count)."""
    live_total, nav_date, hits = 0.0, "", 0
    out = []
    for h in holdings:
        h = dict(h)
        code = _g(h, "amfi", "amfi_code", "code")
        units = _g(h, "units", default=0) or 0
        live = fetch_live_nav(str(code)) if code else None
        if live and units:
            h["live_nav"]   = live["nav"]
            h["live_value"] = round(units * live["nav"], 2)
            h["live_date"]  = live["date"]
            nav_date = live["date"]
            hits += 1
            live_total += h["live_value"]
        else:
            h["live_value"] = h.get("value", 0)
            live_total += h.get("value", 0)
        out.append(h)
    return out, live_total, nav_date, hits


# ─────────────────────────────────────────────────────────────────
#  SCORE ENGINE
# ─────────────────────────────────────────────────────────────────
def compute_scores(holdings, TV, alloc_pct, live_sips):
    n = len(holdings)
    weights = [h["value"] / TV for h in holdings] if holdings else [1.0]

    if 6 <= n <= 12:  s_div = 100
    elif n < 6:       s_div = max(20, n / 6 * 90)
    else:             s_div = max(40, 100 - (n - 12) * 6)

    hhi = sum(w * w for w in weights)
    s_con = max(0, min(100, 100 - (hhi - 1 / max(n, 1)) * 400))

    xirrs = [(h.get("xirr") or 0, h["value"]) for h in holdings if h.get("xirr")]
    wx = sum(x * v for x, v in xirrs) / sum(v for _, v in xirrs) if xirrs else 0
    s_ret = max(0, min(100, 50 + (wx - 12) * 5))

    s_bal = 100.0
    for cat, pct in (alloc_pct or {}).items():
        if pct > 75: s_bal -= (pct - 75) * 2
        if "gold" in cat.lower() and pct > 25: s_bal -= (pct - 25) * 2.5
    s_bal = max(0, s_bal)

    sip_monthly = sum(_g(s, "amount", "sip_amount", default=0) for s in (live_sips or []))
    s_sip = max(0, min(100, (sip_monthly * 12) / TV * 100 * 2.2))

    subs = {"Diversification": round(s_div), "Concentration": round(s_con),
            "Returns": round(s_ret), "Category Balance": round(s_bal),
            "SIP Discipline": round(s_sip)}
    return round(sum(subs.values()) / 5), subs, wx, sip_monthly


def grade(s):
    return ("A+", MINT) if s >= 85 else ("A", MINT) if s >= 75 else \
           ("B", CYAN) if s >= 60 else ("C", AMBER) if s >= 45 else ("D", EMBER)


# ─────────────────────────────────────────────────────────────────
#  MAIN ENTRY — premium top tabs
# ─────────────────────────────────────────────────────────────────
def render_app(data, legacy=None):
    inject_theme()
    _inject_tab_css()
    legacy = legacy or {}

    holdings = sorted(data.get("holdings", []), key=lambda h: -h.get("value", 0))

    use_live = st.session_state.get("v2_use_live", False)
    if use_live:
        holdings, live_total, nav_date, hits = apply_live_navs(holdings)
    else:
        live_total, nav_date, hits = 0, "", 0

    tabs = st.tabs(["🏠 Overview", "📋 My Portfolio", "⏳ SIP Center",
                    "📊 Transactions", "🔔 Alerts", "📈 Analytics"])

    with tabs[0]:
        render_overview(data, holdings, use_live, live_total, nav_date, hits)
    with tabs[1]:
        render_portfolio_v2(data, holdings, use_live)
    with tabs[2]:
        render_sip_v2(data)
    with tabs[3]:
        if legacy.get("transactions"): legacy["transactions"](data)
        else: st.info("Transaction ledger is connected from your 1.0 engine.")
    with tabs[4]:
        if legacy.get("alerts"): legacy["alerts"](data)
        else: render_alerts_v2(data, holdings)
    with tabs[5]:
        if legacy.get("analytics"): legacy["analytics"](data)
        else: st.info("Analytics is connected from your 1.0 engine.")


def _inject_tab_css():
    st.markdown(H(f"""<style>
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px; background: rgba(17,17,48,0.55); backdrop-filter: blur(14px);
        border: 1px solid rgba(139,92,246,0.16); border-radius: 14px;
        padding: 6px; margin-bottom: 0.8rem; }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 9px; padding: 7px 16px; color: {MUTED};
        font-family: 'Space Grotesk', sans-serif; font-size: 0.82rem;
        font-weight: 600; letter-spacing: 0.04em; background: transparent; }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(139,92,246,0.30), rgba(34,211,238,0.16)) !important;
        color: {INK} !important;
        box-shadow: 0 0 18px -6px {VIOLET}; border: 1px solid rgba(139,92,246,0.45); }}
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{
        display: none; }}
    </style>"""), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────
def render_overview(data, holdings, use_live, live_total, nav_date, hits):
    TV_cas = data.get("total_value", 0) or 1
    TI = data.get("total_invested", 0) or 1
    TV = live_total if (use_live and live_total) else TV_cas
    PNL = TV - TI
    name = (data.get("investor_name", "Investor") or "Investor").split()[0].title()

    score, subs, wxirr, sip_monthly = compute_scores(
        holdings, TV, data.get("alloc_pct", {}), data.get("live_sips", []))
    g_letter, g_color = grade(score)

    # header + LIVE NAV control
    hc1, hc2 = st.columns([5, 1.6])
    with hc1:
        src = (f"LIVE NAV · {nav_date} · {hits}/{len(holdings)} funds"
               if (use_live and hits) else f"CAS NAV · {data.get('statement_date', '')}")
        page_header(f"Welcome back, {name} 👋", f"{src} · SipCheck", live=use_live and hits > 0)
    with hc2:
        if st.button("↻  Refresh Live NAV", use_container_width=True, key="v2_live_btn"):
            fetch_live_nav.clear()
            st.session_state["v2_use_live"] = True
            st.rerun()
        if use_live and st.button("← Back to CAS values", use_container_width=True, key="v2_cas_btn"):
            st.session_state["v2_use_live"] = False
            st.rerun()

    # hero health ring
    circ = 2 * math.pi * 84
    dash = circ * score / 100
    bars = ""
    for k, v in subs.items():
        bc = grade(v)[1]
        bars += H(f"""
        <div>
        <div style="display:flex;justify-content:space-between;font-size:0.72rem;margin-bottom:4px;">
        <span style="color:{MUTED}">{k}</span>
        <span class="num" style="color:{bc};font-weight:600">{v}</span></div>
        <div style="height:5px;background:rgba(139,92,246,0.12);border-radius:3px;overflow:hidden;">
        <div style="height:100%;width:{v}%;border-radius:3px;
        background:linear-gradient(90deg,{VIOLET},{bc});box-shadow:0 0 8px {bc}66;"></div>
        </div></div>""")

    st.markdown(H(f"""
    <div class="g-card rise" style="display:flex;align-items:center;gap:2.2rem;
    padding:1.6rem 2rem;flex-wrap:wrap;">
    <div style="position:relative;width:200px;height:200px;flex-shrink:0;">
    <svg width="200" height="200" viewBox="0 0 200 200" style="transform:rotate(-90deg)">
    <defs><linearGradient id="ringG" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="{VIOLET}"/>
    <stop offset="60%" stop-color="{CYAN}"/>
    <stop offset="100%" stop-color="{MINT}"/>
    </linearGradient></defs>
    <circle cx="100" cy="100" r="84" fill="none" stroke="rgba(139,92,246,0.12)" stroke-width="10"/>
    <circle cx="100" cy="100" r="84" fill="none" stroke="url(#ringG)" stroke-width="10"
    stroke-linecap="round" stroke-dasharray="{dash:.0f} {circ:.0f}"
    style="filter:drop-shadow(0 0 10px rgba(139,92,246,0.6));">
    <animate attributeName="stroke-dasharray" from="0 {circ:.0f}"
    to="{dash:.0f} {circ:.0f}" dur="1.4s" calcMode="spline"
    keySplines="0.22 1 0.36 1" fill="freeze"/></circle>
    <circle cx="100" cy="16" r="5" fill="{CYAN}">
    <animateTransform attributeName="transform" type="rotate"
    from="0 100 100" to="{score*3.6:.0f} 100 100" dur="1.4s"
    calcMode="spline" keySplines="0.22 1 0.36 1" fill="freeze"/></circle>
    </svg>
    <div style="position:absolute;inset:0;display:flex;flex-direction:column;
    align-items:center;justify-content:center;">
    <div class="num" style="font-size:2.6rem;font-weight:700;color:{INK};line-height:1;">{score}</div>
    <div style="font-size:0.65rem;letter-spacing:0.15em;color:{MUTED};margin-top:2px;">HEALTH SCORE</div>
    <div class="num" style="font-size:0.95rem;font-weight:700;color:{g_color};margin-top:4px;">
    GRADE {g_letter}</div>
    </div></div>
    <div style="flex:1;min-width:300px;display:grid;grid-template-columns:1fr 1fr;gap:0.8rem 2rem;">
    {bars}
    <div style="align-self:end;">
    <span class="pill">wtd XIRR
    <b class="num" style="color:{MINT if wxirr>=12 else AMBER};margin-left:4px">{wxirr:.1f}%</b>
    </span>
    <span class="pill" style="margin-left:6px">{len(holdings)} funds</span>
    </div></div></div>"""), unsafe_allow_html=True)

    # KPI strip — 5 cards including Realized P&L
    pnl_pct = PNL / TI * 100 if TI else 0
    realized, closed_pos = get_realized(data)
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        glass_kpi("Total Wealth" + (" · LIVE" if use_live and hits else ""),
                  f"₹{TV:,.0f}", f"invested ₹{TI:,.0f}", "", 1)
    with k2:
        glass_kpi("Unrealized P&L", f"₹{PNL:,.0f}",
                  f"{'▲' if PNL >= 0 else '▼'} {abs(pnl_pct):.2f}% all-time",
                  "up" if PNL >= 0 else "down", 2)
    with k3:
        glass_kpi("Realized P&L", f"₹{realized:,.0f}",
                  f"booked from {len(closed_pos)} exits" if closed_pos
                  else "no redemptions in CAS",
                  "up" if realized > 0 else "down" if realized < 0 else "", 3)
    with k4:
        glass_kpi("Weighted XIRR", f"{wxirr:.2f}%", "benchmark 12.00%",
                  "up" if wxirr >= 12 else "warn", 3)
    with k5:
        glass_kpi("Monthly SIP", f"₹{sip_monthly:,.0f}",
                  f"{len(data.get('live_sips', []))} active mandates", "up", 4)

    # ── SIP WATCHDOG — auto-detected missed/overdue/inactive SIPs ──
    all_sips = ((data.get("live_sips", []) or []) +
                (data.get("inactive_sips", data.get("dead_sips", [])) or []))
    misses = [m for m in detect_sip_misses(all_sips)
              if m["status"] in ("missed", "overdue", "inactive")]
    if misses:
        section("SIP Watchdog")
        order = {"missed": 0, "inactive": 1, "overdue": 2}
        for m in sorted(misses, key=lambda m: order.get(m["status"], 9))[:5]:
            if m["status"] == "missed":
                cls, icon = "critical", "🔴"
                title = f"Missed SIP — {m['name'][:40]}"
                sub = (f"₹{m['amount']:,.0f}/month · expected {m['expected_str']} · "
                       f"<b>{m['days_overdue']} days overdue</b> — check your bank mandate / balance")
            elif m["status"] == "inactive":
                cls, icon = "critical", "⛔"
                title = f"Inactive SIP — {m['name'][:40]}"
                sub = (f"₹{m['amount']:,.0f}/month · last seen {m['last_date']} — "
                       f"restart it or you lose ₹{m['yearly']:,.0f}/year of investing")
            else:
                cls, icon = "warning", "🟡"
                title = f"SIP overdue — {m['name'][:40]}"
                sub = (f"₹{m['amount']:,.0f}/month · expected {m['expected_str']} · "
                       f"{m['days_overdue']} days late — may still be processing")
            st.markdown(H(f"""
            <div class="alert-banner {cls} rise">
            <div class="alert-icon">{icon}</div>
            <div class="alert-body">
            <div class="alert-title">{title}</div>
            <div class="alert-sub">{sub}</div>
            </div></div>"""), unsafe_allow_html=True)

    # LIVE SIP STRIP
    sips = data.get("live_sips", []) or []
    if sips:
        section("Live SIP Engine")
        nd = sorted([_g(s, "next_due", "next", "next_date", default="")
                     for s in sips if _g(s, "next_due", "next", "next_date")])
        next_debit = nd[0] if nd else "—"
        upcoming = sorted(sips,
            key=lambda s: str(_g(s, "next_due", "next", "next_date", default="9999")))[:3]
        chips = "".join(H(f"""
            <div style="flex:1;min-width:180px;background:rgba(17,17,48,0.55);
            border:1px solid rgba(52,211,153,0.22);border-left:3px solid {MINT};
            border-radius:12px;padding:0.7rem 0.9rem;">
            <div style="font-size:0.72rem;color:{MUTED};">
            {str(_g(s, 'scheme', 'name', 'fund', default='SIP'))[:28]}</div>
            <div class="num" style="font-size:1rem;font-weight:700;color:{INK};">
            ₹{_g(s, 'amount', 'sip_amount', default=0):,.0f}
            <span style="font-size:0.68rem;color:{MINT};font-weight:600;margin-left:6px;">
            due {_g(s, 'next_due', 'next', 'next_date', default='—')}</span></div>
            </div>""") for s in upcoming)
        st.markdown(H(f"""
        <div class="g-card rise" style="display:flex;gap:0.8rem;flex-wrap:wrap;align-items:stretch;">
        <div style="flex:1;min-width:160px;">
        <div class="kpi-label">Monthly Flow</div>
        <div class="kpi-value" style="color:{MINT}">₹{sip_monthly:,.0f}</div>
        <div class="kpi-sub">₹{sip_monthly*12:,.0f} / year committed</div></div>
        <div style="flex:1;min-width:140px;">
        <div class="kpi-label">Next Debit</div>
        <div class="kpi-value" style="color:{AMBER};font-size:1.2rem;">{next_debit}</div>
        <div class="kpi-sub">{len(sips)} live mandates</div></div>
        {chips}</div>"""), unsafe_allow_html=True)

    # WEALTH JOURNEY + CATEGORY MIX + AMC ALLOCATION
    cL, cM, cR = st.columns([1.5, 1, 1])
    with cL:
        section("Wealth Journey")
        df = pd.DataFrame([{
            "fund": h["scheme"][:22],
            "Invested": h.get("invested", 0),
            "Current": h.get("live_value", h.get("value", 0)),
        } for h in holdings])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["fund"], y=df["Invested"], name="Invested",
            marker_color="rgba(139,92,246,0.45)",
            hovertemplate="₹%{y:,.0f}<extra>invested</extra>"))
        fig.add_trace(go.Bar(x=df["fund"], y=df["Current"], name="Current",
            marker=dict(color=df["Current"],
                        colorscale=[[0, CYAN], [1, MINT]], showscale=False),
            hovertemplate="₹%{y:,.0f}<extra>current</extra>"))
        fig.update_layout(**PLOT, height=300, barmode="group",
            legend=dict(orientation="h", y=1.14, bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(tickangle=-30, gridcolor="rgba(0,0,0,0)", tickfont=dict(size=8.5)),
            yaxis=dict(gridcolor="rgba(139,92,246,0.08)", tickprefix="₹", separatethousands=True))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with cM:
        section("Category Mix")
        alloc = data.get("alloc_values", {})
        if alloc:
            fig = go.Figure(go.Pie(
                labels=list(alloc.keys()), values=list(alloc.values()), hole=0.66,
                marker=dict(colors=DONUT_COLORS, line=dict(color=C["void"], width=3)),
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} · %{percent}<extra></extra>"))
            fig.add_annotation(text=f"<b>₹{TV/100000:.1f}L</b>", showarrow=False,
                               font=dict(family="JetBrains Mono", size=14, color=INK))
            fig.update_layout(**PLOT, height=300,
                legend=dict(orientation="h", y=-0.15, bgcolor="rgba(0,0,0,0)", font=dict(size=9)))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with cR:
        section("AMC Allocation")
        amc_vals = {}
        for h in holdings:
            amc = amc_of(h.get("scheme", ""))
            amc_vals[amc] = amc_vals.get(amc, 0) + h.get("live_value", h.get("value", 0))
        if amc_vals:
            top_amc = max(amc_vals, key=amc_vals.get)
            fig = go.Figure(go.Pie(
                labels=list(amc_vals.keys()), values=list(amc_vals.values()), hole=0.66,
                marker=dict(colors=DONUT_COLORS, line=dict(color=C["void"], width=3)),
                textinfo="none",
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} · %{percent}<extra></extra>"))
            fig.add_annotation(text=f"<b>{len(amc_vals)} AMCs</b>", showarrow=False,
                               font=dict(family="JetBrains Mono", size=13, color=INK))
            fig.update_layout(**PLOT, height=300,
                legend=dict(orientation="h", y=-0.15, bgcolor="rgba(0,0,0,0)", font=dict(size=9)))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            if amc_vals[top_amc] / TV > 0.40:
                st.caption(f"⚠️ {top_amc} holds {amc_vals[top_amc]/TV*100:.0f}% of your wealth "
                           f"— consider spreading across fund houses.")

    # RISK RADAR + CONCENTRATION MAP
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
        fig.update_layout(**PLOT, height=310, showlegend=False,
            polar=dict(bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(range=[0, 100],
                    gridcolor="rgba(139,92,246,0.12)",
                    tickfont=dict(size=8, color=MUTED)),
                angularaxis=dict(
                    gridcolor="rgba(139,92,246,0.12)",
                    tickfont=dict(size=10, color=INK))))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with cB:
        section("Concentration Map")
        df = pd.DataFrame([{
            "fund": h["scheme"][:34],
            "cat":  h.get("category", "Other"),
            "value": h.get("live_value", h.get("value", 0)),
            "w":    h.get("value", 0) / (data.get("total_value") or 1) * 100,
            "xirr": h.get("xirr") or 0,
        } for h in holdings])
        fig = go.Figure(go.Treemap(
            labels=df["fund"], parents=df["cat"], values=df["value"],
            marker=dict(
                colors=df["xirr"],
                colorscale=[[0, EMBER], [0.5, "#1e2338"], [1, MINT]],
                cmid=10, line=dict(color=C["void"], width=2)),
            customdata=np.stack([df["w"], df["xirr"]], axis=-1),
            hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} · %{customdata[0]:.1f}%<br>"
                          "XIRR %{customdata[1]:.1f}%<extra></extra>",
            textfont=dict(family="Inter", size=11, color=INK)))
        fig.update_layout(**PLOT, height=310)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ADVISOR FLAGS
    TVx = data.get("total_value", 0) or 1
    laggards = [h for h in holdings
                if (h.get("xirr") or 99) < 8 and h.get("value", 0) > TVx * 0.05]
    flags = []
    for h in holdings:
        w = h.get("value", 0) / TVx * 100
        if w > 30:
            flags.append(f"⚠️ <b>{h['scheme'][:42]}</b> is <b>{w:.1f}%</b> "
                         f"of your portfolio — single-fund risk.")
    for cat, pct in data.get("alloc_pct", {}).items():
        if "gold" in cat.lower() and pct > 25:
            flags.append(f"⚠️ <b>{cat}</b> at <b>{pct:.1f}%</b> — "
                         f"above the 25% commodities comfort zone.")
    for h in laggards[:2]:
        flags.append(f"📉 <b>{h['scheme'][:42]}</b> XIRR is only "
                     f"<b>{h.get('xirr', 0):.1f}%</b> — review or switch.")
    if flags:
        section("Advisor Flags")
        for f in flags[:4]:
            st.markdown(H(f"""<div class="g-card" style="padding:0.7rem 1rem;font-size:0.84rem;
                margin-bottom:6px;border-left:3px solid {AMBER};">{f}</div>"""),
                unsafe_allow_html=True)

    # SMART REBALANCER
    section("Smart Rebalancer")
    howto("""
1. Pick a strategy — **Aggressive** (younger, long horizon), **Balanced**, **Conservative** (nearing goals), or **Custom** sliders.
2. Purple bar = where you are today; teal bar = the target.
3. The cards below give the **exact ₹** — "Add" means invest more there (or point SIPs there); "Trim" means stop adding (or redeem, mind exit-load/tax).
""")
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
        gd = c2.slider("Gold %", 0, 100 - eq, min(20, 100 - eq), key="v2_gd")
        tgt = {"Equity Funds": eq, "Gold & Commodities": gd, "Debt / Hybrid": 100 - eq - gd}
        c3.metric("Debt / Hybrid %", f"{100-eq-gd}")
    else:
        tgt = presets[preset]

    cur = {k: v / TVx * 100 for k, v in data.get("alloc_values", {}).items()}
    rows = []
    for cat in sorted(set(list(cur.keys()) + list(tgt.keys()))):
        c_pct, t_pct = cur.get(cat, 0), tgt.get(cat, 0)
        rows.append((cat, c_pct, t_pct, (t_pct - c_pct) / 100 * TVx))
    fig = go.Figure()
    fig.add_trace(go.Bar(y=[r[0] for r in rows], x=[r[1] for r in rows], orientation="h",
        name="Current", marker_color="rgba(139,92,246,0.75)", width=0.32,
        hovertemplate="Current %{x:.1f}%<extra></extra>"))
    fig.add_trace(go.Bar(y=[r[0] for r in rows], x=[r[2] for r in rows], orientation="h",
        name="Target", marker_color="rgba(34,211,238,0.55)", width=0.32,
        hovertemplate="Target %{x:.1f}%<extra></extra>"))
    fig.update_layout(**PLOT, height=200, barmode="group",
        legend=dict(orientation="h", y=1.18, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="rgba(139,92,246,0.1)", ticksuffix="%"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    mcols = st.columns(len(rows)) if rows else []
    for col, (cat, c_pct, t_pct, move) in zip(mcols, rows):
        with col:
            verb = "Add" if move > 0 else "Trim" if move < 0 else "Hold"
            glass_kpi(cat, f"{verb} ₹{abs(move):,.0f}", f"{c_pct:.1f}% → {t_pct:.0f}%",
                      "up" if move > 0 else "down" if move < 0 else "", 2)

    # WEALTH TIME MACHINE
    section("Wealth Time Machine · 1,000 simulated futures")
    howto("""
1. Set your **horizon**, **monthly SIP**, **expected return** (default = your real XIRR) and **volatility** (15% = typical equity).
2. The engine simulates **1,000 random market futures**. Faint lines = sample futures; bold cyan = median; purple band = where 80% of outcomes land; dotted grey = money you actually put in.
3. Read the 3 cards as best case / realistic / tough case — planning beats prediction.
""")
    m1, m2, m3, m4 = st.columns(4)
    years   = m1.slider("Horizon (years)", 1, 30, 10, key="v2_yrs")
    sip_amt = m2.number_input("Monthly SIP (₹)", 0, 1_000_000,
                              int(sip_monthly or 9000), step=500, key="v2_sip")
    exp_ret = m3.slider("Expected return %", 4.0, 20.0,
                        float(max(8.0, min(round(wxirr, 1), 16.0))), 0.5, key="v2_ret")
    vol     = m4.slider("Volatility %", 5.0, 30.0, 15.0, 0.5, key="v2_vol")
    W = _monte_carlo(TVx, sip_amt, years, exp_ret, vol)
    x = np.arange(W.shape[1]) / 12
    p10, p50, p90 = np.percentile(W, [10, 50, 90], axis=0)
    inv_line = TVx + sip_amt * np.arange(W.shape[1])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=p90, line=dict(width=0), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=x, y=p10, fill="tonexty",
        fillcolor="rgba(139,92,246,0.14)", line=dict(width=0),
        name="10–90% band", hoverinfo="skip"))
    for i in range(0, 60, 4):
        fig.add_trace(go.Scatter(x=x, y=W[i], mode="lines", showlegend=False,
            hoverinfo="skip", line=dict(color="rgba(34,211,238,0.07)", width=1)))
    fig.add_trace(go.Scatter(x=x, y=p50, name="Median path",
        line=dict(color=CYAN, width=2.5),
        hovertemplate="Yr %{x:.1f} · ₹%{y:,.0f}<extra>median</extra>"))
    fig.add_trace(go.Scatter(x=x, y=inv_line, name="Amount invested",
        line=dict(color=MUTED, width=1.5, dash="dot"),
        hovertemplate="Yr %{x:.1f} · ₹%{y:,.0f}<extra>invested</extra>"))
    fig.update_layout(**PLOT, height=350,
        legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title="Years", gridcolor="rgba(139,92,246,0.08)"),
        yaxis=dict(gridcolor="rgba(139,92,246,0.08)", tickprefix="₹", separatethousands=True))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    r1, r2, r3 = st.columns(3)
    with r1: glass_kpi("Pessimistic (P10)", f"₹{p10[-1]:,.0f}", f"after {years} years", "down", 1)
    with r2: glass_kpi("Median outcome",    f"₹{p50[-1]:,.0f}", f"vs ₹{inv_line[-1]:,.0f} invested", "up", 2)
    with r3: glass_kpi("Optimistic (P90)",  f"₹{p90[-1]:,.0f}",
                        f"{(p90[-1]/max(inv_line[-1],1)):.1f}× of invested", "up", 3)

    # ADVISOR VERDICT
    section("Advisor Verdict")
    if st.button("✦ Generate written review", key="v2_verdict"):
        st.session_state["v2_review"] = _verdict_html(
            data, holdings, TVx, wxirr, subs, sip_monthly, laggards)
    if "v2_review" in st.session_state:
        st.markdown(H(f"""<div class="g-card" style="border-left:3px solid {VIOLET};">
            <div class="kpi-label" style="color:{VIOLET}">✦ Advisor verdict · rule engine ·
            {datetime.now().strftime('%d %b, %I:%M %p')}</div>
            {st.session_state['v2_review']}</div>"""), unsafe_allow_html=True)

    st.markdown(H(f"""<div style="text-align:center;padding:2.5rem 0 1rem;color:{C['faint']};
        font-size:0.7rem;">SipCheck · live NAVs via mfapi.in (free) · everything else
        runs on your device · heuristics for self-review, not investment advice</div>"""),
        unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  TAB 2 — MY PORTFOLIO (ledger with live values + realized P&L)
# ─────────────────────────────────────────────────────────────────
def render_portfolio_v2(data, holdings, use_live):
    page_header("Portfolio Ledger", "Every holding · CAS vs Live · color-coded XIRR")

    cats = {}
    for h in holdings:
        cats.setdefault(h.get("category", "Other"), []).append(h)

    for ci, (cat, hs) in enumerate(cats.items()):
        cat_val = sum(h.get("live_value", h.get("value", 0)) for h in hs)
        dot = DONUT_COLORS[ci % len(DONUT_COLORS)]
        st.markdown(H(f"""<div class="sec">
            <span class="tick" style="background:{dot};box-shadow:0 0 12px {dot};"></span>
            <span class="t">{cat} · ₹{cat_val:,.0f} · {len(hs)} funds</span>
            <span class="line"></span></div>"""), unsafe_allow_html=True)
        rows = []
        for h in hs:
            inv = h.get("invested", 0)
            val = h.get("live_value", h.get("value", 0))
            pnl = val - inv
            rows.append({
                "Scheme":     h.get("scheme", "")[:48],
                "Invested":   f"₹{inv:,.0f}",
                "CAS Value":  f"₹{h.get('value', 0):,.0f}",
                "Live Value": f"₹{h['live_value']:,.0f}" if use_live and h.get("live_nav") else "—",
                "Live NAV":   (f"₹{h['live_nav']:.4f} ({h.get('live_date', '')})"
                               if use_live and h.get("live_nav")
                               else f"₹{h.get('cas_nav', 0):.4f} (CAS)" if h.get("cas_nav") else "—"),
                "P&L":        f"{'▲' if pnl >= 0 else '▼'} ₹{abs(pnl):,.0f}",
                "XIRR %":     f"{h.get('xirr', 0):.2f}" if h.get("xirr") is not None else "—",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Realized / booked profit — fully exited positions
    realized, closed_pos = get_realized(data)
    if closed_pos:
        st.markdown(H(f"""<div class="sec">
            <span class="tick" style="background:{MINT};box-shadow:0 0 12px {MINT};"></span>
            <span class="t">Realized P&amp;L · ₹{realized:,.0f} booked · {len(closed_pos)} exits</span>
            <span class="line"></span></div>"""), unsafe_allow_html=True)
        rrows = []
        for c in closed_pos:
            inv = _g(c, "invested", "cost", "book_cost", default=0) or 0
            # "redeemed" is the key used by dashboard.py's parser
            red = _g(c, "redeemed_amount", "redeemed", "redemption_value",
                     "sold_value", default=0) or 0
            p   = _g(c, "pnl", "realized_pnl", "profit", "gain", default=None)
            if p is None:
                p = red - inv
            rrows.append({
                "Scheme":     str(_g(c, "scheme", "name", default="—"))[:48],
                "Invested":   f"₹{inv:,.0f}",
                "Redeemed":   f"₹{red:,.0f}" if red else "—",
                "Booked P&L": f"{'▲' if p >= 0 else '▼'} ₹{abs(p):,.0f}",
                "Exit Date":  _g(c, "exit_date", "redeemed_date", "last_date", default="—"),
            })
        st.dataframe(pd.DataFrame(rrows), use_container_width=True, hide_index=True)
    elif realized:
        st.caption(f"💰 Realized P&L: ₹{realized:,.0f} (booked profit from past redemptions)")

    # Bubble map — invested vs XIRR, sized by value
    section("Bubble Map · Invested vs XIRR")
    df = pd.DataFrame([{
        "scheme":   h["scheme"][:28],
        "invested": h.get("invested", 0),
        "xirr":     h.get("xirr") or 0,
        "value":    h.get("live_value", h.get("value", 0)),
        "cat":      h.get("category", "Other"),
    } for h in holdings])
    if not df.empty:
        fig = go.Figure()
        for ci, cat in enumerate(df["cat"].unique()):
            d = df[df["cat"] == cat]
            fig.add_trace(go.Scatter(
                x=d["invested"], y=d["xirr"], mode="markers+text",
                name=cat, text=d["scheme"].str[:14], textposition="top center",
                textfont=dict(size=8.5, color=MUTED),
                marker=dict(
                    size=np.sqrt(d["value"]) / np.sqrt(max(df["value"].max(), 1)) * 46 + 8,
                    color=DONUT_COLORS[ci % len(DONUT_COLORS)], opacity=0.78,
                    line=dict(color=C["void"], width=1.5)),
                customdata=d["value"],
                hovertemplate="<b>%{text}</b><br>Invested ₹%{x:,.0f}<br>"
                              "XIRR %{y:.1f}%<br>Value ₹%{customdata:,.0f}<extra></extra>"))
        fig.add_hline(y=12, line=dict(color="rgba(52,211,153,0.4)", dash="dot", width=1),
                      annotation_text="12% benchmark", annotation_font_color=MUTED)
        fig.update_layout(**PLOT, height=380,
            legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(title="Invested (₹)", gridcolor="rgba(139,92,246,0.08)",
                       tickprefix="₹", separatethousands=True),
            yaxis=dict(title="XIRR %", gridcolor="rgba(139,92,246,0.08)", ticksuffix="%"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
#  TAB 3 — SIP CENTER (premium glass cards)
# ─────────────────────────────────────────────────────────────────
def render_sip_v2(data):
    page_header("SIP Center", "Every mandate, its rhythm, and what it costs you per year")
    sips = data.get("live_sips", []) or []
    dead = data.get("inactive_sips", data.get("dead_sips", [])) or []
    monthly = sum(_g(s, "amount", "sip_amount", default=0) for s in sips)
    nd = sorted([str(_g(s, "next_due", "next", "next_date", default=""))
                 for s in sips if _g(s, "next_due", "next", "next_date")])

    k1, k2, k3, k4 = st.columns(4)
    with k1: glass_kpi("Monthly Commitment", f"₹{monthly:,.0f}", f"{len(sips)} live mandates", "up", 1)
    with k2: glass_kpi("Annual Commitment",  f"₹{monthly*12:,.0f}", "auto-invested per year", "", 2)
    with k3: glass_kpi("Next Debit", nd[0] if nd else "—", "keep balance ready", "warn", 3)
    with k4: glass_kpi("Inactive SIPs", f"{len(dead)}", "stopped mandates",
                        "down" if dead else "up", 4)

    view = st.radio("View",
        [f"🟢 Live ({len(sips)})", f"🔴 Inactive ({len(dead)})"],
        horizontal=True, label_visibility="collapsed", key="v2_sipview")
    is_live_view = view.startswith("🟢")
    show = sips if is_live_view else dead
    if not show:
        st.info("Nothing here — all clear!")
        return

    # Premium SIP cards — one glowing glass card per mandate
    cards_html = ""
    for m in sorted(detect_sip_misses(show),
                    key=lambda m: ({"missed": 0, "inactive": 1, "overdue": 2, "on_track": 3}
                                   .get(m["status"], 9), -m["amount"])):
        if not is_live_view or m["status"] == "inactive":
            badge     = '<span class="sip-badge dead">⛔ INACTIVE</span>'
            card_cls  = "missed"
            bar_cls   = "bad"
            streak_note = f"last seen {m['last_date']} — losing ₹{m['yearly']:,.0f}/yr"
        elif m["status"] == "missed":
            badge     = f'<span class="sip-badge missed">🔴 MISSED · {m["days_overdue"]}d</span>'
            card_cls  = "missed"
            bar_cls   = "bad"
            streak_note = f"expected {m['expected_str']} — check bank mandate"
        elif m["status"] == "overdue":
            badge     = f'<span class="sip-badge overdue">🟡 OVERDUE · {m["days_overdue"]}d</span>'
            card_cls  = "overdue"
            bar_cls   = "bad"
            streak_note = f"expected {m['expected_str']} — may be processing"
        else:
            badge     = '<span class="sip-badge live">🟢 ON TRACK</span>'
            card_cls  = ""
            bar_cls   = ""
            streak_note = "running smoothly"

        pct = round(m["hit_months"] / m["total_months"] * 100) if m["total_months"] else 100
        cards_html += H(f"""
        <div class="sip-card {card_cls}">
        <div class="sip-name">{m['name'][:42]}</div>
        <div class="sip-amt">₹{m['amount']:,.2f}
        <span style="font-size:0.7rem;color:{MUTED};font-weight:500;">/month</span>
        {badge}</div>
        <div class="sip-detail">
        <span>Day: <b>{m['day'] or '—'}</b></span>
        <span>Yearly: <b>₹{m['yearly']:,.0f}</b></span>
        <span>Last: <b>{m['last_date']}</b></span>
        <span>Next: <b>{m['next_due']}</b></span>
        </div>
        <div class="sip-bar">
        <div class="sip-bar-fill {bar_cls}" style="width:{pct}%;"></div></div>
        <div class="sip-streak">⚡ {m['hit_months']}/{m['total_months']} months · {streak_note}</div>
        </div>""")
    st.markdown(f'<div class="sip-grid">{cards_html}</div>', unsafe_allow_html=True)

    if sips:
        section("Where your monthly ₹ flows")
        df = pd.DataFrame([{
            "scheme": str(_g(s, "scheme", "name", "fund", default="SIP"))[:26],
            "amt":    _g(s, "amount", "sip_amount", default=0),
        } for s in sips]).sort_values("amt")
        fig = go.Figure(go.Bar(
            x=df["amt"], y=df["scheme"], orientation="h",
            marker=dict(color=df["amt"], colorscale=[[0, VIOLET], [1, MINT]], showscale=False),
            hovertemplate="₹%{x:,.0f}/month<extra></extra>"))
        fig.update_layout(**PLOT, height=max(200, 34 * len(df)),
            xaxis=dict(gridcolor="rgba(139,92,246,0.08)", tickprefix="₹"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────
#  TAB 5 fallback — ALERTS (used only if legacy not passed)
# ─────────────────────────────────────────────────────────────────
def render_alerts_v2(data, holdings):
    page_header("Alerts & Insights", "Auto-generated from your CAS — no setup needed")
    TV = data.get("total_value", 0) or 1
    cards = []
    for s in (data.get("inactive_sips", []) or []):
        cards.append(("ACTION REQUIRED", EMBER, "Inactive SIP",
                      f"{_g(s, 'scheme', 'name', default='A fund')} — "
                      f"last processed {_g(s, 'last_date', 'last', default='a while ago')}"))
    for h in holdings:
        pnl = h.get("value", 0) - h.get("invested", 0)
        if pnl < 0:
            cards.append(("INFO", AMBER, "Unrealized Loss",
                          f"{h['scheme'][:40]} — down ₹{abs(pnl):,.2f} from cost"))
        if h.get("value", 0) / TV > 0.30:
            cards.append(("RISK", AMBER, "Concentration",
                          f"{h['scheme'][:40]} is {h['value']/TV*100:.1f}% of your portfolio"))
    if not cards:
        st.success("✓ No alerts — portfolio looks clean.")
    for tag, color, title, body in cards[:12]:
        st.markdown(H(f"""<div class="g-card" style="margin-bottom:8px;border-left:3px solid {color};">
            <div style="font-size:0.62rem;font-weight:700;letter-spacing:0.12em;color:{color};">{tag}</div>
            <div style="font-weight:600;color:{INK};margin:2px 0;">{title}</div>
            <div style="font-size:0.82rem;color:{MUTED};">{body}</div></div>"""),
            unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _monte_carlo(start, sip, yrs, mu, sigma, paths=1000, seed=7):
    rng = np.random.default_rng(seed)
    months = yrs * 12
    rets = rng.normal(mu / 100 / 12, sigma / 100 / np.sqrt(12), size=(paths, months))
    w = np.empty((paths, months + 1))
    w[:, 0] = start
    for t in range(months):
        w[:, t + 1] = (w[:, t] + sip) * (1 + rets[:, t])
    return w


def _verdict_html(data, holdings, TV, wxirr, subs, sip_monthly, laggards):
    strengths, risks, steps = [], [], []
    top = holdings[0] if holdings else None
    top_w = top.get("value", 0) / TV * 100 if top else 0
    gold_pct = next((p for c, p in data.get("alloc_pct", {}).items()
                     if "gold" in c.lower()), 0)

    if wxirr >= 14:
        strengths.append(f"Your money is compounding at a weighted XIRR of {wxirr:.1f}%, "
                         f"comfortably ahead of the 12% long-term equity benchmark.")
    elif wxirr >= 10:
        strengths.append(f"Weighted XIRR of {wxirr:.1f}% is in a healthy band, "
                         f"close to long-term market averages.")
    if subs["SIP Discipline"] >= 70:
        strengths.append(f"SIP discipline is strong — ₹{sip_monthly:,.0f} flows in every month, "
                         f"smoothing out volatility automatically.")
    if 6 <= len(holdings) <= 12:
        strengths.append(f"{len(holdings)} funds is the sweet spot — diversified without "
                         f"becoming impossible to track.")
    if subs["Concentration"] >= 70:
        strengths.append("No single fund dominates the portfolio, so one bad scheme "
                         "can't sink the ship.")

    if top is not None and top_w > 30:
        risks.append(f"{top['scheme'][:45]} alone is {top_w:.1f}% of your wealth — "
                     f"a stumble in this one fund hits everything.")
    if gold_pct > 25:
        risks.append(f"Gold & commodities at {gold_pct:.1f}% is above the usual 15–25% "
                     f"hedge zone; gold protects but rarely compounds like equity.")
    if laggards:
        risks.append(f"{laggards[0]['scheme'][:45]} is dragging at "
                     f"{laggards[0].get('xirr', 0):.1f}% XIRR — below even FD-level returns.")
    if subs["Category Balance"] < 55:
        risks.append("The category mix is lopsided — most of the portfolio behaves "
                     "the same way in a crash.")
    if len(holdings) > 12:
        risks.append(f"{len(holdings)} funds is over-diversified — many likely hold the same stocks.")
    if not risks:
        risks.append("No major structural red flags — the main risk is simply "
                     "staying invested through drawdowns.")

    if top is not None and top_w > 30:
        steps.append(f"Direct your next few SIPs away from {top['scheme'][:35]} into smaller "
                     f"holdings until it drops below ~25% weight.")
    elif laggards:
        steps.append(f"Set a 2-quarter watch on {laggards[0]['scheme'][:35]}; if XIRR stays "
                     f"under 8%, switch to a category leader.")
    elif gold_pct > 25:
        steps.append("Pause fresh gold purchases and let equity SIPs naturally rebalance "
                     "the mix over 6–12 months.")
    else:
        steps.append(f"Keep the engine running — a 10% annual step-up on your "
                     f"₹{sip_monthly:,.0f} SIP dramatically bends the wealth curve.")

    out = ""
    for s in strengths[:2]:
        out += H(f"""<div style="display:flex;gap:10px;margin-bottom:10px;">
            <span style="color:{MINT};font-weight:700;">✓</span>
            <span style="font-size:0.88rem;line-height:1.6;color:{INK};">{s}</span></div>""")
    for r in risks[:2]:
        out += H(f"""<div style="display:flex;gap:10px;margin-bottom:10px;">
            <span style="color:{AMBER};font-weight:700;">!</span>
            <span style="font-size:0.88rem;line-height:1.6;color:{INK};">{r}</span></div>""")
    out += H(f"""<div style="display:flex;gap:10px;margin-top:14px;padding-top:12px;
        border-top:1px solid rgba(139,92,246,0.15);">
        <span style="color:{CYAN};font-weight:700;">→</span>
        <span style="font-size:0.88rem;line-height:1.6;color:{INK};">
        <b>Next step:</b> {steps[0]}</span></div>""")
    return out


# back-compat: old wiring "render_v2(data)" still works
def render_v2(data, live_data=None):
    render_app(data)
