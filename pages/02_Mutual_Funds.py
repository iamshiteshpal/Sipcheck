# MF Hub page — Under Development
import streamlit as st

st.set_page_config(page_title="MF Hub — SipCheck", page_icon="🏦", layout="wide")
from sidebar_v2 import render_sidebar
render_sidebar()

st.markdown("""
<style>
#MainMenu {visibility:hidden;} footer {visibility:hidden;}
.stApp { background:#0d0d24; color:#f0f0ff; }
section[data-testid="stSidebar"] { background:#0d0d24; border-right:1px solid rgba(139,92,246,0.15); }
.block-container { padding:0; }
</style>""", unsafe_allow_html=True)

st.markdown("""
<div style="min-height:82vh;display:flex;align-items:center;justify-content:center;">
  <div style="text-align:center;max-width:480px;padding:2rem;">
    <div style="font-size:4rem;margin-bottom:1rem;">🔧</div>
    <div style="font-size:1.7rem;font-weight:800;color:#f0f0ff;margin-bottom:0.5rem;">
      MF Hub — Coming Soon
    </div>
    <div style="font-size:0.9rem;color:#6b7280;line-height:1.65;margin-bottom:1.5rem;">
      We're building something powerful here — a dedicated mutual fund explorer
      with live NAV tracking, category comparisons, fund-level analytics, and
      portfolio overlap detection.
    </div>
    <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:1.8rem;">
      <span style="background:rgba(139,92,246,0.12);color:#8b5cf6;font-size:0.75rem;
                   font-weight:600;padding:4px 12px;border-radius:20px;">📊 NAV Tracker</span>
      <span style="background:rgba(16,185,129,0.1);color:#10b981;font-size:0.75rem;
                   font-weight:600;padding:4px 12px;border-radius:20px;">🔍 Fund Explorer</span>
      <span style="background:rgba(245,158,11,0.1);color:#f59e0b;font-size:0.75rem;
                   font-weight:600;padding:4px 12px;border-radius:20px;">📈 Category Charts</span>
      <span style="background:rgba(99,179,237,0.1);color:#63b3ed;font-size:0.75rem;
                   font-weight:600;padding:4px 12px;border-radius:20px;">🔀 Overlap Detector</span>
    </div>
    <div style="background:rgba(139,92,246,0.07);border:1px solid rgba(139,92,246,0.18);
                border-radius:12px;padding:0.9rem 1.2rem;margin-bottom:1.5rem;
                font-size:0.8rem;color:#9ca3af;line-height:1.5;">
      Meanwhile, upload your CAS file on the
      <strong style="color:#f0f0ff;">SipCheck Home</strong> page to see your
      full portfolio analysis, XIRR, SIP mandates, and fund breakdown — all from your own data.
    </div>
    <div style="font-size:0.72rem;color:#374151;">
      🔧 Under active development &nbsp;·&nbsp; SipCheck v2.0
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
