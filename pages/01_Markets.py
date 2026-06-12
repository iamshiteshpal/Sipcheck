import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
import streamlit.components.v1 as components
import plotly.graph_objects as go

def get_market_status():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    weekday = now.weekday()
    time_val = now.hour * 60 + now.minute
    nse_open = weekday < 5 and (9*60+15) <= time_val <= (15*60+30)
    us_open = weekday < 5 and (19*60+30) <= time_val <= (2*60+24*60)
    return {
        "nse": ("● NSE Open", "#20C997") if nse_open else ("● NSE Closed", "#FF4D4D"),
        "us": ("● US Open", "#20C997") if us_open else ("● US Closed", "#6B7280"),
        "crypto": ("● 24/7 Live", "#20C997")
    }

status = get_market_status()

st.set_page_config(page_title="Markets — CAS 360", page_icon="📈", layout="wide")
from sidebar_v2 import render_sidebar
render_sidebar()


# ==========================================
# 1. DATA FETCHING & INDICATOR MATH
# ==========================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_market_data(ticker, period="1y"):
    try:
        df = yf.Ticker(ticker).history(period=period)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None

@st.cache_data(ttl=60, show_spinner=False)
def get_latest_metrics(ticker):
    df = fetch_market_data(ticker, period="5d")
    if df is None: return 0.0, 0.0
    try:
        last_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2] if len(df) > 1 else last_close
        pct_change = ((last_close - prev_close) / prev_close) * 100
        return float(last_close), float(pct_change)
    except Exception:
        return 0.0, 0.0

def calculate_technical_summary(full_df, display_df):
    if full_df is None or len(full_df) < 30: return None
    
    close_full = full_df['Close']
    
    # RSI Calculation
    delta = close_full.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_series = 100 - (100 / (1 + rs))
    
    # MACD Calculation
    exp1 = close_full.ewm(span=12, adjust=False).mean()
    exp2 = close_full.ewm(span=26, adjust=False).mean()
    macd_series = exp1 - exp2
    signal_series = macd_series.ewm(span=9, adjust=False).mean()
    macd_hist = macd_series - signal_series
    
    # Slice to display timeframe
    close_display = display_df['Close']
    display_rsi = rsi_series.loc[display_df.index]
    display_macd = macd_series.loc[display_df.index]
    display_signal = signal_series.loc[display_df.index]
    display_hist = macd_hist.loc[display_df.index]
    
    return {
        "rsi_latest": display_rsi.iloc[-1], 
        "macd_latest": display_macd.iloc[-1],
        "high": close_display.max(), "low": close_display.min(),
        "history": display_df.tail(3)[['Close']].copy(),
        "rsi_series": display_rsi,
        "macd_series": display_macd,
        "signal_series": display_signal,
        "hist_series": display_hist
    }

# ==========================================
# 2. NEON CYBERPUNK UI (Glassmorphism)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

#MainMenu {visibility:hidden;} footer {visibility:hidden;}

/* Deep Space Background */
.stApp { background: #0B0914; color: #E2E8F0; font-family: 'Inter', sans-serif !important; }
section[data-testid="stSidebar"] { background: #0B0914; border-right: 1px solid rgba(168, 85, 247, 0.2); }
.block-container { padding: 0rem 2rem 2rem 2rem; max-width: 100%; }

/* Glassmorphism KPI Cards */
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

/* Neon Badges */
.badge-up { background: rgba(32, 201, 151, 0.15); color: #20C997; border: 1px solid rgba(32, 201, 151, 0.3); padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block;}
.badge-down { background: rgba(255, 77, 77, 0.15); color: #FF4D4D; border: 1px solid rgba(255, 77, 77, 0.3); padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block;}
.badge-neutral { background: rgba(168, 85, 247, 0.15); color: #D8B4FE; border: 1px solid rgba(168, 85, 247, 0.3); padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; display: inline-block;}

/* Glowing Section Labels */
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

/* Custom Cyber Button */
.stButton>button { border: 1px solid rgba(168, 85, 247, 0.5) !important; background: rgba(30, 25, 45, 0.8) !important; color: #D8B4FE !important; font-weight: 500 !important; border-radius: 8px !important; transition: all 0.3s; box-shadow: 0 0 10px rgba(168, 85, 247, 0.1); }
.stButton>button:hover { border-color: #A855F7 !important; color: #FFF !important; box-shadow: 0 0 15px rgba(168, 85, 247, 0.6); }

/* Tech Panel Custom CSS */
.tech-panel { background: rgba(30, 25, 45, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 12px; padding: 20px; height: 100%; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);}
.tech-row { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(168, 85, 247, 0.15); padding: 12px 0; }
.tech-row:last-child { border-bottom: none; }
.tech-label { color: #94A3B8; font-size: 0.85rem; font-weight: 500; }
.tech-val { color: #F8FAFC; font-weight: 600; font-size: 0.95rem;}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] { background-color: rgba(30, 25, 45, 0.4); border-radius: 8px; padding: 5px; gap: 10px; }
.stTabs [data-baseweb="tab"] { color: #94A3B8; font-weight: 600; border-radius: 6px; padding: 8px 16px; }
.stTabs [aria-selected="true"] { background-color: rgba(168, 85, 247, 0.2) !important; color: #D8B4FE !important; border-bottom: 2px solid #A855F7 !important;}

/* Pulse animation */
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.85); }
}
.pulse-dot { animation: pulse-dot 2s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)

def render_kpi(label, value_str, pct_change,
               border_color="#A855F7", ticker=None):
    arrow = "▲" if pct_change >= 0 else "▼"
    badge_bg = "rgba(32,201,151,0.15)" if pct_change >= 0 else "rgba(255,77,77,0.15)"
    badge_fg = "#20C997" if pct_change >= 0 else "#FF4D4D"
    badge_bd = "rgba(32,201,151,0.3)" if pct_change >= 0 else "rgba(255,77,77,0.3)"

    detail_html = ""
    if ticker:
        try:
            t = yf.Ticker(ticker)
            fi = t.fast_info
            vol = fi.three_month_average_volume or 0
            high52 = fi.year_high or 0
            low52 = fi.year_low or 0
            hist = t.history(period="8d")
            week_chg = 0
            if len(hist) >= 6:
                week_chg = ((float(hist['Close'].iloc[-1]) - float(hist['Close'].iloc[-6])) /
                            float(hist['Close'].iloc[-6]) * 100)
            vol_str = (f"{vol/1e7:.1f}Cr" if vol > 1e7 else f"{vol/1e5:.1f}L" if vol > 1e5 else str(int(vol)))
            wc = "#20C997" if week_chg >= 0 else "#FF4D4D"
            wa = "▲" if week_chg >= 0 else "▼"
            sc = "#20C997" if pct_change >= 0 else "#FF4D4D"
            st_text = "BULLISH" if pct_change >= 0 else "BEARISH"
            row = "display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid rgba(168,85,247,0.15);"
            detail_html = (
                f"<div style='font-size:11px;font-weight:700;color:#D8B4FE;margin-bottom:8px;'>{label}</div>"
                f"<div style='{row}'><span style='font-size:10px;color:#94A3B8;'>52W High</span><span style='font-size:11px;color:#20C997;font-weight:600;'>{high52:,.2f}</span></div>"
                f"<div style='{row}'><span style='font-size:10px;color:#94A3B8;'>52W Low</span><span style='font-size:11px;color:#FF4D4D;font-weight:600;'>{low52:,.2f}</span></div>"
                f"<div style='{row}'><span style='font-size:10px;color:#94A3B8;'>Week chg</span><span style='font-size:11px;color:{wc};font-weight:600;'>{wa} {abs(week_chg):.2f}%</span></div>"
                f"<div style='display:flex;justify-content:space-between;padding:4px 0;'><span style='font-size:10px;color:#94A3B8;'>Avg Vol</span><span style='font-size:11px;color:#F8FAFC;font-weight:600;'>{vol_str}</span></div>"
                f"<div style='margin-top:8px;padding:5px 8px;border-radius:6px;background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.2);'>"
                f"<span style='font-size:9px;color:#94A3B8;'>SIGNAL &middot; </span>"
                f"<span style='font-size:10px;font-weight:700;color:{sc};'>{st_text} TODAY</span></div>"
            )
        except Exception:
            detail_html = "<div style='color:#94A3B8;font-size:11px;padding:10px 0;text-align:center;'>Loading details...</div>"

    components.html(f"""
<style>
body{{margin:0;padding:0;background:transparent;overflow:hidden;font-family:Inter,sans-serif;}}
.fc{{perspective:1000px;height:128px;cursor:pointer;}}
.fi{{position:relative;width:100%;height:100%;transition:transform 0.55s cubic-bezier(0.4,0,0.2,1);transform-style:preserve-3d;}}
.fc.flipped .fi{{transform:rotateY(180deg);}}
.ff,.fb{{position:absolute;width:100%;height:100%;backface-visibility:hidden;-webkit-backface-visibility:hidden;border-radius:12px;padding:14px 16px;border:1px solid rgba(168,85,247,0.2);border-top:2px solid {border_color};background:rgba(30,25,45,0.97);box-sizing:border-box;}}
.fb{{transform:rotateY(180deg);background:rgba(20,15,40,0.99);}}
</style>
<div class="fc" onclick="this.classList.toggle('flipped')" title="Click to see details">
<div class="fi">
<div class="ff">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
<span style="font-size:9px;font-weight:700;color:#94A3B8;letter-spacing:0.08em;">{label}</span>
<div style="width:6px;height:6px;border-radius:50%;background:{border_color};box-shadow:0 0 5px {border_color};"></div>
</div>
<div style="font-size:1.35rem;font-weight:700;color:#F8FAFC;margin-bottom:6px;font-family:monospace;">{value_str}</div>
<div style="background:{badge_bg};color:{badge_fg};border:1px solid {badge_bd};padding:3px 8px;border-radius:6px;font-size:0.78rem;font-weight:600;display:inline-block;">{arrow} {abs(pct_change):.2f}%</div>
<div style="font-size:9px;color:#4B5563;margin-top:6px;">&#8635; click for details</div>
</div>
<div class="fb">{detail_html}</div>
</div>
</div>
""", height=140)

# ==========================================
# 3. INDIAN INDICES BAR + TRADINGVIEW TICKER TAPE
# ==========================================
@st.cache_data(ttl=300, show_spinner=False)
def get_indian_bar_data():
    indices = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "BANK NIFTY": "^NSEBANK",
        "NIFTY IT": "^CNXIT",
        "NIFTY MID": "^NSEMDCP50",
    }
    items = []
    for name, sym in indices.items():
        try:
            df = yf.Ticker(sym).history(period="2d")
            if df.empty:
                continue
            price = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2]) if len(df)>1 else price
            chg = ((price-prev)/prev*100) if prev else 0
            items.append((name, price, chg))
        except:
            continue
    return items

indian_items = get_indian_bar_data()

if indian_items:
    cells = ""
    for name, price, chg in indian_items:
        color = "#20C997" if chg >= 0 else "#FF4D4D"
        arrow = "▲" if chg >= 0 else "▼"
        cells += f"""
        <div style="display:flex;flex-direction:column;
        padding:6px 20px;border-right:1px solid rgba(168,85,247,0.15);
        min-width:140px;">
            <span style="font-size:9px;font-weight:700;color:#94A3B8;
            letter-spacing:0.1em;">{name}</span>
            <span style="font-size:14px;font-weight:700;color:#F8FAFC;
            font-family:monospace;margin:2px 0;">
            {price:,.2f}</span>
            <span style="font-size:11px;font-weight:600;color:{color};">
            {arrow} {abs(chg):.2f}%</span>
        </div>"""

    components.html(f"""
    <div style="background:rgba(11,9,20,0.95);
    border-bottom:1px solid rgba(168,85,247,0.2);
    border-top:1px solid rgba(168,85,247,0.2);
    padding:4px 0;display:flex;align-items:center;
    overflow-x:auto;white-space:nowrap;width:100%;">
        <div style="display:flex;align-items:center;
        padding:0 16px;border-right:1px solid rgba(168,85,247,0.3);
        margin-right:4px;min-width:70px;">
            <span style="font-size:10px;font-weight:800;
            color:#A855F7;letter-spacing:0.15em;">🇮🇳 NSE</span>
        </div>
        {cells}
        <div style="padding:0 16px;font-size:9px;color:#4B5563;
        white-space:nowrap;">
            via yfinance · 15min delay
        </div>
    </div>
    """, height=62)

ticker_tape_html = """
<div class="tradingview-widget-container">
<div class="tradingview-widget-container__widget"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
{
  "symbols": [
    {"proName":"FOREXCOM:NSXUSD","title":"Nasdaq 100"},
    {"proName":"FOREXCOM:SPXUSD","title":"S&P 500"},
    {"proName":"OANDA:XAUUSD","title":"Gold"},
    {"proName":"BITSTAMP:BTCUSD","title":"Bitcoin"},
    {"proName":"FX_IDC:USDINR","title":"USD/INR"}
  ],
  "showSymbolLogo": true,
  "colorTheme": "dark",
  "isTransparent": true,
  "locale": "in"
}
</script></div>
"""
components.html(ticker_tape_html, height=55)

# Page Header
st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
col1, col2 = st.columns([0.88, 0.12])
with col1:
    st.markdown('<div style="font-size:2.2rem; font-weight:800; color:#F8FAFC; font-family:\'Inter\', sans-serif; line-height:1.15;">Live Markets</div><div style="font-size:0.7rem; font-weight:600; color:#A855F7; letter-spacing:0.18em; text-transform:uppercase; margin-top:2px; margin-bottom:4px;">Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.85rem; color:#94A3B8; margin-bottom:1rem;">PORTFOLIO INTELLIGENCE &nbsp;·&nbsp; <span class="pulse-dot" style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#20C997;box-shadow:0 0 6px #20C997;vertical-align:middle;margin-right:4px;"></span> LIVE</div>', unsafe_allow_html=True)
with col2:
    if st.button("↻ Resync Node", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

nse_label, nse_color = status["nse"]
us_label, us_color = status["us"]
st.markdown(f"""
<div style="display:flex;align-items:center;gap:20px;margin-bottom:1.2rem;padding:8px 16px;
background:rgba(30,25,45,0.5);border-radius:8px;border:1px solid rgba(168,85,247,0.15);">
    <span style="font-size:0.72rem;font-weight:600;color:{nse_color};letter-spacing:0.06em;">{nse_label}</span>
    <span style="font-size:0.72rem;font-weight:600;color:{us_color};letter-spacing:0.06em;">{us_label}</span>
    <span style="font-size:0.72rem;font-weight:600;color:#20C997;letter-spacing:0.06em;">{status["crypto"][0]}</span>
    <span style="margin-left:auto;font-size:0.68rem;color:#4B5563;">
        Last sync: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%I:%M %p IST')}
    </span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. DASHBOARD CARDS
# ==========================================
st.markdown('<div class="section-accent">Market Indices</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
nifty_p, nifty_c = get_latest_metrics("^NSEI")
sensex_p, sensex_c = get_latest_metrics("^BSESN")
bank_p, bank_c = get_latest_metrics("^NSEBANK")
nasdaq_p, nasdaq_c = get_latest_metrics("^IXIC")

with c1: render_kpi("Nifty 50", f"{nifty_p:,.2f}", nifty_c, "#3B82F6", "^NSEI")
with c2: render_kpi("Sensex", f"{sensex_p:,.2f}", sensex_c, "#3B82F6", "^BSESN")
with c3: render_kpi("Bank Nifty", f"{bank_p:,.2f}", bank_c, "#3B82F6", "^NSEBANK")
with c4: render_kpi("Nasdaq", f"{nasdaq_p:,.2f}", nasdaq_c, "#8B5CF6", "^IXIC")

st.markdown('<div class="section-accent">Commodities & Crypto</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
gold_p, gold_c = get_latest_metrics("GC=F")
crude_p, crude_c = get_latest_metrics("CL=F")
usdinr_p, usdinr_c = get_latest_metrics("INR=X")
btc_p, btc_c = get_latest_metrics("BTC-USD")

with c1: render_kpi("Gold (USD/oz)", f"${gold_p:,.2f}", gold_c, "#F59E0B", "GC=F")
with c2: render_kpi("Crude Oil", f"${crude_p:,.2f}", crude_c, "#F59E0B", "CL=F")
with c3: render_kpi("USD/INR", f"₹{usdinr_p:,.4f}", usdinr_c, "#10B981", "INR=X")
with c4: render_kpi("Bitcoin", f"${btc_p:,.2f}", btc_c, "#F97316", "BTC-USD")

# ==========================================
# 5. TECHNICAL INTELLIGENCE PANEL
# ==========================================
st.markdown('<div class="section-accent">Technical Intelligence</div>', unsafe_allow_html=True)

CHART_ASSETS = {
    "Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Sensex": "^BSESN",
    "S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Dow Jones": "^DJI",
    "Gold": "GC=F", "Crude Oil": "CL=F",
    "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "USD/INR": "INR=X"
}
PERIOD_MAP = {"1 Week": 5, "1 Month": 21, "3 Months": 63, "6 Months": 126, "1 Year": 252}

c_asset, c_tf, c_empty = st.columns([0.25, 0.2, 0.55])
with c_asset:
    selected_asset = st.selectbox("Select Asset", list(CHART_ASSETS.keys()), label_visibility="collapsed")
with c_tf:
    selected_period = st.selectbox("Timeframe", list(PERIOD_MAP.keys()), index=2, label_visibility="collapsed")

chart_ticker = CHART_ASSETS[selected_asset]
display_days = PERIOD_MAP[selected_period]
full_data = fetch_market_data(chart_ticker, period="1y")

if full_data is not None and not full_data.empty:
    display_data = full_data.tail(display_days)
    tech_stats = calculate_technical_summary(full_data, display_data)
    
    col_chart, col_stats = st.columns([0.65, 0.35])
    
    INDIAN_ASSETS = ["Nifty 50", "Bank Nifty", "Sensex", "Nifty IT"]

    TV_SYMBOL_MAP = {
        "S&P 500": "FOREXCOM:SPXUSD",
        "Nasdaq": "FOREXCOM:NSXUSD",
        "Dow Jones": "FOREXCOM:DJI",
        "Gold": "OANDA:XAUUSD",
        "Crude Oil": "OANDA:BCOUSD",
        "Bitcoin": "BITSTAMP:BTCUSD",
        "Ethereum": "BITSTAMP:ETHUSD",
        "USD/INR": "FX_IDC:USDINR",
        "EUR/INR": "FX_IDC:EURINR",
    }
    TF_MAP = {
        "1 Week": "W",
        "1 Month": "M",
        "3 Months": "3M",
        "6 Months": "6M",
        "1 Year": "12M",
    }

    with col_chart:
        if selected_asset in INDIAN_ASSETS:
            if full_data is not None and not full_data.empty:
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=display_data.index,
                    open=display_data['Open'],
                    high=display_data['High'],
                    low=display_data['Low'],
                    close=display_data['Close'],
                    increasing_line_color='#20C997',
                    decreasing_line_color='#FF4D4D',
                    increasing_fillcolor='rgba(32,201,151,0.3)',
                    decreasing_fillcolor='rgba(255,77,77,0.3)',
                    name=selected_asset
                ))
                ema20_line = display_data['Close'].ewm(span=20).mean()
                fig.add_trace(go.Scatter(
                    x=display_data.index, y=ema20_line,
                    line=dict(color='#A855F7', width=1.5, dash='dot'),
                    name='EMA 20'
                ))
                ema50_line = display_data['Close'].ewm(span=50).mean()
                fig.add_trace(go.Scatter(
                    x=display_data.index, y=ema50_line,
                    line=dict(color='#F59E0B', width=1.5, dash='dot'),
                    name='EMA 50'
                ))
                fig.update_layout(
                    height=500,
                    margin=dict(l=0, r=0, t=30, b=0),
                    paper_bgcolor='rgba(11,9,20,1)',
                    plot_bgcolor='rgba(15,12,25,1)',
                    font=dict(color='#94A3B8', family='Inter'),
                    xaxis=dict(showgrid=False, zeroline=False,
                               rangeslider=dict(visible=False), color='#4B5563'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(168,85,247,0.08)',
                               side='right', zeroline=False, color='#4B5563'),
                    legend=dict(bgcolor='rgba(30,25,45,0.8)',
                                bordercolor='rgba(168,85,247,0.2)',
                                borderwidth=1, font=dict(size=11)),
                    hovermode='x unified',
                    hoverlabel=dict(bgcolor='rgba(30,25,45,0.95)',
                                   bordercolor='rgba(168,85,247,0.3)',
                                   font=dict(color='#F8FAFC', size=11))
                )
                st.markdown(
                    f'<div style="font-size:10px;color:#6B7280;margin-bottom:4px;display:flex;align-items:center;gap:8px;">'
                    f'<span style="color:#A855F7;">&#9679;</span>'
                    f'{selected_asset} &middot; {selected_period} &middot; Candlestick + EMA 20/50'
                    f'<span style="margin-left:auto;color:#4B5563;">via yfinance &middot; 15min delay</span>'
                    f'</div>', unsafe_allow_html=True
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            tv_sym = TV_SYMBOL_MAP.get(selected_asset, "FOREXCOM:SPXUSD")
            tv_tf = TF_MAP.get(selected_period, "3M")
            cid = "tv_" + tv_sym.replace(":", "_").replace("/", "_")
            st.components.v1.html(f"""
<div id="{cid}" style="height:500px;border-radius:12px;overflow:hidden;border:1px solid rgba(168,85,247,0.15);"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>
new TradingView.widget({{
  "autosize": true,
  "symbol": "{tv_sym}",
  "interval": "{tv_tf}",
  "timezone": "Asia/Kolkata",
  "theme": "dark",
  "style": "1",
  "locale": "in",
  "toolbar_bg": "#0B0914",
  "enable_publishing": false,
  "withdateranges": true,
  "hide_side_toolbar": false,
  "allow_symbol_change": false,
  "studies": ["RSI@tv-basicstudies","MACD@tv-basicstudies","MAExp@tv-basicstudies"],
  "container_id": "{cid}",
  "width": "100%",
  "height": 500,
  "backgroundColor": "rgba(11,9,20,1)",
  "gridColor": "rgba(168,85,247,0.06)"
}});
</script>
""", height=520)

    # --- RIGHT PANEL (CLEANED UP & STREAMLINED) ---    
    with col_stats:
        if tech_stats:
            rsi_val = tech_stats['rsi_latest']
            macd_val = tech_stats['macd_latest']
            prefix = "₹" if "Nifty" in selected_asset or "Sensex" in selected_asset or "INR" in selected_asset else "$"
            
            # Smart text classes for badges
            if rsi_val > 70:
                rsi_badge, rsi_text = "badge-down", "OVERBOUGHT"
            elif rsi_val < 30:
                rsi_badge, rsi_text = "badge-up", "OVERSOLD"
            else:
                rsi_badge, rsi_text = "badge-neutral", "NEUTRAL"
                
            macd_badge, macd_text = ("badge-up", "BULLISH") if macd_val > 0 else ("badge-down", "BEARISH")
            
            html_panel = (
                f"<div class='tech-panel'>"
                f"<div style='color:#F8FAFC; font-weight:800; font-size:1.3rem; margin-bottom:20px; font-family:Inter;'>{selected_asset}</div>"
                
                # Indicators
                f"<div style='margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid rgba(168, 85, 247, 0.15);'>"
                f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>"
                f"<span class='tech-label'>RSI (14)</span>"
                f"<div style='text-align:right;'><span class='tech-val' style='font-size:1.1rem; margin-right:8px;'>{rsi_val:.1f}</span><span class='{rsi_badge}'>{rsi_text}</span></div>"
                f"</div>"
                f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<span class='tech-label'>MACD Line</span>"
                f"<div style='text-align:right;'><span class='tech-val' style='font-size:1.1rem; margin-right:8px;'>{macd_val:.2f}</span><span class='{macd_badge}'>{macd_text}</span></div>"
                f"</div>"
                f"</div>"
                
                # Price Stats
                f"<div class='tech-row'><span class='tech-label'>Period High</span><span class='tech-val'>{prefix}{tech_stats['high']:,.2f}</span></div>"
                f"<div class='tech-row'><span class='tech-label'>Period Low</span><span class='tech-val'>{prefix}{tech_stats['low']:,.2f}</span></div>"
                
                # Recent Closes
                f"<div style='margin-top: 25px; margin-bottom: 10px;'><span style='color:#A855F7; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;'>Recent Closes</span></div>"
            )
            
            for date, row in tech_stats['history'][::-1].iterrows():
                dt_str = date.strftime('%d %b')
                html_panel += f"<div class='tech-row' style='padding: 8px 0; border:none;'><span class='tech-label'>{dt_str}</span><span class='tech-val' style='font-size:0.95rem;'>{prefix}{row['Close']:,.2f}</span></div>"
                
            html_panel += "</div>"
            st.markdown(html_panel, unsafe_allow_html=True)
else:
    st.error(f"Market data is currently unavailable for {selected_asset}.")

# ==========================================
# 6. AI INTELLIGENCE PANEL
# ==========================================
st.markdown('<div class="section-accent">AI Intelligence</div>', unsafe_allow_html=True)

mode_col, _ = st.columns([0.3, 0.7])
with mode_col:
    ai_mode = st.radio("", ["Easy Mode", "Advanced Mode"],
                       horizontal=True, key="ai_mode",
                       label_visibility="collapsed")

if full_data is not None and tech_stats:
    closes = full_data['Close']
    curr = float(closes.iloc[-1])
    prev = float(closes.iloc[-2])
    ema20 = float(closes.ewm(span=20).mean().iloc[-1])
    ema50 = float(closes.ewm(span=50).mean().iloc[-1])
    rsi_v = float(tech_stats['rsi_latest'])
    macd_v = float(tech_stats['macd_latest'])
    sig_v = float(tech_stats['signal_series'].iloc[-1])

    score = 0
    if curr > ema20: score += 25
    if curr > ema50: score += 25
    if rsi_v > 50: score += 20
    if macd_v > sig_v: score += 20
    if curr > prev: score += 10

    verdict = "BULLISH" if score >= 65 else "BEARISH" if score <= 35 else "NEUTRAL"
    vc  = "#20C997" if verdict == "BULLISH" else "#FF4D4D" if verdict == "BEARISH" else "#D8B4FE"
    vbg = "rgba(32,201,151,0.08)" if verdict == "BULLISH" else "rgba(255,77,77,0.08)" if verdict == "BEARISH" else "rgba(168,85,247,0.08)"
    vb  = "rgba(32,201,151,0.25)" if verdict == "BULLISH" else "rgba(255,77,77,0.25)" if verdict == "BEARISH" else "rgba(168,85,247,0.25)"

    prefix = "₹" if any(x in selected_asset for x in ["Nifty","Sensex","INR"]) else "$" if any(x in selected_asset for x in ["Gold","Oil","Bitcoin","Ethereum","S&P","Nasdaq","Dow"]) else ""

    rsi_txt = "Overbought — may cool soon" if rsi_v > 70 else "Oversold — bounce possible" if rsi_v < 30 else "Healthy range"
    rsi_c   = "#FF4D4D" if rsi_v > 70 else "#20C997" if rsi_v < 30 else "#D8B4FE"
    trend_txt = "above" if curr > ema20 else "below"
    macd_txt  = "Positive — momentum building" if macd_v > sig_v else "Negative — watch carefully"
    macd_c    = "#20C997" if macd_v > sig_v else "#FF4D4D"

    if ai_mode == "Easy Mode":
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div style="background:{vbg};border:1px solid {vb};border-radius:12px;
            padding:20px;text-align:center;height:100%;">
                <div style="font-size:0.65rem;font-weight:700;color:#94A3B8;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">AI VERDICT</div>
                <div style="font-size:1.8rem;font-weight:800;color:{vc};margin-bottom:6px;">{verdict}</div>
                <div style="font-size:0.75rem;color:#94A3B8;margin-bottom:12px;">Confidence: {score}/100</div>
                <div style="height:4px;background:rgba(255,255,255,0.08);border-radius:2px;">
                    <div style="height:4px;width:{score}%;background:{vc};border-radius:2px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        with c2:
            above20 = curr > ema20
            above50 = curr > ema50
            c20 = "#20C997" if above20 else "#FF4D4D"
            c50 = "#20C997" if above50 else "#FF4D4D"
            st.markdown(f"""
            <div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);
            border-radius:12px;padding:20px;height:100%;">
                <div style="font-size:0.65rem;font-weight:700;color:#94A3B8;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:16px;">TREND</div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                    <span style="font-size:0.8rem;color:#94A3B8;">Price vs EMA 20</span>
                    <span style="font-size:0.8rem;font-weight:700;color:{c20};">{'▲ Above' if above20 else '▼ Below'}</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.8rem;color:#94A3B8;">Price vs EMA 50</span>
                    <span style="font-size:0.8rem;font-weight:700;color:{c50};">{'▲ Above' if above50 else '▼ Below'}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);
            border-radius:12px;padding:20px;text-align:center;height:100%;">
                <div style="font-size:0.65rem;font-weight:700;color:#94A3B8;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">MOMENTUM (RSI)</div>
                <div style="font-size:2rem;font-weight:800;color:{rsi_c};margin-bottom:4px;">{rsi_v:.1f}</div>
                <div style="font-size:0.75rem;color:{rsi_c};margin-bottom:12px;">{rsi_txt}</div>
                <div style="height:4px;background:rgba(255,255,255,0.08);border-radius:2px;">
                    <div style="height:4px;width:{min(rsi_v, 100):.0f}%;background:{rsi_c};border-radius:2px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);
            border-radius:12px;padding:20px;height:100%;">
                <div style="font-size:0.65rem;font-weight:700;color:#94A3B8;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px;">PLAIN ENGLISH</div>
                <div style="font-size:0.82rem;color:#CBD5E1;line-height:1.7;">
                    <p style="margin:0 0 8px 0;">{selected_asset} is trading
                    <strong style="color:#F8FAFC;">{trend_txt}</strong>
                    its 20-day average.</p>
                    <p style="margin:0 0 8px 0;">RSI at {rsi_v:.0f} — {rsi_txt.lower()}.</p>
                    <p style="margin:0;">MACD: {macd_txt}.</p>
                </div>
            </div>""", unsafe_allow_html=True)

    else:
        a1, a2, a3 = st.columns(3)
        overall = "Strong Buy" if score >= 80 else "Buy" if score >= 60 else "Strong Sell" if score <= 20 else "Sell" if score <= 40 else "Neutral"
        oc = "#20C997" if score >= 60 else "#FF4D4D" if score <= 40 else "#D8B4FE"

        with a1:
            st.markdown(f"""
            <div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);
            border-radius:12px;padding:20px;height:100%;">
                <div style="font-size:0.65rem;font-weight:700;color:#94A3B8;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:16px;">OSCILLATORS</div>
                <div style="margin-bottom:14px;">
                    <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:4px;">RSI (14)</div>
                    <div style="font-size:1.5rem;font-weight:700;color:{rsi_c};">{rsi_v:.1f}</div>
                </div>
                <div style="margin-bottom:14px;">
                    <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:4px;">MACD</div>
                    <div style="font-size:1.5rem;font-weight:700;color:{macd_c};">{macd_v:.2f}</div>
                </div>
                <div>
                    <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:4px;">Signal</div>
                    <div style="font-size:1.5rem;font-weight:700;color:#D8B4FE;">{sig_v:.2f}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with a2:
            st.markdown(f"""
            <div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);
            border-radius:12px;padding:20px;height:100%;">
                <div style="font-size:0.65rem;font-weight:700;color:#94A3B8;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:16px;">MOVING AVERAGES</div>
                <div style="margin-bottom:14px;">
                    <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:4px;">EMA 20</div>
                    <div style="font-size:1.5rem;font-weight:700;color:#F8FAFC;">{prefix}{ema20:,.2f}</div>
                </div>
                <div style="margin-bottom:14px;">
                    <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:4px;">EMA 50</div>
                    <div style="font-size:1.5rem;font-weight:700;color:#F8FAFC;">{prefix}{ema50:,.2f}</div>
                </div>
                <div>
                    <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:4px;">Current</div>
                    <div style="font-size:1.5rem;font-weight:700;color:#A855F7;">{prefix}{curr:,.2f}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with a3:
            st.markdown(f"""
            <div style="background:rgba(30,25,45,0.6);border:1px solid rgba(168,85,247,0.2);
            border-radius:12px;padding:20px;height:100%;">
                <div style="font-size:0.65rem;font-weight:700;color:#94A3B8;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:16px;">SIGNAL SUMMARY</div>
                <div style="margin-bottom:14px;">
                    <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:4px;">Overall</div>
                    <div style="font-size:1.5rem;font-weight:700;color:{oc};">{overall}</div>
                </div>
                <div style="margin-bottom:14px;">
                    <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:4px;">Trend</div>
                    <div style="font-size:1.5rem;font-weight:700;color:#F8FAFC;">{'Uptrend' if curr > ema50 else 'Downtrend'}</div>
                </div>
                <div>
                    <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:4px;">Momentum</div>
                    <div style="font-size:1.5rem;font-weight:700;color:{'#20C997' if macd_v > sig_v else '#FF4D4D'};">{'Positive' if macd_v > sig_v else 'Negative'}</div>
                </div>
            </div>""", unsafe_allow_html=True)