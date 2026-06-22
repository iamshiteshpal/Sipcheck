import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import difflib

st.set_page_config(page_title="MF Research Hub — SipCheck", page_icon="🏦", layout="wide")
from theme import apply_theme, theme_toggle_button
apply_theme()
from sidebar_v2 import render_sidebar
render_sidebar()

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer { visibility: hidden; }
.stApp { background: #0d0d24; color: #f0f0ff; }
section[data-testid="stSidebar"] {
    background: #0d0d24;
    border-right: 1px solid rgba(139,92,246,0.15);
}
.block-container { padding-top: 1rem; padding-bottom: 2rem; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(139,92,246,0.15);
}
.stTabs [data-baseweb="tab"] {
    color: #6b7280 !important;
    background: transparent !important;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.85rem;
}
.stTabs [aria-selected="true"] {
    color: #8b5cf6 !important;
    background: rgba(139,92,246,0.12) !important;
    border-bottom-color: #8b5cf6 !important;
}
.stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-highlight"] { background: transparent !important; }

/* Dataframes */
.stDataFrame { background: rgba(255,255,255,0.04) !important; border-radius: 10px; }
.stDataFrame thead th { background: rgba(139,92,246,0.15) !important; color: #f0f0ff !important; }
.stDataFrame tbody td { color: #f0f0ff !important; }
iframe[data-testid="stDataFrameResizable"] { border-radius: 10px; }

/* Inputs */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(139,92,246,0.3) !important;
    color: #f0f0ff !important;
    border-radius: 8px;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(139,92,246,0.3) !important;
    color: #f0f0ff !important;
}
.stMultiSelect > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(139,92,246,0.3) !important;
}
.stSlider > div { color: #f0f0ff; }
[data-testid="stMetricValue"] { color: #f0f0ff !important; }
[data-testid="stMetricLabel"] { color: #6b7280 !important; }

/* Buttons */
.stButton > button {
    background: rgba(139,92,246,0.15) !important;
    border: 1px solid rgba(139,92,246,0.4) !important;
    color: #f0f0ff !important;
    border-radius: 8px;
    font-weight: 600;
}
.stButton > button:hover {
    background: rgba(139,92,246,0.3) !important;
}

/* Cards */
.mf-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.75rem;
}
.mf-kpi {
    display: flex; gap: 12px; flex-wrap: wrap; margin: 0.8rem 0;
}
.mf-kpi-t {
    flex: 1; min-width: 110px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(139,92,246,0.16);
    border-radius: 12px;
    padding: 0.7rem 1rem;
}
.mf-kpi-l {
    font-size: 0.62rem; font-weight: 600; color: #6b7280;
    text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 3px;
}
.mf-kpi-v {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.15rem; font-weight: 700; color: #f0f0ff;
}
.mf-insight {
    background: rgba(139,92,246,0.07);
    border: 1px solid rgba(139,92,246,0.22);
    border-left: 4px solid #8b5cf6;
    border-radius: 12px;
    padding: 0.9rem 1.3rem;
    font-size: 0.88rem;
    color: #f0f0ff;
    line-height: 1.65;
    margin: 1rem 0;
}
.sec-lbl {
    font-size: 0.68rem; font-weight: 700; color: #6b7280;
    text-transform: uppercase; letter-spacing: 0.14em;
    margin: 1.2rem 0 0.6rem;
}
.overlap-meter-wrap { margin: 1rem 0; }
.overlap-label { font-size: 1rem; font-weight: 700; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# STATIC DATA
# ═══════════════════════════════════════════════════════════════════════════

STOCK_HOLDINGS = {
    "Bharti Airtel": [
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 7.2, "rating": 5, "aum_cr": 38200, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 6.8, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 6.1, "rating": 5, "aum_cr": 41300, "trend": "↑ Upgraded"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 5.4, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 4.9, "rating": 4, "aum_cr": 29600, "trend": "↓ Downgraded"},
        {"fund": "Kotak Bluechip Fund", "category": "Equity", "weightage": 4.2, "rating": 4, "aum_cr": 18200, "trend": "→ Stable"},
        {"fund": "Franklin India Bluechip", "category": "Equity", "weightage": 3.8, "rating": 3, "aum_cr": 8900, "trend": "→ Stable"},
        {"fund": "Canara Robeco Bluechip", "category": "Equity", "weightage": 3.1, "rating": 4, "aum_cr": 12400, "trend": "↑ Upgraded"},
        {"fund": "DSP Top 100 Equity Fund", "category": "Equity", "weightage": 2.7, "rating": 3, "aum_cr": 7600, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.3, "rating": 4, "aum_cr": 22100, "trend": "↑ Upgraded"},
        {"fund": "UTI Large Cap Fund", "category": "Equity", "weightage": 1.9, "rating": 3, "aum_cr": 11200, "trend": "→ Stable"},
    ],
    "Infosys": [
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 8.5, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 7.9, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "ICICI Pru Technology Fund", "category": "Equity", "weightage": 11.2, "rating": 4, "aum_cr": 12800, "trend": "↑ Upgraded"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 6.3, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 5.8, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 4.2, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "ABSL Digital India Fund", "category": "Equity", "weightage": 9.1, "rating": 4, "aum_cr": 4200, "trend": "→ Stable"},
        {"fund": "Canara Robeco Bluechip", "category": "Equity", "weightage": 3.5, "rating": 4, "aum_cr": 12400, "trend": "↓ Downgraded"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 3.1, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 7.6, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "HDFC Bank": [
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 9.8, "rating": 4, "aum_cr": 31800, "trend": "↑ Upgraded"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 8.4, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 7.6, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 7.1, "rating": 5, "aum_cr": 52100, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 6.9, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Kotak Standard Multicap", "category": "Equity", "weightage": 5.3, "rating": 4, "aum_cr": 44200, "trend": "→ Stable"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 4.8, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "Franklin India Prima Plus", "category": "Equity", "weightage": 3.9, "rating": 3, "aum_cr": 9100, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 8.9, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Nippon India Banking Fund", "category": "Equity", "weightage": 12.4, "rating": 4, "aum_cr": 7200, "trend": "↑ Upgraded"},
    ],
    "Reliance Industries": [
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 9.2, "rating": 5, "aum_cr": 58400, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 8.7, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 8.1, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "SBI Focused Equity Fund", "category": "Equity", "weightage": 7.4, "rating": 4, "aum_cr": 28900, "trend": "↑ Upgraded"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 6.8, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "Kotak Standard Multicap", "category": "Equity", "weightage": 6.1, "rating": 4, "aum_cr": 44200, "trend": "→ Stable"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 5.5, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 9.4, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 4.6, "rating": 4, "aum_cr": 22100, "trend": "↓ Downgraded"},
        {"fund": "ABSL Frontline Equity", "category": "Equity", "weightage": 4.1, "rating": 4, "aum_cr": 26400, "trend": "→ Stable"},
    ],
    "TCS": [
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 8.3, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "ICICI Pru Technology Fund", "category": "Equity", "weightage": 13.6, "rating": 4, "aum_cr": 12800, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 7.4, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 6.9, "rating": 4, "aum_cr": 29600, "trend": "↑ Upgraded"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 5.8, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "ABSL Digital India Fund", "category": "Equity", "weightage": 10.2, "rating": 4, "aum_cr": 4200, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 7.1, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 4.3, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
        {"fund": "Kotak Bluechip Fund", "category": "Equity", "weightage": 3.8, "rating": 4, "aum_cr": 18200, "trend": "→ Stable"},
        {"fund": "Franklin India Opportunities", "category": "Equity", "weightage": 2.9, "rating": 3, "aum_cr": 5100, "trend": "↓ Downgraded"},
    ],
    "ICICI Bank": [
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 9.1, "rating": 5, "aum_cr": 52100, "trend": "↑ Upgraded"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 7.8, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 7.2, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 6.5, "rating": 5, "aum_cr": 38200, "trend": "↑ Upgraded"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 5.9, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "Nippon India Banking Fund", "category": "Equity", "weightage": 14.2, "rating": 4, "aum_cr": 7200, "trend": "↑ Upgraded"},
        {"fund": "Kotak Standard Multicap", "category": "Equity", "weightage": 5.1, "rating": 4, "aum_cr": 44200, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 8.2, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 3.7, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "Franklin India Bluechip", "category": "Equity", "weightage": 3.2, "rating": 3, "aum_cr": 8900, "trend": "→ Stable"},
    ],
    "Axis Bank": [
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 6.8, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 5.9, "rating": 4, "aum_cr": 29600, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 5.2, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 4.8, "rating": 4, "aum_cr": 31800, "trend": "↓ Downgraded"},
        {"fund": "Nippon India Banking Fund", "category": "Equity", "weightage": 11.3, "rating": 4, "aum_cr": 7200, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 3.6, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Canara Robeco Bluechip", "category": "Equity", "weightage": 3.1, "rating": 4, "aum_cr": 12400, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 4.9, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Kotak Bluechip Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 18200, "trend": "→ Stable"},
    ],
    "Maruti Suzuki": [
        {"fund": "HDFC Mid-Cap Opportunities", "category": "Equity", "weightage": 4.6, "rating": 5, "aum_cr": 71200, "trend": "→ Stable"},
        {"fund": "Axis Mid Cap Fund", "category": "Equity", "weightage": 4.1, "rating": 5, "aum_cr": 28400, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "Kotak Emerging Equity", "category": "Equity", "weightage": 3.9, "rating": 4, "aum_cr": 44100, "trend": "↑ Upgraded"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "Nippon India Multi Cap", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 35600, "trend": "↓ Downgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.8, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Asian Paints": [
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 4.2, "rating": 4, "aum_cr": 31800, "trend": "↓ Downgraded"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 5.8, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 3.6, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 3.1, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 2.4, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 29600, "trend": "↓ Downgraded"},
        {"fund": "Canara Robeco Bluechip", "category": "Equity", "weightage": 2.1, "rating": 4, "aum_cr": 12400, "trend": "→ Stable"},
    ],
    "Bajaj Finance": [
        {"fund": "Axis Midcap Fund", "category": "Equity", "weightage": 5.4, "rating": 5, "aum_cr": 28400, "trend": "→ Stable"},
        {"fund": "HDFC Mid-Cap Opportunities", "category": "Equity", "weightage": 4.8, "rating": 5, "aum_cr": 71200, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 4.1, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Kotak Emerging Equity", "category": "Equity", "weightage": 3.7, "rating": 4, "aum_cr": 44100, "trend": "↑ Upgraded"},
        {"fund": "SBI Focused Equity Fund", "category": "Equity", "weightage": 3.2, "rating": 4, "aum_cr": 28900, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 2.9, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "Nippon India Mid Cap", "category": "Equity", "weightage": 3.8, "rating": 4, "aum_cr": 42800, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 2.2, "rating": 5, "aum_cr": 64500, "trend": "→ Stable"},
    ],
    "Wipro": [
        {"fund": "ICICI Pru Technology Fund", "category": "Equity", "weightage": 8.4, "rating": 4, "aum_cr": 12800, "trend": "→ Stable"},
        {"fund": "ABSL Digital India Fund", "category": "Equity", "weightage": 7.1, "rating": 4, "aum_cr": 4200, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 38200, "trend": "↓ Downgraded"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 2.3, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 1.9, "rating": 4, "aum_cr": 48200, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.4, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "HUL": [
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 6.2, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 5.4, "rating": 4, "aum_cr": 31800, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 4.8, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 4.3, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "ICICI Pru FMCG Fund", "category": "Equity", "weightage": 18.6, "rating": 4, "aum_cr": 1800, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 3.1, "rating": 5, "aum_cr": 64500, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.6, "rating": 4, "aum_cr": 22100, "trend": "↓ Downgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Sun Pharma": [
        {"fund": "ICICI Pru Pharma Fund", "category": "Equity", "weightage": 14.8, "rating": 4, "aum_cr": 4600, "trend": "↑ Upgraded"},
        {"fund": "SBI Healthcare Opp Fund", "category": "Equity", "weightage": 12.1, "rating": 4, "aum_cr": 2900, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 3.6, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 2.8, "rating": 5, "aum_cr": 38200, "trend": "↑ Upgraded"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 2.4, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "Nippon India Pharma Fund", "category": "Equity", "weightage": 11.2, "rating": 3, "aum_cr": 6200, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.6, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "L&T": [
        {"fund": "HDFC Infrastructure Fund", "category": "Equity", "weightage": 9.8, "rating": 4, "aum_cr": 3200, "trend": "↑ Upgraded"},
        {"fund": "SBI Focused Equity Fund", "category": "Equity", "weightage": 6.4, "rating": 4, "aum_cr": 28900, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 4.1, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 52100, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.9, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
        {"fund": "ABSL Frontline Equity", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 26400, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 2.1, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Kotak Mahindra Bank": [
        {"fund": "Kotak Bluechip Fund", "category": "Equity", "weightage": 8.2, "rating": 4, "aum_cr": 18200, "trend": "→ Stable"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 6.9, "rating": 4, "aum_cr": 48200, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 5.1, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 4.4, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 41300, "trend": "↓ Downgraded"},
        {"fund": "Nippon India Banking Fund", "category": "Equity", "weightage": 9.6, "rating": 4, "aum_cr": 7200, "trend": "→ Stable"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 3.2, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 4.1, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Titan": [
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 7.4, "rating": 5, "aum_cr": 41300, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 4.6, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "HDFC Mid-Cap Opportunities", "category": "Equity", "weightage": 3.9, "rating": 5, "aum_cr": 71200, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 3.4, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 2.8, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "SBI Focused Equity Fund", "category": "Equity", "weightage": 5.1, "rating": 4, "aum_cr": 28900, "trend": "→ Stable"},
        {"fund": "Kotak Emerging Equity", "category": "Equity", "weightage": 2.3, "rating": 4, "aum_cr": 44100, "trend": "↓ Downgraded"},
    ],
    "Nestle India": [
        {"fund": "ICICI Pru FMCG Fund", "category": "Equity", "weightage": 12.4, "rating": 4, "aum_cr": 1800, "trend": "→ Stable"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 3.8, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 3.2, "rating": 4, "aum_cr": 31800, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 2.8, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 2.4, "rating": 5, "aum_cr": 41300, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 1.9, "rating": 5, "aum_cr": 64500, "trend": "→ Stable"},
    ],
    "ITC": [
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 6.8, "rating": 4, "aum_cr": 31800, "trend": "↑ Upgraded"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 5.9, "rating": 4, "aum_cr": 29600, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru FMCG Fund", "category": "Equity", "weightage": 15.2, "rating": 4, "aum_cr": 1800, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 4.2, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 4.8, "rating": 5, "aum_cr": 52100, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 3.6, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 2.9, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 2.1, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
    ],
    "Power Grid": [
        {"fund": "HDFC Infrastructure Fund", "category": "Equity", "weightage": 7.4, "rating": 4, "aum_cr": 3200, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.8, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Nippon India Power & Infra", "category": "Equity", "weightage": 8.9, "rating": 4, "aum_cr": 8100, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 2.2, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "SBI PSU Fund", "category": "Equity", "weightage": 9.8, "rating": 3, "aum_cr": 4400, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 1.6, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
    ],
    "NTPC": [
        {"fund": "HDFC Infrastructure Fund", "category": "Equity", "weightage": 8.2, "rating": 4, "aum_cr": 3200, "trend": "↑ Upgraded"},
        {"fund": "SBI PSU Fund", "category": "Equity", "weightage": 11.4, "rating": 3, "aum_cr": 4400, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Power & Infra", "category": "Equity", "weightage": 7.6, "rating": 4, "aum_cr": 8100, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.6, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 1.9, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 1.4, "rating": 5, "aum_cr": 38200, "trend": "↓ Downgraded"},
    ],
    # ── New stocks added ──────────────────────────────────────────────────
    "HCL Technologies": [
        {"fund": "ICICI Pru Technology Fund", "category": "Equity", "weightage": 12.4, "rating": 4, "aum_cr": 12800, "trend": "↑ Upgraded"},
        {"fund": "ABSL Digital India Fund", "category": "Equity", "weightage": 9.8, "rating": 4, "aum_cr": 4200, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 4.6, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 4.1, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 3.8, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 4.2, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 3.1, "rating": 4, "aum_cr": 22100, "trend": "↑ Upgraded"},
    ],
    "Tech Mahindra": [
        {"fund": "ICICI Pru Technology Fund", "category": "Equity", "weightage": 9.6, "rating": 4, "aum_cr": 12800, "trend": "→ Stable"},
        {"fund": "ABSL Digital India Fund", "category": "Equity", "weightage": 7.2, "rating": 4, "aum_cr": 4200, "trend": "↑ Upgraded"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 3.4, "rating": 4, "aum_cr": 48200, "trend": "→ Stable"},
        {"fund": "DSP Flexi Cap Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 14800, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 2.2, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.6, "rating": 4, "aum_cr": 22100, "trend": "↑ Upgraded"},
    ],
    "HDFC Life Insurance": [
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 4.8, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 4.2, "rating": 5, "aum_cr": 52100, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 3.6, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 3.1, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 48200, "trend": "↑ Upgraded"},
    ],
    "HDFC AMC": [
        {"fund": "HDFC Mid-Cap Opportunities", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 71200, "trend": "↑ Upgraded"},
        {"fund": "Axis Mid Cap Fund", "category": "Equity", "weightage": 3.4, "rating": 5, "aum_cr": 28400, "trend": "→ Stable"},
        {"fund": "Nippon India Mid Cap", "category": "Equity", "weightage": 2.9, "rating": 4, "aum_cr": 42800, "trend": "→ Stable"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 2.1, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "Kotak Emerging Equity", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 44100, "trend": "→ Stable"},
    ],
    "Bajaj Finserv": [
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 5.2, "rating": 5, "aum_cr": 41300, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 4.8, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 4.1, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 3.6, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
    ],
    "Bajaj Auto": [
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 4.4, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 52100, "trend": "↑ Upgraded"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 3.2, "rating": 4, "aum_cr": 29600, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 2.8, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 48200, "trend": "↑ Upgraded"},
        {"fund": "DSP Flexi Cap Fund", "category": "Equity", "weightage": 2.1, "rating": 4, "aum_cr": 14800, "trend": "→ Stable"},
    ],
    "Tata Motors": [
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 6.2, "rating": 5, "aum_cr": 58400, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 4.8, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "ABSL Flexi Cap Fund", "category": "Equity", "weightage": 4.1, "rating": 4, "aum_cr": 26400, "trend": "→ Stable"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 3.6, "rating": 4, "aum_cr": 48200, "trend": "→ Stable"},
        {"fund": "Axis Mid Cap Fund", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 28400, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Mid Cap", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 42800, "trend": "→ Stable"},
    ],
    "Tata Steel": [
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 5.4, "rating": 5, "aum_cr": 58400, "trend": "↑ Upgraded"},
        {"fund": "ABSL Flexi Cap Fund", "category": "Equity", "weightage": 3.8, "rating": 4, "aum_cr": 26400, "trend": "→ Stable"},
        {"fund": "Kotak Standard Multicap", "category": "Equity", "weightage": 3.2, "rating": 4, "aum_cr": 44200, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.6, "rating": 4, "aum_cr": 22100, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 2.2, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
    ],
    "Tata Power": [
        {"fund": "HDFC Infrastructure Fund", "category": "Equity", "weightage": 6.8, "rating": 4, "aum_cr": 3200, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Power & Infra", "category": "Equity", "weightage": 5.4, "rating": 4, "aum_cr": 8100, "trend": "↑ Upgraded"},
        {"fund": "ABSL Flexi Cap Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 26400, "trend": "→ Stable"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 48200, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 1.9, "rating": 5, "aum_cr": 64500, "trend": "→ Stable"},
    ],
    "Tata Consultancy Services": [
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 8.3, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
        {"fund": "ICICI Pru Technology Fund", "category": "Equity", "weightage": 13.6, "rating": 4, "aum_cr": 12800, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 7.4, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 6.9, "rating": 4, "aum_cr": 29600, "trend": "↑ Upgraded"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 5.8, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "ABSL Digital India Fund", "category": "Equity", "weightage": 10.2, "rating": 4, "aum_cr": 4200, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 7.1, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Larsen & Toubro": [
        {"fund": "HDFC Infrastructure Fund", "category": "Equity", "weightage": 9.8, "rating": 4, "aum_cr": 3200, "trend": "↑ Upgraded"},
        {"fund": "SBI Focused Equity Fund", "category": "Equity", "weightage": 6.4, "rating": 4, "aum_cr": 28900, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 4.1, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 52100, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 64500, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.9, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 2.1, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Adani Ports": [
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 3.6, "rating": 5, "aum_cr": 38200, "trend": "↑ Upgraded"},
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 4.2, "rating": 5, "aum_cr": 58400, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 3.1, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 48200, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.8, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Adani Enterprises": [
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 58400, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 2.6, "rating": 5, "aum_cr": 64500, "trend": "→ Stable"},
        {"fund": "ABSL Flexi Cap Fund", "category": "Equity", "weightage": 2.2, "rating": 4, "aum_cr": 26400, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 1.8, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
    ],
    "UltraTech Cement": [
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 5.6, "rating": 5, "aum_cr": 58400, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 29600, "trend": "↑ Upgraded"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 48200, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.6, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Grasim Industries": [
        {"fund": "ABSL Flexi Cap Fund", "category": "Equity", "weightage": 4.4, "rating": 4, "aum_cr": 26400, "trend": "↑ Upgraded"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 3.6, "rating": 4, "aum_cr": 48200, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.2, "rating": 4, "aum_cr": 22100, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.4, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "JSW Steel": [
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 4.8, "rating": 5, "aum_cr": 58400, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 3.4, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
        {"fund": "ABSL Flexi Cap Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 26400, "trend": "→ Stable"},
        {"fund": "Kotak Standard Multicap", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 44200, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.6, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Hindalco": [
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 4.2, "rating": 5, "aum_cr": 58400, "trend": "↑ Upgraded"},
        {"fund": "ABSL Flexi Cap Fund", "category": "Equity", "weightage": 3.2, "rating": 4, "aum_cr": 26400, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 2.6, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 2.1, "rating": 4, "aum_cr": 48200, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.4, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Coal India": [
        {"fund": "SBI PSU Fund", "category": "Equity", "weightage": 14.8, "rating": 3, "aum_cr": 4400, "trend": "↑ Upgraded"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 3.4, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.8, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.2, "rating": 4, "aum_cr": 22100, "trend": "↑ Upgraded"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 1.6, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
    ],
    "ONGC": [
        {"fund": "SBI PSU Fund", "category": "Equity", "weightage": 12.6, "rating": 3, "aum_cr": 4400, "trend": "→ Stable"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 4.2, "rating": 4, "aum_cr": 31800, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 2.4, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 2.8, "rating": 5, "aum_cr": 52100, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.1, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
    ],
    "Indian Oil Corporation": [
        {"fund": "SBI PSU Fund", "category": "Equity", "weightage": 10.4, "rating": 3, "aum_cr": 4400, "trend": "↑ Upgraded"},
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 2.8, "rating": 5, "aum_cr": 58400, "trend": "→ Stable"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 1.8, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
        {"fund": "DSP Flexi Cap Fund", "category": "Equity", "weightage": 1.6, "rating": 4, "aum_cr": 14800, "trend": "↑ Upgraded"},
    ],
    "BPCL": [
        {"fund": "SBI PSU Fund", "category": "Equity", "weightage": 9.8, "rating": 3, "aum_cr": 4400, "trend": "↑ Upgraded"},
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 58400, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.4, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 1.9, "rating": 4, "aum_cr": 48200, "trend": "→ Stable"},
    ],
    "Cipla": [
        {"fund": "ICICI Pru Pharma Fund", "category": "Equity", "weightage": 11.6, "rating": 4, "aum_cr": 4600, "trend": "↑ Upgraded"},
        {"fund": "SBI Healthcare Opp Fund", "category": "Equity", "weightage": 9.8, "rating": 4, "aum_cr": 2900, "trend": "→ Stable"},
        {"fund": "Nippon India Pharma Fund", "category": "Equity", "weightage": 8.4, "rating": 3, "aum_cr": 6200, "trend": "↑ Upgraded"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 2.1, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
    ],
    "Dr Reddy's": [
        {"fund": "ICICI Pru Pharma Fund", "category": "Equity", "weightage": 12.8, "rating": 4, "aum_cr": 4600, "trend": "→ Stable"},
        {"fund": "Nippon India Pharma Fund", "category": "Equity", "weightage": 9.6, "rating": 3, "aum_cr": 6200, "trend": "↑ Upgraded"},
        {"fund": "SBI Healthcare Opp Fund", "category": "Equity", "weightage": 8.2, "rating": 4, "aum_cr": 2900, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 2.4, "rating": 5, "aum_cr": 38200, "trend": "↑ Upgraded"},
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 1.8, "rating": 5, "aum_cr": 41300, "trend": "→ Stable"},
    ],
    "Divi's Laboratories": [
        {"fund": "ICICI Pru Pharma Fund", "category": "Equity", "weightage": 10.4, "rating": 4, "aum_cr": 4600, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Pharma Fund", "category": "Equity", "weightage": 8.8, "rating": 3, "aum_cr": 6200, "trend": "→ Stable"},
        {"fund": "SBI Healthcare Opp Fund", "category": "Equity", "weightage": 7.4, "rating": 4, "aum_cr": 2900, "trend": "↑ Upgraded"},
        {"fund": "HDFC Mid-Cap Opportunities", "category": "Equity", "weightage": 2.6, "rating": 5, "aum_cr": 71200, "trend": "→ Stable"},
        {"fund": "Axis Mid Cap Fund", "category": "Equity", "weightage": 2.2, "rating": 5, "aum_cr": 28400, "trend": "↑ Upgraded"},
    ],
    "Eicher Motors": [
        {"fund": "HDFC Mid-Cap Opportunities", "category": "Equity", "weightage": 4.2, "rating": 5, "aum_cr": 71200, "trend": "↑ Upgraded"},
        {"fund": "Axis Mid Cap Fund", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 28400, "trend": "→ Stable"},
        {"fund": "Kotak Emerging Equity", "category": "Equity", "weightage": 3.4, "rating": 4, "aum_cr": 44100, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 2.8, "rating": 5, "aum_cr": 64500, "trend": "→ Stable"},
        {"fund": "Nippon India Mid Cap", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 42800, "trend": "→ Stable"},
    ],
    "Hero MotoCorp": [
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 3.8, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "SBI Bluechip Fund", "category": "Equity", "weightage": 3.2, "rating": 4, "aum_cr": 29600, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Large Cap", "category": "Equity", "weightage": 2.6, "rating": 4, "aum_cr": 22100, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 2.2, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.4, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
    ],
    "Mahindra & Mahindra": [
        {"fund": "HDFC Flexi Cap Fund", "category": "Equity", "weightage": 5.8, "rating": 5, "aum_cr": 58400, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 3.4, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 3.1, "rating": 5, "aum_cr": 52100, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 2.6, "rating": 5, "aum_cr": 64500, "trend": "→ Stable"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 1.8, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 2.2, "rating": 4, "aum_cr": 48200, "trend": "↑ Upgraded"},
    ],
    "Interglobe Aviation": [
        {"fund": "HDFC Mid-Cap Opportunities", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 71200, "trend": "↑ Upgraded"},
        {"fund": "Axis Mid Cap Fund", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 28400, "trend": "→ Stable"},
        {"fund": "Kotak Emerging Equity", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 44100, "trend": "↑ Upgraded"},
        {"fund": "DSP Flexi Cap Fund", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 14800, "trend": "→ Stable"},
        {"fund": "Nippon India Mid Cap", "category": "Equity", "weightage": 2.1, "rating": 4, "aum_cr": 42800, "trend": "→ Stable"},
    ],
    "Zomato": [
        {"fund": "Nippon India Flexi Cap Fund", "category": "Equity", "weightage": 4.8, "rating": 4, "aum_cr": 16200, "trend": "↑ Upgraded"},
        {"fund": "DSP Flexi Cap Fund", "category": "Equity", "weightage": 3.4, "rating": 4, "aum_cr": 14800, "trend": "↑ Upgraded"},
        {"fund": "Kotak Flexi Cap Fund", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 48200, "trend": "→ Stable"},
        {"fund": "Axis Mid Cap Fund", "category": "Equity", "weightage": 2.4, "rating": 5, "aum_cr": 28400, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 1.9, "rating": 5, "aum_cr": 64500, "trend": "→ Stable"},
    ],
    "Nykaa": [
        {"fund": "Nippon India Small Cap", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 48200, "trend": "→ Stable"},
        {"fund": "Axis Small Cap Fund", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 22800, "trend": "↑ Upgraded"},
        {"fund": "Kotak Emerging Equity", "category": "Equity", "weightage": 1.8, "rating": 4, "aum_cr": 44100, "trend": "→ Stable"},
        {"fund": "DSP Flexi Cap Fund", "category": "Equity", "weightage": 1.4, "rating": 4, "aum_cr": 14800, "trend": "↑ Upgraded"},
    ],
    "Policybazaar": [
        {"fund": "Nippon India Small Cap", "category": "Equity", "weightage": 2.4, "rating": 4, "aum_cr": 48200, "trend": "↑ Upgraded"},
        {"fund": "Axis Small Cap Fund", "category": "Equity", "weightage": 2.1, "rating": 4, "aum_cr": 22800, "trend": "→ Stable"},
        {"fund": "SBI Small Cap Fund", "category": "Equity", "weightage": 1.8, "rating": 5, "aum_cr": 38600, "trend": "↑ Upgraded"},
        {"fund": "Kotak Small Cap Fund", "category": "Equity", "weightage": 1.4, "rating": 4, "aum_cr": 19600, "trend": "→ Stable"},
    ],
    "Dixon Technologies": [
        {"fund": "Axis Mid Cap Fund", "category": "Equity", "weightage": 4.6, "rating": 5, "aum_cr": 28400, "trend": "↑ Upgraded"},
        {"fund": "HDFC Mid-Cap Opportunities", "category": "Equity", "weightage": 3.8, "rating": 5, "aum_cr": 71200, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Mid Cap", "category": "Equity", "weightage": 3.4, "rating": 4, "aum_cr": 42800, "trend": "→ Stable"},
        {"fund": "Kotak Emerging Equity", "category": "Equity", "weightage": 3.0, "rating": 4, "aum_cr": 44100, "trend": "↑ Upgraded"},
        {"fund": "SBI Small Cap Fund", "category": "Equity", "weightage": 2.2, "rating": 5, "aum_cr": 38600, "trend": "→ Stable"},
    ],
    "Havells India": [
        {"fund": "HDFC Mid-Cap Opportunities", "category": "Equity", "weightage": 3.6, "rating": 5, "aum_cr": 71200, "trend": "→ Stable"},
        {"fund": "Axis Mid Cap Fund", "category": "Equity", "weightage": 3.2, "rating": 5, "aum_cr": 28400, "trend": "↑ Upgraded"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 2.4, "rating": 5, "aum_cr": 64500, "trend": "→ Stable"},
        {"fund": "Kotak Emerging Equity", "category": "Equity", "weightage": 2.8, "rating": 4, "aum_cr": 44100, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Mid Cap", "category": "Equity", "weightage": 2.2, "rating": 4, "aum_cr": 42800, "trend": "→ Stable"},
    ],
    "Pidilite Industries": [
        {"fund": "Axis Bluechip Fund", "category": "Equity", "weightage": 4.2, "rating": 5, "aum_cr": 41300, "trend": "↑ Upgraded"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 3.4, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
        {"fund": "Parag Parikh Flexi Cap", "category": "Equity", "weightage": 2.8, "rating": 5, "aum_cr": 64500, "trend": "→ Stable"},
        {"fund": "HDFC Mid-Cap Opportunities", "category": "Equity", "weightage": 2.4, "rating": 5, "aum_cr": 71200, "trend": "↑ Upgraded"},
        {"fund": "SBI Focused Equity Fund", "category": "Equity", "weightage": 3.6, "rating": 4, "aum_cr": 28900, "trend": "→ Stable"},
    ],
    "SBI": [
        {"fund": "SBI PSU Fund", "category": "Equity", "weightage": 16.2, "rating": 3, "aum_cr": 4400, "trend": "↑ Upgraded"},
        {"fund": "HDFC Top 100 Fund", "category": "Equity", "weightage": 5.4, "rating": 4, "aum_cr": 31800, "trend": "→ Stable"},
        {"fund": "ICICI Pru Bluechip Fund", "category": "Equity", "weightage": 4.2, "rating": 5, "aum_cr": 52100, "trend": "↑ Upgraded"},
        {"fund": "Nippon India Banking Fund", "category": "Equity", "weightage": 10.8, "rating": 4, "aum_cr": 7200, "trend": "↑ Upgraded"},
        {"fund": "UTI Nifty 50 Index Fund", "category": "Equity", "weightage": 4.6, "rating": 5, "aum_cr": 19800, "trend": "→ Stable"},
        {"fund": "Mirae Asset Large Cap Fund", "category": "Equity", "weightage": 2.4, "rating": 5, "aum_cr": 38200, "trend": "→ Stable"},
    ],
}

FUND_HOLDINGS = {
    "Mirae Asset Large Cap Fund": {
        "category": "Equity - Large Cap", "sub_category": "Large Cap",
        "rating": 5, "launch_year": 2008, "aum_cr": 38200, "expense_ratio": 0.54,
        "min_sip": 1000, "benchmark": "Nifty 100 TRI", "fund_manager": "Gaurav Khandelwal",
        "top_sectors": {"Financial Services": 32.1, "IT": 18.4, "Consumer Goods": 10.2, "Energy": 9.8, "Healthcare": 7.6},
        "top_stocks": ["HDFC Bank", "Infosys", "Reliance Industries", "ICICI Bank", "Bharti Airtel"],
        "risk_metrics": {"std_dev": 13.8, "sharpe": 1.48, "beta": 0.92, "alpha": 2.4},
        "holdings": {
            "HDFC Bank": 9.2, "Infosys": 8.5, "Reliance Industries": 8.1,
            "ICICI Bank": 7.4, "TCS": 7.1, "Bharti Airtel": 7.2,
            "Axis Bank": 4.8, "HUL": 4.2, "ITC": 4.2, "L&T": 4.1,
            "Bajaj Finance": 3.9, "Kotak Mahindra Bank": 3.6, "Titan": 3.4,
            "Sun Pharma": 2.8, "Asian Paints": 2.6, "Nestle India": 2.4,
            "Wipro": 2.1, "Maruti Suzuki": 1.8, "Power Grid": 1.6, "NTPC": 1.4,
        },
        "returns": {"1D": 0.42, "1M": 2.1, "3M": 5.8, "6M": 9.4, "1Y": 22.4, "3Y": 18.6, "5Y": 16.2},
    },
    "Axis Bluechip Fund": {
        "category": "Equity - Large Cap", "sub_category": "Large Cap",
        "rating": 5, "launch_year": 2010, "aum_cr": 41300, "expense_ratio": 0.52,
        "min_sip": 500, "benchmark": "Nifty 50 TRI", "fund_manager": "Shreyash Devalkar",
        "top_sectors": {"Financial Services": 28.4, "IT": 22.1, "Consumer Goods": 14.6, "Healthcare": 8.2, "Auto": 6.8},
        "top_stocks": ["Infosys", "TCS", "HDFC Bank", "Titan", "Reliance Industries"],
        "risk_metrics": {"std_dev": 14.2, "sharpe": 1.38, "beta": 0.94, "alpha": 2.1},
        "holdings": {
            "Infosys": 7.9, "TCS": 7.4, "Bharti Airtel": 6.8, "HDFC Bank": 7.2,
            "ICICI Bank": 5.9, "Titan": 7.4, "Asian Paints": 5.8, "Bajaj Finance": 5.4,
            "HUL": 4.3, "Kotak Mahindra Bank": 3.8, "Axis Bank": 3.6,
            "Nestle India": 2.4, "ITC": 2.1, "Wipro": 2.0, "Sun Pharma": 1.9,
            "Maruti Suzuki": 1.8, "L&T": 1.7, "NTPC": 1.1, "Power Grid": 1.0, "Reliance Industries": 5.5,
        },
        "returns": {"1D": 0.38, "1M": 1.9, "3M": 5.4, "6M": 8.8, "1Y": 21.8, "3Y": 17.9, "5Y": 15.6},
    },
    "HDFC Top 100 Fund": {
        "category": "Equity - Large Cap", "sub_category": "Large Cap",
        "rating": 4, "launch_year": 1996, "aum_cr": 31800, "expense_ratio": 1.02,
        "min_sip": 500, "benchmark": "Nifty 100 TRI", "fund_manager": "Rahul Baijal",
        "top_sectors": {"Financial Services": 35.8, "Energy": 14.2, "IT": 12.4, "Consumer Goods": 9.8, "Metals": 5.6},
        "top_stocks": ["HDFC Bank", "ICICI Bank", "Reliance Industries", "ITC", "Infosys"],
        "risk_metrics": {"std_dev": 14.6, "sharpe": 1.32, "beta": 0.96, "alpha": 1.8},
        "holdings": {
            "HDFC Bank": 9.8, "ICICI Bank": 7.2, "Reliance Industries": 6.8,
            "Infosys": 6.3, "ITC": 6.8, "SBI": 5.4, "TCS": 5.8,
            "Axis Bank": 4.8, "HUL": 5.4, "L&T": 4.2, "Kotak Mahindra Bank": 3.8,
            "Bharti Airtel": 5.4, "Asian Paints": 4.2, "Sun Pharma": 3.6,
            "Nestle India": 3.2, "Titan": 2.8, "Wipro": 2.3, "Maruti Suzuki": 2.1,
            "NTPC": 1.8, "Power Grid": 1.6,
        },
        "returns": {"1D": 0.51, "1M": 2.4, "3M": 6.1, "6M": 10.2, "1Y": 24.6, "3Y": 19.2, "5Y": 17.4},
    },
    "ICICI Pru Bluechip Fund": {
        "category": "Equity - Large Cap", "sub_category": "Large Cap",
        "rating": 5, "launch_year": 2008, "aum_cr": 52100, "expense_ratio": 0.87,
        "min_sip": 100, "benchmark": "Nifty 100 TRI", "fund_manager": "Anish Tawakley",
        "top_sectors": {"Financial Services": 33.4, "Energy": 12.8, "IT": 14.2, "Consumer Goods": 8.6, "Telecom": 7.2},
        "top_stocks": ["ICICI Bank", "Reliance Industries", "HDFC Bank", "Infosys", "Bharti Airtel"],
        "risk_metrics": {"std_dev": 14.4, "sharpe": 1.42, "beta": 0.95, "alpha": 2.2},
        "holdings": {
            "ICICI Bank": 9.1, "Reliance Industries": 8.7, "HDFC Bank": 7.1,
            "Infosys": 6.8, "Bharti Airtel": 6.1, "ITC": 4.8, "TCS": 5.2,
            "Axis Bank": 5.2, "L&T": 3.8, "Kotak Mahindra Bank": 4.4,
            "SBI": 4.2, "HUL": 3.1, "Bajaj Finance": 2.9, "Sun Pharma": 2.8,
            "Titan": 2.4, "Nestle India": 2.1, "Asian Paints": 1.9,
            "Maruti Suzuki": 1.8, "NTPC": 1.9, "Power Grid": 2.2,
        },
        "returns": {"1D": 0.46, "1M": 2.2, "3M": 5.9, "6M": 9.8, "1Y": 23.1, "3Y": 18.8, "5Y": 16.8},
    },
    "SBI Bluechip Fund": {
        "category": "Equity - Large Cap", "sub_category": "Large Cap",
        "rating": 4, "launch_year": 2006, "aum_cr": 29600, "expense_ratio": 0.78,
        "min_sip": 500, "benchmark": "S&P BSE 100 TRI", "fund_manager": "Sohini Andani",
        "top_sectors": {"Financial Services": 30.2, "IT": 16.8, "Consumer Goods": 12.4, "Auto": 8.6, "Pharma": 6.2},
        "top_stocks": ["HDFC Bank", "ICICI Bank", "TCS", "Infosys", "HUL"],
        "risk_metrics": {"std_dev": 13.6, "sharpe": 1.26, "beta": 0.91, "alpha": 1.4},
        "holdings": {
            "HDFC Bank": 8.4, "Infosys": 5.8, "ICICI Bank": 7.8, "TCS": 6.9,
            "HUL": 6.2, "ITC": 5.9, "Reliance Industries": 4.8, "Bharti Airtel": 4.9,
            "Axis Bank": 3.8, "Kotak Mahindra Bank": 3.2, "L&T": 2.8,
            "Bajaj Finance": 2.6, "Sun Pharma": 2.4, "Asian Paints": 2.8,
            "Maruti Suzuki": 2.8, "Titan": 2.4, "Nestle India": 2.1,
            "Wipro": 1.9, "NTPC": 1.6, "Power Grid": 1.4,
        },
        "returns": {"1D": 0.35, "1M": 1.7, "3M": 4.9, "6M": 8.2, "1Y": 20.4, "3Y": 16.8, "5Y": 14.8},
    },
    "Nippon India Large Cap Fund": {
        "category": "Equity - Large Cap", "sub_category": "Large Cap",
        "rating": 4, "launch_year": 2004, "aum_cr": 22100, "expense_ratio": 0.89,
        "min_sip": 100, "benchmark": "Nifty 100 TRI", "fund_manager": "Sailesh Raj Bhan",
        "top_sectors": {"Financial Services": 34.2, "Energy": 13.6, "IT": 12.8, "Consumer Goods": 9.4, "Healthcare": 6.8},
        "top_stocks": ["HDFC Bank", "ICICI Bank", "Reliance Industries", "ITC", "Infosys"],
        "risk_metrics": {"std_dev": 14.1, "sharpe": 1.42, "beta": 0.94, "alpha": 2.8},
        "holdings": {
            "HDFC Bank": 9.4, "ICICI Bank": 7.8, "Reliance Industries": 7.2,
            "Infosys": 6.1, "ITC": 5.8, "Bharti Airtel": 4.9, "TCS": 4.6,
            "Axis Bank": 4.2, "HUL": 3.8, "L&T": 3.4, "Kotak Mahindra Bank": 2.9,
            "SBI": 4.1, "Sun Pharma": 2.6, "Asian Paints": 2.2, "Nestle India": 1.8,
            "Bajaj Finance": 1.6, "Titan": 1.4, "Maruti Suzuki": 1.2, "NTPC": 1.8, "Power Grid": 1.4,
        },
        "returns": {"1D": 0.44, "1M": 2.3, "3M": 6.2, "6M": 10.8, "1Y": 23.6, "3Y": 19.8, "5Y": 17.2},
    },
    "Parag Parikh Flexi Cap Fund": {
        "category": "Equity - Flexi Cap", "sub_category": "Flexi Cap",
        "rating": 5, "launch_year": 2013, "aum_cr": 64500, "expense_ratio": 0.63,
        "min_sip": 1000, "benchmark": "Nifty 500 TRI", "fund_manager": "Rajeev Thakkar",
        "top_sectors": {"Financial Services": 24.8, "IT": 19.6, "Consumer Goods": 12.2, "Global Equities": 18.4, "Auto": 7.2},
        "top_stocks": ["HDFC Bank", "Bajaj Holdings", "ITC", "ICICI Bank", "Infosys"],
        "risk_metrics": {"std_dev": 15.4, "sharpe": 1.62, "beta": 0.88, "alpha": 4.8},
        "holdings": {
            "HDFC Bank": 4.8, "Bajaj Holdings": 4.2, "ITC": 2.9, "Reliance Industries": 3.4,
            "ICICI Bank": 3.7, "Infosys": 4.2, "HUL": 3.1, "Axis Bank": 2.8,
            "Kotak Mahindra Bank": 2.4, "Titan": 3.4, "Asian Paints": 2.4,
            "Nestle India": 1.9, "Sun Pharma": 1.6, "L&T": 3.2, "Bharti Airtel": 2.2,
            "Maruti Suzuki": 2.4, "Wipro": 1.8, "NTPC": 1.4, "Power Grid": 1.2, "TCS": 2.1,
        },
        "returns": {"1D": 0.29, "1M": 1.4, "3M": 4.2, "6M": 8.4, "1Y": 19.8, "3Y": 21.4, "5Y": 18.6},
    },
    "Canara Robeco Flexi Cap Fund": {
        "category": "Equity - Flexi Cap", "sub_category": "Flexi Cap",
        "rating": 4, "launch_year": 2003, "aum_cr": 12400, "expense_ratio": 0.57,
        "min_sip": 1000, "benchmark": "Nifty 500 TRI", "fund_manager": "Shridatta Bhandwaldar",
        "top_sectors": {"Financial Services": 29.4, "IT": 17.8, "Consumer Goods": 11.6, "Healthcare": 9.2, "Auto": 7.4},
        "top_stocks": ["HDFC Bank", "ICICI Bank", "Infosys", "TCS", "Reliance Industries"],
        "risk_metrics": {"std_dev": 14.8, "sharpe": 1.28, "beta": 0.93, "alpha": 1.8},
        "holdings": {
            "HDFC Bank": 6.2, "Infosys": 5.4, "ICICI Bank": 5.8, "Reliance Industries": 4.6,
            "TCS": 4.9, "Axis Bank": 3.1, "HUL": 4.1, "ITC": 3.2,
            "Bharti Airtel": 3.1, "Bajaj Finance": 2.8, "Sun Pharma": 3.2,
            "Titan": 2.6, "Asian Paints": 2.1, "L&T": 2.8, "Nestle India": 1.8,
            "Kotak Mahindra Bank": 2.4, "Maruti Suzuki": 2.1, "Wipro": 1.6,
            "NTPC": 1.4, "Power Grid": 1.2,
        },
        "returns": {"1D": 0.41, "1M": 2.0, "3M": 5.5, "6M": 9.2, "1Y": 22.1, "3Y": 18.2, "5Y": 16.4},
    },
    "ABSL Flexi Cap Fund": {
        "category": "Equity - Flexi Cap", "sub_category": "Flexi Cap",
        "rating": 4, "launch_year": 1995, "aum_cr": 26400, "expense_ratio": 0.84,
        "min_sip": 500, "benchmark": "S&P BSE 500 TRI", "fund_manager": "Mahesh Patil",
        "top_sectors": {"Financial Services": 31.2, "Energy": 10.8, "IT": 14.6, "Consumer Goods": 10.4, "Telecom": 6.8},
        "top_stocks": ["Reliance Industries", "HDFC Bank", "ICICI Bank", "Infosys", "Bharti Airtel"],
        "risk_metrics": {"std_dev": 15.8, "sharpe": 1.18, "beta": 0.97, "alpha": 1.6},
        "holdings": {
            "Reliance Industries": 8.2, "HDFC Bank": 7.6, "ICICI Bank": 6.4,
            "Infosys": 5.9, "Bharti Airtel": 5.8, "ITC": 4.8, "TCS": 5.1,
            "HUL": 3.8, "Axis Bank": 3.4, "Bajaj Finance": 3.2,
            "Kotak Mahindra Bank": 2.8, "L&T": 2.6, "Sun Pharma": 2.4,
            "Titan": 2.2, "Asian Paints": 2.0, "Nestle India": 1.8,
            "Maruti Suzuki": 1.6, "Wipro": 1.4, "NTPC": 1.8, "Power Grid": 1.4,
        },
        "returns": {"1D": 0.44, "1M": 2.1, "3M": 5.7, "6M": 9.0, "1Y": 21.6, "3Y": 17.4, "5Y": 15.8},
    },
    "DSP Flexi Cap Fund": {
        "category": "Equity - Flexi Cap", "sub_category": "Flexi Cap",
        "rating": 4, "launch_year": 1997, "aum_cr": 14800, "expense_ratio": 0.72,
        "min_sip": 500, "benchmark": "Nifty 500 TRI", "fund_manager": "Atul Bhole",
        "top_sectors": {"Financial Services": 27.6, "IT": 16.2, "Consumer Goods": 13.4, "Healthcare": 10.8, "Auto": 8.2},
        "top_stocks": ["HDFC Bank", "TCS", "Infosys", "HUL", "ICICI Bank"],
        "risk_metrics": {"std_dev": 14.6, "sharpe": 1.22, "beta": 0.94, "alpha": 1.4},
        "holdings": {
            "HDFC Bank": 7.4, "TCS": 6.8, "Infosys": 5.6, "ICICI Bank": 5.2,
            "HUL": 4.6, "ITC": 4.4, "Reliance Industries": 4.2, "Bharti Airtel": 3.8,
            "Sun Pharma": 3.4, "L&T": 3.2, "Bajaj Finance": 2.8,
            "Titan": 2.6, "Asian Paints": 2.4, "Nestle India": 2.2,
            "Kotak Mahindra Bank": 2.0, "Axis Bank": 1.8, "Maruti Suzuki": 2.4,
            "Wipro": 1.6, "NTPC": 1.4, "Power Grid": 1.2,
        },
        "returns": {"1D": 0.38, "1M": 1.8, "3M": 5.1, "6M": 8.6, "1Y": 20.8, "3Y": 17.1, "5Y": 15.2},
    },
    "Kotak Flexi Cap Fund": {
        "category": "Equity - Flexi Cap", "sub_category": "Flexi Cap",
        "rating": 4, "launch_year": 2009, "aum_cr": 48200, "expense_ratio": 0.62,
        "min_sip": 100, "benchmark": "Nifty 500 TRI", "fund_manager": "Harsha Upadhyaya",
        "top_sectors": {"Financial Services": 30.8, "IT": 15.6, "Consumer Goods": 11.8, "Auto": 9.2, "Healthcare": 7.6},
        "top_stocks": ["HDFC Bank", "ICICI Bank", "Kotak Mahindra Bank", "Reliance Industries", "Infosys"],
        "risk_metrics": {"std_dev": 15.2, "sharpe": 1.24, "beta": 0.95, "alpha": 1.8},
        "holdings": {
            "HDFC Bank": 8.2, "ICICI Bank": 6.8, "Reliance Industries": 5.8,
            "Infosys": 5.4, "Kotak Mahindra Bank": 6.9, "TCS": 4.8, "Bharti Airtel": 4.2,
            "ITC": 3.8, "Axis Bank": 3.4, "HUL": 3.2, "Bajaj Finance": 2.8,
            "Titan": 2.4, "Maruti Suzuki": 2.8, "Sun Pharma": 2.2,
            "L&T": 2.0, "Asian Paints": 1.8, "Nestle India": 1.6,
            "Wipro": 1.9, "NTPC": 1.4, "Power Grid": 1.2,
        },
        "returns": {"1D": 0.43, "1M": 2.1, "3M": 5.6, "6M": 9.1, "1Y": 21.4, "3Y": 17.8, "5Y": 15.6},
    },
    "UTI Flexi Cap Fund": {
        "category": "Equity - Flexi Cap", "sub_category": "Flexi Cap",
        "rating": 4, "launch_year": 1992, "aum_cr": 28400, "expense_ratio": 0.93,
        "min_sip": 500, "benchmark": "Nifty 500 TRI", "fund_manager": "Ajay Tyagi",
        "top_sectors": {"Financial Services": 32.1, "IT": 17.4, "Consumer Goods": 12.8, "Auto": 8.6, "Healthcare": 7.2},
        "top_stocks": ["HDFC Bank", "Bajaj Finance", "Kotak Mahindra Bank", "ICICI Bank", "Infosys"],
        "risk_metrics": {"std_dev": 15.2, "sharpe": 1.18, "beta": 0.96, "alpha": 1.4},
        "holdings": {
            "HDFC Bank": 7.8, "Bajaj Finance": 5.4, "Kotak Mahindra Bank": 5.1,
            "ICICI Bank": 5.8, "Infosys": 5.2, "TCS": 4.6, "HUL": 4.2,
            "ITC": 3.8, "Reliance Industries": 3.6, "Bharti Airtel": 3.2,
            "Axis Bank": 2.8, "L&T": 2.6, "Sun Pharma": 2.4, "Titan": 2.2,
            "Asian Paints": 2.0, "Nestle India": 1.8, "Maruti Suzuki": 1.6,
            "Wipro": 1.4, "NTPC": 1.2, "Power Grid": 1.0,
        },
        "returns": {"1D": 0.36, "1M": 1.8, "3M": 5.2, "6M": 9.1, "1Y": 20.6, "3Y": 17.6, "5Y": 15.4},
    },
    "HDFC Flexi Cap Fund": {
        "category": "Equity - Flexi Cap", "sub_category": "Flexi Cap",
        "rating": 5, "launch_year": 1994, "aum_cr": 58400, "expense_ratio": 0.83,
        "min_sip": 100, "benchmark": "Nifty 500 TRI", "fund_manager": "Roshi Jain",
        "top_sectors": {"Financial Services": 28.4, "Energy": 16.2, "Consumer Goods": 13.8, "IT": 12.4, "Healthcare": 9.2},
        "top_stocks": ["HDFC Bank", "Reliance Industries", "Infosys", "ICICI Bank", "ITC"],
        "risk_metrics": {"std_dev": 14.8, "sharpe": 1.54, "beta": 0.93, "alpha": 4.2},
        "holdings": {
            "HDFC Bank": 9.2, "Reliance Industries": 9.2, "Infosys": 6.4,
            "ICICI Bank": 6.8, "ITC": 5.6, "TCS": 5.2, "Bharti Airtel": 4.8,
            "L&T": 4.2, "HUL": 3.8, "Axis Bank": 3.4, "Kotak Mahindra Bank": 2.8,
            "Bajaj Finance": 2.6, "Sun Pharma": 2.4, "Titan": 2.2,
            "Tata Motors": 2.0, "Asian Paints": 1.8, "Nestle India": 1.6,
            "Maruti Suzuki": 1.4, "NTPC": 1.2, "Power Grid": 1.0,
        },
        "returns": {"1D": 0.52, "1M": 2.6, "3M": 7.1, "6M": 12.4, "1Y": 26.4, "3Y": 22.8, "5Y": 19.6},
    },
    "HDFC Mid-Cap Opportunities Fund": {
        "category": "Equity - Mid Cap", "sub_category": "Mid Cap",
        "rating": 5, "launch_year": 2007, "aum_cr": 71200, "expense_ratio": 0.78,
        "min_sip": 100, "benchmark": "Nifty Midcap 150 TRI", "fund_manager": "Chirag Setalvad",
        "top_sectors": {"Financial Services": 18.4, "Consumer Goods": 14.2, "Auto": 12.8, "Healthcare": 11.6, "IT": 8.4},
        "top_stocks": ["Cholamandalam Finance", "Bajaj Finance", "Supreme Industries", "Persistent Systems", "Maruti Suzuki"],
        "risk_metrics": {"std_dev": 18.4, "sharpe": 1.42, "beta": 1.08, "alpha": 3.8},
        "holdings": {
            "Cholamandalam Finance": 4.8, "Supreme Industries": 4.2, "Tube Investments": 3.8,
            "Persistent Systems": 3.6, "Bajaj Finance": 4.8, "Maruti Suzuki": 4.6,
            "Titan": 3.9, "Crompton Greaves": 3.4, "Mphasis": 3.2,
            "Voltas": 2.8, "Indian Hotels": 2.6, "PI Industries": 2.4,
            "Alkem Laboratories": 2.2, "HDFC Bank": 2.0, "Infosys": 1.8,
            "ITC": 1.6, "L&T": 2.2, "Reliance Industries": 1.4, "TCS": 1.2, "ICICI Bank": 1.6,
        },
        "returns": {"1D": 0.58, "1M": 2.8, "3M": 7.4, "6M": 14.8, "1Y": 28.6, "3Y": 24.2, "5Y": 21.4},
    },
    "Axis Mid Cap Fund": {
        "category": "Equity - Mid Cap", "sub_category": "Mid Cap",
        "rating": 5, "launch_year": 2011, "aum_cr": 28400, "expense_ratio": 0.54,
        "min_sip": 500, "benchmark": "Nifty Midcap 150 TRI", "fund_manager": "Shreyash Devalkar",
        "top_sectors": {"Financial Services": 16.8, "Consumer Goods": 16.4, "Healthcare": 14.2, "IT": 12.6, "Auto": 10.8},
        "top_stocks": ["Bajaj Finance", "Cholamandalam Finance", "Mphasis", "Titan", "Persistent Systems"],
        "risk_metrics": {"std_dev": 19.2, "sharpe": 1.48, "beta": 1.12, "alpha": 4.6},
        "holdings": {
            "Cholamandalam Finance": 4.4, "Mphasis": 4.1, "Tube Investments": 3.8,
            "Page Industries": 3.6, "Titan": 4.1, "Bajaj Finance": 5.4,
            "Alkem Laboratories": 3.4, "Indian Hotels": 3.2, "Persistent Systems": 3.0,
            "Dixon Technologies": 2.8, "PI Industries": 2.6, "Voltas": 2.4,
            "Maruti Suzuki": 2.2, "HDFC Bank": 2.0, "Infosys": 1.8,
            "ITC": 1.6, "L&T": 1.4, "Reliance Industries": 1.2, "ICICI Bank": 1.4, "TCS": 1.6,
        },
        "returns": {"1D": 0.62, "1M": 3.1, "3M": 8.2, "6M": 16.4, "1Y": 30.4, "3Y": 26.1, "5Y": 23.2},
    },
    "Nippon India Mid Cap Fund": {
        "category": "Equity - Mid Cap", "sub_category": "Mid Cap",
        "rating": 4, "launch_year": 2010, "aum_cr": 42800, "expense_ratio": 0.82,
        "min_sip": 100, "benchmark": "Nifty Midcap 150 TRI", "fund_manager": "Manish Gunwani",
        "top_sectors": {"Financial Services": 20.2, "Consumer Goods": 13.8, "IT": 12.4, "Healthcare": 11.8, "Metals": 8.6},
        "top_stocks": ["Bajaj Finance", "Mphasis", "Cholamandalam Finance", "Persistent Systems", "Tube Investments"],
        "risk_metrics": {"std_dev": 19.8, "sharpe": 1.22, "beta": 1.14, "alpha": 3.2},
        "holdings": {
            "Bajaj Finance": 3.8, "Mphasis": 3.4, "Cholamandalam Finance": 3.2,
            "Persistent Systems": 3.0, "Tube Investments": 2.8, "Indian Hotels": 2.6,
            "Alkem Laboratories": 2.4, "Supreme Industries": 2.2, "Voltas": 2.0,
            "Page Industries": 1.8, "PI Industries": 1.6, "Dixon Technologies": 2.4,
            "Titan": 2.2, "HDFC Bank": 1.8, "Infosys": 1.6,
            "Maruti Suzuki": 1.8, "ITC": 1.4, "L&T": 1.6, "ICICI Bank": 1.4, "Reliance Industries": 1.2,
        },
        "returns": {"1D": 0.54, "1M": 2.6, "3M": 6.8, "6M": 13.2, "1Y": 26.2, "3Y": 22.4, "5Y": 19.6},
    },
    "Kotak Emerging Equity": {
        "category": "Equity - Mid Cap", "sub_category": "Mid Cap",
        "rating": 4, "launch_year": 2007, "aum_cr": 44100, "expense_ratio": 0.41,
        "min_sip": 100, "benchmark": "Nifty Midcap 150 TRI", "fund_manager": "Pankaj Tibrewal",
        "top_sectors": {"Financial Services": 22.4, "Consumer Goods": 16.8, "IT": 14.2, "Auto": 11.6, "Healthcare": 9.8},
        "top_stocks": ["Cholamandalam Finance", "Indian Hotels", "Mphasis", "Supreme Industries", "Tube Investments"],
        "risk_metrics": {"std_dev": 19.2, "sharpe": 1.22, "beta": 1.12, "alpha": 3.6},
        "holdings": {
            "Cholamandalam Finance": 4.6, "Indian Hotels": 4.2, "Mphasis": 3.8,
            "Supreme Industries": 3.6, "Tube Investments": 3.2, "Bajaj Finance": 3.8,
            "Persistent Systems": 3.0, "PI Industries": 2.8, "Dixon Technologies": 3.0,
            "Voltas": 2.4, "Alkem Laboratories": 2.2, "Page Industries": 2.0,
            "Maruti Suzuki": 2.4, "HDFC Bank": 1.8, "Infosys": 1.6,
            "ITC": 1.4, "L&T": 1.2, "Titan": 1.8, "ICICI Bank": 1.4, "TCS": 1.2,
        },
        "returns": {"1D": 0.61, "1M": 3.0, "3M": 8.0, "6M": 14.2, "1Y": 25.8, "3Y": 21.6, "5Y": 18.4},
    },
    "DSP Midcap Fund": {
        "category": "Equity - Mid Cap", "sub_category": "Mid Cap",
        "rating": 4, "launch_year": 2006, "aum_cr": 18600, "expense_ratio": 0.68,
        "min_sip": 500, "benchmark": "Nifty Midcap 150 TRI", "fund_manager": "Vinit Sambre",
        "top_sectors": {"Financial Services": 19.6, "IT": 18.4, "Consumer Goods": 14.8, "Healthcare": 12.2, "Chemicals": 9.4},
        "top_stocks": ["Persistent Systems", "SRF", "Mphasis", "Cholamandalam Finance", "Tube Investments"],
        "risk_metrics": {"std_dev": 20.4, "sharpe": 1.18, "beta": 1.14, "alpha": 3.2},
        "holdings": {
            "Persistent Systems": 4.2, "SRF": 3.8, "Mphasis": 3.6,
            "Cholamandalam Finance": 3.4, "Tube Investments": 3.0, "Alkem Laboratories": 2.8,
            "Indian Hotels": 2.6, "PI Industries": 2.4, "Supreme Industries": 2.2,
            "Dixon Technologies": 2.0, "Voltas": 1.8, "Page Industries": 1.6,
            "Bajaj Finance": 3.2, "HDFC Bank": 1.4, "Infosys": 1.2,
            "ITC": 1.0, "L&T": 1.2, "Titan": 1.6, "ICICI Bank": 1.0, "TCS": 0.8,
        },
        "returns": {"1D": 0.56, "1M": 2.7, "3M": 7.2, "6M": 13.1, "1Y": 27.4, "3Y": 23.2, "5Y": 19.8},
    },
    "SBI Small Cap Fund": {
        "category": "Equity - Small Cap", "sub_category": "Small Cap",
        "rating": 5, "launch_year": 2009, "aum_cr": 38600, "expense_ratio": 0.69,
        "min_sip": 500, "benchmark": "S&P BSE Small Cap TRI", "fund_manager": "Bhavin Vithlani",
        "top_sectors": {"Consumer Goods": 22.4, "Healthcare": 16.8, "Auto Ancillaries": 12.6, "Chemicals": 10.4, "IT": 8.2},
        "top_stocks": ["Hawkins Cookers", "Elgi Equipment", "Aarti Industries", "Suprajit Engineering", "Navin Fluorine"],
        "risk_metrics": {"std_dev": 24.2, "sharpe": 1.28, "beta": 1.22, "alpha": 5.4},
        "holdings": {
            "Hawkins Cookers": 3.8, "Elgi Equipment": 3.4, "Suprajit Engineering": 3.2,
            "Aarti Industries": 3.0, "Navin Fluorine": 2.8, "Vinati Organics": 2.6,
            "Astral Poly": 2.4, "Dixon Technologies": 2.2, "CAMS": 2.0,
            "Fine Organic": 1.8, "Shriram Finance": 1.8, "Laurus Labs": 1.6,
            "Bajaj Finance": 1.4, "HDFC Bank": 1.2, "Infosys": 1.0,
            "ITC": 0.8, "L&T": 1.2, "Reliance Industries": 0.8, "Titan": 1.4, "ICICI Bank": 1.0,
        },
        "returns": {"1D": 0.71, "1M": 3.4, "3M": 9.2, "6M": 18.4, "1Y": 34.8, "3Y": 28.6, "5Y": 26.2},
    },
    "HDFC Small Cap Fund": {
        "category": "Equity - Small Cap", "sub_category": "Small Cap",
        "rating": 4, "launch_year": 2008, "aum_cr": 32400, "expense_ratio": 0.62,
        "min_sip": 100, "benchmark": "Nifty Smallcap 250 TRI", "fund_manager": "Chirag Setalvad",
        "top_sectors": {"Chemicals": 18.4, "Consumer Goods": 14.6, "Healthcare": 12.2, "IT": 10.8, "Auto": 9.4},
        "top_stocks": ["Aarti Industries", "Navin Fluorine", "Suprajit Engineering", "Elgi Equipment", "Astral Poly"],
        "risk_metrics": {"std_dev": 23.4, "sharpe": 1.18, "beta": 1.18, "alpha": 4.6},
        "holdings": {
            "Aarti Industries": 3.6, "Navin Fluorine": 3.2, "Suprajit Engineering": 2.8,
            "Elgi Equipment": 2.6, "Astral Poly": 2.4, "Laurus Labs": 2.2,
            "Fine Organic": 2.0, "Hawkins Cookers": 1.8, "Shriram Finance": 1.8,
            "CAMS": 1.6, "Dixon Technologies": 2.4, "Vinati Organics": 1.4,
            "Bajaj Finance": 1.2, "HDFC Bank": 1.0, "Infosys": 0.8,
            "ITC": 0.8, "L&T": 1.0, "Titan": 1.2, "Maruti Suzuki": 1.4, "ICICI Bank": 0.8,
        },
        "returns": {"1D": 0.68, "1M": 3.2, "3M": 8.6, "6M": 16.8, "1Y": 32.4, "3Y": 26.8, "5Y": 24.2},
    },
    "Nippon India Small Cap Fund": {
        "category": "Equity - Small Cap", "sub_category": "Small Cap",
        "rating": 4, "launch_year": 2010, "aum_cr": 48200, "expense_ratio": 0.87,
        "min_sip": 100, "benchmark": "Nifty Smallcap 250 TRI", "fund_manager": "Samir Rachh",
        "top_sectors": {"Industrials": 18.4, "Consumer Goods": 16.6, "Chemicals": 14.2, "Healthcare": 12.8, "IT": 10.4},
        "top_stocks": ["Aarti Industries", "Navin Fluorine", "Suprajit Engineering", "Elgi Equipment", "SRF"],
        "risk_metrics": {"std_dev": 26.4, "sharpe": 1.12, "beta": 1.32, "alpha": 5.4},
        "holdings": {
            "Aarti Industries": 3.2, "Navin Fluorine": 2.8, "Suprajit Engineering": 2.6,
            "Elgi Equipment": 2.4, "SRF": 2.2, "Fine Organic": 2.0,
            "Hawkins Cookers": 1.8, "Laurus Labs": 1.8, "CAMS": 1.6,
            "Dixon Technologies": 2.4, "Vinati Organics": 1.4, "Shriram Finance": 1.4,
            "Bajaj Finance": 1.2, "HDFC Bank": 1.0, "Infosys": 0.8,
            "ITC": 0.6, "L&T": 0.8, "Titan": 1.0, "Maruti Suzuki": 0.8, "ICICI Bank": 0.6,
        },
        "returns": {"1D": 0.76, "1M": 3.8, "3M": 10.2, "6M": 18.2, "1Y": 35.2, "3Y": 29.4, "5Y": 25.6},
    },
    "Axis Small Cap Fund": {
        "category": "Equity - Small Cap", "sub_category": "Small Cap",
        "rating": 5, "launch_year": 2013, "aum_cr": 22800, "expense_ratio": 0.53,
        "min_sip": 500, "benchmark": "Nifty Smallcap 250 TRI", "fund_manager": "Anupam Tiwari",
        "top_sectors": {"Consumer Goods": 20.4, "Healthcare": 16.8, "Chemicals": 14.6, "IT": 11.2, "Industrials": 9.8},
        "top_stocks": ["Aarti Industries", "Navin Fluorine", "Astral Poly", "Hawkins Cookers", "Dixon Technologies"],
        "risk_metrics": {"std_dev": 24.8, "sharpe": 1.28, "beta": 1.24, "alpha": 5.8},
        "holdings": {
            "Aarti Industries": 3.8, "Navin Fluorine": 3.4, "Astral Poly": 3.0,
            "Hawkins Cookers": 2.8, "Dixon Technologies": 2.6, "Vinati Organics": 2.4,
            "CAMS": 2.2, "Elgi Equipment": 2.0, "Suprajit Engineering": 1.8,
            "Fine Organic": 1.6, "Laurus Labs": 1.6, "Shriram Finance": 1.4,
            "SRF": 1.2, "HDFC Bank": 1.0, "Infosys": 0.8,
            "ITC": 0.6, "L&T": 0.8, "Bajaj Finance": 1.0, "Titan": 0.8, "ICICI Bank": 0.6,
        },
        "returns": {"1D": 0.74, "1M": 3.6, "3M": 9.8, "6M": 17.4, "1Y": 36.2, "3Y": 31.4, "5Y": 26.8},
    },
    "Kotak Small Cap Fund": {
        "category": "Equity - Small Cap", "sub_category": "Small Cap",
        "rating": 4, "launch_year": 2005, "aum_cr": 19600, "expense_ratio": 0.46,
        "min_sip": 100, "benchmark": "Nifty Smallcap 250 TRI", "fund_manager": "Pankaj Tibrewal",
        "top_sectors": {"Consumer Goods": 22.8, "Chemicals": 18.4, "Healthcare": 14.2, "IT": 10.6, "Engineering": 8.8},
        "top_stocks": ["Aarti Industries", "Hawkins Cookers", "SRF", "CAMS", "Fine Organic"],
        "risk_metrics": {"std_dev": 25.6, "sharpe": 1.16, "beta": 1.28, "alpha": 4.8},
        "holdings": {
            "Aarti Industries": 3.6, "Hawkins Cookers": 3.2, "SRF": 2.8,
            "CAMS": 2.6, "Fine Organic": 2.4, "Navin Fluorine": 2.2,
            "Suprajit Engineering": 2.0, "Elgi Equipment": 1.8, "Laurus Labs": 1.6,
            "Vinati Organics": 1.6, "Dixon Technologies": 1.4, "Shriram Finance": 1.4,
            "Astral Poly": 1.2, "HDFC Bank": 1.0, "Infosys": 0.8,
            "ITC": 0.6, "L&T": 0.8, "Bajaj Finance": 0.8, "Titan": 0.6, "ICICI Bank": 0.6,
        },
        "returns": {"1D": 0.72, "1M": 3.4, "3M": 9.4, "6M": 16.8, "1Y": 34.6, "3Y": 29.2, "5Y": 24.4},
    },
}

FUND_SCREENER_DATA = [
    {"Fund Name": "Mirae Asset Large Cap Fund", "Category": "Equity", "Sub-Category": "Large Cap", "Rating": 5, "1Y Return": 22.4, "3Y Return": 18.6, "Expense Ratio": 0.54, "AUM (Cr)": 38200, "Min SIP": 1000},
    {"Fund Name": "Axis Bluechip Fund", "Category": "Equity", "Sub-Category": "Large Cap", "Rating": 5, "1Y Return": 21.8, "3Y Return": 17.9, "Expense Ratio": 0.52, "AUM (Cr)": 41300, "Min SIP": 500},
    {"Fund Name": "HDFC Top 100 Fund", "Category": "Equity", "Sub-Category": "Large Cap", "Rating": 4, "1Y Return": 24.6, "3Y Return": 19.2, "Expense Ratio": 1.02, "AUM (Cr)": 31800, "Min SIP": 500},
    {"Fund Name": "ICICI Pru Bluechip Fund", "Category": "Equity", "Sub-Category": "Large Cap", "Rating": 5, "1Y Return": 23.1, "3Y Return": 18.8, "Expense Ratio": 0.87, "AUM (Cr)": 52100, "Min SIP": 100},
    {"Fund Name": "SBI Bluechip Fund", "Category": "Equity", "Sub-Category": "Large Cap", "Rating": 4, "1Y Return": 20.4, "3Y Return": 16.8, "Expense Ratio": 0.78, "AUM (Cr)": 29600, "Min SIP": 500},
    {"Fund Name": "Canara Robeco Bluechip", "Category": "Equity", "Sub-Category": "Large Cap", "Rating": 4, "1Y Return": 22.1, "3Y Return": 18.2, "Expense Ratio": 0.57, "AUM (Cr)": 12400, "Min SIP": 1000},
    {"Fund Name": "Kotak Bluechip Fund", "Category": "Equity", "Sub-Category": "Large Cap", "Rating": 4, "1Y Return": 19.8, "3Y Return": 16.4, "Expense Ratio": 0.46, "AUM (Cr)": 18200, "Min SIP": 100},
    {"Fund Name": "Nippon India Large Cap", "Category": "Equity", "Sub-Category": "Large Cap", "Rating": 4, "1Y Return": 23.6, "3Y Return": 19.8, "Expense Ratio": 0.89, "AUM (Cr)": 22100, "Min SIP": 100},
    {"Fund Name": "Parag Parikh Flexi Cap", "Category": "Equity", "Sub-Category": "Flexi Cap", "Rating": 5, "1Y Return": 19.8, "3Y Return": 21.4, "Expense Ratio": 0.63, "AUM (Cr)": 64500, "Min SIP": 1000},
    {"Fund Name": "Canara Robeco Flexi Cap", "Category": "Equity", "Sub-Category": "Flexi Cap", "Rating": 4, "1Y Return": 22.1, "3Y Return": 18.2, "Expense Ratio": 0.57, "AUM (Cr)": 12400, "Min SIP": 1000},
    {"Fund Name": "ABSL Flexi Cap Fund", "Category": "Equity", "Sub-Category": "Flexi Cap", "Rating": 4, "1Y Return": 21.6, "3Y Return": 17.4, "Expense Ratio": 0.84, "AUM (Cr)": 26400, "Min SIP": 500},
    {"Fund Name": "Kotak Flexi Cap Fund", "Category": "Equity", "Sub-Category": "Flexi Cap", "Rating": 4, "1Y Return": 21.4, "3Y Return": 17.8, "Expense Ratio": 0.62, "AUM (Cr)": 48200, "Min SIP": 100},
    {"Fund Name": "DSP Flexi Cap Fund", "Category": "Equity", "Sub-Category": "Flexi Cap", "Rating": 4, "1Y Return": 20.8, "3Y Return": 17.1, "Expense Ratio": 0.72, "AUM (Cr)": 14800, "Min SIP": 500},
    {"Fund Name": "HDFC Flexi Cap Fund", "Category": "Equity", "Sub-Category": "Flexi Cap", "Rating": 5, "1Y Return": 26.4, "3Y Return": 22.8, "Expense Ratio": 0.83, "AUM (Cr)": 58400, "Min SIP": 100},
    {"Fund Name": "HDFC Mid-Cap Opportunities", "Category": "Equity", "Sub-Category": "Mid Cap", "Rating": 5, "1Y Return": 28.6, "3Y Return": 24.2, "Expense Ratio": 0.78, "AUM (Cr)": 71200, "Min SIP": 100},
    {"Fund Name": "Axis Mid Cap Fund", "Category": "Equity", "Sub-Category": "Mid Cap", "Rating": 5, "1Y Return": 30.4, "3Y Return": 26.1, "Expense Ratio": 0.54, "AUM (Cr)": 28400, "Min SIP": 500},
    {"Fund Name": "Nippon India Mid Cap", "Category": "Equity", "Sub-Category": "Mid Cap", "Rating": 4, "1Y Return": 26.2, "3Y Return": 22.4, "Expense Ratio": 0.82, "AUM (Cr)": 42800, "Min SIP": 100},
    {"Fund Name": "Kotak Emerging Equity", "Category": "Equity", "Sub-Category": "Mid Cap", "Rating": 4, "1Y Return": 25.8, "3Y Return": 21.6, "Expense Ratio": 0.41, "AUM (Cr)": 44100, "Min SIP": 100},
    {"Fund Name": "SBI Small Cap Fund", "Category": "Equity", "Sub-Category": "Small Cap", "Rating": 5, "1Y Return": 34.8, "3Y Return": 28.6, "Expense Ratio": 0.69, "AUM (Cr)": 38600, "Min SIP": 500},
    {"Fund Name": "HDFC Small Cap Fund", "Category": "Equity", "Sub-Category": "Small Cap", "Rating": 4, "1Y Return": 32.4, "3Y Return": 26.8, "Expense Ratio": 0.62, "AUM (Cr)": 32400, "Min SIP": 100},
    {"Fund Name": "Nippon India Small Cap", "Category": "Equity", "Sub-Category": "Small Cap", "Rating": 4, "1Y Return": 35.2, "3Y Return": 29.4, "Expense Ratio": 0.87, "AUM (Cr)": 48200, "Min SIP": 100},
    {"Fund Name": "UTI Nifty 50 Index Fund", "Category": "Equity", "Sub-Category": "Index Fund", "Rating": 5, "1Y Return": 18.6, "3Y Return": 15.8, "Expense Ratio": 0.18, "AUM (Cr)": 19800, "Min SIP": 500},
    {"Fund Name": "Navi Nifty 50 Index Fund", "Category": "Equity", "Sub-Category": "Index Fund", "Rating": 4, "1Y Return": 18.4, "3Y Return": 15.6, "Expense Ratio": 0.06, "AUM (Cr)": 8400, "Min SIP": 10},
    {"Fund Name": "ICICI Pru Nifty 50 Index", "Category": "Equity", "Sub-Category": "Index Fund", "Rating": 5, "1Y Return": 18.5, "3Y Return": 15.7, "Expense Ratio": 0.17, "AUM (Cr)": 24600, "Min SIP": 100},
    {"Fund Name": "ABSL Liquid Fund", "Category": "Debt", "Sub-Category": "Liquid", "Rating": 4, "1Y Return": 7.2, "3Y Return": 6.4, "Expense Ratio": 0.21, "AUM (Cr)": 52400, "Min SIP": 1000},
    {"Fund Name": "HDFC Liquid Fund", "Category": "Debt", "Sub-Category": "Liquid", "Rating": 5, "1Y Return": 7.4, "3Y Return": 6.6, "Expense Ratio": 0.20, "AUM (Cr)": 68200, "Min SIP": 500},
    {"Fund Name": "SBI Liquid Fund", "Category": "Debt", "Sub-Category": "Liquid", "Rating": 4, "1Y Return": 7.1, "3Y Return": 6.3, "Expense Ratio": 0.21, "AUM (Cr)": 72800, "Min SIP": 500},
    {"Fund Name": "ICICI Pru Short Term Fund", "Category": "Debt", "Sub-Category": "Short Duration", "Rating": 4, "1Y Return": 7.8, "3Y Return": 6.9, "Expense Ratio": 0.48, "AUM (Cr)": 18600, "Min SIP": 1000},
    {"Fund Name": "HDFC Corporate Bond Fund", "Category": "Debt", "Sub-Category": "Corporate Bond", "Rating": 5, "1Y Return": 8.4, "3Y Return": 7.2, "Expense Ratio": 0.35, "AUM (Cr)": 28400, "Min SIP": 500},
    {"Fund Name": "ICICI Pru Balanced Adv", "Category": "Hybrid", "Sub-Category": "Balanced Advantage", "Rating": 5, "1Y Return": 14.8, "3Y Return": 13.2, "Expense Ratio": 0.84, "AUM (Cr)": 48600, "Min SIP": 100},
    {"Fund Name": "HDFC Balanced Advantage", "Category": "Hybrid", "Sub-Category": "Balanced Advantage", "Rating": 5, "1Y Return": 16.4, "3Y Return": 14.8, "Expense Ratio": 0.76, "AUM (Cr)": 82400, "Min SIP": 100},
    {"Fund Name": "SBI Equity Hybrid Fund", "Category": "Hybrid", "Sub-Category": "Aggressive Hybrid", "Rating": 4, "1Y Return": 18.2, "3Y Return": 15.6, "Expense Ratio": 0.88, "AUM (Cr)": 62800, "Min SIP": 500},
    {"Fund Name": "Nippon India ETF Nifty 50", "Category": "ETF", "Sub-Category": "Large Cap ETF", "Rating": 4, "1Y Return": 18.3, "3Y Return": 15.6, "Expense Ratio": 0.05, "AUM (Cr)": 12800, "Min SIP": 0},
    {"Fund Name": "SBI Nifty 50 ETF", "Category": "ETF", "Sub-Category": "Large Cap ETF", "Rating": 4, "1Y Return": 18.4, "3Y Return": 15.7, "Expense Ratio": 0.07, "AUM (Cr)": 168400, "Min SIP": 0},
    {"Fund Name": "Motilal Oswal Midcap 150 ETF", "Category": "ETF", "Sub-Category": "Mid Cap ETF", "Rating": 3, "1Y Return": 25.6, "3Y Return": 21.4, "Expense Ratio": 0.09, "AUM (Cr)": 4200, "Min SIP": 0},
]

SUBCATEGORY_MAP = {
    "Equity": ["All", "Large Cap", "Mid Cap", "Small Cap", "Flexi Cap", "Focused", "Index Fund", "ELSS"],
    "Debt": ["All", "Liquid", "Short Duration", "Corporate Bond", "Gilt", "Dynamic Bond"],
    "Hybrid": ["All", "Balanced Advantage", "Aggressive Hybrid", "Conservative Hybrid", "Arbitrage"],
    "ETF": ["All", "Large Cap ETF", "Mid Cap ETF", "Small Cap ETF", "Sectoral ETF"],
    "Index": ["All", "Nifty 50", "Nifty Next 50", "Midcap 150", "Smallcap 250"],
}

CATEGORY_GROUPS = {
    "Large Cap": ["Mirae Asset Large Cap Fund", "Axis Bluechip Fund", "SBI Bluechip Fund",
                  "HDFC Top 100 Fund", "ICICI Pru Bluechip Fund", "Nippon India Large Cap Fund"],
    "Flexi Cap": ["Parag Parikh Flexi Cap Fund", "Canara Robeco Flexi Cap Fund", "ABSL Flexi Cap Fund",
                  "DSP Flexi Cap Fund", "UTI Flexi Cap Fund", "HDFC Flexi Cap Fund"],
    "Mid Cap": ["HDFC Mid-Cap Opportunities Fund", "Kotak Emerging Equity", "Axis Mid Cap Fund", "DSP Midcap Fund"],
    "Small Cap": ["SBI Small Cap Fund", "Nippon India Small Cap Fund", "HDFC Small Cap Fund",
                  "Axis Small Cap Fund", "Kotak Small Cap Fund"],
}

STOCK_INFO = {
    "Bharti Airtel": {
        "full_name": "Bharti Airtel Limited",
        "sector": "Telecom", "industry": "Wireless Telecom Services", "market_cap": "Large Cap", "nse_symbol": "BHARTIARTL",
        "description": "India's largest telecom operator by revenue with 500M+ subscribers. Leading 5G rollout and growing home broadband (Xstream) and enterprise segments.",
    },
    "Infosys": {
        "full_name": "Infosys Limited",
        "sector": "Information Technology", "industry": "IT Services & Consulting", "market_cap": "Large Cap", "nse_symbol": "INFY",
        "description": "India's 2nd largest IT services company. Revenue majority from USA & Europe. Strong in digital transformation, cloud migration, and AI-led services.",
    },
    "HDFC Bank": {
        "full_name": "HDFC Bank Limited",
        "sector": "Banking & Finance", "industry": "Private Sector Bank", "market_cap": "Large Cap", "nse_symbol": "HDFCBANK",
        "description": "India's largest private sector bank by assets. Merged with HDFC Ltd in 2023. Largest constituent of Nifty 50 & Sensex by weight.",
    },
    "Reliance Industries": {
        "full_name": "Reliance Industries Limited",
        "sector": "Conglomerate", "industry": "Oil, Telecom & Retail", "market_cap": "Large Cap", "nse_symbol": "RELIANCE",
        "description": "India's largest company by market cap. Operates O2C (refining/petrochemicals), Jio telecom, Reliance Retail, and new energy businesses.",
    },
    "TCS": {
        "full_name": "Tata Consultancy Services Limited",
        "sector": "Information Technology", "industry": "IT Services & Consulting", "market_cap": "Large Cap", "nse_symbol": "TCS",
        "description": "India's largest IT company and Tata Group flagship. Serves BFSI, retail, telecom, and manufacturing globally. Consistent dividend payer.",
    },
    "ICICI Bank": {
        "full_name": "ICICI Bank Limited",
        "sector": "Banking & Finance", "industry": "Private Sector Bank", "market_cap": "Large Cap", "nse_symbol": "ICICIBANK",
        "description": "India's 2nd largest private bank. Strong retail banking franchise with robust digital channels (iMobile). Healthy asset quality post-2020 cleanup.",
    },
    "Axis Bank": {
        "full_name": "Axis Bank Limited",
        "sector": "Banking & Finance", "industry": "Private Sector Bank", "market_cap": "Large Cap", "nse_symbol": "AXISBANK",
        "description": "India's 3rd largest private sector bank. Acquired Citi India's consumer business in 2023. Focus on premium retail and corporate banking.",
    },
    "Maruti Suzuki": {
        "full_name": "Maruti Suzuki India Limited",
        "sector": "Automobile", "industry": "Passenger Vehicles", "market_cap": "Large Cap", "nse_symbol": "MARUTI",
        "description": "India's largest passenger vehicle manufacturer with ~40% market share. Joint venture with Suzuki Motor Corp. Strong rural distribution network.",
    },
    "Asian Paints": {
        "full_name": "Asian Paints Limited",
        "sector": "Consumer Goods", "industry": "Paints & Coatings", "market_cap": "Large Cap", "nse_symbol": "ASIANPAINT",
        "description": "India's largest paints company with ~35% market share. Premium brand presence across decorative and industrial coatings. Expanding into home décor.",
    },
    "Bajaj Finance": {
        "full_name": "Bajaj Finance Limited",
        "sector": "Banking & Finance", "industry": "Non-Banking Financial Company", "market_cap": "Large Cap", "nse_symbol": "BAJFINANCE",
        "description": "India's largest NBFC by AUM. Strong in consumer durables loans, home loans, SME lending. Known for rapid digital lending and deep cross-sell.",
    },
    "Wipro": {
        "full_name": "Wipro Limited",
        "sector": "Information Technology", "industry": "IT Services & Consulting", "market_cap": "Large Cap", "nse_symbol": "WIPRO",
        "description": "India's 3rd largest IT services company. Revenue split between IT services and consumer care (Santoor, Glucon-D). Focus on consulting-led deals.",
    },
    "HUL": {
        "full_name": "Hindustan Unilever Limited",
        "sector": "Consumer Goods", "industry": "FMCG — Personal & Home Care", "market_cap": "Large Cap", "nse_symbol": "HINDUNILVR",
        "description": "India's largest FMCG company. Portfolio includes Surf Excel, Lux, Dove, Knorr, Horlicks. Subsidiary of Unilever Plc. Dominant rural distribution.",
    },
    "Sun Pharma": {
        "full_name": "Sun Pharmaceutical Industries Limited",
        "sector": "Healthcare", "industry": "Pharmaceuticals", "market_cap": "Large Cap", "nse_symbol": "SUNPHARMA",
        "description": "India's largest pharma company by revenue. Leading presence in US generics and specialty drugs (Ilumya, Cequa). Acquired Ranbaxy in 2015.",
    },
    "L&T": {
        "full_name": "Larsen & Toubro Limited",
        "sector": "Infrastructure & Industrials", "industry": "Engineering & Construction", "market_cap": "Large Cap", "nse_symbol": "LT",
        "description": "India's largest engineering & construction conglomerate. Operates across infrastructure, defence, IT (LTIMindtree), financial services, and realty.",
    },
    "Kotak Mahindra Bank": {
        "full_name": "Kotak Mahindra Bank Limited",
        "sector": "Banking & Finance", "industry": "Private Sector Bank", "market_cap": "Large Cap", "nse_symbol": "KOTAKBANK",
        "description": "India's 4th largest private bank by assets. Founded by Uday Kotak. Known for strong capital ratios, premium savings accounts, and low NPAs.",
    },
    "Titan": {
        "full_name": "Titan Company Limited",
        "sector": "Consumer Goods", "industry": "Jewellery & Watches", "market_cap": "Large Cap", "nse_symbol": "TITAN",
        "description": "Tata Group company. India's largest branded jewellery player (Tanishq) and watch brand (Titan, Fastrack). Expanding into eyewear and fragrances.",
    },
    "Nestle India": {
        "full_name": "Nestle India Limited",
        "sector": "Consumer Goods", "industry": "FMCG — Food & Beverages", "market_cap": "Large Cap", "nse_symbol": "NESTLEIND",
        "description": "Indian subsidiary of Nestle SA. Flagship product Maggi noodles holds ~60% market share. Strong in KitKat, Munch, Milkmaid and coffee (Nescafé).",
    },
    "ITC": {
        "full_name": "ITC Limited",
        "sector": "Consumer Goods", "industry": "Cigarettes, FMCG & Hotels", "market_cap": "Large Cap", "nse_symbol": "ITC",
        "description": "India's largest cigarette manufacturer (Gold Flake, Classic). Diversified into FMCG foods (Aashirvaad, Sunfeast), hotels, agribusiness, and paper.",
    },
    "Power Grid": {
        "full_name": "Power Grid Corporation of India Limited",
        "sector": "Utilities", "industry": "Power Transmission", "market_cap": "Large Cap", "nse_symbol": "POWERGRID",
        "description": "Central PSU that owns and operates India's inter-state power transmission network. Regulated returns business with 85%+ utilisation. High dividend yield.",
    },
    "NTPC": {
        "full_name": "NTPC Limited",
        "sector": "Utilities", "industry": "Power Generation", "market_cap": "Large Cap", "nse_symbol": "NTPC",
        "description": "India's largest power generating company (Navratna PSU). ~70 GW installed capacity. Rapidly expanding renewable energy portfolio targeting 60 GW by 2032.",
    },
    "HCL Technologies": {
        "full_name": "HCL Technologies Limited",
        "sector": "Information Technology", "industry": "IT Services & Products", "market_cap": "Large Cap", "nse_symbol": "HCLTECH",
        "description": "India's 3rd largest IT company. Known for engineering R&D services and product-IP business (HCL Software). Strong deal wins in cloud and digital.",
    },
    "Tech Mahindra": {
        "full_name": "Tech Mahindra Limited",
        "sector": "Information Technology", "industry": "IT Services & Consulting", "market_cap": "Large Cap", "nse_symbol": "TECHM",
        "description": "Mahindra Group IT arm. Specialist in telecom software (5G), digital transformation, and BPO. Pursuing margin recovery after scale-up investments.",
    },
    "HDFC Life Insurance": {
        "full_name": "HDFC Life Insurance Company Limited",
        "sector": "Banking & Finance", "industry": "Life Insurance", "market_cap": "Large Cap", "nse_symbol": "HDFCLIFE",
        "description": "Joint venture between HDFC Bank and Standard Life. India's 2nd largest private life insurer. Strong annuity and protection product mix.",
    },
    "HDFC AMC": {
        "full_name": "HDFC Asset Management Company Limited",
        "sector": "Banking & Finance", "industry": "Asset Management", "market_cap": "Mid Cap", "nse_symbol": "HDFCAMC",
        "description": "India's 2nd largest AMC by AUM (~₹7L Cr). Joint venture with abrdn (formerly Standard Life Aberdeen). High margins, strong brand, and growing SIP book.",
    },
    "Bajaj Finserv": {
        "full_name": "Bajaj Finserv Limited",
        "sector": "Banking & Finance", "industry": "Financial Services Holding Co.", "market_cap": "Large Cap", "nse_symbol": "BAJAJFINSV",
        "description": "Holding company for Bajaj Finance (NBFC), Bajaj Allianz Life, and Bajaj Allianz General Insurance. Considered a surrogate for Bajaj Finance.",
    },
    "Bajaj Auto": {
        "full_name": "Bajaj Auto Limited",
        "sector": "Automobile", "industry": "2-Wheeler & 3-Wheeler", "market_cap": "Large Cap", "nse_symbol": "BAJAJ-AUTO",
        "description": "World's largest 3-wheeler maker. Strong in export markets (Africa, Latin America). Growing premium motorcycles (Pulsar, Dominar) and EV (Chetak).",
    },
    "Tata Motors": {
        "full_name": "Tata Motors Limited",
        "sector": "Automobile", "industry": "Passenger & Commercial Vehicles", "market_cap": "Large Cap", "nse_symbol": "TATAMOTORS",
        "description": "Tata Group auto company. Owns Jaguar Land Rover (luxury EVs). India's leading electric car maker. Strong domestic CV and passenger vehicle franchise.",
    },
    "Tata Steel": {
        "full_name": "Tata Steel Limited",
        "sector": "Metals & Mining", "industry": "Steel Manufacturing", "market_cap": "Large Cap", "nse_symbol": "TATASTEEL",
        "description": "India's 2nd largest steel producer. Owns Tata Steel Netherlands (Ijmuiden) and British Steel (acquired). Committed to net-zero steel by 2045.",
    },
    "Tata Power": {
        "full_name": "Tata Power Company Limited",
        "sector": "Utilities", "industry": "Power Generation & Distribution", "market_cap": "Mid Cap", "nse_symbol": "TATAPOWER",
        "description": "Integrated power company — generation (conventional + renewable), transmission, and distribution. India's largest solar EPC and clean energy player.",
    },
    "Tata Consultancy Services": {
        "full_name": "Tata Consultancy Services Limited",
        "sector": "Information Technology", "industry": "IT Services & Consulting", "market_cap": "Large Cap", "nse_symbol": "TCS",
        "description": "India's largest IT company and Tata Group flagship. Serves BFSI, retail, telecom, and manufacturing globally. Consistent dividend payer with ₹2L+ Cr market cap.",
    },
    "Larsen & Toubro": {
        "full_name": "Larsen & Toubro Limited",
        "sector": "Infrastructure & Industrials", "industry": "Engineering & Construction", "market_cap": "Large Cap", "nse_symbol": "LT",
        "description": "India's largest engineering & construction conglomerate. Operates across infrastructure, defence, IT (LTIMindtree), financial services, and green hydrogen.",
    },
    "Adani Ports": {
        "full_name": "Adani Ports and Special Economic Zone Limited",
        "sector": "Infrastructure", "industry": "Ports & Logistics", "market_cap": "Large Cap", "nse_symbol": "ADANIPORTS",
        "description": "India's largest private port operator handling ~360 MT of cargo. Expanding into logistics (GRAIL) and international ports. Nifty 50 constituent.",
    },
    "Adani Enterprises": {
        "full_name": "Adani Enterprises Limited",
        "sector": "Conglomerate", "industry": "Mining, Airports & New Energy", "market_cap": "Large Cap", "nse_symbol": "ADANIENT",
        "description": "Adani Group flagship and incubator for new businesses — airports, green hydrogen, data centres, roads, and copper. The mother ship of the Adani ecosystem.",
    },
    "UltraTech Cement": {
        "full_name": "UltraTech Cement Limited",
        "sector": "Materials", "industry": "Cement Manufacturing", "market_cap": "Large Cap", "nse_symbol": "ULTRACEMCO",
        "description": "India's largest cement company with ~140 MT capacity. Aditya Birla Group subsidiary. Acquiring India Cements. Dominant in grey, white cement, and concrete.",
    },
    "Grasim Industries": {
        "full_name": "Grasim Industries Limited",
        "sector": "Materials & Conglomerate", "industry": "Cement, Chemicals & Paints", "market_cap": "Large Cap", "nse_symbol": "GRASIM",
        "description": "Aditya Birla Group flagship. Parent of UltraTech Cement. Launching paints business (Birla Opus). Diversified into chlor-alkali and viscose staple fibre.",
    },
    "JSW Steel": {
        "full_name": "JSW Steel Limited",
        "sector": "Metals & Mining", "industry": "Steel Manufacturing", "market_cap": "Large Cap", "nse_symbol": "JSWSTEEL",
        "description": "India's largest steel producer by capacity (~28 MT). JSW Group company (O.P. Jindal family). Expanding through greenfield and international acquisitions.",
    },
    "Hindalco": {
        "full_name": "Hindalco Industries Limited",
        "sector": "Metals & Mining", "industry": "Aluminium & Copper", "market_cap": "Large Cap", "nse_symbol": "HINDALCO",
        "description": "Aditya Birla Group metals arm. Owns Novelis (world's largest aluminium rolling co.). India's only integrated aluminium and copper producer.",
    },
    "Coal India": {
        "full_name": "Coal India Limited",
        "sector": "Energy", "industry": "Coal Mining (PSU)", "market_cap": "Large Cap", "nse_symbol": "COALINDIA",
        "description": "World's largest coal mining company and a Navratna PSU. Produces ~80% of India's domestic coal. High dividend payer with near-monopoly status.",
    },
    "ONGC": {
        "full_name": "Oil & Natural Gas Corporation Limited",
        "sector": "Energy", "industry": "Oil & Gas Exploration (PSU)", "market_cap": "Large Cap", "nse_symbol": "ONGC",
        "description": "India's largest oil & gas producer and a Navratna PSU. Operates onshore and offshore blocks. Subsidiary HPCL adds downstream refining exposure.",
    },
    "Indian Oil Corporation": {
        "full_name": "Indian Oil Corporation Limited",
        "sector": "Energy", "industry": "Oil Refining & Marketing (PSU)", "market_cap": "Large Cap", "nse_symbol": "IOC",
        "description": "India's largest oil company by revenue. Runs 11 refineries, the largest pipeline network, and the Indian Oil petrol pump chain. Maharatna PSU.",
    },
    "BPCL": {
        "full_name": "Bharat Petroleum Corporation Limited",
        "sector": "Energy", "industry": "Oil Refining & Marketing (PSU)", "market_cap": "Large Cap", "nse_symbol": "BPCL",
        "description": "Navratna PSU oil marketing company. Owns Bharat Petroleum brand petrol pumps (19,000+). Government privatisation candidate — outcome still uncertain.",
    },
    "Cipla": {
        "full_name": "Cipla Limited",
        "sector": "Healthcare", "industry": "Pharmaceuticals", "market_cap": "Large Cap", "nse_symbol": "CIPLA",
        "description": "Pioneer of affordable AIDS drugs. Strong in respiratory (Symbicort copy), oncology, and consumer wellness. Significant US generics and domestic branded business.",
    },
    "Dr Reddy's": {
        "full_name": "Dr Reddy's Laboratories Limited",
        "sector": "Healthcare", "industry": "Pharmaceuticals", "market_cap": "Large Cap", "nse_symbol": "DRREDDY",
        "description": "India's 2nd largest pharma company. Heavy exposure to US generics (30% revenue). Growing specialty pipeline (Sputnik V, gRevlimid). Acquired Mayne Pharma products.",
    },
    "Divi's Laboratories": {
        "full_name": "Divi's Laboratories Limited",
        "sector": "Healthcare", "industry": "API Manufacturing", "market_cap": "Large Cap", "nse_symbol": "DIVISLAB",
        "description": "World's largest manufacturer of select APIs and intermediates. Key supplier to global innovators (Roche, Pfizer). Clean FDA track record — a key moat.",
    },
    "Eicher Motors": {
        "full_name": "Eicher Motors Limited",
        "sector": "Automobile", "industry": "Premium Motorcycles & CVs", "market_cap": "Large Cap", "nse_symbol": "EICHERMOT",
        "description": "Owner of Royal Enfield (world's largest premium motorcycle brand). JV with Volvo for commercial vehicles (VE Commercial Vehicles). Premium positioning = high margins.",
    },
    "Hero MotoCorp": {
        "full_name": "Hero MotoCorp Limited",
        "sector": "Automobile", "industry": "2-Wheeler Manufacturer", "market_cap": "Large Cap", "nse_symbol": "HEROMOTOCO",
        "description": "World's largest 2-wheeler manufacturer by volume. Dominant in rural India. EV foray with Vida. Loss of Honda JV in 2010 forced independent product development.",
    },
    "Mahindra & Mahindra": {
        "full_name": "Mahindra & Mahindra Limited",
        "sector": "Automobile & Conglomerate", "industry": "SUVs, Tractors & EVs", "market_cap": "Large Cap", "nse_symbol": "M&M",
        "description": "India's #1 SUV maker (Scorpio, XUV, Thar). World's largest tractor company. EV portfolio (XEV 9e, BE 6). Subsidiaries in IT (Tech M), finance (MMFSL), and aerospace.",
    },
    "Interglobe Aviation": {
        "full_name": "InterGlobe Aviation Limited (IndiGo)",
        "sector": "Consumer Services", "industry": "Low-Cost Aviation", "market_cap": "Large Cap", "nse_symbol": "INDIGO",
        "description": "India's largest airline by market share (~60%). Operates the world's largest fleet of Airbus A320 family aircraft on order. Profitable through cost discipline.",
    },
    "Zomato": {
        "full_name": "Zomato Limited",
        "sector": "Consumer Services", "industry": "Food Delivery & Quick Commerce", "market_cap": "Large Cap", "nse_symbol": "ZOMATO",
        "description": "India's largest food delivery platform. Owns Blinkit (quick commerce). Now profitable at EBITDA level. Added to Nifty 50 in 2024 — first new-age tech to enter.",
    },
    "Nykaa": {
        "full_name": "FSN E-Commerce Ventures Limited (Nykaa)",
        "sector": "Consumer Services", "industry": "Beauty & Fashion E-commerce", "market_cap": "Mid Cap", "nse_symbol": "NYKAA",
        "description": "India's leading beauty & personal care platform (online + offline). Brand Nykaa commands strong loyalty. Expanding into fashion (Nykaa Fashion) and B2B.",
    },
    "Policybazaar": {
        "full_name": "PB Fintech Limited (Policybazaar)",
        "sector": "Banking & Finance", "industry": "Online Insurance Marketplace", "market_cap": "Mid Cap", "nse_symbol": "POLICYBZR",
        "description": "India's largest online insurance marketplace. Also runs Paisabazaar (loans & credit). Growing into issuing policies directly (PB Partners). Now profitable.",
    },
    "Dixon Technologies": {
        "full_name": "Dixon Technologies (India) Limited",
        "sector": "Industrials", "industry": "Electronics Manufacturing Services", "market_cap": "Mid Cap", "nse_symbol": "DIXON",
        "description": "India's largest EMS company. Manufactures TVs, washing machines, phones (Motorola, Samsung). Major beneficiary of PLI schemes for electronics. Rapid revenue growth.",
    },
    "Havells India": {
        "full_name": "Havells India Limited",
        "sector": "Industrials", "industry": "Consumer Electricals & Electronics", "market_cap": "Large Cap", "nse_symbol": "HAVELLS",
        "description": "India's leading consumer electricals brand. Products: fans, cables, switchgear, lights, appliances. Lloyd (AC & TV brand) drives premiumisation. Debt-free.",
    },
    "Pidilite Industries": {
        "full_name": "Pidilite Industries Limited",
        "sector": "Materials", "industry": "Adhesives & Sealants", "market_cap": "Large Cap", "nse_symbol": "PIDILITIND",
        "description": "Maker of Fevicol — India's most trusted adhesive brand. Near-monopoly in construction adhesives (Dr Fixit). Expansion into waterproofing and art materials.",
    },
    "SBI": {
        "full_name": "State Bank of India",
        "sector": "Banking & Finance", "industry": "Public Sector Bank", "market_cap": "Large Cap", "nse_symbol": "SBIN",
        "description": "India's largest bank by assets, branches, and employees. Navratna PSU. Massive retail franchise with 22,000+ branches. Digital banking via YONO app.",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def stars(n: int) -> str:
    return "★" * n + "☆" * (5 - n)


def fmt_cr(v: float) -> str:
    if v >= 1e5:
        return f"₹{v/1e5:.1f}L Cr"
    return f"₹{v:,.0f} Cr"


def _H(s: str) -> str:
    return " ".join(line.strip() for line in s.splitlines() if line.strip())



# ═══════════════════════════════════════════════════════════════════════════
# API FETCH (all cached)
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_amfi_nav():
    try:
        r = requests.get("https://www.amfiindia.com/spages/NAVAll.txt", timeout=15)
        r.raise_for_status()
        rows = []
        for line in r.text.splitlines():
            parts = line.strip().split(";")
            if len(parts) >= 5 and parts[0].strip().isdigit():
                try:
                    rows.append({
                        "Scheme Code": parts[0].strip(),
                        "Scheme Name": parts[3].strip(),
                        "NAV": float(parts[4].strip()),
                        "Date": parts[5].strip() if len(parts) > 5 else "",
                    })
                except (ValueError, IndexError):
                    pass
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_mfapi_list():
    try:
        r = requests.get("https://api.mfapi.in/mf", timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fund_nav_history(scheme_code: str):
    try:
        r = requests.get(f"https://api.mfapi.in/mf/{scheme_code}", timeout=15)
        r.raise_for_status()
        data = r.json()
        nav_data = data.get("data", [])
        df = pd.DataFrame(nav_data)
        if df.empty:
            return pd.DataFrame()
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
        df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
        df = df.dropna().sort_values("date").reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame()


def calc_return(df: pd.DataFrame, days: int) -> float | None:
    if df.empty or len(df) < 2:
        return None
    cutoff = df["date"].max() - timedelta(days=days)
    old = df[df["date"] <= cutoff]
    if old.empty:
        return None
    old_nav = float(old.iloc[-1]["nav"])
    new_nav = float(df.iloc[-1]["nav"])
    if old_nav <= 0:
        return None
    return (new_nav - old_nav) / old_nav * 100


# ═══════════════════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="padding:1.2rem 0 0.4rem;">
  <div style="font-size:1.9rem;font-weight:800;
       background:linear-gradient(90deg,#f0f0ff 30%,#8b5cf6 70%,#10b981);
       -webkit-background-clip:text;background-clip:text;color:transparent;line-height:1.1;">
    MF Research Hub
  </div>
  <div style="font-size:0.68rem;color:#6b7280;letter-spacing:0.18em;
       text-transform:uppercase;margin-top:4px;">
    Stock Search · Overlap Checker · Screener · Fund Compare · Free Data · No Login
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="font-size:0.72rem;color:#6b7280;margin-bottom:0.8rem;">⚠️ Holdings data sourced from AMFI factsheets (updated monthly). NAV data via mfapi.in & AMFI. Not investment advice.</div>', unsafe_allow_html=True)

# ── Market Mood Banner ─────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_market_mood():
    try:
        import yfinance as yf
        ticker = yf.Ticker("^NSEI")
        hist = ticker.history(period="2d")
        if hist.empty or len(hist) < 2:
            return None
        prev_close = float(hist["Close"].iloc[-2])
        curr_close = float(hist["Close"].iloc[-1])
        change = curr_close - prev_close
        pct = change / prev_close * 100
        return {"price": curr_close, "change": change, "pct": pct}
    except Exception:
        return None

_mood = fetch_market_mood()
if _mood:
    _c = "#10b981" if _mood["pct"] >= 0 else "#f87171"
    _arrow = "▲" if _mood["pct"] >= 0 else "▼"
    _mood_label = "Bullish" if _mood["pct"] > 0.5 else ("Bearish" if _mood["pct"] < -0.5 else "Neutral")
    _mood_emoji = "🟢" if _mood["pct"] > 0.5 else ("🔴" if _mood["pct"] < -0.5 else "🟡")
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1.2rem;background:rgba(255,255,255,0.03);
         border:1px solid rgba(139,92,246,0.18);border-radius:12px;padding:0.55rem 1.1rem;
         margin-bottom:1rem;flex-wrap:wrap;">
      <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-size:0.72rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.1em;">Market Mood</span>
        <span style="font-size:0.9rem;">{_mood_emoji} <b style="color:{_c};">{_mood_label}</b></span>
      </div>
      <div style="width:1px;height:22px;background:rgba(139,92,246,0.2);"></div>
      <div style="font-size:0.82rem;color:#a0a0c0;">
        NIFTY 50 &nbsp;
        <b style="color:#f0f0ff;">{_mood['price']:,.1f}</b>
        &nbsp;<span style="color:{_c};">{_arrow} {abs(_mood['change']):.1f} ({abs(_mood['pct']):.2f}%)</span>
      </div>
      <div style="margin-left:auto;font-size:0.65rem;color:#4b5563;">Live · 5-min cache</div>
    </div>
    """, unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────
if "ss_active_stock" not in st.session_state:
    st.session_state.ss_active_stock = None

# ═══════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Stock Search",
    "🔀 Overlap Checker",
    "🎛️ Fund Screener",
    "⚖️ Fund Compare",
])


# ───────────────────────────────────────────────────────────────────────────
# TAB 1 — STOCK SEARCH
# ───────────────────────────────────────────────────────────────────────────
with tab1:
    stock_names = list(STOCK_HOLDINGS.keys())

    # ── Search bar ────────────────────────────────────────────────────────
    t1_left, t1_right = st.columns([5, 1])
    with t1_left:
        stock_query = st.text_input(
            "Search stock",
            placeholder="Type a stock name… e.g. Infosys, HDFC Bank, L&T",
            label_visibility="collapsed",
            key="stock_search_input",
        )
    with t1_right:
        if st.button("✕ Clear", use_container_width=True, key="stock_clear_btn"):
            st.session_state.ss_active_stock = None
            st.rerun()

    # ── Live suggestion pills ─────────────────────────────────────────────
    query_lower = stock_query.strip().lower()
    if query_lower:
        suggestions = [s for s in stock_names if query_lower in s.lower()]
        if not suggestions:
            suggestions = difflib.get_close_matches(stock_query.strip(), stock_names, n=6, cutoff=0.3)
        pill_label = "Matching stocks:" if suggestions else None
    else:
        suggestions = stock_names
        pill_label = "Popular stocks — click to explore:"

    if suggestions and pill_label:
        st.markdown(
            f'<div style="font-size:0.68rem;color:#6b7280;margin:0.6rem 0 0.3rem;">{pill_label}</div>',
            unsafe_allow_html=True,
        )
        pill_batch = suggestions[:10]
        n_cols = min(len(pill_batch), 5)
        pill_cols = st.columns(n_cols)
        for idx, sug in enumerate(pill_batch):
            with pill_cols[idx % n_cols]:
                if st.button(sug, key=f"pill_{sug}", use_container_width=True):
                    st.session_state.ss_active_stock = sug
                    st.rerun()
    elif query_lower and not suggestions:
        st.warning(f"No match for '{stock_query}'. Try: " + ", ".join(stock_names[:6]))

    # ── Resolve active stock ──────────────────────────────────────────────
    active_stock = st.session_state.ss_active_stock
    if not active_stock and query_lower:
        sub_matches = [s for s in stock_names if query_lower in s.lower()]
        if not sub_matches:
            sub_matches = difflib.get_close_matches(stock_query.strip(), stock_names, n=1, cutoff=0.4)
        if sub_matches:
            active_stock = sub_matches[0]

    # ── Results ───────────────────────────────────────────────────────────
    if active_stock:
        st.markdown("<hr style='border:none;border-top:1px solid rgba(139,92,246,0.15);margin:0.8rem 0;'>",
                    unsafe_allow_html=True)

        info = STOCK_INFO.get(active_stock, {})
        full_name = info.get("full_name", active_stock)

        # Stock name header + ⓘ popover
        hdr_col, info_col = st.columns([6, 1])
        with hdr_col:
            st.markdown(
                f'<div style="margin-bottom:0.2rem;">'
                f'<div style="font-size:1.5rem;font-weight:800;color:#f0f0ff;line-height:1.2;">{full_name}</div>'
                f'<div style="font-size:0.72rem;color:#6b7280;margin-top:4px;">'
                f'{info.get("sector","—")} &nbsp;·&nbsp; {info.get("industry","—")} &nbsp;·&nbsp; '
                f'{info.get("market_cap","—")} &nbsp;·&nbsp; NSE: <b style="color:#8b5cf6;">{info.get("nse_symbol","—")}</b>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        with info_col:
            with st.popover("ⓘ Info"):
                st.markdown(f"### {full_name}")
                st.markdown(f"**Sector:** {info.get('sector', '—')}")
                st.markdown(f"**Industry:** {info.get('industry', '—')}")
                st.markdown(f"**Market Cap:** {info.get('market_cap', '—')}")
                st.markdown(f"**NSE Symbol:** `{info.get('nse_symbol', '—')}`")
                if info.get("description"):
                    st.markdown("---")
                    st.markdown(info["description"])

        # Category filter
        cat_filter = st.radio(
            "Filter by category",
            ["All", "Equity", "Debt", "Hybrid", "ETF"],
            horizontal=True,
            key="stock_cat_filter",
            label_visibility="collapsed",
        )

        holdings = STOCK_HOLDINGS.get(active_stock, [])
        if cat_filter != "All":
            holdings = [h for h in holdings if h["category"] == cat_filter]

        if not holdings:
            st.info(f"No {cat_filter} funds found holding {active_stock}.")
        else:
            total_funds = len(holdings)
            avg_weightage = sum(h["weightage"] for h in holdings) / total_funds
            top_fund = max(holdings, key=lambda x: x["weightage"])

            # KPI row
            kc1, kc2, kc3 = st.columns(3)
            with kc1:
                st.markdown(_H(f"""
                <div class="mf-kpi-t">
                  <div class="mf-kpi-l">Funds Holding</div>
                  <div class="mf-kpi-v" style="color:#8b5cf6;">{total_funds}</div>
                </div>"""), unsafe_allow_html=True)
            with kc2:
                st.markdown(_H(f"""
                <div class="mf-kpi-t">
                  <div class="mf-kpi-l">Avg Weightage</div>
                  <div class="mf-kpi-v" style="color:#10b981;">{avg_weightage:.1f}%</div>
                </div>"""), unsafe_allow_html=True)
            with kc3:
                st.markdown(_H(f"""
                <div class="mf-kpi-t">
                  <div class="mf-kpi-l">Highest Exposure</div>
                  <div class="mf-kpi-v" style="color:#f59e0b;">{top_fund['weightage']:.1f}%</div>
                  <div style="font-size:0.6rem;color:#6b7280;margin-top:2px;">{top_fund['fund'][:28]}</div>
                </div>"""), unsafe_allow_html=True)

            # Top 5 fund cards
            st.markdown('<div class="sec-lbl" style="margin-top:1.2rem;">Top 5 Funds by Weightage</div>',
                        unsafe_allow_html=True)
            top5 = sorted(holdings, key=lambda x: x["weightage"], reverse=True)[:5]
            for i, h in enumerate(top5, 1):
                bar_w = min(int(h["weightage"] / 15 * 100), 100)
                wt_color = "#10b981" if h["weightage"] >= 5 else ("#f59e0b" if h["weightage"] >= 2 else "#8b5cf6")
                st.markdown(_H(f"""
                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(139,92,246,0.12);
                     border-radius:12px;padding:0.85rem 1.1rem;margin-bottom:8px;">
                  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">
                    <div style="display:flex;align-items:center;gap:10px;flex:1;min-width:0;">
                      <div style="font-size:1.1rem;font-weight:800;color:#8b5cf6;min-width:26px;">#{i}</div>
                      <div style="flex:1;min-width:0;">
                        <div style="font-size:0.88rem;font-weight:700;color:#f0f0ff;white-space:nowrap;
                             overflow:hidden;text-overflow:ellipsis;">{h['fund']}</div>
                        <div style="font-size:0.68rem;color:#6b7280;margin-top:3px;">
                          {h['category']} &nbsp;·&nbsp; AUM {fmt_cr(h['aum_cr'])} &nbsp;·&nbsp; {stars(h['rating'])}
                        </div>
                      </div>
                    </div>
                    <div style="text-align:right;flex-shrink:0;min-width:80px;">
                      <div style="font-size:1.3rem;font-weight:800;color:{wt_color};">{h['weightage']:.1f}%</div>
                      <div style="font-size:0.65rem;color:#6b7280;">{h['trend']}</div>
                    </div>
                  </div>
                  <div style="height:4px;border-radius:2px;background:rgba(255,255,255,0.05);margin-top:8px;">
                    <div style="height:100%;width:{bar_w}%;border-radius:2px;background:{wt_color};opacity:0.75;"></div>
                  </div>
                </div>"""), unsafe_allow_html=True)

            # Bar chart — top 10
            chart_data = sorted(holdings, key=lambda x: x["weightage"], reverse=True)[:10]
            df_chart = pd.DataFrame(chart_data)
            bar_colors = ["#10b981" if w >= 5 else ("#f59e0b" if w >= 2 else "#8b5cf6")
                          for w in df_chart["weightage"]]
            fig = go.Figure(go.Bar(
                x=df_chart["weightage"],
                y=df_chart["fund"],
                orientation="h",
                marker=dict(color=bar_colors),
                text=[f"{v:.1f}%" for v in df_chart["weightage"]],
                textposition="outside",
                textfont=dict(color="#f0f0ff", size=11),
                hovertemplate="%{y}<br>Weightage: %{x:.2f}%<extra></extra>",
            ))
            fig.update_layout(
                paper_bgcolor="#0d0d24", plot_bgcolor="#0d0d24",
                font=dict(color="#f0f0ff", family="Inter, sans-serif"),
                height=max(260, len(chart_data) * 36),
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis=dict(title="Weightage %", gridcolor="rgba(139,92,246,0.08)",
                           tickfont=dict(color="#6b7280")),
                yaxis=dict(autorange="reversed", tickfont=dict(color="#f0f0ff", size=11)),
                showlegend=False,
                title=dict(text=f"Top 10 Funds — {active_stock} Exposure",
                           font=dict(color="#6b7280", size=12)),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # Full table
            st.markdown('<div class="sec-lbl">All Funds Holding This Stock</div>', unsafe_allow_html=True)
            df_table = pd.DataFrame([{
                "Fund Name": h["fund"],
                "Category": h["category"],
                "Weightage %": h["weightage"],
                "Rating": stars(h["rating"]),
                "AUM (Cr)": f"₹{h['aum_cr']:,}",
                "Trend": h["trend"],
            } for h in sorted(holdings, key=lambda x: x["weightage"], reverse=True)])
            st.dataframe(df_table, use_container_width=True, hide_index=True)
            st.caption("Holdings data updated monthly from AMFI factsheets. Weightage as % of fund NAV.")


# ───────────────────────────────────────────────────────────────────────────
# TAB 2 — OVERLAP CHECKER
# ───────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec-lbl">Select two funds to check portfolio overlap</div>', unsafe_allow_html=True)

    fund_list = list(FUND_HOLDINGS.keys())
    oc1, oc2 = st.columns(2)
    with oc1:
        fund_a = st.selectbox("Fund 1", fund_list, index=0, key="overlap_fund_a")
    with oc2:
        fund_b = st.selectbox("Fund 2", fund_list, index=1, key="overlap_fund_b")

    check_btn = st.button("Check Overlap", use_container_width=False, key="overlap_check")

    if fund_a == fund_b:
        st.warning("Please select two different funds.")
    elif check_btn or True:  # always show after selection changes
        fa_holdings = FUND_HOLDINGS[fund_a]["holdings"]
        fb_holdings = FUND_HOLDINGS[fund_b]["holdings"]

        fa_stocks = set(fa_holdings.keys())
        fb_stocks = set(fb_holdings.keys())
        common = fa_stocks & fb_stocks
        total_unique = fa_stocks | fb_stocks

        overlap_pct = len(common) / len(total_unique) * 100 if total_unique else 0

        # Color-coded overlap meter
        if overlap_pct < 30:
            meter_color = "#10b981"
            overlap_label = "Low Overlap — Good diversification"
            label_style = "color:#10b981;"
        elif overlap_pct < 60:
            meter_color = "#f59e0b"
            overlap_label = "Medium Overlap — Some duplication"
            label_style = "color:#f59e0b;"
        else:
            meter_color = "#f87171"
            overlap_label = "High Overlap — Consider switching one fund"
            label_style = "color:#f87171;"

        st.markdown(f"""
        <div class="mf-card" style="border-color:{meter_color}40;">
          <div class="overlap-label" style="{label_style}">{overlap_label}</div>
          <div style="font-size:2.4rem;font-weight:800;color:{meter_color};font-family:'JetBrains Mono',monospace;">
            {overlap_pct:.1f}%
          </div>
          <div style="font-size:0.72rem;color:#6b7280;margin-bottom:0.8rem;">Portfolio Overlap Score</div>
          <div style="height:12px;border-radius:6px;overflow:hidden;background:rgba(255,255,255,0.06);">
            <div style="height:100%;width:{overlap_pct:.1f}%;border-radius:6px;
                 background:{meter_color};transition:width 0.6s ease;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Summary cards
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(_H(f"""
            <div class="mf-kpi-t" style="text-align:center;">
              <div class="mf-kpi-l">{fund_a.split()[0]} {fund_a.split()[1] if len(fund_a.split())>1 else ''}</div>
              <div class="mf-kpi-v" style="color:#8b5cf6;">{len(fa_stocks)}</div>
              <div style="font-size:0.62rem;color:#6b7280;">stocks</div>
            </div>"""), unsafe_allow_html=True)
        with sc2:
            st.markdown(_H(f"""
            <div class="mf-kpi-t" style="text-align:center;border-color:{meter_color}50;">
              <div class="mf-kpi-l">Common</div>
              <div class="mf-kpi-v" style="color:{meter_color};">{len(common)}</div>
              <div style="font-size:0.62rem;color:#6b7280;">shared stocks</div>
            </div>"""), unsafe_allow_html=True)
        with sc3:
            st.markdown(_H(f"""
            <div class="mf-kpi-t" style="text-align:center;">
              <div class="mf-kpi-l">{fund_b.split()[0]} {fund_b.split()[1] if len(fund_b.split())>1 else ''}</div>
              <div class="mf-kpi-v" style="color:#8b5cf6;">{len(fb_stocks)}</div>
              <div style="font-size:0.62rem;color:#6b7280;">stocks</div>
            </div>"""), unsafe_allow_html=True)

        # Common stocks table
        if common:
            st.markdown('<div class="sec-lbl" style="margin-top:1rem;">Common Holdings</div>', unsafe_allow_html=True)
            rows = []
            for stock in sorted(common):
                w1 = fa_holdings.get(stock, 0)
                w2 = fb_holdings.get(stock, 0)
                rows.append({
                    "Stock": stock,
                    f"{fund_a[:20]}...": w1,
                    f"{fund_b[:20]}...": w2,
                    "Combined Exposure %": round(w1 + w2, 2),
                })
            df_overlap = pd.DataFrame(rows).sort_values("Combined Exposure %", ascending=False)

            def highlight_combined(row):
                if row["Combined Exposure %"] > 10:
                    return ["background-color: rgba(248,113,113,0.12)"] * len(row)
                return [""] * len(row)

            st.dataframe(
                df_overlap.style.apply(highlight_combined, axis=1).format(precision=2),
                use_container_width=True,
                hide_index=True,
            )

            # Insight box
            high_overlap_stocks = [r["Stock"] for _, r in df_overlap.iterrows() if r["Combined Exposure %"] > 10]
            fa_er = FUND_HOLDINGS[fund_a].get("expense_ratio", 0)
            fb_er = FUND_HOLDINGS[fund_b].get("expense_ratio", 0)

            insight_parts = [
                f"You hold <b style='color:#8b5cf6;'>{len(common)} common stocks</b> across both funds, "
                f"paying expense ratios of <b style='color:#f59e0b;'>{fa_er:.2f}%</b> + <b style='color:#f59e0b;'>{fb_er:.2f}%</b>."
            ]
            if high_overlap_stocks:
                insight_parts.append(
                    f"<b style='color:#f87171;'>{', '.join(high_overlap_stocks[:4])}</b> "
                    f"{'and more' if len(high_overlap_stocks) > 4 else ''} have combined exposure >10% — "
                    f"you're effectively double-investing in these."
                )
            if overlap_pct > 60:
                insight_parts.append(
                    "Consider replacing one fund with a different category (e.g., Mid Cap or Flexi Cap) "
                    "for better diversification."
                )
            elif overlap_pct < 30:
                insight_parts.append(
                    "These two funds complement each other well — low overlap means good diversification benefit."
                )

            st.markdown(
                '<div class="mf-insight">' +
                "<br>".join(insight_parts) +
                "</div>",
                unsafe_allow_html=True,
            )

        else:
            st.success("No common stocks found — these funds are perfectly diversified against each other!")


# ───────────────────────────────────────────────────────────────────────────
# TAB 3 — FUND SCREENER
# ───────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec-lbl">Filter mutual funds by your criteria</div>', unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns([2, 2, 1.5, 1.5])

    with fc1:
        sel_cats = st.multiselect(
            "Category",
            ["Equity", "Debt", "Hybrid", "ETF", "Index"],
            default=["Equity"],
            key="screener_cat",
        )

    with fc2:
        all_subcats = ["All"]
        for cat in (sel_cats or ["Equity"]):
            all_subcats += [s for s in SUBCATEGORY_MAP.get(cat, []) if s != "All" and s not in all_subcats]
        sel_subcat = st.selectbox("Sub-Category", all_subcats, key="screener_subcat")

    with fc3:
        min_rating = st.slider("Min Rating ★", 1, 5, 3, key="screener_rating")

    with fc4:
        max_er = st.slider("Max Expense Ratio %", 0.05, 2.5, 1.5, step=0.05, key="screener_er")

    sr_col1, sr_col2, sr_col3 = st.columns([1.5, 1.5, 2])
    with sr_col1:
        min_1y = st.number_input("Min 1Y Return %", value=0.0, step=1.0, key="screener_1y")
    with sr_col2:
        sort_by = st.selectbox("Sort by", ["1Y Return", "Rating", "AUM (Cr)", "Expense Ratio"], key="screener_sort")
    with sr_col3:
        sort_asc = st.radio("Sort order", ["Descending", "Ascending"], horizontal=True, key="screener_order")

    # Filter
    df_screen = pd.DataFrame(FUND_SCREENER_DATA)

    if sel_cats:
        df_screen = df_screen[df_screen["Category"].isin(sel_cats)]
    if sel_subcat and sel_subcat != "All":
        df_screen = df_screen[df_screen["Sub-Category"] == sel_subcat]
    df_screen = df_screen[df_screen["Rating"] >= min_rating]
    df_screen = df_screen[df_screen["Expense Ratio"] <= max_er]
    df_screen = df_screen[df_screen["1Y Return"] >= min_1y]

    asc = sort_asc == "Ascending"
    df_screen = df_screen.sort_values(sort_by, ascending=asc).reset_index(drop=True)

    st.markdown(
        f'<div style="font-size:0.78rem;color:#6b7280;margin:0.6rem 0;">Showing <b style="color:#8b5cf6;">{len(df_screen)}</b> of {len(FUND_SCREENER_DATA)} funds</div>',
        unsafe_allow_html=True,
    )

    if df_screen.empty:
        st.info("No funds match your filters. Try relaxing some criteria.")
    else:
        # Format display columns
        df_disp = df_screen.copy()
        df_disp["Rating"] = df_disp["Rating"].apply(stars)
        df_disp["1Y Return"] = df_disp["1Y Return"].apply(lambda x: f"{x:.1f}%")
        df_disp["3Y Return"] = df_disp["3Y Return"].apply(lambda x: f"{x:.1f}%")
        df_disp["Expense Ratio"] = df_disp["Expense Ratio"].apply(lambda x: f"{x:.2f}%")
        df_disp["AUM (Cr)"] = df_disp["AUM (Cr)"].apply(lambda x: f"₹{x:,.0f}")
        df_disp["Min SIP"] = df_disp["Min SIP"].apply(lambda x: f"₹{x:,}" if x > 0 else "Lump Only")

        cols_to_show = ["Fund Name", "Category", "Sub-Category", "Rating", "1Y Return", "3Y Return", "Expense Ratio", "AUM (Cr)", "Min SIP"]
        st.dataframe(df_disp[cols_to_show], use_container_width=True, hide_index=True)

        # Download button
        csv = df_screen.to_csv(index=False)
        st.download_button(
            label="⬇️ Export as CSV",
            data=csv,
            file_name="mf_screener_results.csv",
            mime="text/csv",
            key="screener_download",
        )

    st.caption("Data sourced from Value Research and AMFI. Returns are trailing annualised. Past performance is not indicative of future results.")


# ───────────────────────────────────────────────────────────────────────────
# TAB 4 — FUND COMPARE  (4-fund upgrade)
# ───────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec-lbl">Compare up to 4 funds side by side</div>', unsafe_allow_html=True)

    fund_options = list(FUND_HOLDINGS.keys())

    # ── "Compare Similar Funds" quick-fill ───────────────────────────────
    cat_names = list(CATEGORY_GROUPS.keys())
    sim_col, _, btn_col = st.columns([3, 0.3, 1.2])
    with sim_col:
        sim_cat = st.selectbox("Compare Similar Funds (auto-fill):", ["— Pick a category —"] + cat_names,
                               key="cmp_similar_cat")
    with btn_col:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        do_similar = st.button("Fill Category", key="cmp_fill_cat", use_container_width=True)

    if do_similar and sim_cat != "— Pick a category —":
        grp = CATEGORY_GROUPS[sim_cat][:4]
        for i, key in enumerate(["cmp_f1", "cmp_f2", "cmp_f3", "cmp_f4"], 1):
            if i - 1 < len(grp):
                st.session_state[key] = grp[i - 1]

    # ── 4 fund selectors ─────────────────────────────────────────────────
    cmp_c1, cmp_c2, cmp_c3, cmp_c4 = st.columns(4)
    defaults = [0, 1, 4, 6]
    with cmp_c1:
        cmp_f1 = st.selectbox("Fund 1", fund_options, index=defaults[0], key="cmp_f1")
    with cmp_c2:
        cmp_f2 = st.selectbox("Fund 2", fund_options, index=defaults[1], key="cmp_f2")
    with cmp_c3:
        cmp_f3 = st.selectbox("Fund 3", fund_options, index=defaults[2], key="cmp_f3")
    with cmp_c4:
        cmp_f4 = st.selectbox("Fund 4", fund_options, index=defaults[3], key="cmp_f4")

    compare_btn = st.button("Compare Funds", use_container_width=False, key="cmp_btn")

    selected_funds = [cmp_f1, cmp_f2, cmp_f3, cmp_f4]
    unique_funds = list(dict.fromkeys(selected_funds))

    funds_data = {f: FUND_HOLDINGS[f] for f in unique_funds}
    fund_colors = ["#8b5cf6", "#10b981", "#f59e0b", "#22d3ee"]

    # ── SECTION 1: OVERVIEW ──────────────────────────────────────────────
    st.markdown('<div class="sec-lbl" style="margin-top:1.2rem;">Overview</div>', unsafe_allow_html=True)

    overview_rows = []
    for label, key in [("Category", "category"), ("Fund Manager", "fund_manager"),
                       ("Rating", "rating"), ("Launch Year", "launch_year"),
                       ("AUM", "aum_cr"), ("Expense Ratio", "expense_ratio"),
                       ("Min SIP", "min_sip"), ("Benchmark", "benchmark")]:
        row = {"Metric": label}
        for fname in unique_funds:
            val = funds_data[fname].get(key, "—")
            if key == "rating":
                val = stars(val)
            elif key == "aum_cr":
                val = fmt_cr(val)
            elif key == "expense_ratio":
                val = f"{val:.2f}%"
            elif key == "min_sip":
                val = f"₹{val:,}"
            row[fname[:20]] = val
        overview_rows.append(row)
    st.dataframe(pd.DataFrame(overview_rows), use_container_width=True, hide_index=True)

    # ── SECTION 2: PERFORMANCE TABLE ─────────────────────────────────────
    st.markdown('<div class="sec-lbl" style="margin-top:1rem;">Performance (Trailing Returns)</div>', unsafe_allow_html=True)

    def color_returns(val):
        if isinstance(val, str):
            if val.startswith("▲"):
                return "color: #10b981; font-weight: 600;"
            elif val.startswith("▼"):
                return "color: #f87171; font-weight: 600;"
        return ""

    perf_periods = [("1 Day", "1D"), ("1 Month", "1M"), ("3 Month", "3M"),
                    ("6 Month", "6M"), ("1 Year", "1Y"), ("3 Year", "3Y"), ("5 Year", "5Y")]
    perf_rows = []
    for label, key in perf_periods:
        row = {"Period": label}
        for fname in unique_funds:
            ret = funds_data[fname].get("returns", {}).get(key)
            row[fname[:20]] = (f"{'▲' if ret >= 0 else '▼'} {abs(ret):.2f}%" if ret is not None else "—")
        perf_rows.append(row)
    df_perf = pd.DataFrame(perf_rows)
    col_names = [c for c in df_perf.columns if c != "Period"]
    st.dataframe(df_perf.style.map(color_returns, subset=col_names), use_container_width=True, hide_index=True)

    # ── SECTION 3: GROUPED RETURNS BAR CHART ─────────────────────────────
    st.markdown('<div class="sec-lbl" style="margin-top:1rem;">Returns Comparison (bar chart)</div>', unsafe_allow_html=True)
    bar_periods = ["1M", "3M", "6M", "1Y", "3Y", "5Y"]
    bar_fig = go.Figure()
    for idx, fname in enumerate(unique_funds):
        rets = funds_data[fname].get("returns", {})
        bar_fig.add_trace(go.Bar(
            name=fname[:22],
            x=bar_periods,
            y=[rets.get(p, 0) for p in bar_periods],
            marker_color=fund_colors[idx % 4],
            text=[f"{rets.get(p, 0):.1f}%" for p in bar_periods],
            textposition="outside",
            textfont=dict(size=9, color="#f0f0ff"),
            hovertemplate=f"<b>{fname[:22]}</b><br>%{{x}}: %{{y:.2f}}%<extra></extra>",
        ))
    bar_fig.update_layout(
        barmode="group",
        paper_bgcolor="#0d0d24", plot_bgcolor="#0d0d24",
        font=dict(color="#f0f0ff", family="Inter, sans-serif"),
        height=320, margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(gridcolor="rgba(139,92,246,0.08)", tickfont=dict(color="#a0a0c0")),
        yaxis=dict(title="Return %", gridcolor="rgba(139,92,246,0.08)", tickfont=dict(color="#6b7280")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#f0f0ff", size=10)),
        hovermode="x unified",
    )
    st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})

    # ── SECTION 4: RADAR / SPIDER CHART ──────────────────────────────────
    st.markdown('<div class="sec-lbl" style="margin-top:1rem;">Risk-Reward Radar</div>', unsafe_allow_html=True)
    radar_dims = ["3Y Returns", "Consistency", "Low Risk", "Low Cost", "Fund Size"]

    def _radar_scores(fd):
        rets = fd.get("returns", {})
        risk = fd.get("risk_metrics", {})
        r3y = rets.get("3Y", 15)
        std = risk.get("std_dev", 18)
        er = fd.get("expense_ratio", 1.0)
        aum = fd.get("aum_cr", 10000)
        sharpe = risk.get("sharpe", 1.0)
        return [
            min(r3y / 30 * 10, 10),
            min(sharpe / 2 * 10, 10),
            max(10 - std / 3, 1),
            max(10 - er * 5, 1),
            min(aum / 80000 * 10, 10),
        ]

    radar_fill = [
        "rgba(139,92,246,0.10)",
        "rgba(16,185,129,0.10)",
        "rgba(245,158,11,0.10)",
        "rgba(34,211,238,0.10)",
    ]
    radar_fig = go.Figure()
    for idx, fname in enumerate(unique_funds):
        scores = _radar_scores(funds_data[fname])
        radar_fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=radar_dims + [radar_dims[0]],
            name=fname[:22],
            line=dict(color=fund_colors[idx % 4], width=2),
            fill="toself",
            fillcolor=radar_fill[idx % 4],
            hovertemplate=f"<b>{fname[:22]}</b><br>%{{theta}}: %{{r:.1f}}/10<extra></extra>",
        ))
    radar_fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(color="#6b7280", size=8),
                            gridcolor="rgba(139,92,246,0.15)"),
            angularaxis=dict(tickfont=dict(color="#a0a0c0", size=10),
                             gridcolor="rgba(139,92,246,0.15)"),
        ),
        paper_bgcolor="#0d0d24",
        font=dict(color="#f0f0ff", family="Inter, sans-serif"),
        height=340, margin=dict(l=30, r=30, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, font=dict(color="#f0f0ff", size=10)),
        showlegend=True,
    )
    st.plotly_chart(radar_fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Radar scores out of 10. Consistency = Sharpe ratio normalised. Low Risk = inverse of std-dev. Low Cost = inverse of expense ratio. Fund Size = AUM normalised to ₹80,000 Cr.")

    # ── SECTION 5: SECTOR ALLOCATION (GROUPED BAR) ────────────────────────
    st.markdown('<div class="sec-lbl" style="margin-top:1rem;">Sector Allocation (grouped)</div>', unsafe_allow_html=True)
    all_sectors: set = set()
    for fd in funds_data.values():
        all_sectors |= set(fd.get("top_sectors", {}).keys())
    all_sectors_sorted = sorted(all_sectors)
    sec_bar_fig = go.Figure()
    for idx, fname in enumerate(unique_funds):
        top_sec = funds_data[fname].get("top_sectors", {})
        sec_bar_fig.add_trace(go.Bar(
            name=fname[:22],
            y=all_sectors_sorted,
            x=[top_sec.get(s, 0) for s in all_sectors_sorted],
            orientation="h",
            marker_color=fund_colors[idx % 4],
            hovertemplate=f"<b>{fname[:22]}</b><br>%{{y}}: %{{x:.1f}}%<extra></extra>",
        ))
    sec_bar_fig.update_layout(
        barmode="group",
        paper_bgcolor="#0d0d24", plot_bgcolor="#0d0d24",
        font=dict(color="#f0f0ff", family="Inter, sans-serif"),
        height=max(280, len(all_sectors_sorted) * 40),
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(title="Allocation %", gridcolor="rgba(139,92,246,0.08)", tickfont=dict(color="#6b7280")),
        yaxis=dict(tickfont=dict(color="#a0a0c0", size=10)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#f0f0ff", size=10)),
        hovermode="y unified",
    )
    st.plotly_chart(sec_bar_fig, use_container_width=True, config={"displayModeBar": False})

    # ── SECTION 6: 1-YEAR NAV TREND ──────────────────────────────────────
    st.markdown('<div class="sec-lbl" style="margin-top:1rem;">1-Year NAV Trend (Indexed to 100)</div>', unsafe_allow_html=True)
    with st.spinner("Fetching live NAV data..."):
        mf_list = fetch_mfapi_list()

    nav_fig = go.Figure()
    for idx, fname in enumerate(unique_funds):
        scheme_code = None
        if mf_list:
            matches = difflib.get_close_matches(fname, [m.get("schemeName", "") for m in mf_list], n=1, cutoff=0.4)
            if matches:
                matched = next((m for m in mf_list if m.get("schemeName") == matches[0]), None)
                if matched:
                    scheme_code = str(matched.get("schemeCode", ""))
        plotted = False
        if scheme_code:
            df_nav = fetch_fund_nav_history(scheme_code)
            if not df_nav.empty:
                df_1y = df_nav[df_nav["date"] >= datetime.now() - timedelta(days=365)].copy()
                if not df_1y.empty:
                    base_nav = float(df_1y.iloc[0]["nav"])
                    if base_nav > 0:
                        df_1y["indexed"] = df_1y["nav"] / base_nav * 100
                        nav_fig.add_trace(go.Scatter(
                            x=df_1y["date"], y=df_1y["indexed"], name=fname[:22],
                            line=dict(color=fund_colors[idx % 4], width=2),
                            hovertemplate=f"{fname[:20]}<br>%{{x|%b %Y}}: %{{y:.1f}}<extra></extra>",
                        ))
                        plotted = True
        if not plotted:
            r1y = funds_data[fname].get("returns", {}).get("1Y", 15)
            x = [datetime.now() - timedelta(days=365 - i * 30) for i in range(13)]
            mr = (1 + r1y / 100) ** (1 / 12) - 1
            nav_fig.add_trace(go.Scatter(
                x=x, y=[100 * (1 + mr) ** i for i in range(13)],
                name=f"{fname[:22]} (est.)",
                line=dict(color=fund_colors[idx % 4], width=2, dash="dot"),
                hovertemplate=f"{fname[:20]}<br>%{{x|%b %Y}}: %{{y:.1f}}<extra></extra>",
            ))
    nav_fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.2)", annotation_text="Base (100)")
    nav_fig.update_layout(
        paper_bgcolor="#0d0d24", plot_bgcolor="#0d0d24",
        font=dict(color="#f0f0ff", family="Inter, sans-serif"),
        height=320, margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor="rgba(139,92,246,0.08)", tickfont=dict(color="#6b7280")),
        yaxis=dict(title="Indexed NAV (Base 100)", gridcolor="rgba(139,92,246,0.08)", tickfont=dict(color="#6b7280")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#f0f0ff", size=10)),
        hovermode="x unified",
    )
    st.plotly_chart(nav_fig, use_container_width=True, config={"displayModeBar": False})

    # ── SECTION 7: COMMON STOCKS ──────────────────────────────────────────
    if len(unique_funds) > 1:
        all_stock_sets = [set(funds_data[f]["holdings"].keys()) for f in unique_funds]
        common_all = all_stock_sets[0]
        for s in all_stock_sets[1:]:
            common_all &= s
        st.markdown('<div class="sec-lbl">Stocks Common to All Selected Funds</div>', unsafe_allow_html=True)
        if common_all:
            common_rows = [{"Stock": stk, **{f[:20]: f"{funds_data[f]['holdings'].get(stk,0):.1f}%" for f in unique_funds}}
                           for stk in sorted(common_all)]
            st.dataframe(pd.DataFrame(common_rows), use_container_width=True, hide_index=True)
            st.markdown(
                f'<div class="mf-insight">These <b style="color:#8b5cf6;">{len(common_all)} stocks</b> appear '
                f'in all {len(unique_funds)} selected funds — unavoidable overlap if you hold all together.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.success("No stocks common to all selected funds — excellent diversification!")

    # ── SECTION 8: SMART RECOMMENDATION ──────────────────────────────────
    st.markdown('<div class="sec-lbl" style="margin-top:1.2rem;">Smart Recommendation</div>', unsafe_allow_html=True)

    def _score(fd):
        r3y = fd.get("returns", {}).get("3Y", 15)
        er = fd.get("expense_ratio", 1.0)
        rating = fd.get("rating", 3)
        r3y_norm = min(r3y / 30, 1) * 100
        er_norm = max(1 - er / 2, 0) * 100
        rat_norm = (rating / 5) * 100
        return round(r3y_norm * 0.40 + er_norm * 0.30 + rat_norm * 0.30, 1)

    scores = {f: _score(funds_data[f]) for f in unique_funds}
    winner = max(scores, key=scores.get)
    winner_data = funds_data[winner]

    rec_parts = []
    if winner_data.get("expense_ratio", 1) < 0.7:
        rec_parts.append(f"lowest expense ratio ({winner_data['expense_ratio']:.2f}%) in this group")
    if winner_data.get("returns", {}).get("3Y", 0) == max(funds_data[f].get("returns", {}).get("3Y", 0) for f in unique_funds):
        rec_parts.append(f"best 3Y return ({winner_data['returns'].get('3Y', 0):.1f}%)")
    if winner_data.get("rating", 0) == max(funds_data[f].get("rating", 0) for f in unique_funds):
        rec_parts.append(f"highest rating ({stars(winner_data.get('rating',3))})")
    rec_reason = " · ".join(rec_parts) if rec_parts else "best overall score"

    score_cols = st.columns(len(unique_funds))
    for idx, fname in enumerate(unique_funds):
        s = scores[fname]
        is_winner = fname == winner
        bg = "rgba(16,185,129,0.12)" if is_winner else "rgba(255,255,255,0.03)"
        border = "2px solid #10b981" if is_winner else "1px solid rgba(139,92,246,0.15)"
        crown = " 👑" if is_winner else ""
        with score_cols[idx]:
            st.markdown(_H(f"""
            <div style="background:{bg};border:{border};border-radius:12px;padding:0.85rem 1rem;text-align:center;">
              <div style="font-size:0.72rem;font-weight:700;color:#8b5cf6;margin-bottom:6px;
                   white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{fname[:24]}{crown}</div>
              <div style="font-size:2rem;font-weight:800;color:{'#10b981' if is_winner else '#f0f0ff'};">{s:.0f}</div>
              <div style="font-size:0.6rem;color:#6b7280;">/ 100</div>
            </div>"""), unsafe_allow_html=True)

    st.markdown(
        f'<div class="mf-insight" style="margin-top:0.8rem;">🏆 <b style="color:#10b981;">{winner}</b> scores '
        f'<b>{scores[winner]:.0f}/100</b> — recommended pick in this group. '
        f'Reason: {rec_reason}.<br><span style="font-size:0.75rem;color:#6b7280;">'
        f'Score = 3Y Return (40%) + Low Expense Ratio (30%) + Rating (30%). Not investment advice.</span></div>',
        unsafe_allow_html=True,
    )

    st.caption("Performance via mfapi.in (dotted = estimate). Sector allocation from AMFI factsheets.")
