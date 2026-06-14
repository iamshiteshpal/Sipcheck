# pages/01_Markets.py — SipCheck Premium Market Intelligence v2.0
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import pytz
import math
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="Markets — SipCheck", page_icon="📈", layout="wide")
from sidebar_v2 import render_sidebar
render_sidebar()
from ui_theme import inject_theme
inject_theme()

# ── Design tokens ─────────────────────────────────────────────────────────
VL  = "#8b5cf6"
CY  = "#22d3ee"
MN  = "#34d399"
EM  = "#f87171"
AM  = "#fbbf24"
INK = "#f0f0ff"
MUT = "#8b93a7"
GL  = "rgba(17,17,48,0.6)"
BR  = "rgba(139,92,246,0.18)"

# ── Extra styles ──────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600;700&display=swap');
#MainMenu,footer{{visibility:hidden;}}
.mkt-sec{{display:flex;align-items:center;gap:10px;margin:1.6rem 0 0.8rem;}}
.mkt-sec .dot{{width:7px;height:7px;border-radius:2px;background:{VL};
               box-shadow:0 0 10px {VL};transform:rotate(45deg);flex-shrink:0;}}
.mkt-sec .lbl{{font-family:'Space Grotesk',sans-serif;font-size:0.75rem;font-weight:700;
               color:{INK};text-transform:uppercase;letter-spacing:0.14em;}}
.mkt-sec .ln{{flex:1;height:1px;background:linear-gradient(90deg,{BR},transparent);}}
.g{{background:{GL};border:1px solid {BR};border-radius:16px;backdrop-filter:blur(14px);}}
.num{{font-family:'JetBrains Mono',monospace;font-feature-settings:'zero';}}
/* Index ticker strip */
.idx-strip{{display:flex;overflow-x:auto;gap:0;background:rgba(7,7,20,0.9);
            border-top:1px solid {BR};border-bottom:1px solid {BR};padding:4px 0;}}
.idx-cell{{padding:5px 20px;border-right:1px solid rgba(139,92,246,0.12);min-width:130px;flex-shrink:0;}}
/* Sector tile */
.sec-tile{{border-radius:12px;padding:0.7rem 0.9rem;text-align:center;transition:transform .2s;cursor:default;}}
.sec-tile:hover{{transform:scale(1.04);}}
/* FII/DII bar */
.flow-bar{{height:10px;border-radius:5px;overflow:hidden;background:rgba(255,255,255,0.06);}}
/* Mover card */
.mv-card{{border-radius:12px;padding:8px 12px;margin-bottom:5px;display:flex;
          align-items:center;justify-content:space-between;font-size:.8rem;}}
/* Market stats pill */
.stat-pill{{display:inline-flex;flex-direction:column;align-items:center;
            padding:0.6rem 1rem;border-radius:12px;background:{GL};
            border:1px solid {BR};min-width:90px;}}
/* Gauge ring */
@keyframes fadeIn{{from{{opacity:0;transform:translateY(8px);}}to{{opacity:1;transform:none;}}}}
.rise-in{{animation:fadeIn .5s ease both;}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────────────────────────────────

NIFTY50 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","BHARTIARTL.NS","ICICIBANK.NS",
    "INFY.NS","KOTAKBANK.NS","SBIN.NS","HINDUNILVR.NS","ITC.NS",
    "LT.NS","AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","TITAN.NS",
    "ASIANPAINT.NS","SUNPHARMA.NS","WIPRO.NS","ONGC.NS","NTPC.NS",
    "NESTLEIND.NS","INDUSINDBK.NS","TATAMOTORS.NS","JSWSTEEL.NS","COALINDIA.NS",
    "POWERGRID.NS","TECHM.NS","HCLTECH.NS","CIPLA.NS","DRREDDY.NS",
]

SECTOR_MAP = {
    "Banking": ("^CNXBANK",   "🏦"),
    "IT":      ("^CNXIT",     "💻"),
    "Pharma":  ("^CNXPHARMA", "💊"),
    "Auto":    ("^CNXAUTO",   "🚗"),
    "FMCG":    ("^CNXFMCG",   "🛒"),
    "Energy":  ("^CNXENERGY", "⚡"),
    "Metal":   ("^CNXMETAL",  "🔩"),
    "Realty":  ("^CNXREALTY", "🏗️"),
}

INDEX_LIST = [
    ("Nifty 50",   "^NSEI",    VL),
    ("Sensex",     "^BSESN",   CY),
    ("Bank Nifty", "^NSEBANK", MN),
    ("Nifty IT",   "^CNXIT",   AM),
]


@st.cache_data(ttl=300, show_spinner=False)
def fetch_breadth_movers():
    adv = dec = unch = 0
    movers: list[dict] = []
    try:
        raw = yf.download(NIFTY50, period="2d", progress=False, auto_adjust=True)
        closes = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
        for sym in closes.columns:
            try:
                s = closes[sym].dropna()
                if len(s) < 2:
                    continue
                chg = float((s.iloc[-1] - s.iloc[-2]) / s.iloc[-2] * 100)
                name = str(sym).replace(".NS", "")
                movers.append({"name": name, "chg": chg, "price": float(s.iloc[-1])})
                if chg > 0.05:
                    adv += 1
                elif chg < -0.05:
                    dec += 1
                else:
                    unch += 1
            except Exception:
                pass
    except Exception:
        pass
    movers.sort(key=lambda x: x["chg"], reverse=True)
    return adv, dec, unch, movers


@st.cache_data(ttl=300, show_spinner=False)
def fetch_sectors():
    out = []
    for name, (sym, icon) in SECTOR_MAP.items():
        try:
            df = yf.Ticker(sym).history(period="2d")
            if df.empty or len(df) < 2:
                out.append({"name": name, "icon": icon, "chg": 0.0, "ok": False})
                continue
            chg = float((df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2] * 100)
            out.append({"name": name, "icon": icon, "chg": chg, "ok": True})
        except Exception:
            out.append({"name": name, "icon": icon, "chg": 0.0, "ok": False})
    return out


@st.cache_data(ttl=300, show_spinner=False)
def fetch_indices():
    out = []
    for name, sym, color in INDEX_LIST:
        try:
            df = yf.Ticker(sym).history(period="7d")
            if df.empty or len(df) < 2:
                out.append({"name": name, "color": color, "price": 0, "chg": 0, "spark": []})
                continue
            price = float(df["Close"].iloc[-1])
            prev  = float(df["Close"].iloc[-2])
            chg   = (price - prev) / prev * 100
            spark = df["Close"].tail(5).tolist()
            out.append({"name": name, "color": color, "price": price, "chg": chg, "spark": spark})
        except Exception:
            out.append({"name": name, "color": color, "price": 0, "chg": 0, "spark": []})
    return out


@st.cache_data(ttl=600, show_spinner=False)
def fetch_vix():
    try:
        df = yf.Ticker("^INDIAVIX").history(period="2d")
        if df.empty or len(df) < 2:
            return None, None
        v    = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])
        return v, (v - prev) / prev * 100
    except Exception:
        return None, None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_nifty_52w():
    try:
        df     = yf.Ticker("^NSEI").history(period="1y")
        if df.empty or len(df) < 2:
            return None, None, None
        curr   = float(df["Close"].iloc[-1])
        hi52   = float(df["High"].max())
        lo52   = float(df["Low"].min())
        pct_hi = (curr - hi52) / hi52 * 100
        return hi52, lo52, pct_hi
    except Exception:
        return None, None, None


@st.cache_data(ttl=300, show_spinner=False)
def fetch_ticker_strip():
    items = [
        ("NIFTY 50", "^NSEI"), ("SENSEX", "^BSESN"),
        ("BANK NIFTY", "^NSEBANK"), ("NIFTY IT", "^CNXIT"), ("NIFTY MID", "^NSEMDCP50"),
    ]
    out = []
    for label, sym in items:
        try:
            df = yf.Ticker(sym).history(period="2d")
            if df.empty or len(df) < 2:
                continue
            price = float(df["Close"].iloc[-1])
            prev  = float(df["Close"].iloc[-2])
            chg   = (price - prev) / prev * 100
            out.append((label, price, chg))
        except Exception:
            pass
    return out


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fii_dii():
    try:
        sess = requests.Session()
        hdr  = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            "Accept":          "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer":         "https://www.nseindia.com/",
        }
        sess.get("https://www.nseindia.com", headers=hdr, timeout=8)
        r    = sess.get("https://www.nseindia.com/api/fiidiiTradeReact",
                        headers=hdr, timeout=8)
        data = r.json()
        if not data:
            return None
        fii  = next((d for d in data if "FII"    in d.get("category","").upper()), None)
        dii  = next((d for d in data if "DII"    in d.get("category","").upper()), None)
        if fii and dii:
            def _f(x):
                return float(str(x).replace(",","").replace(" ","") or 0)
            return {
                "fii_buy":  _f(fii.get("buyValue",  0)),
                "fii_sell": _f(fii.get("sellValue", 0)),
                "fii_net":  _f(fii.get("netValue",  0)),
                "dii_buy":  _f(dii.get("buyValue",  0)),
                "dii_sell": _f(dii.get("sellValue", 0)),
                "dii_net":  _f(dii.get("netValue",  0)),
                "date":     data[0].get("date", "previous trading day"),
            }
    except Exception:
        pass
    return None


@st.cache_data(ttl=60, show_spinner=False)
def fetch_two(sym):
    try:
        df = yf.Ticker(sym).history(period="5d")
        if df is None or df.empty:
            return 0.0, 0.0
        p = float(df["Close"].iloc[-1])
        q = float(df["Close"].iloc[-2]) if len(df) > 1 else p
        return p, (p - q) / q * 100
    except Exception:
        return 0.0, 0.0


# ── Helpers ────────────────────────────────────────────────────────────────

def _H(s: str) -> str:
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def spark_svg(prices: list, w: int = 90, h: int = 32) -> str:
    if len(prices) < 2:
        return ""
    mn, mx = min(prices), max(prices)
    rng    = mx - mn or 1
    pts    = [(i / (len(prices)-1) * w,
               (h-6) - (p-mn)/rng*(h-10) + 3) for i, p in enumerate(prices)]
    poly   = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    fill   = f"0,{h} " + poly + f" {w},{h}"
    up     = prices[-1] >= prices[0]
    sc     = MN if up else EM
    fc     = "rgba(52,211,153,.12)" if up else "rgba(248,113,113,.12)"
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'style="overflow:visible;">'
            f'<polygon points="{fill}" fill="{fc}"/>'
            f'<polyline points="{poly}" fill="none" stroke="{sc}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
            f'</svg>')


def sec_label(title: str):
    st.markdown(
        f'<div class="mkt-sec"><span class="dot"></span>'
        f'<span class="lbl">{title}</span><span class="ln"></span></div>',
        unsafe_allow_html=True,
    )


def _cr(v: float) -> str:
    return f"₹{abs(v):,.0f} Cr"


def market_status_ist():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    t   = now.hour * 60 + now.minute
    wd  = now.weekday()
    nse = wd < 5 and 9*60+15 <= t <= 15*60+30
    us  = wd < 5 and (t >= 19*60+30 or t <= 2*60)
    return nse, us, now


# ═════════════════════════════════════════════════════════════════════════
# PAGE BEGINS
# ═════════════════════════════════════════════════════════════════════════

nse_open, us_open, now_ist = market_status_ist()

# ── NSE Ticker strip ──────────────────────────────────────────────────────
strip_data = fetch_ticker_strip()
if strip_data:
    cells = "".join(
        f'<div class="idx-cell">'
        f'<div style="font-size:9px;font-weight:700;color:{MUT};letter-spacing:.1em;">{n}</div>'
        f'<div class="num" style="font-size:13px;font-weight:700;color:{INK};margin:2px 0;">{p:,.2f}</div>'
        f'<div style="font-size:11px;font-weight:600;color:{"#34d399" if c>=0 else "#f87171"};">'
        f'{"▲" if c>=0 else "▼"} {abs(c):.2f}%</div></div>'
        for n, p, c in strip_data
    )
    components.html(
        f'<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@600&display=swap" rel="stylesheet">'
        f'<style>*{{margin:0;padding:0;box-sizing:border-box;}}'
        f'.idx-strip{{display:flex;overflow-x:auto;background:rgba(7,7,20,.95);'
        f'border-top:1px solid rgba(139,92,246,.2);border-bottom:1px solid rgba(139,92,246,.2);padding:4px 0;}}'
        f'.idx-cell{{padding:5px 18px;border-right:1px solid rgba(139,92,246,.12);min-width:130px;flex-shrink:0;}}'
        f'.num{{font-family:"JetBrains Mono",monospace;}}</style>'
        f'<div class="idx-strip">'
        f'<div style="padding:0 14px;display:flex;align-items:center;border-right:1px solid rgba(139,92,246,.25);margin-right:4px;">'
        f'<span style="font-size:10px;font-weight:800;color:#8b5cf6;letter-spacing:.15em;">🇮🇳 NSE</span></div>'
        f'{cells}'
        f'<div style="padding:0 14px;display:flex;align-items:center;font-size:9px;color:#4b5563;white-space:nowrap;">'
        f'via yfinance · 15-min delay</div></div>',
        height=60,
    )

# ── Global ticker tape ────────────────────────────────────────────────────
components.html("""
<div class="tradingview-widget-container">
<div class="tradingview-widget-container__widget"></div>
<script type="text/javascript"
  src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
{"symbols":[
  {"proName":"FOREXCOM:SPXUSD","title":"S&P 500"},
  {"proName":"FOREXCOM:NSXUSD","title":"Nasdaq 100"},
  {"proName":"OANDA:XAUUSD","title":"Gold"},
  {"proName":"BITSTAMP:BTCUSD","title":"Bitcoin"},
  {"proName":"FX_IDC:USDINR","title":"USD/INR"}
],"showSymbolLogo":true,"colorTheme":"dark","isTransparent":true,"locale":"in"}
</script></div>""", height=55)

# ── Page header ───────────────────────────────────────────────────────────
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
hcol, bcol = st.columns([5, 1])
with hcol:
    st.markdown(
        f'<div style="font-family:\'Space Grotesk\',sans-serif;font-size:2rem;font-weight:800;'
        f'background:linear-gradient(90deg,{INK} 30%,{VL} 70%,{CY});'
        f'-webkit-background-clip:text;background-clip:text;color:transparent;line-height:1.1;">Live Markets</div>'
        f'<div style="font-size:0.68rem;color:{MUT};letter-spacing:.18em;text-transform:uppercase;margin-top:2px;">'
        f'Premium Market Intelligence · via yfinance</div>',
        unsafe_allow_html=True,
    )
with bcol:
    if st.button("↻  Resync", use_container_width=True, key="resync"):
        st.cache_data.clear()
        st.rerun()

# Status bar
nse_col = MN if nse_open else EM
us_col  = MN if us_open  else MUT
st.markdown(
    f'<div style="display:flex;align-items:center;gap:20px;margin:.6rem 0 .2rem;'
    f'padding:7px 16px;background:{GL};border-radius:10px;border:1px solid {BR};">'
    f'<span style="font-size:.72rem;font-weight:700;color:{nse_col};">● NSE {"Open" if nse_open else "Closed"}</span>'
    f'<span style="font-size:.72rem;font-weight:700;color:{us_col};">● US {"Open" if us_open else "Closed"}</span>'
    f'<span style="font-size:.72rem;font-weight:700;color:{MN};">● Crypto 24/7</span>'
    f'<span style="margin-left:auto;font-size:.66rem;color:{MUT};">'
    f'Last sync: {now_ist.strftime("%I:%M %p IST")}</span></div>',
    unsafe_allow_html=True,
)


# ═════════════════════════════════════════════════════════════════════════
# 1. MARKET PULSE
# ═════════════════════════════════════════════════════════════════════════
sec_label("Market Pulse")

with st.spinner("Loading market breadth…"):
    adv, dec, unch, movers = fetch_breadth_movers()

total   = adv + dec + unch or 1
bull_p  = adv / total * 100
bear_p  = dec / total * 100

if bull_p >= 58:
    sentiment, sent_color, sent_emoji = "BULLISH",  MN, "🟢"
elif bear_p >= 58:
    sentiment, sent_color, sent_emoji = "BEARISH",  EM, "🔴"
else:
    sentiment, sent_color, sent_emoji = "NEUTRAL",  AM, "🟡"

# Gauge needle angle: -80 (bearish) → 0 (neutral) → +80 (bullish)
needle_deg = (bull_p - bear_p) * 0.8
needle_deg = max(-82, min(82, needle_deg))

# Build SVG gauge
needle_rad = math.radians(needle_deg - 90)
nx = 100 + math.cos(needle_rad) * 62
ny = 95  - math.sin(needle_rad) * 62

gauge_svg = _H(f"""
<svg width="200" height="110" viewBox="0 0 200 110" style="display:block;margin:0 auto;">
  <defs>
    <linearGradient id="gArc" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="#f87171"/>
      <stop offset="50%"  stop-color="#fbbf24"/>
      <stop offset="100%" stop-color="#34d399"/>
    </linearGradient>
  </defs>
  <!-- background arc -->
  <path d="M 18,95 A 82,82 0 0,1 182,95"
        fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="14" stroke-linecap="round"/>
  <!-- coloured arc -->
  <path d="M 18,95 A 82,82 0 0,1 182,95"
        fill="none" stroke="url(#gArc)" stroke-width="14" stroke-linecap="round" opacity="0.75"/>
  <!-- zone ticks -->
  <line x1="18"  y1="95" x2="24"  y2="95"  stroke="{EM}" stroke-width="2"/>
  <line x1="182" y1="95" x2="176" y2="95"  stroke="{MN}" stroke-width="2"/>
  <line x1="100" y1="13" x2="100" y2="20"  stroke="{AM}" stroke-width="2"/>
  <!-- needle -->
  <line x1="100" y1="95" x2="{nx:.1f}" y2="{ny:.1f}"
        stroke="{INK}" stroke-width="2.5" stroke-linecap="round"
        style="filter:drop-shadow(0 0 4px {sent_color})"/>
  <circle cx="100" cy="95" r="5" fill="{sent_color}" style="filter:drop-shadow(0 0 6px {sent_color})"/>
  <!-- labels -->
  <text x="12"  y="108" fill="{EM}" font-size="8" font-family="Inter,sans-serif" font-weight="700">BEAR</text>
  <text x="155" y="108" fill="{MN}" font-size="8" font-family="Inter,sans-serif" font-weight="700">BULL</text>
</svg>
""")

pc1, pc2, pc3 = st.columns([1, 1.4, 1])

with pc1:
    st.markdown(
        _H(f"""
        <div class="g rise-in" style="padding:1.2rem;text-align:center;height:100%;min-height:200px;
             display:flex;flex-direction:column;align-items:center;justify-content:center;">
          <div style="font-size:.65rem;color:{MUT};text-transform:uppercase;letter-spacing:.14em;margin-bottom:.5rem;">
            Market Sentiment
          </div>
          {gauge_svg}
          <div style="font-size:1.6rem;font-weight:800;color:{sent_color};letter-spacing:.08em;margin-top:.3rem;">
            {sent_emoji} {sentiment}
          </div>
          <div style="font-size:.72rem;color:{MUT};margin-top:.2rem;">
            {bull_p:.0f}% stocks advancing
          </div>
          <div style="font-size:.6rem;color:#374151;margin-top:.4rem;">Nifty 50 · via yfinance</div>
        </div>"""),
        unsafe_allow_html=True,
    )

with pc2:
    st.markdown(
        _H(f"""
        <div class="g rise-in" style="padding:1.4rem;height:100%;min-height:200px;display:flex;
             flex-direction:column;justify-content:space-between;">
          <div style="font-size:.65rem;color:{MUT};text-transform:uppercase;letter-spacing:.14em;
               margin-bottom:.8rem;">Advance / Decline Ratio</div>

          <!-- A/D bar -->
          <div>
            <div style="display:flex;justify-content:space-between;font-size:.72rem;
                 color:{MUT};margin-bottom:5px;">
              <span style="color:{MN};font-weight:700;">▲ {adv} Advances</span>
              <span style="color:{EM};font-weight:700;">{dec} Declines ▼</span>
            </div>
            <div style="height:14px;border-radius:7px;overflow:hidden;
                 background:rgba(255,255,255,0.05);">
              <div style="height:100%;width:{bull_p:.1f}%;border-radius:7px;
                   background:linear-gradient(90deg,{MN},{CY});
                   box-shadow:0 0 8px {MN}44;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:.68rem;
                 color:{MUT};margin-top:4px;">
              <span>{bull_p:.1f}%</span>
              <span>{bear_p:.1f}%</span>
            </div>
          </div>

          <!-- Breadth grid -->
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:.8rem;">
            <div style="text-align:center;padding:.6rem .4rem;border-radius:10px;
                 background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.18);">
              <div class="num" style="font-size:1.3rem;font-weight:700;color:{MN};">{adv}</div>
              <div style="font-size:.6rem;color:{MUT};margin-top:2px;">UP</div>
            </div>
            <div style="text-align:center;padding:.6rem .4rem;border-radius:10px;
                 background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.18);">
              <div class="num" style="font-size:1.3rem;font-weight:700;color:{EM};">{dec}</div>
              <div style="font-size:.6rem;color:{MUT};margin-top:2px;">DOWN</div>
            </div>
            <div style="text-align:center;padding:.6rem .4rem;border-radius:10px;
                 background:rgba(139,92,246,.08);border:1px solid rgba(139,92,246,.18);">
              <div class="num" style="font-size:1.3rem;font-weight:700;color:{VL};">{unch}</div>
              <div style="font-size:.6rem;color:{MUT};margin-top:2px;">FLAT</div>
            </div>
          </div>
          <div style="font-size:.6rem;color:#374151;margin-top:.6rem;">
            Nifty 50 subset · previous close · via yfinance
          </div>
        </div>"""),
        unsafe_allow_html=True,
    )

with pc3:
    vix_val, vix_chg = fetch_vix()
    vix_txt   = f"{vix_val:.2f}" if vix_val else "—"
    vix_color = EM if (vix_val or 0) > 20 else AM if (vix_val or 0) > 15 else MN
    vix_label = "HIGH FEAR" if (vix_val or 0) > 20 else "CAUTION" if (vix_val or 0) > 15 else "LOW FEAR"

    indices_data = fetch_indices()
    nifty_d = next((x for x in indices_data if "Nifty 50" in x["name"]), None)
    mkt_chg = nifty_d["chg"] if nifty_d else 0

    nifty_hi, nifty_lo, pct_hi = fetch_nifty_52w()
    hi_str  = f"{nifty_hi:,.0f}" if nifty_hi else "—"
    lo_str  = f"{nifty_lo:,.0f}" if nifty_lo else "—"
    if pct_hi is not None:
        pct_str = f"Currently {abs(pct_hi):.1f}% below 52W high" if pct_hi < -0.5 else "Near / at 52W high"
    else:
        pct_str = "^NSEI · via yfinance"

    st.markdown(
        _H(f"""
        <div class="g rise-in" style="padding:1.4rem;height:100%;min-height:200px;
             display:flex;flex-direction:column;justify-content:space-between;">
          <div style="font-size:.65rem;color:{MUT};text-transform:uppercase;
               letter-spacing:.14em;margin-bottom:.6rem;">Market Stats</div>

          <!-- VIX -->
          <div style="padding:.7rem 1rem;border-radius:12px;
               background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.15);
               margin-bottom:.6rem;">
            <div style="font-size:.65rem;color:{MUT};margin-bottom:2px;">India VIX · Fear Index</div>
            <div style="display:flex;align-items:baseline;gap:8px;">
              <span class="num" style="font-size:1.8rem;font-weight:700;color:{vix_color};">{vix_txt}</span>
              <span style="font-size:.7rem;font-weight:700;color:{vix_color};">{vix_label}</span>
            </div>
            <div style="font-size:.65rem;color:{MUT};margin-top:2px;">via yfinance (^INDIAVIX)</div>
          </div>

          <!-- Market today -->
          <div style="padding:.7rem 1rem;border-radius:12px;
               background:rgba(139,92,246,.07);border:1px solid {BR};margin-bottom:.6rem;">
            <div style="font-size:.65rem;color:{MUT};margin-bottom:2px;">Nifty 50 Today</div>
            <div class="num" style="font-size:1.5rem;font-weight:700;
                 color:{"#34d399" if mkt_chg>=0 else "#f87171"};">
              {"▲" if mkt_chg>=0 else "▼"} {abs(mkt_chg):.2f}%
            </div>
          </div>

          <!-- Nifty 52W Hi/Lo from yfinance -->
          <div style="padding:.65rem .9rem;border-radius:10px;
               background:rgba(34,211,238,.05);border:1px solid rgba(34,211,238,.12);">
            <div style="font-size:.62rem;color:{MUT};margin-bottom:.4rem;">📅 Nifty 52W Range</div>
            <div style="display:flex;justify-content:space-between;align-items:flex-end;">
              <div>
                <div class="num" style="font-size:.85rem;font-weight:700;color:{MN};">{hi_str}</div>
                <div style="font-size:.6rem;color:{MUT};">52W High</div>
              </div>
              <div style="text-align:right;">
                <div class="num" style="font-size:.85rem;font-weight:700;color:{EM};">{lo_str}</div>
                <div style="font-size:.6rem;color:{MUT};">52W Low</div>
              </div>
            </div>
            <div style="font-size:.6rem;color:#374151;margin-top:.4rem;">{pct_str}</div>
          </div>
        </div>"""),
        unsafe_allow_html=True,
    )


# ═════════════════════════════════════════════════════════════════════════
# 2. INDEX SNAPSHOT with Sparklines
# ═════════════════════════════════════════════════════════════════════════
sec_label("Index Snapshot")

indices_data = fetch_indices()
icols = st.columns(4)
for col, idx in zip(icols, indices_data):
    spark = spark_svg(idx["spark"])
    chg_c = MN if idx["chg"] >= 0 else EM
    with col:
        st.markdown(
            _H(f"""
            <div class="g" style="padding:1rem 1.1rem;border-top:3px solid {idx['color']};">
              <div style="font-size:.68rem;color:{MUT};font-weight:700;
                   text-transform:uppercase;letter-spacing:.1em;margin-bottom:.4rem;">
                {idx['name']}
              </div>
              <div class="num" style="font-size:1.4rem;font-weight:700;color:{INK};">
                {idx['price']:,.2f}
              </div>
              <div style="display:flex;align-items:center;justify-content:space-between;margin-top:.3rem;">
                <span style="font-size:.8rem;font-weight:700;color:{chg_c};">
                  {"▲" if idx['chg']>=0 else "▼"} {abs(idx['chg']):.2f}%
                </span>
                {spark}
              </div>
              <div style="font-size:.6rem;color:#374151;margin-top:.4rem;">via yfinance · 5d sparkline</div>
            </div>"""),
            unsafe_allow_html=True,
        )


# ═════════════════════════════════════════════════════════════════════════
# 3. SECTOR HEATMAP
# ═════════════════════════════════════════════════════════════════════════
sec_label("Sector Heatmap · NSE Indices via yfinance")

sector_data = fetch_sectors()

# Build 4x2 heatmap grid
def sector_tile_html(s: dict) -> str:
    chg     = s["chg"]
    ok      = s.get("ok", True)
    mag     = min(abs(chg) / 3, 1)   # 0–1 intensity
    if not ok or chg == 0:
        bg = "rgba(55,65,81,0.5)"
        bd = "rgba(107,114,128,0.3)"
        tc = MUT
    elif chg > 0:
        bg = f"rgba(52,211,153,{0.08 + mag*0.25:.2f})"
        bd = f"rgba(52,211,153,{0.2 + mag*0.3:.2f})"
        tc = MN
    else:
        bg = f"rgba(248,113,113,{0.08 + mag*0.25:.2f})"
        bd = f"rgba(248,113,113,{0.2 + mag*0.3:.2f})"
        tc = EM
    sign = "▲" if chg > 0 else ("▼" if chg < 0 else "–")
    chg_str = f"{sign} {abs(chg):.2f}%" if ok else "N/A"
    return _H(f"""
    <div style="background:{bg};border:1px solid {bd};border-radius:14px;
         padding:.85rem .7rem;text-align:center;transition:transform .2s;min-height:80px;">
      <div style="font-size:1.3rem;margin-bottom:.2rem;">{s['icon']}</div>
      <div style="font-size:.72rem;font-weight:700;color:{INK};margin-bottom:.2rem;">{s['name']}</div>
      <div class="num" style="font-size:.95rem;font-weight:700;color:{tc};">{chg_str}</div>
    </div>""")

row1_html = "".join(sector_tile_html(s) for s in sector_data[:4])
row2_html = "".join(sector_tile_html(s) for s in sector_data[4:])

for row_html in [row1_html, row2_html]:
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:10px;">'
        f'{row_html}</div>',
        unsafe_allow_html=True,
    )
st.caption("NSE sector indices: ^CNXBANK · ^CNXIT · ^CNXPHARMA · ^CNXAUTO · ^CNXFMCG · ^CNXENERGY · ^CNXMETAL · ^CNXREALTY")


# ═════════════════════════════════════════════════════════════════════════
# 4. FII / DII ACTIVITY
# ═════════════════════════════════════════════════════════════════════════
sec_label("FII / DII Activity · Previous Trading Day")

fii_dii = fetch_fii_dii()

if fii_dii:
    fd    = fii_dii
    fd_date = fd.get("date", "previous trading day")

    fii_net_c = MN if fd["fii_net"] >= 0 else EM
    dii_net_c = MN if fd["dii_net"] >= 0 else EM
    fii_sign  = "▲ Net Buy" if fd["fii_net"] >= 0 else "▼ Net Sell"
    dii_sign  = "▲ Net Buy" if fd["dii_net"] >= 0 else "▼ Net Sell"

    max_flow = max(fd["fii_buy"], fd["fii_sell"], fd["dii_buy"], fd["dii_sell"], 1)

    def bar_pct(v):
        return min(v / max_flow * 100, 100)

    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown(
            _H(f"""
            <div class="g" style="padding:1.2rem 1.4rem;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
                <div>
                  <div style="font-size:.68rem;color:{MUT};text-transform:uppercase;
                       letter-spacing:.12em;">FII / FPI Activity</div>
                  <div style="font-size:.62rem;color:#374151;margin-top:2px;">
                    Foreign Institutional Investors · {fd_date}
                  </div>
                </div>
                <div style="font-size:1.1rem;font-weight:800;color:{fii_net_c};">
                  {fii_sign}<br>
                  <span class="num" style="font-size:.9rem;">{_cr(fd["fii_net"])}</span>
                </div>
              </div>
              <!-- Buy bar -->
              <div style="margin-bottom:.6rem;">
                <div style="display:flex;justify-content:space-between;font-size:.7rem;color:{MUT};margin-bottom:3px;">
                  <span>Buy</span><span class="num" style="color:{MN};">{_cr(fd["fii_buy"])}</span>
                </div>
                <div style="height:8px;border-radius:4px;overflow:hidden;background:rgba(255,255,255,.06);">
                  <div style="height:100%;width:{bar_pct(fd['fii_buy']):.0f}%;
                       background:linear-gradient(90deg,{MN},{CY});border-radius:4px;"></div>
                </div>
              </div>
              <!-- Sell bar -->
              <div>
                <div style="display:flex;justify-content:space-between;font-size:.7rem;color:{MUT};margin-bottom:3px;">
                  <span>Sell</span><span class="num" style="color:{EM};">{_cr(fd["fii_sell"])}</span>
                </div>
                <div style="height:8px;border-radius:4px;overflow:hidden;background:rgba(255,255,255,.06);">
                  <div style="height:100%;width:{bar_pct(fd['fii_sell']):.0f}%;
                       background:linear-gradient(90deg,{EM},{AM});border-radius:4px;"></div>
                </div>
              </div>
            </div>"""),
            unsafe_allow_html=True,
        )
    with fc2:
        st.markdown(
            _H(f"""
            <div class="g" style="padding:1.2rem 1.4rem;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
                <div>
                  <div style="font-size:.68rem;color:{MUT};text-transform:uppercase;
                       letter-spacing:.12em;">DII Activity</div>
                  <div style="font-size:.62rem;color:#374151;margin-top:2px;">
                    Domestic Institutional Investors · {fd_date}
                  </div>
                </div>
                <div style="font-size:1.1rem;font-weight:800;color:{dii_net_c};">
                  {dii_sign}<br>
                  <span class="num" style="font-size:.9rem;">{_cr(fd["dii_net"])}</span>
                </div>
              </div>
              <div style="margin-bottom:.6rem;">
                <div style="display:flex;justify-content:space-between;font-size:.7rem;color:{MUT};margin-bottom:3px;">
                  <span>Buy</span><span class="num" style="color:{MN};">{_cr(fd["dii_buy"])}</span>
                </div>
                <div style="height:8px;border-radius:4px;overflow:hidden;background:rgba(255,255,255,.06);">
                  <div style="height:100%;width:{bar_pct(fd['dii_buy']):.0f}%;
                       background:linear-gradient(90deg,{MN},{CY});border-radius:4px;"></div>
                </div>
              </div>
              <div>
                <div style="display:flex;justify-content:space-between;font-size:.7rem;color:{MUT};margin-bottom:3px;">
                  <span>Sell</span><span class="num" style="color:{EM};">{_cr(fd["dii_sell"])}</span>
                </div>
                <div style="height:8px;border-radius:4px;overflow:hidden;background:rgba(255,255,255,.06);">
                  <div style="height:100%;width:{bar_pct(fd['dii_sell']):.0f}%;
                       background:linear-gradient(90deg,{EM},{AM});border-radius:4px;"></div>
                </div>
              </div>
            </div>"""),
            unsafe_allow_html=True,
        )
    st.caption("Source: NSE India API · nseindia.com/api/fiidiiTradeReact · previous trading session")
else:
    st.markdown(
        _H(f"""
        <div class="g" style="padding:1.2rem 1.6rem;display:flex;align-items:center;gap:16px;">
          <div style="font-size:2rem;">📡</div>
          <div>
            <div style="font-size:.85rem;font-weight:600;color:{INK};">FII/DII data temporarily unavailable</div>
            <div style="font-size:.75rem;color:{MUT};margin-top:4px;">
              NSE API requires a session cookie. Check live data at
              <a href="https://www.nseindia.com/market-data/live-market-statistics" target="_blank"
                 style="color:{CY};">nseindia.com</a>
            </div>
          </div>
        </div>"""),
        unsafe_allow_html=True,
    )


# ═════════════════════════════════════════════════════════════════════════
# 5. TOP MOVERS
# ═════════════════════════════════════════════════════════════════════════
sec_label("Top Movers · Nifty 50 · Previous Close")

gainers = [m for m in movers if m["chg"] > 0][:5]
losers  = [m for m in reversed(movers) if m["chg"] < 0][:5]

mc1, mc2 = st.columns(2)
with mc1:
    st.markdown(f'<div style="font-size:.72rem;font-weight:700;color:{MN};text-transform:uppercase;'
                f'letter-spacing:.12em;margin-bottom:.5rem;">🟢 Top Gainers</div>',
                unsafe_allow_html=True)
    if gainers:
        for g in gainers:
            st.markdown(
                _H(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                     padding:9px 14px;border-radius:10px;margin-bottom:5px;
                     background:rgba(52,211,153,.07);border:1px solid rgba(52,211,153,.18);">
                  <span style="font-size:.82rem;font-weight:600;color:{INK};
                        font-family:'JetBrains Mono',monospace;">{g['name']}</span>
                  <div style="text-align:right;">
                    <span class="num" style="font-size:.9rem;font-weight:700;color:{MN};">
                      ▲ {g['chg']:.2f}%
                    </span>
                    <div class="num" style="font-size:.65rem;color:{MUT};">₹{g['price']:,.1f}</div>
                  </div>
                </div>"""),
                unsafe_allow_html=True,
            )
    else:
        st.caption("No data available.")

with mc2:
    st.markdown(f'<div style="font-size:.72rem;font-weight:700;color:{EM};text-transform:uppercase;'
                f'letter-spacing:.12em;margin-bottom:.5rem;">🔴 Top Losers</div>',
                unsafe_allow_html=True)
    if losers:
        for lo in losers:
            st.markdown(
                _H(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                     padding:9px 14px;border-radius:10px;margin-bottom:5px;
                     background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.18);">
                  <span style="font-size:.82rem;font-weight:600;color:{INK};
                        font-family:'JetBrains Mono',monospace;">{lo['name']}</span>
                  <div style="text-align:right;">
                    <span class="num" style="font-size:.9rem;font-weight:700;color:{EM};">
                      ▼ {abs(lo['chg']):.2f}%
                    </span>
                    <div class="num" style="font-size:.65rem;color:{MUT};">₹{lo['price']:,.1f}</div>
                  </div>
                </div>"""),
                unsafe_allow_html=True,
            )
    else:
        st.caption("No data available.")

st.caption("Nifty 50 constituents · vs previous close · via yfinance · 15-min delay")


# ═════════════════════════════════════════════════════════════════════════
# 6. EXISTING: INDICES + COMMODITIES FLIP CARDS
# ═════════════════════════════════════════════════════════════════════════

def render_flip_kpi(label, value_str, pct_change, accent="#8b5cf6"):
    arrow    = "▲" if pct_change >= 0 else "▼"
    b_bg = "rgba(52,211,153,.15)" if pct_change >= 0 else "rgba(248,113,113,.15)"
    b_fg = MN if pct_change >= 0 else EM
    b_bd = "rgba(52,211,153,.3)"  if pct_change >= 0 else "rgba(248,113,113,.3)"
    components.html(f"""
<style>
body{{margin:0;padding:0;background:transparent;overflow:hidden;font-family:Inter,sans-serif;}}
.fc{{perspective:1000px;height:112px;}}
.fi{{position:relative;width:100%;height:100%;transition:transform .5s cubic-bezier(.4,0,.2,1);transform-style:preserve-3d;}}
.fc:hover .fi{{transform:rotateY(10deg);}}
.ff{{position:absolute;width:100%;height:100%;backface-visibility:hidden;border-radius:12px;
     padding:14px 16px;border:1px solid rgba(139,92,246,.18);border-top:2px solid {accent};
     background:rgba(17,17,48,.6);box-sizing:border-box;backdrop-filter:blur(14px);}}
</style>
<div class="fc">
<div class="fi">
<div class="ff">
  <div style="font-size:9px;font-weight:700;color:#8b93a7;letter-spacing:.08em;">{label}</div>
  <div style="font-size:1.35rem;font-weight:700;color:#f0f0ff;margin:6px 0;font-family:monospace;">{value_str}</div>
  <div style="background:{b_bg};color:{b_fg};border:1px solid {b_bd};padding:3px 9px;
       border-radius:6px;font-size:.78rem;font-weight:700;display:inline-block;">
    {arrow} {abs(pct_change):.2f}%
  </div>
  <div style="font-size:9px;color:#374151;margin-top:5px;">via yfinance</div>
</div>
</div>
</div>""", height=124)


sec_label("Global Indices")
c1, c2, c3, c4 = st.columns(4)
nifty_p, nifty_c   = fetch_two("^NSEI")
sensex_p, sensex_c = fetch_two("^BSESN")
bank_p,   bank_c   = fetch_two("^NSEBANK")
nasdaq_p, nasdaq_c = fetch_two("^IXIC")
with c1: render_flip_kpi("Nifty 50",   f"{nifty_p:,.2f}",  nifty_c,  VL)
with c2: render_flip_kpi("Sensex",     f"{sensex_p:,.2f}", sensex_c, CY)
with c3: render_flip_kpi("Bank Nifty", f"{bank_p:,.2f}",   bank_c,   MN)
with c4: render_flip_kpi("Nasdaq",     f"{nasdaq_p:,.2f}", nasdaq_c, VL)

sec_label("Commodities & Currencies")
c1, c2, c3, c4 = st.columns(4)
gold_p,  gold_c  = fetch_two("GC=F")
crude_p, crude_c = fetch_two("CL=F")
inr_p,   inr_c   = fetch_two("INR=X")
btc_p,   btc_c   = fetch_two("BTC-USD")
with c1: render_flip_kpi("Gold (USD/oz)", f"${gold_p:,.2f}",  gold_c,  AM)
with c2: render_flip_kpi("Crude Oil",     f"${crude_p:,.2f}", crude_c, AM)
with c3: render_flip_kpi("USD/INR",       f"₹{inr_p:,.4f}",  inr_c,   MN)
with c4: render_flip_kpi("Bitcoin",       f"${btc_p:,.0f}",   btc_c,   EM)


# ═════════════════════════════════════════════════════════════════════════
# 7. SMART MARKET INSIGHTS
# ═════════════════════════════════════════════════════════════════════════
sec_label("Smart Market Insights · Public data · No upload required")

# Pre-fetch all needed data (all cached — no extra network calls)
_sm_indices  = fetch_indices()
_sm_nifty    = next((x for x in _sm_indices if "Nifty 50" in x["name"]), None)
_sm_lc_chg   = _sm_nifty["chg"] if _sm_nifty else 0.0
_, _sm_mid_chg  = fetch_two("^NSEMDCP50")
_, _sm_sp_chg = fetch_two("^GSPC")
_sm_vix, _   = fetch_vix()

# Sort sectors for bars
_ok_secs     = [s for s in sector_data if s.get("ok")]
_sorted_secs = sorted(_ok_secs, key=lambda x: x["chg"], reverse=True)
_top3        = _sorted_secs[:3]
_bot_raw     = list(reversed(_sorted_secs))
_bot3        = [s for s in _bot_raw if s not in _top3][:3]

ins_c1, ins_c2 = st.columns([1.15, 1])

with ins_c1:
    st.markdown(
        f'<div style="font-size:.7rem;font-weight:700;color:{MUT};text-transform:uppercase;'
        f'letter-spacing:.12em;margin-bottom:.7rem;">📊 Sector Performance Today</div>',
        unsafe_allow_html=True,
    )

    def _sec_bar(sec: dict, is_gain: bool) -> str:
        chg  = sec["chg"]
        col  = MN if is_gain else EM
        bg   = "rgba(52,211,153,.07)" if is_gain else "rgba(248,113,113,.07)"
        bd   = "rgba(52,211,153,.18)" if is_gain else "rgba(248,113,113,.18)"
        bw   = min(abs(chg) / 3 * 100, 100)
        sign = "▲" if chg > 0 else "▼"
        return _H(f"""
        <div style="background:{bg};border:1px solid {bd};border-radius:8px;
             padding:7px 11px;margin-bottom:6px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <span style="font-size:.76rem;font-weight:600;color:{INK};">{sec['icon']} {sec['name']}</span>
            <span class="num" style="font-size:.8rem;font-weight:700;color:{col};">
              {sign} {abs(chg):.2f}%
            </span>
          </div>
          <div style="height:4px;border-radius:2px;background:rgba(255,255,255,.05);">
            <div style="height:100%;width:{bw:.0f}%;border-radius:2px;
                 background:{col};opacity:.75;"></div>
          </div>
        </div>""")

    bars_html = ""
    if _top3:
        bars_html += (f'<div style="font-size:.62rem;color:{MN};font-weight:700;'
                      f'letter-spacing:.08em;margin-bottom:3px;">▲ TOP GAINERS</div>')
        for s in _top3:
            bars_html += _sec_bar(s, True)
    if _bot3:
        bars_html += (f'<div style="font-size:.62rem;color:{EM};font-weight:700;'
                      f'letter-spacing:.08em;margin:.6rem 0 3px;">▼ WORST PERFORMERS</div>')
        for s in _bot3:
            bars_html += _sec_bar(s, False)

    st.markdown(
        bars_html or f'<div style="color:{MUT};font-size:.8rem;">No sector data available.</div>',
        unsafe_allow_html=True,
    )
    st.caption("NSE sector indices · ^CNXBANK ^CNXIT ^CNXPHARMA ^CNXAUTO ^CNXFMCG ^CNXENERGY ^CNXMETAL ^CNXREALTY · via yfinance")

with ins_c2:
    st.markdown(
        f'<div style="font-size:.7rem;font-weight:700;color:{MUT};text-transform:uppercase;'
        f'letter-spacing:.12em;margin-bottom:.7rem;">💡 Market Mood</div>',
        unsafe_allow_html=True,
    )

    # Money Flow label
    if _sm_lc_chg > 0 and _sm_mid_chg > _sm_lc_chg:
        _mf_label, _mf_color, _mf_emoji = "Risk-On · Mid beating Large", MN,  "🔥"
    elif _sm_lc_chg > 0:
        _mf_label, _mf_color, _mf_emoji = "Large Cap led rally",          CY,  "💹"
    elif _sm_lc_chg < 0 and _sm_mid_chg < _sm_lc_chg:
        _mf_label, _mf_color, _mf_emoji = "Risk-Off · Broad selloff",     EM,  "🔻"
    else:
        _mf_label, _mf_color, _mf_emoji = "Mixed / Defensive tilt",       AM,  "⚡"

    # VIX label
    _vl  = "LOW"    if (_sm_vix or 0) < 15 else "MEDIUM" if (_sm_vix or 0) < 20 else "HIGH"
    _vc  = MN       if (_sm_vix or 0) < 15 else AM       if (_sm_vix or 0) < 20 else EM
    _vt  = f"{_sm_vix:.1f}" if _sm_vix else "—"

    # Global cue
    _sp_dir = "▲ Positive" if _sm_sp_chg >= 0 else "▼ Negative"
    _sp_col = MN if _sm_sp_chg >= 0 else EM

    st.markdown(
        _H(f"""
        <div style="display:flex;flex-direction:column;gap:8px;">
          <div class="g" style="padding:.8rem 1rem;">
            <div style="font-size:.62rem;color:{MUT};text-transform:uppercase;
                 letter-spacing:.1em;margin-bottom:.3rem;">💰 Money Flow</div>
            <div style="font-size:.88rem;font-weight:700;color:{_mf_color};">
              {_mf_emoji} {_mf_label}
            </div>
            <div class="num" style="font-size:.7rem;color:{MUT};margin-top:3px;">
              Large: {_sm_lc_chg:+.2f}% · Mid: {_sm_mid_chg:+.2f}%
            </div>
            <div style="font-size:.6rem;color:#374151;margin-top:2px;">
              ^NSEI vs ^NSEMDCP50 · via yfinance
            </div>
          </div>
          <div class="g" style="padding:.8rem 1rem;">
            <div style="font-size:.62rem;color:{MUT};text-transform:uppercase;
                 letter-spacing:.1em;margin-bottom:.3rem;">📉 Volatility</div>
            <div style="display:flex;align-items:baseline;gap:8px;">
              <span class="num" style="font-size:1.2rem;font-weight:700;color:{_vc};">{_vt}</span>
              <span style="font-size:.78rem;font-weight:700;color:{_vc};">{_vl} FEAR</span>
            </div>
            <div style="font-size:.6rem;color:#374151;margin-top:2px;">
              India VIX · ^INDIAVIX · via yfinance
            </div>
          </div>
          <div class="g" style="padding:.8rem 1rem;">
            <div style="font-size:.62rem;color:{MUT};text-transform:uppercase;
                 letter-spacing:.1em;margin-bottom:.3rem;">🌍 Global Cue</div>
            <div style="font-size:.88rem;font-weight:700;color:{_sp_col};">{_sp_dir}</div>
            <div class="num" style="font-size:.7rem;color:{MUT};margin-top:3px;">
              S&P 500: {_sm_sp_chg:+.2f}%
            </div>
            <div style="font-size:.6rem;color:#374151;margin-top:2px;">
              ^GSPC · US market · via yfinance
            </div>
          </div>
        </div>"""),
        unsafe_allow_html=True,
    )

# ── Plain-English summary ────────────────────────────────────────────────
_summary: list[str] = []

if sentiment == "BULLISH":
    _summary.append(
        f"Markets are <b style='color:{MN}'>positive</b> today — "
        f"{bull_p:.0f}% of Nifty 50 stocks are advancing."
    )
elif sentiment == "BEARISH":
    _summary.append(
        f"Markets are <b style='color:{EM}'>under pressure</b> — "
        f"{bear_p:.0f}% of Nifty 50 stocks are declining."
    )
else:
    _summary.append(
        f"Markets are <b style='color:{AM}'>mixed</b> today — "
        f"bulls and bears are broadly balanced."
    )

if _ok_secs:
    _best  = max(_ok_secs, key=lambda x: x["chg"])
    _worst = min(_ok_secs, key=lambda x: x["chg"])
    if abs(_best["chg"]) > 0.05 or abs(_worst["chg"]) > 0.05:
        _summary.append(
            f"<b style='color:{MN}'>{_best['icon']} {_best['name']}</b> is leading "
            f"({_best['chg']:+.2f}%); "
            f"<b style='color:{EM}'>{_worst['icon']} {_worst['name']}</b> is lagging "
            f"({_worst['chg']:+.2f}%)."
        )

if _sm_vix:
    if _sm_vix < 15:
        _summary.append(
            f"India VIX at <b style='color:{MN}'>{_sm_vix:.1f}</b> — "
            f"low volatility, stable market conditions."
        )
    elif _sm_vix < 20:
        _summary.append(
            f"India VIX at <b style='color:{AM}'>{_sm_vix:.1f}</b> — "
            f"moderate volatility, some caution warranted."
        )
    else:
        _summary.append(
            f"India VIX at <b style='color:{EM}'>{_sm_vix:.1f}</b> — "
            f"elevated fear, choppy conditions likely."
        )

_sum_html = "".join(
    f'<div style="font-size:.84rem;color:{INK};line-height:1.7;margin-bottom:.25rem;">• {l}</div>'
    for l in _summary
)

st.markdown(
    _H(f"""
    <div class="g" style="padding:1.2rem 1.4rem;margin-top:.6rem;border-left:3px solid {VL};">
      <div style="font-size:.68rem;color:{MUT};text-transform:uppercase;
           letter-spacing:.12em;margin-bottom:.7rem;">
        📝 What This Means · Auto-generated from live data
      </div>
      {_sum_html}
      <div style="font-size:.62rem;color:#374151;margin-top:.8rem;">
        Sources: Nifty 50 breadth · NSE sector indices · India VIX · S&P 500 ·
        All via yfinance · No CAS upload required
      </div>
    </div>"""),
    unsafe_allow_html=True,
)

st.markdown(
    f'<div style="margin-top:1.4rem;font-size:.65rem;color:#374151;'
    f'padding:8px 14px;border-radius:8px;background:rgba(17,17,48,.4);">'
    f'📊 Data sources: yfinance (NSE/BSE indices, sectors, commodities, VIX, S&P 500) · '
    f'NSE India API (FII/DII flows) · '
    f'All market data carries 15-min delay · '
    f'Not financial advice.</div>',
    unsafe_allow_html=True,
)
