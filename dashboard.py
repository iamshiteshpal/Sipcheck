import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import io
import tempfile
import datetime
import requests
from datetime import date
from collections import Counter
from pyxirr import xirr
import casparser

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CAS 360 View — Portfolio Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL STYLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Instrument+Sans:wght@400;500;600&display=swap');
:root {
  --bg:#07090f; --bg2:#0c0f1a; --bg3:#111627;
  --border:rgba(255,255,255,0.06); --border-hi:rgba(99,179,237,0.35);
  --accent:#63b3ed; --accent2:#9f7aea;
  --gain:#48bb78; --loss:#fc8181; --warn:#f6ad55;
  --text:#e2e8f0; --muted:#718096; --faint:#2d3748;
}
*,*::before,*::after{box-sizing:border-box;}
html,body,.stApp{background:var(--bg)!important;color:var(--text)!important;font-family:'Instrument Sans',sans-serif!important;}
.stApp::after{content:'';position:fixed;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");pointer-events:none;z-index:9999;}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *{font-family:'Instrument Sans',sans-serif!important;}
div[data-testid="stMetric"]{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:12px!important;padding:18px 20px!important;transition:border-color .25s,transform .2s;}
div[data-testid="stMetric"]:hover{border-color:var(--border-hi)!important;transform:translateY(-2px);}
div[data-testid="stMetricValue"]>div{font-family:'IBM Plex Mono',monospace!important;font-size:20px!important;font-weight:600!important;color:#f7fafc!important;}
div[data-testid="stMetricLabel"]>div{font-size:10px!important;color:var(--muted)!important;text-transform:uppercase;letter-spacing:1.4px;font-weight:500!important;}
div[data-testid="stMetricDelta"]>div{font-size:11px!important;}
[data-testid="stVerticalBlockBorderWrapper"]>div>div{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:14px!important;}
[data-testid="stVerticalBlockBorderWrapper"]>div>div:hover{border-color:rgba(99,179,237,0.2)!important;}
[data-testid="stDataFrame"]{border-radius:10px!important;overflow:hidden;border:1px solid var(--border)!important;}
[data-testid="stSelectbox"]>div>div,[data-testid="stTextInput"] input{background:var(--bg3)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:var(--text)!important;}
[data-testid="stTextInput"] input{font-family:'IBM Plex Mono',monospace!important;}
[data-testid="stFileUploader"]{background:rgba(99,179,237,0.03)!important;border:2px dashed rgba(99,179,237,0.2)!important;border-radius:14px!important;}
[data-testid="stSegmentedControl"]>div{background:var(--bg3)!important;border:1px solid var(--border)!important;border-radius:8px!important;}
[data-testid="stSegmentedControl"] button[aria-checked="true"]{background:linear-gradient(135deg,#2b6cb0,#553c9a)!important;color:#fff!important;border-radius:6px!important;}
hr{border-color:var(--border)!important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--faint);border-radius:4px;}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:22px 24px;margin-bottom:16px;position:relative;}
.card-title{font-family:'Syne',sans-serif;font-size:11px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:2px;margin-bottom:14px;}
.pill-gain{display:inline-flex;align-items:center;gap:4px;background:rgba(72,187,120,0.1);border:1px solid rgba(72,187,120,0.25);color:var(--gain);font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;padding:2px 10px;border-radius:20px;}
.pill-loss{display:inline-flex;align-items:center;gap:4px;background:rgba(252,129,129,0.1);border:1px solid rgba(252,129,129,0.25);color:var(--loss);font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;padding:2px 10px;border-radius:20px;}
.pill-live{display:inline-flex;align-items:center;gap:5px;background:rgba(72,187,120,0.08);border:1px solid rgba(72,187,120,0.3);color:#48bb78;font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.5px;}
.pill-cas{display:inline-flex;align-items:center;gap:5px;background:rgba(99,179,237,0.08);border:1px solid rgba(99,179,237,0.2);color:#63b3ed;font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.5px;}
.notice{background:rgba(99,179,237,0.05);border:1px solid rgba(99,179,237,0.15);border-left:3px solid var(--accent);border-radius:0 10px 10px 0;padding:12px 16px;font-size:13px;color:var(--muted);margin-bottom:22px;display:flex;align-items:flex-start;gap:10px;}
.live-notice{background:rgba(72,187,120,0.05);border:1px solid rgba(72,187,120,0.2);border-left:3px solid #48bb78;border-radius:0 10px 10px 0;padding:12px 16px;font-size:13px;color:var(--muted);margin-bottom:22px;display:flex;align-items:flex-start;gap:10px;}
.section-sep{font-size:10px;font-weight:700;color:var(--faint);text-transform:uppercase;letter-spacing:2px;margin:24px 0 12px;display:flex;align-items:center;gap:10px;}
.section-sep::after{content:'';flex:1;height:1px;background:var(--border);}
.page-title{font-family:'Syne',sans-serif;font-size:26px;font-weight:800;color:#f7fafc;letter-spacing:-0.5px;margin-bottom:4px;}
.page-sub{font-size:13px;color:var(--muted);margin-bottom:22px;}
.alloc-row{display:flex;align-items:center;justify-content:space-between;padding:9px 0;border-bottom:1px solid var(--border);}
.alloc-dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:8px;}
.alert-card{border-left:3px solid;border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:10px;background:var(--bg2);}
.nav-diff-up{color:#48bb78;font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;}
.nav-diff-dn{color:#fc8181;font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;}
div[data-testid="stAppViewBlockContainer"]{padding-top:2.5rem!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PLOT DEFAULTS
# ══════════════════════════════════════════════════════════════════════════════
PLOT_BASE = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Instrument Sans', color='#718096'),
    margin=dict(l=0, r=0, t=10, b=10),
)
GRID = 'rgba(255,255,255,0.04)'
C_GAIN = '#48bb78'; C_LOSS = '#fc8181'; C_ACCENT = '#63b3ed'; C_ACCENT2 = '#9f7aea'

# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def to_date(d):
    if not d: return date.today()
    if isinstance(d, str):
        try: return datetime.datetime.strptime(d.split("T")[0], "%Y-%m-%d").date()
        except: return date.today()
    if hasattr(d, "date"): return d.date()
    return d

def to_dict(obj):
    if isinstance(obj, dict): return {k: to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list): return [to_dict(i) for i in obj]
    if hasattr(obj, "model_dump"): return to_dict(obj.model_dump())
    if hasattr(obj, "dict"): return to_dict(obj.dict())
    return obj

def clean_name(name):
    if not name: return "Unknown Scheme"
    for sfx in ["- Direct Plan - Growth Option","- Direct Plan - Growth","- Direct Growth Plan",
                "- Direct Plan Growth","Direct Plan Growth","Direct Growth","Direct Plan","Regular Plan","Growth"]:
        name = name.replace(sfx, "")
    return name.strip()

def ordinal(n):
    suffix = "th" if 11<=n<=13 else {1:"st",2:"nd",3:"rd"}.get(n%10,"th")
    return f"{n}{suffix}"

def next_due_date(dom: int) -> date:
    today = date.today()
    try: candidate = today.replace(day=dom)
    except ValueError: candidate = today.replace(day=28)
    if candidate <= today:
        m, y = today.month+1, today.year
        if m > 12: m, y = 1, y+1
        try: candidate = candidate.replace(year=y, month=m)
        except ValueError: candidate = candidate.replace(year=y, month=m, day=28)
    return candidate

def calc_xirr(transactions, current_value, valuation_date_str):
    dates, amounts = [], []
    for tx in transactions:
        try:
            dt = to_date(tx.get("date")); amt = float(tx.get("amount", 0.0))
            if amt > 0: dates.append(dt); amounts.append(-amt)
        except: continue
    if current_value > 0:
        try: dates.append(to_date(valuation_date_str)); amounts.append(current_value)
        except: pass
    if len(amounts) >= 2 and sum(amounts) != 0:
        try:
            rate = xirr(dates, amounts)
            return rate * 100 if rate is not None else 0.0
        except: return 0.0
    return 0.0

def fmt_inr(v): return f"₹{abs(v):,.2f}"
def gain_arrow(v): return "▲" if v >= 0 else "▼"
def gain_color(v): return C_GAIN if v >= 0 else C_LOSS

# ══════════════════════════════════════════════════════════════════════════════
#  LIVE NAV ENGINE
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all_schemes_list():
    """Download full AMFI scheme master — returns list of {code, name}"""
    try:
        r = requests.get("https://api.mfapi.in/mf", timeout=15)
        if r.status_code == 200:
            return r.json()   # list of {"schemeCode": int, "schemeName": str}
    except: pass
    return []

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_nav(scheme_code: int):
    """Fetch latest NAV for a given scheme code."""
    try:
        r = requests.get(f"https://api.mfapi.in/mf/{scheme_code}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            nav_data = data.get("data", [])
            if nav_data:
                latest = nav_data[0]
                return {
                    "nav":  float(latest.get("nav", 0)),
                    "date": latest.get("date", ""),
                }
    except: pass
    return None

def fuzzy_match_scheme(cas_name: str, scheme_list: list) -> dict | None:
    """
    Find best matching AMFI scheme for a CAS scheme name.
    Uses simple word-overlap scoring — no extra library needed.
    """
    cas_clean  = clean_name(cas_name).lower()
    cas_words  = set(cas_clean.split())

    best_score = 0
    best_match = None

    for s in scheme_list:
        amfi_name  = s.get("schemeName", "").lower()
        amfi_words = set(amfi_name.split())
        overlap    = len(cas_words & amfi_words)
        total      = len(cas_words | amfi_words)
        score      = overlap / total if total else 0
        if score > best_score:
            best_score = score
            best_match = s

    # Only accept if at least 40% word overlap
    if best_score >= 0.40:
        return best_match
    return None

def fetch_live_navs(holdings: list) -> dict:
    """
    For each holding, find scheme code and fetch live NAV.
    Returns dict: {scheme_name: {"nav": float, "date": str, "code": int}}
    """
    scheme_list = fetch_all_schemes_list()
    if not scheme_list:
        return {}

    result = {}
    for h in holdings:
        sname = h["scheme"]
        match = fuzzy_match_scheme(sname, scheme_list)
        if match:
            code     = match["schemeCode"]
            nav_data = fetch_nav(code)
            if nav_data and nav_data["nav"] > 0:
                result[sname] = {
                    "nav":  nav_data["nav"],
                    "date": nav_data["date"],
                    "code": code,
                    "name": match["schemeName"],
                }
    return result

# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT: EXCEL
# ══════════════════════════════════════════════════════════════════════════════
def generate_excel(d):
    out = io.BytesIO()
    try:
        live_navs = st.session_state.get("live_navs", {})
        with pd.ExcelWriter(out, engine="xlsxwriter") as w:
            # Use live total if available
            total_val = st.session_state.get("live_total_value", d["total_value"])
            pd.DataFrame([
                {"Field":"Name",           "Value":d["investor_name"]},
                {"Field":"Email",          "Value":d["investor_email"]},
                {"Field":"PAN",            "Value":d.get("investor_pan","—")},
                {"Field":"Statement Date", "Value":d["statement_date"]},
                {"Field":"Total Value",    "Value":total_val},
                {"Field":"Total Invested", "Value":d["total_invested"]},
                {"Field":"Unrealized P&L", "Value":total_val - d["total_invested"]},
                {"Field":"Realized P&L",   "Value":d.get("realized_pnl",0.0)},
                {"Field":"NAV Source",     "Value":"Live (MFAPI)" if live_navs else "CAS Statement"},
            ]).to_excel(w, sheet_name="Summary", index=False)

            if d["holdings"]:
                rows = []
                for s in d["holdings"]:
                    ln = live_navs.get(s["scheme"])
                    units = d["agg_map"].get(s["scheme"], {}).get("units", 0)
                    live_val = units * ln["nav"] if ln and units else s["value"]
                    rows.append({
                        "Scheme":        clean_name(s["scheme"]),
                        "Category":      s["category"],
                        "Units":         units,
                        "Invested":      s["invested"],
                        "CAS Value":     s["value"],
                        "Live NAV":      ln["nav"] if ln else "—",
                        "Live Value":    live_val,
                        "P&L":           live_val - s["invested"],
                        "XIRR %":        s["xirr"],
                    })
                pd.DataFrame(rows).to_excel(w, sheet_name="Holdings", index=False)

            if d.get("redeemed"):
                pd.DataFrame(d["redeemed"]).to_excel(w, sheet_name="Redeemed", index=False)

            all_sips = d.get("live_sips",[]) + d.get("dead_sips",[])
            if all_sips:
                pd.DataFrame([{
                    "Scheme":    clean_name(s["scheme"]),
                    "Amount":    s["amount"],
                    "Day":       s["day_label"],
                    "Last Date": s["last_date"],
                    "Status":    s["status"],
                } for s in all_sips]).to_excel(w, sheet_name="SIPs", index=False)
        return out.getvalue()
    except: return None

# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT: HTML
# ══════════════════════════════════════════════════════════════════════════════
def generate_html(d):
    live_navs  = st.session_state.get("live_navs", {})
    rows_h     = ""
    for s in d.get("holdings",[]):
        ln    = live_navs.get(s["scheme"])
        units = d["agg_map"].get(s["scheme"],{}).get("units",0)
        lv    = units * ln["nav"] if ln and units else s["value"]
        pnl   = lv - s["invested"]
        nav_badge = f'<span style="color:#48bb78;font-size:10px;font-family:monospace;">● LIVE ₹{ln["nav"]:,.4f}</span>' if ln else '<span style="color:#718096;font-size:10px;">CAS</span>'
        rows_h += f"""<tr>
          <td>{clean_name(s['scheme'])}<br>{nav_badge}</td><td>{s['category']}</td>
          <td>{fmt_inr(s['invested'])}</td><td>{fmt_inr(lv)}</td>
          <td style="color:{'#48bb78' if pnl>=0 else '#fc8181'};font-weight:600;">{gain_arrow(pnl)} {fmt_inr(pnl)}</td>
          <td style="color:{'#48bb78' if s['xirr']>=0 else '#fc8181'};font-family:monospace;">{s['xirr']:.2f}%</td>
        </tr>"""

    rows_red = ""
    for r in d.get("redeemed",[]):
        p = r["profit"]
        rows_red += f"""<tr><td>{clean_name(r['scheme'])}</td><td>{fmt_inr(r['invested'])}</td>
          <td>{fmt_inr(r['redeemed'])}</td>
          <td style="color:{'#48bb78' if p>=0 else '#fc8181'};font-weight:600;">{gain_arrow(p)} {fmt_inr(p)}</td></tr>"""
    if not rows_red:
        rows_red = "<tr><td colspan='4' style='text-align:center;color:#718096;padding:20px;'>No fully redeemed schemes.</td></tr>"

    rows_sip = ""
    for s in d.get("live_sips",[]) + d.get("dead_sips",[]):
        color = "#48bb78" if s["status"]=="Live" else "#fc8181"
        rows_sip += f"""<tr><td>{clean_name(s['scheme'])}</td>
          <td style="font-family:monospace;">{fmt_inr(s['amount'])}</td>
          <td>{s['day_label']}</td><td>{s['last_date']}</td>
          <td style="color:{color};font-weight:700;">{s['status'].upper()}</td></tr>"""

    total_val = st.session_state.get("live_total_value", d["total_value"])
    pnl_total = total_val - d["total_invested"]
    realized  = d.get("realized_pnl",0.0)
    nav_src   = "Live NAV (MFAPI.in)" if live_navs else "CAS Statement"

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>CAS 360 View — {d['investor_name']}</title>
<style>
  @media print{{body{{background:#07090f!important;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}}}
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
<div class="card">
  <h1>CAS 360 VIEW</h1><div class="sub">Portfolio Intelligence — {nav_src}</div>
  <table style="border:none;background:transparent;"><tbody>
    <tr><td style="background:transparent;color:#718096;font-size:11px;width:120px;">Name</td>
        <td style="background:transparent;color:#f7fafc;font-weight:600;">{d['investor_name'].title()}</td>
        <td style="background:transparent;color:#718096;font-size:11px;width:120px;">Email</td>
        <td style="background:transparent;color:#f7fafc;">{d['investor_email'] or '—'}</td></tr>
    <tr><td style="background:transparent;color:#718096;font-size:11px;">PAN</td>
        <td style="background:transparent;color:#9f7aea;font-family:monospace;font-weight:700;">{d.get('investor_pan','—')}</td>
        <td style="background:transparent;color:#718096;font-size:11px;">Statement Date</td>
        <td style="background:transparent;color:#f7fafc;">{d['statement_date']}</td></tr>
  </tbody></table>
  <div class="grid-4">
    <div class="kpi"><div class="kpi-label">Total Wealth</div><div class="kpi-value">{fmt_inr(total_val)}</div></div>
    <div class="kpi"><div class="kpi-label">Invested</div><div class="kpi-value" style="color:#63b3ed;">{fmt_inr(d['total_invested'])}</div></div>
    <div class="kpi"><div class="kpi-label">Unrealized P&L</div><div class="kpi-value" style="color:{'#48bb78' if pnl_total>=0 else '#fc8181'};">{gain_arrow(pnl_total)} {fmt_inr(pnl_total)}</div></div>
    <div class="kpi"><div class="kpi-label">Realized P&L</div><div class="kpi-value" style="color:{'#48bb78' if realized>=0 else '#fc8181'};">{gain_arrow(realized)} {fmt_inr(realized)}</div></div>
  </div>
</div>
<div class="sec">Active Holdings</div>
<table><thead><tr><th>Scheme</th><th>Category</th><th>Invested</th><th>Live Value</th><th>P&L</th><th>XIRR %</th></tr></thead>
<tbody>{rows_h}</tbody></table>
<div class="sec">SIP Registry</div>
<table><thead><tr><th>Scheme</th><th>Amount</th><th>Day</th><th>Last Date</th><th>Status</th></tr></thead>
<tbody>{rows_sip}</tbody></table>
<div class="sec">Fully Redeemed Positions</div>
<table><thead><tr><th>Scheme</th><th>Invested</th><th>Redeemed</th><th>Realized P&L</th></tr></thead>
<tbody>{rows_red}</tbody></table>
<div class="footer">Generated by CAS 360 View · Confidential · {nav_src}</div>
</body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
#  PDF PARSER
# ══════════════════════════════════════════════════════════════════════════════
def parse_pdf(pdf_bytes, password):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf_bytes); path = f.name
    try:
        raw = casparser.read_cas_pdf(path, password=password)
        return to_dict(raw), None
    except Exception as e:
        err = str(e).lower()
        if any(k in err for k in ["password","decrypt","incorrect"]):
            return None, "wrong_password"
        return None, str(e)
    finally:
        try: os.unlink(path)
        except: pass

# ══════════════════════════════════════════════════════════════════════════════
#  DATA PROCESSOR
# ══════════════════════════════════════════════════════════════════════════════
def process(raw):
    raw  = to_dict(raw)
    info = raw.get("investor_info", {})
    result = dict(
        investor_name=info.get("name","Investor"), investor_email=info.get("email",""),
        investor_pan=info.get("pan","—"), statement_date=str(date.today()),
        total_value=0.0, total_invested=0.0, unrealized_pnl=0.0, realized_pnl=0.0,
        alloc_values={}, alloc_pct={}, holdings=[], live_sips=[], dead_sips=[],
        redeemed=[], recent_redemptions=[], tx_map={}, agg_map={}, duplicate_alerts=[],
    )
    total_val=0.0; total_inv=0.0; type_map={}

    for folio in raw.get("folios",[]):
        for scheme in folio.get("schemes",[]):
            val   = scheme.get("valuation",{})
            sname = scheme.get("scheme","Unknown")
            vdate = str(val.get("date", result["statement_date"]))
            result["statement_date"] = vdate
            cost  = float(val.get("cost",0.0))
            value = float(val.get("value",0.0))
            units = float(scheme.get("close",0.0))
            rtype = str(scheme.get("type","EQUITY")).upper()
            cat   = "Equity Funds" if rtype=="EQUITY" else "Debt Funds"
            txs   = scheme.get("transactions",[])
            result["tx_map"][sname] = txs

            inv_scheme=red_scheme=0.0
            for tx in txs:
                amt   = abs(float(tx.get("amount",0.0)))
                ttype = str(tx.get("type","")).upper()
                tdesc = str(tx.get("description","")).upper()
                if any(k in ttype or k in tdesc for k in ["PURCHASE","REINVEST","SIP","STP-IN"]):
                    inv_scheme += amt
                if any(k in ttype or k in tdesc for k in ["REDEMPTION","PAYOUT","WITHDRAWAL","STP-OUT"]):
                    red_scheme += amt
                    try:
                        rd = to_date(tx.get("date"))
                        result["recent_redemptions"].append({"date_obj":rd,"Date":rd.strftime("%d %b %Y"),"Scheme":clean_name(sname),"Payout":amt})
                    except: pass

            if units < 0.001 and inv_scheme > 0 and red_scheme > 0:
                profit = red_scheme - inv_scheme
                result["redeemed"].append({"scheme":sname,"invested":inv_scheme,"redeemed":red_scheme,"profit":profit})
                result["realized_pnl"] += profit
                result["agg_map"][sname] = {"cost":cost,"units":units,"value":value}
                continue

            total_val += value; total_inv += cost
            type_map[cat] = type_map.get(cat,0.0) + value
            result["agg_map"][sname] = {"cost":cost,"units":units,"value":value}
            result["holdings"].append({"scheme":sname,"invested":cost,"value":value,"pnl":value-cost,"xirr":calc_xirr(txs,value,vdate),"category":cat})

            sip_kw = ["SIP","SYSTEMATIC","RECURRING","AUTO","DEBIT","E-DEBIT","ECS","MANDATE"]
            sip_txs = [t for t in txs if any(k in str(t.get("description","")).upper() or k in str(t.get("type","")).upper() for k in sip_kw)]
            if sip_txs:
                days    = [to_date(t.get("date")).day for t in sip_txs]
                dom     = Counter(days).most_common(1)[0][0] if days else 1
                sorted_sip = sorted(sip_txs, key=lambda x: to_date(x.get("date")))
                latest  = sorted_sip[-1]
                amt_sip = float(latest.get("amount",0.0))
                if amt_sip > 0:
                    last_dt     = to_date(latest.get("date"))
                    cutoff      = to_date(vdate) - datetime.timedelta(days=90)
                    nd          = next_due_date(dom)
                    rec = dict(scheme=sname, amount=amt_sip, day_label=ordinal(dom),
                               last_date=last_dt.strftime("%d %b %Y"),
                               next_date=nd.strftime("%d %b %Y"), next_iso=nd.isoformat(),
                               status="Live" if last_dt>=cutoff and units>0.01 else "Inactive")
                    (result["live_sips"] if rec["status"]=="Live" else result["dead_sips"]).append(rec)

    result.update(total_value=total_val, total_invested=total_inv,
                  unrealized_pnl=total_val-total_inv, alloc_values=type_map,
                  alloc_pct={k:(v/total_val)*100 for k,v in type_map.items()} if total_val>0 else {})
    result["recent_redemptions"] = sorted(result["recent_redemptions"], key=lambda x:x["date_obj"], reverse=True)
    return result

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for key, val in [("profiles",{}),("active",None),("show_email",True),("pin_ok",False),
                 ("switch_target",None),("live_navs",{}),("live_total_value",None),
                 ("nav_fetched_for",None),("nav_fetch_time",None)]:
    if key not in st.session_state: st.session_state[key] = val

def active_data():
    a = st.session_state.active
    return st.session_state.profiles.get(a) if a else None

# ══════════════════════════════════════════════════════════════════════════════
#  UPLOAD SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def show_upload():
    st.markdown("""
    <div style="display:flex;justify-content:center;padding-top:48px;">
      <div style="max-width:520px;width:100%;text-align:center;">
        <div style="width:64px;height:64px;background:rgba(99,179,237,0.08);border:1px solid rgba(99,179,237,0.2);
                    border-radius:18px;display:flex;align-items:center;justify-content:center;
                    margin:0 auto 22px;font-size:28px;">📂</div>
        <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#f7fafc;
                    letter-spacing:-0.5px;margin-bottom:8px;">Upload your CAS PDF</div>
        <div style="font-size:14px;color:#718096;margin-bottom:32px;line-height:1.7;">
          Consolidated Account Statement from CAMS or KFintech.<br>Your data never leaves your device.
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
    col = st.columns([1,2,1])[1]
    with col:
        uploaded = st.file_uploader("CAS PDF", type=["pdf"], label_visibility="collapsed")
        password = st.text_input("PDF Password", type="password", placeholder="PAN / Date of Birth")
        if uploaded and password:
            if st.button("Analyse Portfolio →", use_container_width=True, type="primary"):
                with st.spinner("Parsing…"):
                    data, err = parse_pdf(uploaded.read(), password)
                if err == "wrong_password":
                    st.error("Wrong password. Try your PAN number or date of birth (DDMMYYYY).")
                elif err:
                    st.error(f"Parse error: {err}")
                else:
                    d2 = process(data)
                    name = d2["investor_name"].title()
                    st.session_state.profiles[name] = d2
                    st.session_state.active = name
                    st.session_state.pin_ok = True
                    # clear nav cache for new profile
                    st.session_state.live_navs = {}
                    st.session_state.live_total_value = None
                    st.session_state.nav_fetched_for = None
                    st.success(f"Portfolio loaded — {name}")
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
d = active_data()

with st.sidebar:
    st.markdown("""
    <div style="padding:6px 0 20px;">
      <div style="font-family:'Syne',sans-serif;font-size:21px;font-weight:800;color:#f7fafc;letter-spacing:-0.5px;">
        CAS 360 <span style="color:#63b3ed;">View</span></div>
      <div style="font-size:10px;color:#2d3748;text-transform:uppercase;letter-spacing:2px;font-weight:600;margin-top:2px;">
        Portfolio Intelligence</div>
    </div>""", unsafe_allow_html=True)

    if d:
        menu = st.radio("nav",["Dashboard","My Portfolio","SIP Center","Transactions","Alerts"],label_visibility="collapsed")
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        email_display = d["investor_email"] if st.session_state.show_email else "••••••••••"
        st.markdown(f"""
        <div style="background:rgba(99,179,237,0.04);border:1px solid rgba(99,179,237,0.12);
                    border-radius:10px;padding:12px 14px;margin-bottom:10px;">
          <div style="font-size:13px;font-weight:600;color:#f7fafc;margin-bottom:2px;">{d['investor_name'].title()}</div>
        """, unsafe_allow_html=True)
        ec1, ec2 = st.columns([5,1])
        with ec1: st.markdown(f"<div style='font-size:11px;color:#4a5568;'>{email_display}</div>", unsafe_allow_html=True)
        with ec2:
            if st.button("👁" if st.session_state.show_email else "🙈", key="eye"):
                st.session_state.show_email = not st.session_state.show_email; st.rerun()
        try: dp = to_date(d["statement_date"]).strftime("%d %b %Y")
        except: dp = "—"
        st.markdown(f"<div style='font-size:10px;color:#2d3748;margin-top:6px;'>STATEMENT · {dp}</div></div>", unsafe_allow_html=True)

        if len(st.session_state.profiles) > 1:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            keys = list(st.session_state.profiles.keys())
            idx  = keys.index(st.session_state.active) if st.session_state.active in keys else 0
            sel  = st.selectbox("Switch Profile", keys, index=idx, label_visibility="collapsed")
            if sel != st.session_state.active:
                st.session_state.switch_target = sel; st.session_state.pin_ok = False
            if not st.session_state.pin_ok and st.session_state.switch_target:
                pin = st.text_input("PIN", type="password", max_chars=4, placeholder="••••")
                if pin == "2002":
                    st.session_state.active = st.session_state.switch_target
                    st.session_state.switch_target = None; st.session_state.pin_ok = True
                    st.session_state.live_navs = {}; st.session_state.live_total_value = None
                    st.rerun()
                elif len(pin) == 4: st.error("Wrong PIN")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("＋ Add Another CAS", use_container_width=True):
            st.session_state.active = None; st.session_state.pin_ok = False; st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout & Clear Data", use_container_width=True):
            st.session_state.clear(); st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── LIVE NAV SECTION IN SIDEBAR ──────────────────────────────────────
        st.markdown("<div style='font-size:10px;color:#2d3748;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-bottom:8px;'>Live NAV</div>", unsafe_allow_html=True)

        nav_fetched = bool(st.session_state.live_navs and st.session_state.nav_fetched_for == st.session_state.active)

        if nav_fetched:
            ft = st.session_state.nav_fetch_time
            matched = len(st.session_state.live_navs)
            total_h = len(d["holdings"])
            st.markdown(f"""
            <div style="background:rgba(72,187,120,0.06);border:1px solid rgba(72,187,120,0.2);
                        border-radius:8px;padding:10px 12px;margin-bottom:8px;">
              <div style="font-size:10px;color:#48bb78;font-weight:700;margin-bottom:2px;">● LIVE NAV ACTIVE</div>
              <div style="font-size:11px;color:#718096;">Updated: {ft}</div>
              <div style="font-size:11px;color:#718096;">{matched}/{total_h} schemes matched</div>
            </div>""", unsafe_allow_html=True)
            if st.button("🔄 Refresh NAV", use_container_width=True):
                fetch_nav.clear(); fetch_all_schemes_list.clear()
                st.session_state.live_navs = {}; st.session_state.live_total_value = None
                st.session_state.nav_fetched_for = None; st.rerun()
            if st.button("✕ Back to CAS Values", use_container_width=True):
                st.session_state.live_navs = {}; st.session_state.live_total_value = None
                st.session_state.nav_fetched_for = None; st.rerun()
        else:
            st.markdown("""
            <div style="font-size:12px;color:#718096;margin-bottom:8px;line-height:1.5;">
              Fetch today's NAV from MFAPI.in and recalculate your portfolio value live.
            </div>""", unsafe_allow_html=True)
            if st.button("🚀 Fetch Live NAV", use_container_width=True, type="primary"):
                with st.spinner("Fetching live NAV for all schemes…"):
                    navs = fetch_live_navs(d["holdings"])
                    if navs:
                        st.session_state.live_navs = navs
                        st.session_state.nav_fetched_for = st.session_state.active
                        st.session_state.nav_fetch_time = datetime.datetime.now().strftime("%d %b %Y %I:%M %p")
                        # recalculate total
                        live_total = 0.0
                        for h in d["holdings"]:
                            ln    = navs.get(h["scheme"])
                            units = d["agg_map"].get(h["scheme"],{}).get("units",0)
                            live_total += (units * ln["nav"]) if ln and units else h["value"]
                        st.session_state.live_total_value = live_total
                        st.success(f"Done! {len(navs)}/{len(d['holdings'])} schemes updated.")
                    else:
                        st.error("Could not fetch NAV. Check internet connection.")
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:10px;color:#2d3748;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-bottom:8px;'>Export</div>", unsafe_allow_html=True)
        xls = generate_excel(d)
        if xls:
            st.download_button("📊 Excel", data=xls, file_name=f"CAS360_{d['investor_name']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        st.download_button("📄 HTML Report", data=generate_html(d),
            file_name=f"CAS360_{d['investor_name']}.html", mime="text/html", use_container_width=True)
    else:
        menu = "upload"
        if st.session_state.profiles:
            keys = list(st.session_state.profiles.keys())
            sel  = st.selectbox("Return to", ["— select —"]+keys, label_visibility="collapsed")
            if sel != "— select —":
                st.session_state.active = sel; st.session_state.pin_ok = True; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  GUARD
# ══════════════════════════════════════════════════════════════════════════════
if not d: show_upload(); st.stop()

# helper: get effective value for a holding (live if available, else CAS)
def effective_value(h):
    ln    = st.session_state.live_navs.get(h["scheme"])
    units = d["agg_map"].get(h["scheme"],{}).get("units",0)
    if ln and units: return units * ln["nav"], True
    return h["value"], False

def effective_total():
    return st.session_state.live_total_value if st.session_state.live_total_value else d["total_value"]

# ══════════════════════════════════════════════════════════════════════════════
#  ①  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if menu == "Dashboard":
    fname = d["investor_name"].split()[0].title()
    st.markdown(f'<div class="page-title">Welcome back, {fname} 👋</div>', unsafe_allow_html=True)

    nav_active = bool(st.session_state.live_navs and st.session_state.nav_fetched_for == st.session_state.active)
    try: dp = to_date(d["statement_date"]).strftime("%d %b %Y")
    except: dp = "—"

    if nav_active:
        ft = st.session_state.nav_fetch_time
        st.markdown(f"""
        <div class="live-notice">
          <span style="color:#48bb78;font-size:16px;">●</span>
          <div><span style="color:#48bb78;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">
          Live NAV Active · Updated {ft}</span><br>
          Portfolio values are calculated using today's NAV from MFAPI.in</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="notice">
          <span style="color:#63b3ed;font-size:16px;">◈</span>
          <div><span style="color:#63b3ed;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">
          Statement · {dp}</span><br>
          Showing CAS values. Click <b>🚀 Fetch Live NAV</b> in sidebar for today's prices.</div>
        </div>""", unsafe_allow_html=True)

    tv   = effective_total()
    pnl  = tv - d["total_invested"]
    pnl_pct = (pnl / d["total_invested"] * 100) if d["total_invested"] else 0.0
    sip_mo  = sum(s["amount"] for s in d["live_sips"])

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Wealth",   fmt_inr(tv))
    with m2: st.metric("Invested",       fmt_inr(d["total_invested"]))
    with m3: st.metric("Unrealized P&L", fmt_inr(pnl), delta=f"{'▲' if pnl>=0 else '▼'} {abs(pnl_pct):.2f}% all-time")
    with m4: st.metric("Monthly SIP",    fmt_inr(sip_mo), delta=f"{len(d['live_sips'])} active")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    ch, al = st.columns([3,2])
    with ch:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Wealth Journey</div>', unsafe_allow_html=True)
        pill_cls = "pill-gain" if pnl>=0 else "pill-loss"
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:28px;font-weight:700;
                    color:#f7fafc;letter-spacing:-1px;margin-bottom:8px;">{fmt_inr(tv)}</div>
        <span class="{pill_cls}">{gain_arrow(pnl)} {fmt_inr(pnl)}</span>
        {"&nbsp;<span class='pill-live'>● LIVE NAV</span>" if nav_active else "&nbsp;<span class='pill-cas'>CAS</span>"}
        """, unsafe_allow_html=True)

        tf = st.segmented_control("tf",["1M","6M","1Y","3Y","ALL"],default="1Y",label_visibility="collapsed")
        bv=tv; bi=d["total_invested"]
        slices={
            "1M": (["May 5","May 10","May 15","May 20","May 27"],[bv*.97,bv*.985,bv*.975,bv*.99,bv]),
            "6M": (["Dec","Jan","Feb","Mar","Apr","May"],[bi*.87,bi*.92,bi*.95,bi*.97,bv*.99,bv]),
            "1Y": (["Jun '25","Sep '25","Dec '25","Mar '26","May '26"],[bi*.91,bi*.95,bi*.97,bv*.99,bv]),
            "3Y": (["May '23","Nov '23","May '24","Nov '24","May '25","Nov '25","May '26"],[bi*.35,bi*.55,bi*.70,bi*.83,bi*.93,bv*.98,bv]),
            "ALL":(["Jan '24","Jul '24","Jan '25","Jul '25","Jan '26","May '26"],[bi*.20,bi*.48,bi*.68,bi*.83,bi*.93,bv]),
        }
        xs, ys = slices.get(tf, slices["1Y"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers",
            line=dict(color=C_ACCENT, width=2.5, shape="spline"),
            fill="tozeroy", fillcolor="rgba(99,179,237,0.06)",
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"))
        fig.update_layout(height=220, xaxis=dict(showgrid=False,tickfont=dict(size=11,color="#4a5568")),
            yaxis=dict(showgrid=True,gridcolor=GRID,tickfont=dict(size=11,color="#4a5568")),
            hovermode="x unified", **PLOT_BASE)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

    with al:
        st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Asset Allocation</div>', unsafe_allow_html=True)

        # Recalculate allocation using live values if available
        if nav_active:
            live_type_map = {}
            for h in d["holdings"]:
                lv, _ = effective_value(h)
                live_type_map[h["category"]] = live_type_map.get(h["category"],0.0) + lv
            ap = {k:(v/tv)*100 for k,v in live_type_map.items()} if tv>0 else {}
            av = live_type_map
        else:
            ap = d["alloc_pct"]; av = d["alloc_values"]

        if ap:
            df_pie = pd.DataFrame({"Class":list(ap.keys()),"Pct":list(ap.values())})
            fig_pie = px.pie(df_pie, names="Class", values="Pct", hole=0.7,
                color_discrete_sequence=[C_ACCENT,"#f6ad55",C_GAIN,C_ACCENT2])
            fig_pie.update_traces(textinfo="none", hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>")
            fig_pie.update_layout(height=170, showlegend=False, **PLOT_BASE)
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar":False})

        colors = {"Equity Funds":C_ACCENT,"Debt Funds":"#f6ad55","Gold Funds":C_GAIN,"International":C_ACCENT2}
        for cls, pct in ap.items():
            val = av.get(cls,0.0); col = colors.get(cls,C_ACCENT2)
            st.markdown(f"""
            <div class="alloc-row">
              <div style="display:flex;align-items:center;flex:1;">
                <span class="alloc-dot" style="background:{col};box-shadow:0 0 5px {col}55;"></span>
                <span style="font-size:13px;font-weight:500;color:#e2e8f0;">{cls}</span>
              </div>
              <div style="text-align:right;min-width:110px;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:600;color:#f7fafc;">₹{val:,.0f}</div>
                <div style="font-size:11px;color:#4a5568;">{pct:.1f}%</div>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        with st.container(border=True):
            st.markdown('<div class="card-title">Performance Breakdown</div>', unsafe_allow_html=True)
            ng = sum(1 for h in d["holdings"] if effective_value(h)[0]-h["invested"]>=0)
            nl = sum(1 for h in d["holdings"] if effective_value(h)[0]-h["invested"]<0)
            fig_r = go.Figure(go.Pie(labels=["Profitable","In Loss"],values=[ng,nl],hole=0.65,
                marker_colors=[C_GAIN,C_LOSS],textinfo="none"))
            fig_r.update_layout(height=120, showlegend=True,
                legend=dict(font=dict(size=11,color="#718096"),bgcolor="rgba(0,0,0,0)",
                            orientation="h",x=0.5,xanchor="center",y=-0.2), **PLOT_BASE)
            st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar":False})
            st.markdown('<div class="section-sep">Top Gainers</div>', unsafe_allow_html=True)
            ranked = sorted(d["holdings"], key=lambda h: effective_value(h)[0]-h["invested"], reverse=True)
            top3   = [h for h in ranked if effective_value(h)[0]-h["invested"]>0][:3]
            if top3:
                st.dataframe(pd.DataFrame([{
                    "Scheme": clean_name(s["scheme"]),
                    "P&L":    fmt_inr(effective_value(s)[0]-s["invested"]),
                    "XIRR":   f"{s['xirr']:.1f}%",
                } for s in top3]), use_container_width=True, hide_index=True)

    with r2:
        with st.container(border=True):
            st.markdown('<div class="card-title">⏱ SIP Countdown</div>', unsafe_allow_html=True)
            sorted_sips = sorted(d["live_sips"], key=lambda x: x["next_iso"])
            if sorted_sips:
                ticker_html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px;">'
                for idx, s in enumerate(sorted_sips[:4]):
                    sn=clean_name(s["scheme"]); iso=s["next_iso"]; did=f"sip_{idx}"
                    ticker_html += f"""
                    <div style="background:#111627;border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px;">
                      <div style="font-size:11px;color:#718096;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:4px;" title="{sn}">{sn[:26]}…</div>
                      <div id="{did}" style="font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:700;color:#63b3ed;">—</div>
                    </div>
                    <script>(function(){{
                      var t=new Date("{iso}T00:00:00").getTime();
                      function tick(){{var diff=t-Date.now();var el=document.getElementById("{did}");if(!el)return;
                        if(isNaN(t)||diff<=0){{el.textContent="DUE TODAY";return;}}
                        var d=Math.floor(diff/86400000),h=Math.floor(diff%86400000/3600000),m=Math.floor(diff%3600000/60000);
                        el.textContent=d+"d "+h+"h "+m+"m";}}
                      setInterval(tick,30000);tick();
                    }})();</script>"""
                ticker_html += "</div>"
                st.components.v1.html(ticker_html, height=130, scrolling=False)
                st.dataframe(pd.DataFrame([{
                    "Scheme": clean_name(s["scheme"]),"Amount":fmt_inr(s["amount"]),
                    "Day":s["day_label"],"Next":s["next_date"]} for s in sorted_sips[:4]]),
                    use_container_width=True, hide_index=True)
            else:
                st.info("No live SIPs detected.")

    r3, r4 = st.columns(2)
    with r3:
        with st.container(border=True):
            st.markdown('<div class="card-title">Capital Concentration</div>', unsafe_allow_html=True)
            top5 = sorted(d["holdings"], key=lambda h: effective_value(h)[0], reverse=True)[:5]
            if top5:
                tw2 = effective_total() or 1.0
                df_c = pd.DataFrame([{
                    "Scheme": clean_name(s["scheme"]),
                    "Value":  effective_value(s)[0],
                    "Pct":    effective_value(s)[0]/tw2*100,
                } for s in top5])
                fig_c = px.bar(df_c, x="Value", y="Scheme", orientation="h",
                    color="Pct", color_continuous_scale=["#1a365d",C_ACCENT,"#bee3f8"])
                fig_c.update_layout(height=180, xaxis=dict(visible=False),
                    yaxis=dict(tickfont=dict(size=10,color="#718096"),title=""),
                    coloraxis_showscale=False, **PLOT_BASE)
                st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar":False})

    with r4:
        with st.container(border=True):
            st.markdown('<div class="card-title">Recent Redemptions</div>', unsafe_allow_html=True)
            reds = d.get("recent_redemptions",[])
            if reds:
                df_r = pd.DataFrame([{"Scheme":r["Scheme"],"Payout":r["Payout"]} for r in reds[:4]])
                fig_r2 = px.bar(df_r, x="Payout", y="Scheme", orientation="h", color_discrete_sequence=[C_LOSS])
                fig_r2.update_layout(height=140, xaxis=dict(visible=False),
                    yaxis=dict(tickfont=dict(size=10,color="#718096"),title=""), **PLOT_BASE)
                st.plotly_chart(fig_r2, use_container_width=True, config={"displayModeBar":False})
                st.dataframe(pd.DataFrame([{"Date":r["Date"],"Scheme":r["Scheme"],
                    "Payout":fmt_inr(r["Payout"])} for r in reds[:4]]),
                    use_container_width=True, hide_index=True)
            else:
                st.info("No recent redemptions found.")

# ══════════════════════════════════════════════════════════════════════════════
#  ②  MY PORTFOLIO
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "My Portfolio":
    st.markdown('<div class="page-title">Portfolio Ledger</div>', unsafe_allow_html=True)
    nav_active = bool(st.session_state.live_navs and st.session_state.nav_fetched_for==st.session_state.active)

    if nav_active:
        ft = st.session_state.nav_fetch_time
        st.markdown(f"""<div class="live-notice">
          <span style="color:#48bb78;font-size:16px;">●</span>
          <div><span style="color:#48bb78;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">
          Live NAV Active · {ft}</span><br>Values recalculated using today's NAV.</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="page-sub">Open holdings and fully redeemed positions · CAS values</div>', unsafe_allow_html=True)

    for label, cat, color in [("Equity Funds","Equity Funds",C_ACCENT),("Debt Funds","Debt Funds","#f6ad55")]:
        group = [s for s in d["holdings"] if s["category"]==cat]
        if not group: continue
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin:22px 0 10px;">
          <div style="width:7px;height:7px;border-radius:50%;background:{color};box-shadow:0 0 5px {color};"></div>
          <span style="font-size:11px;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:2px;">{label}</span>
          <div style="flex:1;height:1px;background:rgba(255,255,255,0.05);"></div>
        </div>""", unsafe_allow_html=True)

        rows = []
        for s in sorted(group, key=lambda x: effective_value(x)[0], reverse=True):
            lv, is_live = effective_value(s)
            pnl = lv - s["invested"]
            ln  = st.session_state.live_navs.get(s["scheme"])
            nav_str = f"₹{ln['nav']:,.4f} ({ln['date']})" if ln else "CAS"
            rows.append({
                "Scheme":        clean_name(s["scheme"]),
                "Invested":      fmt_inr(s["invested"]),
                "Value":         fmt_inr(lv),
                "P&L":           f"{'▲' if pnl>=0 else '▼'} {fmt_inr(pnl)}",
                "XIRR %":        f"{s['xirr']:.2f}%",
                "NAV Source":    nav_str,
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-sep">Bubble Map — Invested vs XIRR</div>', unsafe_allow_html=True)
    df_b = pd.DataFrame([{
        "Scheme":   clean_name(s["scheme"]),
        "Invested": s["invested"],
        "XIRR":     s["xirr"],
        "Gain":     max(effective_value(s)[0]-s["invested"],0),
        "Type":     s["category"],
    } for s in d["holdings"] if s["invested"]>0])
    if not df_b.empty:
        fig_b = px.scatter(df_b, x="Invested", y="XIRR", size="Gain", color="Type",
            hover_name="Scheme", color_discrete_map={"Equity Funds":C_ACCENT,"Debt Funds":"#f6ad55"})
        fig_b.update_layout(height=340,
            xaxis=dict(showgrid=True,gridcolor=GRID,title="Invested (₹)",tickfont=dict(size=11,color="#718096")),
            yaxis=dict(showgrid=True,gridcolor=GRID,title="XIRR %",tickfont=dict(size=11,color="#718096")),
            legend=dict(font=dict(size=11,color="#718096"),bgcolor="rgba(0,0,0,0)"), **PLOT_BASE)
        st.plotly_chart(fig_b, use_container_width=True, config={"displayModeBar":False})

    st.markdown('<div class="section-sep" style="margin-top:36px;">Fully Redeemed Positions</div>', unsafe_allow_html=True)
    if d.get("redeemed"):
        rp=d["realized_pnl"]; rc=gain_color(rp)
        st.markdown(f"""
        <div style="background:rgba({'72,187,120' if rp>=0 else '252,129,129'},0.05);
                    border:1px solid rgba({'72,187,120' if rp>=0 else '252,129,129'},0.2);
                    border-radius:10px;padding:14px 18px;margin-bottom:14px;">
          <div style="font-size:10px;color:{rc};text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:4px;">Total Realized P&L</div>
          <div style="font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:700;color:{rc};">{gain_arrow(rp)} {fmt_inr(rp)}</div>
        </div>""", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([{
            "Scheme":   clean_name(r["scheme"]),
            "Invested": fmt_inr(r["invested"]),
            "Redeemed": fmt_inr(r["redeemed"]),
            "P&L":      f"{'▲' if r['profit']>=0 else '▼'} {fmt_inr(r['profit'])}",
        } for r in d["redeemed"]]), use_container_width=True, hide_index=True)
    else:
        st.info("No fully redeemed positions found.")

# ══════════════════════════════════════════════════════════════════════════════
#  ③  SIP CENTER
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "SIP Center":
    st.markdown('<div class="page-title">SIP Center</div>', unsafe_allow_html=True)
    live_s=d.get("live_sips",[]); dead_s=d.get("dead_sips",[])
    tab = st.segmented_control("sip_tab",[f"🟢 Live ({len(live_s)})",f"🔴 Inactive ({len(dead_s)})"],
        default=f"🟢 Live ({len(live_s)})",label_visibility="collapsed")
    target = live_s if "Live" in tab else dead_s
    total_out = sum(s["amount"] for s in target)
    status_lbl = "LIVE" if "Live" in tab else "INACTIVE"
    st.markdown(f"""
    <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;
                padding:20px 24px;display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <div>
        <div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;">Total Monthly Outflow</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:30px;font-weight:700;color:#f7fafc;letter-spacing:-1px;">{fmt_inr(total_out)}</div>
      </div>
      <div style="font-size:12px;font-weight:700;color:{'#48bb78' if 'Live' in tab else '#fc8181'};">{len(target)} {status_lbl}</div>
    </div>""", unsafe_allow_html=True)
    if target:
        st.dataframe(pd.DataFrame([{
            "Scheme":    clean_name(s["scheme"]),
            "Amount":    fmt_inr(s["amount"]),
            "Day":       s["day_label"],
            "Last Date": s["last_date"],
            "Next Due":  s["next_date"],
            "Status":    s["status"],
        } for s in target]), use_container_width=True, hide_index=True)
    else: st.info("No SIPs in this category.")
    all_sips = live_s+dead_s
    if all_sips:
        st.markdown('<div class="section-sep">Monthly Outflow by Scheme</div>', unsafe_allow_html=True)
        df_bar = pd.DataFrame([{"Scheme":clean_name(s["scheme"]),"Amount":s["amount"]} for s in all_sips])
        fig_bar = px.bar(df_bar, x="Amount", y="Scheme", orientation="h", color="Amount",
            color_continuous_scale=["#1a365d",C_ACCENT,"#bee3f8"])
        fig_bar.update_layout(height=max(200,len(all_sips)*30), xaxis=dict(visible=False),
            yaxis=dict(tickfont=dict(size=11,color="#718096"),title=""), coloraxis_showscale=False, **PLOT_BASE)
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})

# ══════════════════════════════════════════════════════════════════════════════
#  ④  TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "Transactions":
    st.markdown('<div class="page-title">Transaction Ledger</div>', unsafe_allow_html=True)
    tx=d.get("tx_map",{}); ag=d.get("agg_map",{})
    if not tx:
        st.warning("No transaction data found.")
    else:
        sel  = st.selectbox("Select Scheme", list(tx.keys()), label_visibility="visible")
        tots = ag.get(sel,{"cost":0.0,"units":0.0,"value":0.0})
        ln   = st.session_state.live_navs.get(sel)
        live_val = tots["units"] * ln["nav"] if ln and tots["units"] else tots["value"]
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Book Cost",     fmt_inr(tots["cost"]))
        with c2: st.metric("Units",         f"{tots['units']:.3f}")
        with c3: st.metric("CAS Value",     fmt_inr(tots["value"]))
        with c4: st.metric("Live Value" if ln else "Current Value", fmt_inr(live_val),
                            delta=f"NAV ₹{ln['nav']:,.4f} · {ln['date']}" if ln else None)

        rows_tx = []
        for e in tx.get(sel,[]):
            rows_tx.append({
                "Date":        to_date(e.get("date")).strftime("%d %b %Y") if e.get("date") else "—",
                "Description": e.get("description","—"),
                "Amount":      fmt_inr(float(e["amount"])) if e.get("amount") else "—",
                "NAV":         f"₹{float(e['nav']):,.4f}" if e.get("nav") else "—",
                "Units":       f"{float(e['units']):,.3f}" if e.get("units") else "—",
                "Type":        e.get("type","—"),
            })
        st.dataframe(pd.DataFrame(rows_tx), use_container_width=True, hide_index=True)

        st.markdown('<div class="section-sep" style="margin-top:28px;">All Holdings — XIRR Table</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([{
            "Scheme":      clean_name(s["scheme"]),
            "Invested":    fmt_inr(s["invested"]),
            "Live Value":  fmt_inr(effective_value(s)[0]),
            "P&L":         f"{'▲' if effective_value(s)[0]-s['invested']>=0 else '▼'} {fmt_inr(effective_value(s)[0]-s['invested'])}",
            "XIRR %":      f"{s['xirr']:.2f}%",
            "Category":    s["category"],
        } for s in d["holdings"]]), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ⑤  ALERTS
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "Alerts":
    st.markdown('<div class="page-title">Alerts & Insights</div>', unsafe_allow_html=True)
    alerts = []
    for a in d.get("duplicate_alerts",[]):
        alerts.append(("warn","Duplicate SIP Detected",f"{clean_name(a['scheme'])} — {a['count']}× entries on {a['dates']}"))
    for s in d.get("dead_sips",[]):
        alerts.append(("danger","Inactive SIP",f"{clean_name(s['scheme'])} — last processed {s['last_date']}"))
    for s in d["holdings"]:
        lv, _ = effective_value(s)
        if lv - s["invested"] < 0:
            alerts.append(("info","Unrealized Loss",f"{clean_name(s['scheme'])} — down {fmt_inr(lv-s['invested'])} from cost"))

    if not alerts:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;">
          <div style="font-size:48px;margin-bottom:12px;">◎</div>
          <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#f7fafc;margin-bottom:6px;">All Clear</div>
          <div style="font-size:13px;color:#718096;">No alerts detected in your portfolio.</div>
        </div>""", unsafe_allow_html=True)
    else:
        colors={"warn":"#f6ad55","danger":"#fc8181","info":"#63b3ed"}
        labels={"warn":"WARNING","danger":"ACTION REQUIRED","info":"INFO"}
        for lvl,title,detail in alerts:
            c=colors.get(lvl,C_ACCENT); l=labels.get(lvl,"INFO")
            st.markdown(f"""
            <div class="alert-card" style="border-color:{c};">
              <div style="font-size:9px;font-weight:700;color:{c};text-transform:uppercase;letter-spacing:1.5px;font-family:'IBM Plex Mono',monospace;margin-bottom:4px;">{l}</div>
              <div style="font-size:14px;font-weight:600;color:#f7fafc;margin-bottom:3px;">{title}</div>
              <div style="font-size:13px;color:#718096;">{detail}</div>
            </div>""", unsafe_allow_html=True)