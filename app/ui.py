import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.config import C_ACCENT, C_ACCENT2, C_GAIN, C_LOSS, GRID, PLOT_BASE
from app.exporters import generate_excel, generate_html
from app.helpers import clean_name, fmt_inr, gain_arrow, gain_color, to_date
from app.live import fetch_live_navs
from app.parser import parse_pdf
from app.processor import process


def initialize_session_state():
    defaults = {
        "profiles": {},
        "active": None,
        "show_email": True,
        "pin_ok": False,
        "switch_target": None,
        "live_data": {},
        "live_last_updated": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def active_data():
    active = st.session_state.active
    return st.session_state.profiles.get(active) if active else None


def show_upload():
    st.markdown(
        """
        <div style="display:flex;justify-content:center;padding-top:48px;">
          <div style="max-width:520px;width:100%;text-align:center;">
            <div style="width:64px;height:64px;background:rgba(99,179,237,0.08);border:1px solid rgba(99,179,237,0.2);
                        border-radius:18px;display:flex;align-items:center;justify-content:center;
    margin:0 auto 22px;font-size:28px;">📂</div>
            <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:#f7fafc;
    letter-spacing:-0.5px;margin-bottom:8px;">Upload your CAS PDF</div>
            <div style="font-size:14px;color:#718096;margin-bottom:32px;line-height:1.7;">
              Consolidated Account Statement from CAMS or KFintech.<br>
              Your data never leaves your device.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col = st.columns([1, 2, 1])[1]
    with col:
        uploaded = st.file_uploader("CAS PDF", type=["pdf"], label_visibility="collapsed")
        password = st.text_input("PDF Password", type="password", placeholder="PAN / Date of Birth")

        if uploaded and password:
            if st.button("Analyse Portfolio →", use_container_width=True, type="primary"):
                with st.spinner("Parsing…"):
                    data, error = parse_pdf(uploaded.read(), password)
                if error == "wrong_password":
                    st.error("Wrong password. Try your PAN number or date of birth (DDMMYYYY).")
                elif error:
                    st.error(f"Parse error: {error}")
                else:
                    portfolio = process(data)
                    investor_name = portfolio["investor_name"].title()
                    st.session_state.profiles[investor_name] = portfolio
                    st.session_state.active = investor_name
                    st.session_state.pin_ok = True
                    st.success(f"Portfolio loaded — {investor_name}")
                    st.rerun()


def build_sidebar(data):
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:6px 0 20px;">
              <div style="font-family:'Syne',sans-serif;font-size:21px;font-weight:800;
    color:#f7fafc;letter-spacing:-0.5px;">CAS 360 <span style="color:#63b3ed;">View</span></div>
              <div style="font-size:10px;color:#2d3748;text-transform:uppercase;letter-spacing:2px;
    font-weight:600;margin-top:2px;">Portfolio Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if data:
            menu = st.radio(
                "nav",
                ["Dashboard", "My Portfolio", "SIP Center", "Transactions", "Alerts"],
                label_visibility="collapsed",
            )
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            email_display = data["investor_email"] if st.session_state.show_email else "••••••••••"
            st.markdown(
                f"""
                <div style="background:rgba(99,179,237,0.04);border:1px solid rgba(99,179,237,0.12);
                            border-radius:10px;padding:12px 14px;margin-bottom:10px;">
                  <div style="font-size:13px;font-weight:600;color:#f7fafc;margin-bottom:2px;">
                    {data['investor_name'].title()}</div>
                """,
                unsafe_allow_html=True,
            )

            ec1, ec2 = st.columns([5, 1])
            with ec1:
                st.markdown(f"<div style='font-size:11px;color:#4a5568;'>{email_display}</div>", unsafe_allow_html=True)
            with ec2:
                if st.button("👁" if st.session_state.show_email else "🙈", key="eye"):
                    st.session_state.show_email = not st.session_state.show_email
                    st.rerun()

            try:
                statement_date = to_date(data["statement_date"]).strftime("%d %b %Y")
            except Exception:
                statement_date = "—"
            st.markdown(
                f"""
                <div style="font-size:10px;color:#2d3748;margin-top:6px;">STATEMENT · {statement_date}</div>
                </div>""",
                unsafe_allow_html=True,
            )

            if len(st.session_state.profiles) > 1:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                keys = list(st.session_state.profiles.keys())
                index = keys.index(st.session_state.active) if st.session_state.active in keys else 0
                selected = st.selectbox("Switch Profile", keys, index=index, label_visibility="collapsed")
                if selected != st.session_state.active:
                    st.session_state.switch_target = selected
                    st.session_state.pin_ok = False
                if not st.session_state.pin_ok and st.session_state.switch_target:
                    pin = st.text_input("PIN", type="password", max_chars=4, placeholder="••••")
                    if pin == "2002":
                        st.session_state.active = st.session_state.switch_target
                        st.session_state.switch_target = None
                        st.session_state.pin_ok = True
                        st.rerun()
                    elif len(pin) == 4:
                        st.error("Wrong PIN")

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("＋ Add Another CAS", use_container_width=True):
                st.session_state.active = None
                st.session_state.pin_ok = False
                st.rerun()

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("🚪 Logout & Clear Data", use_container_width=True):
                st.session_state.clear()
                st.rerun()

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(
                "<div style='font-size:10px;color:#2d3748;text-transform:uppercase;letter-spacing:1.5px;font-weight:600;margin-bottom:8px;'>Export</div>",
                unsafe_allow_html=True,
            )

            live_data = st.session_state.get("live_data", {})
            xls = generate_excel(data, live_data)
            if xls:
                st.download_button(
                    "📊 Excel",
                    data=xls,
                    file_name=f"CAS360_{data['investor_name']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            st.download_button(
                "📄 HTML Report (Print as PDF)",
                data=generate_html(data, live_data),
                file_name=f"CAS360_{data['investor_name']}.html",
                mime="text/html",
                use_container_width=True,
            )
        else:
            menu = "upload"
            if st.session_state.profiles:
                keys = list(st.session_state.profiles.keys())
                selected = st.selectbox("Return to", ["— select —"] + keys, label_visibility="collapsed")
                if selected != "— select —":
                    st.session_state.active = selected
                    st.session_state.pin_ok = True
                    st.rerun()
    return menu


def render_dashboard(data):
    first_name = data["investor_name"].split()[0].title()
    st.markdown(f'<div class="page-title">Welcome back, {first_name} 👋</div>', unsafe_allow_html=True)
    try:
        statement_date = to_date(data["statement_date"]).strftime("%d %b %Y")
    except Exception:
        statement_date = "—"

    nc1, nc2 = st.columns([3, 1])
    with nc1:
        st.markdown(
            f"""
            <div class="notice" style="margin-bottom:8px;">
              <span style="color:#63b3ed;font-size:16px;">◈</span>
              <div>
                <span style="color:#63b3ed;font-size:11px;font-weight:700;text-transform:uppercase;
        letter-spacing:1px;">CAS Statement · {statement_date}</span><br>
                Base figures computed from your uploaded PDF.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with nc2:
        if st.button("🔄 Refresh Latest NAV", use_container_width=True):
            with st.spinner("Fetching latest NAVs from AMFI..."):
                live_data, live_date = fetch_live_navs(data["holdings"])
                st.session_state.live_data = live_data
                st.session_state.live_last_updated = live_date
            st.rerun()

    display_wealth = data["total_value"]
    if st.session_state.live_data:
        st.markdown(
            f"""
            <div style="background:rgba(72,187,120,0.1);border:1px solid rgba(72,187,120,0.25);
                        border-radius:10px;padding:8px 16px;margin-bottom:20px;display:inline-flex;
                        align-items:center;gap:8px;color:#48bb78;font-size:12px;font-weight:700;">
                <span style="display:inline-block;width:8px;height:8px;background:#48bb78;border-radius:50%;box-shadow:0 0 6px #48bb78;"></span>
                LIVE DATA ACTIVE · Latest NAVs as of {st.session_state.live_last_updated}
            </div>
            """,
            unsafe_allow_html=True,
        )
        new_wealth = 0
        for holding in data["holdings"]:
            scheme_name = holding["scheme"]
            if scheme_name in st.session_state.live_data:
                new_wealth += st.session_state.live_data[scheme_name]["live_value"]
            else:
                new_wealth += holding["value"]
        display_wealth = new_wealth

    display_pnl = display_wealth - data["total_invested"]
    pnl_pct = (display_pnl / data["total_invested"] * 100) if data["total_invested"] else 0.0
    sip_monthly = sum(s["amount"] for s in data["live_sips"])

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Wealth", fmt_inr(display_wealth))
    with m2:
        st.metric("Invested", fmt_inr(data["total_invested"]))
    with m3:
        st.metric("Unrealized P&L", fmt_inr(display_pnl), delta=f"{gain_arrow(display_pnl)} {abs(pnl_pct):.2f}% all-time")
    with m4:
        st.metric("Monthly SIP", fmt_inr(sip_monthly), delta=f"{len(data['live_sips'])} active")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    ch, al = st.columns([3, 2])
    with ch:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Wealth Journey</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="font-family:'IBM Plex Mono',monospace;font-size:28px;font-weight:700;
    color:#f7fafc;letter-spacing:-1px;margin-bottom:8px;">{fmt_inr(display_wealth)}</div>
            <span class=\"{'pill-gain' if display_pnl>=0 else 'pill-loss'}\">{gain_arrow(display_pnl)} {fmt_inr(display_pnl)}</span>
            """,
            unsafe_allow_html=True,
        )

        timeframe = st.segmented_control("tf", ["1M", "6M", "1Y", "3Y", "ALL"], default="1Y", label_visibility="collapsed")
        base_value = display_wealth
        invested_value = data["total_invested"]
        slices = {
            "1M": (["May 5", "May 10", "May 15", "May 20", "May 27"], [base_value * 0.97, base_value * 0.985, base_value * 0.975, base_value * 0.99, base_value]),
            "6M": (["Dec", "Jan", "Feb", "Mar", "Apr", "May"], [invested_value * 0.87, invested_value * 0.92, invested_value * 0.95, invested_value * 0.97, base_value * 0.99, base_value]),
            "1Y": (["Jun '25", "Sep '25", "Dec '25", "Mar '26", "May '26"], [invested_value * 0.91, invested_value * 0.95, invested_value * 0.97, base_value * 0.99, base_value]),
            "3Y": (["May '23", "Nov '23", "May '24", "Nov '24", "May '25", "Nov '25", "May '26"], [invested_value * 0.35, invested_value * 0.55, invested_value * 0.70, invested_value * 0.83, invested_value * 0.93, base_value * 0.98, base_value]),
            "ALL": (["Jan '24", "Jul '24", "Jan '25", "Jul '25", "Jan '26", "May '26"], [invested_value * 0.20, invested_value * 0.48, invested_value * 0.68, invested_value * 0.83, invested_value * 0.93, base_value]),
        }
        xs, ys = slices.get(timeframe, slices["1Y"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=xs,
            y=ys,
            mode="lines+markers",
            line=dict(color=C_ACCENT, width=2.5, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(99,179,237,0.06)",
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            height=220,
            xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#4a5568")),
            yaxis=dict(showgrid=True, gridcolor=GRID, tickfont=dict(size=11, color="#4a5568")),
            hovermode="x unified",
            **PLOT_BASE,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with al:
        st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Asset Allocation</div>', unsafe_allow_html=True)
        allocation_pct = data["alloc_pct"]
        allocation_values = data["alloc_values"]
        if allocation_pct:
            df_pie = pd.DataFrame({"Class": list(allocation_pct.keys()), "Pct": list(allocation_pct.values())})
            fig_pie = px.pie(
                df_pie,
                names="Class",
                values="Pct",
                hole=0.7,
                color_discrete_sequence=[C_ACCENT, "#f6ad55", C_GAIN, C_ACCENT2],
            )
            fig_pie.update_traces(textinfo="none", hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>")
            fig_pie.update_layout(height=170, showlegend=False, **PLOT_BASE)
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

        colors = {"Equity Funds": C_ACCENT, "Debt Funds": "#f6ad55", "Gold Funds": C_GAIN, "International": C_ACCENT2}
        for asset_class, pct in allocation_pct.items():
            value = allocation_values.get(asset_class, 0.0)
            color = colors.get(asset_class, C_ACCENT2)
            st.markdown(
                f"""
                <div class="alloc-row">
                  <div style="display:flex;align-items:center;flex:1;">
                    <span class="alloc-dot" style="background:{color};box-shadow:0 0 5px {color}55;"></span>
                    <span style="font-size:13px;font-weight:500;color:#e2e8f0;">{asset_class}</span>
                  </div>
                  <div style="text-align:right;min-width:110px;">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:600;color:#f7fafc;">₹{value:,.0f}</div>
                    <div style="font-size:11px;color:#4a5568;">{pct:.1f}%</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="card-title">Performance Breakdown</div>', unsafe_allow_html=True)
        profitable = sum(1 for item in data["holdings"] if item["pnl"] >= 0)
        losing = sum(1 for item in data["holdings"] if item["pnl"] < 0)
        fig_perf = go.Figure(go.Pie(
            labels=["Profitable", "In Loss"],
            values=[profitable, losing],
            hole=0.65,
            marker_colors=[C_GAIN, C_LOSS],
            textinfo="none",
        ))
        fig_perf.update_layout(
            height=120,
            showlegend=True,
            legend=dict(font=dict(size=11, color="#718096"), bgcolor="rgba(0,0,0,0)", orientation="h", x=0.5, xanchor="center", y=-0.2),
            **PLOT_BASE,
        )
        st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="section-sep">Top Gainers</div>', unsafe_allow_html=True)
        top_gainers = sorted([item for item in data["holdings"] if item["pnl"] > 0], key=lambda x: x["pnl"], reverse=True)[:3]
        if top_gainers:
            st.dataframe(
                pd.DataFrame([
                    {
                        "Scheme": clean_name(item["scheme"]),
                        "P&L": fmt_inr(item["pnl"]),
                        "XIRR": f"{item['xirr']:.1f}%",
                    }
                    for item in top_gainers
                ]),
                use_container_width=True,
                hide_index=True,
            )

    with r2:
        st.markdown('<div class="card-title">⏱ SIP Countdown</div>', unsafe_allow_html=True)
        sorted_sips = sorted(data["live_sips"], key=lambda x: x["next_iso"])
        if sorted_sips:
            ticker_html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px;">'
            for idx, sip in enumerate(sorted_sips[:4]):
                scheme_name = clean_name(sip["scheme"])
                target_iso = sip["next_iso"]
                dom_id = f"sip_{idx}"
                ticker_html += f"""
                    <div style="background:#111627;border:1px solid rgba(255,255,255,0.06);border-radius:8px;padding:10px 12px;">
                      <div style="font-size:11px;color:#718096;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:4px;" title=\"{scheme_name}\">{scheme_name[:26]}…</div>
                      <div id=\"{dom_id}\" style="font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:700;color:#63b3ed;">—</div>
                    </div>
                    <script>
                    (function(){{
                      var target = new Date("{target_iso}T00:00:00").getTime();
                      function tick(){{
                        var diff = target - Date.now();
                        var el = document.getElementById("{dom_id}");
                        if(!el) return;
                        if(isNaN(target) || diff <= 0){{ el.textContent = "DUE TODAY"; return; }}
                        var d = Math.floor(diff/86400000);
                        var h = Math.floor(diff%86400000/3600000);
                        var m = Math.floor(diff%3600000/60000);
                        el.textContent = d + "d " + h + "h " + m + "m";
                      }}
                      setInterval(tick, 30000);
                      tick();
                    }})();
                    </script>
                """
            ticker_html += "</div>"
            components.html(ticker_html, height=130, scrolling=False)

            sip_rows = [
                {
                    "Scheme": clean_name(sip["scheme"]),
                    "Amount": fmt_inr(sip["amount"]),
                    "Day": sip["day_label"],
                    "Next": sip["next_date"],
                }
                for sip in sorted_sips[:4]
            ]
            st.dataframe(pd.DataFrame(sip_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No live SIPs detected.")

    r3, r4 = st.columns(2)
    with r3:
        st.markdown('<div class="card-title">Capital Concentration</div>', unsafe_allow_html=True)
        top_holdings = sorted(data["holdings"], key=lambda x: x["value"], reverse=True)[:5]
        if top_holdings:
            total_value_for_bubble = display_wealth or 1.0
            df_concentration = pd.DataFrame([
                {
                    "Scheme": clean_name(item["scheme"]),
                    "Value": item["value"],
                    "Pct": item["value"] / total_value_for_bubble * 100,
                }
                for item in top_holdings
            ])
            fig_concentration = px.bar(
                df_concentration,
                x="Value",
                y="Scheme",
                orientation="h",
                color="Pct",
                color_continuous_scale=["#1a365d", C_ACCENT, "#bee3f8"],
            )
            fig_concentration.update_layout(
                height=180,
                xaxis=dict(visible=False),
                yaxis=dict(tickfont=dict(size=10, color="#718096"), title=""),
                coloraxis_showscale=False,
                **PLOT_BASE,
            )
            st.plotly_chart(fig_concentration, use_container_width=True, config={"displayModeBar": False})

    with r4:
        st.markdown('<div class="card-title">Recent Redemptions</div>', unsafe_allow_html=True)
        recent_redemptions = data.get("recent_redemptions", [])
        if recent_redemptions:
            df_redemptions = pd.DataFrame([
                {"Scheme": item["Scheme"], "Payout": item["Payout"]}
                for item in recent_redemptions[:4]
            ])
            fig_redemptions = px.bar(
                df_redemptions,
                x="Payout",
                y="Scheme",
                orientation="h",
                color_discrete_sequence=[C_LOSS],
            )
            fig_redemptions.update_layout(
                height=140,
                xaxis=dict(visible=False),
                yaxis=dict(tickfont=dict(size=10, color="#718096"), title=""),
                **PLOT_BASE,
            )
            st.plotly_chart(fig_redemptions, use_container_width=True, config={"displayModeBar": False})
            st.dataframe(
                pd.DataFrame([
                    {
                        "Date": item["Date"],
                        "Scheme": item["Scheme"],
                        "Payout": fmt_inr(item["Payout"]),
                    }
                    for item in recent_redemptions[:4]
                ]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No recent redemptions found.")


def render_my_portfolio(data):
    st.markdown('<div class="page-title">Portfolio Ledger</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Open holdings and fully redeemed positions</div>', unsafe_allow_html=True)

    for label, category, color in [
        ("Equity Funds", "Equity Funds", C_ACCENT),
        ("Debt Funds", "Debt Funds", "#f6ad55"),
    ]:
        group = [item for item in data["holdings"] if item["category"] == category]
        if not group:
            continue
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:8px;margin:22px 0 10px;">
              <div style="width:7px;height:7px;border-radius:50%;background:{color};box-shadow:0 0 5px {color};"></div>
              <span style="font-size:11px;font-weight:700;color:{color};text-transform:uppercase;letter-spacing:2px;">{label}</span>
              <div style="flex:1;height:1px;background:rgba(255,255,255,0.05);"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rows = []
        for item in sorted(group, key=lambda x: x["value"], reverse=True):
            scheme_name = item["scheme"]
            cas_value = item["value"]
            live_value = cas_value
            badge = ""
            show_nav = item.get("cas_nav", 0.0)
            show_date = item.get("cas_date", "—")
            try:
                show_date = to_date(show_date).strftime("%d %b %Y")
            except Exception:
                show_date = "—"
            if st.session_state.live_data and scheme_name in st.session_state.live_data:
                live_value = st.session_state.live_data[scheme_name]["live_value"]
                show_nav = st.session_state.live_data[scheme_name]["nav"]
                show_date = st.session_state.live_data[scheme_name]["date"]
                badge = " 🟢"

            current_pnl = live_value - item["invested"]
            rows.append({
                "Scheme": clean_name(scheme_name) + badge,
                "Invested": fmt_inr(item["invested"]),
                "CAS Value": fmt_inr(cas_value),
                "Live Value": fmt_inr(live_value) if badge else "—",
                "NAV": f"₹{show_nav:,.4f}" if show_nav else "—",
                "NAV Date": show_date,
                "Current P&L": (f"▲ {fmt_inr(current_pnl)}" if current_pnl >= 0 else f"▼ {fmt_inr(current_pnl)}"),
                "XIRR %": f"{item['xirr']:.2f}%",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-sep">Bubble Map — Invested vs XIRR</div>', unsafe_allow_html=True)
    df_bubble = pd.DataFrame([
        {
            "Scheme": clean_name(item["scheme"]),
            "Invested": item["invested"],
            "XIRR": item["xirr"],
            "Gain": max(item["pnl"], 0),
            "Type": item["category"],
        }
        for item in data["holdings"] if item["invested"] > 0
    ])
    if not df_bubble.empty:
        fig_bubble = px.scatter(
            df_bubble,
            x="Invested",
            y="XIRR",
            size="Gain",
            color="Type",
            hover_name="Scheme",
            color_discrete_map={"Equity Funds": C_ACCENT, "Debt Funds": "#f6ad55"},
        )
        fig_bubble.update_layout(
            height=340,
            xaxis=dict(showgrid=True, gridcolor=GRID, title="Invested (₹)", tickfont=dict(size=11, color="#718096")),
            yaxis=dict(showgrid=True, gridcolor=GRID, title="XIRR %", tickfont=dict(size=11, color="#718096")),
            legend=dict(font=dict(size=11, color="#718096"), bgcolor="rgba(0,0,0,0)"),
            **PLOT_BASE,
        )
        st.plotly_chart(fig_bubble, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-sep" style="margin-top:36px;">Fully Redeemed Positions</div>', unsafe_allow_html=True)
    if data.get("redeemed"):
        realized = data["realized_pnl"]
        color = gain_color(realized)
        st.markdown(
            f"""
            <div style="background:rgba({'72,187,120' if realized>=0 else '252,129,129'},0.05);border:1px solid rgba({'72,187,120' if realized>=0 else '252,129,129'},0.2);
                                border-radius:10px;padding:14px 18px;margin-bottom:14px;">
              <div style="font-size:10px;color:{color};text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:4px;">Total Realized P&L</div>
              <div style="font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:700;color:{color};">
                {gain_arrow(realized)} {fmt_inr(realized)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        redeemed_rows = [
            {
                "Scheme": clean_name(item["scheme"]),
                "Invested": fmt_inr(item["invested"]),
                "Redeemed": fmt_inr(item["redeemed"]),
                "P&L": (f"▲ {fmt_inr(item['profit'])}" if item["profit"] >= 0 else f"▼ {fmt_inr(item['profit'])}"),
            }
            for item in data["redeemed"]
        ]
        st.dataframe(pd.DataFrame(redeemed_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No fully redeemed positions found.")


def render_sip_center(data):
    st.markdown('<div class="page-title">SIP Center</div>', unsafe_allow_html=True)
    live_sips = data.get("live_sips", [])
    dead_sips = data.get("dead_sips", [])

    tab = st.segmented_control(
        "sip_tab",
        [f"🟢 Live ({len(live_sips)})", f"🔴 Inactive ({len(dead_sips)})"],
        default=f"🟢 Live ({len(live_sips)})",
        label_visibility="collapsed",
    )
    target_list = live_sips if "Live" in tab else dead_sips
    total_outflow = sum(item["amount"] for item in target_list)
    status_label = "LIVE" if "Live" in tab else "INACTIVE"

    st.markdown(
        f"""
        <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;
    padding:20px 24px;display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:16px;">
          <div>
            <div style="font-size:10px;color:var(--muted);text-transform:uppercase;
    letter-spacing:1.5px;margin-bottom:4px;">Total Monthly Outflow</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:30px;font-weight:700;
    color:#f7fafc;letter-spacing:-1px;">{fmt_inr(total_outflow)}</div>
          </div>
          <div style="font-size:12px;font-weight:700;color:{'#48bb78' if 'Live' in tab else '#fc8181'};">
            {len(target_list)} {status_label}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if target_list:
        rows = [
            {
                "Scheme": clean_name(item["scheme"]),
                "Amount": fmt_inr(item["amount"]),
                "Day": item["day_label"],
                "Last Date": item["last_date"],
                "Next Due": item["next_date"],
                "Status": item["status"],
            }
            for item in target_list
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No SIPs in this category.")

    all_sips = live_sips + dead_sips
    if all_sips:
        st.markdown('<div class="section-sep">Monthly Outflow by Scheme</div>', unsafe_allow_html=True)
        df_bar = pd.DataFrame([
            {"Scheme": clean_name(item["scheme"]), "Amount": item["amount"]}
            for item in all_sips
        ])
        fig_bar = px.bar(
            df_bar,
            x="Amount",
            y="Scheme",
            orientation="h",
            color="Amount",
            color_continuous_scale=["#1a365d", C_ACCENT, "#bee3f8"],
        )
        fig_bar.update_layout(
            height=max(200, len(all_sips) * 30),
            xaxis=dict(visible=False),
            yaxis=dict(tickfont=dict(size=11, color="#718096"), title=""),
            coloraxis_showscale=False,
            **PLOT_BASE,
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})


def render_transactions(data):
    st.markdown('<div class="page-title">Transaction Ledger</div>', unsafe_allow_html=True)
    tx_map = data.get("tx_map", {})
    agg_map = data.get("agg_map", {})

    if not tx_map:
        st.warning("No transaction data found.")
        return

    selected_scheme = st.selectbox("Select Scheme", list(tx_map.keys()), label_visibility="visible")
    totals = agg_map.get(selected_scheme, {"cost": 0.0, "units": 0.0, "value": 0.0})
    c1, c2, c3 = st.columns(3)
    c1.metric("Book Cost", fmt_inr(totals["cost"]))
    c2.metric("Units", f"{totals['units']:.3f}")
    c3.metric("Current Value", fmt_inr(totals["value"]))

    rows = []
    for transaction in tx_map.get(selected_scheme, []):
        rows.append({
            "Date": to_date(transaction.get("date")).strftime("%d %b %Y") if transaction.get("date") else "—",
            "Description": transaction.get("description", "—"),
            "Amount": fmt_inr(float(transaction["amount"])) if transaction.get("amount") else "—",
            "NAV": f"₹{float(transaction['nav']):,.4f}" if transaction.get("nav") else "—",
            "Units": f"{float(transaction['units']):,.3f}" if transaction.get("units") else "—",
            "Type": transaction.get("type", "—"),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-sep" style="margin-top:28px;">All Holdings — XIRR Table</div>', unsafe_allow_html=True)
    performance = [
        {
            "Scheme": clean_name(item["scheme"]),
            "Invested": fmt_inr(item["invested"]),
            "Value": fmt_inr(item["value"]),
            "P&L": (f"▲ {fmt_inr(item['pnl'])}" if item["pnl"] >= 0 else f"▼ {fmt_inr(item['pnl'])}"),
            "XIRR %": f"{item['xirr']:.2f}%",
            "Category": item["category"],
        }
        for item in data["holdings"]
    ]
    st.dataframe(pd.DataFrame(performance), use_container_width=True, hide_index=True)


def render_alerts(data):
    st.markdown('<div class="page-title">Alerts & Insights</div>', unsafe_allow_html=True)

    alerts = []
    for duplicate in data.get("duplicate_alerts", []):
        alerts.append(("warn", "Duplicate SIP Detected", f"{clean_name(duplicate['scheme'])} — {duplicate['count']}× entries on {duplicate['dates']}"))
    for sip in data.get("dead_sips", []):
        alerts.append(("danger", "Inactive SIP", f"{clean_name(sip['scheme'])} — last processed {sip['last_date']}"))
    for holding in [item for item in data["holdings"] if item["pnl"] < 0]:
        alerts.append(("info", "Unrealized Loss", f"{clean_name(holding['scheme'])} — down {fmt_inr(holding['pnl'])} from cost"))

    if not alerts:
        st.markdown(
            """
            <div style="text-align:center;padding:60px 20px;">
              <div style="font-size:48px;margin-bottom:12px;">◎</div>
              <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#f7fafc;margin-bottom:6px;">All Clear</div>
              <div style="font-size:13px;color:#718096;">No alerts detected in your portfolio.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    colors = {"warn": "#f6ad55", "danger": "#fc8181", "info": "#63b3ed"}
    labels = {"warn": "WARNING", "danger": "ACTION REQUIRED", "info": "INFO"}
    for level, title, detail in alerts:
        color = colors.get(level, C_ACCENT)
        label = labels.get(level, "INFO")
        st.markdown(
            f"""
            <div class="alert-card" style="border-color:{color};">
              <div style="font-size:9px;font-weight:700;color:{color};text-transform:uppercase;
                          letter-spacing:1.5px;font-family:'IBM Plex Mono',monospace;margin-bottom:4px;">{label}</div>
              <div style="font-size:14px;font-weight:600;color:#f7fafc;margin-bottom:3px;">{title}</div>
              <div style="font-size:13px;color:#718096;">{detail}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def run_app():
    initialize_session_state()
    active = active_data()
    menu = build_sidebar(active)
    if not active:
        show_upload()
        st.stop()
    if menu == "Dashboard":
        render_dashboard(active)
    elif menu == "My Portfolio":
        render_my_portfolio(active)
    elif menu == "SIP Center":
        render_sip_center(active)
    elif menu == "Transactions":
        render_transactions(active)
    elif menu == "Alerts":
        render_alerts(active)
