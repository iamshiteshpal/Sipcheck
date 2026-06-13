import streamlit as st
import streamlit.components.v1 as components
from sidebar_v2 import render_sidebar
from home_v2 import render_home_v2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import io
import json
import tempfile
import datetime
import requests
from datetime import date
from collections import Counter, defaultdict
from pyxirr import xirr
import casparser

PLOT_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Instrument Sans', color='#718096'),
    margin=dict(l=0, r=0, t=10, b=10),
)
GRID = 'rgba(255,255,255,0.04)'
C_GAIN = '#48bb78'
C_LOSS = '#fc8181'
C_ACCENT = '#63b3ed'
C_ACCENT2 = '#9f7aea'


def apply_page_config():
    st.set_page_config(
        page_title="SipCheck",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_global_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* REMOVE ALL BORDERS COMPLETELY */
*, *::before, *::after {
    box-sizing: border-box;
}

/* Main app */
.stApp {
    background: #07090f !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Remove any red/black borders */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
.main,
.block-container {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

/* Block container */
.block-container {
    padding: 0.5rem 2rem 2rem 2rem !important;
    max-width: 100% !important;
}

/* Hide header */
[data-testid="stHeader"] {
    background: transparent !important;
    border: none !important;
}

/* PREMIUM SIDEBAR */
section[data-testid="stSidebar"] {
    background: #0D0B1A !important;
    border: none !important;
    border-right: 1px solid rgba(168,85,247,0.12) !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] > div {
    background: #0D0B1A !important;
    border: none !important;
}

/* Sidebar nav links */
section[data-testid="stSidebar"] a {
    color: #6B7280 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 9px 20px !important;
    border-radius: 0 !important;
    border-left: 2px solid transparent !important;
    text-decoration: none !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

section[data-testid="stSidebar"] a:hover {
    color: #D8B4FE !important;
    background: rgba(168,85,247,0.07) !important;
    border-left: 2px solid rgba(168,85,247,0.5) !important;
}

section[data-testid="stSidebar"] [aria-selected="true"] {
    color: #D8B4FE !important;
    background: rgba(168,85,247,0.12) !important;
    border-left: 2px solid #A855F7 !important;
    font-weight: 600 !important;
}

/* Buttons */
.stButton > button {
    border: 1px solid rgba(168,85,247,0.4) !important;
    background: rgba(30,25,45,0.8) !important;
    color: #D8B4FE !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    border-color: #A855F7 !important;
    background: rgba(168,85,247,0.15) !important;
    color: #fff !important;
    box-shadow: 0 0 12px rgba(168,85,247,0.3) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #1A1A2E !important;
    border: 1px solid rgba(168,85,247,0.2) !important;
    color: #fff !important;
    border-radius: 8px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(30,25,45,0.4) !important;
    border-radius: 8px !important;
    padding: 4px !important;
    border: none !important;
    gap: 8px !important;
}

.stTabs [data-baseweb="tab"] {
    color: #94A3B8 !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    border: none !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(168,85,247,0.2) !important;
    color: #D8B4FE !important;
    border-bottom: 2px solid #A855F7 !important;
}

/* ── Layout classes ── */
.page-title {
    font-size: 22px;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.03em;
    margin-bottom: 10px;
}
.notice {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    background: rgba(99,179,237,0.05);
    border: 1px solid rgba(99,179,237,0.12);
    border-radius: 8px;
    font-size: 12px;
    color: #718096;
    margin-bottom: 8px;
}
.card {
    background: #0C0F1A;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
}
.card-title {
    font-size: 11px;
    font-weight: 700;
    color: #4A5568;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 14px;
}
.pill-gain {
    display: inline-block;
    padding: 3px 10px;
    background: rgba(72,187,120,0.12);
    border: 1px solid rgba(72,187,120,0.25);
    border-radius: 20px;
    color: #48bb78;
    font-size: 12px;
    font-weight: 600;
}
.pill-loss {
    display: inline-block;
    padding: 3px 10px;
    background: rgba(252,129,129,0.12);
    border: 1px solid rgba(252,129,129,0.25);
    border-radius: 20px;
    color: #fc8181;
    font-size: 12px;
    font-weight: 600;
}
.section-sep {
    font-size: 10px;
    font-weight: 700;
    color: #4A5568;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 14px 0 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.alloc-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.alloc-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 10px;
    flex-shrink: 0;
}

/* ── Streamlit metric override ── */
[data-testid="stMetric"] {
    background: #0C0F1A !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 10px !important;
    font-weight: 700 !important;
    color: #4A5568 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}
[data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #F8FAFC !important;
}
[data-testid="stMetricDelta"] svg { display: none !important; }
[data-testid="stMetricDelta"] > div {
    font-size: 12px !important;
    color: #48bb78 !important;
}

/* ── Plotly chart containers ── */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
[data-testid="stPlotlyChart"] > div { border-radius: 10px; }

/* ── DataFrame / table ── */
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden; }

/* Hide streamlit branding */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

/* Hide Streamlit auto-generated multi-page nav */
[data-testid="stSidebarNav"] { display: none !important; }

/* Page link nav styling */
section[data-testid="stSidebar"] [data-testid="stPageLink"] {
    padding: 0 !important;
    margin: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    color: #6B7280 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
    text-decoration: none !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    border-left: 2px solid transparent !important;
    border-radius: 0 !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    color: #D8B4FE !important;
    background: rgba(168,85,247,0.07) !important;
    border-left-color: rgba(168,85,247,0.5) !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink-active"] a {
    color: #D8B4FE !important;
    background: rgba(168,85,247,0.12) !important;
    border-left-color: #A855F7 !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def to_date(d):
    if not d:
        return date.today()
    if isinstance(d, str):
        try:
            return datetime.datetime.strptime(d.split("T")[0], "%Y-%m-%d").date()
        except Exception:
            return date.today()
    if hasattr(d, "date"):
        return d.date()
    return d


def to_dict(obj):
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(i) for i in obj]
    if hasattr(obj, "model_dump"):
        return to_dict(obj.model_dump())
    if hasattr(obj, "dict"):
        return to_dict(obj.dict())
    return obj


def clean_name(name):
    if not name:
        return "Unknown Scheme"
    for sfx in [
        "- Direct Plan - Growth Option", "- Direct Plan - Growth",
        "- Direct Growth Plan", "- Direct Plan Growth",
        "Direct Plan Growth", "Direct Growth", "Direct Plan",
        "Regular Plan", "Growth",
    ]:
        name = name.replace(sfx, "")
    name = name.strip().rstrip("-").strip()
    return name


def ordinal(n):
    suffix = "th" if 11 <= n <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def next_due_date(dom: int) -> date:
    today = date.today()
    try:
        candidate = today.replace(day=dom)
    except ValueError:
        candidate = today.replace(day=28)
    if candidate <= today:
        m, y = today.month + 1, today.year
        if m > 12:
            m, y = 1, y + 1
        try:
            candidate = candidate.replace(year=y, month=m)
        except ValueError:
            candidate = candidate.replace(year=y, month=m, day=28)
    return candidate


def calc_xirr(transactions, current_value, valuation_date_str):
    dates, amounts = [], []
    for tx in transactions:
        try:
            dt = to_date(tx.get("date"))
            amt = float(tx.get("amount", 0.0))
            if amt > 0:
                dates.append(dt)
                amounts.append(-amt)
        except Exception:
            continue
    if current_value > 0:
        try:
            dates.append(to_date(valuation_date_str))
            amounts.append(current_value)
        except Exception:
            pass
    if len(amounts) >= 2 and sum(amounts) != 0:
        try:
            rate = xirr(dates, amounts)
            return rate * 100 if rate is not None else 0.0
        except Exception:
            return 0.0
    return 0.0


def fmt_inr(v):
    """Full precision INR — used in tables, exports, HTML reports."""
    return f"₹{abs(v):,.2f}"


def fmt_inr_short(v):
    """
    Compact INR formatter for dashboard KPI tiles so values never truncate.
    ≥ 1 Cr  → ₹X.XX Cr
    ≥ 1 L   → ₹X.XX L
    < 1 L   → ₹X,XXX
    Negative values prefix with −.
    """
    sign = "−" if v < 0 else ""
    av = abs(v)
    if av >= 1_00_00_000:          # 1 crore and above
        return f"{sign}₹{av / 1_00_00_000:.2f} Cr"
    if av >= 1_00_000:             # 1 lakh and above
        return f"{sign}₹{av / 1_00_000:.2f} L"
    return f"{sign}₹{av:,.0f}"    # below 1 lakh — plain number


def gain_arrow(v):
    return "▲" if v >= 0 else "▼"


def gain_color(v):
    return C_GAIN if v >= 0 else C_LOSS


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


# ─────────────────────────────────────────────
# PDF PARSING
# ─────────────────────────────────────────────

def parse_pdf(pdf_bytes, password):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf_bytes)
        path = f.name
    try:
        raw = casparser.read_cas_pdf(path, password=password)
        return to_dict(raw), None
    except Exception as exc:
        err = str(exc).lower()
        if any(k in err for k in ["password", "decrypt", "incorrect"]):
            return None, "wrong_password"
        return None, str(exc)
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


# ─────────────────────────────────────────────
# LIVE NAV FETCH
# ─────────────────────────────────────────────

def fetch_live_navs(holdings):
    live_dict = {}
    latest_date = None
    for holding in holdings:
        amfi = holding.get("amfi")
        if not amfi:
            continue
        try:
            response = requests.get(f"https://api.mfapi.in/mf/{amfi}", timeout=5)
            if response.status_code != 200:
                continue
            data = response.json().get("data", [])
            if not data:
                continue
            nav = float(data[0]["nav"])
            date_str = data[0]["date"]
            live_dict[holding["scheme"]] = {
                "nav": nav,
                "date": date_str,
                "live_value": nav * holding["units"],
            }
            latest_date = date_str
        except Exception:
            continue
    return live_dict, latest_date


# ─────────────────────────────────────────────
# EXPORT: EXCEL
# ─────────────────────────────────────────────

def generate_excel(d, live_data=None):
    out = io.BytesIO()
    live_data = live_data or {}
    display_wealth = d["total_value"]
    has_live = False

    if live_data:
        new_wealth = 0
        for h in d["holdings"]:
            sname = h["scheme"]
            if sname in live_data:
                new_wealth += live_data[sname]["live_value"]
                has_live = True
            else:
                new_wealth += h["value"]
        display_wealth = new_wealth if has_live else d["total_value"]

    display_pnl = display_wealth - d["total_invested"]

    try:
        with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
            pd.DataFrame([
                {"Field": "Name", "Value": d["investor_name"]},
                {"Field": "Email", "Value": d["investor_email"]},
                {"Field": "PAN", "Value": d.get("investor_pan", "—")},
                {"Field": "Statement Date", "Value": d["statement_date"]},
                {"Field": "Total Value", "Value": display_wealth},
                {"Field": "Total Invested", "Value": d["total_invested"]},
                {"Field": "Unrealized P&L", "Value": display_pnl},
                {"Field": "Realized P&L", "Value": d.get("realized_pnl", 0.0)},
            ]).to_excel(writer, sheet_name="Summary", index=False)

            if d["holdings"]:
                rows = []
                for s in d["holdings"]:
                    sname = s["scheme"]
                    cas_val = s["value"]
                    l_val = cas_val
                    nav = s.get("cas_nav", 0.0)
                    dt = s.get("cas_date", "—")
                    if live_data and sname in live_data:
                        l_val = live_data[sname]["live_value"]
                        nav = live_data[sname]["nav"]
                        dt = live_data[sname]["date"]
                        sname = sname + " (LIVE)"
                    rows.append({
                        "Scheme": clean_name(sname),
                        "Category": s["category"],
                        "Invested": s["invested"],
                        "CAS Value": cas_val,
                        "Live Value": l_val if live_data else "—",
                        "NAV": nav,
                        "NAV Date": dt,
                        "Current P&L": l_val - s["invested"],
                        "XIRR %": s["xirr"],
                    })
                pd.DataFrame(rows).to_excel(writer, sheet_name="Holdings", index=False)

            if d.get("redeemed"):
                pd.DataFrame(d["redeemed"]).to_excel(writer, sheet_name="Redeemed", index=False)

            all_sips = d.get("live_sips", []) + d.get("dead_sips", [])
            if all_sips:
                pd.DataFrame([
                    {
                        "Scheme": clean_name(s["scheme"]),
                        "Amount": s["amount"],
                        "Day": s["day_label"],
                        "Last Date": s["last_date"],
                        "Status": s["status"],
                    }
                    for s in all_sips
                ]).to_excel(writer, sheet_name="SIPs", index=False)

        return out.getvalue()
    except Exception:
        return None


# ─────────────────────────────────────────────
# EXPORT: HTML REPORT
# ─────────────────────────────────────────────

def generate_html(d, live_data=None):
    live_data = live_data or {}
    display_wealth = d["total_value"]

    if live_data:
        new_wealth = 0
        for h in d["holdings"]:
            sname = h["scheme"]
            if sname in live_data:
                new_wealth += live_data[sname]["live_value"]
            else:
                new_wealth += h["value"]
        display_wealth = new_wealth

    display_pnl = display_wealth - d["total_invested"]
    realized = d.get("realized_pnl", 0.0)

    rows_holdings = ""
    for s in d.get("holdings", []):
        sname = s["scheme"]
        cas_val = s["value"]
        l_val = cas_val
        nav = s.get("cas_nav", 0.0)
        dt = s.get("cas_date", "—")
        badge = ""
        if live_data and sname in live_data:
            l_val = live_data[sname]["live_value"]
            nav = live_data[sname]["nav"]
            dt = live_data[sname]["date"]
            badge = " 🟢"
        curr_pnl = l_val - s["invested"]
        rows_holdings += f"""<tr>
          <td>{clean_name(sname)}{badge}</td>
          <td>{fmt_inr(s['invested'])}</td>
          <td>{fmt_inr(cas_val)}</td>
          <td style=\"font-weight:700;\">{fmt_inr(l_val) if badge else '—'}</td>
          <td>₹{nav:,.4f}</td>
          <td>{dt}</td>
          <td style=\"color:{'#48bb78' if curr_pnl>=0 else '#fc8181'};font-weight:600;\">{fmt_inr(curr_pnl)}</td>
          <td style=\"color:{'#48bb78' if s['xirr']>=0 else '#fc8181'};font-family:monospace;\">{s['xirr']:.2f}%</td>
        </tr>"""

    rows_redeemed = ""
    for r in d.get("redeemed", []):
        p = r["profit"]
        rows_redeemed += f"""<tr>
          <td>{clean_name(r['scheme'])}</td><td>{fmt_inr(r['invested'])}</td>
          <td>{fmt_inr(r['redeemed'])}</td>
          <td style=\"color:{'#48bb78' if p>=0 else '#fc8181'};font-weight:600;\">{fmt_inr(p)}</td>
        </tr>"""
    if not rows_redeemed:
        rows_redeemed = "<tr><td colspan='4' style='text-align:center;color:#718096;padding:20px;'>No fully redeemed schemes.</td></tr>"

    rows_sip = ""
    for s in d.get("live_sips", []) + d.get("dead_sips", []):
        color = "#48bb78" if s["status"] == "Live" else "#fc8181"
        rows_sip += f"""<tr>
          <td>{clean_name(s['scheme'])}</td>
          <td style=\"font-family:'IBM Plex Mono',monospace;\">{fmt_inr(s['amount'])}</td>
          <td>{s['day_label']}</td><td>{s['last_date']}</td>
          <td style=\"color:{color};font-weight:700;\">{s['status'].upper()}</td>
        </tr>"""

    live_header = " — 🟢 LIVE DATA ACTIVE" if live_data else ""

    return f"""<!DOCTYPE html>
<html><head><meta charset=\"utf-8\">
<title>SipCheck — {d['investor_name']}</title>
<style>
  @media print {{body{{background:#07090f!important;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}}}
  body{{background:#07090f;color:#e2e8f0;font-family:'Helvetica Neue',Helvetica,sans-serif;padding:32px;line-height:1.5;}}
  h1{{font-size:24px;font-weight:800;color:#fff;margin:0 0 4px;letter-spacing:-0.5px;}}
  .sub{{font-size:12px;color:#63b3ed;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:20px;}}
  .card{{background:#0c0f1a;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:22px;margin-bottom:20px;}}
  .grid-4{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:16px 0;}}
  .kpi{{background:#111627;border:1px solid rgba(255,255,255,0.05);border-radius:8px;padding:14px;}}
  .kpi-label{{font-size:9px;color:#718096;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px;}}
  .kpi-value{{font-size:18px;font-weight:700;font-family:monospace;color:#fff;}}
  table{{width:100%;border-collapse:collapse;border-radius:10px;overflow:hidden;border:1px solid rgba(255,255,255,0.07);margin:10px 0;}}
  th{{background:#111627;color:#9f7aea;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;padding:12px 14px;text-align:left;}}
  td{{background:#0c0f1a;color:#e2e8f0;font-size:12px;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,0.04);}}
  tr:nth-child(even) td{{background:#111627;}}
  .sec{{font-size:10px;font-weight:700;color:#2d3748;text-transform:uppercase;letter-spacing:2px;margin:30px 0 12px;border-left:3px solid #63b3ed;padding-left:10px;}}
  .footer{{text-align:center;font-size:10px;color:#2d3748;border-top:1px solid rgba(255,255,255,0.05);padding-top:14px;margin-top:40px;}}
</style></head><body>
<div class=\"card\">
  <h1>SipCheck VIEW</h1>
  <div class=\"sub\">Portfolio Intelligence Dashboard{live_header}</div>
  <table style=\"border:none;background:transparent;\"><tbody>
    <tr><td style=\"background:transparent;color:#718096;font-size:11px;width:120px;\">Name</td><td style=\"background:transparent;color:#f7fafc;font-weight:600;\">{d['investor_name'].title()}</td>
        <td style=\"background:transparent;color:#718096;font-size:11px;width:120px;\">Email</td><td style=\"background:transparent;color:#f7fafc;\">{d['investor_email'] or '—'}</td></tr>
    <tr><td style=\"background:transparent;color:#718096;font-size:11px;\">PAN</td><td style=\"background:transparent;color:#9f7aea;font-family:monospace;font-weight:700;\">{d.get('investor_pan','—')}</td>
        <td style=\"background:transparent;color:#718096;font-size:11px;\">Statement Date</td><td style=\"background:transparent;color:#f7fafc;\">{d['statement_date']}</td></tr>
  </tbody></table>
  <div class=\"grid-4\">
    <div class=\"kpi\"><div class=\"kpi-label\">Total Wealth</div><div class=\"kpi-value\">{fmt_inr(display_wealth)}</div></div>
    <div class=\"kpi\"><div class=\"kpi-label\">Invested</div><div class=\"kpi-value\" style=\"color:#63b3ed;\">{fmt_inr(d['total_invested'])}</div></div>
    <div class=\"kpi\"><div class=\"kpi-label\">Unrealized P&L</div><div class=\"kpi-value\" style=\"color:{'#48bb78' if display_pnl>=0 else '#fc8181'};\">{fmt_inr(display_pnl)}</div></div>
    <div class=\"kpi\"><div class=\"kpi-label\">Realized P&L</div><div class=\"kpi-value\" style=\"color:{'#48bb78' if realized>=0 else '#fc8181'};\">{fmt_inr(realized)}</div></div>
  </div>
</div>
<div class=\"sec\">Active Holdings</div>
<table><thead><tr><th>Scheme</th><th>Invested</th><th>CAS Value</th><th>Live Value</th><th>NAV</th><th>NAV Date</th><th>P&L</th><th>XIRR %</th></tr></thead>
<tbody>{rows_holdings}</tbody></table>
<div class=\"sec\">SIP Registry</div>
<table><thead><tr><th>Scheme</th><th>Amount</th><th>Day</th><th>Last Date</th><th>Status</th></tr></thead>
<tbody>{rows_sip}</tbody></table>
<div class=\"sec\">Fully Redeemed Positions</div>
<table><thead><tr><th>Scheme</th><th>Invested</th><th>Redeemed</th><th>Realized P&L</th></tr></thead>
<tbody>{rows_redeemed}</tbody></table>
<div class=\"footer\">Generated by SipCheck · Confidential</div>
</body></html>"""


# ─────────────────────────────────────────────
# SIP / TRANSACTION CONSTANTS
# ─────────────────────────────────────────────

SIP_TX_KEYS = ["SIP", "SYSTEMATIC", "RECURRING", "AUTO DEBIT", "E-DEBIT", "ECS", "MANDATE"]

TX_META = {
    "SIP":                  {"icon": "🔁", "color": "#63b3ed",  "group": "inflow"},
    "Lumpsum Purchase":     {"icon": "💰", "color": "#9f7aea",  "group": "inflow"},
    "STP In":               {"icon": "⚡️", "color": "#68d391",  "group": "inflow"},
    "Switch In":            {"icon": "🔀", "color": "#4fd1c5",  "group": "inflow"},
    "STP Out":              {"icon": "⬇️", "color": "#f6ad55",  "group": "outflow"},
    "Switch Out":           {"icon": "🔀", "color": "#ed8936",  "group": "outflow"},
    "SWP":                  {"icon": "💸", "color": "#fc8181",  "group": "outflow"},
    "Redemption":           {"icon": "🏦", "color": "#fc8181",  "group": "outflow"},
    "SIP Reversal":         {"icon": "↩️", "color": "#fbb6ce",  "group": "reversal"},
    "STP In Reversal":      {"icon": "↩️", "color": "#fbb6ce",  "group": "reversal"},
    "STP Out Reversal":     {"icon": "↩️", "color": "#fbb6ce",  "group": "reversal"},
    "Switch In Reversal":   {"icon": "↩️", "color": "#fbb6ce",  "group": "reversal"},
    "Switch Out Reversal":  {"icon": "↩️", "color": "#fbb6ce",  "group": "reversal"},
    "SWP Reversal":         {"icon": "↩️", "color": "#fbb6ce",  "group": "reversal"},
    "Redemption Reversal":  {"icon": "↩️", "color": "#fbb6ce",  "group": "reversal"},
    "Reversal / Rejection": {"icon": "✖",  "color": "#fc8181",  "group": "reversal"},
    "Other":                {"icon": "○",  "color": "#718096",  "group": "other"},
}

SPECIAL_TX_TYPES = [t for t in TX_META if t not in ("SIP", "Lumpsum Purchase", "Other")]


# ─────────────────────────────────────────────
# TRANSACTION CLASSIFICATION
# ─────────────────────────────────────────────

def classify_transaction(tx):
    raw_units   = float(tx.get("units")  or 0.0)
    txn_type    = str(tx.get("type",        "")).upper()
    description = str(tx.get("description", "")).upper()
    combined    = txn_type + " " + description

    is_reversal_kw = any(k in combined for k in [
        "REVERSAL", "REVERSED", "REJECTION", "REJECTED",
        "BOUNCE", "BOUNCED", "INSUFFICIENT", "FAILED",
        "RETURN", "CANCELLED", "CANCEL",
    ])

    is_stp_out    = "STP" in combined and ("OUT" in combined or "TRANSFER OUT" in combined)
    is_stp_in     = "STP" in combined and ("IN" in combined or "TRANSFER IN" in combined) and not is_stp_out
    is_switch_out = "SWITCH" in combined and "OUT" in combined
    is_switch_in  = "SWITCH" in combined and "IN" in combined and not is_switch_out
    is_swp        = "SWP" in combined or "SYSTEMATIC WITHDRAWAL" in combined
    is_sip_kw     = any(k in combined for k in SIP_TX_KEYS)
    is_redemption = any(k in combined for k in ["REDEMPTION", "PAYOUT", "WITHDRAWAL"]) and not is_swp
    is_purchase   = any(k in combined for k in ["PURCHASE", "LUMPSUM", "NFO", "NEW FUND", "REINVEST", "DIVIDEND REINVEST"])

    if is_stp_out:      base = "STP Out"
    elif is_stp_in:     base = "STP In"
    elif is_switch_out: base = "Switch Out"
    elif is_switch_in:  base = "Switch In"
    elif is_swp:        base = "SWP"
    elif is_redemption: base = "Redemption"
    elif is_sip_kw:     base = "SIP"
    elif is_purchase:   base = "Lumpsum Purchase"
    else:               base = "Other"

    OUTFLOW_BASES = {"Redemption", "STP Out", "Switch Out", "SWP"}
    INFLOW_BASES  = {"SIP", "Lumpsum Purchase", "STP In", "Switch In"}

    if base in OUTFLOW_BASES:
        is_reversal = (raw_units > 0) or is_reversal_kw
    elif base in INFLOW_BASES:
        is_reversal = (raw_units < 0) or is_reversal_kw
    else:
        is_reversal = is_reversal_kw

    if is_reversal and base != "Other":
        return base + " Reversal"
    elif is_reversal:
        return "Reversal / Rejection"
    return base


# ─────────────────────────────────────────────
# TRANSACTION ACCOUNTING
# ─────────────────────────────────────────────

def account_transactions(transactions):
    invested = sip_invested = lumpsum_invested = redeemed_amount = 0.0
    special_txs = []

    BUY_CLASSES      = {"SIP", "Lumpsum Purchase", "STP In",  "Switch In"}
    SELL_CLASSES     = {"Redemption", "SWP", "STP Out", "Switch Out"}
    REV_BUY_CLASSES  = {"SIP Reversal", "STP In Reversal", "Switch In Reversal"}
    REV_SELL_CLASSES = {"Redemption Reversal", "SWP Reversal", "STP Out Reversal", "Switch Out Reversal"}

    for tx in transactions:
        amount    = abs(float(tx.get("amount") or 0.0))
        raw_units = float(tx.get("units")  or 0.0)
        tx_date   = to_date(tx.get("date"))
        tx_class  = classify_transaction(tx)

        if tx_class in BUY_CLASSES:
            invested += amount
            if tx_class == "SIP":
                sip_invested += amount
            else:
                lumpsum_invested += amount
        elif tx_class in REV_BUY_CLASSES:
            invested = max(0.0, invested - amount)
            if tx_class == "SIP Reversal":
                sip_invested = max(0.0, sip_invested - amount)
            else:
                lumpsum_invested = max(0.0, lumpsum_invested - amount)
        elif tx_class in SELL_CLASSES:
            redeemed_amount += amount
        elif tx_class in REV_SELL_CLASSES:
            redeemed_amount = max(0.0, redeemed_amount - amount)

        special_txs.append({
            "date_obj":    tx_date,
            "Date":        tx_date.strftime("%d %b %Y"),
            "Type":        tx_class,
            "Amount":      amount,
            "Raw Amount":  float(tx.get("amount") or 0.0),
            "Units":       raw_units,
            "Description": tx.get("description", ""),
        })

    return {
        "invested":         invested,
        "sip_invested":     sip_invested,
        "lumpsum_invested": lumpsum_invested,
        "redeemed_amount":  redeemed_amount,
        "special_txs":      special_txs,
    }


# ─────────────────────────────────────────────
# SIP MANDATE DETECTION
# ─────────────────────────────────────────────

def detect_sip_mandates(sip_transactions, scheme_name, units, valuation_date_str):
    import re as _re

    def get_mandate_key(tx):
        desc      = str(tx.get("description", "")).upper()
        amount    = str(abs(float(tx.get("amount") or 0)))
        is_multi  = "MULTI" in desc
        multi_flag= "MULTI" if is_multi else "SINGLE"
        m = _re.search(r"(\d+)/(\d+)", desc)
        if m:
            total = int(m.group(2))
            return f"LONG_{amount}_{multi_flag}" if total > 100 else f"{total}_{multi_flag}"
        return f"AMT_{amount}_{multi_flag}"

    mandate_groups = {}
    for tx in sip_transactions:
        mandate_groups.setdefault(get_mandate_key(tx), []).append(tx)

    # Merge orphan first-instalments into the instalment-numbered series.
    # Two-pass strategy:
    #   Pass 1 (same-amount): same as before — merge small same-amount groups.
    #   Pass 2 (cross-amount): merge AMT_* orphans (≤2 txs) into the largest
    #     instalment-key group with the same MULTI flag, regardless of amount.
    #     This handles the common case where instalment 1 has a different amount
    #     (e.g. ₹1,999.90 first deduction vs ₹999.95 for instalments 2–62).
    if len(mandate_groups) > 1:
        # Pass 1: same-amount merge
        amount_to_groups = {}
        for mk, mtxs in mandate_groups.items():
            amt = str(abs(float(mtxs[0].get("amount") or 0)))
            amount_to_groups.setdefault(amt, []).append((mk, mtxs))
        merged = {}
        for amt, groups in amount_to_groups.items():
            if len(groups) == 1:
                mk, mtxs = groups[0]
                merged[mk] = mtxs
            else:
                sorted_by_size = sorted(groups, key=lambda x: len(x[1]), reverse=True)
                main_key, main_txs = sorted_by_size[0]
                main_multi = "MULTI" in main_key
                for mk, mtxs in sorted_by_size[1:]:
                    if len(mtxs) <= 2 and ("MULTI" in mk) == main_multi:
                        main_txs = main_txs + mtxs
                    else:
                        merged[mk] = mtxs
                merged[main_key] = main_txs
        mandate_groups = merged

        # Pass 2: merge AMT_* orphans (no instalment number) into the largest
        # instalment-numbered group with matching MULTI flag
        if len(mandate_groups) > 1:
            inst_keys   = [k for k in mandate_groups if not k.startswith("AMT_")]
            orphan_keys = [k for k in mandate_groups if k.startswith("AMT_")
                           and len(mandate_groups[k]) <= 2]
            for ork in orphan_keys:
                orphan_multi = "MULTI" in ork
                candidates   = [(k, mandate_groups[k]) for k in inst_keys
                                if ("MULTI" in k) == orphan_multi]
                if candidates:
                    best_key = max(candidates, key=lambda x: len(x[1]))[0]
                    mandate_groups[best_key] = mandate_groups[best_key] + mandate_groups.pop(ork)

    statement_date_obj = to_date(valuation_date_str)
    cutoff_live        = statement_date_obj - datetime.timedelta(days=75)
    sip_records        = []

    for _mandate_key, mandate_txs in mandate_groups.items():
        sorted_mandate = sorted(mandate_txs, key=lambda x: to_date(x.get("date")))
        latest_tx      = sorted_mandate[-1]
        amount_sip     = float(latest_tx.get("amount", 0.0))
        if amount_sip <= 0:
            continue

        days      = [to_date(t.get("date")).day for t in mandate_txs]
        dom       = Counter(days).most_common(1)[0][0] if days else 1
        last_date = to_date(latest_tx.get("date"))
        next_due  = next_due_date(dom)

        is_recent = last_date >= cutoff_live
        status    = "Live" if (units > 0.01 and is_recent) else "Inactive"

        sip_label = scheme_name
        if len(mandate_groups) > 1:
            desc = str(latest_tx.get("description", ""))
            sip_label = scheme_name + (" (Multi SIP)" if "MULTI" in desc.upper() else " (Physical)")

        days_since_last   = (statement_date_obj - last_date).days
        missed_last_month = (status == "Live" and days_since_last > 39)

        sip_records.append({
            "scheme":            sip_label,
            "amount":            amount_sip,
            "day_label":         ordinal(dom),
            "dom":               dom,
            "last_date":         last_date.strftime("%d %b %Y"),
            "last_date_obj":     last_date,
            "next_date":         next_due.strftime("%d %b %Y"),
            "next_iso":          next_due.isoformat(),
            "installments":      len(mandate_txs),
            "days_since_last":   days_since_last,
            "missed_last_month": missed_last_month,
            "status":            status,
        })

    return sip_records


# ─────────────────────────────────────────────
# DATA PROCESSING
# ─────────────────────────────────────────────

def process(raw):
    raw = to_dict(raw)
    info = raw.get("investor_info", {})

    result = {
        "investor_name":          info.get("name", "Investor"),
        "investor_email":         info.get("email", ""),
        "investor_pan":           info.get("pan", "—"),
        "statement_date":         str(date.today()),
        "total_value":            0.0,
        "total_invested":         0.0,
        "total_sip_invested":     0.0,
        "total_lumpsum_invested": 0.0,
        "unrealized_pnl":         0.0,
        "realized_pnl":           0.0,
        "alloc_values":           {},
        "alloc_pct":              {},
        "holdings":               [],
        "live_sips":              [],
        "dead_sips":              [],
        "redeemed":               [],
        "recent_redemptions":     [],
        "special_transactions":   [],
        "tx_map":                 {},
        "agg_map":                {},
        "duplicate_alerts":       [],
    }

    total_val = 0.0
    total_inv = 0.0
    type_map  = {}

    for folio in raw.get("folios", []):
        for scheme in folio.get("schemes", []):
            valuation   = scheme.get("valuation", {})
            scheme_name = scheme.get("scheme", "Unknown")
            valuation_date = str(valuation.get("date", result["statement_date"]))
            result["statement_date"] = valuation_date

            cost   = float(valuation.get("cost",  0.0))
            value  = float(valuation.get("value", 0.0))
            units  = float(scheme.get("close",    0.0))

            sname_lower = scheme_name.lower()
            scheme_type = str(scheme.get("type", "EQUITY")).upper()
            if any(k in sname_lower for k in ("gold", "silver", "metal", "commodity")):
                category = "Gold & Commodities"
            elif any(k in sname_lower for k in ("international", "global", "overseas", "us ", "nasdaq", "s&p", "hang seng", "japan", "europe")):
                category = "International"
            elif scheme_type in ("EQUITY", "ELSS"):
                category = "Equity Funds"
            else:
                category = "Debt Funds"

            transactions = scheme.get("transactions", [])
            result["tx_map"][scheme_name] = transactions

            # ── Accounting ──────────────────────────────────────────
            acct             = account_transactions(transactions)
            invested         = acct["invested"]
            sip_invested     = acct["sip_invested"]
            lumpsum_invested = acct["lumpsum_invested"]
            redeemed_amount  = acct["redeemed_amount"]

            # Enrich special txs with scheme + category
            for stx in acct["special_txs"]:
                stx["Scheme"]   = clean_name(scheme_name)
                stx["Category"] = category
                result["special_transactions"].append(stx)

            # Populate recent_redemptions from classified txs
            for stx in acct["special_txs"]:
                if stx["Type"] in ("Redemption", "SWP"):
                    result["recent_redemptions"].append({
                        "date_obj": stx["date_obj"],
                        "Date":     stx["Date"],
                        "Scheme":   clean_name(scheme_name),
                        "Payout":   stx["Amount"],
                    })

            # ── Fully redeemed position ──────────────────────────────
            if units < 0.001 and invested > 0 and redeemed_amount > 0:
                profit = redeemed_amount - invested
                result["redeemed"].append({
                    "scheme":   scheme_name,
                    "invested": invested,
                    "redeemed": redeemed_amount,
                    "profit":   profit,
                })
                result["realized_pnl"] += profit
                result["agg_map"][scheme_name] = {"cost": cost, "units": units, "value": value}
                continue

            total_val += value
            total_inv += cost
            type_map[category] = type_map.get(category, 0.0) + value
            result["agg_map"][scheme_name] = {"cost": cost, "units": units, "value": value}

            pnl        = value - cost
            xirr_value = calc_xirr(transactions, value, valuation_date)
            cas_nav    = float(valuation.get("nav", 0.0))
            if cas_nav == 0.0 and units > 0:
                cas_nav = value / units

            result["holdings"].append({
                "scheme":            scheme_name,
                "amfi":              scheme.get("amfi"),
                "units":             units,
                "invested":          invested,
                "sip_invested":      sip_invested,
                "lumpsum_invested":  lumpsum_invested,
                "value":             value,
                "pnl":               pnl,
                "xirr":              xirr_value,
                "category":          category,
                "cas_nav":           cas_nav,
                "cas_date":          valuation_date,
            })

            # ── SIP mandate detection ────────────────────────────────
            sip_txs = [
                t for t in transactions
                if any(k in str(t.get("description","")).upper()
                       or k in str(t.get("type","")).upper()
                       for k in SIP_TX_KEYS)
                and float(t.get("units")  or 0.0) > 0
                and float(t.get("amount") or 0.0) > 0
            ]
            if sip_txs:
                for rec in detect_sip_mandates(sip_txs, scheme_name, units, valuation_date):
                    if rec["status"] == "Live":
                        result["live_sips"].append(rec)
                    else:
                        result["dead_sips"].append(rec)

    result["total_value"]            = total_val
    result["total_invested"]         = total_inv
    result["total_sip_invested"]     = sum(h["sip_invested"]     for h in result["holdings"])
    result["total_lumpsum_invested"] = sum(h["lumpsum_invested"]  for h in result["holdings"])
    result["unrealized_pnl"]         = total_val - total_inv
    result["alloc_values"]           = type_map
    result["alloc_pct"]              = {k: (v / total_val) * 100 for k, v in type_map.items()} if total_val else {}

    result["recent_redemptions"] = sorted(
        result["recent_redemptions"], key=lambda x: x["date_obj"], reverse=True
    )
    result["special_transactions"] = sorted(
        result["special_transactions"], key=lambda x: x["date_obj"], reverse=True
    )

    return result


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

def initialize_session_state():
    defaults = {
        "profiles": {},
        "active": None,
        "show_email": True,
        "pin_ok": False,
        "switch_target": None,
        "live_data": {},
        "live_last_updated": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def active_data():
    active = st.session_state.active
    return st.session_state.profiles.get(active) if active else None


# ─────────────────────────────────────────────
# UPLOAD SCREEN
# ─────────────────────────────────────────────

def show_upload():
    render_home_v2()

    st.markdown("<hr style='border:none;border-top:1px solid rgba(139,92,246,0.2);margin:1.5rem 0 1.2rem;'>",
                unsafe_allow_html=True)
    col = st.columns([1, 2, 1])[1]
    with col:
        uploaded = st.file_uploader("CAS PDF", type=["pdf"], label_visibility="collapsed")
        password = st.text_input("PDF Password", type="password", placeholder="PAN / Date of Birth")

        if uploaded and password:
            if st.button("Analyse Portfolio →", use_container_width=True, type="primary"):
                with st.spinner("Parsing…"):
                    data, error = parse_pdf(uploaded.read(), password)
                if error == "wrong_password":
                    st.error("Wrong password. Try your PAN number or date of birth (DDMMYYYY).")
                elif error:
                    st.error(f"Parse error: {error}")
                else:
                    portfolio = process(data)
                    investor_name = portfolio["investor_name"].title()
                    st.session_state.profiles[investor_name] = portfolio
                    st.session_state.active = investor_name
                    st.session_state.pin_ok = True
                    st.success(f"Portfolio loaded — {investor_name}")
                    st.rerun()

    # ── About / Features section ──────────────────────────────────────────────
    st.markdown("<div style='height:56px'></div>", unsafe_allow_html=True)

    # Note: HTML must start at column 0 of the string — 4-space indent = markdown code block
    about_html = (
"<div style='max-width:860px;margin:0 auto;padding:0 16px;'>"

"<div style='display:flex;align-items:center;gap:14px;margin-bottom:40px;'>"
"<div style='flex:1;height:1px;background:rgba(99,179,237,0.10);'></div>"
"<span style='font-size:10px;font-weight:700;color:rgba(99,179,237,0.45);"
"text-transform:uppercase;letter-spacing:2.5px;'>What is SipCheck</span>"
"<div style='flex:1;height:1px;background:rgba(99,179,237,0.10);'></div>"
"</div>"

"<div style='text-align:center;margin-bottom:44px;'>"
"<div style='font-family:Syne,sans-serif;font-size:22px;font-weight:800;"
"color:#f0f6ff;letter-spacing:-0.3px;margin-bottom:12px;'>"
"Your mutual fund portfolio, finally in one clear view.</div>"
"<div style='font-size:14px;color:#718096;line-height:1.85;max-width:620px;margin:0 auto;'>"
"SipCheck reads your Consolidated Account Statement (CAS) PDF issued by "
"<strong style='color:#e2e8f0;'>CAMS</strong> or <strong style='color:#e2e8f0;'>KFintech</strong>"
" and turns it into an interactive portfolio dashboard. No account creation, "
"no syncing, no data leaving your browser.</div>"
"</div>"

"<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:44px;'>"

"<div style='background:#0c0f1a;border:1px solid rgba(99,179,237,0.12);border-radius:14px;padding:22px 20px;'>"
"<div style='font-size:24px;margin-bottom:12px;'>📊</div>"
"<div style='font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:6px;'>Dashboard Overview</div>"
"<div style='font-size:12px;color:#718096;line-height:1.7;'>Total wealth, unrealized P&amp;L, SIP monthly outflow and asset allocation — all at a glance with live NAV refresh.</div>"
"</div>"

"<div style='background:#0c0f1a;border:1px solid rgba(99,179,237,0.12);border-radius:14px;padding:22px 20px;'>"
"<div style='font-size:24px;margin-bottom:12px;'>💼</div>"
"<div style='font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:6px;'>Portfolio Ledger</div>"
"<div style='font-size:12px;color:#718096;line-height:1.7;'>Every holding broken down by category — Equity, Debt, Gold &amp; Commodities, International — with XIRR, NAV, and live value.</div>"
"</div>"

"<div style='background:#0c0f1a;border:1px solid rgba(99,179,237,0.12);border-radius:14px;padding:22px 20px;'>"
"<div style='font-size:24px;margin-bottom:12px;'>🔄</div>"
"<div style='font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:6px;'>SIP Center</div>"
"<div style='font-size:12px;color:#718096;line-height:1.7;'>Active and stopped SIPs side by side. Monthly outflow chart, next due dates, and bounce detection built in.</div>"
"</div>"

"<div style='background:#0c0f1a;border:1px solid rgba(99,179,237,0.12);border-radius:14px;padding:22px 20px;'>"
"<div style='font-size:24px;margin-bottom:12px;'>📋</div>"
"<div style='font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:6px;'>Transaction Ledger</div>"
"<div style='font-size:12px;color:#718096;line-height:1.7;'>Full transaction history per scheme — purchase, redemption, switch, dividend — with XIRR table across all holdings.</div>"
"</div>"

"<div style='background:#0c0f1a;border:1px solid rgba(99,179,237,0.12);border-radius:14px;padding:22px 20px;'>"
"<div style='font-size:24px;margin-bottom:12px;'>🔔</div>"
"<div style='font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:6px;'>Alerts &amp; Insights</div>"
"<div style='font-size:12px;color:#718096;line-height:1.7;'>Auto-detects stopped SIPs, unrealized losses, and duplicate SIP entries so nothing slips through unnoticed.</div>"
"</div>"

"<div style='background:#0c0f1a;border:1px solid rgba(99,179,237,0.12);border-radius:14px;padding:22px 20px;'>"
"<div style='font-size:24px;margin-bottom:12px;'>🔒</div>"
"<div style='font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:6px;'>100% Private</div>"
"<div style='font-size:12px;color:#718096;line-height:1.7;'>Parsed entirely in-session. Nothing is stored on any server. Close the tab and your data is gone — zero data retention.</div>"
"</div>"

"</div>"

"<div style='background:#0c0f1a;border:1px solid rgba(99,179,237,0.10);border-radius:16px;"
"padding:28px 32px;margin-bottom:44px;'>"
"<div style='font-size:10px;font-weight:700;color:rgba(99,179,237,0.5);text-transform:uppercase;"
"letter-spacing:2.5px;margin-bottom:20px;'>How it works</div>"
"<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:12px;text-align:center;'>"
"<div><div style='font-size:20px;margin-bottom:8px;'>1️⃣</div>"
"<div style='font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;'>Get your CAS</div>"
"<div style='font-size:11px;color:#718096;'>Request from CAMS or KFintech portal — arrives by email as a PDF</div></div>"
"<div><div style='font-size:20px;margin-bottom:8px;'>2️⃣</div>"
"<div style='font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;'>Upload here</div>"
"<div style='font-size:11px;color:#718096;'>Drop the PDF above and enter the password (PAN or date of birth)</div></div>"
"<div><div style='font-size:20px;margin-bottom:8px;'>3️⃣</div>"
"<div style='font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;'>Instant analysis</div>"
"<div style='font-size:11px;color:#718096;'>Your full portfolio parses in seconds — no waiting, no signup</div></div>"
"<div><div style='font-size:20px;margin-bottom:8px;'>4️⃣</div>"
"<div style='font-size:12px;font-weight:600;color:#e2e8f0;margin-bottom:4px;'>Refresh live NAV</div>"
"<div style='font-size:11px;color:#718096;'>Hit Refresh Latest NAV to pull real-time values from AMFI</div></div>"
"</div></div>"

"<div style='text-align:center;padding-bottom:40px;'>"
"<div style='font-size:11px;color:rgba(99,179,237,0.35);letter-spacing:1px;'>"
"SipCheck · Built for Indian mutual fund investors · "
"<span style='color:rgba(255,255,255,0.15);'>Data never leaves your device</span>"
"</div></div>"

"</div>"
    )
    st.markdown(about_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

def build_sidebar(data):
    with st.sidebar:
        if data:
            email_display = data["investor_email"] if st.session_state.show_email else "••••••••••"
            st.markdown(
                f"""
                <div style="background:rgba(99,179,237,0.04);border:1px solid rgba(99,179,237,0.12);
                            border-radius:10px;padding:12px 14px;margin-bottom:10px;">
                  <div style="font-size:13px;font-weight:600;color:#f7fafc;margin-bottom:2px;">
                    {data['investor_name'].title()}</div>
                """,
                unsafe_allow_html=True,
            )

            ec1, ec2 = st.columns([5, 1])
            with ec1:
                st.markdown(f"<div style='font-size:11px;color:#4a5568;'>{email_display}</div>", unsafe_allow_html=True)
            with ec2:
                if st.button("👁" if st.session_state.show_email else "🙈", key="eye"):
                    st.session_state.show_email = not st.session_state.show_email
                    st.rerun()

            try:
                statement_date = to_date(data["statement_date"]).strftime("%d %b %Y")
            except Exception:
                statement_date = "—"
            st.markdown(
                f"""
                <div style="font-size:10px;color:#2d3748;margin-top:6px;">STATEMENT · {statement_date}</div>
                </div>""",
                unsafe_allow_html=True,
            )

            if len(st.session_state.profiles) > 1:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                keys = list(st.session_state.profiles.keys())
                index = keys.index(st.session_state.active) if st.session_state.active in keys else 0
                selected = st.selectbox("Switch Profile", keys, index=index, label_visibility="collapsed")
                if selected != st.session_state.active:
                    st.session_state.switch_target = selected
                    st.session_state.pin_ok = False
                if not st.session_state.pin_ok and st.session_state.switch_target:
                    pin = st.text_input("PIN", type="password", max_chars=4, placeholder="••••")
                    if pin == "2002":
                        st.session_state.active = st.session_state.switch_target
                        st.session_state.switch_target = None
                        st.session_state.pin_ok = True
                        st.rerun()
                    elif len(pin) == 4:
                        st.error("Wrong PIN")

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("＋ Add Another CAS", use_container_width=True):
                st.session_state.active = None
                st.session_state.pin_ok = False
                st.rerun()

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("🚪 Logout & Clear Data", use_container_width=True):
                st.session_state.clear()
                st.rerun()

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:10px;color:#2d3748;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-bottom:8px;'>Export</div>",
                unsafe_allow_html=True,
            )

            live_data = st.session_state.get("live_data", {})
            xls = generate_excel(data, live_data)
            if xls:
                st.download_button(
                    "📊 Excel",
                    data=xls,
                    file_name=f"SipCheck_{data['investor_name']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            st.download_button(
                "📄 HTML Report (Print as PDF)",
                data=generate_html(data, live_data),
                file_name=f"SipCheck_{data['investor_name']}.html",
                mime="text/html",
                use_container_width=True,
            )
        else:
            if st.session_state.profiles:
                keys = list(st.session_state.profiles.keys())
                selected = st.selectbox("Return to", ["— select —"] + keys, label_visibility="collapsed")
                if selected != "— select —":
                    st.session_state.active = selected
                    st.session_state.pin_ok = True
                    st.rerun()


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

def render_dashboard(data):
    import dashboard_v2
    dashboard_v2.render_app(
        data,
        legacy={
            "transactions": render_transactions,
            "alerts":       render_alerts,
            "analytics":    render_mf_analytics,
        })

# ─────────────────────────────────────────────
# MY PORTFOLIO
# ─────────────────────────────────────────────

def render_my_portfolio(data):
    st.markdown('<div class="page-title">Portfolio Ledger</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Open holdings and fully redeemed positions</div>', unsafe_allow_html=True)

    cat_colors = {
        "Equity Funds":      "#3B82F6",
        "Debt Funds":        "#06B6D4",
        "Gold & Commodities":"#F59E0B",
        "International":     C_ACCENT2,
    }
    seen_cats = []
    for h in data["holdings"]:
        c = h.get("category", "Equity Funds")
        if c not in seen_cats:
            seen_cats.append(c)
    for category in seen_cats:
        label = category
        color = cat_colors.get(category, C_ACCENT2)
        group = [item for item in data["holdings"] if item["category"] == category]
        if not group:
            continue
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:8px;margin:22px 0 10px;">
              <div style="width:7px;height:7px;border-radius:50%;background:{color};box-shadow:0 0 5px {color};"></div>
              <span style="font-size:11px;font-weight:500;color:{color};letter-spacing:0.08em;">{label}</span>
              <div style="flex:1;height:1px;background:rgba(255,255,255,0.05);"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rows = []
        for item in sorted(group, key=lambda x: x["value"], reverse=True):
            scheme_name = item["scheme"]
            cas_value = item["value"]
            live_value = cas_value
            badge = ""
            show_nav = item.get("cas_nav", 0.0)
            show_date = item.get("cas_date", "—")
            try:
                show_date = to_date(show_date).strftime("%d %b %Y")
            except Exception:
                show_date = "—"
            if st.session_state.live_data and scheme_name in st.session_state.live_data:
                live_value = st.session_state.live_data[scheme_name]["live_value"]
                show_nav = st.session_state.live_data[scheme_name]["nav"]
                show_date = st.session_state.live_data[scheme_name]["date"]
                badge = " 🟢"

            current_pnl = live_value - item["invested"]
            rows.append({
                "Scheme": clean_name(scheme_name) + badge,
                "Invested": fmt_inr(item["invested"]),
                "CAS Value": fmt_inr(cas_value),
                "Live Value": fmt_inr(live_value) if badge else "—",
                "NAV": f"₹{show_nav:,.4f}" if show_nav else "—",
                "NAV Date": show_date,
                "Current P&L": (f"▲ {fmt_inr(current_pnl)}" if current_pnl >= 0 else f"▼ {fmt_inr(current_pnl)}"),
                "XIRR %": f"{item['xirr']:.2f}%",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-sep">Bubble map — invested vs XIRR</div>', unsafe_allow_html=True)
    max_inv = max((h["invested"] for h in data["holdings"] if h["invested"] > 0), default=1)
    df_bubble = pd.DataFrame([
        {
            "Scheme": clean_name(item["scheme"]),
            "Invested": item["invested"],
            "XIRR": item["xirr"],
            "BubbleSize": max(30, (item["invested"] / max_inv) ** 0.5 * 60),
            "Type": item["category"],
        }
        for item in data["holdings"] if item["invested"] > 0
    ])
    if not df_bubble.empty:
        fig_bubble = px.scatter(
            df_bubble,
            x="Invested",
            y="XIRR",
            size="BubbleSize",
            color="Type",
            hover_name="Scheme",
            size_max=40,
            color_discrete_map={"Equity Funds": "#3B82F6", "Gold & Commodities": "#F59E0B", "Debt Funds": "#06B6D4"},
            hover_data={"BubbleSize": False, "Invested": ":,.0f"},
        )
        fig_bubble.update_layout(
            height=340,
            xaxis=dict(showgrid=True, gridcolor=GRID, title="Invested (₹)", tickfont=dict(size=11, color="#718096")),
            yaxis=dict(showgrid=True, gridcolor=GRID, title="XIRR %", tickfont=dict(size=11, color="#718096")),
            legend=dict(font=dict(size=11, color="#718096"), bgcolor="rgba(0,0,0,0)"),
            **PLOT_BASE,
        )
        st.plotly_chart(fig_bubble, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-sep" style="margin-top:36px;">Fully redeemed positions</div>', unsafe_allow_html=True)
    if data.get("redeemed"):
        realized = data["realized_pnl"]
        color = gain_color(realized)
        redeemed_items = data["redeemed"]
        gold_pnl = sum(
            item["profit"] for item in redeemed_items
            if "gold" in item["scheme"].lower() or "silver" in item["scheme"].lower()
        )
        equity_pnl = realized - gold_pnl
        st.markdown(
            f"""
            <div style="background:rgba({'72,187,120' if realized>=0 else '252,129,129'},0.05);
                border:1px solid rgba({'72,187,120' if realized>=0 else '252,129,129'},0.2);
                border-radius:10px;padding:16px 20px;margin-bottom:14px;display:flex;align-items:flex-start;gap:24px;">
              <div style="flex:1;">
                <div style="font-size:11px;color:#718096;letter-spacing:0.08em;margin-bottom:6px;">Total realized P&amp;L</div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                  <span style="font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:700;color:{color};">{gain_arrow(realized)} {fmt_inr(realized)}</span>
                  <span style="font-size:18px;color:{color};">↑</span>
                </div>
                <div style="display:flex;gap:16px;">
                  <span style="font-size:12px;color:#718096;">Equity: <span style="color:#3B82F6;font-weight:600;">{fmt_inr(equity_pnl)}</span></span>
                  <span style="font-size:12px;color:#718096;">Gold: <span style="color:#F59E0B;font-weight:600;">{fmt_inr(gold_pnl)}</span></span>
                </div>
              </div>
              <div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:10px 14px;text-align:center;min-width:80px;">
                <div style="font-size:11px;color:#718096;margin-bottom:4px;">Schemes exited</div>
                <div style="font-size:20px;font-weight:700;color:#e2e8f0;">{len(redeemed_items)}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        redeemed_rows = [
            {
                "Scheme": clean_name(item["scheme"]),
                "Invested": fmt_inr(item["invested"]),
                "Redeemed": fmt_inr(item["redeemed"]),
                "P&L": (f"▲ {fmt_inr(item['profit'])}" if item["profit"] >= 0 else f"▼ {fmt_inr(item['profit'])}"),
            }
            for item in data["redeemed"]
        ]
        st.dataframe(pd.DataFrame(redeemed_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No fully redeemed positions found.")


# ─────────────────────────────────────────────
# SIP CENTER
# ─────────────────────────────────────────────

def render_sip_center(data):
    st.markdown('<div class="page-title">SIP Center</div>', unsafe_allow_html=True)
    live_sips = data.get("live_sips", [])
    dead_sips = data.get("dead_sips", [])

    tab = st.segmented_control(
        "sip_tab",
        [f"🟢 Live ({len(live_sips)})", f"🔴 Inactive ({len(dead_sips)})"],
        default=f"🟢 Live ({len(live_sips)})",
        label_visibility="collapsed",
    )
    if tab is None:
        tab = f"🟢 Live ({len(live_sips)})"
    target_list = live_sips if "Live" in tab else dead_sips
    total_outflow = sum(item["amount"] for item in target_list)
    annual_commit = total_outflow * 12
    is_live_tab = "Live" in tab
    status_label = "live" if is_live_tab else "inactive"
    badge_color = "#48bb78" if is_live_tab else "#fc8181"
    next_debit = min((item["next_date"] for item in target_list), default="—") if target_list else "—"

    st.markdown(
        f"""
        <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;
                    padding:20px 24px;margin-bottom:16px;">
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:20px;align-items:center;">
            <div>
              <div style="font-size:11px;color:#718096;letter-spacing:0.08em;margin-bottom:4px;">Monthly</div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:26px;font-weight:700;color:#48bb78;letter-spacing:-1px;">{fmt_inr(total_outflow)}</div>
            </div>
            <div>
              <div style="font-size:11px;color:#718096;letter-spacing:0.08em;margin-bottom:4px;">Annual commitment</div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:18px;font-weight:600;color:#f7fafc;">{fmt_inr(annual_commit)}</div>
            </div>
            <div>
              <div style="font-size:11px;color:#718096;letter-spacing:0.08em;margin-bottom:4px;">Next debit</div>
              <div style="font-size:16px;font-weight:600;color:#f6ad55;">{next_debit}</div>
            </div>
            <div style="font-size:12px;font-weight:700;color:{badge_color};">{len(target_list)} {status_label}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if target_list:
        is_a = is_live_tab
        badge_bg     = "rgba(72,187,120,0.12)"  if is_a else "rgba(252,129,129,0.12)"
        badge_clr    = "#48bb78"                if is_a else "#fc8181"
        badge_border = "rgba(72,187,120,0.3)"   if is_a else "rgba(252,129,129,0.3)"
        badge_text   = "Live"                   if is_a else "Paused"
        rows_html = "".join(
            f"""<tr style="border-bottom:1px solid rgba(255,255,255,0.04);background:{'transparent' if is_a else 'rgba(252,129,129,0.04)'};">
              <td style="color:#e2e8f0;padding:10px;font-size:13px;font-weight:500;">{clean_name(item['scheme'])}</td>
              <td style="color:#9CA3AF;padding:10px;font-size:13px;">{fmt_inr(item['amount'])}</td>
              <td style="color:#9CA3AF;padding:10px;font-size:13px;">{item['day_label']}</td>
              <td style="color:#9CA3AF;padding:10px;font-size:13px;">{item['last_date']}</td>
              <td style="color:#9CA3AF;padding:10px;font-size:13px;">{item['next_date']}</td>
              <td style="padding:10px;"><span style="background:{badge_bg};color:{badge_clr};border:1px solid {badge_border};border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;">{badge_text}</span></td>
            </tr>"""
            for item in target_list
        )
        st.markdown(
            f"""<table style="width:100%;border-collapse:collapse;">
              <thead><tr style="border-bottom:1px solid rgba(255,255,255,0.06);">
                <th style="color:#718096;font-size:11px;font-weight:500;letter-spacing:0.08em;text-align:left;padding:6px 10px;">Scheme</th>
                <th style="color:#718096;font-size:11px;font-weight:500;letter-spacing:0.08em;text-align:left;padding:6px 10px;">Amount</th>
                <th style="color:#718096;font-size:11px;font-weight:500;letter-spacing:0.08em;text-align:left;padding:6px 10px;">Day</th>
                <th style="color:#718096;font-size:11px;font-weight:500;letter-spacing:0.08em;text-align:left;padding:6px 10px;">Last date</th>
                <th style="color:#718096;font-size:11px;font-weight:500;letter-spacing:0.08em;text-align:left;padding:6px 10px;">Next due</th>
                <th style="color:#718096;font-size:11px;font-weight:500;letter-spacing:0.08em;text-align:left;padding:6px 10px;">Status</th>
              </tr></thead>
              <tbody>{rows_html}</tbody>
            </table>""",
            unsafe_allow_html=True,
        )
    else:
        st.info("No SIPs in this category.")

    all_sips = live_sips + dead_sips
    if all_sips:
        st.markdown('<div class="section-sep">Monthly outflow by scheme</div>', unsafe_allow_html=True)
        df_bar = pd.DataFrame(
            [{"Scheme": clean_name(item["scheme"]), "Amount": item["amount"], "Status": "Live"} for item in live_sips] +
            [{"Scheme": clean_name(item["scheme"]), "Amount": item["amount"], "Status": "Inactive"} for item in dead_sips]
        )
        fig_bar = px.bar(
            df_bar,
            x="Amount",
            y="Scheme",
            orientation="h",
            color="Status",
            color_discrete_map={"Live": "#10B981", "Inactive": "#EF4444"},
            text="Amount",
        )
        fig_bar.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
            textfont=dict(size=10, color="#718096"),
        )
        fig_bar.update_layout(
            height=max(220, len(all_sips) * 32),
            xaxis=dict(visible=False),
            yaxis=dict(tickfont=dict(size=11, color="#718096"), title=""),
            legend=dict(font=dict(size=11, color="#718096"), bgcolor="rgba(0,0,0,0)"),
            **PLOT_BASE,
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
# TRANSACTIONS
# ─────────────────────────────────────────────

def render_transactions(data):
    st.markdown('<div class="page-title">Transaction Ledger</div>', unsafe_allow_html=True)
    tx_map = data.get("tx_map", {})
    agg_map = data.get("agg_map", {})

    if not tx_map:
        st.warning("No transaction data found.")
        return

    selected_scheme = st.selectbox("Select Scheme", list(tx_map.keys()), label_visibility="visible")
    totals = agg_map.get(selected_scheme, {"cost": 0.0, "units": 0.0, "value": 0.0})
    c1, c2, c3 = st.columns(3)
    c1.metric("Book Cost", fmt_inr(totals["cost"]))
    c2.metric("Units", f"{totals['units']:.3f}")
    c3.metric("Current Value", fmt_inr(totals["value"]))

    rows = []
    for transaction in tx_map.get(selected_scheme, []):
        rows.append({
            "Date": to_date(transaction.get("date")).strftime("%d %b %Y") if transaction.get("date") else "—",
            "Description": transaction.get("description", "—"),
            "Amount": fmt_inr(float(transaction["amount"])) if transaction.get("amount") else "—",
            "NAV": f"₹{float(transaction['nav']):,.4f}" if transaction.get("nav") else "—",
            "Units": f"{float(transaction['units']):,.3f}" if transaction.get("units") else "—",
            "Type": transaction.get("type", "—"),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-sep" style="margin-top:28px;">All Holdings — XIRR Table</div>', unsafe_allow_html=True)
    performance = [
        {
            "Scheme": clean_name(item["scheme"]),
            "Invested": fmt_inr(item["invested"]),
            "Value": fmt_inr(item["value"]),
            "P&L": (f"▲ {fmt_inr(item['pnl'])}" if item["pnl"] >= 0 else f"▼ {fmt_inr(item['pnl'])}"),
            "XIRR %": f"{item['xirr']:.2f}%",
            "Category": item["category"],
        }
        for item in data["holdings"]
    ]
    st.dataframe(pd.DataFrame(performance), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────

def render_alerts(data):
    st.markdown('<div class="page-title">Alerts & Insights</div>', unsafe_allow_html=True)

    alerts = []
    for duplicate in data.get("duplicate_alerts", []):
        alerts.append(("warn", "Duplicate SIP Detected", f"{clean_name(duplicate['scheme'])} — {duplicate['count']}× entries on {duplicate['dates']}"))
    for sip in data.get("dead_sips", []):
        alerts.append(("danger", "Inactive SIP", f"{clean_name(sip['scheme'])} — last processed {sip['last_date']}"))
    for holding in [item for item in data["holdings"] if item["pnl"] < 0]:
        alerts.append(("info", "Unrealized Loss", f"{clean_name(holding['scheme'])} — down {fmt_inr(holding['pnl'])} from cost"))

    if not alerts:
        st.markdown(
            """
            <div style="text-align:center;padding:60px 20px;">
              <div style="font-size:48px;margin-bottom:12px;">◎</div>
              <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#f7fafc;margin-bottom:6px;">All Clear</div>
              <div style="font-size:13px;color:#718096;">No alerts detected in your portfolio.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    colors = {"warn": "#f6ad55", "danger": "#fc8181", "info": "#63b3ed"}
    labels = {"warn": "WARNING", "danger": "ACTION REQUIRED", "info": "INFO"}
    for level, title, detail in alerts:
        color = colors.get(level, C_ACCENT)
        label = labels.get(level, "INFO")
        st.markdown(
            f"""
            <div class="alert-card" style="border-color:{color};">
              <div style="font-size:9px;font-weight:700;color:{color};text-transform:uppercase;
                          letter-spacing:1.5px;font-family:'IBM Plex Mono',monospace;margin-bottom:4px;">{label}</div>
              <div style="font-size:14px;font-weight:600;color:#f7fafc;margin-bottom:3px;">{title}</div>
              <div style="font-size:13px;color:#718096;">{detail}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# MF ANALYTICS (React component via CDN)
# ─────────────────────────────────────────────


def render_mf_analytics(data):
    st.markdown('<div class="page-title">MF Analytics</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-sub">Asset allocation · AMC breakdown · SIP · Lumpsum · SWP · STP · Redemptions</div>',
        unsafe_allow_html=True,
    )

    # ── Helper: Extract AMC from scheme name ───────────────────────────────
    def _extract_amc(scheme_name):
        base = scheme_name.split(' - ')[0].strip()
        known = sorted([
            'Aditya Birla Sun Life', 'ICICI Prudential', 'Nippon India',
            'Mirae Asset', 'Motilal Oswal', 'Franklin Templeton', 'PGIM India',
            'Parag Parikh', 'Canara Robeco', 'Baroda BNP Paribas',
            'WhiteOak Capital', 'JM Financial', 'Mahindra Manulife',
            'Invesco India', 'Kotak Mahindra', 'Edelweiss', 'LIC MF',
            'Quant', 'HDFC', 'SBI', 'UTI', 'Axis', 'Kotak', 'Tata',
            'DSP', 'Navi', 'Sundaram', 'Union', 'ITI', 'IDFC', 'BOI',
        ], key=len, reverse=True)
        bl = base.lower()
        for a in known:
            if bl.startswith(a.lower()):
                return a
        words = base.split()
        if len(words) >= 3 and words[1][:1].isupper() and words[2][:1].isupper():
            return ' '.join(words[:3])
        if len(words) >= 2 and len(words) > 1 and words[1][:1].isupper():
            return ' '.join(words[:2])
        return words[0] if words else 'Other'

    # ── 1. Category + AMC Allocation ──────────────────────────────────────
    CAT_COLORS = {
        "Equity Funds":       "#10B981",
        "Debt Funds":         "#3B82F6",
        "Gold & Commodities": "#F59E0B",
        "International":      "#8B5CF6",
    }
    cat_invested = defaultdict(float)
    for h in data.get("holdings", []):
        cat_invested[h["category"]] += h.get("invested", 0)

    alloc = [
        {
            "category": cat,
            "invested": round(cat_invested.get(cat, 0), 2),
            "value":    round(val, 2),
            "color":    CAT_COLORS.get(cat, "#06B6D4"),
        }
        for cat, val in data.get("alloc_values", {}).items()
        if val > 0
    ]

    AMC_PALETTE = [
        "#10B981","#3B82F6","#F59E0B","#8B5CF6","#06B6D4",
        "#F97316","#EC4899","#84CC16","#EF4444","#A78BFA",
    ]
    amc_val = defaultdict(float)
    amc_inv = defaultdict(float)
    for h in data.get("holdings", []):
        amc = _extract_amc(h["scheme"])
        amc_val[amc] += h.get("value", 0)
        amc_inv[amc] += h.get("invested", 0)

    sorted_amcs = sorted(amc_val.items(), key=lambda x: x[1], reverse=True)
    top_amcs    = sorted_amcs[:9]
    others_v    = sum(v for _, v in sorted_amcs[9:])
    others_i    = sum(amc_inv[a] for a, _ in sorted_amcs[9:])
    amc_alloc   = [
        {"amc": a, "value": round(v, 2), "invested": round(amc_inv[a], 2),
         "color": AMC_PALETTE[i % len(AMC_PALETTE)]}
        for i, (a, v) in enumerate(top_amcs)
    ]
    if others_v > 0:
        amc_alloc.append({"amc": "Others", "value": round(others_v, 2),
                          "invested": round(others_i, 2), "color": "#6B7280"})

    # ── 2. Investment Timeline (all + SIP only) ────────────────────────────
    BUY_CLS = {"SIP", "Lumpsum Purchase", "STP In", "Switch In"}
    SIP_CLS = {"SIP"}
    month_totals     = defaultdict(float)
    sip_month_totals = defaultdict(float)
    for txs in data.get("tx_map", {}).values():
        for tx in txs:
            cls = classify_transaction(tx)
            if cls in BUY_CLS:
                amt = abs(float(tx.get("amount") or 0))
                dt  = to_date(tx.get("date"))
                if amt > 0:
                    month_totals[(dt.year, dt.month)] += amt
                    if cls in SIP_CLS:
                        sip_month_totals[(dt.year, dt.month)] += amt

    growth = []
    cumul  = 0.0
    for (yr, mo) in sorted(month_totals.keys()):
        cumul += month_totals[(yr, mo)]
        growth.append({"month": datetime.date(yr, mo, 1).strftime("%b '%y"), "value": round(cumul, 2)})

    sip_growth = []
    sc = 0.0
    for (yr, mo) in sorted(sip_month_totals.keys()):
        sc += sip_month_totals[(yr, mo)]
        sip_growth.append({
            "month":   datetime.date(yr, mo, 1).strftime("%b '%y"),
            "monthly": round(sip_month_totals[(yr, mo)], 2),
            "cumul":   round(sc, 2),
        })

    # ── 3. Lumpsum ─────────────────────────────────────────────────────────
    total_inv      = data.get("total_invested", 0) or 1
    total_val      = data.get("total_value", 0)
    total_lump_inv = data.get("total_lumpsum_invested", 0)
    lump_frac      = total_lump_inv / total_inv if total_inv > 0 else 0
    lump_val       = round(total_val * lump_frac, 2)
    lsummary = {
        "inv": round(total_lump_inv, 2),
        "val": lump_val,
        "roi": round((lump_val - total_lump_inv) / total_lump_inv * 100, 2) if total_lump_inv > 0 else 0,
        "count": sum(1 for h in data.get("holdings", []) if h.get("lumpsum_invested", 0) >= 1),
    }

    lschemes = []
    for h in sorted(data.get("holdings", []), key=lambda x: x.get("lumpsum_invested", 0), reverse=True):
        li = h.get("lumpsum_invested", 0)
        if li < 1:
            continue
        inv  = h.get("invested", 0) or 1
        frac = min(li / inv, 1.0)
        lschemes.append({
            "name": clean_name(h["scheme"])[:40],
            "inv":  round(li, 2),
            "val":  round(h.get("value", 0) * frac, 2),
            "nav":  round(h.get("cas_nav", 0), 4),
            "date": h.get("cas_date", ""),
        })
    lschemes = lschemes[:10]

    # ── 4. SIP Health ──────────────────────────────────────────────────────
    live_sips = data.get("live_sips", [])
    dead_sips = data.get("dead_sips", [])
    all_sips  = live_sips + dead_sips
    n_total   = len(all_sips)
    n_live    = len(live_sips)
    score     = round((n_live / n_total) * 100) if n_total > 0 else 0

    mandates = [
        {"name": clean_name(s["scheme"])[:22], "amt": s["amount"],
         "done": s["installments"], "status": s["status"]}
        for s in all_sips[:10]
    ]
    missed_sips = [
        {"scheme": clean_name(s["scheme"])[:35], "date": s["last_date"], "amt": s["amount"]}
        for s in live_sips if s.get("missed_last_month")
    ][:5]
    sip_full = [
        {"scheme": clean_name(s["scheme"])[:40], "amount": s["amount"],
         "installments": s["installments"], "status": s["status"],
         "lastDate": s["last_date"], "nextDate": s["next_date"]}
        for s in all_sips
    ]
    sip_data = {
        "score":         score,
        "liveCount":     n_live,
        "totalCount":    n_total,
        "totalInvested": round(data.get("total_sip_invested", 0), 2),
        "mandates":      mandates,
        "missed":        missed_sips,
        "bd":            {"live": n_live, "total": n_total, "missed": len(missed_sips)},
    }

    # ── 5. SWP + STP + Switch ──────────────────────────────────────────────
    special_txs = data.get("special_transactions", [])
    swp_txs     = [t for t in special_txs if t["Type"] == "SWP"]
    stp_in_txs  = [t for t in special_txs if t["Type"] == "STP In"]
    stp_out_txs = [t for t in special_txs if t["Type"] == "STP Out"]
    switch_txs  = [t for t in special_txs if t["Type"] in ("Switch Out", "Switch In")]

    monthly_wd = defaultdict(float)
    for t in swp_txs:
        monthly_wd[t["date_obj"].strftime("%b '%y")] += t["Amount"]
    wd_list = [{"m": k, "a": round(v, 2)} for k, v in sorted(monthly_wd.items())]

    stp_monthly = defaultdict(float)
    for t in stp_out_txs:
        stp_monthly[t["date_obj"].strftime("%b '%y")] += t["Amount"]
    stp_list = [{"m": k, "a": round(v, 2)} for k, v in sorted(stp_monthly.items())]

    all_stp = sorted(stp_in_txs + stp_out_txs, key=lambda x: x["date_obj"], reverse=True)
    stp_log = [
        {"date": t["Date"], "scheme": t["Scheme"][:32], "type": t["Type"],
         "val": round(t["Amount"], 2), "units": round(abs(t.get("Units", 0)), 3)}
        for t in all_stp[:10]
    ]
    switch_log = [
        {"date": t["Date"], "scheme": t["Scheme"][:32], "type": t["Type"],
         "val": round(t["Amount"], 2), "units": round(abs(t.get("Units", 0)), 3)}
        for t in sorted(switch_txs, key=lambda x: x["date_obj"], reverse=True)[:10]
    ]

    swp_data = {
        "wd":            wd_list,
        "totalWithdrawn": round(sum(t["Amount"] for t in swp_txs), 2),
        "swpCount":      len(swp_txs),
        "stp":           stp_list,
        "stpLog":        stp_log,
        "totalSTPIn":    round(sum(t["Amount"] for t in stp_in_txs), 2),
        "totalSTPOut":   round(sum(t["Amount"] for t in stp_out_txs), 2),
        "stpCount":      len(stp_out_txs),
        "switchLog":     switch_log,
    }

    # ── 6. Redemptions ─────────────────────────────────────────────────────
    redemp_txs = [t for t in special_txs if t["Type"] == "Redemption"]
    by_scheme  = defaultdict(float)
    for t in redemp_txs:
        by_scheme[t["Scheme"]] += t["Amount"]

    chart_data = [
        {"n": k[:22], "r": round(v, 2)}
        for k, v in sorted(by_scheme.items(), key=lambda x: x[1], reverse=True)[:8]
    ]
    recent_txns = [
        {"s": t["Scheme"][:32], "d": t["Date"],
         "u": round(abs(t.get("Units", 0)), 3), "amt": round(t["Amount"], 2)}
        for t in sorted(redemp_txs, key=lambda x: x["date_obj"], reverse=True)[:10]
    ]
    redeemed_full = [
        {"s": r["scheme"][:32], "inv": round(r["invested"], 2),
         "red": round(r["redeemed"], 2), "profit": round(r["profit"], 2)}
        for r in sorted(data.get("redeemed", []), key=lambda x: x["redeemed"], reverse=True)[:8]
    ]
    total_profit = sum(r["profit"] for r in data.get("redeemed", []))
    redemp_data = {
        "chart":         chart_data,
        "txns":          recent_txns,
        "full":          redeemed_full,
        "totalRedeemed": round(sum(t["Amount"] for t in redemp_txs), 2),
        "txnCount":      len(redemp_txs),
        "totalProfit":   round(total_profit, 2),
    }

    # ── Serialize all data ─────────────────────────────────────────────────
    _data_json = json.dumps({
        "alloc":     alloc,
        "amcAlloc":  amc_alloc,
        "growth":    growth,
        "sipGrowth": sip_growth,
        "lschemes":  lschemes,
        "lsummary":  lsummary,
        "sip":       sip_data,
        "sipFull":   sip_full,
        "swp":       swp_data,
        "redemp":    redemp_data,
        "totalValue": round(total_val, 2),
        "totalInvested": round(data.get("total_invested", 0), 2),
    }, ensure_ascii=False, default=str)

    # ── HTML: pre-data section ─────────────────────────────────────────────
    _pre = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#07090f;color:#e2e8f0;font-family:'Inter','Segoe UI',sans-serif;font-size:14px}

/* ── Tab bar ── */
.tab-bar{position:sticky;top:0;z-index:50;background:#0c0f1a;border-bottom:1px solid #1e2235;display:flex;overflow-x:auto;-webkit-overflow-scrolling:touch;padding:0 8px}
.tab-btn{background:none;border:none;cursor:pointer;padding:13px 18px;font-size:12.5px;font-weight:600;color:#6b7280;border-bottom:2px solid transparent;white-space:nowrap;font-family:inherit;transition:color .2s,border-color .2s;letter-spacing:.3px}
.tab-btn:hover{color:#cbd5e1}
.tab-btn.active{color:#63b3ed;border-bottom-color:#63b3ed}
.tab-content{display:none;padding:18px 16px;max-width:1400px;margin:0 auto}
.tab-content.active{display:block}

/* ── Cards ── */
.card{background:linear-gradient(135deg,#0d1117 0%,#111827 100%);border:1px solid #1e2235;border-radius:12px;padding:18px}
.card-title{color:#e2e8f0;font-weight:700;font-size:14px;margin-bottom:14px;letter-spacing:.2px}
.card-sub{color:#6b7280;font-size:11px;margin-top:-10px;margin-bottom:14px}

/* ── Grids ── */
.grid-2{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.grid-3{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.grid-4{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.flex-col{display:flex;flex-direction:column;gap:16px}

/* ── KPI tiles ── */
.kpi{background:linear-gradient(135deg,#0d1117,#0f1520);border:1px solid #1e2235;border-radius:10px;padding:14px 18px;min-width:130px}
.kpi-label{color:#6b7280;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px}
.kpi-value{font-size:20px;font-weight:800;line-height:1.1}
.kpi-sub{font-size:11px;color:#6b7280;margin-top:4px}

/* ── Table ── */
.data-table{width:100%;border-collapse:collapse;font-size:12px;min-width:520px}
.data-table th{color:#6b7280;text-align:left;padding:8px 10px;font-size:10.5px;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid #1e2235;white-space:nowrap}
.data-table td{padding:9px 10px;border-bottom:1px solid #111827;color:#9ca3af;vertical-align:middle}
.data-table tbody tr:hover{background:rgba(99,179,237,.04)}
.table-wrap{overflow-x:auto;border-radius:8px}

/* ── Badges ── */
.badge{border-radius:5px;padding:2px 8px;font-size:10.5px;font-weight:700;letter-spacing:.3px}
.badge-live{background:rgba(16,185,129,.15);color:#10b981}
.badge-dead{background:rgba(239,68,68,.13);color:#ef4444}
.badge-in{background:rgba(16,185,129,.13);color:#10b981}
.badge-out{background:rgba(239,68,68,.13);color:#ef4444}

/* ── Alloc breakdown ── */
.alloc-item{background:#0d1117;border:1px solid #1e2235;border-radius:8px;padding:10px 14px;margin-bottom:8px;transition:border-color .2s}
.alloc-item:hover{border-color:#2a3a5c}
.pb{background:#1e2235;border-radius:4px;height:5px;margin-top:7px;overflow:hidden}
.pf{height:5px;border-radius:4px;width:0;transition:width 1s cubic-bezier(.4,0,.2,1)}
.row{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px}

/* ── Colors ── */
.green{color:#10b981}.blue{color:#3b82f6}.red{color:#ef4444}.yellow{color:#f59e0b}
.muted{color:#6b7280}.secondary{color:#9ca3af}

/* ── Timeline ── */
.timeline-item{border-left:2px solid #1e2235;padding:0 0 16px 16px;position:relative}
.timeline-item:last-child{padding-bottom:0}
.timeline-dot{width:9px;height:9px;border-radius:50%;position:absolute;left:-5px;top:1px;border:2px solid #07090f}

/* ── Empty state ── */
.empty{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 20px;color:#374151;text-align:center;gap:10px}
.empty svg{opacity:.4}
.empty p{font-size:13px;color:#6b7280}

/* ── Gauge ── */
.gauge-wrap{position:relative;width:200px;height:120px;margin:0 auto}
#sip-gauge-label{position:absolute;bottom:0;left:0;width:100%;text-align:center;line-height:1.2}

/* ── Animations ── */
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.tab-content.active>.*{animation:fadeUp .3s ease-out}
@keyframes barGrow{from{transform:scaleY(0);transform-origin:bottom}to{transform:scaleY(1)}}
</style>
</head>
<body>

<div class="tab-bar">
  <button class="tab-btn active" onclick="showTab('allocation',this)">Asset Allocation</button>
  <button class="tab-btn" onclick="showTab('lumpsum',this)">Lumpsum</button>
  <button class="tab-btn" onclick="showTab('sip',this)">SIP Health</button>
  <button class="tab-btn" onclick="showTab('swp',this)">SWP &amp; STP</button>
  <button class="tab-btn" onclick="showTab('redemptions',this)">Redemptions</button>
</div>

<!-- ── Allocation ── -->
<div id="tab-allocation" class="tab-content active">
  <div class="flex-col">
    <div class="grid-4" id="alloc-kpis"></div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Category Allocation</div>
        <div style="height:260px;position:relative"><canvas id="alloc-donut"></canvas></div>
      </div>
      <div class="card">
        <div class="card-title">AMC / Fund House Allocation</div>
        <div style="height:260px;position:relative"><canvas id="amc-donut"></canvas></div>
      </div>
    </div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Category Breakdown</div>
        <div id="alloc-breakdown"></div>
      </div>
      <div class="card">
        <div class="card-title">Top AMC Breakdown</div>
        <div id="amc-breakdown"></div>
      </div>
    </div>
  </div>
</div>

<!-- ── Lumpsum ── -->
<div id="tab-lumpsum" class="tab-content">
  <div class="flex-col">
    <div class="grid-4" id="lumpsum-kpis"></div>
    <div class="card">
      <div class="card-title">Cumulative Investment Over Time</div>
      <div class="card-sub">All purchases: SIP + Lumpsum + STP In + Switch In</div>
      <div style="height:240px;position:relative"><canvas id="lumpsum-area"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Top Lumpsum Schemes</div>
      <div style="height:220px;position:relative"><canvas id="lumpsum-bar"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Lumpsum Scheme Breakdown</div>
      <div class="table-wrap"><table id="lumpsum-table" class="data-table"></table></div>
    </div>
  </div>
</div>

<!-- ── SIP Health ── -->
<div id="tab-sip" class="tab-content">
  <div class="flex-col">
    <div class="grid-2">
      <div class="card">
        <div class="card-title">SIP Health Score</div>
        <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap">
          <div class="gauge-wrap"><canvas id="sip-gauge" width="200" height="120"></canvas><div id="sip-gauge-label"></div></div>
          <div style="display:flex;gap:10px;flex-wrap:wrap" id="sip-metrics"></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">Monthly SIP Investment</div>
        <div class="card-sub">Amount invested per month via SIP</div>
        <div style="height:180px;position:relative"><canvas id="sip-monthly-bar"></canvas></div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">SIP Cumulative Growth</div>
      <div class="card-sub">Total SIP corpus built over time</div>
      <div style="height:220px;position:relative"><canvas id="sip-growth-area"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">SIP Mandate Installments</div>
      <div style="height:220px;position:relative"><canvas id="sip-bar"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">&#9888; Missed Last Month</div>
      <div id="missed-list"></div>
    </div>
    <div class="card">
      <div class="card-title">All SIP Mandates</div>
      <div class="table-wrap"><table id="sip-table" class="data-table"></table></div>
    </div>
  </div>
</div>

<!-- ── SWP & STP ── -->
<div id="tab-swp" class="tab-content">
  <div class="flex-col">
    <div class="grid-4" id="swp-kpis"></div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Monthly SWP Withdrawals</div>
        <div style="height:220px;position:relative"><canvas id="swp-bar"></canvas></div>
        <div id="swp-empty-msg"></div>
      </div>
      <div class="card">
        <div class="card-title">Monthly STP Transfers</div>
        <div style="height:220px;position:relative"><canvas id="stp-bar"></canvas></div>
        <div id="stp-empty-msg"></div>
      </div>
    </div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Switch Transactions</div>
        <div id="switch-log"></div>
      </div>
      <div class="card">
        <div class="card-title">STP Transaction Log</div>
        <div id="stp-log"></div>
      </div>
    </div>
  </div>
</div>

<!-- ── Redemptions ── -->
<div id="tab-redemptions" class="tab-content">
  <div class="flex-col">
    <div class="grid-4" id="redemp-kpis"></div>
    <div class="card">
      <div class="card-title">Redemptions by Scheme</div>
      <div style="height:240px;position:relative"><canvas id="redemp-bar"></canvas></div>
      <div id="redemp-bar-empty"></div>
    </div>
    <div class="card">
      <div class="card-title">Recent Redemption Transactions</div>
      <div class="table-wrap"><table id="redemp-table" class="data-table"></table></div>
    </div>
    <div class="card" id="redeemed-full-card">
      <div class="card-title">Fully Exited Positions &amp; P&amp;L</div>
      <div class="table-wrap"><table id="redemp-full-table" class="data-table"></table></div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<script>
"""

    # ── HTML: post-data section ────────────────────────────────────────────
    _post = """
// ── Destructure DATA ──
const {alloc,amcAlloc,growth,sipGrowth,lschemes,lsummary,sip,sipFull,swp,redemp,totalValue,totalInvested}=DATA;

// ── Global Chart defaults ──
Chart.defaults.color='#6b7280';
Chart.defaults.borderColor='#1e2235';
Chart.defaults.font.family="'Inter','Segoe UI',sans-serif";
const ANIM={duration:900,easing:'easeInOutQuart'};

// ── Helpers ──
const fmtINR=v=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR',maximumFractionDigits:0}).format(v??0);
const fmtINRS=v=>{const a=Math.abs(v??0);return a>=1e7?`₹${(a/1e7).toFixed(2)}Cr`:a>=1e5?`₹${(a/1e5).toFixed(2)}L`:fmtINR(v)};
const fmtPct=v=>`${(v??0)>=0?'+':''}${(v??0).toFixed(2)}%`;
const pctColor=v=>(v??0)>=0?'#10b981':'#ef4444';

// Chart registry
const CR={};
function nc(id,cfg){
  const el=document.getElementById(id);
  if(!el)return;
  if(CR[id])CR[id].destroy();
  CR[id]=new Chart(el,cfg);
}

// Counter animation
function countUp(el,target,fmt){
  if(!el)return;
  const steps=40,dur=900,interval=dur/steps;
  let i=0;
  const t=setInterval(()=>{
    i++;const v=target*(i/steps);
    el.textContent=fmt(Math.min(v,target));
    if(i>=steps)clearInterval(t);
  },interval);
}

// Empty state HTML
function emptyHTML(msg){
  return `<div class="empty"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg><p>${msg}</p></div>`;
}

// Animate progress bars
function animateBars(){
  setTimeout(()=>{
    document.querySelectorAll('.pf[data-w]').forEach(el=>{
      el.style.width=el.dataset.w+'%';
    });
  },100);
}

// Tab switcher
function showTab(id,btn){
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('tab-'+id).classList.add('active');
  TABS[id]();
}

const TABS={};

// ═══════════════════════════════════════════════════════
//  TAB 1 — ASSET ALLOCATION
// ═══════════════════════════════════════════════════════
TABS.allocation=function(){
  if(!alloc.length){
    document.getElementById('tab-allocation').innerHTML=emptyHTML('No holdings data found.');
    return;
  }
  const totV=alloc.reduce((s,d)=>s+d.value,0);
  const totI=alloc.reduce((s,d)=>s+d.invested,0);
  const pnl=totV-totI;
  const pnlPct=totI>0?(pnl/totI*100).toFixed(2):0;

  // KPI tiles
  const kpiEl=document.getElementById('alloc-kpis');
  kpiEl.innerHTML=[
    {l:'Current Value',  v:totV,    c:'#10b981', fmt:fmtINRS},
    {l:'Total Invested', v:totI,    c:'#63b3ed', fmt:fmtINRS},
    {l:'Unrealised P&L', v:pnl,     c:pnl>=0?'#10b981':'#ef4444', fmt:fmtINRS},
    {l:'Overall Return', v:pnlPct,  c:pnl>=0?'#10b981':'#ef4444', fmt:v=>`${v>=0?'+':''}${parseFloat(v).toFixed(2)}%`},
  ].map(k=>`<div class="kpi"><div class="kpi-label">${k.l}</div><div class="kpi-value" style="color:${k.c}" data-target="${k.v}" data-fmt="${k.fmt}">${k.fmt(k.v)}</div></div>`).join('');

  // Category donut
  nc('alloc-donut',{
    type:'doughnut',
    data:{
      labels:alloc.map(d=>d.category),
      datasets:[{data:alloc.map(d=>d.value),backgroundColor:alloc.map(d=>d.color),borderWidth:2,borderColor:'#07090f',hoverOffset:10}]
    },
    options:{
      responsive:true,maintainAspectRatio:false,cutout:'64%',animation:ANIM,
      plugins:{
        legend:{position:'bottom',labels:{color:'#9ca3af',font:{size:11},padding:12,boxWidth:10}},
        tooltip:{callbacks:{label:ctx=>`  ${ctx.label}: ${fmtINRS(ctx.parsed)} (${(ctx.parsed/totV*100).toFixed(1)}%)`}}
      }
    }
  });

  // AMC donut
  if(amcAlloc.length){
    const amcTot=amcAlloc.reduce((s,d)=>s+d.value,0);
    nc('amc-donut',{
      type:'doughnut',
      data:{
        labels:amcAlloc.map(d=>d.amc),
        datasets:[{data:amcAlloc.map(d=>d.value),backgroundColor:amcAlloc.map(d=>d.color),borderWidth:2,borderColor:'#07090f',hoverOffset:10}]
      },
      options:{
        responsive:true,maintainAspectRatio:false,cutout:'64%',animation:ANIM,
        plugins:{
          legend:{position:'bottom',labels:{color:'#9ca3af',font:{size:10},padding:10,boxWidth:9}},
          tooltip:{callbacks:{label:ctx=>`  ${ctx.label}: ${fmtINRS(ctx.parsed)} (${(ctx.parsed/amcTot*100).toFixed(1)}%)`}}
        }
      }
    });
  }

  // Category breakdown
  document.getElementById('alloc-breakdown').innerHTML=
    alloc.map(d=>{
      const g=d.value-d.invested,pct=(d.value/totV*100).toFixed(1),ret=d.invested>0?((g/d.invested)*100).toFixed(1):0;
      return `<div class="alloc-item">
        <div class="row" style="margin-bottom:5px">
          <div style="display:flex;align-items:center;gap:8px">
            <div style="width:10px;height:10px;border-radius:50%;background:${d.color};flex-shrink:0"></div>
            <span style="color:#e2e8f0;font-weight:600;font-size:13px">${d.category}</span>
          </div>
          <span style="color:#e2e8f0;font-weight:800;font-size:14px">${pct}%</span>
        </div>
        <div class="row" style="font-size:11.5px;margin-bottom:7px">
          <span class="secondary">Inv: ${fmtINRS(d.invested)}</span>
          <span style="color:#63b3ed">Val: ${fmtINRS(d.value)}</span>
          <span style="color:${pnlColor(g)};font-weight:700">${g>=0?'+':''}${fmtINRS(g)} (${ret}%)</span>
        </div>
        <div class="pb"><div class="pf" data-w="${pct}" style="background:${d.color}"></div></div>
      </div>`;
    }).join('');

  // AMC breakdown
  if(amcAlloc.length){
    const amcTot=amcAlloc.reduce((s,d)=>s+d.value,0);
    document.getElementById('amc-breakdown').innerHTML=
      amcAlloc.map(d=>{
        const pct=(d.value/amcTot*100).toFixed(1);
        const g=d.value-d.invested, ret=d.invested>0?((g/d.invested)*100).toFixed(1):0;
        return `<div class="alloc-item">
          <div class="row" style="margin-bottom:5px">
            <div style="display:flex;align-items:center;gap:8px">
              <div style="width:10px;height:10px;border-radius:50%;background:${d.color};flex-shrink:0"></div>
              <span style="color:#e2e8f0;font-weight:600;font-size:12.5px">${d.amc}</span>
            </div>
            <span style="color:#e2e8f0;font-weight:800">${pct}%</span>
          </div>
          <div class="row" style="font-size:11px;margin-bottom:7px">
            <span class="secondary">Inv: ${fmtINRS(d.invested)}</span>
            <span style="color:#63b3ed">Val: ${fmtINRS(d.value)}</span>
            <span style="color:${pnlColor(g)};font-weight:700">${g>=0?'+':''}${fmtINRS(g)}</span>
          </div>
          <div class="pb"><div class="pf" data-w="${pct}" style="background:${d.color}"></div></div>
        </div>`;
      }).join('');
  }
  animateBars();
};

function pnlColor(v){return v>=0?'#10b981':'#ef4444';}

// ═══════════════════════════════════════════════════════
//  TAB 2 — LUMPSUM
// ═══════════════════════════════════════════════════════
TABS.lumpsum=function(){
  const ls=lsummary;
  // KPI tiles
  document.getElementById('lumpsum-kpis').innerHTML=[
    {l:'Lumpsum Invested', v:ls.inv, c:'#9ca3af', fmt:fmtINRS},
    {l:'Current Value',    v:ls.val, c:'#10b981', fmt:fmtINRS},
    {l:'Est. Gain/Loss',   v:ls.val-ls.inv, c:pnlColor(ls.val-ls.inv), fmt:fmtINRS},
    {l:'Est. Return',      v:ls.roi, c:pnlColor(ls.roi), fmt:v=>`${v>=0?'+':''}${v.toFixed(2)}%`},
  ].map(k=>`<div class="kpi"><div class="kpi-label">${k.l}</div><div class="kpi-value" style="color:${k.c}">${k.fmt(k.v)}</div></div>`).join('');

  // Cumulative area chart
  if(growth.length){
    nc('lumpsum-area',{
      type:'line',
      data:{
        labels:growth.map(d=>d.month),
        datasets:[{
          label:'Cumulative Invested',
          data:growth.map(d=>d.value),
          borderColor:'#63b3ed',borderWidth:2.5,fill:true,
          backgroundColor:'rgba(99,179,237,0.08)',pointRadius:0,tension:0.4
        }]
      },
      options:{
        responsive:true,maintainAspectRatio:false,animation:ANIM,
        plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`  ${fmtINRS(ctx.parsed.y)}`}}},
        scales:{
          x:{ticks:{color:'#6b7280',font:{size:10},maxTicksLimit:10},grid:{display:false}},
          y:{ticks:{color:'#6b7280',font:{size:10},callback:v=>fmtINRS(v)},grid:{color:'#1e2235'}}
        }
      }
    });
  } else {
    document.getElementById('lumpsum-area').parentElement.innerHTML=emptyHTML('No investment timeline data.');
  }

  // Top schemes bar chart
  if(lschemes.length){
    nc('lumpsum-bar',{
      type:'bar',
      data:{
        labels:lschemes.map(s=>s.name.length>18?s.name.slice(0,16)+'…':s.name),
        datasets:[
          {label:'Invested',data:lschemes.map(s=>s.inv),backgroundColor:'rgba(99,179,237,0.7)',borderRadius:5,borderSkipped:false},
          {label:'Current Value',data:lschemes.map(s=>s.val),backgroundColor:'rgba(16,185,129,0.7)',borderRadius:5,borderSkipped:false},
        ]
      },
      options:{
        responsive:true,maintainAspectRatio:false,animation:ANIM,
        plugins:{
          legend:{labels:{color:'#9ca3af',font:{size:11},boxWidth:10}},
          tooltip:{callbacks:{label:ctx=>`  ${ctx.dataset.label}: ${fmtINRS(ctx.parsed.y)}`}}
        },
        scales:{
          x:{ticks:{color:'#6b7280',font:{size:10}},grid:{display:false}},
          y:{ticks:{color:'#6b7280',font:{size:10},callback:v=>fmtINRS(v)},grid:{color:'#1e2235'}}
        }
      }
    });
  } else {
    document.getElementById('lumpsum-bar').parentElement.innerHTML=emptyHTML('No lumpsum investments found.');
  }

  // Table
  if(!lschemes.length){
    document.getElementById('lumpsum-table').parentElement.innerHTML=emptyHTML('No lumpsum investments found.');
    return;
  }
  const ths=['Scheme','Invested','Current Value','NAV','Return %'].map(h=>`<th>${h}</th>`).join('');
  const rows=lschemes.map(s=>{
    const ret=s.inv>0?((s.val-s.inv)/s.inv*100):0;
    return `<tr>
      <td style="color:#e2e8f0;font-weight:500">${s.name}</td>
      <td style="color:#9ca3af">${fmtINR(s.inv)}</td>
      <td style="color:#10b981;font-weight:600">${fmtINR(s.val)}</td>
      <td style="font-family:monospace;color:#6b7280;font-size:11px">₹${s.nav.toFixed(4)}</td>
      <td><span style="color:${pnlColor(ret)};font-weight:700">${fmtPct(ret)}</span></td>
    </tr>`;
  }).join('');
  document.getElementById('lumpsum-table').innerHTML=`<thead><tr>${ths}</tr></thead><tbody>${rows}</tbody>`;
};

// ═══════════════════════════════════════════════════════
//  TAB 3 — SIP HEALTH
// ═══════════════════════════════════════════════════════
TABS.sip=function(){
  const sc=sip.score,nl=sip.liveCount,nt=sip.totalCount;
  const col=sc>=75?'#10b981':sc>=50?'#f59e0b':'#ef4444';

  // Gauge
  nc('sip-gauge',{
    type:'doughnut',
    data:{datasets:[{data:[sc,100-sc],backgroundColor:[col,'#1e2235'],borderWidth:0,circumference:180,rotation:-90}]},
    options:{responsive:false,animation:ANIM,cutout:'72%',plugins:{legend:{display:false},tooltip:{enabled:false}}}
  });
  document.getElementById('sip-gauge-label').innerHTML=
    `<span style="font-size:34px;font-weight:900;color:${col}">${sc}</span><span style="color:#6b7280;font-size:13px">/100</span><br>
     <span style="color:#6b7280;font-size:11px">${sc>=75?'Excellent':sc>=50?'Good':'Needs Attention'}</span>`;

  // KPI metrics
  document.getElementById('sip-metrics').innerHTML=[
    {l:'Active SIPs',   v:nl,                        c:'#10b981'},
    {l:'Total SIPs',    v:nt,                        c:'#63b3ed'},
    {l:'Missed',        v:sip.missed.length,         c:'#ef4444'},
    {l:'SIP Corpus',    v:fmtINRS(sip.totalInvested),c:'#9ca3af'},
  ].map(m=>`<div class="kpi" style="text-align:center;min-width:100px">
      <div style="color:${m.c};font-size:22px;font-weight:800">${m.v}</div>
      <div class="kpi-label" style="margin-top:4px">${m.l}</div>
    </div>`).join('');

  // Monthly SIP bar
  if(sipGrowth.length){
    const last24=sipGrowth.slice(-24);
    nc('sip-monthly-bar',{
      type:'bar',
      data:{
        labels:last24.map(d=>d.month),
        datasets:[{label:'Monthly SIP',data:last24.map(d=>d.monthly),backgroundColor:'rgba(16,185,129,0.7)',borderRadius:4,borderSkipped:false}]
      },
      options:{
        responsive:true,maintainAspectRatio:false,animation:ANIM,
        plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`  ${fmtINR(ctx.parsed.y)}`}}},
        scales:{
          x:{ticks:{color:'#6b7280',font:{size:9},maxRotation:45},grid:{display:false}},
          y:{ticks:{color:'#6b7280',font:{size:10},callback:v=>fmtINRS(v)},grid:{color:'#1e2235'}}
        }
      }
    });

    // SIP cumulative growth area
    nc('sip-growth-area',{
      type:'line',
      data:{
        labels:sipGrowth.map(d=>d.month),
        datasets:[{
          label:'Cumulative SIP',
          data:sipGrowth.map(d=>d.cumul),
          borderColor:'#10b981',borderWidth:2.5,fill:true,
          backgroundColor:'rgba(16,185,129,0.08)',pointRadius:0,tension:0.4
        }]
      },
      options:{
        responsive:true,maintainAspectRatio:false,animation:ANIM,
        plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`  Corpus: ${fmtINRS(ctx.parsed.y)}`}}},
        scales:{
          x:{ticks:{color:'#6b7280',font:{size:10},maxTicksLimit:12},grid:{display:false}},
          y:{ticks:{color:'#6b7280',font:{size:10},callback:v=>fmtINRS(v)},grid:{color:'#1e2235'}}
        }
      }
    });
  } else {
    document.getElementById('sip-monthly-bar').parentElement.innerHTML=emptyHTML('No SIP transactions found.');
    document.getElementById('sip-growth-area').parentElement.innerHTML=emptyHTML('No SIP transactions found.');
  }

  // Mandates bar
  if(sip.mandates.length){
    nc('sip-bar',{
      type:'bar',
      data:{
        labels:sip.mandates.map(m=>m.name),
        datasets:[
          {label:'Installments Done',data:sip.mandates.map(m=>m.done),backgroundColor:sip.mandates.map(m=>m.status==='Live'?'rgba(16,185,129,0.75)':'rgba(239,68,68,0.6)'),borderRadius:5,borderSkipped:false},
        ]
      },
      options:{
        indexAxis:'y',responsive:true,maintainAspectRatio:false,animation:ANIM,
        plugins:{
          legend:{display:false},
          tooltip:{callbacks:{label:ctx=>`  ${ctx.parsed.x} installments | ₹${ctx.chart.data.datasets[0].data[ctx.dataIndex].toLocaleString('en-IN')}`}}
        },
        scales:{
          x:{ticks:{color:'#6b7280',font:{size:10}},grid:{color:'#1e2235'}},
          y:{ticks:{color:'#e2e8f0',font:{size:10}},grid:{display:false}}
        }
      }
    });
  } else {
    document.getElementById('sip-bar').parentElement.innerHTML=emptyHTML('No SIP mandates found.');
  }

  // Missed list
  document.getElementById('missed-list').innerHTML=sip.missed.length
    ? sip.missed.map(m=>`<div style="background:#0d1117;border:1px solid #2d1515;border-radius:8px;padding:12px 16px;margin-bottom:8px">
        <div style="color:#ef4444;font-weight:700;font-size:13px">${m.scheme}</div>
        <div class="secondary" style="font-size:11.5px;margin-top:4px">Last deducted: ${m.date} &middot; ${fmtINR(m.amt)}/month</div>
        <div style="color:#ef4444;font-size:11px;margin-top:3px">No deduction detected in last 39 days</div>
      </div>`).join('')
    : emptyHTML('All active SIPs are on track &mdash; no missed payments detected.');

  // Full SIP table
  const sths=['Scheme','Amount','Installments','Status','Last Date','Next Date'].map(h=>`<th>${h}</th>`).join('');
  const strows=(sipFull||[]).map(s=>{
    const bc=s.status==='Live'?'badge-live':'badge-dead';
    return `<tr>
      <td style="color:#e2e8f0;font-weight:500">${s.scheme}</td>
      <td style="color:#63b3ed;font-weight:600">${fmtINR(s.amount)}</td>
      <td>${s.installments}</td>
      <td><span class="badge ${bc}">${s.status}</span></td>
      <td style="color:#9ca3af;font-size:11.5px">${s.lastDate}</td>
      <td style="color:#9ca3af;font-size:11.5px">${s.nextDate}</td>
    </tr>`;
  }).join('');
  document.getElementById('sip-table').innerHTML=sipFull&&sipFull.length
    ? `<thead><tr>${sths}</tr></thead><tbody>${strows}</tbody>`
    : `<thead><tr>${sths}</tr></thead><tbody><tr><td colspan="6">${emptyHTML('No SIP mandates found.')}</td></tr></tbody>`;
};

// ═══════════════════════════════════════════════════════
//  TAB 4 — SWP & STP
// ═══════════════════════════════════════════════════════
TABS.swp=function(){
  // KPI tiles
  document.getElementById('swp-kpis').innerHTML=[
    {l:'Total SWP Withdrawn', v:swp.totalWithdrawn, c:'#ef4444', fmt:fmtINRS},
    {l:'SWP Transactions',    v:swp.swpCount+' txns', c:'#9ca3af', fmt:v=>v},
    {l:'Total STP Out',       v:swp.totalSTPOut,   c:'#f59e0b', fmt:fmtINRS},
    {l:'STP Transactions',    v:swp.stpCount+' txns', c:'#9ca3af', fmt:v=>v},
  ].map(k=>`<div class="kpi"><div class="kpi-label">${k.l}</div><div class="kpi-value" style="color:${k.c}">${k.fmt(k.v)}</div></div>`).join('');

  // SWP monthly bar
  if(swp.wd.length){
    document.getElementById('swp-bar').style.display='block';
    nc('swp-bar',{
      type:'bar',
      data:{
        labels:swp.wd.map(d=>d.m),
        datasets:[{label:'Withdrawn',data:swp.wd.map(d=>d.a),backgroundColor:'rgba(239,68,68,0.7)',borderRadius:4,borderSkipped:false}]
      },
      options:{
        responsive:true,maintainAspectRatio:false,animation:ANIM,
        plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`  ${fmtINR(ctx.parsed.y)}`}}},
        scales:{
          x:{ticks:{color:'#6b7280',font:{size:10}},grid:{display:false}},
          y:{ticks:{color:'#6b7280',font:{size:10},callback:v=>fmtINRS(v)},grid:{color:'#1e2235'}}
        }
      }
    });
    document.getElementById('swp-empty-msg').innerHTML='';
  } else {
    document.getElementById('swp-bar').style.display='none';
    document.getElementById('swp-empty-msg').innerHTML=emptyHTML('No SWP (Systematic Withdrawal Plan) transactions found in this portfolio.');
  }

  // STP monthly bar
  if(swp.stp.length){
    document.getElementById('stp-bar').style.display='block';
    nc('stp-bar',{
      type:'bar',
      data:{
        labels:swp.stp.map(d=>d.m),
        datasets:[{label:'STP Out',data:swp.stp.map(d=>d.a),backgroundColor:'rgba(245,158,11,0.7)',borderRadius:4,borderSkipped:false}]
      },
      options:{
        responsive:true,maintainAspectRatio:false,animation:ANIM,
        plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`  ${fmtINR(ctx.parsed.y)}`}}},
        scales:{
          x:{ticks:{color:'#6b7280',font:{size:10}},grid:{display:false}},
          y:{ticks:{color:'#6b7280',font:{size:10},callback:v=>fmtINRS(v)},grid:{color:'#1e2235'}}
        }
      }
    });
    document.getElementById('stp-empty-msg').innerHTML='';
  } else {
    document.getElementById('stp-bar').style.display='none';
    document.getElementById('stp-empty-msg').innerHTML=emptyHTML('No STP (Systematic Transfer Plan) transactions found.');
  }

  // Switch log timeline
  document.getElementById('switch-log').innerHTML=swp.switchLog.length
    ? swp.switchLog.map((sw,i)=>{
        const isOut=sw.type==='Switch Out';
        return `<div class="timeline-item">
          <div class="timeline-dot" style="background:${isOut?'#ef4444':'#10b981'}"></div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">
            <span class="muted" style="font-size:10.5px">${sw.date}</span>
            <span class="badge ${isOut?'badge-out':'badge-in'}">${isOut?'OUT':'IN'}</span>
          </div>
          <div style="color:#e2e8f0;font-weight:600;font-size:12.5px;margin-bottom:3px">${sw.scheme}</div>
          <div class="secondary" style="font-size:11.5px">${sw.units>0?sw.units.toFixed(3)+' units &middot; ':''} ${fmtINR(sw.val)}</div>
        </div>`;
      }).join('')
    : emptyHTML('No switch transactions found in this portfolio.');

  // STP log timeline
  document.getElementById('stp-log').innerHTML=swp.stpLog.length
    ? swp.stpLog.map((t,i)=>{
        const isOut=t.type==='STP Out';
        return `<div class="timeline-item">
          <div class="timeline-dot" style="background:${isOut?'#f59e0b':'#10b981'}"></div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">
            <span class="muted" style="font-size:10.5px">${t.date}</span>
            <span class="badge" style="background:rgba(245,158,11,.13);color:#f59e0b">${t.type}</span>
          </div>
          <div style="color:#e2e8f0;font-weight:600;font-size:12.5px;margin-bottom:3px">${t.scheme}</div>
          <div class="secondary" style="font-size:11.5px">${t.units>0?t.units.toFixed(3)+' units &middot; ':''} ${fmtINR(t.val)}</div>
        </div>`;
      }).join('')
    : emptyHTML('No STP (Systematic Transfer Plan) transactions found.');
};

// ═══════════════════════════════════════════════════════
//  TAB 5 — REDEMPTIONS
// ═══════════════════════════════════════════════════════
TABS.redemptions=function(){
  const tr=redemp.totalRedeemed, tp=redemp.totalProfit||0;

  // KPI tiles
  document.getElementById('redemp-kpis').innerHTML=[
    {l:'Total Redeemed',   v:tr,               c:'#63b3ed', fmt:fmtINRS},
    {l:'Realised P&L',     v:tp,               c:pnlColor(tp), fmt:fmtINRS},
    {l:'Redemption Txns',  v:redemp.txnCount,  c:'#9ca3af', fmt:v=>v},
    {l:'Schemes Exited',   v:redemp.full.length,c:'#9ca3af', fmt:v=>v},
  ].map(k=>`<div class="kpi"><div class="kpi-label">${k.l}</div><div class="kpi-value" style="color:${k.c}">${k.fmt(k.v)}</div></div>`).join('');

  // Bar chart
  if(redemp.chart.length){
    document.getElementById('redemp-bar').style.display='block';
    document.getElementById('redemp-bar-empty').innerHTML='';
    nc('redemp-bar',{
      type:'bar',
      data:{
        labels:redemp.chart.map(d=>d.n),
        datasets:[{label:'Redeemed',data:redemp.chart.map(d=>d.r),backgroundColor:'rgba(16,185,129,0.7)',borderRadius:5,borderSkipped:false}]
      },
      options:{
        responsive:true,maintainAspectRatio:false,animation:ANIM,
        plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`  ${fmtINR(ctx.parsed.y)}`}}},
        scales:{
          x:{ticks:{color:'#6b7280',font:{size:11}},grid:{display:false}},
          y:{ticks:{color:'#6b7280',font:{size:10},callback:v=>fmtINRS(v)},grid:{color:'#1e2235'}}
        }
      }
    });
  } else {
    document.getElementById('redemp-bar').style.display='none';
    document.getElementById('redemp-bar-empty').innerHTML=emptyHTML('No redemption transactions found in this portfolio.');
  }

  // Recent transactions table
  const rths=['Scheme','Date','Units','Amount'].map(h=>`<th>${h}</th>`).join('');
  if(redemp.txns.length){
    const rrows=redemp.txns.map(t=>`<tr>
      <td style="color:#e2e8f0;font-weight:500">${t.s}</td>
      <td style="color:#9ca3af;font-size:11.5px;white-space:nowrap">${t.d}</td>
      <td style="font-family:monospace;color:#6b7280">${t.u}</td>
      <td style="color:#10b981;font-weight:600">${fmtINR(t.amt)}</td>
    </tr>`).join('');
    const rfooter=`<tr style="background:#0d1117"><td colspan="3" style="color:#9ca3af;font-weight:700;padding:10px">Total Redeemed</td><td style="color:#10b981;font-weight:700;padding:10px">${fmtINR(redemp.totalRedeemed)}</td></tr>`;
    document.getElementById('redemp-table').innerHTML=`<thead><tr>${rths}</tr></thead><tbody>${rrows}</tbody><tfoot>${rfooter}</tfoot>`;
  } else {
    document.getElementById('redemp-table').parentElement.innerHTML=emptyHTML('No redemption transactions found.');
  }

  // Fully exited P&L
  const fcard=document.getElementById('redeemed-full-card');
  if(redemp.full.length){
    fcard.style.display='block';
    const fths=['Scheme','Invested','Redeemed','P&L','Return'].map(h=>`<th>${h}</th>`).join('');
    const frows=redemp.full.map(r=>{
      const ret=r.inv>0?((r.profit/r.inv)*100).toFixed(1):0;
      return `<tr>
        <td style="color:#e2e8f0;font-weight:500">${r.s}</td>
        <td style="color:#9ca3af">${fmtINR(r.inv)}</td>
        <td style="color:#10b981;font-weight:600">${fmtINR(r.red)}</td>
        <td style="color:${pnlColor(r.profit)};font-weight:700">${fmtINRS(r.profit)}</td>
        <td><span style="color:${pnlColor(ret)};font-weight:700">${ret>=0?'+':''}${ret}%</span></td>
      </tr>`;
    }).join('');
    document.getElementById('redemp-full-table').innerHTML=`<thead><tr>${fths}</tr></thead><tbody>${frows}</tbody>`;
  } else {
    fcard.style.display='none';
  }
};

// Initial render
TABS.allocation();
</script>
</body>
</html>"""

    _html = _pre + "const DATA=" + _data_json + ";\n" + _post
    components.html(_html, height=1100, scrolling=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def run_app():
    apply_page_config()
    inject_global_styles()
    initialize_session_state()
    render_sidebar()
    active = active_data()
    build_sidebar(active)
    if not active:
        show_upload()
        st.stop()
    render_dashboard(active)


run_app()