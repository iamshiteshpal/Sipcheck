import sys

content = open('dashboard.py', encoding='utf-8').read()

new_block = r'''    # ── 3D PANEL ROW ─────────────────────────────────────────────────────
    lc, cc, rc = st.columns([3, 4, 3], gap="medium")

    with lc:
        st.markdown("""
        <div style="display:flex;flex-direction:column;gap:16px;padding-top:16px;">
          <div style="animation:floatA 4s ease-in-out infinite;">
            <div style="background:linear-gradient(135deg,rgba(0,30,40,0.9),rgba(0,15,25,0.95));
                        backdrop-filter:blur(20px);border:1px solid rgba(0,240,255,0.3);
                        border-radius:16px;padding:0;overflow:hidden;
                        box-shadow:0 0 0 1px rgba(0,240,255,0.06),0 12px 40px rgba(0,0,0,0.6),
                                   inset 0 1px 0 rgba(0,240,255,0.12);">
              <div style="position:relative;padding:18px;min-height:120px;">
                <svg style="position:absolute;inset:0;width:100%;height:100%;opacity:0.2;"
                     viewBox="0 0 200 120">
                  <path d="M0 30 H40 V10 H80" stroke="#00F0FF" stroke-width="1" fill="none"/>
                  <path d="M80 10 H120 V50 H160 V30 H200" stroke="#00F0FF" stroke-width="1" fill="none"/>
                  <path d="M0 80 H30 V100 H70 V70 H110 V100 H150 V80 H200"
                        stroke="#00F0FF" stroke-width="0.7" fill="none"/>
                  <circle cx="40" cy="10" r="2.5" fill="#00F0FF"/>
                  <circle cx="80" cy="50" r="2.5" fill="#00F0FF"/>
                  <circle cx="160" cy="30" r="2.5" fill="#00F0FF"/>
                </svg>
                <div style="position:relative;display:flex;align-items:center;gap:12px;">
                  <div style="width:54px;height:54px;border-radius:14px;flex-shrink:0;
                              background:radial-gradient(circle at 35% 35%,rgba(0,240,255,0.25),rgba(0,120,150,0.1));
                              border:1px solid rgba(0,240,255,0.4);font-size:26px;line-height:54px;
                              text-align:center;box-shadow:0 0 20px rgba(0,240,255,0.25),
                              inset 0 0 10px rgba(0,240,255,0.08);
                              animation:neonPulse 3s ease infinite;">&#128274;</div>
                  <div>
                    <p style="font-size:13px;font-weight:700;color:white;margin:0 0 4px;">Zero Storage</p>
                    <p style="font-size:10px;color:#64748b;margin:0;line-height:1.5;">
                      On-device parsing<br>No server upload</p>
                  </div>
                </div>
                <div style="position:absolute;left:0;right:0;height:1.5px;top:50%;
                            background:linear-gradient(90deg,transparent,rgba(0,240,255,0.3),transparent);
                            animation:scanline 3s linear infinite;pointer-events:none;"></div>
              </div>
              <div style="height:1px;background:linear-gradient(90deg,rgba(0,240,255,0.3),transparent);"></div>
              <div style="padding:7px 16px;">
                <span style="font-size:9px;color:rgba(0,240,255,0.4);font-family:monospace;letter-spacing:1px;">
                  STATUS: SECURE &#9679; ENCRYPTED</span>
              </div>
            </div>
          </div>
          <div style="animation:floatB 5s ease-in-out .8s infinite;">
            <div style="background:linear-gradient(135deg,rgba(40,0,50,0.9),rgba(20,0,30,0.95));
                        backdrop-filter:blur(20px);border:1px solid rgba(176,38,255,0.3);
                        border-radius:16px;padding:16px 18px;
                        box-shadow:0 0 0 1px rgba(176,38,255,0.06),0 12px 40px rgba(0,0,0,0.6),
                                   inset 0 1px 0 rgba(176,38,255,0.12);">
              <p style="font-size:9px;font-weight:700;color:rgba(176,38,255,0.8);
                        text-transform:uppercase;letter-spacing:2px;margin:0 0 10px;">SIP Health</p>
              <svg width="100%" height="44" viewBox="0 0 180 44" preserveAspectRatio="none">
                <polyline points="0,22 14,22 24,4 40,40 54,8 70,32 90,12 106,26 124,16 160,16 180,16"
                  fill="none" stroke="rgba(176,38,255,0.2)" stroke-width="8"
                  stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="0,22 14,22 24,4 40,40 54,8 70,32 90,12 106,26 124,16 160,16 180,16"
                  fill="none" stroke="#B026FF" stroke-width="2"
                  stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <div style="display:flex;justify-content:space-between;margin-top:8px;">
                <span style="font-size:10px;color:rgba(176,38,255,0.7);">&#9679; 9 active SIPs</span>
                <span style="font-size:10px;color:#34d399;font-weight:600;">0 bounced</span>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with cc:
        st.markdown("""
        <div style="position:relative;z-index:2;">
          <div style="position:absolute;inset:-20px;border-radius:32px;
                      background:radial-gradient(ellipse at center,rgba(0,240,255,0.1) 0%,
                      rgba(176,38,255,0.05) 40%,transparent 70%);
                      filter:blur(18px);pointer-events:none;"></div>
          <div style="position:relative;border-radius:20px;padding:24px 22px 20px;
                      background:rgba(10,14,22,0.95);backdrop-filter:blur(24px);
                      background-image:linear-gradient(rgba(10,14,22,0.95),rgba(8,12,20,0.95)),
                                       linear-gradient(135deg,#00F0FF,#B026FF);
                      background-origin:border-box;background-clip:padding-box,border-box;
                      border:2px solid transparent;
                      box-shadow:0 24px 80px rgba(0,0,0,0.6),0 0 40px rgba(0,240,255,0.05) inset;
                      text-align:center;">
            <div style="position:absolute;top:10px;left:10px;width:12px;height:12px;
                        border-top:2px solid rgba(0,240,255,0.7);
                        border-left:2px solid rgba(0,240,255,0.7);"></div>
            <div style="position:absolute;top:10px;right:10px;width:12px;height:12px;
                        border-top:2px solid rgba(0,240,255,0.7);
                        border-right:2px solid rgba(0,240,255,0.7);"></div>
            <div style="position:absolute;bottom:10px;left:10px;width:12px;height:12px;
                        border-bottom:2px solid rgba(176,38,255,0.7);
                        border-left:2px solid rgba(176,38,255,0.7);"></div>
            <div style="position:absolute;bottom:10px;right:10px;width:12px;height:12px;
                        border-bottom:2px solid rgba(176,38,255,0.7);
                        border-right:2px solid rgba(176,38,255,0.7);"></div>
            <p style="font-size:17px;font-weight:800;color:white;margin:0 0 4px;letter-spacing:-.5px;">
              Upload your CAS PDF</p>
            <p style="font-size:11px;color:#475569;margin:0 0 16px;">
              Drag and drop or click to browse &#8212; PDF only</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "CAS PDF", type=["pdf"],
            label_visibility="collapsed",
            help="Your CAS PDF from CAMS or KFintech"
        )

        st.markdown("""
        <div style="margin:10px 0 5px;text-align:center;">
          <p style="font-size:10px;font-weight:700;color:#334155;margin:0 0 3px;
                    text-transform:uppercase;letter-spacing:1.5px;">Password</p>
          <p style="font-size:10px;color:#475569;margin:0;">PAN (ABCDE1234F) or DOB (DDMMYYYY)</p>
        </div>
        """, unsafe_allow_html=True)

        password = st.text_input(
            "CAS Password", type="password",
            placeholder="ABCDE1234F or 01011990",
            key="pdf_password", label_visibility="collapsed",
        )
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if uploaded and password:
            if st.button("Analyze My Portfolio →", use_container_width=True, type="primary"):
                with st.spinner("Parsing…"):
                    data, error = parse_pdf(uploaded.read(), password)
                if error == "wrong_password":
                    st.error("Wrong password. Try PAN (ABCDE1234F) or DOB (DDMMYYYY).")
                elif error:
                    st.error(f"Parse error: {error}")
                else:
                    portfolio     = process(data)
                    investor_name = portfolio["investor_name"].title()
                    st.session_state.profiles[investor_name] = portfolio
                    st.session_state.active = investor_name
                    st.session_state.pin_ok = True
                    st.success(f"✅ Loaded — {investor_name}")
                    st.rerun()
        elif uploaded:
            st.markdown('<p style="text-align:center;font-size:11px;color:#475569;margin:4px 0;">Enter password above</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="text-align:center;font-size:11px;color:#334155;margin:4px 0;">Upload your PDF above</p>', unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-top:8px;">
          <span style="font-size:9px;color:#334155;letter-spacing:.5px;">
            &#128274; PROCESSED ON DEVICE &#183; NOTHING STORED</span>
        </div>
        """, unsafe_allow_html=True)

    with rc:
        st.markdown("""
        <div style="display:flex;flex-direction:column;gap:16px;padding-top:16px;">
          <div style="animation:floatC 4.5s ease-in-out .4s infinite;">
            <div style="background:linear-gradient(135deg,rgba(0,20,30,0.9),rgba(0,10,20,0.95));
                        backdrop-filter:blur(20px);border:1px solid rgba(0,240,255,0.3);
                        border-radius:16px;padding:16px 18px;
                        box-shadow:0 0 0 1px rgba(0,240,255,0.06),0 12px 40px rgba(0,0,0,0.6),
                                   inset 0 1px 0 rgba(0,240,255,0.12);">
              <p style="font-size:9px;font-weight:700;color:rgba(0,240,255,0.7);
                        text-transform:uppercase;letter-spacing:2px;margin:0 0 12px;">Data Sources</p>
              <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:10px;">
                <div style="display:flex;align-items:center;gap:10px;">
                  <div style="width:34px;height:34px;border-radius:9px;
                              background:rgba(0,240,255,0.15);border:1px solid rgba(0,240,255,0.35);
                              font-size:15px;line-height:34px;text-align:center;
                              box-shadow:0 0 10px rgba(0,240,255,0.2);">&#127970;</div>
                  <div>
                    <p style="font-size:12px;font-weight:700;color:white;margin:0;">CAMS</p>
                    <p style="font-size:9px;color:#64748b;margin:0;">camsonline.com</p>
                  </div>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                  <div style="width:34px;height:34px;border-radius:9px;
                              background:rgba(176,38,255,0.15);border:1px solid rgba(176,38,255,0.35);
                              font-size:15px;line-height:34px;text-align:center;
                              box-shadow:0 0 10px rgba(176,38,255,0.2);">&#127970;</div>
                  <div>
                    <p style="font-size:12px;font-weight:700;color:white;margin:0;">KFintech</p>
                    <p style="font-size:9px;color:#64748b;margin:0;">kfintech.com</p>
                  </div>
                </div>
              </div>
              <svg width="100%" height="24" viewBox="0 0 160 24">
                <path d="M10 8 Q80 0 150 8" stroke="rgba(0,240,255,0.5)" stroke-width="1.5"
                      fill="none" stroke-dasharray="5 3"/>
                <path d="M10 16 Q80 24 150 16" stroke="rgba(176,38,255,0.5)" stroke-width="1.5"
                      fill="none" stroke-dasharray="5 3"/>
                <circle cx="10" cy="12" r="3" fill="#00F0FF"/>
                <circle cx="150" cy="12" r="3" fill="#B026FF"/>
              </svg>
            </div>
          </div>
          <div style="animation:floatD 5.5s ease-in-out 1.2s infinite;">
            <div style="background:linear-gradient(135deg,rgba(0,20,15,0.9),rgba(0,10,8,0.95));
                        backdrop-filter:blur(20px);border:1px solid rgba(16,185,129,0.3);
                        border-radius:16px;padding:16px 18px;
                        box-shadow:0 0 0 1px rgba(16,185,129,0.06),0 12px 40px rgba(0,0,0,0.6),
                                   inset 0 1px 0 rgba(16,185,129,0.12);">
              <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                <p style="font-size:9px;font-weight:700;color:rgba(16,185,129,0.8);
                          text-transform:uppercase;letter-spacing:2px;margin:0;">XIRR</p>
                <span style="font-size:12px;font-weight:800;color:#34d399;
                             text-shadow:0 0 10px rgba(52,211,153,0.5);">&#9650; 8.3%</span>
              </div>
              <div style="display:flex;align-items:flex-end;gap:3px;height:48px;margin-bottom:8px;">
                <div style="flex:1;background:rgba(16,185,129,0.18);border-radius:3px 3px 0 0;height:38%;"></div>
                <div style="flex:1;background:rgba(16,185,129,0.18);border-radius:3px 3px 0 0;height:52%;"></div>
                <div style="flex:1;background:rgba(16,185,129,0.18);border-radius:3px 3px 0 0;height:33%;"></div>
                <div style="flex:1;background:rgba(16,185,129,0.25);border-radius:3px 3px 0 0;height:68%;"></div>
                <div style="flex:1;background:rgba(16,185,129,0.18);border-radius:3px 3px 0 0;height:46%;"></div>
                <div style="flex:1;background:linear-gradient(to top,#065f46,#34d399);
                            border-radius:3px 3px 0 0;height:94%;
                            box-shadow:0 0 14px rgba(52,211,153,0.7),0 -4px 12px rgba(52,211,153,0.3);"></div>
                <div style="flex:1;background:rgba(16,185,129,0.25);border-radius:3px 3px 0 0;height:60%;"></div>
              </div>
              <div style="height:1px;background:linear-gradient(90deg,rgba(16,185,129,0.4),transparent);margin-bottom:6px;"></div>
              <span style="font-size:9px;color:rgba(52,211,153,0.6);font-family:monospace;">LIVE_NAV: CONNECTED</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # features
    st.markdown("""
    <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(0,240,255,0.22),transparent);margin:52px 0 0;"></div>
    <div style="text-align:center;padding:48px 0 32px;">
      <div style="display:inline-block;background:rgba(176,38,255,0.07);border:1px solid rgba(176,38,255,0.28);
                  border-radius:40px;padding:4px 16px;margin-bottom:13px;">
        <span style="font-size:9px;font-weight:700;color:#c084fc;letter-spacing:2px;text-transform:uppercase;">WHY CAS 360</span>
      </div>
      <h2 style="font-size:clamp(1.7rem,3.5vw,2.6rem);font-weight:900;color:white;
                 letter-spacing:-2px;margin:0 0 8px;line-height:1.1;">
        Everything your portfolio needs,<br>in one place.
      </h2>
      <p style="font-size:.9rem;color:#64748b;margin:0;">
        Institutional-grade portfolio intelligence for every Indian investor.
      </p>
    </div>
    """, unsafe_allow_html=True)

    def _dc(col, icon, title, body, bc="rgba(0,240,255,0.13)", ic="rgba(0,240,255,0.07)"):
        col.markdown(f"""<div style="background:rgba(255,255,255,0.025);backdrop-filter:blur(12px);
                    border:1px solid {bc};border-radius:18px;padding:20px;height:100%;">
          <div style="font-size:20px;margin-bottom:12px;">{icon}</div>
          <p style="font-size:14px;font-weight:700;color:white;margin:0 0 7px;">{title}</p>
          <p style="font-size:12px;color:#64748b;line-height:1.6;margin:0;">{body}</p></div>""",
          unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3, gap="medium")
    _dc(f1, "&#128202;", "Live NAV &amp; XIRR",
        "Real-time NAV from MFAPI. Per-scheme XIRR calculated automatically across your entire portfolio history.")
    _dc(f2, "&#128260;", "360&#176; Portfolio View",
        "Every folio, scheme, and transaction from both CAMS and KFintech, unified in one dashboard.",
        "rgba(176,38,255,0.13)", "rgba(176,38,255,0.07)")
    _dc(f3, "&#128176;", "P&amp;L Analytics",
        "Realised &amp; unrealised gains broken down by scheme, category, and time period.")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    fs1, fs2 = st.columns([1.6, 1], gap="medium")
    with fs1:
        st.markdown("""<div style="background:linear-gradient(135deg,rgba(79,46,229,0.4),rgba(139,92,246,0.22),rgba(37,99,235,0.3));
                    backdrop-filter:blur(12px);border:1px solid rgba(139,92,246,0.32);
                    border-radius:18px;padding:22px;">
          <div style="font-size:20px;margin-bottom:11px;">&#128260;</div>
          <p style="font-size:16px;font-weight:800;color:white;margin:0 0 7px;">SIP Health Monitor</p>
          <p style="font-size:12px;color:rgba(255,255,255,0.62);line-height:1.65;margin:0 0 13px;">
            Track every active SIP &#8212; next due dates, mandate status, bounce alerts.</p>
          <span style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.17);
                       color:white;font-size:10px;font-weight:600;padding:3px 10px;border-radius:20px;margin-right:5px;">Active SIPs</span>
          <span style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.17);
                       color:white;font-size:10px;font-weight:600;padding:3px 10px;border-radius:20px;margin-right:5px;">Bounce Alerts</span>
          <span style="background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.17);
                       color:white;font-size:10px;font-weight:600;padding:3px 10px;border-radius:20px;">Next Due Date</span>
        </div>""", unsafe_allow_html=True)
    _dc(fs2, "&#128106;", "Family View",
        "Analyse multiple CAS files together across family members.",
        "rgba(59,130,246,0.18)", "rgba(59,130,246,0.07)")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    fp1, fp2 = st.columns([1, 1.6], gap="medium")
    _dc(fp1, "&#129381;", "Asset Allocation",
        "Equity vs Debt breakdown with interactive charts and risk exposure view.")
    with fp2:
        st.markdown("""<div style="background:rgba(255,255,255,0.025);backdrop-filter:blur(12px);
                    border:1px solid rgba(16,185,129,0.16);border-radius:18px;padding:20px;height:100%;">
          <div style="font-size:20px;margin-bottom:12px;">&#128737;</div>
          <p style="font-size:14px;font-weight:700;color:white;margin:0 0 7px;">100% Private by Design</p>
          <p style="font-size:12px;color:#64748b;line-height:1.6;margin:0 0 12px;">
            Your CAS PDF is parsed entirely on your device using casparser. Nothing uploaded, logged, or stored.</p>
          <span style="background:rgba(16,185,129,0.09);border:1px solid rgba(16,185,129,0.28);
                       color:#34d399;font-size:10px;font-weight:700;padding:3px 10px;border-radius:20px;margin-right:5px;">
            &#10003; No server storage</span>
          <span style="background:rgba(16,185,129,0.09);border:1px solid rgba(16,185,129,0.28);
                       color:#34d399;font-size:10px;font-weight:700;padding:3px 10px;border-radius:20px;">
            &#10003; Local processing</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(176,38,255,0.22),transparent);margin:48px 0 18px;"></div>
    <p style="text-align:center;color:#1e293b;font-size:11px;padding-bottom:44px;">
      &#169; 2026 cas.360 view &nbsp;&middot;&nbsp; All data processed locally &nbsp;&middot;&nbsp; Zero server storage
    </p>
    """, unsafe_allow_html=True)'''

old_start = '    # ── 3-PANEL ROW: left HUDs \xb7 upload portal \xb7 right HUDs ─────────────'
old_end_suffix = '\n\n\n# ─────────────────────────────\n# SIDEBAR'

idx_s = content.find(old_start)
idx_e = content.find(old_end_suffix)

print(f"Block from {idx_s} to {idx_e}, length={idx_e-idx_s}")

new_content = content[:idx_s] + new_block + '\n\n\n' + content[idx_e+3:]

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done. Total lines:', new_content.count('\n'))
