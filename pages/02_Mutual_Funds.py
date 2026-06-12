# MF Hub page - placeholder
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Mutual Funds — CAS 360", page_icon="🏦", layout="wide")
from sidebar_v2 import render_sidebar
render_sidebar()


st.markdown("""
<style>
#MainMenu {visibility:hidden;} footer {visibility:hidden;}
.stApp { background:#0d0d24; color:#f0f0ff; }
section[data-testid="stSidebar"] { background:#0d0d24; border-right:1px solid rgba(139,92,246,0.15); }
.block-container { padding:1.5rem 2rem; }
.mkt-header { font-size:1.6rem; font-weight:700; color:#f0f0ff; margin-bottom:0.25rem; }
.mkt-sub { font-size:0.82rem; color:#6b7280; margin-bottom:1.5rem; }
.section-title {
    font-size:0.72rem; font-weight:600; color:#8b5cf6;
    text-transform:uppercase; letter-spacing:0.08em;
    margin:1.5rem 0 0.75rem; border-left:3px solid #8b5cf6; padding-left:10px;
}
.fund-card {
    background:#111130; border:1px solid rgba(139,92,246,0.15);
    border-radius:10px; padding:0.85rem 1rem; margin-bottom:0.5rem;
}
.fund-name { font-size:0.83rem; font-weight:500; color:#f0f0ff; }
.fund-meta { font-size:0.73rem; color:#6b7280; margin-top:3px; }
.up   { color:#10b981; font-weight:600; }
.down { color:#ef4444; font-weight:600; }
.watch-card {
    background:#111130; border:1px solid rgba(16,185,129,0.25);
    border-radius:10px; padding:1rem; margin-bottom:0.5rem;
    border-left:3px solid #10b981;
}
.nav-big { font-size:1.3rem; font-weight:700; color:#f0f0ff; }
.badge-live {
    display:inline-block; background:#064e3b; color:#10b981;
    font-size:0.68rem; font-weight:600; padding:2px 8px;
    border-radius:10px; margin-left:6px;
}
</style>
""", unsafe_allow_html=True)

MFAPI = "https://api.mfapi.in/mf"

TOP_FUNDS = {
    "Large Cap": [
        {"code":"119598","name":"Mirae Asset Large Cap"},
        {"code":"120503","name":"Axis Bluechip Fund"},
        {"code":"125354","name":"SBI Bluechip Fund"},
        {"code":"100016","name":"HDFC Top 100 Fund"},
    ],
    "Mid Cap": [
        {"code":"119847","name":"Mirae Asset Midcap"},
        {"code":"120841","name":"Axis Midcap Fund"},
        {"code":"100236","name":"HDFC Mid-Cap Opp"},
        {"code":"119062","name":"Kotak Emerging Equity"},
    ],
    "Small Cap": [
        {"code":"120828","name":"Axis Small Cap Fund"},
        {"code":"125497","name":"DSP Small Cap Fund"},
        {"code":"100232","name":"HDFC Small Cap Fund"},
        {"code":"135800","name":"Nippon India Small Cap"},
    ],
    "ELSS": [
        {"code":"120503","name":"Axis Long Term Equity"},
        {"code":"120716","name":"Mirae Tax Saver"},
        {"code":"100026","name":"HDFC TaxSaver"},
    ],
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_nav(code):
    try:
        r = requests.get(f"{MFAPI}/{code}", timeout=8)
        if r.status_code != 200: return {}
        data = r.json()
        if not data.get("data"): return {}
        d0 = data["data"][0]; d1 = data["data"][1] if len(data["data"])>1 else d0
        nav   = float(d0["nav"]); prev = float(d1["nav"])
        chg   = nav - prev; pct = (chg/prev)*100 if prev else 0
        return {
            "name": data["meta"]["scheme_name"],
            "nav": nav, "prev": prev,
            "change": chg, "pct": pct,
            "date": d0["date"],
        }
    except: return {}

@st.cache_data(ttl=86400, show_spinner=False)
def get_history(code, days=90):
    try:
        r = requests.get(f"{MFAPI}/{code}", timeout=10)
        if r.status_code != 200: return pd.DataFrame()
        df = pd.DataFrame(r.json().get("data",[]))
        df["date"] = pd.to_datetime(df["date"], dayfirst=True)
        df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
        df = df.dropna().sort_values("date")
        cutoff = datetime.now() - timedelta(days=days)
        return df[df["date"] >= cutoff].reset_index(drop=True)
    except: return pd.DataFrame()

def get_watchlist():
    if "wl" not in st.session_state: st.session_state.wl = []
    return st.session_state.wl

def add_watch(code, name):
    wl = get_watchlist()
    if len(wl) >= 5: return "full"
    if any(w["code"]==code for w in wl): return "exists"
    wl.append({"code":code,"name":name}); return "ok"

def remove_watch(code):
    st.session_state.wl = [w for w in get_watchlist() if w["code"]!=code]

# ── PAGE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="mkt-header">🏦 Mutual Fund Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="mkt-sub">Live NAVs from mfapi.in · Updated daily after market close</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Top Performers", "⭐ My Watchlist (max 5)"])

# ── TAB 1: TOP PERFORMERS ─────────────────────────────────────────────────────
with tab1:
    cat_cols = st.columns(len(TOP_FUNDS))
    for ci, (cat, funds) in enumerate(TOP_FUNDS.items()):
        with cat_cols[ci]:
            st.markdown(f'<div class="section-title">{cat}</div>', unsafe_allow_html=True)
            for f in funds:
                nav = get_nav(f["code"])
                if not nav:
                    st.markdown(f'<div class="fund-card"><div class="fund-name">{f["name"]}</div><div class="fund-meta">Loading…</div></div>',
                                unsafe_allow_html=True)
                    continue
                css = "up" if nav["pct"]>=0 else "down"
                arr = "▲" if nav["pct"]>=0 else "▼"
                st.markdown(f"""
                <div class="fund-card">
                    <div class="fund-name">{f['name']}</div>
                    <div class="fund-meta">
                        NAV ₹{nav['nav']:.2f} &nbsp;
                        <span class="{css}">{arr} {abs(nav['pct']):.2f}%</span>
                        &nbsp;· {nav['date']}
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button("＋ Add to Watchlist", key=f"add_{f['code']}_{ci}",
                              use_container_width=True):
                    res = add_watch(f["code"], f["name"])
                    if res=="ok": st.toast(f"✅ Added {f['name'][:30]}")
                    elif res=="full": st.toast("⚠️ Watchlist full — max 5 funds")
                    else: st.toast("Already in watchlist")

# ── TAB 2: WATCHLIST ──────────────────────────────────────────────────────────
with tab2:
    wl = get_watchlist()
    if not wl:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#6b7280;">
            <div style="font-size:2rem;margin-bottom:1rem">⭐</div>
            <div>Your watchlist is empty.</div>
            <div style="font-size:0.8rem;margin-top:6px">Add up to 5 funds from the Top Performers tab.</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.caption(f"Tracking {len(wl)}/5 funds")
        wl_cols = st.columns(min(len(wl), 3))
        for i, w in enumerate(wl):
            nav = get_nav(w["code"])
            with wl_cols[i % 3]:
                if nav:
                    css = "up" if nav["pct"]>=0 else "down"
                    arr = "▲" if nav["pct"]>=0 else "▼"
                    st.markdown(f"""
                    <div class="watch-card">
                        <div class="fund-meta">{w['name'][:40]}</div>
                        <div class="nav-big">₹{nav['nav']:.2f}
                            <span class="badge-live">LIVE</span>
                        </div>
                        <div class="{css}">{arr} ₹{abs(nav['change']):.2f} ({nav['pct']:+.2f}%)</div>
                        <div class="fund-meta" style="margin-top:6px">prev ₹{nav['prev']:.2f} · {nav['date']}</div>
                    </div>""", unsafe_allow_html=True)
                if st.button("✕ Remove", key=f"rm_{w['code']}", use_container_width=True):
                    remove_watch(w["code"]); st.rerun()

        # Comparison chart
        if len(wl) >= 2:
            st.markdown('<div class="section-title">Performance Comparison (Normalised to 100)</div>',
                        unsafe_allow_html=True)
            days_opt = st.select_slider("Period", [7,30,90,180,365], value=30,
                                         format_func=lambda x: f"{x} days")
            import plotly.graph_objects as go
            colors = ["#8b5cf6","#10b981","#f59e0b","#3b82f6","#ef4444"]
            fig = go.Figure()
            for idx, w in enumerate(wl):
                df = get_history(w["code"], days=days_opt+5)
                if df.empty or len(df)<2: continue
                cutoff = df["date"].max() - pd.Timedelta(days=days_opt)
                df = df[df["date"]>=cutoff]
                base = df["nav"].iloc[0]
                norm = (df["nav"]/base)*100
                fig.add_trace(go.Scatter(
                    x=df["date"], y=norm, mode="lines",
                    name=w["name"][:25],
                    line=dict(color=colors[idx%len(colors)], width=2),
                    hovertemplate="%{y:.1f}<extra></extra>",
                ))
            fig.update_layout(
                height=300, paper_bgcolor="#111130", plot_bgcolor="#0d0d24",
                margin=dict(l=8,r=8,t=10,b=8),
                font=dict(color="#6b7280",size=10),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                xaxis=dict(gridcolor="rgba(139,92,246,0.1)",showgrid=True,zeroline=False),
                yaxis=dict(gridcolor="rgba(139,92,246,0.1)",showgrid=True,zeroline=False),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;color:#374151;font-size:0.72rem;">
    NAV data from mfapi.in · AMFI India · For informational purposes only
</div>""", unsafe_allow_html=True)