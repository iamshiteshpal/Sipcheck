# SIP Simulator page - placeholder
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="SIP Simulator — CAS 360", page_icon="📊", layout="wide")

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
.result-card {
    background:#111130; border:1px solid rgba(139,92,246,0.2);
    border-radius:12px; padding:1.2rem 1.4rem; text-align:center;
}
.result-label { font-size:0.72rem; color:#6b7280; text-transform:uppercase;
                letter-spacing:0.06em; margin-bottom:4px; }
.result-value { font-size:1.5rem; font-weight:700; color:#f0f0ff; }
.result-gain  { font-size:0.82rem; color:#10b981; font-weight:600; margin-top:3px; }
.winner-box {
    background:#0a1a0f; border:1px solid #10b981;
    border-radius:12px; padding:1rem 1.4rem; margin-top:1rem;
}
.input-card {
    background:#111130; border:1px solid rgba(139,92,246,0.15);
    border-radius:12px; padding:1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ── SIP math ──────────────────────────────────────────────────────────────────
def sip_fv(monthly, annual_rate, years):
    r = (annual_rate/100)/12
    n = years*12
    if r == 0: return monthly*n
    return monthly*(((1+r)**n - 1)/r)*(1+r)

ASSETS = {
    "Nifty 50 Index":   {"rate":12.5, "color":"#10b981", "icon":"📈"},
    "Large Cap MF":     {"rate":11.5, "color":"#8b5cf6", "icon":"🏦"},
    "Mid Cap MF":       {"rate":14.0, "color":"#3b82f6", "icon":"📊"},
    "Small Cap MF":     {"rate":16.0, "color":"#f59e0b", "icon":"🚀"},
    "Gold":             {"rate": 8.5, "color":"#eab308", "icon":"🥇"},
    "Debt Fund":        {"rate": 7.0, "color":"#6b7280", "icon":"🏛️"},
    "Fixed Deposit":    {"rate": 6.5, "color":"#374151", "icon":"🏦"},
    "Savings Account":  {"rate": 4.0, "color":"#1f2937", "icon":"💰"},
}

# ── PAGE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="mkt-header">📊 SIP Simulator</div>', unsafe_allow_html=True)
st.markdown('<div class="mkt-sub">Compare what ₹X/month becomes across different asset classes over time</div>',
            unsafe_allow_html=True)

# ── INPUTS ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Configure your SIP</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    monthly = st.number_input("Monthly SIP Amount (₹)", min_value=500,
                               max_value=1000000, value=5000, step=500)
with c2:
    years = st.slider("Investment Period", 1, 30, 10,
                       format="%d years")
with c3:
    selected = st.multiselect("Compare Assets",
                               list(ASSETS.keys()),
                               default=["Nifty 50 Index","Large Cap MF","Gold","Fixed Deposit"])

if not selected:
    st.warning("Please select at least one asset to compare.")
    st.stop()

invested = monthly * years * 12

# ── CALCULATE ─────────────────────────────────────────────────────────────────
results = {}
for name in selected:
    a = ASSETS[name]
    fv = sip_fv(monthly, a["rate"], years)
    results[name] = {"fv":fv, "gain":fv-invested, "rate":a["rate"],
                     "color":a["color"], "icon":a["icon"]}

sorted_results = sorted(results.items(), key=lambda x: -x[1]["fv"])
winner_name, winner_data = sorted_results[0]

# ── SUMMARY KPI ROW ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)
kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.markdown(f"""<div class="result-card">
        <div class="result-label">Total Invested</div>
        <div class="result-value">₹{invested:,.0f}</div>
        <div class="result-gain">{years} yrs × ₹{monthly:,}/mo</div>
    </div>""", unsafe_allow_html=True)
with kpi_cols[1]:
    st.markdown(f"""<div class="result-card">
        <div class="result-label">Best Return ({winner_name})</div>
        <div class="result-value">₹{winner_data['fv']:,.0f}</div>
        <div class="result-gain">+₹{winner_data['gain']:,.0f} gain</div>
    </div>""", unsafe_allow_html=True)
with kpi_cols[2]:
    abs_ret = (winner_data['gain']/invested)*100
    st.markdown(f"""<div class="result-card">
        <div class="result-label">Absolute Return</div>
        <div class="result-value">{abs_ret:.1f}%</div>
        <div class="result-gain">on ₹{invested:,.0f} invested</div>
    </div>""", unsafe_allow_html=True)
with kpi_cols[3]:
    st.markdown(f"""<div class="result-card">
        <div class="result-label">Wealth Multiplier</div>
        <div class="result-value">{winner_data['fv']/invested:.2f}x</div>
        <div class="result-gain">your money grew</div>
    </div>""", unsafe_allow_html=True)

# ── BAR CHART ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Asset Comparison Chart</div>', unsafe_allow_html=True)

names  = [n for n,_ in sorted_results]
values = [d["fv"] for _,d in sorted_results]
colors = [ASSETS[n]["color"] for n in names]
labels = [f"₹{v/1e5:.2f}L" if v<1e7 else f"₹{v/1e7:.2f}Cr" for v in values]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=names, y=values,
    marker_color=colors,
    text=labels, textposition="outside",
    textfont=dict(color="#f0f0ff", size=11),
    hovertemplate="%{x}<br>₹%{y:,.0f}<extra></extra>",
))
# Invested line
fig.add_hline(y=invested, line_dash="dot", line_color="#6b7280",
               annotation_text=f"Invested: ₹{invested:,.0f}",
               annotation_font_color="#6b7280")
fig.update_layout(
    height=340, paper_bgcolor="#111130", plot_bgcolor="#0d0d24",
    margin=dict(l=8,r=8,t=40,b=8), showlegend=False,
    font=dict(color="#6b7280", size=11),
    xaxis=dict(gridcolor="rgba(139,92,246,0.1)", tickfont=dict(color="#9ca3af")),
    yaxis=dict(gridcolor="rgba(139,92,246,0.1)", showgrid=True,
               tickformat=",.0f", tickprefix="₹"),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ── DETAILED TABLE ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Detailed Breakdown</div>', unsafe_allow_html=True)
rows = []
for name, d in sorted_results:
    rows.append({
        "Asset":           f"{ASSETS[name]['icon']} {name}",
        "Annual Return":   f"{d['rate']}%",
        "Final Value":     f"₹{d['fv']:,.0f}",
        "Total Gain":      f"₹{d['gain']:,.0f}",
        "Absolute Return": f"{(d['gain']/invested)*100:.1f}%",
        "Multiplier":      f"{d['fv']/invested:.2f}x",
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── YEAR BY YEAR GROWTH ───────────────────────────────────────────────────────
st.markdown('<div class="section-title">Year-by-Year Growth</div>', unsafe_allow_html=True)
fig2 = go.Figure()
for name, d in sorted_results:
    yearly = [sip_fv(monthly, d["rate"], y) for y in range(1, years+1)]
    fig2.add_trace(go.Scatter(
        x=list(range(1, years+1)), y=yearly,
        mode="lines+markers", name=name,
        line=dict(color=ASSETS[name]["color"], width=2),
        marker=dict(size=4),
        hovertemplate=f"{name}<br>Year %{{x}}: ₹%{{y:,.0f}}<extra></extra>",
    ))
fig2.add_hline(y=invested, line_dash="dot", line_color="#6b7280",
                annotation_text="Total Invested", annotation_font_color="#6b7280")
fig2.update_layout(
    height=300, paper_bgcolor="#111130", plot_bgcolor="#0d0d24",
    margin=dict(l=8,r=8,t=10,b=8),
    font=dict(color="#6b7280", size=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#9ca3af")),
    xaxis=dict(gridcolor="rgba(139,92,246,0.1)", title="Year", tickfont=dict(color="#9ca3af")),
    yaxis=dict(gridcolor="rgba(139,92,246,0.1)", showgrid=True,
               tickformat=",.0f", tickprefix="₹"),
)
st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;color:#374151;font-size:0.72rem;">
    Returns based on historical averages · Past performance does not guarantee future results · Not financial advice
</div>""", unsafe_allow_html=True)