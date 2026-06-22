# pages/08_Reconciliation.py  —  SipCheck Reconciliation (Admin Only)
import streamlit as st
import datetime
import time

from dashboard import (
    classify_transaction, account_transactions, calc_xirr,
    fmt_inr, clean_name, to_date, TX_META,
)
from ui_theme import inject_theme, page_header, section, glass_kpi
from sidebar_v2 import render_sidebar
from theme import apply_theme, theme_toggle_button

st.set_page_config(page_title="Reconciliation — SipCheck", page_icon="🔒", layout="wide")
render_sidebar()
inject_theme()
apply_theme()

# ── Constants ─────────────────────────────────────────────────────────────
RECON_PWD    = "2002"
MAX_WRONG    = 3
LOCKOUT_SECS = 60

TX_FILTER_LABELS = [
    "All", "SIP", "Lumpsum Purchase", "Redemption",
    "Switch In", "Switch Out", "SWP", "STP In", "STP Out",
    "Reversal", "Dividend", "Transfer In/Out",
]

# ── Extra page styling ────────────────────────────────────────────────────
st.markdown("""
<style>
.recon-warn {
    background:rgba(245,158,11,0.07);
    border:1px solid rgba(245,158,11,0.22);
    border-left:4px solid #f59e0b;
    border-radius:12px;
    padding:.65rem 1rem;
    margin-bottom:.9rem;
    font-size:.8rem;
    color:#d97706;
}
.tx-row {
    display:grid;
    grid-template-columns:30px 190px 100px 120px 100px 140px 50px;
    gap:6px;
    align-items:center;
    padding:5px 6px;
    border-radius:8px;
    font-size:.76rem;
    border-bottom:1px solid rgba(139,92,246,.07);
}
.tx-row:hover { background:rgba(139,92,246,.05); }
.tx-hdr { font-size:.64rem; font-weight:700; color:#6b7280;
           text-transform:uppercase; letter-spacing:.1em; }
.lock-box {
    min-height:60vh; display:flex; align-items:center; justify-content:center;
}
.lock-card {
    text-align:center; max-width:380px; width:100%;
    padding:2.5rem 2rem;
    background:rgba(17,17,48,.65);
    border:1px solid rgba(139,92,246,.22);
    border-radius:20px;
    backdrop-filter:blur(16px);
}
.qchip {
    display:inline-block; padding:2px 10px; border-radius:20px;
    font-size:.65rem; font-weight:700;
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────
def _init():
    defs: dict = {
        "recon_auth":         False,
        "recon_wrong":        0,
        "recon_locked_until": 0.0,
        "recon_deleted_txs":  {},   # {scheme: [tx_dict, ...]}
        "recon_unmapped":     set(),
        "recon_unmapped_rsn": {},   # {scheme: reason}
        "recon_ceased":       {},   # {sip_key: {...}}
        "recon_log":          [],
        "recon_queries":      [],
        "recon_qnum":         0,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────
def _log(heading: str, detail: str, category: str = "action"):
    st.session_state.recon_log.insert(0, {
        "ts":       datetime.datetime.now().strftime("%d %b %Y · %H:%M:%S"),
        "heading":  heading,
        "detail":   detail,
        "category": category,
    })


def _active_data():
    active = st.session_state.get("active")
    profiles = st.session_state.get("profiles", {})
    return profiles.get(active) if active else None


def _recalc(data: dict):
    """Recompute invested / pnl / xirr for every holding and update totals."""
    total_inv = 0.0
    for h in data.get("holdings", []):
        txs  = data["tx_map"].get(h["scheme"], [])
        acct = account_transactions(txs)
        h["invested"]         = acct["invested"]
        h["sip_invested"]     = acct["sip_invested"]
        h["lumpsum_invested"] = acct["lumpsum_invested"]
        h["pnl"]              = h["value"] - acct["invested"]
        h["xirr"]             = calc_xirr(txs, h["value"], data["statement_date"])
        total_inv += acct["invested"]
    data["total_invested"]         = total_inv
    data["total_sip_invested"]     = sum(h.get("sip_invested", 0) for h in data.get("holdings", []))
    data["total_lumpsum_invested"] = sum(h.get("lumpsum_invested", 0) for h in data.get("holdings", []))
    data["unrealized_pnl"]         = data.get("total_value", 0) - total_inv


def _matches_filter(cls: str, filt: str) -> bool:
    if filt == "All":
        return True
    if filt == "Reversal":
        return "Reversal" in cls
    if filt == "Dividend":
        return cls == "Dividend Payout"
    if filt == "Transfer In/Out":
        return "Transfer" in cls or "Transmission" in cls
    return cls == filt


def _sip_key(s: dict) -> str:
    return f"{s.get('scheme','')[:50]}|{s.get('amount',0)}"


def _fmt_pnl(v: float) -> str:
    sign = "+" if v >= 0 else "-"
    return f"{sign}₹{abs(v):,.2f}"


def _changes_today() -> int:
    today = datetime.datetime.now().strftime("%d %b %Y")
    return sum(1 for e in st.session_state.recon_log if today in e.get("ts", ""))


# ── Lock Screen ───────────────────────────────────────────────────────────
def render_lock_screen():
    locked_until = st.session_state.recon_locked_until
    remaining    = max(0, int(locked_until - time.time()))

    st.markdown('<div class="lock-box"><div class="lock-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:3.5rem;margin-bottom:.8rem;">🔒</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.4rem;font-weight:700;
                color:#f0f0ff;margin-bottom:.35rem;">Admin Access</div>
    <div style="font-size:.82rem;color:#6b7280;margin-bottom:1.4rem;">
        Reconciliation module requires admin password.
    </div>
    """, unsafe_allow_html=True)

    if remaining > 0:
        st.error(f"🔐 Too many wrong attempts. Locked for {remaining}s.")
        if st.button("↻ Refresh", use_container_width=True):
            st.rerun()
    else:
        pwd = st.text_input("Admin Password", type="password",
                            placeholder="Enter password",
                            label_visibility="collapsed",
                            key="recon_pwd_input")
        if st.button("Unlock  →", use_container_width=True, type="primary", key="recon_unlock_btn"):
            if pwd == RECON_PWD:
                st.session_state.recon_auth  = True
                st.session_state.recon_wrong = 0
                _log("🔓 Admin Logged In", "Admin authenticated successfully.")
                st.rerun()
            else:
                st.session_state.recon_wrong += 1
                wrong = st.session_state.recon_wrong
                if wrong >= MAX_WRONG:
                    st.session_state.recon_locked_until = time.time() + LOCKOUT_SECS
                    st.error(f"🔐 Locked for {LOCKOUT_SECS}s after {MAX_WRONG} failed attempts.")
                else:
                    st.error(f"Wrong password — {MAX_WRONG - wrong} attempt(s) remaining.")
                st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)


# ── Admin Header / Stats ──────────────────────────────────────────────────
def render_admin_header():
    st.markdown("""
    <div class="recon-warn">
    ⚠️ <b>Session-based changes</b> — All modifications live in session memory only.
    Export your Activity Log or note changes before closing this window.
    </div>""", unsafe_allow_html=True)

    changes   = _changes_today()
    pending_q = sum(1 for q in st.session_state.recon_queries if q["status"] in ("Open", "In Progress"))
    del_total = sum(len(v) for v in st.session_state.recon_deleted_txs.values())
    unmapped  = len(st.session_state.recon_unmapped)

    k1, k2, k3, k4, kcol = st.columns([1, 1, 1, 1, 0.8])
    with k1: glass_kpi("Changes Today",    str(changes))
    with k2: glass_kpi("Pending Queries",  str(pending_q))
    with k3: glass_kpi("Deleted Txns",     str(del_total))
    with k4: glass_kpi("Unmapped Schemes", str(unmapped))
    with kcol:
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        if st.button("🔒 Lock", key="recon_logout", use_container_width=True):
            st.session_state.recon_auth = False
            _log("🔒 Admin Locked", "Admin session ended.")
            st.rerun()


# ── Global Search ─────────────────────────────────────────────────────────
def render_global_search(data: dict):
    q = st.text_input("", placeholder="🔍  Search folios, schemes, transactions, queries…",
                      key="recon_global_q", label_visibility="collapsed")
    if not q or len(q.strip()) < 2:
        return
    q = q.strip().lower()
    results: list[str] = []

    for scheme in data.get("tx_map", {}):
        if q in scheme.lower():
            results.append(f"📁 Scheme: {clean_name(scheme)}")

    for scheme, folio in data.get("scheme_folio", {}).items():
        if q in folio.lower():
            results.append(f"🔢 Folio {folio} → {clean_name(scheme)}")

    for scheme, txs in data.get("tx_map", {}).items():
        for tx in txs:
            desc = str(tx.get("description", "")).lower()
            if q in desc:
                results.append(f"💳 Txn match in {clean_name(scheme)}: {desc[:55]}…")
                break  # one match per scheme to keep results concise

    for qi in st.session_state.recon_queries:
        if q in qi.get("subject", "").lower() or q in qi.get("desc", "").lower():
            results.append(f"🎫 Query {qi['ticket']}: {qi['subject']}")

    if results:
        with st.expander(f"**{len(results)} result(s) for '{q}'**", expanded=True):
            for r in results[:25]:
                st.markdown(
                    f"<div style='padding:5px 12px;font-size:.8rem;color:#d4d4d4;"
                    f"border-left:2px solid #8b5cf6;margin-bottom:4px;'>{r}</div>",
                    unsafe_allow_html=True,
                )
    else:
        st.caption(f"No results for '{q}'.")


# ── Tab 1: Folio Reconciliation ───────────────────────────────────────────
def render_folio_recon(data: dict):
    scheme_folio = data.get("scheme_folio", {})
    amc_schemes  = data.get("amc_schemes",  {})
    tx_map       = data.get("tx_map", {})
    deleted      = st.session_state.recon_deleted_txs

    section("FOLIO RECONCILIATION")

    mode = st.radio(
        "mode", ["🔢 Search by Folio Number", "🏢 Search by AMC"],
        horizontal=True, key="recon_folio_mode", label_visibility="collapsed",
    )

    if mode == "🔢 Search by Folio Number":
        folio_q = st.text_input("", placeholder="Folio number e.g. 1234567/89",
                                key="recon_folio_q", label_visibility="collapsed").strip()
        if folio_q:
            schemes_to_show = [s for s, f in scheme_folio.items() if folio_q.lower() in f.lower()]
        else:
            schemes_to_show = sorted(tx_map.keys())
    else:
        all_amcs = sorted(a for a in amc_schemes if a and a != "Unknown")
        amc_sel  = st.selectbox("AMC", ["(All AMCs)"] + all_amcs, key="recon_amc_sel",
                                label_visibility="collapsed")
        schemes_to_show = list(tx_map.keys()) if amc_sel == "(All AMCs)" \
            else amc_schemes.get(amc_sel, [])

    # ── Deleted-transactions restore section ──────────────────────────
    del_total = sum(len(v) for v in deleted.values())
    if del_total:
        with st.expander(f"♻️ Deleted Transactions ({del_total}) — click to restore", expanded=False):
            for scheme, del_txs in list(deleted.items()):
                if not del_txs:
                    continue
                st.markdown(f"**{clean_name(scheme)}**")
                for i, tx in enumerate(del_txs):
                    cls  = tx.get("_cls", "—")
                    meta = TX_META.get(cls, {"icon": "○", "color": "#718096"})
                    rc1, rc2, rc3, rc4, rc5 = st.columns([2.2, 1.5, 1.8, 1.5, 0.7])
                    with rc1:
                        st.markdown(
                            f"<span style='color:{meta['color']};font-size:.78rem;'>"
                            f"{meta['icon']} {cls}</span>",
                            unsafe_allow_html=True,
                        )
                    with rc2: st.caption(str(tx.get("date", "—")))
                    with rc3: st.caption(fmt_inr(abs(float(tx.get("amount") or 0))))
                    with rc4: st.caption(f"{float(tx.get('units') or 0):+.4f} u")
                    with rc5:
                        if st.button("♻️", key=f"rst_{scheme[:15]}_{i}", help="Restore"):
                            txlist = data["tx_map"].setdefault(scheme, [])
                            txlist.append(tx)
                            data["tx_map"][scheme] = sorted(
                                txlist, key=lambda x: to_date(x.get("date")),
                            )
                            st.session_state.recon_deleted_txs[scheme].pop(i)
                            if not st.session_state.recon_deleted_txs[scheme]:
                                del st.session_state.recon_deleted_txs[scheme]
                            _recalc(data)
                            _log(f"♻️ Restored transaction",
                                 f"Scheme: {clean_name(scheme)} | {cls} | {tx.get('date','')}", "restore")
                            st.rerun()

    if not schemes_to_show:
        st.info("No schemes match. Try a different folio/AMC.")
        return

    # ── Scheme cards ──────────────────────────────────────────────────
    for scheme in schemes_to_show:
        txs       = tx_map.get(scheme, [])
        agg       = data.get("agg_map", {}).get(scheme, {})
        h_rec     = next((h for h in data.get("holdings", []) if h["scheme"] == scheme), None)
        folio_num = scheme_folio.get(scheme, "—")
        amc_name  = next((a for a, ss in amc_schemes.items() if scheme in ss), "—")

        invested  = h_rec["invested"] if h_rec else 0.0
        value     = float(agg.get("value", 0))
        units     = float(agg.get("units", 0))
        pnl       = h_rec["pnl"] if h_rec else 0.0
        xirr_val  = h_rec["xirr"] if h_rec else 0.0
        category  = h_rec["category"] if h_rec else "—"

        with st.expander(
            f"📁  {clean_name(scheme)}   ·   Folio: {folio_num}   ·   {len(txs)} txns",
            expanded=False,
        ):
            # Scheme info row
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                st.markdown(f"<div class='kpi-label'>AMC</div>"
                            f"<div style='font-size:.85rem;font-weight:600;color:#f0f0ff;'>{amc_name}</div>",
                            unsafe_allow_html=True)
            with ic2:
                st.markdown(f"<div class='kpi-label'>Category</div>"
                            f"<div style='font-size:.85rem;font-weight:600;color:#f0f0ff;'>{category}</div>",
                            unsafe_allow_html=True)
            with ic3:
                st.markdown(f"<div class='kpi-label'>Balance Units</div>"
                            f"<div style='font-family:JetBrains Mono,monospace;font-size:.85rem;"
                            f"font-weight:600;color:#f0f0ff;'>{units:.4f}</div>",
                            unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # KPI row
            k1, k2, k3, k4, k5 = st.columns(5)
            with k1: glass_kpi("Invested",     fmt_inr(invested))
            with k2: glass_kpi("Current Value", fmt_inr(value))
            with k3: glass_kpi("P&L", _fmt_pnl(pnl), tone="up" if pnl >= 0 else "down")
            with k4: glass_kpi("XIRR", f"{xirr_val:.1f}%", tone="up" if xirr_val >= 0 else "down")
            with k5: glass_kpi("Txn Count", str(len(txs)))

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            st.markdown("**Transactions**")

            # Filter pills
            filt_k = f"filt_{scheme[:18]}"
            filt = st.radio("filter", TX_FILTER_LABELS, horizontal=True,
                            key=filt_k, label_visibility="collapsed")

            # Column headers
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            hc = st.columns([0.4, 2.4, 1.5, 1.8, 1.4, 1.8, 0.7])
            for col, lbl in zip(hc, ["✓", "Type", "Date", "Amount", "NAV", "Units / Bal", "Del"]):
                with col:
                    st.markdown(f"<div class='tx-hdr'>{lbl}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='border:none;border-top:1px solid rgba(139,92,246,.12);margin:3px 0 5px;'>",
                        unsafe_allow_html=True)

            bulk_sel: list[int] = []
            sel_all_k = f"selall_{scheme[:18]}"
            select_all = st.checkbox("Select all", key=sel_all_k, value=False)

            found_any = False
            for idx, tx in enumerate(txs):
                cls = tx.get("_cls") or classify_transaction(tx)
                if not _matches_filter(cls, filt):
                    continue
                found_any = True
                meta = TX_META.get(cls, {"icon": "○", "color": "#718096"})
                row_k = f"{scheme[:14]}_{idx}"

                r0, r1, r2, r3, r4, r5, r6 = st.columns([0.4, 2.4, 1.5, 1.8, 1.4, 1.8, 0.7])
                with r0:
                    chk = st.checkbox("", value=select_all,
                                      key=f"chk_{row_k}", label_visibility="collapsed")
                    if chk:
                        bulk_sel.append(idx)
                with r1:
                    st.markdown(
                        f"<span style='color:{meta['color']};font-size:.77rem;'>"
                        f"{meta['icon']} {cls}</span>",
                        unsafe_allow_html=True,
                    )
                with r2:
                    st.caption(str(tx.get("date", "—")))
                with r3:
                    amt = abs(float(tx.get("amount") or 0))
                    st.markdown(
                        f"<span style='font-family:JetBrains Mono,monospace;font-size:.75rem;"
                        f"color:#f0f0ff;'>{fmt_inr(amt)}</span>",
                        unsafe_allow_html=True,
                    )
                with r4:
                    nav = float(tx.get("nav") or 0)
                    st.caption(f"₹{nav:.4f}" if nav else "—")
                with r5:
                    u_tx = float(tx.get("units")   or 0)
                    bal  = float(tx.get("balance")  or 0)
                    st.caption(f"{u_tx:+.4f}  /  {bal:.4f}")
                with r6:
                    ck = f"cdel_{row_k}"
                    if not st.session_state.get(ck):
                        if st.button("❌", key=f"del_{row_k}", help="Delete"):
                            st.session_state[ck] = True
                            st.rerun()
                    else:
                        st.caption("Sure?")

                # Confirmation below this row
                if st.session_state.get(f"cdel_{row_k}"):
                    wa, wb, wc = st.columns([3, 1, 1])
                    with wa:
                        st.warning("Delete this transaction? All calculations will update.")
                    with wb:
                        if st.button("✅ Yes", key=f"dy_{row_k}"):
                            popped = data["tx_map"][scheme].pop(idx)
                            st.session_state.recon_deleted_txs.setdefault(scheme, []).append(popped)
                            _recalc(data)
                            _log(
                                f"❌ Deleted transaction",
                                f"{clean_name(scheme)} | {cls} | {tx.get('date','')} | "
                                f"{fmt_inr(abs(float(tx.get('amount') or 0)))}",
                                "deletion",
                            )
                            st.session_state.pop(f"cdel_{row_k}", None)
                            st.rerun()
                    with wc:
                        if st.button("Cancel", key=f"dn_{row_k}"):
                            st.session_state.pop(f"cdel_{row_k}", None)
                            st.rerun()

            if not found_any:
                st.caption("No transactions match this filter.")
                continue

            # Bulk delete
            if bulk_sel:
                bk = f"bk_{scheme[:14]}"
                if st.button(f"🗑️ Delete {len(bulk_sel)} selected", key=f"bdel_{scheme[:14]}"):
                    st.session_state[bk] = True
                if st.session_state.get(bk):
                    st.warning(f"Delete {len(bulk_sel)} transactions? This affects all calculations.")
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.button("✅ Confirm Delete All", key=f"bdy_{scheme[:14]}"):
                            to_delete = sorted(set(bulk_sel), reverse=True)
                            for di in to_delete:
                                if di < len(data["tx_map"].get(scheme, [])):
                                    popped = data["tx_map"][scheme].pop(di)
                                    st.session_state.recon_deleted_txs.setdefault(scheme, []).append(popped)
                            _recalc(data)
                            _log(f"🗑️ Bulk deleted {len(to_delete)} txns",
                                 f"Scheme: {clean_name(scheme)}", "deletion")
                            st.session_state.pop(bk, None)
                            st.rerun()
                    with bc2:
                        if st.button("Cancel", key=f"bdn_{scheme[:14]}"):
                            st.session_state.pop(bk, None)
                            st.rerun()


# ── Tab 2: Scheme Reconciliation ──────────────────────────────────────────
def render_scheme_recon(data: dict):
    holdings       = data.get("holdings", [])
    redeemed_list  = data.get("redeemed", [])
    unmapped       = st.session_state.recon_unmapped
    reasons        = st.session_state.recon_unmapped_rsn
    scheme_folio   = data.get("scheme_folio", {})
    amc_schemes    = data.get("amc_schemes", {})

    section("SCHEME RECONCILIATION")

    all_schemes = [h["scheme"] for h in holdings] + [r["scheme"] for r in redeemed_list]
    mapped_h    = [h for h in holdings if h["scheme"] not in unmapped]
    unmapped_h  = [h for h in holdings if h["scheme"] in unmapped]
    mapped_red  = [r for r in redeemed_list if r["scheme"] not in unmapped]

    mapped_val   = sum(h["value"] for h in mapped_h)
    unmapped_val = sum(h["value"] for h in unmapped_h)

    k1, k2, k3, k4 = st.columns(4)
    with k1: glass_kpi("Total Mapped",   str(len(mapped_h) + len(mapped_red)))
    with k2: glass_kpi("Total Unmapped", str(len(unmapped_h)))
    with k3: glass_kpi("Mapped Value",   fmt_inr(mapped_val))
    with k4: glass_kpi("Unmapped Value", fmt_inr(unmapped_val))

    section("MAPPED SCHEMES")

    all_mapped = [(h["scheme"], "active") for h in mapped_h] + \
                 [(r["scheme"], "redeemed") for r in mapped_red]

    if not all_mapped:
        st.info("No mapped schemes.")
    else:
        for scheme, kind in all_mapped:
            folio_num = scheme_folio.get(scheme, "—")
            amc_name  = next((a for a, ss in amc_schemes.items() if scheme in ss), "—")

            if kind == "active":
                h_rec  = next(h for h in mapped_h if h["scheme"] == scheme)
                status = "🟢 Active" if float(data.get("agg_map", {}).get(scheme, {}).get("units", 0)) > 0.001 else "⚫ Closed"
                pnl_v  = h_rec["pnl"]
                with st.expander(f"✅ {clean_name(scheme)}  ·  {status}  ·  {folio_num}"):
                    r1, r2, r3, r4 = st.columns(4)
                    with r1: glass_kpi("Invested", fmt_inr(h_rec["invested"]))
                    with r2: glass_kpi("Value",    fmt_inr(h_rec["value"]))
                    with r3: glass_kpi("P&L",      _fmt_pnl(pnl_v), tone="up" if pnl_v >= 0 else "down")
                    with r4: glass_kpi("XIRR",     f"{h_rec['xirr']:.1f}%",
                                       tone="up" if h_rec["xirr"] >= 0 else "down")

                    st.caption(f"AMC: {amc_name}  ·  Category: {h_rec.get('category','—')}")
                    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                    _render_unmap_button(scheme, data)
            else:
                r_rec = next(r for r in mapped_red if r["scheme"] == scheme)
                with st.expander(f"✅ {clean_name(scheme)}  ·  🔴 Fully Redeemed  ·  {folio_num}"):
                    r1, r2, r3 = st.columns(3)
                    with r1: glass_kpi("Invested",  fmt_inr(r_rec["invested"]))
                    with r2: glass_kpi("Redeemed",  fmt_inr(r_rec["redeemed"]))
                    with r3: glass_kpi("Realized P&L", _fmt_pnl(r_rec["profit"]),
                                       tone="up" if r_rec["profit"] >= 0 else "down")
                    _render_unmap_button(scheme, data)

    section("UNMAPPED SCHEMES")

    if not unmapped_h:
        st.caption("No unmapped schemes.")
    else:
        for h_rec in unmapped_h:
            scheme = h_rec["scheme"]
            rsn    = reasons.get(scheme, "—")
            with st.expander(f"❌ {clean_name(scheme)}  ·  Reason: {rsn}"):
                r1, r2, r3 = st.columns(3)
                with r1: glass_kpi("Invested", fmt_inr(h_rec["invested"]))
                with r2: glass_kpi("Value",    fmt_inr(h_rec["value"]))
                with r3: glass_kpi("P&L",      _fmt_pnl(h_rec["pnl"]),
                                   tone="up" if h_rec["pnl"] >= 0 else "down")
                st.caption(f"Unmapped reason: {rsn}")
                if st.button("✅ Remap to Portfolio", key=f"remap_{scheme[:20]}"):
                    st.session_state.recon_unmapped.discard(scheme)
                    st.session_state.recon_unmapped_rsn.pop(scheme, None)
                    _log(f"✅ Scheme Remapped", f"{clean_name(scheme)}", "mapping")
                    st.rerun()


def _render_unmap_button(scheme: str, data: dict):
    uk = f"uck_{scheme[:20]}"
    if not st.session_state.get(uk):
        if st.button("🚫 Unmap from Portfolio", key=f"unmap_{scheme[:20]}"):
            st.session_state[uk] = True
            st.rerun()
    else:
        rsn = st.text_input("Reason for unmapping:", key=f"ursn_{scheme[:20]}")
        uc1, uc2 = st.columns(2)
        with uc1:
            if st.button("✅ Confirm Unmap", key=f"uyes_{scheme[:20]}"):
                st.session_state.recon_unmapped.add(scheme)
                st.session_state.recon_unmapped_rsn[scheme] = rsn or "No reason provided"
                _log(f"🚫 Scheme Unmapped", f"{clean_name(scheme)} — {rsn}", "mapping")
                st.session_state.pop(uk)
                st.rerun()
        with uc2:
            if st.button("Cancel", key=f"uno_{scheme[:20]}"):
                st.session_state.pop(uk)
                st.rerun()


# ── Tab 3: SIP Reconciliation ─────────────────────────────────────────────
def render_sip_recon(data: dict):
    live_sips = data.get("live_sips", [])
    dead_sips = data.get("dead_sips", [])
    ceased    = st.session_state.recon_ceased

    section("SIP RECONCILIATION")

    active_sips    = [s for s in live_sips if _sip_key(s) not in ceased]
    monthly_active = sum(s["amount"] for s in active_sips)
    monthly_ceased = sum(info.get("amount", 0) for info in ceased.values())

    k1, k2, k3, k4 = st.columns(4)
    with k1: glass_kpi("Active SIPs",    str(len(active_sips)))
    with k2: glass_kpi("Ceased SIPs",    str(len(ceased)))
    with k3: glass_kpi("Monthly Active", fmt_inr(monthly_active))
    with k4: glass_kpi("Monthly Ceased", fmt_inr(monthly_ceased))

    view = st.radio("sip_view", ["🟢 Active SIPs", "🔴 Ceased SIPs"],
                    horizontal=True, key="recon_sip_view", label_visibility="collapsed")

    if view == "🟢 Active SIPs":
        section("ACTIVE SIPs")
        if not active_sips:
            st.info("No active SIPs in portfolio.")
        for s in active_sips:
            sk = _sip_key(s)
            with st.expander(
                f"🟢 {clean_name(s['scheme'])}  ·  {fmt_inr(s['amount'])}/month",
            ):
                c1, c2, c3, c4 = st.columns(4)
                with c1: glass_kpi("Amount",    fmt_inr(s["amount"]))
                with c2: glass_kpi("Debit Day", s.get("day_label", "—"))
                with c3: glass_kpi("Last Debit", s.get("last_date", "—"))
                with c4: glass_kpi("Next Due",   s.get("next_date", "—"))
                st.caption(f"Instalments: {s.get('installments', '—')}")

                ck = f"csk_{sk[:22]}"
                if not st.session_state.get(ck):
                    if st.button("⏸ Cease SIP", key=f"cease_{sk[:22]}"):
                        st.session_state[ck] = True
                        st.rerun()
                else:
                    st.warning(
                        f"Ceasing this SIP will remove {fmt_inr(s['amount'])}/month "
                        f"from calculations. Continue?"
                    )
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button("✅ Yes, Cease", key=f"cy_{sk[:22]}"):
                            ceased[sk] = {
                                "scheme":    s["scheme"],
                                "amount":    s["amount"],
                                "ceased_dt": datetime.datetime.now().strftime("%d %b %Y"),
                                "ceased_by": "Admin",
                                "original":  s,
                            }
                            data["live_sips"] = [x for x in data["live_sips"]
                                                 if _sip_key(x) != sk]
                            _log(f"⏸ SIP Ceased",
                                 f"{clean_name(s['scheme'])} | {fmt_inr(s['amount'])}/month", "sip")
                            st.session_state.pop(ck)
                            st.rerun()
                    with cc2:
                        if st.button("Cancel", key=f"cn_{sk[:22]}"):
                            st.session_state.pop(ck)
                            st.rerun()

    else:  # Ceased
        section("CEASED SIPs (Admin-ceased)")
        if not ceased:
            st.caption("No SIPs have been ceased in this session.")

        for sk, info in list(ceased.items()):
            with st.expander(
                f"🔴 {clean_name(info['scheme'])}  ·  {fmt_inr(info['amount'])}/month"
            ):
                c1, c2, c3 = st.columns(3)
                with c1: glass_kpi("Amount",    fmt_inr(info["amount"]))
                with c2: glass_kpi("Ceased",    info["ceased_dt"])
                with c3: glass_kpi("By",        info["ceased_by"])
                if st.button("▶️ Reactivate SIP", key=f"react_{sk[:22]}"):
                    orig = info.get("original")
                    if orig:
                        data["live_sips"].append(orig)
                    del ceased[sk]
                    _log(f"▶️ SIP Reactivated", f"{clean_name(info['scheme'])}", "sip")
                    st.rerun()

        if dead_sips:
            section("NATURALLY INACTIVE SIPs (from CAS)")
            for s in dead_sips:
                if _sip_key(s) in ceased:
                    continue
                st.markdown(
                    f"<div style='padding:8px 12px;border-radius:8px;"
                    f"background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.14);"
                    f"margin-bottom:6px;font-size:.8rem;color:#8b93a7;'>"
                    f"🔴 <b style='color:#f0f0ff;'>{clean_name(s['scheme'])}</b> "
                    f"· {fmt_inr(s['amount'])}/month "
                    f"· Last: {s.get('last_date','—')}</div>",
                    unsafe_allow_html=True,
                )


# ── Tab 4: Activity Log ───────────────────────────────────────────────────
def render_activity_log():
    section("ACTIVITY LOG")

    log = st.session_state.recon_log
    if not log:
        st.info("No activity yet. Actions taken in Reconciliation will appear here.")
        return

    st.markdown(
        "<div class='recon-warn' style='margin-bottom:.5rem;'>"
        "⚠️ Log is session-based and clears on page refresh.</div>",
        unsafe_allow_html=True,
    )

    CATS = ["All", "deletion", "restore", "mapping", "sip", "action"]
    ICONS = {"deletion":"🗑️","restore":"♻️","mapping":"🗺️","sip":"⏸","action":"📋"}

    cat_filt = st.radio("Log filter", CATS, horizontal=True,
                        key="log_cat_filt", label_visibility="collapsed")
    filtered = log if cat_filt == "All" else [e for e in log if e.get("category") == cat_filt]

    if not filtered:
        st.caption("No entries for this filter.")
        return

    log_text = "\n".join(
        f"[{e['ts']}] {e['heading']}\n  {e['detail']}" for e in filtered
    )
    st.download_button(
        "📋 Export Log as TXT", log_text,
        file_name="sipcheck_recon_log.txt", mime="text/plain", key="export_log_btn",
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    for entry in filtered:
        cat   = entry.get("category", "action")
        icon  = ICONS.get(cat, "📋")
        label = f"{icon}  {entry['heading']}"
        with st.expander(f"{label}   ·   {entry['ts']}", expanded=False):
            st.caption(entry["detail"])


# ── Tab 5: Client Queries (Admin View) ────────────────────────────────────
def render_queries_admin():
    section("CLIENT QUERIES — ADMIN VIEW")

    queries = st.session_state.recon_queries
    if not queries:
        st.info("No queries submitted yet.")
        return

    STATUS_COLORS = {"Open": "#fbbf24", "In Progress": "#3b82f6", "Resolved": "#34d399"}
    STATUS_ICONS  = {"Open": "🟡",      "In Progress": "🔵",      "Resolved": "🟢"}

    open_c = sum(1 for q in queries if q["status"] == "Open")
    ip_c   = sum(1 for q in queries if q["status"] == "In Progress")
    res_c  = sum(1 for q in queries if q["status"] == "Resolved")
    k1, k2, k3 = st.columns(3)
    with k1: glass_kpi("🟡 Open",        str(open_c))
    with k2: glass_kpi("🔵 In Progress", str(ip_c))
    with k3: glass_kpi("🟢 Resolved",    str(res_c))

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    STATUS_LIST = ["Open", "In Progress", "Resolved"]

    for i, q in enumerate(queries):
        icon  = STATUS_ICONS.get(q["status"], "○")
        color = STATUS_COLORS.get(q["status"], "#6b7280")
        sev_color = {"Low": "#34d399", "Medium": "#fbbf24", "High": "#f87171"}.get(q["severity"], "#6b7280")

        with st.expander(
            f"{icon}  {q['ticket']}  —  {q['subject']}  ·  [{q['severity']}]",
            expanded=(q["status"] == "Open"),
        ):
            st.markdown(
                f"<div style='font-size:.8rem;color:#d4d4d4;margin-bottom:.5rem;'>"
                f"<b>Section:</b> {q['section']}  ·  "
                f"<b>Severity:</b> <span style='color:{sev_color};'>{q['severity']}</span>  ·  "
                f"<b>Submitted:</b> {q['submitted_at']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Description:** {q['desc']}")

            if q.get("note"):
                st.markdown(
                    f"<div style='background:rgba(34,211,238,.07);border-left:3px solid #22d3ee;"
                    f"padding:6px 12px;border-radius:6px;font-size:.8rem;color:#d4d4d4;margin:.5rem 0;'>"
                    f"📝 Resolution note: {q['note']}</div>",
                    unsafe_allow_html=True,
                )

            ns_idx = STATUS_LIST.index(q["status"])
            new_status = st.selectbox(
                "Update Status", STATUS_LIST, index=ns_idx, key=f"qs_{q['ticket']}",
                label_visibility="collapsed",
            )
            new_note = st.text_area(
                "Resolution Note", value=q.get("note", ""), key=f"qn_{q['ticket']}",
                height=80, label_visibility="collapsed",
                placeholder="Add resolution note…",
            )
            if st.button("💾 Save", key=f"qsv_{q['ticket']}"):
                old = queries[i]["status"]
                queries[i]["status"] = new_status
                queries[i]["note"]   = new_note
                if old != new_status:
                    _log(f"📋 Query {q['ticket']} updated",
                         f"Status: {old} → {new_status} | {q['subject']}", "action")
                st.rerun()


# ── Client Query Form (public — no password needed) ───────────────────────
def render_client_query_form():
    section("CLIENT QUERIES")

    queries = st.session_state.recon_queries

    with st.expander("📝 Submit a Query / Report an Issue", expanded=False):
        q_section  = st.selectbox(
            "Section", ["Dashboard", "Portfolio", "SIP", "Transactions", "Alerts", "Other"],
            key="cq_section",
        )
        q_subject  = st.text_input("Subject", placeholder="Brief issue title", key="cq_subject")
        q_desc     = st.text_area("Describe the issue", placeholder="What did you notice?",
                                   key="cq_desc", height=100)
        q_severity = st.radio("Severity", ["Low", "Medium", "High"],
                              horizontal=True, key="cq_sev")

        if st.button("🎫 Submit Query", key="cq_submit"):
            if not q_subject.strip() or not q_desc.strip():
                st.error("Please fill in Subject and Description.")
            else:
                st.session_state.recon_qnum += 1
                ticket = f"SPC-{st.session_state.recon_qnum:03d}"
                queries.append({
                    "ticket":       ticket,
                    "section":      q_section,
                    "subject":      q_subject.strip(),
                    "desc":         q_desc.strip(),
                    "severity":     q_severity,
                    "status":       "Open",
                    "note":         "",
                    "submitted_at": datetime.datetime.now().strftime("%d %b %Y  %H:%M"),
                })
                _log(f"🎫 Query Raised: {ticket}", f"{q_subject} [{q_severity}]", "action")
                st.success(f"✅ Query submitted! Ticket number: **{ticket}**")
                st.rerun()

    # My Queries (public view)
    if queries:
        STATUS_ICONS = {"Open": "🟡", "In Progress": "🔵", "Resolved": "🟢"}
        st.markdown("**My Queries**")
        for q in queries:
            icon = STATUS_ICONS.get(q["status"], "○")
            sev_color = {"Low": "#34d399", "Medium": "#fbbf24", "High": "#f87171"}.get(q["severity"], "#6b7280")
            st.markdown(
                f"<div style='padding:7px 14px;border-radius:10px;"
                f"background:rgba(17,17,48,.5);border:1px solid rgba(139,92,246,.15);"
                f"margin-bottom:5px;font-size:.8rem;display:flex;justify-content:space-between;"
                f"align-items:center;'>"
                f"<span>{icon} <b style='color:#f0f0ff;'>{q['ticket']}</b> — {q['subject']}</span>"
                f"<span style='color:{sev_color};font-size:.72rem;font-weight:700;'>{q['severity']} · {q['status']}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────
_init()

page_header("Reconciliation 🔒", "Admin-only data management panel")

# Client queries always visible (no password required)
render_client_query_form()

# Check for portfolio data
data = _active_data()
if not data:
    st.warning("No portfolio loaded. Upload a CAS file from **SipCheck Home** first.")
    st.stop()

# Password gate
if not st.session_state.recon_auth:
    section("ADMIN ACCESS")
    render_lock_screen()
    st.stop()

# ── Admin section ────────────────────────────────────────────────────────
render_admin_header()

section("GLOBAL SEARCH")
render_global_search(data)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📁  Folio Reconciliation",
    "📊  Scheme Reconciliation",
    "⏸  SIP Reconciliation",
    "📝  Activity Log",
    "🎫  Queries (Admin)",
])

with tab1:
    render_folio_recon(data)
with tab2:
    render_scheme_recon(data)
with tab3:
    render_sip_recon(data)
with tab4:
    render_activity_log()
with tab5:
    render_queries_admin()
