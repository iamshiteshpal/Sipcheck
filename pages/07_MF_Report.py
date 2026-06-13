import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime, timedelta
import math

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MF Report · SipCheck",
    page_icon="📊",
    layout="wide",
)
from sidebar_v2 import render_sidebar
render_sidebar()


# ── global CSS – matches SipCheck dark theme ──────────────────────────────────
st.markdown("""
<style>
  /* ── base ── */
  html, body, [data-testid="stAppViewContainer"] {
      background: #0e1117 !important;
      color: #e0e0e0;
      font-family: 'Inter', sans-serif;
  }
  [data-testid="stSidebar"] { background: #161b27 !important; }
  h1,h2,h3,h4 { color: #ffffff; font-weight: 600; }

  /* ── section header bar (same as SIP Simulator) ── */
  .section-bar {
      border-left: 3px solid #7c6af7;
      padding: 2px 0 2px 12px;
      margin: 28px 0 14px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .12em;
      color: #7c6af7;
      text-transform: uppercase;
  }

  /* ── KPI metric cards ── */
  .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
  }
  .kpi-card {
      background: #1a1f2e;
      border: 1px solid #2a2f42;
      border-radius: 10px;
      padding: 14px 16px;
  }
  .kpi-label {
      font-size: 11px;
      color: #8b92a5;
      text-transform: uppercase;
      letter-spacing: .08em;
      margin-bottom: 6px;
  }
  .kpi-value {
      font-size: 22px;
      font-weight: 700;
      color: #ffffff;
      line-height: 1.2;
  }
  .kpi-sub {
      font-size: 11px;
      color: #5dcaa5;
      margin-top: 4px;
  }
  .kpi-value.green  { color: #5dcaa5; }
  .kpi-value.red    { color: #f07b6b; }
  .kpi-value.purple { color: #a89bf7; }
  .kpi-value.amber  { color: #f5c842; }

  /* ── fund header card ── */
  .fund-header-card {
      background: linear-gradient(135deg, #1a1f2e 60%, #1e2340);
      border: 1px solid #2a2f42;
      border-radius: 14px;
      padding: 24px 28px;
      margin-bottom: 24px;
      position: relative;
  }
  .fund-number {
      font-size: 11px;
      color: #5a6080;
      font-weight: 600;
      letter-spacing: .1em;
      text-transform: uppercase;
      margin-bottom: 6px;
  }
  .fund-title {
      font-size: 26px;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 8px;
  }
  .fund-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
  }
  .badge-flexi   { background: #2d2a5e; color: #a89bf7; }
  .badge-large   { background: #1a3a2a; color: #5dcaa5; }
  .badge-index   { background: #1a2a3a; color: #5badf7; }
  .badge-hybrid  { background: #3a2a1a; color: #f5c842; }
  .badge-small   { background: #3a1a1a; color: #f07b6b; }

  /* ── holdings bar ── */
  .holding-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
  }
  .holding-name { font-size: 13px; color: #c8ccd8; width: 180px; flex-shrink: 0; }
  .holding-track {
      flex: 1;
      background: #1e2338;
      border-radius: 4px;
      height: 7px;
      overflow: hidden;
  }
  .holding-fill {
      height: 100%;
      border-radius: 4px;
      background: #7c6af7;
  }
  .holding-pct { font-size: 13px; font-weight: 600; color: #a89bf7; width: 48px; text-align: right; }

  /* ── insight / outlook box ── */
  .insight-box {
      background: #12181f;
      border-left: 3px solid #5dcaa5;
      border-radius: 0 10px 10px 0;
      padding: 14px 18px;
      margin: 14px 0;
      font-size: 13.5px;
      line-height: 1.75;
      color: #c0c8d8;
  }
  .insight-label {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: .1em;
      color: #5dcaa5;
      text-transform: uppercase;
      margin-bottom: 6px;
  }

  /* ── competitor box ── */
  .competitor-box {
      background: #12181f;
      border-left: 3px solid #5badf7;
      border-radius: 0 10px 10px 0;
      padding: 14px 18px;
      margin: 14px 0;
  }
  .competitor-label {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: .1em;
      color: #5badf7;
      text-transform: uppercase;
      margin-bottom: 6px;
  }
  .competitor-name {
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
      margin-bottom: 6px;
  }
  .competitor-desc { font-size: 13px; line-height: 1.7; color: #9ba3b8; }

  /* ── risk meter ── */
  .risk-row {
      display: flex;
      gap: 6px;
      align-items: center;
      margin: 10px 0;
  }
  .risk-dot {
      width: 28px; height: 8px;
      border-radius: 4px;
      background: #2a2f42;
  }
  .risk-dot.active-low    { background: #5dcaa5; }
  .risk-dot.active-mod    { background: #f5c842; }
  .risk-dot.active-high   { background: #f07b6b; }
  .risk-dot.active-vhigh  { background: #e83a3a; }

  /* ── tag pills ── */
  .tag-pill {
      display: inline-block;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
      margin: 3px;
      background: #252b3e;
      color: #8b92a5;
  }

  /* ── performance table ── */
  .perf-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .perf-table th {
      background: #1a1f2e;
      color: #8b92a5;
      padding: 8px 12px;
      text-align: left;
      font-size: 11px;
      letter-spacing: .06em;
      text-transform: uppercase;
      border-bottom: 1px solid #2a2f42;
  }
  .perf-table td { padding: 8px 12px; border-bottom: 1px solid #1e2338; color: #c8ccd8; }
  .perf-table tr:last-child td { border-bottom: none; }
  .ret-pos { color: #5dcaa5; font-weight: 600; }
  .ret-neg { color: #f07b6b; font-weight: 600; }
  .ret-mod { color: #f5c842; font-weight: 600; }
  .rank-top { color: #a89bf7; font-weight: 600; }
  .rank-mid { color: #8b92a5; }

  /* ── selector card ── */
  .selector-card {
      background: #1a1f2e;
      border: 1px solid #2a2f42;
      border-radius: 12px;
      padding: 20px 24px;
      margin-bottom: 20px;
  }

  /* ── download button ── */
  .stDownloadButton > button {
      background: #7c6af7 !important;
      color: white !important;
      border: none !important;
      border-radius: 8px !important;
      font-weight: 600 !important;
      padding: 10px 20px !important;
  }
  .stDownloadButton > button:hover { background: #9580ff !important; }
  .stButton > button {
      background: #1e2338 !important;
      color: #c8ccd8 !important;
      border: 1px solid #2a2f42 !important;
      border-radius: 8px !important;
  }

  /* hide streamlit default chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  FUND DATABASE – edit this to add more funds
# ────────────────────────────────────────────────────────────────────────────
FUND_DB = {
    "Parag Parikh Flexi Cap Fund": {
        "scheme_code": "122639",
        "amfi_code": "122639",
        "category": "Flexi Cap",
        "sub_category": "Global Allocation",
        "badge_class": "badge-flexi",
        "amc": "PPFAS Mutual Fund",
        "fund_manager": "Rajeev Thakkar, Raj Mehta, Rukun Tarachandani",
        "launch_date": "May 24, 2013",
        "benchmark": "Nifty 500 TRI",
        "aum_cr": 141447,
        "expense_ratio": 0.53,
        "exit_load": "2% (0-365d), 1% (365-730d)",
        "min_sip": 1000,
        "min_lumpsum": 1000,
        "cagr_1y": -3.25,
        "cagr_3y": 15.32,
        "cagr_5y": 15.10,
        "cagr_inception": 19.0,
        "std_dev": 8.42,
        "sharpe": -0.80,
        "alpha": -0.96,
        "beta": 0.72,
        "aum_milestone": "Crossed Rs.1 trillion (May 2025)",
        "calendar_returns": {
            2021: {"fund": 46.3, "benchmark": 29.9, "rank": "Top quartile"},
            2022: {"fund": -4.0, "benchmark": -9.8, "rank": "Top 3 in category"},
            2023: {"fund": 24.0, "benchmark": 20.2, "rank": "Top quartile"},
            2024: {"fund": 6.1,  "benchmark": 8.0,  "rank": "Mid-range"},
            2025: {"fund": -2.6, "benchmark": -0.8, "rank": "Mid-range"},
        },
        "holdings": [
            {"name": "HDFC Bank Ltd",    "pct": 7.94, "sector": "Banking"},
            {"name": "Power Grid Corp",  "pct": 6.99, "sector": "Power"},
            {"name": "Coal India Ltd",   "pct": 5.95, "sector": "Energy"},
            {"name": "ITC Ltd",          "pct": 5.40, "sector": "FMCG"},
            {"name": "ICICI Bank Ltd",   "pct": 4.92, "sector": "Banking"},
            {"name": "Alphabet (Google)","pct": 4.10, "sector": "Global Tech"},
            {"name": "Bajaj Holdings",   "pct": 4.40, "sector": "Finance"},
            {"name": "Maruti Suzuki",    "pct": 3.50, "sector": "Auto"},
        ],
        "allocation": {"Equity": 80.8, "Cash & Others": 19.2},
        "sector_allocation": {
            "Banking": 19.9, "Power": 7.0, "FMCG/Coal": 5.9,
            "Global Tech": 4.1, "Auto": 3.5, "Finance": 4.4, "Others": 55.2,
        },
        "risk_level": "Very High",
        "tags": ["Value Investing", "Global Exposure", "Low Volatility", "Direct Plan"],
        "insight": (
            "PPFAS follows a disciplined value-investing philosophy - buying high-quality businesses "
            "at reasonable prices and holding them for the long term. The fund's unique edge is its "
            "10-15% allocation to international stocks (Alphabet, Meta, Microsoft), providing natural "
            "currency hedging and access to global compounders unavailable in purely domestic funds. "
            "The low standard deviation of 8.42 makes this one of the least volatile equity funds "
            "in India despite its flexi-cap mandate - ideal for risk-conscious investors."
        ),
        "outlook": (
            "Recent underperformance in 2024-25 reflects a cautious, value-tilted stance during a "
            "momentum-driven market cycle. The large AUM (Rs.1.41 trillion) may begin to limit agility "
            "in mid/small-cap opportunities. However, the long-term 3-5 year outlook remains strong "
            "at 13-16% CAGR as global stocks recover and domestic value stocks re-rate. "
            "The fund's consistent top-quartile ranking in down markets (2022: best in category) "
            "demonstrates its capital-preservation strength."
        ),
        "competitors": [
            {
                "name": "HDFC Flexi Cap Fund",
                "reason": "Higher 5Y returns (16.78% vs 15.1%) but lacks international exposure. "
                          "Large-cap concentration 78.25%. Better if pure return-maximisation is goal.",
                "cagr_5y": 16.78,
                "expense": 0.77,
                "aum_cr": 62000,
            },
            {
                "name": "SBI Flexi Cap Fund",
                "reason": "More diversified across market caps, managed by Dinesh Balachandran. "
                          "Shorter high-performance track record vs PPFC. No global allocation.",
                "cagr_5y": 14.2,
                "expense": 0.60,
                "aum_cr": 28000,
            },
        ],
        "suitability": "Best for investors with 5+ year horizon who want equity growth with lower volatility and natural global diversification.",
        "tax_ltcg": "12.5% on gains above Rs.1.25L (after 1 year)",
        "tax_stcg": "20% (within 1 year)",
    },

    "UTI Nifty 50 Index Fund": {
        "scheme_code": "120716",
        "amfi_code": "120716",
        "category": "Large Cap",
        "sub_category": "Index (Passive)",
        "badge_class": "badge-index",
        "amc": "UTI Mutual Fund",
        "fund_manager": "Sharwan Kumar Goyal, Ayush Jain",
        "launch_date": "Jan 1, 2013",
        "benchmark": "Nifty 50 TRI",
        "aum_cr": 27849,
        "expense_ratio": 0.26,
        "exit_load": "Nil",
        "min_sip": 500,
        "min_lumpsum": 1000,
        "cagr_1y": -4.59,
        "cagr_3y": 10.24,
        "cagr_5y": 10.41,
        "cagr_inception": 11.82,
        "std_dev": 12.73,
        "sharpe": 0.57,
        "alpha": 0.57,
        "beta": 1.0,
        "aum_milestone": "Rs.27,849 Cr AUM (May 2026)",
        "calendar_returns": {
            2021: {"fund": 24.1, "benchmark": 24.1, "rank": "Tracks index"},
            2022: {"fund": 5.3,  "benchmark": 5.3,  "rank": "Tracks index"},
            2023: {"fund": 20.9, "benchmark": 20.9, "rank": "Tracks index"},
            2024: {"fund": 9.6,  "benchmark": 9.6,  "rank": "Tracks index"},
            2025: {"fund": 5.6,  "benchmark": 5.6,  "rank": "Tracks index"},
        },
        "holdings": [
            {"name": "HDFC Bank Ltd",       "pct": 10.74, "sector": "Banking"},
            {"name": "Reliance Industries", "pct": 8.79,  "sector": "Energy"},
            {"name": "ICICI Bank Ltd",      "pct": 8.21,  "sector": "Banking"},
            {"name": "Bharti Airtel Ltd",   "pct": 6.10,  "sector": "Telecom"},
            {"name": "Larsen & Toubro",     "pct": 4.29,  "sector": "Infra"},
            {"name": "Infosys Ltd",         "pct": 4.10,  "sector": "IT"},
            {"name": "TCS",                 "pct": 3.80,  "sector": "IT"},
            {"name": "Kotak Mahindra Bank", "pct": 3.20,  "sector": "Banking"},
        ],
        "allocation": {"Equity": 100.08, "Cash & Others": -0.08},
        "sector_allocation": {
            "Financial Services": 36.8, "Energy": 12.1, "IT": 11.2,
            "Consumer": 7.3, "Industrials": 6.5, "Telecom": 6.1, "Others": 20.0,
        },
        "risk_level": "Moderately High",
        "tags": ["Passive", "Low Cost", "Nifty 50", "Index Tracking"],
        "insight": (
            "This fund passively replicates the Nifty 50 index - India's top 50 companies by market "
            "capitalisation. As a passive fund, there is zero fund-manager risk and near-zero tracking "
            "error (0.02%). The ultra-low expense ratio of 0.26% (direct plan) means more of your "
            "money compounds over time. Ideal as the 'core' holding in any portfolio - set it, "
            "forget it, and let India's top companies do the work."
        ),
        "outlook": (
            "India's Nifty 50 is projected to grow at 10-13% CAGR over the long term, tracking "
            "nominal GDP growth plus corporate earnings expansion. Near-term headwinds include FII "
            "outflows and global rate environment, keeping 1-2 year returns at 8-10%. "
            "Over a 10-year horizon, Rs.10,000/month SIP in this fund would historically have grown "
            "to Rs.24-28 lakhs on Rs.12 lakh invested. The simplest, most reliable India equity bet."
        ),
        "competitors": [
            {
                "name": "Nippon India Nifty 50 Index Fund",
                "reason": "Lower expense ratio (0.10% vs 0.26%) tracking the same index. "
                          "Over 20 years, that 0.16% difference compounds to significant extra returns.",
                "cagr_5y": 10.45,
                "expense": 0.10,
                "aum_cr": 8500,
            },
            {
                "name": "HDFC Nifty 50 Index Fund",
                "reason": "Competitive expense ratio (0.20%), large AUM, good liquidity. "
                          "Slightly lower tracking error than UTI in recent years.",
                "cagr_5y": 10.43,
                "expense": 0.20,
                "aum_cr": 12000,
            },
        ],
        "suitability": "Best for first-time investors or as a core portfolio holding. 3+ year horizon, lowest-cost India equity exposure.",
        "tax_ltcg": "12.5% on gains above Rs.1.25L (after 1 year)",
        "tax_stcg": "20% (within 1 year)",
    },

    "ICICI Prudential Bluechip Fund": {
        "scheme_code": "120586",
        "amfi_code": "120586",
        "category": "Large Cap",
        "sub_category": "Active Management",
        "badge_class": "badge-large",
        "amc": "ICICI Prudential Mutual Fund",
        "fund_manager": "Sankaran Naren, Vaibhav Dusad, Sharmila D'mello",
        "launch_date": "May 23, 2008",
        "benchmark": "Nifty 100 TRI",
        "aum_cr": 75650,
        "expense_ratio": 0.70,
        "exit_load": "1% within 1 month",
        "min_sip": 100,
        "min_lumpsum": 100,
        "cagr_1y": -5.02,
        "cagr_3y": 13.51,
        "cagr_5y": 13.25,
        "cagr_inception": 14.53,
        "std_dev": 13.2,
        "sharpe": -0.29,
        "alpha": -1.9,
        "beta": 0.88,
        "aum_milestone": "Rs.75,650 Cr AUM - 2nd largest large cap fund",
        "calendar_returns": {
            2021: {"fund": 29.2, "benchmark": 25.6, "rank": "Top 30%"},
            2022: {"fund": 7.4,  "benchmark": 5.1,  "rank": "Top 30%"},
            2023: {"fund": 27.4, "benchmark": 22.1, "rank": "Top 30%"},
            2024: {"fund": 16.9, "benchmark": 14.0, "rank": "Top 30%"},
            2025: {"fund": 11.3, "benchmark": 9.8,  "rank": "Top 30%"},
        },
        "holdings": [
            {"name": "HDFC Bank Ltd",       "pct": 8.50, "sector": "Banking"},
            {"name": "Reliance Industries", "pct": 6.04, "sector": "Energy"},
            {"name": "Larsen & Toubro",     "pct": 5.48, "sector": "Infra"},
            {"name": "Bharti Airtel Ltd",   "pct": 5.39, "sector": "Telecom"},
            {"name": "ICICI Bank Ltd",      "pct": 3.30, "sector": "Banking"},
            {"name": "Infosys Ltd",         "pct": 3.10, "sector": "IT"},
            {"name": "Axis Bank",           "pct": 2.80, "sector": "Banking"},
            {"name": "Sun Pharma",          "pct": 2.50, "sector": "Pharma"},
        ],
        "allocation": {"Large Cap": 82.71, "Mid Cap": 7.97, "Small Cap": 0.6, "Non-Equity": 8.72},
        "sector_allocation": {
            "Financial Services": 28.5, "Energy": 10.2, "IT": 9.8,
            "Telecom": 7.4, "Industrials": 6.8, "Pharma": 5.1, "Others": 32.2,
        },
        "risk_level": "Moderately High",
        "tags": ["Blue Chip", "Active", "Consistent Outperformer", "Top 30% CRISIL"],
        "insight": (
            "ICICI Prudential Bluechip has maintained top-30-percentile ranking for 4 consecutive "
            "quarters (CRISIL). Managed by the legendary Sankaran Naren using a contrarian value "
            "approach - the fund buys quality companies when they are out of favour. The tactical "
            "8-10% non-equity buffer helps cushion during market corrections, a feature not found "
            "in most pure large-cap funds. Since inception in 2008, Rs.10,000 invested has grown to "
            "Rs.83,539 - a 13.65% CAGR over 16 years across multiple market cycles."
        ),
        "outlook": (
            "The fund has outperformed its benchmark (Nifty 100 TRI) across all time frames from "
            "6-month to 10-year. Large AUM (Rs.75,650 Cr) is a mild concern as deployment options "
            "narrow, but Naren's approach of holding cash/debt as a buffer has historically helped "
            "during corrections. Expected 3-year forward CAGR: 12-15%. 2025's underperformance "
            "(-5.02% 1Y) is typical for value-style funds in momentum markets - expect a strong "
            "mean reversion when market breadth normalises."
        ),
        "competitors": [
            {
                "name": "Canara Robeco Bluechip Equity Fund",
                "reason": "Lower expense ratio (0.51% vs 0.70%), 5Y returns of 16.5%, 59-stock portfolio. "
                          "Cost-efficient alternative for long-term investors.",
                "cagr_5y": 16.5,
                "expense": 0.51,
                "aum_cr": 15000,
            },
            {
                "name": "Nippon India Large Cap Fund",
                "reason": "Highest 5Y CAGR in large cap category (~21.8%, Value Research 5-star). "
                          "More aggressive stance, higher beta than ICICI Pru.",
                "cagr_5y": 21.8,
                "expense": 0.65,
                "aum_cr": 32000,
            },
        ],
        "suitability": "Best for investors wanting active large-cap management with a proven long-term track record. 3-5 year horizon minimum.",
        "tax_ltcg": "12.5% on gains above Rs.1.25L (after 1 year)",
        "tax_stcg": "20% (within 1 year)",
    },

    "HDFC Balanced Advantage Fund": {
        "scheme_code": "118989",
        "amfi_code": "118989",
        "category": "Hybrid",
        "sub_category": "Dynamic Asset Allocation",
        "badge_class": "badge-hybrid",
        "amc": "HDFC Mutual Fund",
        "fund_manager": "Gopal Agarwal, Anil Bamboli, Srinivasan Ramamurthy",
        "launch_date": "Feb 1, 1994",
        "benchmark": "Nifty 50 Hybrid Composite Debt 50:50 Index",
        "aum_cr": 105378,
        "expense_ratio": 1.27,
        "exit_load": "1% (excess 15%) within 1 year",
        "min_sip": 100,
        "min_lumpsum": 100,
        "cagr_1y": -5.5,
        "cagr_3y": 23.0,
        "cagr_5y": 26.0,
        "cagr_inception": 17.7,
        "std_dev": 11.4,
        "sharpe": 0.82,
        "alpha": 3.1,
        "beta": 0.75,
        "aum_milestone": "First hybrid fund to cross Rs.1 trillion AUM (Jun 2025)",
        "calendar_returns": {
            2021: {"fund": 27.8, "benchmark": 18.4, "rank": "Top quartile"},
            2022: {"fund": 8.1,  "benchmark": 4.2,  "rank": "Top quartile"},
            2023: {"fund": 31.3, "benchmark": 17.8, "rank": "Top quartile"},
            2024: {"fund": 16.7, "benchmark": 12.5, "rank": "Top quartile"},
            2025: {"fund": 7.2,  "benchmark": 5.9,  "rank": "#23 in category"},
        },
        "holdings": [
            {"name": "HDFC Bank Ltd",       "pct": 7.2,  "sector": "Banking"},
            {"name": "ICICI Bank Ltd",      "pct": 5.2,  "sector": "Banking"},
            {"name": "Bharti Airtel Ltd",   "pct": 3.09, "sector": "Telecom"},
            {"name": "Reliance Industries", "pct": 2.7,  "sector": "Energy"},
            {"name": "Govt Securities",     "pct": 20.0, "sector": "Debt"},
            {"name": "Infosys Ltd",         "pct": 2.4,  "sector": "IT"},
            {"name": "Axis Bank",           "pct": 2.1,  "sector": "Banking"},
            {"name": "REITs & InvITs",      "pct": 1.64, "sector": "Real Estate"},
        ],
        "allocation": {"Equity": 62.0, "Debt": 36.36, "REITs & InvIT": 1.64},
        "sector_allocation": {
            "Financial Services": 24.0, "Debt/Gsec": 20.0, "Energy": 8.0,
            "Telecom": 5.0, "IT": 4.5, "Real Estate": 1.64, "Others": 36.86,
        },
        "risk_level": "Moderately High",
        "tags": ["Dynamic Allocation", "Auto Rebalancing", "Debt + Equity", "30-Year Track Record"],
        "insight": (
            "HDFC BAF is India's only hybrid fund to cross Rs.1 trillion AUM - a testament to 30 years "
            "of investor trust. Its model-driven approach automatically shifts between equity (40-80%) "
            "and debt (20-60%) based on market valuations. When P/E ratios are high, it moves money "
            "to debt; when cheap, it loads up on equity. This means you never need to rebalance "
            "manually - the fund does it for you. The result: equity-like returns with meaningfully "
            "lower drawdowns than pure equity funds."
        ),
        "outlook": (
            "Currently leads the balanced advantage category across all time frames. 23% CAGR over "
            "3 years and 26% over 5 years (as of June 2025). The fund's model-based allocation "
            "currently holds ~62% equity given market valuations - balanced positioning for FY2026. "
            "Forward estimate: 12-15% CAGR over the next 3 years with significantly lower volatility "
            "than pure equity. The mandatory debt allocation (~35%) acts as an inbuilt shock absorber, "
            "making drawdowns 30-40% smaller than a pure equity fund in bear markets."
        ),
        "competitors": [
            {
                "name": "Edelweiss Balanced Advantage Fund",
                "reason": "Lower expense ratio (~0.40% direct) with competitive returns. "
                          "Much smaller AUM gives it more agility. Suitable for cost-conscious investors.",
                "cagr_5y": 18.2,
                "expense": 0.40,
                "aum_cr": 12000,
            },
            {
                "name": "Kotak Balanced Advantage Fund",
                "reason": "Simpler equity glide-path model, credible for first-time hybrid investors. "
                          "Lower AUM improves flexibility in stock selection.",
                "cagr_5y": 16.8,
                "expense": 0.55,
                "aum_cr": 18000,
            },
        ],
        "suitability": "Ideal for investors who want equity growth without riding full equity volatility. 3+ year horizon. Perfect for SIP investors who don't want to time the market.",
        "tax_ltcg": "12.5% on gains above Rs.1.25L (after 1 year) - taxed as equity",
        "tax_stcg": "20% (within 1 year)",
    },

    "Nippon India Small Cap Fund": {
        "scheme_code": "118778",
        "amfi_code": "118778",
        "category": "Small Cap",
        "sub_category": "High Growth / High Risk",
        "badge_class": "badge-small",
        "amc": "Nippon India Mutual Fund",
        "fund_manager": "Samir Rachh",
        "launch_date": "Sep 16, 2010",
        "benchmark": "Nifty Smallcap 250 TRI",
        "aum_cr": 61809,
        "expense_ratio": 0.67,
        "exit_load": "1% within 1 year",
        "min_sip": 100,
        "min_lumpsum": 5000,
        "cagr_1y": 1.0,
        "cagr_3y": 22.0,
        "cagr_5y": 22.86,
        "cagr_inception": 23.0,
        "std_dev": 19.8,
        "sharpe": 0.76,
        "alpha": 2.58,
        "beta": 1.18,
        "aum_milestone": "Subscription capped since July 2023 - protecting existing investors",
        "calendar_returns": {
            2021: {"fund": 74.3, "benchmark": 55.2, "rank": "Top 10%"},
            2022: {"fund": -2.0, "benchmark": -3.1, "rank": "Top 20%"},
            2023: {"fund": 48.9, "benchmark": 38.3, "rank": "Top 15%"},
            2024: {"fund": 26.1, "benchmark": 20.2, "rank": "Top 30%"},
            2025: {"fund": -4.7, "benchmark": -7.2, "rank": "Top 30%"},
        },
        "holdings": [
            {"name": "MCX India Ltd",       "pct": 2.07, "sector": "Finance"},
            {"name": "HDFC Bank Ltd",       "pct": 1.81, "sector": "Banking"},
            {"name": "Karur Vysya Bank",    "pct": 1.49, "sector": "Banking"},
            {"name": "Apar Industries",     "pct": 1.41, "sector": "Industrials"},
            {"name": "Deepak Nitrite",      "pct": 1.30, "sector": "Chemicals"},
            {"name": "Tube Investments",    "pct": 1.25, "sector": "Auto Ancillary"},
            {"name": "Birla Corp",          "pct": 1.18, "sector": "Cement"},
            {"name": "Sheela Foam",         "pct": 1.10, "sector": "Consumer"},
        ],
        "allocation": {"Small Cap": 72.5, "Mid Cap": 15.3, "Large Cap": 5.2, "Cash & Debt": 7.0},
        "sector_allocation": {
            "Industrials": 18.5, "Financial Services": 14.2, "Consumer": 12.1,
            "Chemicals": 9.8, "Auto Ancillary": 8.4, "Healthcare": 7.2, "Others": 29.8,
        },
        "risk_level": "Very High",
        "tags": ["Small Cap", "200+ Stocks", "CRISIL 4-Star", "Capped Subscriptions"],
        "insight": (
            "India's largest small-cap fund by AUM (Rs.61,809 Cr) with the strongest 14-year track "
            "record in the category. Managed by Samir Rachh since 2017 using a bottom-up stock "
            "selection approach across 200+ stocks - much more diversified than peers. The fund's "
            "subscription cap (since July 2023) protects existing investors by preventing AUM from "
            "growing too large for the small-cap universe. Rs.10,000 invested at inception (Sep 2010) "
            "has grown to Rs.1.81 lakh - a 23% annualised return over 14 years."
        ),
        "outlook": (
            "Small caps are inherently cyclical - 2025's -4.7% is normal after 48.9% in 2023 and "
            "26.1% in 2024. India's small-cap universe has significant 5-10 year upside as domestic "
            "consumption, manufacturing (PLI schemes), and formalisation of the economy drive "
            "earnings growth in smaller companies. Forward estimate: 16-20% CAGR over next 5 years. "
            "CAUTION: Expect 30-40% peak-to-trough drawdowns in any 2-year window. "
            "Strictly for investors with 7+ year horizon and high risk tolerance."
        ),
        "competitors": [
            {
                "name": "Quant Small Cap Fund",
                "reason": "5-year CAGR of 22.38% vs Nippon's 22.86% - virtually identical. "
                          "Uses VLRT quantitative model. More volatile but generates tactical alpha. "
                          "Best for high-risk, short-to-medium term investors.",
                "cagr_5y": 22.38,
                "expense": 0.64,
                "aum_cr": 28000,
            },
            {
                "name": "SBI Small Cap Fund",
                "reason": "Oldest, most disciplined small-cap fund. Superior downside protection. "
                          "Large AUM (~Rs.30,000 Cr) limits agility but suits conservative small-cap investors.",
                "cagr_5y": 20.8,
                "expense": 0.74,
                "aum_cr": 30000,
            },
        ],
        "suitability": "Strictly for investors with 7+ year horizon, high risk tolerance, and ability to stay invested through 30-40% drawdowns. Not suitable for short-term goals.",
        "tax_ltcg": "12.5% on gains above Rs.1.25L (after 1 year)",
        "tax_stcg": "20% (within 1 year)",
    },
}


# ────────────────────────────────────────────────────────────────────────────
#  RULE ENGINE – generates text insights from numbers (no AI needed)
# ────────────────────────────────────────────────────────────────────────────
def rule_engine_quick_verdict(fund: dict) -> str:
    c5 = fund["cagr_5y"]
    aum = fund["aum_cr"]
    exp = fund["expense_ratio"]
    sd  = fund["std_dev"]
    lines = []
    if c5 >= 20:    lines.append(f"Strong outperformer - {c5}% 5Y CAGR, significantly above category average.")
    elif c5 >= 14:  lines.append(f"Consistent performer - {c5}% 5Y CAGR, above category average.")
    else:           lines.append(f"Returns of {c5}% are broadly in line with category average.")
    if aum >= 50000:    lines.append(f"Large AUM of Rs.{aum:,} Cr ensures high liquidity and stability.")
    elif aum >= 10000:  lines.append(f"Mid-sized fund (Rs.{aum:,} Cr AUM) - good balance of agility and liquidity.")
    else:               lines.append(f"Smaller AUM of Rs.{aum:,} Cr provides high agility in stock selection.")
    if exp <= 0.30:     lines.append(f"Extremely cost-efficient at {exp}% expense ratio.")
    elif exp <= 0.80:   lines.append(f"Expense ratio of {exp}% is reasonable for this fund type.")
    else:               lines.append(f"Higher expense ratio of {exp}% - factor into long-term return expectations.")
    if sd <= 10:    lines.append(f"Low volatility (sd={sd}) - suitable for risk-conscious investors.")
    elif sd <= 15:  lines.append(f"Moderate volatility (sd={sd}) - balanced risk/return profile.")
    else:           lines.append(f"High volatility (sd={sd}) - requires long-term commitment (7+ years).")
    return "  ·  ".join(lines)


def get_risk_color(level: str) -> str:
    return {"Low": "#5dcaa5", "Moderate": "#5badf7",
            "Moderately High": "#f5c842", "High": "#f07b6b",
            "Very High": "#e83a3a"}.get(level, "#8b92a5")


def calc_sip_projection(monthly: float, years: int, cagr: float) -> float:
    r = (cagr / 100) / 12
    n = years * 12
    if r == 0: return monthly * n
    return monthly * (((1 + r) ** n - 1) / r) * (1 + r)


# ────────────────────────────────────────────────────────────────────────────
#  NAV FETCH from mfapi.in (free, no key needed)
# ────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_nav_history(scheme_code: str):
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            data = r.json()
            return data.get("data", [])[:365]
    except Exception:
        pass
    return []


@st.cache_data(ttl=86400)
def fetch_latest_nav(scheme_code: str):
    history = fetch_nav_history(scheme_code)
    if history:
        return float(history[0]["nav"])
    return None


# ────────────────────────────────────────────────────────────────────────────
#  CHART BUILDERS
# ────────────────────────────────────────────────────────────────────────────
def make_performance_chart(fund: dict) -> go.Figure:
    years = list(fund["calendar_returns"].keys())
    fund_returns = [fund["calendar_returns"][y]["fund"] for y in years]
    bench_returns = [fund["calendar_returns"][y]["benchmark"] for y in years]

    colors_fund  = ["#5dcaa5" if v >= 0 else "#f07b6b" for v in fund_returns]
    colors_bench = ["#7c6af7" if v >= 0 else "#a86af7" for v in bench_returns]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[str(y) for y in years], y=fund_returns,
        name=fund["amc"].split()[0] + " Fund",
        marker_color=colors_fund,
        text=[f"{v:+.1f}%" for v in fund_returns],
        textposition="outside",
        textfont=dict(size=12, color="#e0e0e0"),
    ))
    fig.add_trace(go.Bar(
        x=[str(y) for y in years], y=bench_returns,
        name=fund["benchmark"],
        marker_color=colors_bench,
        text=[f"{v:+.1f}%" for v in bench_returns],
        textposition="outside",
        textfont=dict(size=12, color="#e0e0e0"),
        opacity=0.7,
    ))
    fig.add_hline(y=0, line_color="#3a3f52", line_width=1)
    fig.update_layout(
        barmode="group",
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="#c8ccd8", size=13),
        legend=dict(orientation="h", y=1.1, x=0, font=dict(size=12)),
        margin=dict(l=10, r=10, t=40, b=10),
        height=320,
        yaxis=dict(
            gridcolor="#1e2338", zeroline=False,
            ticksuffix="%", tickfont=dict(size=11),
        ),
        xaxis=dict(tickfont=dict(size=12)),
    )
    return fig


def make_sector_chart(fund: dict) -> go.Figure:
    sectors = list(fund["sector_allocation"].keys())
    vals    = list(fund["sector_allocation"].values())
    colors  = ["#7c6af7","#5dcaa5","#5badf7","#f5c842","#f07b6b","#a89bf7","#5dcaa5","#f07b6b"]
    fig = go.Figure(go.Pie(
        labels=sectors, values=vals,
        hole=0.55,
        marker=dict(colors=colors[:len(sectors)], line=dict(color="#0e1117", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#e0e0e0"),
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font=dict(color="#c8ccd8"),
        legend=dict(font=dict(size=11), orientation="v"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=280,
        showlegend=False,
    )
    return fig


def make_nav_chart(scheme_code: str) -> go.Figure | None:
    history = fetch_nav_history(scheme_code)
    if not history:
        return None
    dates = [datetime.strptime(d["date"], "%d-%m-%Y") for d in history]
    navs  = [float(d["nav"]) for d in history]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=navs, mode="lines",
        line=dict(color="#7c6af7", width=2),
        fill="tozeroy",
        fillcolor="rgba(124,106,247,0.08)",
        hovertemplate="Rs.%{y:.2f}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font=dict(color="#c8ccd8"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=220,
        xaxis=dict(gridcolor="#1e2338", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#1e2338", tickprefix="Rs.", tickfont=dict(size=11)),
        showlegend=False,
    )
    return fig


def make_rolling_cagr_bar(fund: dict) -> go.Figure:
    periods = ["1 Year", "3 Year", "5 Year", "Since Inception"]
    values  = [fund["cagr_1y"], fund["cagr_3y"], fund["cagr_5y"], fund["cagr_inception"]]
    colors  = ["#5dcaa5" if v >= 0 else "#f07b6b" for v in values]
    fig = go.Figure(go.Bar(
        x=periods, y=values,
        marker_color=colors,
        text=[f"{v:+.2f}%" for v in values],
        textposition="outside",
        textfont=dict(size=13, color="#e0e0e0"),
    ))
    fig.add_hline(y=0, line_color="#3a3f52", line_width=1)
    fig.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font=dict(color="#c8ccd8"),
        margin=dict(l=10, r=10, t=30, b=10),
        height=260,
        yaxis=dict(gridcolor="#1e2338", ticksuffix="%", tickfont=dict(size=11)),
        xaxis=dict(tickfont=dict(size=12)),
        showlegend=False,
    )
    return fig


def make_sip_projection_chart(fund: dict) -> go.Figure:
    monthly = 10000
    years_range = list(range(1, 21))
    invested    = [monthly * y * 12 for y in years_range]
    projected   = [calc_sip_projection(monthly, y, fund["cagr_5y"]) for y in years_range]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years_range, y=invested, name="Total Invested",
        fill="tozeroy", fillcolor="rgba(91,173,247,0.08)",
        line=dict(color="#5badf7", width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=years_range, y=projected, name="Projected Value",
        fill="tonexty", fillcolor="rgba(124,106,247,0.10)",
        line=dict(color="#7c6af7", width=2.5),
        hovertemplate="Year %{x}: Rs.%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font=dict(color="#c8ccd8"),
        legend=dict(orientation="h", y=1.05, x=0),
        margin=dict(l=10, r=10, t=40, b=10),
        height=260,
        xaxis=dict(gridcolor="#1e2338", title="Years", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#1e2338", tickprefix="Rs.", tickfont=dict(size=11)),
    )
    return fig


# ────────────────────────────────────────────────────────────────────────────
#  PDF GENERATOR (HTML → download)
# ────────────────────────────────────────────────────────────────────────────
def generate_pdf_html(fund: dict, fund_name: str) -> str:
    cr = fund["calendar_returns"]
    rows = ""
    for yr, d in cr.items():
        fv, bv = d["fund"], d["benchmark"]
        fc = "color:#27c485" if fv >= 0 else "color:#f07b6b"
        bc = "color:#27c485" if bv >= 0 else "color:#f07b6b"
        rows += f"""
        <tr>
          <td>{yr}</td>
          <td style="{fc};font-weight:600">{fv:+.1f}%</td>
          <td style="{bc}">{bv:+.1f}%</td>
          <td>{d['rank']}</td>
        </tr>"""

    holdings_rows = ""
    for h in fund["holdings"][:8]:
        w = int(h["pct"] / 12 * 100)
        holdings_rows += f"""
        <tr>
          <td>{h['name']}</td>
          <td>{h['sector']}</td>
          <td>
            <div style="display:flex;align-items:center;gap:8px">
              <div style="flex:1;background:#2a2f42;border-radius:3px;height:6px">
                <div style="width:{w}%;background:#7c6af7;height:100%;border-radius:3px"></div>
              </div>
              <span style="font-weight:600;color:#a89bf7;min-width:42px">{h['pct']}%</span>
            </div>
          </td>
        </tr>"""

    comp_cards = ""
    for c in fund["competitors"]:
        diff = c["cagr_5y"] - fund["cagr_5y"]
        diff_str = f"+{diff:.2f}%" if diff > 0 else f"{diff:.2f}%"
        diff_col = "#27c485" if diff > 0 else "#f07b6b"
        comp_cards += f"""
        <div style="border:1px solid #2a2f42;border-radius:8px;padding:14px;margin-bottom:10px">
          <div style="font-weight:600;font-size:15px;margin-bottom:6px">{c['name']}</div>
          <div style="display:flex;gap:20px;font-size:12px;color:#8b92a5;margin-bottom:8px">
            <span>5Y CAGR: <b style="color:#ffffff">{c['cagr_5y']}%</b>
              <span style="color:{diff_col}"> ({diff_str} vs this fund)</span></span>
            <span>Expense: <b style="color:#ffffff">{c['expense']}%</b></span>
            <span>AUM: <b style="color:#ffffff">Rs.{c['aum_cr']:,} Cr</b></span>
          </div>
          <div style="font-size:13px;color:#9ba3b8;line-height:1.7">{c['reason']}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{fund_name} - SipCheck Report</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background:#0e1117; color:#e0e0e0; font-family:Arial,sans-serif; padding:32px; }}
    h1 {{ font-size:26px; color:#fff; margin-bottom:4px; }}
    h2 {{ font-size:15px; color:#7c6af7; letter-spacing:.08em; text-transform:uppercase;
          margin:24px 0 10px; border-left:3px solid #7c6af7; padding-left:10px; }}
    .badge {{ display:inline-block; padding:4px 12px; border-radius:16px;
              font-size:12px; font-weight:600; margin-top:6px; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:14px 0; }}
    .card {{ background:#1a1f2e; border:1px solid #2a2f42; border-radius:8px; padding:12px; }}
    .clabel {{ font-size:10px; color:#8b92a5; text-transform:uppercase; letter-spacing:.08em; }}
    .cval {{ font-size:20px; font-weight:700; color:#fff; margin-top:4px; }}
    .green {{ color:#5dcaa5; }} .red {{ color:#f07b6b; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; margin:10px 0; }}
    th {{ background:#1a1f2e; color:#8b92a5; padding:8px; text-align:left;
          font-size:11px; text-transform:uppercase; border-bottom:1px solid #2a2f42; }}
    td {{ padding:8px; border-bottom:1px solid #1e2338; }}
    .insight {{ background:#12181f; border-left:3px solid #5dcaa5;
                border-radius:0 8px 8px 0; padding:12px 16px; font-size:13px;
                line-height:1.75; color:#c0c8d8; margin:10px 0; }}
    .footer {{ margin-top:32px; padding-top:14px; border-top:1px solid #2a2f42;
               font-size:11px; color:#5a6080; line-height:1.6; }}
    .header-bar {{ display:flex; justify-content:space-between; align-items:center;
                   border-bottom:1px solid #2a2f42; padding-bottom:16px; margin-bottom:20px; }}
    .cas-logo {{ font-size:20px; font-weight:700; color:#7c6af7; }}
    .gen-date {{ font-size:12px; color:#8b92a5; }}
  </style>
</head>
<body>
  <div class="header-bar">
    <div class="cas-logo">SipCheck · Mutual Fund Report</div>
    <div class="gen-date">Generated: {datetime.now().strftime("%d %B %Y, %I:%M %p")}</div>
  </div>

  <div style="font-size:11px;color:#5a6080;margin-bottom:4px">Fund Report</div>
  <h1>{fund_name}</h1>
  <span class="badge" style="background:#2d2a5e;color:#a89bf7">{fund['category']} · {fund['sub_category']}</span>
  <div style="font-size:12px;color:#8b92a5;margin-top:8px">
    AMC: {fund['amc']} &nbsp;|&nbsp; Manager: {fund['fund_manager']} &nbsp;|&nbsp; Since: {fund['launch_date']}
  </div>

  <h2>Key metrics</h2>
  <div class="grid">
    <div class="card"><div class="clabel">AUM</div><div class="cval">Rs.{fund['aum_cr']:,} Cr</div></div>
    <div class="card"><div class="clabel">Expense Ratio</div><div class="cval">{fund['expense_ratio']}%</div></div>
    <div class="card"><div class="clabel">3-Year CAGR</div><div class="cval {'green' if fund['cagr_3y']>=0 else 'red'}">{fund['cagr_3y']:+.2f}%</div></div>
    <div class="card"><div class="clabel">5-Year CAGR</div><div class="cval {'green' if fund['cagr_5y']>=0 else 'red'}">{fund['cagr_5y']:+.2f}%</div></div>
    <div class="card"><div class="clabel">Since Inception</div><div class="cval green">{fund['cagr_inception']}%</div></div>
    <div class="card"><div class="clabel">Std. Deviation</div><div class="cval">{fund['std_dev']}</div></div>
    <div class="card"><div class="clabel">Sharpe Ratio</div><div class="cval">{fund['sharpe']}</div></div>
    <div class="card"><div class="clabel">Risk Level</div><div class="cval" style="font-size:15px">{fund['risk_level']}</div></div>
  </div>
  <div style="font-size:12px;color:#5dcaa5;margin-top:-4px">+ {fund['aum_milestone']}</div>

  <h2>Calendar year performance vs {fund['benchmark']}</h2>
  <table>
    <tr><th>Year</th><th>Fund Return</th><th>Benchmark</th><th>Category Rank</th></tr>
    {rows}
  </table>

  <h2>Top holdings</h2>
  <table>
    <tr><th>Stock / Asset</th><th>Sector</th><th>Allocation</th></tr>
    {holdings_rows}
  </table>

  <h2>Fund insight</h2>
  <div class="insight">{fund['insight']}</div>

  <h2>Future outlook</h2>
  <div class="insight" style="border-left-color:#5badf7">{fund['outlook']}</div>

  <h2>Competitor analysis</h2>
  {comp_cards}

  <h2>Suitability & taxation</h2>
  <div class="insight" style="border-left-color:#f5c842">
    <b>Who should invest:</b> {fund['suitability']}<br><br>
    <b>LTCG Tax:</b> {fund['tax_ltcg']}<br>
    <b>STCG Tax:</b> {fund['tax_stcg']}<br>
    <b>Exit Load:</b> {fund['exit_load']}
  </div>

  <div class="footer">
    <b>Disclaimer:</b> This report is generated by SipCheck for informational purposes only.
    Past performance is not indicative of future returns. All mutual fund investments are subject
    to market risk. Please read the Scheme Information Document carefully before investing.
    Data sourced from AMFI, mfapi.in, and publicly available fund factsheets.
    SEBI Registration required for investment advice. SipCheck is not a SEBI-registered advisor.
  </div>
</body>
</html>"""


# ────────────────────────────────────────────────────────────────────────────
#  MAIN PAGE
# ────────────────────────────────────────────────────────────────────────────
st.markdown("## Mutual Fund Report")
st.markdown(
    "<div style='color:#8b92a5;font-size:14px;margin-bottom:20px'>"
    "Select any scheme to generate a detailed fund report - holdings, performance, "
    "outlook, competitor analysis &amp; PDF download. No AI API required."
    "</div>", unsafe_allow_html=True
)

# ── Scheme selector ────────────────────────────────────────────────────────
st.markdown('<div class="section-bar">SELECT SCHEME</div>', unsafe_allow_html=True)

col_sel, col_mode = st.columns([3, 1])
with col_sel:
    selected = st.selectbox(
        "Choose a mutual fund scheme",
        options=list(FUND_DB.keys()),
        index=0,
        label_visibility="collapsed",
    )
with col_mode:
    plan = st.radio("Plan", ["Direct", "Regular"], horizontal=True)

fund = FUND_DB[selected]
nav_live = fetch_latest_nav(fund["scheme_code"])

# ── Fund header card ───────────────────────────────────────────────────────
badge_html = f'<span class="fund-badge {fund["badge_class"]}">{fund["category"]} · {fund["sub_category"]}</span>'
tags_html  = "".join(f'<span class="tag-pill">{t}</span>' for t in fund["tags"])
nav_str    = f"Rs.{nav_live:.4f}" if nav_live else "-"

st.markdown(f"""
<div class="fund-header-card">
  <div class="fund-number">Mutual Fund Report &nbsp;·&nbsp; {fund['amc']}</div>
  <div class="fund-title">{selected}</div>
  {badge_html}
  <div style="margin-top:10px;font-size:13px;color:#8b92a5">
    <b style="color:#c8ccd8">Fund Manager:</b> {fund['fund_manager']} &nbsp;|&nbsp;
    <b style="color:#c8ccd8">Benchmark:</b> {fund['benchmark']} &nbsp;|&nbsp;
    <b style="color:#c8ccd8">Launch:</b> {fund['launch_date']} &nbsp;|&nbsp;
    <b style="color:#c8ccd8">Live NAV:</b> {nav_str}
  </div>
  <div style="margin-top:10px">{tags_html}</div>
  <div style="margin-top:12px;font-size:12px;color:#5dcaa5">+ {fund['aum_milestone']}</div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-bar">KEY METRICS</div>', unsafe_allow_html=True)

c1y_cls = "green" if fund["cagr_1y"] >= 0 else "red"
c3y_cls = "green" if fund["cagr_3y"] >= 0 else "red"
c5y_cls = "green" if fund["cagr_5y"] >= 0 else "red"

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">AUM</div>
    <div class="kpi-value">Rs.{fund['aum_cr']:,}</div>
    <div class="kpi-sub">Crores</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Expense Ratio</div>
    <div class="kpi-value {'green' if fund['expense_ratio']<=0.5 else 'amber'}">{fund['expense_ratio']}%</div>
    <div class="kpi-sub">Direct plan</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">1-Year CAGR</div>
    <div class="kpi-value {c1y_cls}">{fund['cagr_1y']:+.2f}%</div>
    <div class="kpi-sub">Trailing returns</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">3-Year CAGR</div>
    <div class="kpi-value {c3y_cls}">{fund['cagr_3y']:+.2f}%</div>
    <div class="kpi-sub">Annualised</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">5-Year CAGR</div>
    <div class="kpi-value {c5y_cls}">{fund['cagr_5y']:+.2f}%</div>
    <div class="kpi-sub">Annualised</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Since Inception</div>
    <div class="kpi-value green">{fund['cagr_inception']}%</div>
    <div class="kpi-sub">CAGR</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Std. Deviation</div>
    <div class="kpi-value purple">{fund['std_dev']}</div>
    <div class="kpi-sub">{'Low volatility' if fund['std_dev']<=12 else 'High volatility'}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Sharpe Ratio</div>
    <div class="kpi-value {'green' if fund['sharpe']>0 else 'red'}">{fund['sharpe']}</div>
    <div class="kpi-sub">Risk-adjusted return</div>
  </div>
</div>
""", unsafe_allow_html=True)

# risk level
risk_col = get_risk_color(fund["risk_level"])
st.markdown(
    f'<div style="font-size:13px;color:#8b92a5;margin-bottom:4px">Risk level</div>'
    f'<div style="font-size:18px;font-weight:700;color:{risk_col};margin-bottom:16px">'
    f'▲ {fund["risk_level"]}</div>',
    unsafe_allow_html=True
)

# quick verdict from rule engine
verdict = rule_engine_quick_verdict(fund)
st.markdown(
    f'<div style="background:#1a1f2e;border:1px solid #2a2f42;border-radius:10px;'
    f'padding:14px 18px;font-size:13px;color:#c0c8d8;line-height:1.8;margin-bottom:20px">'
    f'<span style="color:#f5c842;font-weight:600;font-size:11px;text-transform:uppercase;'
    f'letter-spacing:.08em">Quick Verdict &nbsp;</span><br>{verdict}</div>',
    unsafe_allow_html=True
)

# ── Charts row ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-bar">RETURNS OVERVIEW</div>', unsafe_allow_html=True)
col_r1, col_r2 = st.columns(2)
with col_r1:
    st.markdown("<div style='font-size:13px;color:#8b92a5;margin-bottom:6px'>CAGR across periods</div>", unsafe_allow_html=True)
    st.plotly_chart(make_rolling_cagr_bar(fund), use_container_width=True, config={"displayModeBar": False})
with col_r2:
    st.markdown("<div style='font-size:13px;color:#8b92a5;margin-bottom:6px'>Live NAV - last 365 days</div>", unsafe_allow_html=True)
    nav_fig = make_nav_chart(fund["scheme_code"])
    if nav_fig:
        st.plotly_chart(nav_fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("NAV history not available offline. Connect to internet for live data.")

# ── Calendar year performance ───────────────────────────────────────────────
st.markdown('<div class="section-bar">CALENDAR YEAR PERFORMANCE</div>', unsafe_allow_html=True)
st.plotly_chart(make_performance_chart(fund), use_container_width=True, config={"displayModeBar": False})

# performance table
cr = fund["calendar_returns"]
rows_html = ""
for yr, d in cr.items():
    fv, bv = d["fund"], d["benchmark"]
    beat = "Yes" if fv > bv else "No"
    beat_col = "#5dcaa5" if fv > bv else "#f07b6b"
    fc   = "ret-pos" if fv >= 0 else "ret-neg"
    bc   = "ret-pos" if bv >= 0 else "ret-neg"
    rk   = "rank-top" if "Top" in d["rank"] else "rank-mid"
    rows_html += f"""<tr>
      <td>{yr}</td>
      <td class="{fc}">{fv:+.1f}%</td>
      <td class="{bc}">{bv:+.1f}%</td>
      <td class="{rk}">{d['rank']}</td>
      <td style="text-align:center;color:{beat_col};font-weight:600">{beat}</td>
    </tr>"""

st.markdown(f"""
<table class="perf-table">
  <thead>
    <tr><th>Year</th><th>Fund Return</th><th>{fund['benchmark']}</th><th>Category Rank</th><th>Outperformed?</th></tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
""", unsafe_allow_html=True)

# ── Holdings ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-bar">PORTFOLIO HOLDINGS</div>', unsafe_allow_html=True)
col_h1, col_h2 = st.columns([3, 2])

with col_h1:
    st.markdown("<div style='font-size:13px;color:#8b92a5;margin-bottom:12px'>Top holdings</div>", unsafe_allow_html=True)
    max_pct = max(h["pct"] for h in fund["holdings"])
    for h in fund["holdings"]:
        bar_w = int(h["pct"] / max_pct * 100)
        st.markdown(f"""
        <div class="holding-row">
          <span class="holding-name">{h['name']}</span>
          <div class="holding-track"><div class="holding-fill" style="width:{bar_w}%"></div></div>
          <span class="holding-pct">{h['pct']}%</span>
        </div>""", unsafe_allow_html=True)

    alloc_str = "  ·  ".join([f"<b style='color:#ffffff'>{k}</b> <span style='color:#7c6af7'>{v}%</span>"
                               for k, v in fund["allocation"].items()])
    st.markdown(f"<div style='font-size:12px;color:#8b92a5;margin-top:10px'>{alloc_str}</div>",
                unsafe_allow_html=True)

with col_h2:
    st.markdown("<div style='font-size:13px;color:#8b92a5;margin-bottom:6px'>Sector allocation</div>", unsafe_allow_html=True)
    st.plotly_chart(make_sector_chart(fund), use_container_width=True, config={"displayModeBar": False})

# ── SIP Projection ─────────────────────────────────────────────────────────
st.markdown('<div class="section-bar">SIP PROJECTION (Rs.10,000/month)</div>', unsafe_allow_html=True)
col_sip1, col_sip2 = st.columns([3, 2])

with col_sip1:
    st.plotly_chart(make_sip_projection_chart(fund), use_container_width=True, config={"displayModeBar": False})

with col_sip2:
    sip_yrs = st.slider("Investment horizon (years)", 1, 20, 10)
    sip_amt = st.number_input("Monthly SIP amount (Rs.)", min_value=500, max_value=500000, value=10000, step=500)
    projected_val = calc_sip_projection(sip_amt, sip_yrs, fund["cagr_5y"])
    total_invested = sip_amt * sip_yrs * 12
    gain = projected_val - total_invested
    multiplier = projected_val / total_invested

    st.markdown(f"""
    <div class="kpi-grid" style="grid-template-columns:1fr 1fr">
      <div class="kpi-card">
        <div class="kpi-label">Total Invested</div>
        <div class="kpi-value" style="font-size:18px">Rs.{total_invested:,.0f}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Projected Value</div>
        <div class="kpi-value green" style="font-size:18px">Rs.{projected_val:,.0f}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Estimated Gain</div>
        <div class="kpi-value green" style="font-size:18px">Rs.{gain:,.0f}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Wealth Multiplier</div>
        <div class="kpi-value purple" style="font-size:18px">{multiplier:.2f}x</div>
      </div>
    </div>
    <div style="font-size:11px;color:#5a6080;margin-top:8px">
      Based on 5Y CAGR of {fund['cagr_5y']}%. Projection is illustrative - not a guarantee.
    </div>
    """, unsafe_allow_html=True)

# ── Insight & Outlook ──────────────────────────────────────────────────────
st.markdown('<div class="section-bar">FUND INSIGHT & OUTLOOK</div>', unsafe_allow_html=True)

col_i1, col_i2 = st.columns(2)
with col_i1:
    st.markdown(f"""
    <div class="insight-box">
      <div class="insight-label">Fund Insight</div>
      {fund['insight']}
    </div>""", unsafe_allow_html=True)

with col_i2:
    st.markdown(f"""
    <div class="insight-box" style="border-left-color:#5badf7">
      <div class="insight-label" style="color:#5badf7">Future Outlook</div>
      {fund['outlook']}
    </div>""", unsafe_allow_html=True)

# ── Competitor Analysis ────────────────────────────────────────────────────
st.markdown('<div class="section-bar">COMPETITOR ANALYSIS</div>', unsafe_allow_html=True)

for comp in fund["competitors"]:
    diff     = comp["cagr_5y"] - fund["cagr_5y"]
    diff_str = f"+{diff:.2f}%" if diff > 0 else f"{diff:.2f}%"
    diff_col = "#5dcaa5" if diff > 0 else "#f07b6b"
    exp_diff = comp["expense"] - fund["expense_ratio"]
    exp_str  = f"+{exp_diff:.2f}%" if exp_diff > 0 else f"{exp_diff:.2f}%"
    exp_col  = "#f07b6b" if exp_diff > 0 else "#5dcaa5"

    st.markdown(f"""
    <div class="competitor-box">
      <div class="competitor-label">Better alternative?</div>
      <div class="competitor-name">{comp['name']}</div>
      <div style="display:flex;gap:20px;margin-bottom:10px;font-size:12px;color:#8b92a5">
        <span>5Y CAGR: <b style="color:#fff">{comp['cagr_5y']}%</b>
          <span style="color:{diff_col}"> ({diff_str} vs this fund)</span></span>
        <span>Expense: <b style="color:#fff">{comp['expense']}%</b>
          <span style="color:{exp_col}"> ({exp_str})</span></span>
        <span>AUM: <b style="color:#fff">Rs.{comp['aum_cr']:,} Cr</b></span>
      </div>
      <div class="competitor-desc">{comp['reason']}</div>
    </div>""", unsafe_allow_html=True)

# ── Suitability & Tax ──────────────────────────────────────────────────────
st.markdown('<div class="section-bar">SUITABILITY & TAXATION</div>', unsafe_allow_html=True)

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Who should invest</div>
      <div style="font-size:13px;color:#c0c8d8;margin-top:8px;line-height:1.7">{fund['suitability']}</div>
    </div>""", unsafe_allow_html=True)
with col_s2:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Taxation</div>
      <div style="font-size:13px;color:#c0c8d8;margin-top:8px;line-height:1.8">
        <b style="color:#f5c842">LTCG</b> - {fund['tax_ltcg']}<br>
        <b style="color:#f07b6b">STCG</b> - {fund['tax_stcg']}
      </div>
    </div>""", unsafe_allow_html=True)
with col_s3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Minimums & Exit Load</div>
      <div style="font-size:13px;color:#c0c8d8;margin-top:8px;line-height:1.8">
        Min SIP: <b style="color:#fff">Rs.{fund['min_sip']:,}</b><br>
        Min Lumpsum: <b style="color:#fff">Rs.{fund['min_lumpsum']:,}</b><br>
        Exit Load: <b style="color:#f07b6b">{fund['exit_load']}</b>
      </div>
    </div>""", unsafe_allow_html=True)

# ── PDF Download ───────────────────────────────────────────────────────────
st.markdown('<div class="section-bar">DOWNLOAD REPORT</div>', unsafe_allow_html=True)

pdf_html = generate_pdf_html(fund, selected)
col_dl1, col_dl2, _ = st.columns([2, 2, 4])

with col_dl1:
    st.download_button(
        label="Download PDF Report",
        data=pdf_html.encode("utf-8"),
        file_name=f"SipCheck_{selected.replace(' ','_')[:30]}_{datetime.now().strftime('%Y%m%d')}.html",
        mime="text/html",
        use_container_width=True,
    )
with col_dl2:
    if st.button("Refresh Live NAV", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown(
    "<div style='font-size:11px;color:#5a6080;margin-top:8px'>"
    "Tip: Open the downloaded HTML file in Chrome → File → Print → Save as PDF for a clean print."
    "</div>", unsafe_allow_html=True
)

# ── Disclaimer ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:32px;padding-top:16px;border-top:1px solid #1e2338;
     font-size:11px;color:#5a6080;line-height:1.7">
  <b>Disclaimer:</b> This report is generated by SipCheck for informational and educational purposes only.
  Past performance is not indicative of future returns. All mutual fund investments are subject to market risk.
  Please read the Scheme Information Document (SID) carefully before investing. Data sourced from AMFI,
  mfapi.in, and publicly available fund factsheets. SipCheck is not a SEBI-registered investment advisor.
  Consult a qualified financial advisor before making investment decisions.
</div>
""", unsafe_allow_html=True)

# ── Fund Library (57 funds) + Request a Scheme ─────────────────────────────
from fund_registry_v2 import render_registry_browser, render_request_scheme
render_registry_browser(deep_dive_names=list(FUND_DB.keys()))
render_request_scheme(existing_names=list(FUND_DB.keys()))
