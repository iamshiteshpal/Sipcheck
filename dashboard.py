import streamlit as st
import streamlit.components.v1 as components
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
        page_title="CAS 360 View — Portfolio Intelligence",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_global_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Instrument+Sans:wght@400;500;600&display=swap');
        :root {
          --bg:        #07090f;
          --bg2:       #0c0f1a;
          --bg3:       #111627;
          --border:    rgba(255,255,255,0.06);
          --border-hi: rgba(99,179,237,0.35);
          --accent:    #63b3ed;
          --accent2:   #9f7aea;
          --gain:      #48bb78;
          --loss:      #fc8181;
          --warn:      #f6ad55;
          --text:      #e2e8f0;
          --muted:     #718096;
          --faint:     #2d3748;
        }
        *, *::before, *::after { box-sizing: border-box; }
        html, body, .stApp {
          background: var(--bg) !important;
          color: var(--text) !important;
          font-family: 'Instrument Sans', sans-serif !important;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
          background: var(--bg2) !important;
          border-right: 1px solid rgba(99,179,237,0.12) !important;
        }
        [data-testid="stSidebar"] * { font-family: 'Instrument Sans', sans-serif !important; }
        [data-testid="stSidebar"] label { color: var(--muted) !important; font-size: 12px !important; }

        /* ── All Buttons ── */
        [data-testid="stButton"] button {
          background: var(--bg3) !important;
          color: var(--text) !important;
          border: 1px solid rgba(99,179,237,0.20) !important;
          border-radius: 8px !important;
          font-weight: 500 !important;
          font-size: 13px !important;
          transition: border-color .2s, background .2s, transform .15s !important;
        }
        [data-testid="stButton"] button:hover {
          background: var(--bg2) !important;
          border-color: rgba(99,179,237,0.55) !important;
          transform: translateY(-1px) !important;
          box-shadow: 0 4px 16px rgba(99,179,237,0.12) !important;
        }
        [data-testid="stButton"] button:active { transform: translateY(0) !important; }
        /* Danger/logout button — reddish tint */
        [data-testid="stSidebar"] [data-testid="stButton"]:last-of-type button {
          border-color: rgba(252,129,129,0.22) !important;
          color: #fc8181 !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"]:last-of-type button:hover {
          background: rgba(252,129,129,0.06) !important;
          border-color: rgba(252,129,129,0.50) !important;
        }

        /* ── Metrics ── */
        div[data-testid="stMetric"] {
          background: var(--bg2) !important;
          border: 1px solid rgba(99,179,237,0.14) !important;
          border-radius: 14px !important;
          padding: 18px 20px !important;
          transition: border-color .25s, transform .2s, box-shadow .2s;
        }
        div[data-testid="stMetric"]:hover {
          border-color: rgba(99,179,237,0.38) !important;
          transform: translateY(-2px);
          box-shadow: 0 6px 24px rgba(99,179,237,0.08) !important;
        }
        div[data-testid="stMetricValue"] > div {
          font-family: 'IBM Plex Mono', monospace !important;
          font-size: 20px !important;
          font-weight: 700 !important;
          color: #f0f6ff !important;
        }
        div[data-testid="stMetricLabel"] > div {
          font-size: 9px !important;
          color: var(--muted) !important;
          text-transform: uppercase;
          letter-spacing: 1.6px;
          font-weight: 600 !important;
        }
        div[data-testid="stMetricDelta"] > div { font-size: 11px !important; font-weight: 600 !important; }

        /* ── Vertical block borders ── */
        [data-testid="stVerticalBlockBorderWrapper"] > div > div {
          background: var(--bg2) !important;
          border: 1px solid rgba(99,179,237,0.10) !important;
          border-radius: 14px !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] > div > div:hover {
          border-color: rgba(99,179,237,0.22) !important;
        }

        /* ── DataFrame / Table ── */
        [data-testid="stDataFrame"] {
          border-radius: 12px !important;
          overflow: hidden !important;
          border: 1px solid rgba(99,179,237,0.16) !important;
          background: var(--bg2) !important;
        }
        [data-testid="stDataFrame"] > div { background: var(--bg2) !important; }

        /* ── Selectbox / Text Input ── */
        [data-testid="stSelectbox"] > div > div {
          background: var(--bg3) !important;
          border: 1px solid rgba(99,179,237,0.18) !important;
          border-radius: 8px !important;
          color: var(--text) !important;
        }
        [data-testid="stSelectbox"] > div > div:focus-within {
          border-color: var(--accent) !important;
          box-shadow: 0 0 0 2px rgba(99,179,237,0.15) !important;
        }
        [data-testid="stTextInput"] input {
          background: var(--bg3) !important;
          border: 1px solid rgba(99,179,237,0.18) !important;
          border-radius: 8px !important;
          color: var(--text) !important;
          font-family: 'IBM Plex Mono', monospace !important;
        }
        [data-testid="stTextInput"] input:focus {
          border-color: var(--accent) !important;
          box-shadow: 0 0 0 2px rgba(99,179,237,0.15) !important;
        }

        /* ── File Uploader ── */
        [data-testid="stFileUploader"] {
          background: rgba(99,179,237,0.03) !important;
          border: 2px dashed rgba(99,179,237,0.25) !important;
          border-radius: 14px !important;
        }
        [data-testid="stFileUploader"]:hover {
          border-color: rgba(99,179,237,0.55) !important;
          background: rgba(99,179,237,0.06) !important;
        }
        [data-testid="stFileUploaderDropzone"] {
          background: transparent !important;
        }
        [data-testid="stFileUploaderDropzoneInstructions"] {
          color: var(--muted) !important;
        }

        /* ── Segmented Control ── */
        [data-testid="stSegmentedControl"] > div {
          background: var(--bg3) !important;
          border: 1px solid rgba(99,179,237,0.14) !important;
          border-radius: 10px !important;
          padding: 3px !important;
        }
        [data-testid="stSegmentedControl"] button {
          color: var(--muted) !important;
          border-radius: 7px !important;
          font-weight: 500 !important;
        }
        [data-testid="stSegmentedControl"] button[aria-checked="true"] {
          background: linear-gradient(135deg,#1a4a7a,#3b2d6e) !important;
          color: #e2e8f0 !important;
          border-radius: 7px !important;
          box-shadow: 0 2px 10px rgba(99,179,237,0.18) !important;
          font-weight: 600 !important;
        }

        /* ── Radio (nav) ── */
        [data-testid="stRadio"] label {
          color: var(--muted) !important;
          font-size: 13px !important;
          font-weight: 500 !important;
          padding: 6px 0 !important;
          transition: color .15s;
        }
        [data-testid="stRadio"] label:hover { color: var(--text) !important; }
        [data-testid="stRadio"] [aria-checked="true"] ~ span { color: var(--accent) !important; font-weight: 600 !important; }

        /* ── Scrollbar ── */
        hr { border-color: rgba(99,179,237,0.10) !important; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: rgba(99,179,237,0.20); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(99,179,237,0.40); }

        /* ── Force dark on inline white/light backgrounds ── */
        [style*="background:#ffffff"],[style*="background: #ffffff"],
        [style*="background:#fff;"],[style*="background: #fff;"],
        [style*="background:#fff "],[style*="background: #fff "] {
          background: var(--bg2) !important; color: var(--text) !important;
        }
        [style*="background:#f8fafc"],[style*="background: #f8fafc"],
        [style*="background:#f1f5f9"],[style*="background: #f1f5f9"],
        [style*="background:#f0f4f8"],[style*="background: #f0f4f8"] {
          background: var(--bg3) !important; color: var(--text) !important;
        }
        [style*="color:#0f172a"],[style*="color: #0f172a"],
        [style*="color:#1e293b"],[style*="color: #1e293b"],
        [style*="color:#334155"],[style*="color: #334155"],
        [style*="color:#2d3748"],[style*="color: #2d3748"] { color: var(--text) !important; }

        /* ── Component classes ── */
        .card {
          background: var(--bg2);
          border: 1px solid rgba(99,179,237,0.12);
          border-radius: 16px;
          padding: 22px 24px;
          margin-bottom: 16px;
          position: relative;
          transition: border-color .2s, box-shadow .2s;
        }
        .card:hover { border-color: rgba(99,179,237,0.28); box-shadow: 0 4px 24px rgba(99,179,237,0.06); }
        .card-title { font-family: 'Syne', sans-serif; font-size: 10px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 2.5px; margin-bottom: 14px; }
        .pill-gain { display: inline-flex; align-items: center; gap: 4px; background: rgba(72,187,120,0.1); border: 1px solid rgba(72,187,120,0.28); color: var(--gain); font-family: 'IBM Plex Mono',monospace; font-size: 11px; font-weight: 600; padding: 3px 11px; border-radius: 20px; }
        .pill-loss { display: inline-flex; align-items: center; gap: 4px; background: rgba(252,129,129,0.1); border: 1px solid rgba(252,129,129,0.28); color: var(--loss); font-family: 'IBM Plex Mono',monospace; font-size: 11px; font-weight: 600; padding: 3px 11px; border-radius: 20px; }
        .notice { background: rgba(99,179,237,0.05); border: 1px solid rgba(99,179,237,0.18); border-left: 3px solid var(--accent); border-radius: 0 10px 10px 0; padding: 12px 16px; font-size: 13px; color: var(--muted); margin-bottom: 22px; display: flex; align-items: flex-start; gap: 10px; }
        .section-sep { font-size: 10px; font-weight: 700; color: rgba(99,179,237,0.45); text-transform: uppercase; letter-spacing: 2px; margin: 24px 0 12px; display: flex; align-items: center; gap: 10px; }
        .section-sep::after { content:''; flex:1; height:1px; background: rgba(99,179,237,0.10); }
        .page-title { font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800; color: #f0f6ff; letter-spacing: -0.5px; margin-bottom: 4px; }
        .page-sub { font-size: 13px; color: var(--muted); margin-bottom: 22px; }
        .sip-card { background: var(--bg3); border: 1px solid rgba(99,179,237,0.10); border-radius: 10px; padding: 12px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
        .alloc-row { display: flex; align-items: center; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
        .alloc-dot { width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:8px; }
        .alert-card { border-left: 3px solid; border-radius: 0 10px 10px 0; padding: 12px 16px; margin-bottom: 10px; background: var(--bg2); border-top: 1px solid rgba(255,255,255,0.04); border-right: 1px solid rgba(255,255,255,0.04); border-bottom: 1px solid rgba(255,255,255,0.04); }
        div[data-testid="stAppViewBlockContainer"] { padding-top: 2.5rem !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
    return name.strip()


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
<title>CAS 360 View — {d['investor_name']}</title>
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
  <h1>CAS 360 VIEW</h1>
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
<div class=\"footer\">Generated by CAS 360 View · Confidential</div>
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

    # Merge small orphan groups with same amount into the largest group
    if len(mandate_groups) > 1:
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
    st.markdown(
        """
        <div style="display:flex;justify-content:center;padding-top:48px;">
          <div style="max-width:520px;width:100%;text-align:center;">
            <div style="width:64px;height:64px;background:rgba(99,179,237,0.08);border:1px solid rgba(99,179,237,0.2);
                        border-radius:18px;display:flex;align-items:center;justify-content:center;
    margin:0 auto 22px;font-size:28px;">📂</div>
            <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#f7fafc;
    letter-spacing:-0.5px;margin-bottom:8px;">Upload your CAS PDF</div>
            <div style="font-size:14px;color:#718096;margin-bottom:32px;line-height:1.7;">
              Consolidated Account Statement from CAMS or KFintech.<br>
              Your data never leaves your device.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
"text-transform:uppercase;letter-spacing:2.5px;'>What is CAS 360 View</span>"
"<div style='flex:1;height:1px;background:rgba(99,179,237,0.10);'></div>"
"</div>"

"<div style='text-align:center;margin-bottom:44px;'>"
"<div style='font-family:Syne,sans-serif;font-size:22px;font-weight:800;"
"color:#f0f6ff;letter-spacing:-0.3px;margin-bottom:12px;'>"
"Your mutual fund portfolio, finally in one clear view.</div>"
"<div style='font-size:14px;color:#718096;line-height:1.85;max-width:620px;margin:0 auto;'>"
"CAS 360 View reads your Consolidated Account Statement (CAS) PDF issued by "
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
"CAS 360 View · Built for Indian mutual fund investors · "
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
        st.markdown(
            """
            <div style="padding:6px 0 20px;">
              <div style="font-family:'Syne',sans-serif;font-size:21px;font-weight:800;
    color:#f7fafc;letter-spacing:-0.5px;">CAS 360 <span style="color:#63b3ed;">View</span></div>
              <div style="font-size:10px;color:#2d3748;text-transform:uppercase;letter-spacing:2px;
    font-weight:600;margin-top:2px;">Portfolio Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if data:
            menu = st.radio(
                "nav",
                ["Dashboard", "My Portfolio", "SIP Center", "Transactions", "Alerts"],
                label_visibility="collapsed",
            )
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

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
                    file_name=f"CAS360_{data['investor_name']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            st.download_button(
                "📄 HTML Report (Print as PDF)",
                data=generate_html(data, live_data),
                file_name=f"CAS360_{data['investor_name']}.html",
                mime="text/html",
                use_container_width=True,
            )
        else:
            menu = "upload"
            if st.session_state.profiles:
                keys = list(st.session_state.profiles.keys())
                selected = st.selectbox("Return to", ["— select —"] + keys, label_visibility="collapsed")
                if selected != "— select —":
                    st.session_state.active = selected
                    st.session_state.pin_ok = True
                    st.rerun()
    return menu


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

def render_dashboard(data):
    first_name = data["investor_name"].split()[0].title()
    st.markdown(f'<div class="page-title">Welcome back, {first_name} 👋</div>', unsafe_allow_html=True)
    try:
        statement_date = to_date(data["statement_date"]).strftime("%d %b %Y")
    except Exception:
        statement_date = "—"

    nc1, nc2 = st.columns([3, 1])
    with nc1:
        st.markdown(
            f"""
            <div class="notice" style="margin-bottom:8px;">
              <span style="color:#63b3ed;font-size:16px;">◈</span>
              <div>
                <span style="color:#63b3ed;font-size:11px;font-weight:700;text-transform:uppercase;
        letter-spacing:1px;">CAS Statement · {statement_date}</span><br>
                Base figures computed from your uploaded PDF.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with nc2:
        if st.button("🔄 Refresh Latest NAV", use_container_width=True):
            with st.spinner("Fetching latest NAVs from AMFI..."):
                live_data, live_date = fetch_live_navs(data["holdings"])
                st.session_state.live_data = live_data
                st.session_state.live_last_updated = live_date
            st.rerun()

    display_wealth = data["total_value"]
    if st.session_state.live_data:
        st.markdown(
            f"""
            <div style="background:rgba(72,187,120,0.1);border:1px solid rgba(72,187,120,0.25);
                        border-radius:10px;padding:8px 16px;margin-bottom:20px;display:inline-flex;
                        align-items:center;gap:8px;color:#48bb78;font-size:12px;font-weight:700;">
                <span style="display:inline-block;width:8px;height:8px;background:#48bb78;border-radius:50%;box-shadow:0 0 6px #48bb78;"></span>
                LIVE DATA ACTIVE · Latest NAVs as of {st.session_state.live_last_updated}
            </div>
            """,
            unsafe_allow_html=True,
        )
        new_wealth = 0
        for holding in data["holdings"]:
            scheme_name = holding["scheme"]
            if scheme_name in st.session_state.live_data:
                new_wealth += st.session_state.live_data[scheme_name]["live_value"]
            else:
                new_wealth += holding["value"]
        display_wealth = new_wealth

    display_pnl = display_wealth - data["total_invested"]
    pnl_pct = (display_pnl / data["total_invested"] * 100) if data["total_invested"] else 0.0
    sip_monthly = sum(s["amount"] for s in data["live_sips"])

    # ── FIX: use fmt_inr_short so values never truncate in metric tiles ──
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Wealth", fmt_inr(display_wealth))
    with m2:
        st.metric("Invested", fmt_inr(data["total_invested"]))
    with m3:
        st.metric(
            "Unrealized P&L",
            fmt_inr(display_pnl),
            delta=f"{gain_arrow(display_pnl)} {abs(pnl_pct):.2f}% all-time",
        )
    with m4:
        st.metric(
            "Monthly SIP",
            fmt_inr(sip_monthly),
            delta=f"{len(data['live_sips'])} active",
        )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    ch, al = st.columns([3, 2])
    with ch:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Wealth Journey</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="font-family:'IBM Plex Mono',monospace;font-size:28px;font-weight:700;
    color:#f7fafc;letter-spacing:-1px;margin-bottom:8px;">{fmt_inr(display_wealth)}</div>
            <span class=\"{'pill-gain' if display_pnl>=0 else 'pill-loss'}\">{gain_arrow(display_pnl)} {fmt_inr(display_pnl)}</span>
            """,
            unsafe_allow_html=True,
        )

        top_n = sorted(data["holdings"], key=lambda x: x["value"], reverse=True)[:8]
        df_wj = pd.DataFrame([
            {
                "Scheme": clean_name(h["scheme"])[:28],
                "Invested": h["invested"],
                "Current Value": h["value"],
            }
            for h in top_n
        ])
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Invested", x=df_wj["Scheme"], y=df_wj["Invested"],
            marker_color="rgba(99,179,237,0.45)", hovertemplate="<b>%{x}</b><br>Invested: ₹%{y:,.0f}<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            name="Current Value", x=df_wj["Scheme"], y=df_wj["Current Value"],
            marker_color=C_ACCENT, hovertemplate="<b>%{x}</b><br>Value: ₹%{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            height=220, barmode="group",
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#4a5568"), tickangle=-20),
            yaxis=dict(showgrid=True, gridcolor=GRID, tickfont=dict(size=10, color="#4a5568")),
            legend=dict(font=dict(size=10, color="#718096"), bgcolor="rgba(0,0,0,0)", orientation="h", x=1, xanchor="right", y=1.15),
            hovermode="x unified",
            **PLOT_BASE,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with al:
        st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Asset Allocation</div>', unsafe_allow_html=True)
        allocation_pct = data["alloc_pct"]
        allocation_values = data["alloc_values"]
        if allocation_pct:
            df_pie = pd.DataFrame({"Class": list(allocation_pct.keys()), "Pct": list(allocation_pct.values())})
            fig_pie = px.pie(
                df_pie,
                names="Class",
                values="Pct",
                hole=0.7,
                color_discrete_sequence=[C_ACCENT, "#f6ad55", C_GAIN, C_ACCENT2],
            )
            fig_pie.update_traces(textinfo="none", hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>")
            fig_pie.update_layout(height=170, showlegend=False, **PLOT_BASE)
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

        colors = {"Equity Funds": C_ACCENT, "Debt Funds": "#f6ad55", "Gold Funds": C_GAIN, "International": C_ACCENT2}
        for asset_class, pct in allocation_pct.items():
            value = allocation_values.get(asset_class, 0.0)
            color = colors.get(asset_class, C_ACCENT2)
            st.markdown(
                f"""
                <div class="alloc-row">
                  <div style="display:flex;align-items:center;flex:1;">
                    <span class="alloc-dot" style="background:{color};box-shadow:0 0 5px {color}55;"></span>
                    <span style="font-size:13px;font-weight:500;color:#e2e8f0;">{asset_class}</span>
                  </div>
                  <div style="text-align:right;min-width:110px;">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:600;color:#f7fafc;">₹{value:,.0f}</div>
                    <div style="font-size:11px;color:#4a5568;">{pct:.1f}%</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="card-title">Performance Breakdown</div>', unsafe_allow_html=True)
        profitable = sum(1 for item in data["holdings"] if item["pnl"] >= 0)
        losing = sum(1 for item in data["holdings"] if item["pnl"] < 0)
        fig_perf = go.Figure(go.Pie(
            labels=["Profitable", "In Loss"],
            values=[profitable, losing],
            hole=0.65,
            marker_colors=[C_GAIN, C_LOSS],
            textinfo="none",
        ))
        fig_perf.update_layout(
            height=120,
            showlegend=True,
            legend=dict(font=dict(size=11, color="#718096"), bgcolor="rgba(0,0,0,0)", orientation="h", x=0.5, xanchor="center", y=-0.2),
            **PLOT_BASE,
        )
        st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="section-sep">Top Gainers</div>', unsafe_allow_html=True)
        top_gainers = sorted([item for item in data["holdings"] if item["pnl"] > 0], key=lambda x: x["pnl"], reverse=True)[:3]
        if top_gainers:
            st.dataframe(
                pd.DataFrame([
                    {
                        "Scheme": clean_name(item["scheme"]),
                        "P&L": fmt_inr(item["pnl"]),
                        "XIRR": f"{item['xirr']:.1f}%",
                    }
                    for item in top_gainers
                ]),
                use_container_width=True,
                hide_index=True,
            )

    with r2:
        st.markdown('<div class="card-title">⏱ SIP Countdown</div>', unsafe_allow_html=True)
        sorted_sips = sorted(data["live_sips"], key=lambda x: x["next_iso"])
        if sorted_sips:
            ticker_html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px;">'
            for idx, sip in enumerate(sorted_sips[:4]):
                scheme_name = clean_name(sip["scheme"])
                target_iso = sip["next_iso"]
                dom_id = f"sip_{idx}"
                ticker_html += f"""
                    <div style="background:#111627;border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px;">
                      <div style="font-size:11px;color:#718096;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:4px;" title=\"{scheme_name}\">{scheme_name[:26]}…</div>
                      <div id=\"{dom_id}\" style="font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:700;color:#63b3ed;">—</div>
                    </div>
                    <script>
                    (function(){{
                      var target = new Date("{target_iso}T00:00:00").getTime();
                      function tick(){{
                        var diff = target - Date.now();
                        var el = document.getElementById("{dom_id}");
                        if(!el) return;
                        if(isNaN(target) || diff <= 0){{ el.textContent = "DUE TODAY"; return; }}
                        var d = Math.floor(diff/86400000);
                        var h = Math.floor(diff%86400000/3600000);
                        var m = Math.floor(diff%3600000/60000);
                        el.textContent = d + "d " + h + "h " + m + "m";
                      }}
                      setInterval(tick, 30000);
                      tick();
                    }})();
                    </script>
                """
            ticker_html += "</div>"
            components.html(ticker_html, height=130, scrolling=False)

            sip_rows = [
                {
                    "Scheme": clean_name(sip["scheme"]),
                    "Amount": fmt_inr(sip["amount"]),
                    "Day": sip["day_label"],
                    "Next": sip["next_date"],
                }
                for sip in sorted_sips[:4]
            ]
            st.dataframe(pd.DataFrame(sip_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No live SIPs detected.")

    r3, r4 = st.columns(2)
    with r3:
        st.markdown('<div class="card-title">Capital Concentration</div>', unsafe_allow_html=True)
        top_holdings = sorted(data["holdings"], key=lambda x: x["value"], reverse=True)[:5]
        if top_holdings:
            total_value_for_bubble = display_wealth or 1.0
            df_concentration = pd.DataFrame([
                {
                    "Scheme": clean_name(item["scheme"]),
                    "Value": item["value"],
                    "Pct": item["value"] / total_value_for_bubble * 100,
                }
                for item in top_holdings
            ])
            fig_concentration = px.bar(
                df_concentration,
                x="Value",
                y="Scheme",
                orientation="h",
                color="Pct",
                color_continuous_scale=["#1a365d", C_ACCENT, "#bee3f8"],
            )
            fig_concentration.update_layout(
                height=180,
                xaxis=dict(visible=False),
                yaxis=dict(tickfont=dict(size=10, color="#718096"), title=""),
                coloraxis_showscale=False,
                **PLOT_BASE,
            )
            st.plotly_chart(fig_concentration, use_container_width=True, config={"displayModeBar": False})

    with r4:
        st.markdown('<div class="card-title">Recent Redemptions</div>', unsafe_allow_html=True)
        recent_redemptions = data.get("recent_redemptions", [])
        if recent_redemptions:
            df_redemptions = pd.DataFrame([
                {"Scheme": item["Scheme"], "Payout": item["Payout"]}
                for item in recent_redemptions[:4]
            ])
            fig_redemptions = px.bar(
                df_redemptions,
                x="Payout",
                y="Scheme",
                orientation="h",
                color_discrete_sequence=[C_LOSS],
            )
            fig_redemptions.update_layout(
                height=140,
                xaxis=dict(visible=False),
                yaxis=dict(tickfont=dict(size=10, color="#718096"), title=""),
                **PLOT_BASE,
            )
            st.plotly_chart(fig_redemptions, use_container_width=True, config={"displayModeBar": False})
            st.dataframe(
                pd.DataFrame([
                    {
                        "Date": item["Date"],
                        "Scheme": item["Scheme"],
                        "Payout": fmt_inr(item["Payout"]),
                    }
                    for item in recent_redemptions[:4]
                ]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No recent redemptions found.")


# ─────────────────────────────────────────────
# MY PORTFOLIO
# ─────────────────────────────────────────────

def render_my_portfolio(data):
    st.markdown('<div class="page-title">Portfolio Ledger</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Open holdings and fully redeemed positions</div>', unsafe_allow_html=True)

    cat_colors = {
        "Equity Funds":      C_ACCENT,
        "Debt Funds":        "#f6ad55",
        "Gold & Commodities":"#ecc94b",
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
              <span style="font-size:11px;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:2px;">{label}</span>
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

    st.markdown('<div class="section-sep">Bubble Map — Invested vs XIRR</div>', unsafe_allow_html=True)
    df_bubble = pd.DataFrame([
        {
            "Scheme": clean_name(item["scheme"]),
            "Invested": item["invested"],
            "XIRR": item["xirr"],
            "Gain": max(item["pnl"], 0),
            "Type": item["category"],
        }
        for item in data["holdings"] if item["invested"] > 0
    ])
    if not df_bubble.empty:
        fig_bubble = px.scatter(
            df_bubble,
            x="Invested",
            y="XIRR",
            size="Gain",
            color="Type",
            hover_name="Scheme",
            color_discrete_map={"Equity Funds": C_ACCENT, "Debt Funds": "#f6ad55"},
        )
        fig_bubble.update_layout(
            height=340,
            xaxis=dict(showgrid=True, gridcolor=GRID, title="Invested (₹)", tickfont=dict(size=11, color="#718096")),
            yaxis=dict(showgrid=True, gridcolor=GRID, title="XIRR %", tickfont=dict(size=11, color="#718096")),
            legend=dict(font=dict(size=11, color="#718096"), bgcolor="rgba(0,0,0,0)"),
            **PLOT_BASE,
        )
        st.plotly_chart(fig_bubble, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-sep" style="margin-top:36px;">Fully Redeemed Positions</div>', unsafe_allow_html=True)
    if data.get("redeemed"):
        realized = data["realized_pnl"]
        color = gain_color(realized)
        st.markdown(
            f"""
            <div style="background:rgba({'72,187,120' if realized>=0 else '252,129,129'},0.05);border:1px solid rgba({'72,187,120' if realized>=0 else '252,129,129'},0.2);
                                border-radius:10px;padding:14px 18px;margin-bottom:14px;">
              <div style="font-size:10px;color:{color};text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:4px;">Total Realized P&L</div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:700;color:{color};">
                {gain_arrow(realized)} {fmt_inr(realized)}</div>
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
    status_label = "LIVE" if "Live" in tab else "INACTIVE"

    st.markdown(
        f"""
        <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;
    padding:20px 24px;display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:16px;">
          <div>
            <div style="font-size:10px;color:var(--muted);text-transform:uppercase;
    letter-spacing:1.5px;margin-bottom:4px;">Total Monthly Outflow</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:30px;font-weight:700;
    color:#f7fafc;letter-spacing:-1px;">{fmt_inr(total_outflow)}</div>
          </div>
          <div style="font-size:12px;font-weight:700;color:{'#48bb78' if 'Live' in tab else '#fc8181'};">
            {len(target_list)} {status_label}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if target_list:
        rows = [
            {
                "Scheme": clean_name(item["scheme"]),
                "Amount": fmt_inr(item["amount"]),
                "Day": item["day_label"],
                "Last Date": item["last_date"],
                "Next Due": item["next_date"],
                "Status": item["status"],
            }
            for item in target_list
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No SIPs in this category.")

    all_sips = live_sips + dead_sips
    if all_sips:
        st.markdown('<div class="section-sep">Monthly Outflow by Scheme</div>', unsafe_allow_html=True)
        df_bar = pd.DataFrame([
            {"Scheme": clean_name(item["scheme"]), "Amount": item["amount"]}
            for item in all_sips
        ])
        fig_bar = px.bar(
            df_bar,
            x="Amount",
            y="Scheme",
            orientation="h",
            color="Amount",
            color_continuous_scale=["#1a365d", C_ACCENT, "#bee3f8"],
        )
        fig_bar.update_layout(
            height=max(200, len(all_sips) * 30),
            xaxis=dict(visible=False),
            yaxis=dict(tickfont=dict(size=11, color="#718096"), title=""),
            coloraxis_showscale=False,
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
# MAIN
# ─────────────────────────────────────────────

def run_app():
    apply_page_config()
    inject_global_styles()
    initialize_session_state()
    active = active_data()
    menu = build_sidebar(active)
    if not active:
        show_upload()
        st.stop()
    if menu == "Dashboard":
        render_dashboard(active)
    elif menu == "My Portfolio":
        render_my_portfolio(active)
    elif menu == "SIP Center":
        render_sip_center(active)
    elif menu == "Transactions":
        render_transactions(active)
    elif menu == "Alerts":
        render_alerts(active)


run_app()