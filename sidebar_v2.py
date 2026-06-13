# ──────────────────────────────────────────────────────────────────
#  CAS 360 v2.2 – UNIFIED SIDEBAR  (sidebar_v2.py)
#  Place in PROJECT ROOT next to dashboard.py.
#
#  Use on every page (dashboard.py + each file in pages/):
#
#      from sidebar_v2 import render_sidebar
#      render_sidebar()
#
#  Also requires .streamlit/config.toml to contain:
#      [client]
#      showSidebarNavigation = false
# ──────────────────────────────────────────────────────────────────
import os
import streamlit as st

NAV = [
    ("🏠   SipCheck Home",   "dashboard.py"),
    ("📈  Live Markets",     "pages/01_Markets.py"),
    ("🏦  MF Hub",           "pages/02_Mutual_Funds.py"),
    ("📰  News & Pulse",     "pages/04_News.py"),
    ("🎯  Goal Tracker",     "pages/05_Goals.py"),
    ("👨‍👩‍👧  Family Wealth",    "pages/06_Family_Planner.py"),
    ("📊  MF Report Pro",    "pages/07_MF_Report.py"),
]


def render_sidebar():
    # Fix: black band/border at top of every page — make Streamlit's header transparent
    st.markdown(
        """<style>
        header[data-testid="stHeader"]{background:transparent !important;backdrop-filter:none !important;}
        header[data-testid="stHeader"] *{background:transparent !important;}
        div[data-testid="stToolbar"]{background:transparent !important;}
        div[data-testid="stDecoration"]{display:none !important;}
        div[data-testid="stStatusWidget"]{background:transparent !important;}
        </style>""",
        unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(
            " ".join(line.strip() for line in """
            <div style="padding:0.4rem 0 1.1rem;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:1.35rem;font-weight:700;">
            <span style="color:#f0f0ff;">Sip</span>
            <span style="background:linear-gradient(90deg,#8b5cf6,#22d3ee);-webkit-background-clip:text;background-clip:text;color:transparent;">Check</span>
            <span style="color:#8b5cf6;">📊</span></div>
            <div style="font-size:0.6rem;letter-spacing:0.22em;color:#6b7280;font-weight:600;">PORTFOLIO INTELLIGENCE · v2.3</div>
            <div style="font-size:0.68rem;color:#8b93a7;margin-top:4px;font-style:italic;">Track your SIP. Grow your Wealth.</div>
            </div>""".splitlines() if line.strip()),
            unsafe_allow_html=True)

        for label, path in NAV:
            if os.path.exists(path):
                st.page_link(path, label=label, use_container_width=True)

        st.markdown(
            """<div style="margin-top:1.2rem;padding-top:0.9rem;border-top:1px solid rgba(139,92,246,0.15);font-size:0.62rem;color:#374151;letter-spacing:0.06em;">Your data never leaves your device.</div>""",
            unsafe_allow_html=True)
