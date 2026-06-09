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

if st.session_state.get("fp_step", 1) >= 3:

    st.markdown("""
<div style="display:flex;gap:0;margin-bottom:2rem;margin-top:2rem;">
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#10B981;color:#fff;border:2px solid #10B981;">✓</div>
        <div style="font-size:10px;font-weight:500;color:#10B981;">Family Setup</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#10B981;color:#fff;border:2px solid #10B981;">✓</div>
        <div style="font-size:10px;font-weight:500;color:#10B981;">Finances</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#A855F7;color:#fff;border:2px solid #A855F7;">3</div>
        <div style="font-size:10px;font-weight:500;color:#D8B4FE;">Goals</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:rgba(30,25,45,0.8);color:#6B7280;border:2px solid #2D2D2D;">4</div>
        <div style="font-size:10px;font-weight:500;color:#6B7280;">Your Plan</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-accent">Family Goals</div>', unsafe_allow_html=True)

    st.markdown("""
<div style="font-size:12px;color:#94A3B8;margin-bottom:16px;">
Add financial goals for your family. Each goal will be funded from your monthly surplus of """ +
f"<strong style='color:#20C997;'>₹{st.session_state.get('monthly_surplus', 0):,}</strong>" +
"""</div>
""", unsafe_allow_html=True)

    if "family_goals" not in st.session_state:
        st.session_state["family_goals"] = []

    GOAL_ICONS = {
        "Home Purchase": "🏠",
        "Child Education": "🎓",
        "Retirement": "🌴",
        "Emergency Fund": "🛡️",
        "Car Purchase": "🚗",
        "Wedding": "💍",
        "Business": "💼",
        "Vacation": "✈️",
        "Medical Fund": "🏥",
        "Custom": "🎯",
    }

    with st.expander("➕ Add a goal", expanded=len(st.session_state["family_goals"]) == 0):
        gc1, gc2 = st.columns(2)
        with gc1:
            g_type = st.selectbox("Goal type", list(GOAL_ICONS.keys()), key="g_type")
            g_member = st.selectbox(
                "For which member?",
                ["Entire Family"] + [m["name"] for m in st.session_state.get("family_members", [])],
                key="g_member"
            )
            g_amount = st.number_input(
                "Target amount (₹)", min_value=10000, max_value=100000000,
                value=1000000, step=10000, key="g_amount"
            )

        with gc2:
            g_years = st.slider("Years to achieve", min_value=1, max_value=30, value=5, key="g_years")
            g_priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="g_priority")
            g_notes = st.text_input("Notes (optional)", placeholder="e.g. IIT fees for son", key="g_notes")

        if st.button("Add Goal ➕", use_container_width=True, key="add_goal_btn"):
            r = 12.0 / 100 / 12
            m = g_years * 12
            sip = (g_amount * r / ((1 + r) ** m - 1)) if r > 0 else (g_amount / m)
            st.session_state["family_goals"].append({
                "type": g_type,
                "icon": GOAL_ICONS[g_type],
                "member": g_member,
                "amount": g_amount,
                "years": g_years,
                "priority": g_priority,
                "notes": g_notes,
                "sip_needed": sip,
            })
            st.rerun()

    if st.session_state["family_goals"]:

        total_sip_needed = sum(g["sip_needed"] for g in st.session_state["family_goals"])
        surplus = st.session_state.get("monthly_surplus", 0)
        sip_feasible = total_sip_needed <= surplus

        for i, goal in enumerate(st.session_state["family_goals"]):
            p_color = "#FF4D4D" if goal["priority"] == "High" else "#F59E0B" if goal["priority"] == "Medium" else "#20C997"
            feasible = goal["sip_needed"] <= (surplus / len(st.session_state["family_goals"]))
            notes_part = f" · {goal['notes']}" if goal["notes"] else ""

            st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);border-left:3px solid {p_color};border-radius:12px;padding:14px 16px;margin-bottom:8px;display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
<div style="font-size:1.5rem;">{goal['icon']}</div>
<div style="flex:1;min-width:150px;">
<div style="font-size:13px;font-weight:600;color:#F8FAFC;">{goal['type']}</div>
<div style="font-size:11px;color:#94A3B8;">For: {goal['member']} · {goal['years']} years{notes_part}</div>
</div>
<div style="text-align:center;min-width:100px;">
<div style="font-size:10px;color:#94A3B8;">TARGET</div>
<div style="font-size:14px;font-weight:700;color:#F8FAFC;">₹{goal['amount']:,}</div>
</div>
<div style="text-align:center;min-width:120px;">
<div style="font-size:10px;color:#94A3B8;">MONTHLY SIP</div>
<div style="font-size:14px;font-weight:700;color:{'#20C997' if feasible else '#FF4D4D'};">₹{goal['sip_needed']:,.0f}</div>
</div>
<div style="text-align:center;">
<span style="font-size:10px;font-weight:600;padding:3px 8px;border-radius:4px;background:{'rgba(32,201,151,0.15)' if feasible else 'rgba(255,77,77,0.15)'};color:{'#20C997' if feasible else '#FF4D4D'};">
{'✓ Feasible' if feasible else '⚠ Stretch'}
</span>
</div>
</div>""", unsafe_allow_html=True)

            if st.button(f"Remove goal {i+1}", key=f"rem_goal_{i}"):
                st.session_state["family_goals"].pop(i)
                st.rerun()

        status_color = "#20C997" if sip_feasible else "#FF4D4D"
        status_text = "✓ All goals feasible!" if sip_feasible else "⚠ Exceeds surplus — reduce goals or increase income"
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.8);border:1px solid rgba(168,85,247,0.2);border-radius:12px;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-top:12px;">
<div>
<div style="font-size:11px;color:#94A3B8;margin-bottom:4px;">Total SIP needed for all goals</div>
<div style="font-size:1.4rem;font-weight:700;color:#F8FAFC;">₹{total_sip_needed:,.0f}/month</div>
</div>
<div style="text-align:center;">
<div style="font-size:11px;color:#94A3B8;margin-bottom:4px;">Available surplus</div>
<div style="font-size:1.4rem;font-weight:700;color:#20C997;">₹{surplus:,}/month</div>
</div>
<div style="text-align:center;">
<div style="font-size:11px;color:#94A3B8;margin-bottom:4px;">Status</div>
<div style="font-size:13px;font-weight:700;color:{status_color};">{status_text}</div>
</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

        if st.button("Generate My Family Plan →", type="primary", key="gen_plan"):
            st.session_state["fp_step"] = 4
            st.rerun()

if st.session_state.get("fp_step", 1) >= 4:

    st.markdown("""
<div style="display:flex;gap:0;margin-bottom:2rem;margin-top:2rem;">
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#10B981;color:#fff;">✓</div>
        <div style="font-size:10px;color:#10B981;">Family Setup</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#10B981;color:#fff;">✓</div>
        <div style="font-size:10px;color:#10B981;">Finances</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#10B981;color:#fff;">✓</div>
        <div style="font-size:10px;color:#10B981;">Goals</div>
    </div>
    <div style="flex:1;text-align:center;">
        <div style="width:32px;height:32px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;background:#A855F7;color:#fff;border:2px solid #A855F7;">4</div>
        <div style="font-size:10px;color:#D8B4FE;">Your Plan</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="text-align:center;padding:1rem 0 1.5rem;">
    <div style="font-size:1.6rem;font-weight:800;color:#F8FAFC;">Your Family Financial Plan</div>
    <div style="font-size:0.85rem;color:#6B7280;margin-top:4px;">Powered by AI · Based on your family data</div>
</div>
""", unsafe_allow_html=True)

    members = st.session_state.get("family_members", [])
    goals = st.session_state.get("family_goals", [])
    surplus = st.session_state.get("monthly_surplus", 0)
    total_income = sum(m["income"] for m in members)
    total_sip = sum(g["sip_needed"] for g in goals)
    savings_rate = (surplus / total_income * 100) if total_income > 0 else 0

    score = 0
    if savings_rate >= 30: score += 25
    elif savings_rate >= 20: score += 20
    elif savings_rate >= 10: score += 12
    else: score += 5
    if total_sip <= surplus: score += 25
    elif total_sip <= surplus * 1.2: score += 15
    else: score += 5
    score += 20
    score += 15
    if len(goals) >= 2: score += 15
    elif len(goals) >= 1: score += 10
    score = min(score, 100)

    score_color = "#20C997" if score >= 70 else "#F59E0B" if score >= 50 else "#FF4D4D"
    score_label = "Excellent" if score >= 70 else "Good" if score >= 50 else "Needs Work"
    ideal_cover = total_income * 12 * 15
    emergency_needed = (
        st.session_state.get("exp_household", 30000) +
        st.session_state.get("exp_education", 0) +
        st.session_state.get("exp_lifestyle", 10000)
    ) * 6

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.8);border:1px solid rgba(168,85,247,0.2);border-top:2px solid {score_color};border-radius:12px;padding:16px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;margin-bottom:6px;">FINANCIAL HEALTH SCORE
<span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:rgba(168,85,247,0.3);color:#A855F7;font-size:9px;font-weight:700;text-align:center;line-height:14px;margin-left:4px;cursor:help;" title="Score out of 100 based on your savings rate, goal feasibility and financial cushion. 70+ is Excellent.">i</span></div>
<div style="font-size:2.5rem;font-weight:800;color:{score_color};">{score}</div>
<div style="font-size:11px;color:{score_color};margin-top:2px;">{score_label}</div>
<div style="background:#1F2937;border-radius:4px;height:5px;margin-top:8px;">
<div style="width:{score}%;height:100%;border-radius:4px;background:{score_color};"></div>
</div>
</div>""", unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.8);border:1px solid rgba(32,201,151,0.2);border-top:2px solid #20C997;border-radius:12px;padding:16px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;margin-bottom:6px;">MONTHLY SURPLUS
<span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:rgba(32,201,151,0.2);color:#20C997;font-size:9px;font-weight:700;text-align:center;line-height:14px;margin-left:4px;cursor:help;" title="Your income minus all expenses, EMIs and insurance. This is the money left every month to invest towards your goals.">i</span></div>
<div style="font-size:1.6rem;font-weight:800;color:#20C997;">₹{surplus:,}</div>
<div style="font-size:11px;color:#6B7280;">available to invest</div>
<div style="font-size:11px;color:#20C997;margin-top:4px;">Savings rate: {savings_rate:.1f}%</div>
</div>""", unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.8);border:1px solid rgba(239,68,68,0.2);border-top:2px solid #FF4D4D;border-radius:12px;padding:16px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;margin-bottom:6px;">IDEAL LIFE COVER NEEDED
<span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:rgba(239,68,68,0.2);color:#FF4D4D;font-size:9px;font-weight:700;text-align:center;line-height:14px;margin-left:4px;cursor:help;" title="Ideal term insurance = 15 times your annual income. If anything happens to the earner, family can survive 15 years. Get a pure term plan - cheapest and best protection.">i</span></div>
<div style="font-size:1.6rem;font-weight:800;color:#FF4D4D;">₹{ideal_cover/100000:.0f}L</div>
<div style="font-size:11px;color:#6B7280;">= 15× annual income</div>
<div style="font-size:11px;color:#F59E0B;margin-top:4px;">Verify your current cover</div>
</div>""", unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.8);border:1px solid rgba(245,158,11,0.2);border-top:2px solid #F59E0B;border-radius:12px;padding:16px;text-align:center;">
<div style="font-size:10px;color:#94A3B8;font-weight:600;margin-bottom:6px;">EMERGENCY FUND NEEDED
<span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:rgba(245,158,11,0.2);color:#F59E0B;font-size:9px;font-weight:700;text-align:center;line-height:14px;margin-left:4px;cursor:help;" title="6 months of essential expenses kept in a liquid fund or savings account. Never invest this in equity. This protects your family during job loss or medical emergency.">i</span></div>
<div style="font-size:1.6rem;font-weight:800;color:#F59E0B;">₹{emergency_needed:,}</div>
<div style="font-size:11px;color:#6B7280;">6 months expenses</div>
<div style="font-size:11px;color:#F59E0B;margin-top:4px;">Build this first</div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-accent" style="margin-top:1.5rem;">Goal Roadmap</div>', unsafe_allow_html=True)

    priority_order = sorted(goals, key=lambda x: (0 if x["priority"] == "High" else 1 if x["priority"] == "Medium" else 2))
    remaining_surplus = surplus
    for rank, goal in enumerate(priority_order):
        feasible = goal["sip_needed"] <= remaining_surplus
        remaining_surplus -= goal["sip_needed"]
        p_color = "#FF4D4D" if goal["priority"] == "High" else "#F59E0B" if goal["priority"] == "Medium" else "#20C997"
        st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.15);border-left:3px solid {p_color};border-radius:10px;padding:12px 16px;margin-bottom:6px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
<div style="width:24px;height:24px;border-radius:50%;background:{p_color}20;border:1px solid {p_color};display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:{p_color};">#{rank+1}</div>
<div style="font-size:1.2rem;">{goal['icon']}</div>
<div style="flex:1;">
<div style="font-size:13px;font-weight:600;color:#F8FAFC;">{goal['type']}</div>
<div style="font-size:11px;color:#94A3B8;">{goal['member']} · {goal['years']} years · {goal['priority']} priority</div>
</div>
<div style="text-align:right;">
<div style="font-size:14px;font-weight:700;color:#F8FAFC;">₹{goal['amount']:,}</div>
<div style="font-size:11px;color:{'#20C997' if feasible else '#FF4D4D'};">SIP: ₹{goal['sip_needed']:,.0f}/mo</div>
</div>
<span style="font-size:10px;font-weight:600;padding:3px 10px;border-radius:4px;background:{'rgba(32,201,151,0.15)' if feasible else 'rgba(255,77,77,0.15)'};color:{'#20C997' if feasible else '#FF4D4D'};">
{'✓ Funded' if feasible else '⚠ Shortfall'}
</span>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-accent" style="margin-top:1.5rem;">Your Personalized Plan</div>', unsafe_allow_html=True)

    if st.button("Generate My Family Plan", type="primary", key="gen_ai_plan"):
        st.session_state["family_plan"] = "generated"

    if st.session_state.get("family_plan"):

        members = st.session_state.get("family_members", [])
        goals = st.session_state.get("family_goals", [])
        surplus = st.session_state.get("monthly_surplus", 0)
        total_income = sum(m["income"] for m in members)
        total_sip = sum(g["sip_needed"] for g in goals)
        savings_rate = (surplus / total_income * 100 if total_income > 0 else 0)
        ideal_cover = total_income * 12 * 15
        emergency_needed = (
            st.session_state.get("exp_household", 30000) +
            st.session_state.get("exp_education", 0) +
            st.session_state.get("exp_lifestyle", 10000)
        ) * 6

        primary = members[0] if members else {"name": "Your family", "role": ""}

        insights = []
        if savings_rate >= 30:
            insights.append(f"✅ Excellent savings rate of {savings_rate:.1f}% — you are in the top 10% of Indian families financially.")
        elif savings_rate >= 20:
            insights.append(f"✅ Good savings rate of {savings_rate:.1f}% — slightly above the recommended 20% minimum.")
        elif savings_rate >= 10:
            insights.append(f"⚠️ Your savings rate is {savings_rate:.1f}% — try to reach 20% by reducing lifestyle expenses.")
        else:
            insights.append(f"🔴 Your savings rate of {savings_rate:.1f}% is too low — focus on reducing expenses before investing.")

        if total_sip <= surplus * 0.7:
            insights.append(f"✅ Your goals need ₹{total_sip:,.0f}/month which is well within your ₹{surplus:,} surplus — you have room to add more goals.")
        elif total_sip <= surplus:
            insights.append(f"✅ Your goals need ₹{total_sip:,.0f}/month — just within your surplus. Stay consistent and avoid new EMIs.")
        else:
            insights.append(f"🔴 Your goals need ₹{total_sip:,.0f}/month but surplus is only ₹{surplus:,} — reduce goal amounts or extend timelines.")

        actions = []
        actions.append(f"Build emergency fund of ₹{emergency_needed:,} first — keep in liquid mutual fund or savings account")

        high_goals = [g for g in goals if g["priority"] == "High"]
        if high_goals:
            g = high_goals[0]
            actions.append(f"Start SIP of ₹{g['sip_needed']:,.0f}/month for {g['type']} — this is your highest priority goal")

        if len(goals) > 1:
            for g in goals[1:]:
                actions.append(f"Allocate ₹{g['sip_needed']:,.0f}/month for {g['type']} ({g['years']} year goal)")

        actions.append(f"Get term life insurance of ₹{ideal_cover/100000:.0f} Lakhs — costs only ₹{int(ideal_cover/100000*40):,}/year for a {primary.get('age', 35)} year old")

        leftover = surplus - total_sip
        if leftover > 5000:
            actions.append(f"Remaining ₹{leftover:,.0f} surplus — invest in Nifty 50 index fund for long-term wealth building")

        fund_recs = {
            "Home Purchase": "Large Cap + Debt funds (60:40) — stable growth with capital protection",
            "Child Education": "Mid Cap + Large Cap funds (50:50) — 8+ year horizon allows equity exposure",
            "Retirement": "Multi-cap + PPF + NPS (60:20:20) — diversified for very long term",
            "Emergency Fund": "Liquid mutual fund — never equity, instant access needed",
            "Car Purchase": "Debt fund + RD (50:50) — short term goal needs stable returns",
            "Wedding": "Debt fund + Gold ETF (60:40) — 3-5 year horizon",
            "Business": "Large Cap + Liquid fund (70:30) — preserve capital while growing",
            "Vacation": "Liquid fund or RD — short term, capital preservation",
            "Medical Fund": "Liquid fund — instant access needed",
            "Custom": "Large Cap index fund — reliable long-term compounder",
        }

        corpus_1yr = total_sip * 12 * 1.12

        insights_html = "".join([f'<div style="font-size:12px;color:#E2E8F0;margin-bottom:6px;line-height:1.6;">{i}</div>' for i in insights])
        actions_html = "".join([f'<div style="font-size:12px;color:#E2E8F0;margin-bottom:8px;display:flex;gap:8px;"><span style="color:#A855F7;font-weight:700;flex-shrink:0;">{i+1}.</span><span style="line-height:1.6;">{a}</span></div>' for i, a in enumerate(actions)])
        funds_html = "".join([f'<div style="font-size:12px;color:#E2E8F0;margin-bottom:6px;line-height:1.6;"><span style="color:#20C997;">{g["icon"]} {g["type"]}: </span>{fund_recs.get(g["type"], "Large Cap index fund — reliable compounder")}</div>' for g in goals])

        plan_html = f"""
<div style="background:rgba(168,85,247,0.06);border:1px solid rgba(168,85,247,0.25);border-left:3px solid #A855F7;border-radius:12px;padding:22px 24px;margin-top:12px;">
<div style="font-size:14px;font-weight:700;color:#D8B4FE;margin-bottom:16px;">📋 {primary['name'].split()[0]}'s Family Financial Plan</div>
<div style="font-size:13px;font-weight:600;color:#A855F7;margin-bottom:8px;letter-spacing:0.05em;">FINANCIAL HEALTH INSIGHTS</div>
{insights_html}
<div style="height:1px;background:rgba(168,85,247,0.15);margin:14px 0;"></div>
<div style="font-size:13px;font-weight:600;color:#A855F7;margin-bottom:8px;letter-spacing:0.05em;">YOUR ACTION PLAN — DO THESE NOW</div>
{actions_html}
<div style="height:1px;background:rgba(168,85,247,0.15);margin:14px 0;"></div>
<div style="font-size:13px;font-weight:600;color:#A855F7;margin-bottom:8px;letter-spacing:0.05em;">FUND RECOMMENDATIONS PER GOAL</div>
{funds_html}
<div style="height:1px;background:rgba(168,85,247,0.15);margin:14px 0;"></div>
<div style="font-size:13px;font-weight:600;color:#A855F7;margin-bottom:8px;letter-spacing:0.05em;">12-MONTH MILESTONE</div>
<div style="font-size:12px;color:#E2E8F0;line-height:1.6;">
If you follow this plan consistently for 12 months, your investment portfolio will grow to approximately <strong style="color:#20C997;">₹{corpus_1yr:,.0f}</strong>. Your emergency fund will be fully built. All your goals will be on track. Your family will be financially protected.
</div>
<div style="margin-top:14px;padding-top:12px;border-top:1px solid rgba(168,85,247,0.15);font-size:10px;color:#4B5563;">
⚠️ This plan is for educational purposes only. Consult a SEBI-registered financial advisor before investing.
</div>
</div>
"""
        import plotly.graph_objects as go

        st.markdown("<div style='margin-top:1.5rem;'></div>",
                    unsafe_allow_html=True)

        st.markdown(f"""
<div style="text-align:center;margin-bottom:1.5rem;">
<div style="font-size:1.4rem;font-weight:800;color:#F8FAFC;">
📋 {primary['name'].split()[0]}'s Family Financial Plan
</div>
<div style="font-size:11px;color:#6B7280;margin-top:4px;">
Personalized based on your actual numbers
</div>
</div>
""", unsafe_allow_html=True)

        ins_col, pie_col = st.columns([0.55, 0.45])

        with ins_col:
            st.markdown("""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);border-radius:12px;padding:18px 20px;height:100%;">
<div style="font-size:11px;font-weight:700;color:#A855F7;letter-spacing:0.1em;margin-bottom:14px;">FINANCIAL HEALTH INSIGHTS</div>
""" + "".join([f"""
<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;padding:10px;border-radius:8px;background:rgba(168,85,247,0.04);border:1px solid rgba(168,85,247,0.1);">
<span style="font-size:16px;flex-shrink:0;">{'✅' if '✅' in insight else '⚠️' if '⚠️' in insight else '🔴'}</span>
<span style="font-size:12px;color:#E2E8F0;line-height:1.6;">{insight.replace('✅ ','').replace('⚠️ ','').replace('🔴 ','')}</span>
</div>""" for insight in insights]) + """
</div>""", unsafe_allow_html=True)

        with pie_col:
            pie_labels = []
            pie_values = []
            pie_colors = []

            exp_total = (
                st.session_state.get("exp_household", 0) +
                st.session_state.get("exp_education", 0) +
                st.session_state.get("exp_lifestyle", 0) +
                st.session_state.get("exp_other", 0)
            )
            emi_total = (
                st.session_state.get("emi_home", 0) +
                st.session_state.get("emi_car", 0) +
                st.session_state.get("emi_personal", 0)
            )
            ins_total = st.session_state.get("insurance_premium", 0)

            if exp_total > 0:
                pie_labels.append("Expenses")
                pie_values.append(exp_total)
                pie_colors.append("#EF4444")
            if emi_total > 0:
                pie_labels.append("EMIs")
                pie_values.append(emi_total)
                pie_colors.append("#3B82F6")
            if ins_total > 0:
                pie_labels.append("Insurance")
                pie_values.append(ins_total)
                pie_colors.append("#8B5CF6")
            if total_sip > 0:
                pie_labels.append("Goal SIPs")
                pie_values.append(total_sip)
                pie_colors.append("#10B981")
            if leftover > 0:
                pie_labels.append("Free Surplus")
                pie_values.append(leftover)
                pie_colors.append("#20C997")

            fig_pie = go.Figure(go.Pie(
                labels=pie_labels,
                values=pie_values,
                hole=0.65,
                marker=dict(
                    colors=pie_colors,
                    line=dict(color='#0B0914', width=2)
                ),
                textinfo='percent',
                textfont=dict(size=11, color='white'),
                hovertemplate='%{label}<br>₹%{value:,}<br>%{percent}<extra></extra>'
            ))
            fig_pie.update_layout(
                height=240,
                margin=dict(l=0, r=0, t=20, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(
                    font=dict(size=10, color='#94A3B8'),
                    bgcolor='rgba(0,0,0,0)',
                    orientation='v',
                    x=1.0, y=0.5
                ),
                annotations=[dict(
                    text=f"₹{total_income:,}<br>income",
                    x=0.38, y=0.5,
                    font=dict(size=12, color='#F8FAFC'),
                    showarrow=False
                )]
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("<div style='margin-top:1rem;'></div>",
                    unsafe_allow_html=True)

        act_col, proj_col = st.columns([0.45, 0.55])

        with act_col:
            action_colors = [
                "#FF4D4D", "#F59E0B",
                "#20C997", "#3B82F6", "#A855F7"
            ]
            action_html = """
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);border-radius:12px;padding:18px 20px;">
<div style="font-size:11px;font-weight:700;color:#A855F7;letter-spacing:0.1em;margin-bottom:14px;">YOUR ACTION PLAN — DO THESE NOW</div>"""
            for i, action in enumerate(actions):
                color = action_colors[i % len(action_colors)]
                action_html += f"""
<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:10px;">
<div style="width:22px;height:22px;border-radius:50%;background:{color}20;border:1px solid {color};display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:{color};flex-shrink:0;">{i+1}</div>
<div style="font-size:11px;color:#E2E8F0;line-height:1.6;flex:1;">{action}</div>
</div>"""
            action_html += "</div>"
            st.markdown(action_html, unsafe_allow_html=True)

        with proj_col:
            months = list(range(1, 13))
            monthly_growth = []
            cumulative = 0
            for m in months:
                monthly_gain = total_sip * (1 + 0.01) ** m
                cumulative += monthly_gain
                monthly_growth.append(cumulative)

            fig_proj = go.Figure()

            fig_proj.add_trace(go.Bar(
                x=[f"M{m}" for m in months],
                y=monthly_growth,
                marker=dict(
                    color=monthly_growth,
                    colorscale=[
                        [0, "rgba(168,85,247,0.4)"],
                        [1, "rgba(32,201,151,0.9)"]
                    ],
                    line=dict(color='rgba(0,0,0,0)', width=0)
                ),
                hovertemplate='Month %{x}<br>Portfolio: ₹%{y:,.0f}<extra></extra>'
            ))

            fig_proj.add_trace(go.Scatter(
                x=[f"M{m}" for m in months],
                y=monthly_growth,
                mode='lines+markers',
                line=dict(color='#20C997', width=2),
                marker=dict(size=5, color='#20C997'),
                name='Growth trend',
                hoverinfo='skip'
            ))

            fig_proj.update_layout(
                title=dict(
                    text="12-Month Portfolio Projection",
                    font=dict(size=12, color='#94A3B8'),
                    x=0
                ),
                height=280,
                margin=dict(l=0, r=0, t=40, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(15,12,25,1)',
                font=dict(color='#94A3B8', size=10),
                xaxis=dict(showgrid=False, zeroline=False, color='#4B5563'),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(168,85,247,0.08)',
                    zeroline=False,
                    tickformat='₹,.0f',
                    color='#4B5563'
                ),
                showlegend=False,
                hovermode='x unified',
                hoverlabel=dict(
                    bgcolor='rgba(30,25,45,0.95)',
                    bordercolor='rgba(168,85,247,0.3)',
                    font=dict(color='#F8FAFC', size=11)
                )
            )
            st.plotly_chart(fig_proj, use_container_width=True)

        st.markdown("<div style='margin-top:1rem;'></div>",
                    unsafe_allow_html=True)

        st.markdown("""
<div style="font-size:11px;font-weight:700;color:#A855F7;letter-spacing:0.1em;margin-bottom:10px;">
FUND RECOMMENDATIONS PER GOAL</div>
""", unsafe_allow_html=True)

        fund_cols = st.columns(min(len(goals), 3))
        for i, goal in enumerate(goals):
            with fund_cols[i % 3]:
                rec = fund_recs.get(goal["type"], "Large Cap index fund")
                parts = rec.split(" — ")
                fund_name = parts[0]
                fund_why = parts[1] if len(parts) > 1 else ""

                st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.15);border-top:2px solid #A855F7;border-radius:10px;padding:14px;height:100%;">
<div style="font-size:16px;margin-bottom:6px;">{goal['icon']}</div>
<div style="font-size:12px;font-weight:600;color:#F8FAFC;margin-bottom:4px;">{goal['type']}</div>
<div style="font-size:11px;color:#20C997;font-weight:500;margin-bottom:6px;">{fund_name}</div>
<div style="font-size:10px;color:#6B7280;line-height:1.5;">{fund_why}</div>
<div style="margin-top:10px;padding-top:8px;border-top:1px solid rgba(168,85,247,0.1);">
<div style="display:flex;justify-content:space-between;font-size:10px;">
<span style="color:#94A3B8;">Monthly SIP</span>
<span style="color:#20C997;font-weight:600;">₹{goal['sip_needed']:,.0f}</span>
</div>
<div style="display:flex;justify-content:space-between;font-size:10px;margin-top:3px;">
<span style="color:#94A3B8;">Target</span>
<span style="color:#F8FAFC;font-weight:600;">₹{goal['amount']:,}</span>
</div>
<div style="display:flex;justify-content:space-between;font-size:10px;margin-top:3px;">
<span style="color:#94A3B8;">Timeline</span>
<span style="color:#F8FAFC;font-weight:600;">{goal['years']} years</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem;'></div>",
                    unsafe_allow_html=True)

        st.markdown("""
<div style="font-size:11px;font-weight:700;color:#A855F7;letter-spacing:0.1em;margin-bottom:10px;">
SAFE INVESTMENT OPTIONS — BEYOND MUTUAL FUNDS
</div>
""", unsafe_allow_html=True)

        safe_col1, safe_col2, safe_col3, safe_col4 = st.columns(4)

        with safe_col1:
            st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(245,158,11,0.3);border-top:2px solid #F59E0B;border-radius:10px;padding:14px;">
<div style="font-size:20px;margin-bottom:6px;">🥇</div>
<div style="font-size:12px;font-weight:600;color:#F59E0B;margin-bottom:6px;">Gold Investment</div>
<div style="font-size:11px;color:#E2E8F0;line-height:1.6;margin-bottom:8px;">
Allocate 5-10% of portfolio to gold.
Best options: <strong style="color:#F8FAFC;">Gold ETF or Sovereign Gold Bond (SGB)</strong>.
SGB gives 2.5% extra interest + gold price appreciation.
</div>
<div style="background:rgba(245,158,11,0.08);border-radius:6px;padding:8px;">
<div style="font-size:10px;color:#94A3B8;margin-bottom:3px;">Suggested allocation</div>
<div style="font-size:13px;font-weight:700;color:#F59E0B;">₹{int(surplus * 0.07):,}/month</div>
<div style="font-size:10px;color:#6B7280;">7% of your surplus</div>
</div>
<div style="margin-top:8px;font-size:10px;color:#94A3B8;line-height:1.5;">
📈 10-year gold CAGR in India: ~10%<br>
🛡️ Best hedge against inflation<br>
💡 Sovereign Gold Bond: Zero making charge
</div>
</div>""", unsafe_allow_html=True)

        with safe_col2:
            st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(59,130,246,0.3);border-top:2px solid #3B82F6;border-radius:10px;padding:14px;">
<div style="font-size:20px;margin-bottom:6px;">🏗️</div>
<div style="font-size:12px;font-weight:600;color:#3B82F6;margin-bottom:6px;">Real Estate / Land</div>
<div style="font-size:11px;color:#E2E8F0;line-height:1.6;margin-bottom:8px;">
Land in Tier-2/3 cities gives 8-12% appreciation.
Best option without large capital: <strong style="color:#F8FAFC;">REITs</strong>
— invest in real estate from ₹300/unit.
</div>
<div style="background:rgba(59,130,246,0.08);border-radius:6px;padding:8px;">
<div style="font-size:10px;color:#94A3B8;margin-bottom:3px;">REIT minimum investment</div>
<div style="font-size:13px;font-weight:700;color:#3B82F6;">₹300 per unit</div>
<div style="font-size:10px;color:#6B7280;">Embassy, Mindspace, Nexus REITs</div>
</div>
<div style="margin-top:8px;font-size:10px;color:#94A3B8;line-height:1.5;">
📈 Avg REIT return India: 8-10% p.a.<br>
💰 Quarterly dividend income<br>
🏢 Commercial property exposure
</div>
</div>""", unsafe_allow_html=True)

        with safe_col3:
            fd_rate = 7.25
            fd_amount = int(emergency_needed)
            fd_return = fd_amount * (fd_rate / 100)
            st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(32,201,151,0.3);border-top:2px solid #20C997;border-radius:10px;padding:14px;">
<div style="font-size:20px;margin-bottom:6px;">🏦</div>
<div style="font-size:12px;font-weight:600;color:#20C997;margin-bottom:6px;">Fixed Deposit</div>
<div style="font-size:11px;color:#E2E8F0;line-height:1.6;margin-bottom:8px;">
For emergency fund and safe returns.
<strong style="color:#F8FAFC;">Small Finance Banks</strong> offer
up to 9% FD rate. DICGC insured up to ₹5L.
</div>
<div style="background:rgba(32,201,151,0.08);border-radius:6px;padding:8px;">
<div style="font-size:10px;color:#94A3B8;margin-bottom:3px;">If you FD your emergency fund</div>
<div style="font-size:13px;font-weight:700;color:#20C997;">+₹{fd_return:,.0f}/year</div>
<div style="font-size:10px;color:#6B7280;">at 7.25% on ₹{fd_amount:,}</div>
</div>
<div style="margin-top:8px;font-size:10px;color:#94A3B8;line-height:1.5;">
🏦 Best FD rates: AU Bank, Ujjivan, ESAF<br>
📅 Lock-in: 1-5 years<br>
✅ Zero market risk — guaranteed returns
</div>
</div>""", unsafe_allow_html=True)

        with safe_col4:
            ppf_annual = min(150000, int(surplus * 12 * 0.1))
            ppf_return = ppf_annual * 0.071
            st.markdown(f"""
<div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.3);border-top:2px solid #A855F7;border-radius:10px;padding:14px;">
<div style="font-size:20px;margin-bottom:6px;">📮</div>
<div style="font-size:12px;font-weight:600;color:#A855F7;margin-bottom:6px;">PPF + NPS</div>
<div style="font-size:11px;color:#E2E8F0;line-height:1.6;margin-bottom:8px;">
PPF: 7.1% tax-free returns + ₹1.5L tax deduction under 80C.
NPS: Extra ₹50,000 tax deduction under 80CCD.
</div>
<div style="background:rgba(168,85,247,0.08);border-radius:6px;padding:8px;">
<div style="font-size:10px;color:#94A3B8;margin-bottom:3px;">Annual PPF + tax saving</div>
<div style="font-size:13px;font-weight:700;color:#A855F7;">₹{ppf_return:,.0f} + tax saved</div>
<div style="font-size:10px;color:#6B7280;">Invest ₹{ppf_annual//12:,}/month in PPF</div>
</div>
<div style="margin-top:8px;font-size:10px;color:#94A3B8;line-height:1.5;">
🔒 PPF lock-in: 15 years<br>
💰 Save up to ₹46,800 in taxes<br>
🏛️ Government guaranteed — zero risk
</div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem;'></div>",
                    unsafe_allow_html=True)

        st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(168,85,247,0.12) 0%,rgba(32,201,151,0.08) 100%);border:1px solid rgba(168,85,247,0.25);border-radius:12px;padding:20px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;">
<div>
<div style="font-size:11px;color:#94A3B8;font-weight:600;letter-spacing:0.08em;margin-bottom:6px;">12-MONTH MILESTONE</div>
<div style="font-size:13px;color:#E2E8F0;line-height:1.7;max-width:500px;">
Follow this plan for 12 months and your portfolio grows to
<strong style="color:#20C997;font-size:15px;">₹{corpus_1yr:,.0f}</strong>.
Emergency fund fully built. All goals on track. Family financially protected. 🎯
</div>
</div>
<div style="text-align:center;">
<div style="font-size:10px;color:#6B7280;margin-bottom:4px;">ANNUAL SAVINGS</div>
<div style="font-size:1.8rem;font-weight:800;color:#A855F7;">₹{total_sip*12:,.0f}</div>
<div style="font-size:10px;color:#6B7280;">invested per year</div>
</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem;'></div>",
                    unsafe_allow_html=True)

        st.markdown("""
<div style="font-size:10px;color:#4B5563;text-align:center;margin-bottom:12px;">
⚠️ This plan is for educational purposes only.
Consult a SEBI-registered financial advisor before making investment decisions.
</div>
""", unsafe_allow_html=True)
