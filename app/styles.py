import streamlit as st


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
        .stApp::after {
          content: '';
          position: fixed;
          inset: 0;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
          pointer-events: none;
          z-index: 9999;
        }
        [data-testid="stSidebar"] {
          background: var(--bg2) !important;
          border-right: 1px solid var(--border) !important;
        }
        [data-testid="stSidebar"] * { font-family: 'Instrument Sans', sans-serif !important; }
        div[data-testid="stMetric"] {
          background: var(--bg2) !important;
          border: 1px solid var(--border) !important;
          border-radius: 12px !important;
          padding: 18px 20px !important;
          transition: border-color .25s, transform .2s;
        }
        div[data-testid="stMetric"]:hover {
          border-color: var(--border-hi) !important;
          transform: translateY(-2px);
        }
        div[data-testid="stMetricValue"] > div {
          font-family: 'IBM Plex Mono', monospace !important;
          font-size: 20px !important;
          font-weight: 600 !important;
          color: #f7fafc !important;
        }
        div[data-testid="stMetricLabel"] > div {
          font-size: 10px !important;
          color: var(--muted) !important;
          text-transform: uppercase;
          letter-spacing: 1.4px;
          font-weight: 500 !important;
        }
        div[data-testid="stMetricDelta"] > div { font-size: 11px !important; }
        [data-testid="stVerticalBlockBorderWrapper"] > div > div {
          background: var(--bg2) !important;
          border: 1px solid var(--border) !important;
          border-radius: 14px !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] > div > div:hover {
          border-color: rgba(99,179,237,0.2) !important;
        }
        [data-testid="stDataFrame"] {
          border-radius: 10px !important;
          overflow: hidden;
          border: 1px solid var(--border) !important;
        }
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stTextInput"] input {
          background: var(--bg3) !important;
          border: 1px solid var(--border) !important;
          border-radius: 8px !important;
          color: var(--text) !important;
        }
        [data-testid="stTextInput"] input { font-family: 'IBM Plex Mono', monospace !important; }
        [data-testid="stFileUploader"] {
          background: rgba(99,179,237,0.03) !important;
          border: 2px dashed rgba(99,179,237,0.2) !important;
          border-radius: 14px !important;
        }
        [data-testid="stSegmentedControl"] > div {
          background: var(--bg3) !important;
          border: 1px solid var(--border) !important;
          border-radius: 8px !important;
        }
        [data-testid="stSegmentedControl"] button[aria-checked="true"] {
          background: linear-gradient(135deg,#2b6cb0,#553c9a) !important;
          color: #fff !important;
          border-radius: 6px !important;
        }
        hr { border-color: var(--border) !important; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: var(--faint); border-radius: 4px; }
        .card { background: var(--bg2); border: 1px solid var(--border); border-radius: 14px; padding: 22px 24px; margin-bottom: 16px; position: relative; }
        .card-title { font-family: 'Syne', sans-serif; font-size: 11px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 14px; }
        .pill-gain { display: inline-flex; align-items: center; gap: 4px; background: rgba(72,187,120,0.1); border: 1px solid rgba(72,187,120,0.25); color: var(--gain); font-family: 'IBM Plex Mono',monospace; font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 20px; }
        .pill-loss { display: inline-flex; align-items: center; gap: 4px; background: rgba(252,129,129,0.1); border: 1px solid rgba(252,129,129,0.25); color: var(--loss); font-family: 'IBM Plex Mono',monospace; font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 20px; }
        .notice { background: rgba(99,179,237,0.05); border: 1px solid rgba(99,179,237,0.15); border-left: 3px solid var(--accent); border-radius: 0 10px 10px 0; padding: 12px 16px; font-size: 13px; color: var(--muted); margin-bottom: 22px; display: flex; align-items: flex-start; gap: 10px; }
        .section-sep { font-size: 10px; font-weight: 700; color: var(--faint); text-transform: uppercase; letter-spacing: 2px; margin: 24px 0 12px; display: flex; align-items: center; gap: 10px; }
        .section-sep::after { content:''; flex:1; height:1px; background: var(--border); }
        .page-title { font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 800; color: #f7fafc; letter-spacing: -0.5px; margin-bottom: 4px; }
        .page-sub { font-size: 13px; color: var(--muted); margin-bottom: 22px; }
        .sip-card { background: var(--bg3); border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
        .alloc-row { display: flex; align-items: center; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid var(--border); }
        .alloc-dot { width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:8px; }
        .alert-card { border-left: 3px solid; border-radius: 0 10px 10px 0; padding: 12px 16px; margin-bottom: 10px; background: var(--bg2); }
        div[data-testid="stAppViewBlockContainer"] { padding-top: 2.5rem !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
