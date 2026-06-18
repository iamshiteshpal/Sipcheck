"""pages/00_Get_CAS.py — Step-by-step guide to request CAMS CAS PDF."""
from __future__ import annotations

import html as _html
import re
import streamlit as st
import streamlit.components.v1 as components
from datetime import date
from sidebar_v2 import render_sidebar

# ── Design tokens ──────────────────────────────────────────────────────────────
_BG  = "#070714"; _GL  = "rgba(17,17,48,0.55)"
_VIO = "#8b5cf6"; _CYN = "#22d3ee"; _MNT = "#34d399"
_AMB = "#fbbf24"; _EMB = "#f87171"; _INK = "#f0f0ff"
_MUT = "#8b93a7"; _BD  = "rgba(139,92,246,0.22)"
_CAMS_URL = (
    "https://www.camsonline.com/Investors/Statements/Consolidated-Account-Statement"
)


# ── Validators ─────────────────────────────────────────────────────────────────
def _pan_ok(v: str) -> bool:
    return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", v))

def _email_ok(v: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", v))


# ── CSS ─────────────────────────────────────────────────────────────────────────
def _inject_css() -> None:
    st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap');
html,body,[data-testid="stAppViewContainer"]{{background:{_BG}!important;color:{_INK};font-family:'Space Grotesk',sans-serif;}}
[data-testid="stAppViewContainer"]{{scroll-behavior:smooth;}}
#MainMenu,footer{{visibility:hidden;}}[data-testid="stDecoration"]{{display:none!important;}}
.info-banner{{background:linear-gradient(135deg,rgba(34,211,238,.10),rgba(139,92,246,.08));border:1px solid rgba(34,211,238,.30);border-left:4px solid {_CYN};border-radius:12px;padding:.9rem 1.1rem;font-size:.87rem;line-height:1.6;margin-bottom:1.1rem;color:{_INK};}}
.warn-banner{{background:linear-gradient(135deg,rgba(251,191,36,.10),rgba(248,113,113,.08));border:1px solid rgba(251,191,36,.35);border-left:4px solid {_AMB};border-radius:12px;padding:.9rem 1.1rem;font-size:.87rem;line-height:1.6;margin-bottom:1.1rem;color:{_INK};}}
.tip-note{{background:rgba(139,92,246,.07);border:1px solid rgba(139,92,246,.18);border-radius:10px;padding:.7rem 1rem;font-size:.82rem;color:{_MUT};line-height:1.55;margin-bottom:.9rem;}}
.step-wrap{{display:flex;align-items:flex-start;gap:.9rem;background:rgba(17,17,48,.62);border:1px solid {_BD};border-radius:14px;padding:1rem 1.2rem;margin-bottom:.7rem;}}
.sn{{display:flex;align-items:center;justify-content:center;min-width:44px;width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,{_VIO},{_CYN});color:#fff;font-weight:800;font-size:1.05rem;box-shadow:0 0 18px rgba(139,92,246,.4);flex-shrink:0;}}
.sn.done{{background:linear-gradient(135deg,{_MNT},rgba(34,211,238,.7));box-shadow:0 0 14px rgba(52,211,153,.4);}}
.sb{{flex:1;min-width:0;}}
.st-ttl{{font-size:.92rem;font-weight:700;color:{_INK};margin-bottom:.3rem;}}
.st-why{{font-size:.73rem;color:{_MUT};margin-top:.35rem;}}
.st-warn{{color:{_AMB};font-size:.79rem;margin-top:.3rem;font-weight:600;}}
.val-wrap{{background:rgba(8,8,26,.8);border:1px solid rgba(139,92,246,.35);border-radius:12px;padding:.8rem 1rem;margin:.5rem 0;text-align:center;}}
.val-lbl{{font-size:.66rem;color:{_MUT};letter-spacing:.08em;text-transform:uppercase;margin-bottom:.3rem;}}
.val-md{{font-family:'JetBrains Mono',monospace;font-size:1.6rem;font-weight:700;color:{_CYN};letter-spacing:.04em;word-break:break-all;}}
.val-xl{{font-family:'JetBrains Mono',monospace;font-size:1.85rem;font-weight:700;color:{_AMB};letter-spacing:.05em;word-break:break-all;line-height:1.3;}}
.val-xl-grn{{font-family:'JetBrains Mono',monospace;font-size:1.85rem;font-weight:700;color:{_MNT};letter-spacing:.05em;word-break:break-all;line-height:1.3;}}
.val-generic{{font-family:'JetBrains Mono',monospace;font-size:1.1rem;font-weight:500;color:{_MUT};letter-spacing:.03em;font-style:italic;}}
.sh{{font-size:1.12rem;font-weight:700;color:{_INK};margin:1.3rem 0 .8rem;padding-bottom:.4rem;border-bottom:1px solid rgba(139,92,246,.18);}}
.priv{{font-size:.7rem;color:{_MUT};text-align:right;margin-top:.5rem;}}
.cams-btn-wrap{{text-align:center;margin:1.2rem 0;}}
a.cams-btn{{display:inline-block;background:linear-gradient(135deg,{_VIO},{_CYN});color:#fff!important;font-weight:700;font-size:1.05rem;padding:.85rem 2.2rem;border-radius:14px;text-decoration:none!important;letter-spacing:.02em;box-shadow:0 4px 24px rgba(139,92,246,.4);transition:transform .15s,box-shadow .15s;}}
a.cams-btn:hover{{transform:translateY(-2px);box-shadow:0 6px 30px rgba(139,92,246,.55);}}
.cta-card{{background:linear-gradient(135deg,rgba(139,92,246,.15),rgba(34,211,238,.08));border:1px solid rgba(139,92,246,.35);border-radius:20px;padding:2rem 1.8rem;text-align:center;margin-top:1rem;}}
.sep{{border-top:1px solid rgba(139,92,246,.15);margin:1.5rem 0;}}
</style>""", unsafe_allow_html=True)


# ── Copy button (clipboard API + execCommand fallback) ─────────────────────────
def _copy_btn(text: str, uid: str, label: str = "📋 Copy") -> None:
    safe = (text.replace("\\", "\\\\").replace("'", "\\'")
               .replace("\n", "\\n").replace("\r", ""))
    html = f"""<style>
#cb{uid}{{background:linear-gradient(135deg,rgba(139,92,246,.22),rgba(34,211,238,.16));
color:#f0f0ff;border:1px solid rgba(139,92,246,.40);border-radius:8px;padding:6px 16px;
cursor:pointer;font-size:13px;font-weight:600;font-family:'Space Grotesk',sans-serif;
transition:all .2s;white-space:nowrap;}}
#cb{uid}:hover{{background:linear-gradient(135deg,rgba(139,92,246,.38),rgba(34,211,238,.28));}}
</style>
<button id="cb{uid}" onclick="var b=this,t='{safe}';
navigator.clipboard.writeText(t).then(function(){{
  b.textContent='✓ Copied!';b.style.color='#34d399';
  setTimeout(function(){{b.textContent='{label}';b.style.color='#f0f0ff';}},2000);
}}).catch(function(){{
  var ta=document.createElement('textarea');ta.value=t;
  document.body.appendChild(ta);ta.select();document.execCommand('copy');
  document.body.removeChild(ta);b.textContent='✓ Copied!';b.style.color='#34d399';
  setTimeout(function(){{b.textContent='{label}';b.style.color='#f0f0ff';}},2000);
}});">{label}</button>"""
    components.html(html, height=42)


# ── Generic step card + checkbox ───────────────────────────────────────────────
def _step(n: int, title: str, body: str, why: str = "", warn: str = "") -> None:
    done = st.session_state.get(f"cas_step_{n}", False)
    nc   = "sn done" if done else "sn"
    dim  = "opacity:.65;" if done else ""
    st.markdown(f"""
<div class="step-wrap" style="{dim}">
  <div class="{nc}">{n}</div>
  <div class="sb">
    <div class="st-ttl">{title}</div>
    <div style="font-size:.85rem;color:{_INK};margin:.2rem 0;">{body}</div>
    {f'<div class="st-warn">⚠ {warn}</div>' if warn else ""}
    {f'<div class="st-why">💡 {why}</div>' if why else ""}
  </div>
</div>""", unsafe_allow_html=True)
    st.checkbox("✓ Done", key=f"cas_step_{n}")


# ── Optional cheat-sheet form (collapsible) ────────────────────────────────────
def _cheatsheet_form() -> None:
    st.markdown(
        '<div class="tip-note">💡 <strong>Most users skip the form below</strong> and use '
        'the step-by-step guide directly. The form just displays your email, PAN, and '
        'password in large text while you type into CAMS — open it only if you find that helpful.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("📝 Want a visual cheat-sheet? (Optional)", expanded=False):
        # Email
        st.text_input("Email ID", key="cas_email", placeholder="you@example.com")
        email = st.session_state.get("cas_email", "").strip()
        if email and not _email_ok(email):
            st.caption("⚠ Enter a valid email address.")

        # PAN — optional, no max_chars, auto-uppercased on read
        st.text_input("PAN Number (Optional)", key="cas_pan",
                      placeholder="e.g. ABCDE1234F",
                      help="Skip if you don't remember — email alone works on CAMS")
        st.caption("Skip if you don't remember — email alone works. Any case is fine.")
        pan = st.session_state.get("cas_pan", "").upper().strip()
        if pan and not _pan_ok(pan):
            st.caption("⚠ PAN format: 5 letters + 4 digits + 1 letter (e.g. ABCDE1234F)")

        # Password
        show_pw = st.checkbox("Show password", key="cas_show_pw")
        st.text_input(
            "Choose Your Password", key="cas_pw",
            type="default" if show_pw else "password",
            placeholder="Min 8 characters — e.g. Rahul@2026",
        )
        pw = st.session_state.get("cas_pw", "")
        if pw and len(pw) < 8:
            st.caption("⚠ Password must be at least 8 characters.")

        st.markdown(
            '<div class="priv">🔒 Optional details (if filled) stay only in this browser tab. '
            'Nothing is saved or sent anywhere.</div>',
            unsafe_allow_html=True,
        )

        if st.button("Clear Details", key="cas_clear"):
            for k in (["cas_pan", "cas_email", "cas_pw", "cas_show_pw", "cas_show_pw9"]
                       + [f"cas_step_{i}" for i in range(1, 10)]):
                st.session_state.pop(k, None)
            st.rerun()


# ── Full step-by-step guide (always shown) ─────────────────────────────────────
def _guide() -> None:
    email = st.session_state.get("cas_email", "").strip()
    pan   = st.session_state.get("cas_pan", "").upper().strip()
    pw    = st.session_state.get("cas_pw", "")

    # Validate what was filled so we only display real values
    has_email = bool(email and _email_ok(email))
    has_pan   = bool(pan and _pan_ok(pan))
    has_pw    = len(pw) >= 8

    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

    # ── Open CAMS button (always prominent) ────────────────────────────────────
    st.markdown(
        f'<div class="cams-btn-wrap">'
        f'<a class="cams-btn" href="{_CAMS_URL}" target="_blank">🌐 Open CAMS Website</a>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="warn-banner"><strong>⚠ Important:</strong> CAMS blocks copy-paste in '
        'Email and Password fields. Keep THIS page open in another tab and '
        '<strong>type the values carefully</strong> while reading from here.</div>',
        unsafe_allow_html=True,
    )

    # ── Steps 1–6: same for all users ─────────────────────────────────────────
    _step(1,
          'Select Correct Statement Icon',
          'In the <strong>left sidebar</strong> on the CAMS page, click the '
          '<strong>FIRST icon</strong> labeled <strong>"CAS – CAMS+KFintech"</strong>.',
          why="Consolidated data from both registrars — every fund you own in one PDF.",
          warn='Do NOT click "CAS-CAMS" (without KFintech) — that misses half your funds.')

    _step(2,
          'Statement Type',
          'Select <strong>"Detailed (Includes transaction listing)"</strong>.',
          why="Full transaction history is required for SipCheck analysis.")

    _step(3,
          'Period',
          'Select the <strong>"Specific Period"</strong> radio button.')

    # Step 4 — From Date
    from_d = "01-Jan-1991"
    done4  = st.session_state.get("cas_step_4", False)
    st.markdown(f"""
<div class="step-wrap" style="{'opacity:.65;' if done4 else ''}">
  <div class="{'sn done' if done4 else 'sn'}">4</div>
  <div class="sb">
    <div class="st-ttl">From Date</div>
    <div style="font-size:.85rem;color:{_INK};margin:.2rem 0 .4rem;">
      Enter this start date in the <strong>From</strong> field on CAMS:</div>
    <div class="val-wrap"><div class="val-lbl">FROM DATE</div>
      <div class="val-md">{from_d}</div></div>
    <div class="st-why">💡 Earliest date CAMS allows — captures your complete fund history.</div>
  </div>
</div>""", unsafe_allow_html=True)
    c4, _ = st.columns([1, 4])
    with c4:
        _copy_btn(from_d, "fd")
    st.checkbox("✓ Done", key="cas_step_4")

    # Step 5 — To Date
    to_d  = date.today().strftime("%d-%b-%Y")
    done5 = st.session_state.get("cas_step_5", False)
    st.markdown(f"""
<div class="step-wrap" style="{'opacity:.65;' if done5 else ''}">
  <div class="{'sn done' if done5 else 'sn'}">5</div>
  <div class="sb">
    <div class="st-ttl">To Date</div>
    <div style="font-size:.85rem;color:{_INK};margin:.2rem 0 .4rem;">
      Enter today's date in the <strong>To</strong> field on CAMS:</div>
    <div class="val-wrap"><div class="val-lbl">TO DATE (TODAY — AUTO-UPDATED)</div>
      <div class="val-md">{to_d}</div></div>
    <div class="st-why">💡 Always use today for the most current data.</div>
  </div>
</div>""", unsafe_allow_html=True)
    c5, _ = st.columns([1, 4])
    with c5:
        _copy_btn(to_d, "td")
    st.checkbox("✓ Done", key="cas_step_5")

    _step(6,
          'Folio Listing',
          'Select <strong>"With zero balance folios"</strong>.',
          why="Includes closed/redeemed folios — SipCheck builds your complete transaction history.")

    # ── Steps 7–9: adaptive (big display if form filled, generic if not) ───────

    # Step 7 — Email
    done7 = st.session_state.get("cas_step_7", False)
    if has_email:
        email_h = _html.escape(email)
        st.markdown(f"""
<div class="step-wrap" style="border-color:rgba(251,191,36,.4);{'opacity:.65;' if done7 else ''}">
  <div class="{'sn done' if done7 else 'sn'}">7</div>
  <div class="sb">
    <div class="st-ttl">Type Your Email Address
      <span style="color:{_AMB};font-size:.78rem;font-weight:600;"> (PASTE BLOCKED)</span></div>
    <div style="font-size:.85rem;color:{_INK};margin:.2rem 0 .4rem;">
      Type this email carefully in the <strong>Email</strong> field on CAMS:</div>
    <div class="val-wrap" style="border-color:rgba(251,191,36,.45);">
      <div class="val-lbl">YOUR EMAIL — TYPE THIS</div>
      <div class="val-xl">{email_h}</div>
    </div>
    <div class="st-warn">⚠ Paste is blocked by CAMS — type every character manually.</div>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div class="step-wrap" style="{'opacity:.65;' if done7 else ''}">
  <div class="{'sn done' if done7 else 'sn'}">7</div>
  <div class="sb">
    <div class="st-ttl">Type Your Email Address
      <span style="color:{_AMB};font-size:.78rem;font-weight:600;"> (PASTE BLOCKED)</span></div>
    <div style="font-size:.85rem;color:{_INK};margin:.2rem 0 .4rem;">
      Type your registered email address in the <strong>Email</strong> field on CAMS.</div>
    <div class="val-wrap" style="border-color:rgba(139,92,246,.20);">
      <div class="val-lbl">YOUR EMAIL</div>
      <div class="val-generic">your registered email address</div>
    </div>
    <div class="st-warn">⚠ Paste is blocked — type manually.</div>
    <div class="st-why">💡 Fill the optional cheat-sheet above to see your email in large text here.</div>
  </div>
</div>""", unsafe_allow_html=True)
    st.checkbox("✓ Done", key="cas_step_7")

    # Step 8 — PAN
    done8 = st.session_state.get("cas_step_8", False)
    if has_pan:
        pan_h = _html.escape(pan)
        st.markdown(f"""
<div class="step-wrap" style="{'opacity:.65;' if done8 else ''}">
  <div class="{'sn done' if done8 else 'sn'}">8</div>
  <div class="sb">
    <div class="st-ttl">PAN Number
      <span style="color:{_MUT};font-size:.78rem;font-weight:500;"> (Optional but recommended)</span></div>
    <div style="font-size:.85rem;color:{_INK};margin:.2rem 0 .4rem;">
      Enter your PAN in the <strong>PAN</strong> field on CAMS:</div>
    <div class="val-wrap"><div class="val-lbl">YOUR PAN</div>
      <div class="val-md">{pan_h}</div></div>
  </div>
</div>""", unsafe_allow_html=True)
        c8, _ = st.columns([1, 4])
        with c8:
            _copy_btn(pan, "pn")
    else:
        st.markdown(f"""
<div class="step-wrap" style="{'opacity:.65;' if done8 else ''}">
  <div class="{'sn done' if done8 else 'sn'}">8</div>
  <div class="sb">
    <div class="st-ttl">PAN Number
      <span style="color:{_MUT};font-size:.78rem;font-weight:500;"> (Optional but recommended)</span></div>
    <div style="font-size:.85rem;color:{_INK};margin:.2rem 0 .3rem;">
      Enter your PAN in the <strong>PAN</strong> field on CAMS, or leave it blank.</div>
    <div class="st-why">💡 Fill the optional cheat-sheet above to show your PAN here with a copy button.</div>
  </div>
</div>""", unsafe_allow_html=True)
    st.checkbox("✓ Done", key="cas_step_8")

    # Step 9 — Password
    show9 = st.session_state.get("cas_show_pw9", False)
    done9 = st.session_state.get("cas_step_9", False)
    if has_pw:
        pw_disp = _html.escape(pw) if show9 else "•" * len(pw)
        pw_cls  = "val-xl-grn" if show9 else "val-xl"
        st.markdown(f"""
<div class="step-wrap" style="border-color:rgba(52,211,153,.35);{'opacity:.65;' if done9 else ''}">
  <div class="{'sn done' if done9 else 'sn'}">9</div>
  <div class="sb">
    <div class="st-ttl">Type Your Password
      <span style="color:{_AMB};font-size:.78rem;font-weight:600;"> (PASTE BLOCKED)</span></div>
    <div style="font-size:.85rem;color:{_INK};margin:.2rem 0 .4rem;">
      Type this in <em>both</em> the <strong>Password</strong> and
      <strong>Confirm Password</strong> fields on CAMS:</div>
    <div class="val-wrap" style="border-color:rgba(52,211,153,.4);">
      <div class="val-lbl">YOUR PASSWORD — TYPE THIS EXACTLY</div>
      <div class="{pw_cls}">{pw_disp}</div>
    </div>
    <div class="st-warn">⚠ Paste is blocked — type carefully in both password fields.</div>
    <div class="st-why">💡 <strong>Remember this password</strong> — you'll need it to open the PDF when it arrives.</div>
  </div>
</div>""", unsafe_allow_html=True)
        c9a, _ = st.columns([2, 3])
        with c9a:
            lbl9 = "👁 Reveal Password" if not show9 else "🙈 Hide Password"
            if st.button(lbl9, key="cas_pw9_tog"):
                st.session_state["cas_show_pw9"] = not show9
                st.rerun()
    else:
        st.markdown(f"""
<div class="step-wrap" style="border-color:rgba(52,211,153,.25);{'opacity:.65;' if done9 else ''}">
  <div class="{'sn done' if done9 else 'sn'}">9</div>
  <div class="sb">
    <div class="st-ttl">Type Your Password
      <span style="color:{_AMB};font-size:.78rem;font-weight:600;"> (PASTE BLOCKED)</span></div>
    <div style="font-size:.85rem;color:{_INK};margin:.2rem 0 .3rem;">
      Choose a password and type it in <em>both</em> the <strong>Password</strong> and
      <strong>Confirm Password</strong> fields on CAMS.</div>
    <div class="st-warn">⚠ Paste is blocked — type carefully in both password fields.</div>
    <div class="st-why">💡 Fill the optional cheat-sheet above to show your password in large text here.<br>
      <strong>Remember your chosen password</strong> — you'll need it to open the PDF when it arrives.</div>
  </div>
</div>""", unsafe_allow_html=True)
    st.checkbox("✓ Done", key="cas_step_9")

    # ── Final: Submit ──────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="step-wrap" style="border-color:rgba(52,211,153,.5);margin-top:.5rem;">
  <div style="display:flex;align-items:center;justify-content:center;min-width:44px;width:44px;
    height:44px;border-radius:50%;background:linear-gradient(135deg,{_MNT},rgba(34,211,238,.7));
    color:#fff;font-weight:800;font-size:1.2rem;box-shadow:0 0 14px rgba(52,211,153,.4);
    flex-shrink:0;">✓</div>
  <div class="sb" style="margin-left:.9rem;">
    <div class="st-ttl" style="color:{_MNT};">Submit on CAMS</div>
    <div style="font-size:.85rem;color:{_INK};margin:.2rem 0;">
      Click the <strong>Submit</strong> button on the CAMS website.</div>
    <div style="font-size:.82rem;color:{_MUT};margin:.45rem 0 0;line-height:1.65;">
      📧 A password-protected PDF will arrive in your email in <strong>5–15 minutes</strong>.<br>
      💡 Check your spam / junk folder if not received within 30 minutes.
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ── Final CTA card ─────────────────────────────────────────────────────────────
def _cta() -> None:
    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="cta-card">
  <div style="font-size:1.25rem;font-weight:700;color:{_INK};margin-bottom:.5rem;">
    📄 Got your CAS PDF in email?</div>
  <div style="font-size:.88rem;color:{_MUT};margin-bottom:1.3rem;line-height:1.55;">
    Upload it to SipCheck and see your complete portfolio analyzed in seconds.</div>
</div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Upload CAS Now →", use_container_width=True,
                     type="primary", key="cas_go_upload"):
            st.switch_page("dashboard.py")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(
        page_title="Get Your CAS · SipCheck",
        page_icon="📥",
        layout="centered",
        initial_sidebar_state="auto",
    )
    render_sidebar()
    _inject_css()

    st.markdown(f"""
<div style="text-align:center;padding:1.8rem 0 1rem;">
  <div style="font-size:2rem;font-weight:800;color:{_INK};letter-spacing:-.02em;">
    📥 Get Your CAS PDF</div>
  <div style="font-size:.95rem;color:{_MUT};margin-top:.4rem;line-height:1.5;">
    Don't have your CAS yet? Follow this guide — takes 2 minutes.</div>
</div>""", unsafe_allow_html=True)

    st.markdown(
        '<div class="info-banner"><strong>💡 Why only CAMS?</strong> CAMS CAS is already '
        'consolidated — it includes <em>all</em> your mutual funds across both CAMS and '
        'KFintech registrars in a single PDF. One request, complete data covering every '
        'fund you own.</div>',
        unsafe_allow_html=True,
    )

    _cheatsheet_form()
    _guide()
    _cta()


main()
