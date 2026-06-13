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
    ("📰  News & Pulse",     "pages/04_News.py"),
    ("🎯  Goal Tracker",     "pages/05_Goals.py"),
    ("👨‍👩‍👧  Family Wealth",    "pages/06_Family_Planner.py"),
    ("📊  MF Report Pro",    "pages/07_MF_Report.py"),
    ("🔒  Reconciliation",   "pages/08_Reconciliation.py"),
]

# Pages that are under development — shown in nav but with a Coming Soon badge
NAV_WIP = [
    ("🏦  MF Hub",  "pages/02_Mutual_Funds.py"),
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

        # WIP items — grayed out with Coming Soon badge, still navigable
        st.markdown("""<style>
        .wip-nav-item {
            display:flex; align-items:center; justify-content:space-between;
            padding:0.45rem 0.75rem; border-radius:8px; margin-bottom:2px;
            background:rgba(139,92,246,0.04);
            border:1px solid rgba(139,92,246,0.08);
            cursor:pointer; text-decoration:none; width:100%; box-sizing:border-box;
        }
        .wip-nav-item:hover { background:rgba(139,92,246,0.09); }
        .wip-nav-label { font-size:0.85rem; color:#4b5563; font-weight:500; }
        .wip-badge {
            font-size:0.58rem; font-weight:700; letter-spacing:0.05em;
            background:rgba(245,158,11,0.15); color:#f59e0b;
            padding:1px 6px; border-radius:6px; white-space:nowrap;
        }
        </style>""", unsafe_allow_html=True)

        for label, path in NAV_WIP:
            if os.path.exists(path):
                st.page_link(path, label=f"{label}", use_container_width=True)
                st.markdown(
                    f'<div style="margin-top:-8px;margin-bottom:4px;padding:0 0.75rem;">'
                    f'<span style="font-size:0.62rem;color:#f59e0b;background:rgba(245,158,11,0.12);'
                    f'padding:1px 7px;border-radius:6px;font-weight:700;letter-spacing:0.04em;">'
                    f'🔧 Coming Soon</span></div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            """<div style="margin-top:1.2rem;padding-top:0.9rem;border-top:1px solid rgba(139,92,246,0.15);font-size:0.62rem;color:#374151;letter-spacing:0.06em;">Your data never leaves your device.</div>""",
            unsafe_allow_html=True)
