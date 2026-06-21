import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import difflib

st.set_page_config(page_title="MF Research Hub — SipCheck", page_icon="🏦", layout="wide")
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
}

FUND_HOLDINGS = {
    "Mirae Asset Large Cap Fund": {
        "category": "Equity - Large Cap",
        "rating": 5,
        "aum_cr": 38200,
        "expense_ratio": 0.54,
        "min_sip": 1000,
        "launch_year": 2008,
        "benchmark": "Nifty 100 TRI",
        "sectors": {"Financial Services": 32.1, "IT": 18.4, "Consumer Goods": 10.2, "Energy": 9.8, "Healthcare": 7.6},
        "holdings": {
            "HDFC Bank": 9.2, "Infosys": 8.5, "Reliance Industries": 8.1,
            "ICICI Bank": 7.4, "TCS": 7.1, "Bharti Airtel": 7.2,
            "Axis Bank": 4.8, "HUL": 4.2, "ITC": 4.2, "L&T": 4.1,
            "Bajaj Finance": 3.9, "Kotak Mahindra Bank": 3.6, "Titan": 3.4,
            "Sun Pharma": 2.8, "Asian Paints": 2.6, "Nestle India": 2.4,
            "Wipro": 2.1, "Maruti Suzuki": 1.8, "Power Grid": 1.6, "NTPC": 1.4,
        },
        "returns": {"1D": 0.42, "1M": 2.1, "3M": 5.8, "1Y": 22.4, "3Y": 18.6},
    },
    "Axis Bluechip Fund": {
        "category": "Equity - Large Cap",
        "rating": 5,
        "aum_cr": 41300,
        "expense_ratio": 0.52,
        "min_sip": 500,
        "launch_year": 2010,
        "benchmark": "Nifty 50 TRI",
        "sectors": {"Financial Services": 28.4, "IT": 22.1, "Consumer Goods": 14.6, "Healthcare": 8.2, "Auto": 6.8},
        "holdings": {
            "Infosys": 7.9, "TCS": 7.4, "Bharti Airtel": 6.8, "HDFC Bank": 7.2,
            "ICICI Bank": 5.9, "Titan": 7.4, "Asian Paints": 5.8, "Bajaj Finance": 5.4,
            "HUL": 4.3, "Kotak Mahindra Bank": 3.8, "Axis Bank": 3.6,
            "Nestle India": 2.4, "ITC": 2.1, "Wipro": 2.0, "Sun Pharma": 1.9,
            "Maruti Suzuki": 1.8, "L&T": 1.7, "NTPC": 1.1, "Power Grid": 1.0, "Reliance Industries": 5.5,
        },
        "returns": {"1D": 0.38, "1M": 1.9, "3M": 5.4, "1Y": 21.8, "3Y": 17.9},
    },
    "HDFC Top 100 Fund": {
        "category": "Equity - Large Cap",
        "rating": 4,
        "aum_cr": 31800,
        "expense_ratio": 1.02,
        "min_sip": 500,
        "launch_year": 1996,
        "benchmark": "Nifty 100 TRI",
        "sectors": {"Financial Services": 35.8, "Energy": 14.2, "IT": 12.4, "Consumer Goods": 9.8, "Metals": 5.6},
        "holdings": {
            "HDFC Bank": 9.8, "ICICI Bank": 7.2, "Reliance Industries": 6.8,
            "Infosys": 6.3, "ITC": 6.8, "SBI": 5.4, "TCS": 5.8,
            "Axis Bank": 4.8, "HUL": 5.4, "L&T": 4.2, "Kotak Mahindra Bank": 3.8,
            "Bharti Airtel": 5.4, "Asian Paints": 4.2, "Sun Pharma": 3.6,
            "Nestle India": 3.2, "Titan": 2.8, "Wipro": 2.3, "Maruti Suzuki": 2.1,
            "NTPC": 1.8, "Power Grid": 1.6,
        },
        "returns": {"1D": 0.51, "1M": 2.4, "3M": 6.1, "1Y": 24.6, "3Y": 19.2},
    },
    "ICICI Pru Bluechip Fund": {
        "category": "Equity - Large Cap",
        "rating": 5,
        "aum_cr": 52100,
        "expense_ratio": 0.87,
        "min_sip": 100,
        "launch_year": 2008,
        "benchmark": "Nifty 100 TRI",
        "sectors": {"Financial Services": 33.4, "Energy": 12.8, "IT": 14.2, "Consumer Goods": 8.6, "Telecom": 7.2},
        "holdings": {
            "ICICI Bank": 9.1, "Reliance Industries": 8.7, "HDFC Bank": 7.1,
            "Infosys": 6.8, "Bharti Airtel": 6.1, "ITC": 4.8, "TCS": 5.2,
            "Axis Bank": 5.2, "L&T": 3.8, "Kotak Mahindra Bank": 4.4,
            "SBI": 4.2, "HUL": 3.1, "Bajaj Finance": 2.9, "Sun Pharma": 2.8,
            "Titan": 2.4, "Nestle India": 2.1, "Asian Paints": 1.9,
            "Maruti Suzuki": 1.8, "NTPC": 1.9, "Power Grid": 2.2,
        },
        "returns": {"1D": 0.46, "1M": 2.2, "3M": 5.9, "1Y": 23.1, "3Y": 18.8},
    },
    "SBI Bluechip Fund": {
        "category": "Equity - Large Cap",
        "rating": 4,
        "aum_cr": 29600,
        "expense_ratio": 0.78,
        "min_sip": 500,
        "launch_year": 2006,
        "benchmark": "S&P BSE 100 TRI",
        "sectors": {"Financial Services": 30.2, "IT": 16.8, "Consumer Goods": 12.4, "Auto": 8.6, "Pharma": 6.2},
        "holdings": {
            "HDFC Bank": 8.4, "Infosys": 5.8, "ICICI Bank": 7.8, "TCS": 6.9,
            "HUL": 6.2, "ITC": 5.9, "Reliance Industries": 4.8, "Bharti Airtel": 4.9,
            "Axis Bank": 3.8, "Kotak Mahindra Bank": 3.2, "L&T": 2.8,
            "Bajaj Finance": 2.6, "Sun Pharma": 2.4, "Asian Paints": 2.8,
            "Maruti Suzuki": 2.8, "Titan": 2.4, "Nestle India": 2.1,
            "Wipro": 1.9, "NTPC": 1.6, "Power Grid": 1.4,
        },
        "returns": {"1D": 0.35, "1M": 1.7, "3M": 4.9, "1Y": 20.4, "3Y": 16.8},
    },
    "Parag Parikh Flexi Cap Fund": {
        "category": "Equity - Flexi Cap",
        "rating": 5,
        "aum_cr": 64500,
        "expense_ratio": 0.63,
        "min_sip": 1000,
        "launch_year": 2013,
        "benchmark": "Nifty 500 TRI",
        "sectors": {"Financial Services": 24.8, "IT": 19.6, "Consumer Goods": 12.2, "Global Equities": 18.4, "Auto": 7.2},
        "holdings": {
            "HDFC Bank": 4.8, "Bajaj Holdings": 4.2, "ITC": 2.9, "Reliance Industries": 3.4,
            "ICICI Bank": 3.7, "Infosys": 4.2, "HUL": 3.1, "Axis Bank": 2.8,
            "Kotak Mahindra Bank": 2.4, "Titan": 3.4, "Asian Paints": 2.4,
            "Nestle India": 1.9, "Sun Pharma": 1.6, "L&T": 3.2, "Bharti Airtel": 2.2,
            "Maruti Suzuki": 2.4, "Wipro": 1.8, "NTPC": 1.4, "Power Grid": 1.2, "TCS": 2.1,
        },
        "returns": {"1D": 0.29, "1M": 1.4, "3M": 4.2, "1Y": 19.8, "3Y": 21.4},
    },
    "Canara Robeco Flexi Cap Fund": {
        "category": "Equity - Flexi Cap",
        "rating": 4,
        "aum_cr": 12400,
        "expense_ratio": 0.57,
        "min_sip": 1000,
        "launch_year": 2003,
        "benchmark": "Nifty 500 TRI",
        "sectors": {"Financial Services": 29.4, "IT": 17.8, "Consumer Goods": 11.6, "Healthcare": 9.2, "Auto": 7.4},
        "holdings": {
            "HDFC Bank": 6.2, "Infosys": 5.4, "ICICI Bank": 5.8, "Reliance Industries": 4.6,
            "TCS": 4.9, "Axis Bank": 3.1, "HUL": 4.1, "ITC": 3.2,
            "Bharti Airtel": 3.1, "Bajaj Finance": 2.8, "Sun Pharma": 3.2,
            "Titan": 2.6, "Asian Paints": 2.1, "L&T": 2.8, "Nestle India": 1.8,
            "Kotak Mahindra Bank": 2.4, "Maruti Suzuki": 2.1, "Wipro": 1.6,
            "NTPC": 1.4, "Power Grid": 1.2,
        },
        "returns": {"1D": 0.41, "1M": 2.0, "3M": 5.5, "1Y": 22.1, "3Y": 18.2},
    },
    "ABSL Flexi Cap Fund": {
        "category": "Equity - Flexi Cap",
        "rating": 4,
        "aum_cr": 26400,
        "expense_ratio": 0.84,
        "min_sip": 500,
        "launch_year": 1995,
        "benchmark": "S&P BSE 500 TRI",
        "sectors": {"Financial Services": 31.2, "Energy": 10.8, "IT": 14.6, "Consumer Goods": 10.4, "Telecom": 6.8},
        "holdings": {
            "Reliance Industries": 8.2, "HDFC Bank": 7.6, "ICICI Bank": 6.4,
            "Infosys": 5.9, "Bharti Airtel": 5.8, "ITC": 4.8, "TCS": 5.1,
            "HUL": 3.8, "Axis Bank": 3.4, "Bajaj Finance": 3.2,
            "Kotak Mahindra Bank": 2.8, "L&T": 2.6, "Sun Pharma": 2.4,
            "Titan": 2.2, "Asian Paints": 2.0, "Nestle India": 1.8,
            "Maruti Suzuki": 1.6, "Wipro": 1.4, "NTPC": 1.8, "Power Grid": 1.4,
        },
        "returns": {"1D": 0.44, "1M": 2.1, "3M": 5.7, "1Y": 21.6, "3Y": 17.4},
    },
    "DSP Flexi Cap Fund": {
        "category": "Equity - Flexi Cap",
        "rating": 4,
        "aum_cr": 14800,
        "expense_ratio": 0.72,
        "min_sip": 500,
        "launch_year": 1997,
        "benchmark": "Nifty 500 TRI",
        "sectors": {"Financial Services": 27.6, "IT": 16.2, "Consumer Goods": 13.4, "Healthcare": 10.8, "Auto": 8.2},
        "holdings": {
            "HDFC Bank": 7.4, "TCS": 6.8, "Infosys": 5.6, "ICICI Bank": 5.2,
            "HUL": 4.6, "ITC": 4.4, "Reliance Industries": 4.2, "Bharti Airtel": 3.8,
            "Sun Pharma": 3.4, "L&T": 3.2, "Bajaj Finance": 2.8,
            "Titan": 2.6, "Asian Paints": 2.4, "Nestle India": 2.2,
            "Kotak Mahindra Bank": 2.0, "Axis Bank": 1.8, "Maruti Suzuki": 2.4,
            "Wipro": 1.6, "NTPC": 1.4, "Power Grid": 1.2,
        },
        "returns": {"1D": 0.38, "1M": 1.8, "3M": 5.1, "1Y": 20.8, "3Y": 17.1},
    },
    "Kotak Flexi Cap Fund": {
        "category": "Equity - Flexi Cap",
        "rating": 4,
        "aum_cr": 48200,
        "expense_ratio": 0.62,
        "min_sip": 100,
        "launch_year": 2009,
        "benchmark": "Nifty 500 TRI",
        "sectors": {"Financial Services": 30.8, "IT": 15.6, "Consumer Goods": 11.8, "Auto": 9.2, "Healthcare": 7.6},
        "holdings": {
            "HDFC Bank": 8.2, "ICICI Bank": 6.8, "Reliance Industries": 5.8,
            "Infosys": 5.4, "Kotak Mahindra Bank": 6.9, "TCS": 4.8, "Bharti Airtel": 4.2,
            "ITC": 3.8, "Axis Bank": 3.4, "HUL": 3.2, "Bajaj Finance": 2.8,
            "Titan": 2.4, "Maruti Suzuki": 2.8, "Sun Pharma": 2.2,
            "L&T": 2.0, "Asian Paints": 1.8, "Nestle India": 1.6,
            "Wipro": 1.9, "NTPC": 1.4, "Power Grid": 1.2,
        },
        "returns": {"1D": 0.43, "1M": 2.1, "3M": 5.6, "1Y": 21.4, "3Y": 17.8},
    },
    "HDFC Mid-Cap Opportunities Fund": {
        "category": "Equity - Mid Cap",
        "rating": 5,
        "aum_cr": 71200,
        "expense_ratio": 0.78,
        "min_sip": 100,
        "launch_year": 2007,
        "benchmark": "Nifty Midcap 150 TRI",
        "sectors": {"Financial Services": 18.4, "Consumer Goods": 14.2, "Auto": 12.8, "Healthcare": 11.6, "IT": 8.4},
        "holdings": {
            "Cholamandalam Finance": 4.8, "Supreme Industries": 4.2, "Tube Investments": 3.8,
            "Persistent Systems": 3.6, "Bajaj Finance": 4.8, "Maruti Suzuki": 4.6,
            "Titan": 3.9, "Crompton Greaves": 3.4, "Mphasis": 3.2,
            "Voltas": 2.8, "Indian Hotels": 2.6, "PI Industries": 2.4,
            "Alkem Laboratories": 2.2, "HDFC Bank": 2.0, "Infosys": 1.8,
            "ITC": 1.6, "L&T": 2.2, "Reliance Industries": 1.4, "TCS": 1.2, "ICICI Bank": 1.6,
        },
        "returns": {"1D": 0.58, "1M": 2.8, "3M": 7.4, "1Y": 28.6, "3Y": 24.2},
    },
    "Axis Mid Cap Fund": {
        "category": "Equity - Mid Cap",
        "rating": 5,
        "aum_cr": 28400,
        "expense_ratio": 0.54,
        "min_sip": 500,
        "launch_year": 2011,
        "benchmark": "Nifty Midcap 150 TRI",
        "sectors": {"Financial Services": 16.8, "Consumer Goods": 16.4, "Healthcare": 14.2, "IT": 12.6, "Auto": 10.8},
        "holdings": {
            "Cholamandalam Finance": 4.4, "Mphasis": 4.1, "Tube Investments": 3.8,
            "Page Industries": 3.6, "Titan": 4.1, "Bajaj Finance": 5.4,
            "Alkem Laboratories": 3.4, "Indian Hotels": 3.2, "Persistent Systems": 3.0,
            "Dixon Technologies": 2.8, "PI Industries": 2.6, "Voltas": 2.4,
            "Maruti Suzuki": 2.2, "HDFC Bank": 2.0, "Infosys": 1.8,
            "ITC": 1.6, "L&T": 1.4, "Reliance Industries": 1.2, "ICICI Bank": 1.4, "TCS": 1.6,
        },
        "returns": {"1D": 0.62, "1M": 3.1, "3M": 8.2, "1Y": 30.4, "3Y": 26.1},
    },
    "Nippon India Mid Cap Fund": {
        "category": "Equity - Mid Cap",
        "rating": 4,
        "aum_cr": 42800,
        "expense_ratio": 0.82,
        "min_sip": 100,
        "launch_year": 2010,
        "benchmark": "Nifty Midcap 150 TRI",
        "sectors": {"Financial Services": 20.2, "Consumer Goods": 13.8, "IT": 12.4, "Healthcare": 11.8, "Metals": 8.6},
        "holdings": {
            "Bajaj Finance": 3.8, "Mphasis": 3.4, "Cholamandalam Finance": 3.2,
            "Persistent Systems": 3.0, "Tube Investments": 2.8, "Indian Hotels": 2.6,
            "Alkem Laboratories": 2.4, "Supreme Industries": 2.2, "Voltas": 2.0,
            "Page Industries": 1.8, "PI Industries": 1.6, "Dixon Technologies": 2.4,
            "Titan": 2.2, "HDFC Bank": 1.8, "Infosys": 1.6,
            "Maruti Suzuki": 1.8, "ITC": 1.4, "L&T": 1.6, "ICICI Bank": 1.4, "Reliance Industries": 1.2,
        },
        "returns": {"1D": 0.54, "1M": 2.6, "3M": 6.8, "1Y": 26.2, "3Y": 22.4},
    },
    "SBI Small Cap Fund": {
        "category": "Equity - Small Cap",
        "rating": 5,
        "aum_cr": 38600,
        "expense_ratio": 0.69,
        "min_sip": 500,
        "launch_year": 2009,
        "benchmark": "S&P BSE Small Cap TRI",
        "sectors": {"Consumer Goods": 22.4, "Healthcare": 16.8, "Auto Ancillaries": 12.6, "Chemicals": 10.4, "IT": 8.2},
        "holdings": {
            "Hawkins Cookers": 3.8, "Elgi Equipment": 3.4, "Suprajit Engineering": 3.2,
            "Aarti Industries": 3.0, "Navin Fluorine": 2.8, "Vinati Organics": 2.6,
            "Astral Poly": 2.4, "Dixon Technologies": 2.2, "CAMS": 2.0,
            "Fine Organic": 1.8, "Shriram Finance": 1.8, "Laurus Labs": 1.6,
            "Bajaj Finance": 1.4, "HDFC Bank": 1.2, "Infosys": 1.0,
            "ITC": 0.8, "L&T": 1.2, "Reliance Industries": 0.8, "Titan": 1.4, "ICICI Bank": 1.0,
        },
        "returns": {"1D": 0.71, "1M": 3.4, "3M": 9.2, "1Y": 34.8, "3Y": 28.6},
    },
    "HDFC Small Cap Fund": {
        "category": "Equity - Small Cap",
        "rating": 4,
        "aum_cr": 32400,
        "expense_ratio": 0.62,
        "min_sip": 100,
        "launch_year": 2008,
        "benchmark": "Nifty Smallcap 250 TRI",
        "sectors": {"Chemicals": 18.4, "Consumer Goods": 14.6, "Healthcare": 12.2, "IT": 10.8, "Auto": 9.4},
        "holdings": {
            "Aarti Industries": 3.6, "Navin Fluorine": 3.2, "Suprajit Engineering": 2.8,
            "Elgi Equipment": 2.6, "Astral Poly": 2.4, "Laurus Labs": 2.2,
            "Fine Organic": 2.0, "Hawkins Cookers": 1.8, "Shriram Finance": 1.8,
            "CAMS": 1.6, "Dixon Technologies": 2.4, "Vinati Organics": 1.4,
            "Bajaj Finance": 1.2, "HDFC Bank": 1.0, "Infosys": 0.8,
            "ITC": 0.8, "L&T": 1.0, "Titan": 1.2, "Maruti Suzuki": 1.4, "ICICI Bank": 0.8,
        },
        "returns": {"1D": 0.68, "1M": 3.2, "3M": 8.6, "1Y": 32.4, "3Y": 26.8},
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


def plotly_dark_layout(**kwargs):
    base = dict(
        template="plotly_dark",
        paper_bgcolor="#0d0d24",
        plot_bgcolor="#0d0d24",
        font=dict(color="#f0f0ff", family="Inter, sans-serif"),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    base.update(kwargs)
    return base


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
                **plotly_dark_layout(height=max(260, len(chart_data) * 36)),
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
# TAB 4 — FUND COMPARE
# ───────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec-lbl">Compare up to 3 funds side by side</div>', unsafe_allow_html=True)

    fund_options = list(FUND_HOLDINGS.keys())
    cmp_c1, cmp_c2, cmp_c3 = st.columns(3)
    with cmp_c1:
        cmp_f1 = st.selectbox("Fund 1", fund_options, index=0, key="cmp_f1")
    with cmp_c2:
        cmp_f2 = st.selectbox("Fund 2", fund_options, index=1, key="cmp_f2")
    with cmp_c3:
        cmp_f3 = st.selectbox("Fund 3", fund_options, index=4, key="cmp_f3")

    compare_btn = st.button("Compare Funds", use_container_width=False, key="cmp_btn")

    selected_funds = [cmp_f1, cmp_f2, cmp_f3]
    unique_funds = list(dict.fromkeys(selected_funds))

    if compare_btn or True:
        funds_data = {f: FUND_HOLDINGS[f] for f in unique_funds}

        # ── SECTION 1: OVERVIEW ──
        st.markdown('<div class="sec-lbl" style="margin-top:1.2rem;">Overview</div>', unsafe_allow_html=True)

        overview_rows = []
        metrics = [
            ("Category", "category"),
            ("Rating", "rating"),
            ("Launch Year", "launch_year"),
            ("AUM", "aum_cr"),
            ("Expense Ratio", "expense_ratio"),
            ("Min SIP", "min_sip"),
            ("Benchmark", "benchmark"),
        ]
        for label, key in metrics:
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
                row[fname[:22]] = val
            overview_rows.append(row)

        df_overview = pd.DataFrame(overview_rows)
        st.dataframe(df_overview, use_container_width=True, hide_index=True)

        # ── SECTION 2: PERFORMANCE ──
        st.markdown('<div class="sec-lbl" style="margin-top:1rem;">Performance (Trailing Returns)</div>', unsafe_allow_html=True)

        perf_periods = [("1 Day", "1D"), ("1 Month", "1M"), ("3 Month", "3M"), ("1 Year", "1Y"), ("3 Year", "3Y")]
        perf_rows = []
        for label, key in perf_periods:
            row = {"Period": label}
            for fname in unique_funds:
                ret = funds_data[fname].get("returns", {}).get(key)
                if ret is not None:
                    sign = "▲" if ret >= 0 else "▼"
                    row[fname[:22]] = f"{sign} {abs(ret):.2f}%"
                else:
                    row[fname[:22]] = "—"
            perf_rows.append(row)

        df_perf = pd.DataFrame(perf_rows)

        def color_returns(val):
            if isinstance(val, str):
                if val.startswith("▲"):
                    return "color: #10b981; font-weight: 600;"
                elif val.startswith("▼"):
                    return "color: #f87171; font-weight: 600;"
            return ""

        col_names = [c for c in df_perf.columns if c != "Period"]
        styled_perf = df_perf.style.map(color_returns, subset=col_names)
        st.dataframe(styled_perf, use_container_width=True, hide_index=True)

        # Line chart — 1Y performance comparison
        st.markdown('<div class="sec-lbl">1-Year NAV Trend (Indexed to 100)</div>', unsafe_allow_html=True)

        with st.spinner("Fetching live NAV data..."):
            mf_list = fetch_mfapi_list()

        # Map fund names to scheme codes (best-effort fuzzy match)
        nav_fig = go.Figure()
        colors_cycle = ["#8b5cf6", "#10b981", "#f59e0b"]

        for idx, fname in enumerate(unique_funds):
            scheme_code = None
            if mf_list:
                matches = difflib.get_close_matches(fname, [m.get("schemeName", "") for m in mf_list], n=1, cutoff=0.4)
                if matches:
                    matched = next((m for m in mf_list if m.get("schemeName") == matches[0]), None)
                    if matched:
                        scheme_code = str(matched.get("schemeCode", ""))

            if scheme_code:
                df_nav = fetch_fund_nav_history(scheme_code)
                if not df_nav.empty:
                    one_year_ago = datetime.now() - timedelta(days=365)
                    df_1y = df_nav[df_nav["date"] >= one_year_ago].copy()
                    if not df_1y.empty:
                        base_nav = float(df_1y.iloc[0]["nav"])
                        if base_nav > 0:
                            df_1y["indexed"] = df_1y["nav"] / base_nav * 100
                            nav_fig.add_trace(go.Scatter(
                                x=df_1y["date"],
                                y=df_1y["indexed"],
                                name=fname[:25],
                                line=dict(color=colors_cycle[idx % 3], width=2),
                                hovertemplate=f"{fname[:20]}<br>%{{x|%b %Y}}: %{{y:.1f}}<extra></extra>",
                            ))
                            continue

            # Fallback: synthetic from stored returns
            returns = funds_data[fname].get("returns", {})
            r1y = returns.get("1Y", 15)
            x = [datetime.now() - timedelta(days=365 - i * 30) for i in range(13)]
            monthly_r = (1 + r1y / 100) ** (1 / 12) - 1
            y = [100 * (1 + monthly_r) ** i for i in range(13)]
            nav_fig.add_trace(go.Scatter(
                x=x, y=y,
                name=f"{fname[:25]} (est.)",
                line=dict(color=colors_cycle[idx % 3], width=2, dash="dot"),
                hovertemplate=f"{fname[:20]}<br>%{{x|%b %Y}}: %{{y:.1f}}<extra></extra>",
            ))

        nav_fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.2)", annotation_text="Base (100)")
        nav_fig.update_layout(
            **plotly_dark_layout(height=320),
            xaxis=dict(title="", gridcolor="rgba(139,92,246,0.08)", tickfont=dict(color="#6b7280")),
            yaxis=dict(title="Indexed NAV (Base 100)", gridcolor="rgba(139,92,246,0.08)", tickfont=dict(color="#6b7280")),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#f0f0ff", size=11)),
            hovermode="x unified",
        )
        st.plotly_chart(nav_fig, use_container_width=True, config={"displayModeBar": False})

        # ── SECTION 3: PORTFOLIO ──
        st.markdown('<div class="sec-lbl" style="margin-top:1rem;">Portfolio — Sector Allocation</div>', unsafe_allow_html=True)

        sector_cols = st.columns(len(unique_funds))
        for i, fname in enumerate(unique_funds):
            sectors = funds_data[fname].get("sectors", {})
            with sector_cols[i]:
                st.markdown(f"<div style='font-size:0.72rem;font-weight:700;color:#8b5cf6;text-align:center;margin-bottom:4px;'>{fname[:28]}</div>", unsafe_allow_html=True)
                if sectors:
                    sec_labels = list(sectors.keys())
                    sec_vals = list(sectors.values())
                    sec_fig = go.Figure(go.Pie(
                        labels=sec_labels,
                        values=sec_vals,
                        hole=0.52,
                        textinfo="percent",
                        textfont=dict(size=10, color="#f0f0ff"),
                        marker=dict(colors=["#8b5cf6", "#10b981", "#f59e0b", "#22d3ee", "#f87171"]),
                        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
                    ))
                    sec_fig.update_layout(
                        **plotly_dark_layout(height=240),
                        margin=dict(l=5, r=5, t=10, b=10),
                        showlegend=True,
                        legend=dict(font=dict(size=9, color="#6b7280"), orientation="v", x=1.0),
                    )
                    st.plotly_chart(sec_fig, use_container_width=True, config={"displayModeBar": False})

        # Common stocks across all selected funds
        if len(unique_funds) > 1:
            all_stock_sets = [set(funds_data[f]["holdings"].keys()) for f in unique_funds]
            common_all = all_stock_sets[0]
            for s in all_stock_sets[1:]:
                common_all = common_all & s

            st.markdown('<div class="sec-lbl">Stocks Common to All Selected Funds</div>', unsafe_allow_html=True)
            if common_all:
                common_rows = []
                for stock in sorted(common_all):
                    row = {"Stock": stock}
                    for fname in unique_funds:
                        row[fname[:22]] = f"{funds_data[fname]['holdings'].get(stock, 0):.1f}%"
                    common_rows.append(row)
                st.dataframe(pd.DataFrame(common_rows), use_container_width=True, hide_index=True)
                st.markdown(
                    f'<div class="mf-insight">These <b style="color:#8b5cf6;">{len(common_all)} stocks</b> appear in all {len(unique_funds)} selected funds. '
                    f'They represent unavoidable concentration if you hold all these funds together.</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.success("No stocks are common to all selected funds — excellent diversification!")

        st.caption("Performance data via mfapi.in (dotted lines = estimates when live NAV unavailable). Sector allocation from AMFI factsheets.")
