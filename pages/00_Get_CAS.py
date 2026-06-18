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
.sh{{font-size:1.12rem;font-weight:700;color:{_INK};margin:1.3rem 0 .8rem;padding-bottom:.4rem;border-bottom:1px solid rgba(139,92,246,.18);}}
.priv{{font-size:.7rem;color:{_MUT};text-align:right;margin-bottom:.4rem;}}
.cams-btn-wrap{{text-align:center;margin:1.2rem 0;}}
a.cams-btn{{display:inline-block;background:linear-gradient(135deg,{_VIO},{_CYN});color:#fff!important;font-weight:700;font-size:1.05rem;padding:.85rem 2.2rem;border-radius:14px;text-decoration:none!important;letter-spacing:.02em;box-shadow:0 4px 24px rgba(139,92,246,.4);transition:transform .15s,box-shadow .15s;}}
a.cams-btn:hover{{transform:translateY(-2px);box-shadow:0 6px 30px rgba(139,92,246,.55);}}
.cta-card{{background:linear-gradient(135deg,rgba(139,92,246,.15),rgba(34,211,238,.08));border:1px solid rgba(139,92,246,.35);border-radius:20px;padding:2rem 1.8rem;text-align:center;margin-top:1rem;}}
.sep{{border-top:1px solid rgba(139,92,246,.15);margin:1.5rem 0;}}
</style>""", unsafe_allow_html=True)


# ── Copy button (clipboard API with execCommand fallback) ──────────────────────
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


def _scroll_to(el_id: str) -> None:
    components.html(
        f"<script>try{{parent.document.getElementById('{el_id}')"
        f".scrollIntoView({{behavior:'smooth'}})}}catch(e){{}}</script>",
        height=1,
    )


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


# ── Section 1: Your Details ────────────────────────────────────────────────────
def _section1() -> None:
    st.markdown('<div class="sh">📝 Your Details</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="priv">🔒 Your details stay only in this browser tab — nothing saved or sent anywhere.</div>',
        unsafe_allow_html=True,
    )

    # PAN
    pan_raw = st.text_input("PAN Number", key="cas_pan",
                            placeholder="e.g. ABCDE1234F", max_chars=10)
    pan = pan_raw.upper().strip()
    pan_valid = _pan_ok(pan)
    if pan and not pan_valid:
        st.markdown(
            f'<div style="color:{_EMB};font-size:.75rem;margin-top:-8px;">'
            f'⚠ Must be 5 letters + 4 digits + 1 letter (e.g. ABCDE1234F)</div>',
            unsafe_allow_html=True,
        )

    # Email
    email_raw = st.text_input("Email ID", key="cas_email",
                              placeholder="you@example.com")
    email = email_raw.strip()
    email_valid = _email_ok(email)
    if email and not email_valid:
        st.markdown(
            f'<div style="color:{_EMB};font-size:.75rem;margin-top:-8px;">'
            f'⚠ Enter a valid email address</div>',
            unsafe_allow_html=True,
        )

    # DOB
    if "cas_dob" not in st.session_state:
        st.session_state["cas_dob"] = date(1990, 1, 1)
    dob = st.date_input("Date of Birth", key="cas_dob",
                        min_value=date(1920, 1, 1), max_value=date.today())

    # Password
    show_pw = st.checkbox("Show password", key="cas_show_pw")
    pw = st.text_input(
        "Choose Your Password", key="cas_pw",
        type="default" if show_pw else "password",
        placeholder="Min 8 characters",
    )
    st.markdown(
        f'<div style="font-size:.72rem;color:{_MUT};margin-top:-8px;">'
        f'💡 Suggestion: combine name + year — e.g. '
        f'<span style="font-family:\'JetBrains Mono\',monospace;color:{_AMB};">Rahul@2026</span></div>',
        unsafe_allow_html=True,
    )
    pw_valid = len(pw) >= 8
    if pw and not pw_valid:
        st.markdown(
            f'<div style="color:{_EMB};font-size:.75rem;">⚠ Password must be at least 8 characters</div>',
            unsafe_allow_html=True,
        )

    all_valid = pan_valid and email_valid and (dob is not None) and pw_valid

    col_a, col_b = st.columns([3, 1])
    with col_a:
        if st.button("Continue to CAS Request →", disabled=not all_valid,
                     use_container_width=True, type="primary", key="cas_continue"):
            st.session_state["cas_guide_ready"] = True
            _scroll_to("cas-s2")
    with col_b:
        if st.button("Clear", use_container_width=True, key="cas_clear"):
            for k in (["cas_pan", "cas_email", "cas_dob", "cas_pw",
                        "cas_show_pw", "cas_guide_ready", "cas_show_pw9"]
                       + [f"cas_step_{i}" for i in range(1, 10)]):
                st.session_state.pop(k, None)
            st.rerun()

    if not all_valid and any([pan, email, pw]):
        st.caption("Complete all fields correctly to unlock the step-by-step guide.")


# ── Section 2: CAS Request Guide ──────────────────────────────────────────────
def _section2(email: str, pan: str, pw: str) -> None:
    email_h = _html.escape(email)
    pan_h   = _html.escape(pan)

    st.markdown('<div id="cas-s2" style="padding-top:.5rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sh">🌐 CAS Request Helper</div>', unsafe_allow_html=True)

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

    # ── Steps 1-3 (simple text) ────────────────────────────────────────────────
    _step(1,
          'Select Correct Statement Icon',
          'In the <strong>left sidebar</strong> on the CAMS page, click the '
          '<strong>FIRST icon</strong> labeled <strong>"CAS – CAMS+KFintech"</strong>.',
          why="This gives consolidated data from both registrars — every fund you own in one PDF.",
          warn='Do NOT click "CAS-CAMS" (without KFintech) — that misses half your funds.')

    _step(2,
          'Statement Type',
          'Select <strong>"Detailed (Includes transaction listing)"</strong>.',
          why="Full transaction history is required for SipCheck analysis.")

    _step(3,
          'Period',
          'Select the <strong>"Specific Period"</strong> radio button.')

    # ── Step 4: From Date ──────────────────────────────────────────────────────
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

    # ── Step 5: To Date ────────────────────────────────────────────────────────
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

    # ── Step 6 ─────────────────────────────────────────────────────────────────
    _step(6,
          'Folio Listing',
          'Select <strong>"With zero balance folios"</strong>.',
          why="Includes closed/redeemed folios — SipCheck builds your complete transaction history.")

    # ── Step 7: Type Email (NO copy button) ────────────────────────────────────
    done7 = st.session_state.get("cas_step_7", False)
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
    st.checkbox("✓ Done", key="cas_step_7")

    # ── Step 8: PAN (copy OK) ──────────────────────────────────────────────────
    done8 = st.session_state.get("cas_step_8", False)
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
    st.checkbox("✓ Done", key="cas_step_8")

    # ── Step 9: Type Password (NO copy button, show/hide toggle) ───────────────
    show9   = st.session_state.get("cas_show_pw9", False)
    pw_disp = _html.escape(pw) if show9 else "•" * max(len(pw), 1)
    pw_cls  = "val-xl-grn" if show9 else "val-xl"
    done9   = st.session_state.get("cas_step_9", False)
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
        label9 = "👁 Reveal Password" if not show9 else "🙈 Hide Password"
        if st.button(label9, key="cas_pw9_tog"):
            st.session_state["cas_show_pw9"] = not show9
            st.rerun()
    st.checkbox("✓ Done", key="cas_step_9")

    # ── Final: Submit ──────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="step-wrap" style="border-color:rgba(52,211,153,.5);margin-top:1rem;">
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


# ── Section 3: Final CTA ───────────────────────────────────────────────────────
def _section3() -> None:
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

    _section1()

    if st.session_state.get("cas_guide_ready"):
        email = st.session_state.get("cas_email", "").strip()
        pan   = st.session_state.get("cas_pan", "").upper().strip()
        pw    = st.session_state.get("cas_pw", "")
        st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
        _section2(email, pan, pw)
        st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
        _section3()


main()
