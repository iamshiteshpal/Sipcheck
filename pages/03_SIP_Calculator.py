# pages/03_SIP_Calculator.py — SipCheck SIP Calculator (public — no CAS required)
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go

st.set_page_config(
    page_title="SIP Calculator — SipCheck",
    page_icon="🧮",
    layout="wide",
)
from sidebar_v2 import render_sidebar
render_sidebar()
from ui_theme import inject_theme, page_header, section
inject_theme()

# ── Extra page CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
.result-big {
    font-family:'JetBrains Mono',monospace;
    font-size:2.8rem; font-weight:700; line-height:1.1;
    background:linear-gradient(90deg,#22d3ee,#8b5cf6);
    -webkit-background-clip:text; background-clip:text; color:transparent;
}
.result-lbl {
    font-size:0.72rem; font-weight:600; color:#8b93a7;
    text-transform:uppercase; letter-spacing:0.14em; margin-bottom:6px;
}
.result-sub { font-size:0.80rem; color:#8b93a7; margin-top:6px; }

.kpi3 { display:flex; gap:10px; flex-wrap:wrap; margin:1rem 0; }
.kpi3-t {
    flex:1; min-width:120px;
    background:rgba(17,17,48,0.55); border:1px solid rgba(139,92,246,0.16);
    border-radius:12px; padding:0.75rem 1rem;
}
.kpi3-l {
    font-size:0.6rem; font-weight:600; color:#8b93a7;
    text-transform:uppercase; letter-spacing:0.12em; margin-bottom:3px;
}
.kpi3-v {
    font-family:'JetBrains Mono',monospace; font-size:1.15rem;
    font-weight:700; color:#f0f0ff;
}
.kpi3-v.gr { color:#34d399; }
.kpi3-v.cy { color:#22d3ee; }

.insight-box {
    background:rgba(139,92,246,0.07); border:1px solid rgba(139,92,246,0.22);
    border-left:4px solid #8b5cf6; border-radius:12px;
    padding:0.9rem 1.3rem; font-size:0.92rem; color:#f0f0ff;
    line-height:1.65; margin:1.2rem 0;
}
.insight-box .hi { color:#22d3ee; font-weight:700; }

.ls-box {
    background:rgba(251,191,36,0.05); border:1px solid rgba(251,191,36,0.2);
    border-radius:12px; padding:0.85rem 1.2rem; margin:0.8rem 0;
}
.ls-row { display:flex; gap:16px; flex-wrap:wrap; }
.ls-item { flex:1; min-width:130px; }
.ls-lbl {
    font-size:0.62rem; font-weight:600; color:#8b93a7;
    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:2px;
}
.ls-val { font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:700; }
.ls-note { font-size:0.68rem; color:#8b93a7; margin-top:8px; }

.cta-box {
    background:rgba(139,92,246,0.07); border:1px solid rgba(139,92,246,0.18);
    border-radius:16px; padding:1.4rem 1.8rem; text-align:center; margin-top:2rem;
}
.cta-t {
    font-family:'Space Grotesk',sans-serif; font-size:1.05rem;
    color:#f0f0ff; margin-bottom:6px; font-weight:600;
}
.cta-s { font-size:0.8rem; color:#8b93a7; }

@media (max-width:768px) {
    .result-big { font-size:2.1rem !important; }
    .kpi3-v { font-size:1rem !important; }
    .insight-box { font-size:0.82rem !important; padding:0.75rem 1rem !important; }
    .cta-box { padding:1rem 1.1rem !important; }
    .ls-row { gap:10px; }
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────
def _fmt(v: float) -> str:
    if v >= 1e7:
        return f"₹{v/1e7:.2f} Cr"
    if v >= 1e5:
        return f"₹{v/1e5:.2f} L"
    return f"₹{v:,.0f}"


def build_yearly(monthly: float, rate: float, years: int, stepup: float = 0.0):
    r = rate / 12 / 100
    portfolio = invested = 0.0
    cur = monthly
    labels, inv_list, val_list = [], [], []
    for yr in range(1, years + 1):
        for _ in range(12):
            portfolio = portfolio * (1 + r) + cur
            invested += cur
        if stepup > 0:
            cur *= (1 + stepup / 100)
        labels.append(yr)
        inv_list.append(round(invested, 2))
        val_list.append(round(portfolio, 2))
    return labels, inv_list, val_list


def ls_yearly(total: float, rate: float, years: int) -> list:
    return [round(total * (1 + rate / 100) ** y, 2) for y in range(1, years + 1)]


# ── Separate CSS string for the share card (not f-string, so {} are literal) ──
_SHARE_CSS = """
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:transparent;font-family:system-ui,sans-serif;}
.card{
  background:linear-gradient(135deg,#0f0f2e 0%,#1a0b2e 55%,#0a1628 100%);
  border:1px solid rgba(139,92,246,0.35);
  border-radius:16px;padding:20px 24px;color:#f0f0ff;width:100%;
}
.brand-name{font-size:1.05rem;font-weight:700;margin-bottom:2px;}
.brand-name span{color:#8b5cf6;}
.brand-tag{font-size:0.58rem;color:#6b7280;letter-spacing:0.15em;font-weight:600;margin-bottom:14px;}
.divider{height:1px;background:rgba(139,92,246,0.2);margin:10px 0;}
.row{display:flex;justify-content:space-between;align-items:center;padding:4px 0;font-size:0.83rem;}
.row-l{color:#8b93a7;}
.row-v{font-family:'JetBrains Mono',monospace;font-weight:600;}
.big{font-size:1.55rem;font-weight:700;color:#22d3ee;font-family:'JetBrains Mono',monospace;margin:8px 0;}
.green{color:#34d399;}.amber{color:#fbbf24;}.purple{color:#8b5cf6;}
.btn-row{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap;}
.btn{
  flex:1;min-width:110px;padding:9px 14px;border-radius:9px;
  border:1px solid rgba(139,92,246,0.4);background:rgba(139,92,246,0.12);
  color:#f0f0ff;cursor:pointer;font-size:0.82rem;font-weight:600;
  transition:background .2s;
}
.btn:hover{background:rgba(139,92,246,0.25);}
.ok{color:#34d399!important;border-color:rgba(52,211,153,0.4)!important;}
@media print{
  body{background:#0f0f2e;}
  .btn-row{display:none!important;}
}
</style>
"""

# ─────────────────────────────── PAGE ────────────────────────────────────
page_header(
    "🧮 SIP Calculator",
    "Estimate your SIP corpus · No signup · No CAS upload required",
)

# ── Inputs ────────────────────────────────────────────────────────────────
section("Configure Your SIP Plan")
left, right = st.columns([1, 1.3], gap="large")

with left:
    sip_amt   = st.slider("Monthly SIP Amount (₹)", 500, 100_000, 5_000, step=500,
                          help="Amount you plan to invest every month")
    rate      = st.slider("Expected Annual Return (%)", 5.0, 20.0, 12.0, step=0.5,
                          help="Historical large-cap equity MF average is ~12–14% long term")
    years     = st.slider("Investment Period (Years)", 1, 40, 15)
    stepup_on = st.toggle("Step-up SIP  —  increase amount every year")
    stepup_pct = 0.0
    if stepup_on:
        stepup_pct = float(st.slider("Annual Step-up (%)", 1, 30, 10,
                                     help="SIP amount grows by this % at the start of each year"))
    cmp_ls = st.toggle("Compare with Lumpsum investment")

# ── Calculations ──────────────────────────────────────────────────────────
yr_labels, yr_inv, yr_val = build_yearly(
    sip_amt, rate, years, stepup_pct if stepup_on else 0.0
)
final_val   = yr_val[-1]
total_inv   = yr_inv[-1]
wealth_gain = final_val - total_inv
multiple    = final_val / total_inv if total_inv > 0 else 1.0
ls_vals     = ls_yearly(total_inv, rate, years) if cmp_ls else []
ls_final    = ls_vals[-1] if ls_vals else 0.0

with right:
    # Big corpus display
    stepup_note_sub = f" · Step-up {stepup_pct:.0f}%/yr" if stepup_on else ""
    st.markdown(
        f'<div class="g-card">'
        f'<div class="result-lbl">Estimated Corpus</div>'
        f'<div class="result-big">{_fmt(final_val)}</div>'
        f'<div class="result-sub">in {years} year{"s" if years > 1 else ""}'
        f' &nbsp;·&nbsp; SIP: {_fmt(sip_amt)}/mo{stepup_note_sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # KPI tiles
    st.markdown(
        f'<div class="kpi3">'
        f'<div class="kpi3-t"><div class="kpi3-l">Total Invested</div>'
        f'<div class="kpi3-v">{_fmt(total_inv)}</div></div>'
        f'<div class="kpi3-t"><div class="kpi3-l">Wealth Gained</div>'
        f'<div class="kpi3-v gr">{_fmt(wealth_gain)}</div></div>'
        f'<div class="kpi3-t"><div class="kpi3-l">Return Multiple</div>'
        f'<div class="kpi3-v cy">{multiple:.1f}x</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Donut chart
    fig_d = go.Figure(go.Pie(
        values=[total_inv, wealth_gain],
        labels=["Total Invested", "Wealth Gained"],
        hole=0.62,
        marker=dict(
            colors=["#8b5cf6", "#34d399"],
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        textinfo="none",
        hovertemplate="%{label}: ₹%{value:,.0f} (%{percent})<extra></extra>",
    ))
    fig_d.add_annotation(
        text=f"<b>{multiple:.1f}x</b>",
        x=0.5, y=0.55, showarrow=False,
        font=dict(size=20, color="#22d3ee", family="JetBrains Mono"),
    )
    fig_d.add_annotation(
        text="returns",
        x=0.5, y=0.38, showarrow=False,
        font=dict(size=11, color="#8b93a7"),
    )
    fig_d.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.12,
            x=0.5, xanchor="center",
            font=dict(color="#8b93a7", size=11),
        ),
        margin=dict(l=10, r=10, t=5, b=35),
        height=210,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})

# ── Lumpsum comparison box ────────────────────────────────────────────────
if cmp_ls:
    sip_wins = final_val > ls_final
    diff_str = _fmt(abs(final_val - ls_final))
    verdict  = ("SIP wins" if sip_wins else "Lumpsum wins") + f" by {diff_str}"
    v_color  = "#34d399" if sip_wins else "#fbbf24"
    st.markdown(
        f'<div class="ls-box"><div class="ls-row">'
        f'<div class="ls-item"><div class="ls-lbl">SIP Final Value</div>'
        f'<div class="ls-val" style="color:#22d3ee">{_fmt(final_val)}</div></div>'
        f'<div class="ls-item"><div class="ls-lbl">Lumpsum Final Value</div>'
        f'<div class="ls-val" style="color:#fbbf24">{_fmt(ls_final)}</div></div>'
        f'<div class="ls-item"><div class="ls-lbl">Verdict</div>'
        f'<div class="ls-val" style="color:{v_color}">{verdict}</div></div>'
        f'</div>'
        f'<div class="ls-note">&#x2139;&#xfe0f; Lumpsum assumes {_fmt(total_inv)} invested'
        f' on Day 1 at {rate:.1f}% p.a. compounded annually.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Year-by-year growth chart ─────────────────────────────────────────────
section("Year-by-Year Growth")
fig_a = go.Figure()
fig_a.add_trace(go.Scatter(
    x=yr_labels, y=yr_inv, name="Amount Invested",
    fill="tozeroy",
    line=dict(color="#8b5cf6", width=2),
    fillcolor="rgba(139,92,246,0.10)",
    hovertemplate="Year %{x} · Invested: ₹%{y:,.0f}<extra></extra>",
))
fig_a.add_trace(go.Scatter(
    x=yr_labels, y=yr_val, name="Portfolio Value",
    fill="tonexty",
    line=dict(color="#22d3ee", width=2.5),
    fillcolor="rgba(34,211,238,0.09)",
    hovertemplate="Year %{x} · Portfolio: ₹%{y:,.0f}<extra></extra>",
))
if cmp_ls:
    fig_a.add_trace(go.Scatter(
        x=yr_labels, y=ls_vals,
        name=f"Lumpsum ({_fmt(total_inv)} on Day 1)",
        line=dict(color="#fbbf24", width=2, dash="dash"),
        hovertemplate="Year %{x} · Lumpsum: ₹%{y:,.0f}<extra></extra>",
    ))
fig_a.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(
        title="Year",
        gridcolor="rgba(139,92,246,0.08)",
        tickfont=dict(color="#8b93a7"),
        title_font=dict(color="#8b93a7"),
        dtick=max(1, years // 10),
    ),
    yaxis=dict(
        title="Value (₹)",
        gridcolor="rgba(139,92,246,0.08)",
        tickfont=dict(color="#8b93a7"),
        title_font=dict(color="#8b93a7"),
        tickformat=",.0f",
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, x=0,
        font=dict(color="#8b93a7", size=11),
        bgcolor="rgba(0,0,0,0)",
    ),
    margin=dict(l=10, r=10, t=30, b=40),
    height=340,
    hovermode="x unified",
)
st.plotly_chart(fig_a, use_container_width=True, config={"displayModeBar": False})

# ── Insight line ──────────────────────────────────────────────────────────
_su_note = f" growing {stepup_pct:.0f}%/yr" if stepup_on else ""
_ls_note  = (
    f" Lumpsum of same amount gives <span class='hi'>{_fmt(ls_final)}</span>."
    if cmp_ls else ""
)
st.markdown(
    f'<div class="insight-box">'
    f'&#x1f4a1; Investing <span class="hi">{_fmt(sip_amt)}/month{_su_note}</span>'
    f' for <span class="hi">{years} year{"s" if years > 1 else ""}</span>'
    f' at <span class="hi">{rate:.1f}% p.a.</span>'
    f' can grow to <span class="hi">{_fmt(final_val)}</span> &mdash;'
    f' that\'s <span class="hi">{multiple:.1f}x</span>'
    f' your total invested amount of {_fmt(total_inv)}.{_ls_note}'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Share This Plan ───────────────────────────────────────────────────────
section("Share This Plan")

_su_tag   = f" (+{stepup_pct:.0f}%/yr step-up)" if stepup_on else ""
_ls_line  = f"\nvs Lumpsum:      {_fmt(ls_final)}" if cmp_ls else ""
share_text = (
    f"\U0001f4ca SipCheck — SIP Calculator\n"
    f"{'─'*33}\n"
    f"Monthly SIP:     {_fmt(sip_amt)}{_su_tag}\n"
    f"Return Rate:     {rate:.1f}% p.a.\n"
    f"Period:          {years} years\n"
    f"{'─'*33}\n"
    f"Total Invested:  {_fmt(total_inv)}\n"
    f"Estimated Value: {_fmt(final_val)}\n"
    f"Wealth Gained:   {_fmt(wealth_gain)}\n"
    f"Return Multiple: {multiple:.1f}x"
    f"{_ls_line}\n"
    f"{'─'*33}\n"
    f"Plan your SIP at SipCheck \U0001f680"
)
_js_text = share_text.replace("\\", "\\\\").replace("`", "'").replace("${", "\\${")

_ls_row_html = (
    f'<div class="row"><span class="row-l">vs Lumpsum (same ₹)</span>'
    f'<span class="row-v amber">{_fmt(ls_final)}</span></div>'
    if cmp_ls else ""
)
_su_card = f" +{stepup_pct:.0f}%/yr" if stepup_on else ""
_share_h  = 460 if cmp_ls else 430

share_html = (
    f'<!DOCTYPE html><html><head><meta charset="utf-8">{_SHARE_CSS}</head><body>'
    f'<div class="card">'
    f'<div class="brand-name">Sip<span>Check</span> \U0001f4ca</div>'
    f'<div class="brand-tag">SIP CALCULATOR SUMMARY</div>'
    f'<div class="divider"></div>'
    f'<div class="row"><span class="row-l">Monthly SIP</span>'
    f'<span class="row-v purple">{_fmt(sip_amt)}{_su_card}</span></div>'
    f'<div class="row"><span class="row-l">Annual Return</span>'
    f'<span class="row-v">{rate:.1f}% p.a.</span></div>'
    f'<div class="row"><span class="row-l">Period</span>'
    f'<span class="row-v">{years} years</span></div>'
    f'<div class="divider"></div>'
    f'<div style="font-size:0.62rem;color:#8b93a7;letter-spacing:0.12em;margin-bottom:2px;">ESTIMATED CORPUS</div>'
    f'<div class="big">{_fmt(final_val)}</div>'
    f'<div class="row"><span class="row-l">Total Invested</span>'
    f'<span class="row-v">{_fmt(total_inv)}</span></div>'
    f'<div class="row"><span class="row-l">Wealth Gained</span>'
    f'<span class="row-v green">{_fmt(wealth_gain)}</span></div>'
    f'<div class="row"><span class="row-l">Return Multiple</span>'
    f'<span class="row-v">{multiple:.1f}x</span></div>'
    f'{_ls_row_html}'
    f'<div class="btn-row">'
    f'<button class="btn" id="cb" onclick="cpText()">\U0001f4cb Copy Summary</button>'
    f'<button class="btn" onclick="window.print()">\U0001f5a8️ Save / Print</button>'
    f'</div></div>'
    f'<script>'
    f'const T=`{_js_text}`;'
    f'function cpText(){{'
    f'  const b=document.getElementById("cb");'
    f'  navigator.clipboard.writeText(T).then(()=>{{'
    f'    b.textContent="✅ Copied!";b.classList.add("ok");'
    f'    setTimeout(()=>{{b.textContent="\U0001f4cb Copy Summary";b.classList.remove("ok");}},2000);'
    f'  }}).catch(()=>{{'
    f'    const ta=document.createElement("textarea");'
    f'    ta.value=T;document.body.appendChild(ta);ta.select();'
    f'    document.execCommand("copy");document.body.removeChild(ta);'
    f'    b.textContent="✅ Copied!";b.classList.add("ok");'
    f'    setTimeout(()=>{{b.textContent="\U0001f4cb Copy Summary";b.classList.remove("ok");}},2000);'
    f'  }});'
    f'}}'
    f'</script>'
    f'</body></html>'
)

components.html(share_html, height=_share_h, scrolling=False)

# ── CTA ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="cta-box">'
    '<div class="cta-t">\U0001f4c1 Want to see how your actual mutual funds compare?</div>'
    '<div class="cta-s">Upload your CAS PDF on the home page to get real XIRR, fund-wise P&amp;L,'
    ' switch history, SIP health score and AI insights &mdash; all private, processed on-device.</div>'
    '</div>',
    unsafe_allow_html=True,
)
st.page_link(
    "dashboard.py",
    label="⬆️  Upload your CAS  →  Free · Instant · Private",
    use_container_width=False,
)
