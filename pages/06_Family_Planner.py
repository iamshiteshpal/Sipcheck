import streamlit as st

st.set_page_config(page_title="Family Planner — CAS 360", page_icon="👨‍👩‍👧‍👦", layout="wide")

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

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
ROLE_AVATARS = {
    "Father": "👨",
    "Mother": "👩",
    "Son": "👦",
    "Daughter": "👧",
    "Grandfather": "👴",
    "Grandmother": "👵",
    "Self": "🧑",
    "Spouse": "💑",
}

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "family_members" not in st.session_state:
    st.session_state["family_members"] = []

# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.5rem;">
<div style="font-size:1.8rem;font-weight:800;color:#F8FAFC;">Family Wealth Planner
<span style="color:#A855F7;">👨‍👩‍👧‍👦</span></div>
<div style="font-size:0.8rem;color:#6B7280;margin-top:2px;">
Build a complete financial plan for your entire family
</div>
</div>
""", unsafe_allow_html=True)

# ─── PROGRESS STEPS BAR ───────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;gap:0;margin-bottom:2rem;">
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;
        margin:0 auto 6px;display:flex;align-items:center;
        justify-content:center;font-size:12px;font-weight:600;
        background:#A855F7;color:#fff;
        border:2px solid #A855F7;">1</div>
        <div style="font-size:10px;font-weight:500;
        color:#D8B4FE;">Family Setup</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;
        margin:0 auto 6px;display:flex;align-items:center;
        justify-content:center;font-size:12px;font-weight:600;
        background:rgba(30,25,45,0.8);color:#6B7280;
        border:2px solid #2D2D2D;">2</div>
        <div style="font-size:10px;font-weight:500;
        color:#6B7280;">Finances</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;
        margin:0 auto 6px;display:flex;align-items:center;
        justify-content:center;font-size:12px;font-weight:600;
        background:rgba(30,25,45,0.8);color:#6B7280;
        border:2px solid #2D2D2D;">3</div>
        <div style="font-size:10px;font-weight:500;
        color:#6B7280;">Goals</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;
        margin:0 auto 6px;display:flex;align-items:center;
        justify-content:center;font-size:12px;font-weight:600;
        background:rgba(30,25,45,0.8);color:#6B7280;
        border:2px solid #2D2D2D;">4</div>
        <div style="font-size:10px;font-weight:500;
        color:#6B7280;">Your Plan</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── ADD MEMBER FORM ──────────────────────────────────────────────────────────
st.markdown('<div class="section-accent">Add Family Members</div>', unsafe_allow_html=True)

with st.expander("➕ Add a family member", expanded=len(st.session_state["family_members"]) == 0):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        m_name = st.text_input("Name", key="m_name", placeholder="e.g. Rajesh")
    with col2:
        m_role = st.selectbox("Role", list(ROLE_AVATARS.keys()), key="m_role")
    with col3:
        m_age = st.number_input("Age", min_value=1, max_value=90, value=35, key="m_age")
    with col4:
        m_income = st.number_input("Monthly Income (₹)", min_value=0, max_value=10000000,
                                   value=50000, step=1000, key="m_income")

    if st.button("Add Member ➕", use_container_width=True, key="add_member_btn"):
        if m_name.strip():
            st.session_state["family_members"].append({
                "name": m_name.strip(),
                "role": m_role,
                "avatar": ROLE_AVATARS[m_role],
                "age": m_age,
                "income": m_income,
            })
            st.rerun()

# ─── DISPLAY ADDED MEMBERS ────────────────────────────────────────────────────
if st.session_state["family_members"]:
    st.markdown('<div class="section-accent">Your Family</div>', unsafe_allow_html=True)

    total_income = sum(m["income"] for m in st.session_state["family_members"])

    cols = st.columns(min(len(st.session_state["family_members"]), 5))
    for i, member in enumerate(st.session_state["family_members"]):
        with cols[i % 5]:
            st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);border-top:2px solid #A855F7;border-radius:12px;padding:16px;text-align:center;position:relative;">
<div style="font-size:2rem;margin-bottom:6px;">{member['avatar']}</div>
<div style="font-size:13px;font-weight:600;color:#F8FAFC;">{member['name']}</div>
<div style="font-size:11px;color:#94A3B8;margin:2px 0;">{member['role']} · Age {member['age']}</div>
<div style="font-size:12px;font-weight:600;color:#20C997;margin-top:6px;">₹{member['income']:,}/mo</div>
</div>""", unsafe_allow_html=True)

            if st.button("Remove", key=f"rem_{i}", use_container_width=True):
                st.session_state["family_members"].pop(i)
                st.rerun()

    st.markdown(f"""
<div style="background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.2);border-radius:10px;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;margin-top:12px;">
    <div>
        <div style="font-size:11px;color:#94A3B8;">Total family members</div>
        <div style="font-size:1.4rem;font-weight:700;color:#F8FAFC;">{len(st.session_state['family_members'])} members</div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:11px;color:#94A3B8;">Combined monthly income</div>
        <div style="font-size:1.4rem;font-weight:700;color:#20C997;">₹{total_income:,}/mo</div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:11px;color:#94A3B8;">Annual family income</div>
        <div style="font-size:1.4rem;font-weight:700;color:#A855F7;">₹{total_income * 12:,}/yr</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([0.2, 0.8])
    with col_btn1:
        if st.button("Continue to Finances →", type="primary", key="to_finances"):
            st.session_state["fp_step"] = 2
            st.rerun()

else:
    st.markdown("""
<div style="text-align:center;padding:3rem;color:#6B7280;font-size:13px;">
    👆 Add your first family member above to get started
</div>
""", unsafe_allow_html=True)

if st.session_state.get("fp_step", 1) >= 2:

    st.markdown("""
<div style="display:flex;gap:0;margin-bottom:2rem;margin-top:2rem;">
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#10B981;color:#fff;border:2px solid #10B981;">✓</div>
        <div style="font-size:10px;font-weight:500;color:#10B981;">Family Setup</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#A855F7;color:#fff;border:2px solid #A855F7;">2</div>
        <div style="font-size:10px;font-weight:500;color:#D8B4FE;">Finances</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:rgba(30,25,45,0.8);color:#6B7280;border:2px solid #2D2D2D;">3</div>
        <div style="font-size:10px;font-weight:500;color:#6B7280;">Goals</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:rgba(30,25,45,0.8);color:#6B7280;border:2px solid #2D2D2D;">4</div>
        <div style="font-size:10px;font-weight:500;color:#6B7280;">Your Plan</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-accent">Family Finances</div>', unsafe_allow_html=True)

    fin_col1, fin_col2 = st.columns(2)

    with fin_col1:
        st.markdown("""
<div style="font-size:12px;font-weight:600;color:#D8B4FE;margin-bottom:12px;">Monthly Expenses</div>
""", unsafe_allow_html=True)

        exp_household = st.number_input(
            "Household expenses (rent, food, bills)",
            min_value=0, max_value=1000000, value=30000, step=1000, key="exp_household"
        )
        exp_education = st.number_input(
            "Children education fees",
            min_value=0, max_value=500000, value=10000, step=1000, key="exp_education"
        )
        exp_lifestyle = st.number_input(
            "Lifestyle (dining, entertainment, travel)",
            min_value=0, max_value=500000, value=10000, step=1000, key="exp_lifestyle"
        )
        exp_other = st.number_input(
            "Other expenses",
            min_value=0, max_value=500000, value=5000, step=1000, key="exp_other"
        )

    with fin_col2:
        st.markdown("""
<div style="font-size:12px;font-weight:600;color:#D8B4FE;margin-bottom:12px;">EMIs &amp; Obligations</div>
""", unsafe_allow_html=True)

        emi_home = st.number_input(
            "Home loan EMI", min_value=0, max_value=500000, value=0, step=1000, key="emi_home"
        )
        emi_car = st.number_input(
            "Car loan EMI", min_value=0, max_value=200000, value=0, step=1000, key="emi_car"
        )
        emi_personal = st.number_input(
            "Personal loan EMI", min_value=0, max_value=200000, value=0, step=1000, key="emi_personal"
        )
        insurance_premium = st.number_input(
            "Total insurance premiums/month", min_value=0, max_value=100000, value=5000, step=500, key="insurance_premium"
        )
        existing_sip = st.number_input(
            "Existing SIP/investments/month", min_value=0, max_value=500000, value=0, step=1000, key="existing_sip"
        )

    # ── CALCULATIONS ──────────────────────────────────────────────────────────
    total_income = sum(m["income"] for m in st.session_state.get("family_members", []))
    total_expenses = exp_household + exp_education + exp_lifestyle + exp_other
    total_emis = emi_home + emi_car + emi_personal + insurance_premium
    total_obligations = total_emis + existing_sip
    monthly_surplus = total_income - total_expenses - total_obligations
    savings_rate = (monthly_surplus / total_income * 100) if total_income > 0 else 0

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);border-top:2px solid #A855F7;border-radius:12px;padding:14px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;margin-bottom:6px;">TOTAL INCOME</div>
<div style="font-size:1.3rem;font-weight:700;color:#F8FAFC;">₹{total_income:,}</div>
<div style="font-size:10px;color:#6B7280;">per month</div>
</div>""", unsafe_allow_html=True)

    with s2:
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(255,77,77,0.2);border-top:2px solid #FF4D4D;border-radius:12px;padding:14px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;margin-bottom:6px;">TOTAL OUTFLOW</div>
<div style="font-size:1.3rem;font-weight:700;color:#FF4D4D;">₹{total_expenses + total_obligations:,}</div>
<div style="font-size:10px;color:#6B7280;">expenses + EMIs</div>
</div>""", unsafe_allow_html=True)

    with s3:
        surplus_color = "#20C997" if monthly_surplus > 0 else "#FF4D4D"
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(32,201,151,0.2);border-top:2px solid {surplus_color};border-radius:12px;padding:14px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;margin-bottom:6px;">INVESTABLE SURPLUS</div>
<div style="font-size:1.3rem;font-weight:700;color:{surplus_color};">₹{monthly_surplus:,}</div>
<div style="font-size:10px;color:#6B7280;">available to invest</div>
</div>""", unsafe_allow_html=True)

    with s4:
        rate_color = "#20C997" if savings_rate >= 20 else "#F59E0B" if savings_rate >= 10 else "#FF4D4D"
        rate_label = "Excellent!" if savings_rate >= 20 else "Good" if savings_rate >= 10 else "Needs work"
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);border-top:2px solid {rate_color};border-radius:12px;padding:14px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;margin-bottom:6px;">SAVINGS RATE</div>
<div style="font-size:1.3rem;font-weight:700;color:{rate_color};">{savings_rate:.1f}%</div>
<div style="font-size:10px;color:#6B7280;">{rate_label}</div>
</div>""", unsafe_allow_html=True)

    # ── CASH FLOW BREAKDOWN ───────────────────────────────────────────────────
    import plotly.graph_objects as go

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    cf_col1, cf_col2 = st.columns([0.4, 0.6])

    labels = ['Household', 'Education', 'Lifestyle', 'Other',
              'EMIs', 'Insurance', 'Existing SIP', 'Surplus']
    values = [exp_household, exp_education, exp_lifestyle, exp_other,
              emi_home + emi_car + emi_personal, insurance_premium,
              existing_sip, max(0, monthly_surplus)]
    colors = ['#EF4444', '#F97316', '#F59E0B', '#94A3B8',
              '#3B82F6', '#8B5CF6', '#06B6D4', '#20C997']

    with cf_col1:
        fig_cf = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker=dict(colors=colors, line=dict(color='#0B0914', width=2)),
            textinfo='percent',
            textfont=dict(size=10, color='white'),
        ))
        fig_cf.update_layout(
            height=250,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            annotations=[dict(
                text=f"₹{total_income:,}<br>income",
                x=0.5, y=0.5,
                font=dict(size=11, color='#F8FAFC'),
                showarrow=False
            )]
        )
        st.plotly_chart(fig_cf, use_container_width=True)

    with cf_col2:
        row_labels = ['Household expenses', 'Education', 'Lifestyle', 'Other expenses',
                      'All EMIs', 'Insurance', 'Existing investments', 'Available surplus']
        row_values = [exp_household, exp_education, exp_lifestyle, exp_other,
                      emi_home + emi_car + emi_personal, insurance_premium,
                      existing_sip, max(0, monthly_surplus)]
        for lbl, val, col in zip(row_labels, row_values, colors):
            pct = (val / total_income * 100) if total_income > 0 else 0
            st.markdown(f"""
<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
<div style="width:10px;height:10px;border-radius:50%;background:{col};flex-shrink:0;"></div>
<div style="flex:1;font-size:11px;color:#94A3B8;">{lbl}</div>
<div style="font-size:11px;font-weight:600;color:#F8FAFC;">₹{val:,}</div>
<div style="font-size:10px;color:#6B7280;width:35px;text-align:right;">{pct:.0f}%</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    if monthly_surplus > 0:
        if st.button("Continue to Goals →", type="primary", key="to_goals"):
            st.session_state["fp_step"] = 3
            st.session_state["monthly_surplus"] = monthly_surplus
            st.rerun()
    else:
        st.markdown("""
<div style="background:rgba(255,77,77,0.08);border:1px solid rgba(255,77,77,0.2);border-radius:10px;padding:12px 16px;font-size:12px;color:#FF4D4D;">
⚠️ Your expenses exceed income. Reduce expenses or increase income before planning investments.
</div>""", unsafe_allow_html=True)
