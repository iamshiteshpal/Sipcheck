import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import math

st.set_page_config(page_title="Goals — CAS 360", page_icon="🎯", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

#MainMenu {visibility:hidden;} footer {visibility:hidden;}

.stApp { background: #0B0914; color: #E2E8F0; font-family: 'Inter', sans-serif !important; }
section[data-testid="stSidebar"] { background: #0B0914; border-right: 1px solid rgba(168, 85, 247, 0.2); }
.block-container { padding: 0rem 2rem 2rem 2rem; max-width: 100%; }

.kpi-card-custom {
    background: rgba(30, 25, 45, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(168, 85, 247, 0.2);
    border-radius: 12px;
    padding: 18px 20px;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    min-height: 110px;
    position: relative;
    overflow: hidden;
}
.kpi-card-custom::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--card-accent, #A855F7);
    border-radius: 12px 12px 0 0;
}
.kpi-card-custom:hover {
    border-color: #A855F7;
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.4);
    transform: translateY(-2px);
}
.kpi-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;}
.kpi-lbl { font-size: 0.8rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;}
.kpi-val { font-size: 1.6rem; font-weight: 700; color: #F8FAFC; margin-bottom: 4px; font-family: 'Inter', sans-serif;}

.badge-up { background: rgba(32, 201, 151, 0.15); color: #20C997; border: 1px solid rgba(32, 201, 151, 0.3); padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block;}
.badge-down { background: rgba(255, 77, 77, 0.15); color: #FF4D4D; border: 1px solid rgba(255, 77, 77, 0.3); padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block;}
.badge-neutral { background: rgba(168, 85, 247, 0.15); color: #D8B4FE; border: 1px solid rgba(168, 85, 247, 0.3); padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block;}

.section-accent {
    font-size: 0.75rem;
    font-weight: 600;
    color: #94A3B8;
    margin: 1.5rem 0 0.75rem 0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-accent::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(168,85,247,0.15);
}

.stButton>button { border: 1px solid rgba(168, 85, 247, 0.5) !important; background: rgba(30, 25, 45, 0.8) !important; color: #D8B4FE !important; font-weight: 500 !important; border-radius: 8px !important; transition: all 0.3s; box-shadow: 0 0 10px rgba(168, 85, 247, 0.1); }
.stButton>button:hover { border-color: #A855F7 !important; color: #FFF !important; box-shadow: 0 0 15px rgba(168, 85, 247, 0.6); }

.tech-panel { background: rgba(30, 25, 45, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 12px; padding: 20px; height: 100%; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);}
.tech-row { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(168, 85, 247, 0.15); padding: 12px 0; }
.tech-row:last-child { border-bottom: none; }
.tech-label { color: #94A3B8; font-size: 0.85rem; font-weight: 500; }
.tech-val { color: #F8FAFC; font-weight: 600; font-size: 0.95rem;}

.stTabs [data-baseweb="tab-list"] { background-color: rgba(30, 25, 45, 0.4); border-radius: 8px; padding: 5px; gap: 10px; }
.stTabs [data-baseweb="tab"] { color: #94A3B8; font-weight: 600; border-radius: 6px; padding: 8px 16px; }
.stTabs [aria-selected="true"] { background-color: rgba(168, 85, 247, 0.2) !important; color: #D8B4FE !important; border-bottom: 2px solid #A855F7 !important;}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.85); }
}
.pulse-dot { animation: pulse-dot 2s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)

# ─── GOAL TEMPLATES ───────────────────────────────────────────────────────────
GOAL_TEMPLATES = {
    "🏠 Buy a Home": {"target": 5000000, "years": 10, "icon": "🏠"},
    "🎓 Child Education": {"target": 2000000, "years": 8, "icon": "🎓"},
    "✈️ Dream Vacation": {"target": 500000, "years": 3, "icon": "✈️"},
    "🏎️ Buy a Car": {"target": 1500000, "years": 5, "icon": "🏎️"},
    "💼 Emergency Fund": {"target": 600000, "years": 2, "icon": "💼"},
    "🌴 Early Retirement": {"target": 20000000, "years": 20, "icon": "🌴"},
    "💍 Wedding": {"target": 1000000, "years": 3, "icon": "💍"},
    "🏗️ Custom Goal": {"target": 1000000, "years": 5, "icon": "🎯"},
}

# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.5rem;">
<div style="font-size:1.8rem;font-weight:800;color:#F8FAFC;">
Goal Planner <span style="color:#A855F7;">🎯</span></div>
<div style="font-size:0.8rem;color:#6B7280;margin-top:2px;">
Calculate exactly how much to invest to reach your financial goals
</div>
</div>
""", unsafe_allow_html=True)

# ─── SECTION 1: GOAL SELECTOR ─────────────────────────────────────────────────
st.markdown('<div class="section-accent">Choose Your Goal</div>', unsafe_allow_html=True)

if "selected_goal" not in st.session_state:
    st.session_state["selected_goal"] = "🏠 Buy a Home"

cols = st.columns(4)
for i, (gname, gdata) in enumerate(GOAL_TEMPLATES.items()):
    with cols[i % 4]:
        is_selected = st.session_state.get("selected_goal") == gname
        border = "#A855F7" if is_selected else "rgba(168,85,247,0.2)"
        bg = "rgba(168,85,247,0.15)" if is_selected else "rgba(30,25,45,0.6)"
        if st.button(f"{gdata['icon']} {gname.split(' ', 1)[1]}", key=f"goal_{i}", use_container_width=True):
            st.session_state["selected_goal"] = gname
            st.rerun()

# ─── SECTION 2: INPUT PANEL + RESULTS ────────────────────────────────────────
selected = st.session_state.get("selected_goal", "🏠 Buy a Home")
template = GOAL_TEMPLATES[selected]

st.markdown('<div class="section-accent">Plan Your Investment</div>', unsafe_allow_html=True)

left_col, right_col = st.columns([0.4, 0.6])

with left_col:
    st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.25);border-top:2px solid #A855F7;border-radius:12px;padding:20px 22px;margin-bottom:12px;">
<div style="font-size:1rem;font-weight:700;color:#D8B4FE;margin-bottom:4px;">{selected} Details</div>
</div>""", unsafe_allow_html=True)

    goal_amount = st.number_input(
        "Target Amount (₹)",
        min_value=10000,
        max_value=100000000,
        value=template["target"],
        step=10000,
        key="goal_amount"
    )

    years = st.slider(
        "Time Horizon (years)",
        min_value=1, max_value=30,
        value=template["years"],
        key="goal_years"
    )

    current_savings = st.number_input(
        "Already Saved (₹)",
        min_value=0,
        max_value=100000000,
        value=0,
        step=1000,
        key="current_savings"
    )

    expected_return = st.slider(
        "Expected Annual Return (%)",
        min_value=4.0, max_value=25.0,
        value=12.0, step=0.5,
        key="exp_return"
    )

    inflation_rate = st.slider(
        "Inflation Rate (%)",
        min_value=0.0, max_value=10.0,
        value=6.0, step=0.5,
        key="inflation"
    )

    # ── CALCULATIONS ──────────────────────────────────────────────────────────
    r_monthly = expected_return / 100 / 12
    months = years * 12

    inflation_adj_target = goal_amount * ((1 + inflation_rate / 100) ** years)
    fv_current = current_savings * ((1 + r_monthly) ** months)
    remaining = max(0, inflation_adj_target - fv_current)

    if r_monthly > 0 and remaining > 0:
        sip_needed = remaining * r_monthly / (((1 + r_monthly) ** months) - 1)
    else:
        sip_needed = remaining / months if months > 0 else 0

    if r_monthly > 0:
        lumpsum_needed = remaining / ((1 + r_monthly) ** months)
    else:
        lumpsum_needed = remaining

    total_invested_sip = sip_needed * months
    total_returns = remaining - total_invested_sip

with right_col:
    # ── RESULT CARDS ──────────────────────────────────────────────────────────
    r1, r2 = st.columns(2)
    r3, r4 = st.columns(2)

    with r1:
        st.markdown(f"""
<div style="background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.3);border-top:2px solid #A855F7;border-radius:12px;padding:16px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;letter-spacing:0.08em;margin-bottom:6px;">MONTHLY SIP NEEDED</div>
<div style="font-size:1.6rem;font-weight:800;color:#A855F7;">₹{sip_needed:,.0f}</div>
<div style="font-size:10px;color:#6B7280;margin-top:4px;">per month for {years} years</div>
</div>""", unsafe_allow_html=True)

    with r2:
        st.markdown(f"""
<div style="background:rgba(32,201,151,0.08);border:1px solid rgba(32,201,151,0.25);border-top:2px solid #20C997;border-radius:12px;padding:16px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;letter-spacing:0.08em;margin-bottom:6px;">OR LUMPSUM TODAY</div>
<div style="font-size:1.6rem;font-weight:800;color:#20C997;">₹{lumpsum_needed:,.0f}</div>
<div style="font-size:10px;color:#6B7280;margin-top:4px;">one-time investment</div>
</div>""", unsafe_allow_html=True)

    with r3:
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);border-radius:12px;padding:16px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;letter-spacing:0.08em;margin-bottom:6px;">INFLATION ADJ. TARGET</div>
<div style="font-size:1.4rem;font-weight:700;color:#F8FAFC;">₹{inflation_adj_target:,.0f}</div>
<div style="font-size:10px;color:#6B7280;margin-top:4px;">in {years} years at {inflation_rate}% inflation</div>
</div>""", unsafe_allow_html=True)

    with r4:
        gain_color = "#20C997" if total_returns > 0 else "#FF4D4D"
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);border-radius:12px;padding:16px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;letter-spacing:0.08em;margin-bottom:6px;">WEALTH GAIN</div>
<div style="font-size:1.4rem;font-weight:700;color:{gain_color};">₹{abs(total_returns):,.0f}</div>
<div style="font-size:10px;color:#6B7280;margin-top:4px;">returns on your SIP investment</div>
</div>""", unsafe_allow_html=True)

    # ── GROWTH CHART ──────────────────────────────────────────────────────────
    st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)

    years_list = list(range(0, years + 1))
    corpus_values = []
    invested_values = []
    target_line = []

    for y in years_list:
        m = y * 12
        fv_sip = sip_needed * (((1 + r_monthly) ** m - 1) / r_monthly) if r_monthly > 0 and m > 0 else sip_needed * m
        fv_savings = current_savings * ((1 + r_monthly) ** m)
        corpus_values.append(fv_sip + fv_savings)
        invested_values.append(sip_needed * m + current_savings)
        target_line.append(inflation_adj_target)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=years_list, y=invested_values,
        name='Total Invested',
        fill='tozeroy',
        fillcolor='rgba(168,85,247,0.1)',
        line=dict(color='#A855F7', width=2),
        hovertemplate='Year %{x}: ₹%{y:,.0f}<extra>Invested</extra>'
    ))

    fig.add_trace(go.Scatter(
        x=years_list, y=corpus_values,
        name='Portfolio Value',
        fill='tonexty',
        fillcolor='rgba(32,201,151,0.15)',
        line=dict(color='#20C997', width=2.5),
        hovertemplate='Year %{x}: ₹%{y:,.0f}<extra>Portfolio</extra>'
    ))

    fig.add_trace(go.Scatter(
        x=years_list, y=target_line,
        name='Inflation Adj. Target',
        line=dict(color='#FF4D4D', width=1.5, dash='dash'),
        hovertemplate='Target: ₹%{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94A3B8', family='Inter'),
        xaxis=dict(showgrid=False, zeroline=False, title='Years', color='#4B5563'),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(168,85,247,0.08)',
            side='right', zeroline=False,
            tickformat='₹,.0f', color='#4B5563'
        ),
        legend=dict(
            bgcolor='rgba(30,25,45,0.8)',
            bordercolor='rgba(168,85,247,0.2)',
            borderwidth=1, font=dict(size=10),
            orientation='h', yanchor='bottom',
            y=1.02, xanchor='right', x=1
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(30,25,45,0.95)',
            bordercolor='rgba(168,85,247,0.3)',
            font=dict(color='#F8FAFC', size=11)
        )
    )

    st.plotly_chart(fig, use_container_width=True)

# ─── SECTION 3: RETURN SCENARIOS ──────────────────────────────────────────────
st.markdown('<div class="section-accent">Return Scenarios</div>', unsafe_allow_html=True)

scenarios = [
    ("Conservative", 8.0, "#94A3B8"),
    ("Moderate", 12.0, "#A855F7"),
    ("Aggressive", 16.0, "#20C997"),
    ("Very Aggressive", 20.0, "#F59E0B"),
]

sc_cols = st.columns(4)
for i, (sname, sret, scol) in enumerate(scenarios):
    sr_m = sret / 100 / 12
    if sr_m > 0 and months > 0:
        s_sip = remaining * sr_m / (((1 + sr_m) ** months) - 1)
    else:
        s_sip = remaining / months if months > 0 else 0
    s_total = s_sip * months
    s_gain = remaining - s_total

    with sc_cols[i]:
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);border-top:2px solid {scol};border-radius:12px;padding:14px 16px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;margin-bottom:8px;">{sname.upper()}</div>
<div style="font-size:11px;color:{scol};font-weight:600;margin-bottom:4px;">{sret}% p.a.</div>
<div style="font-size:1.2rem;font-weight:700;color:#F8FAFC;">₹{s_sip:,.0f}</div>
<div style="font-size:10px;color:#6B7280;margin-top:4px;">/month</div>
<div style="font-size:10px;color:#20C997;margin-top:6px;">Gain: ₹{max(0, s_gain):,.0f}</div>
</div>""", unsafe_allow_html=True)
