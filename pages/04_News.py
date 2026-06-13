"""Financial News Hub — SipCheck v2.0"""
import streamlit as st
import feedparser
import requests
import os
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
except ImportError:
    import pytz
    IST = pytz.timezone("Asia/Kolkata")

st.set_page_config(page_title="Financial News Hub — SipCheck", page_icon="📰", layout="wide")
from sidebar_v2 import render_sidebar
render_sidebar()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""<style>
#MainMenu {visibility:hidden;} footer {visibility:hidden;}
.stApp { background:#0d0d24; color:#f0f0ff; }
section[data-testid="stSidebar"] { background:#0d0d24; border-right:1px solid rgba(139,92,246,0.15); }
.block-container { padding:1.5rem 2rem; }

.mkt-header { font-size:1.6rem; font-weight:700; color:#f0f0ff; margin-bottom:0.25rem; }
.mkt-sub    { font-size:0.82rem; color:#6b7280; margin-bottom:1.2rem; }

.section-title {
    font-size:0.72rem; font-weight:600; color:#8b5cf6;
    text-transform:uppercase; letter-spacing:0.08em;
    margin:1.5rem 0 0.75rem; border-left:3px solid #8b5cf6; padding-left:10px;
}

/* Global Market Pulse ticker */
.ticker-wrap {
    background:#080818; border:1px solid rgba(139,92,246,0.2);
    border-radius:10px; padding:0.65rem 1.1rem; margin-bottom:1rem;
    overflow-x:auto; white-space:nowrap; scrollbar-width:none;
}
.ticker-item  { display:inline-block; margin-right:1.8rem; }
.ticker-label { font-size:0.68rem; color:#6b7280; margin-right:4px; }
.ticker-val   { font-size:0.85rem; font-weight:700; color:#f0f0ff; }
.tick-up      { font-size:0.72rem; color:#10b981; margin-left:3px; }
.tick-down    { font-size:0.72rem; color:#ef4444; margin-left:3px; }
.ticker-ts    { font-size:0.68rem; color:#374151; margin-left:8px; }

/* Economic calendar */
.econ-card {
    background:#0f0f2a; border:1px solid rgba(139,92,246,0.12);
    border-radius:8px; padding:0.65rem 1rem; margin-bottom:0.4rem;
    display:flex; align-items:flex-start; gap:10px;
}
.econ-dot    { width:9px; height:9px; border-radius:50%; margin-top:5px; flex-shrink:0; }
.econ-red    { background:#ef4444; box-shadow:0 0 6px rgba(239,68,68,0.5); }
.econ-yellow { background:#f59e0b; }
.econ-green  { background:#10b981; }
.econ-event  { font-size:0.84rem; font-weight:500; color:#f0f0ff; }
.econ-meta   { font-size:0.7rem; color:#6b7280; margin-top:2px; }
.econ-date   { font-size:0.7rem; color:#8b5cf6; font-weight:600; white-space:nowrap; flex-shrink:0; }

.countdown-box {
    background:linear-gradient(135deg,rgba(139,92,246,0.12),rgba(16,185,129,0.06));
    border:1px solid rgba(139,92,246,0.25); border-radius:10px;
    padding:0.85rem 1.1rem; margin-bottom:0.9rem; text-align:center;
}

/* News cards */
.news-card {
    background:#111130; border:1px solid rgba(139,92,246,0.1);
    border-radius:10px; padding:0.85rem 1.1rem; margin-bottom:0.45rem;
    border-left:3px solid #8b5cf6;
}
.news-card:hover { border-left-color:#10b981; }
.news-title a { color:#f0f0ff; text-decoration:none; font-size:0.86rem;
                font-weight:500; line-height:1.45; }
.news-title a:hover { color:#8b5cf6; }
.news-meta   { font-size:0.7rem; color:#6b7280; margin-top:4px; }
.source-badge {
    display:inline-block; background:rgba(139,92,246,0.12);
    color:#8b5cf6; font-size:0.63rem; font-weight:700;
    padding:1px 7px; border-radius:8px; margin-right:6px; letter-spacing:0.02em;
}
.rbi-badge  { display:inline-block; background:rgba(239,68,68,0.12); color:#ef4444;
              font-size:0.63rem; font-weight:700; padding:1px 7px; border-radius:8px; margin-right:5px; }
.sebi-badge { display:inline-block; background:rgba(245,158,11,0.12); color:#f59e0b;
              font-size:0.63rem; font-weight:700; padding:1px 7px; border-radius:8px; margin-right:5px; }
.pol-badge  { display:inline-block; background:rgba(99,179,237,0.12); color:#63b3ed;
              font-size:0.63rem; font-weight:700; padding:1px 7px; border-radius:8px; margin-right:5px; }

/* IPO/NFO */
.ipo-card {
    background:#0f0f2a; border:1px solid rgba(16,185,129,0.15);
    border-left:3px solid #10b981; border-radius:8px;
    padding:0.65rem 1rem; margin-bottom:0.4rem;
}
.nfo-card {
    background:#0f0f2a; border:1px solid rgba(139,92,246,0.15);
    border-left:3px solid #8b5cf6; border-radius:8px;
    padding:0.65rem 1rem; margin-bottom:0.4rem;
}

/* Earnings */
.earn-card {
    background:#0f0f2a; border:1px solid rgba(245,158,11,0.15);
    border-left:3px solid #f59e0b; border-radius:8px;
    padding:0.65rem 1rem; margin-bottom:0.4rem;
}

/* Week preview */
.week-card {
    background:linear-gradient(135deg,#0f0f2a,#111130);
    border:1px solid rgba(139,92,246,0.2); border-radius:12px;
    padding:1.1rem 1.4rem; margin-bottom:0.8rem;
}
.week-title { font-size:0.95rem; font-weight:700; color:#8b5cf6; margin-bottom:0.6rem; }
.week-item  { font-size:0.8rem; color:#9ca3af; padding:3px 0; }
.week-item strong { color:#f0f0ff; }

/* AI */
.ai-box   { background:#0a0a1f; border:1px solid rgba(139,92,246,0.28);
            border-radius:12px; padding:0.95rem 1.1rem; margin-bottom:0.8rem; }
.ai-label { font-size:0.68rem; font-weight:700; color:#8b5cf6;
            text-transform:uppercase; letter-spacing:0.08em; margin-bottom:6px; }
</style>""", unsafe_allow_html=True)


# ── Constants ─────────────────────────────────────────────────────────────────

RSS_FEEDS = [
    ("Economic Times",    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
    ("Moneycontrol",      "https://www.moneycontrol.com/rss/latestnews.xml"),
    ("Business Standard", "https://www.business-standard.com/rss/markets-106.rss"),
    ("LiveMint",          "https://www.livemint.com/rss/markets"),
    ("Reuters India",     "https://feeds.reuters.com/reuters/INbusinessNews"),
    ("NDTV Profit",       "https://feeds.feedburner.com/NdtvProfitLatestNews"),
    ("CNBC TV18",         "https://www.cnbctv18.com/commonfeeds/v1/hin/rss/market.xml"),
    ("Financial Express", "https://www.financialexpress.com/market/feed/"),
]

FILTERS = {
    "All":          [],
    "Nifty/Sensex": ["nifty", "sensex", "bse", "nse", "index"],
    "Mutual Funds": ["mutual fund", "nav", "sip", "amfi", "scheme", " mf ", "fund"],
    "RBI/Policy":   ["rbi", "repo", "inflation", "gdp", "monetary", "rupee", "rate cut", "rate hike"],
    "Global":       ["fed", "us market", "global", "nasdaq", "dow", "s&p", "china", "europe", "dollar"],
    "Gold/Crude":   ["gold", "crude", "oil", "silver", "commodity", "mcx"],
    "IT/Stocks":    ["infosys", "tcs", "wipro", "hdfc", "reliance", "it sector"],
    "IPO/NFO":      ["ipo", "nfo", "new fund offer", "listing", "allotment"],
}

RBI_SEBI_KWS = [
    "rbi", "sebi", "monetary policy", "repo rate", "rate cut", "rate hike",
    "reserve bank", "securities exchange board", "rbi governor", "rbi meeting",
    "mpc", "inflation target", "liquidity",
]
IPO_KWS  = ["ipo", "initial public offer", "ipo listing", "ipo open", "ipo close",
             "ipo allotment", "ipo subscription", "mainboard ipo", "sme ipo"]
NFO_KWS  = ["nfo", "new fund offer", "new scheme", "nfo open", "nfo close", "nfo subscription"]
EARN_KWS = [
    "results", "quarterly results", "q1 result", "q2 result", "q3 result", "q4 result",
    "net profit", "net loss", "revenue", "earnings", "eps", "declares dividend",
    "annual results",
]

MARKET_SYMBOLS = [
    ("S&P Fut",    "ES=F",      "$"),
    ("Nasdaq Fut", "NQ=F",      "$"),
    ("Crude Oil",  "CL=F",      "$"),
    ("Gold",       "GC=F",      "$"),
    ("USD/INR",    "USDINR=X",  "₹"),
    ("US 10Y",     "^TNX",      "%"),
    ("Nifty 50",   "^NSEI",     "₹"),
    ("Bank Nifty", "^NSEBANK",  "₹"),
]


# ── Data fetchers ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def fetch_market_data():
    try:
        import yfinance as yf
        result = []
        for label, sym, prefix in MARKET_SYMBOLS:
            try:
                fi = yf.Ticker(sym).fast_info
                price = float(fi.last_price or 0)
                prev  = float(fi.previous_close or price)
                pct   = ((price - prev) / prev * 100) if prev else 0.0
                result.append({"label": label, "price": price, "pct": pct, "prefix": prefix})
            except Exception:
                pass
        return result
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_econ_calendar():
    try:
        r = requests.get(
            "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
            headers={"User-Agent": "Mozilla/5.0 SipCheck/2.0"},
            timeout=10,
        )
        if r.status_code == 200:
            events = r.json()
            return [
                e for e in events
                if e.get("impact") in ("High", "Medium")
                and e.get("country", "").upper() in ("USD", "INR", "EUR", "GBP", "JPY", "CNY", "AUD")
            ]
    except Exception:
        pass
    return []


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_rss(max_per_feed=10):
    articles = []
    for source, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                pub = ""
                if hasattr(entry, "published"):
                    try:
                        pub = parsedate_to_datetime(entry.published).strftime("%d %b, %I:%M %p")
                    except Exception:
                        pub = entry.get("published", "")
                title = entry.get("title", "").strip()
                if not title:
                    continue
                summary = ""
                if hasattr(entry, "summary") and entry.summary:
                    import re
                    summary = re.sub(r"<[^>]+>", "", entry.summary)[:250]
                articles.append({
                    "title":   title,
                    "source":  source,
                    "url":     entry.get("link", "#"),
                    "pub":     pub,
                    "summary": summary,
                })
        except Exception:
            continue
    seen, unique = set(), []
    for a in articles:
        k = a["title"][:40].lower()
        if k not in seen:
            seen.add(k)
            unique.append(a)
    return unique


def filter_articles(articles, category):
    kws = FILTERS.get(category, [])
    if not kws:
        return articles
    out = [a for a in articles
           if any(k in (a["title"] + " " + a.get("summary", "")).lower() for k in kws)]
    return out if out else articles


def get_ai_summary(headlines, api_key):
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=220,
            messages=[{"role": "user", "content":
                "Summarise today's Indian financial market mood in 3 short, direct sentences "
                "based on these headlines:\n" + "\n".join(f"- {h}" for h in headlines[:8])}],
        )
        return msg.content[0].text.strip()
    except Exception:
        return None


def _now_ist():
    from datetime import timezone
    try:
        return datetime.now(IST)
    except Exception:
        return datetime.now(timezone.utc)


def _parse_ff_date(date_str):
    """Parse Forex Factory ISO date string → datetime with IST timezone."""
    import re
    try:
        ds = re.sub(r'([+-]\d{2})(\d{2})$', r'\1:\2', str(date_str))
        d = datetime.fromisoformat(ds)
        return d.astimezone(IST)
    except Exception:
        return None


def _next_event_countdown(events):
    now = _now_ist()
    upcoming = [
        (_parse_ff_date(e["date"]), e)
        for e in events
        if e.get("impact") == "High" and _parse_ff_date(e.get("date", ""))
    ]
    upcoming = [(d, e) for d, e in upcoming if d and d > now]
    if not upcoming:
        return None, None
    upcoming.sort(key=lambda x: x[0])
    nxt_dt, nxt_e = upcoming[0]
    delta = nxt_dt - now
    hrs  = int(delta.total_seconds()) // 3600
    mins = (int(delta.total_seconds()) % 3600) // 60
    return f"{hrs}h {mins}m", nxt_e


# ── Section renderers ─────────────────────────────────────────────────────────

def render_market_ticker(mkt_data):
    if not mkt_data:
        return
    items = ""
    for d in mkt_data:
        price, pct, prefix, label = d["price"], d["pct"], d["prefix"], d["label"]
        if price <= 0:
            continue
        if prefix == "%":
            p_str = f"{price:.3f}%"
        elif prefix == "₹":
            p_str = f"₹{price:,.2f}"
        else:
            p_str = f"${price:,.2f}"
        cls  = "tick-up" if pct >= 0 else "tick-down"
        sign = "▲" if pct >= 0 else "▼"
        items += (
            f'<span class="ticker-item">'
            f'<span class="ticker-label">{label}</span>'
            f'<span class="ticker-val">{p_str}</span>'
            f'<span class="{cls}">{sign} {abs(pct):.2f}%</span>'
            f'</span>'
        )
    if not items:
        return
    ts = _now_ist().strftime("%I:%M %p IST")
    st.markdown(
        f'<div class="ticker-wrap">{items}'
        f'<span class="ticker-ts">⟳ {ts} · auto-refresh 5 min</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_econ_calendar(events):
    st.markdown('<div class="section-title">Economic Calendar — This Week</div>', unsafe_allow_html=True)

    cdown, nxt_e = _next_event_countdown(events)
    if cdown and nxt_e:
        st.markdown(
            f'<div class="countdown-box">'
            f'<div style="font-size:0.68rem;color:#6b7280;margin-bottom:3px;">Next High-Impact Event</div>'
            f'<div style="font-size:1rem;font-weight:700;color:#8b5cf6;">'
            f'{nxt_e.get("title","")} <span style="color:#6b7280;font-size:0.72rem;">({nxt_e.get("country","")})</span></div>'
            f'<div style="font-size:1.5rem;font-weight:800;color:#10b981;margin:4px 0;">{cdown}</div>'
            f'<div style="font-size:0.68rem;color:#6b7280;">🔴 High Impact · times in IST</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if not events:
        st.markdown(
            '<div style="color:#6b7280;font-size:0.82rem;padding:0.6rem 0;">'
            'Calendar data unavailable. '
            '<a href="https://www.forexfactory.com/calendar" target="_blank" style="color:#8b5cf6;">'
            'View on Forex Factory ↗</a></div>',
            unsafe_allow_html=True,
        )
        return

    now = _now_ist()
    shown = 0
    for e in events[:25]:
        impact  = e.get("impact", "")
        title   = e.get("title", "")
        country = e.get("country", "")
        prev    = e.get("previous", "")
        fore    = e.get("forecast", "")
        actual  = e.get("actual", "")
        d = _parse_ff_date(e.get("date", ""))
        if not d:
            continue
        shown += 1
        is_past  = d < now
        dot_cls  = "econ-red" if impact == "High" else "econ-yellow"
        icon     = "🔴" if impact == "High" else "🟡"
        date_str = d.strftime("%a %d %b, %I:%M %p")
        detail   = ""
        if actual:
            detail = f'Actual: <strong style="color:#10b981">{actual}</strong>'
        elif fore:
            detail = f"Forecast: {fore}"
        if prev:
            detail += f" &nbsp;|&nbsp; Prev: {prev}"
        opacity = "0.45" if is_past else "1"
        st.markdown(
            f'<div class="econ-card" style="opacity:{opacity};">'
            f'<div class="econ-dot {dot_cls}"></div>'
            f'<div style="flex:1;min-width:0;">'
            f'<div class="econ-event">{icon} {title} '
            f'<span style="color:#6b7280;font-size:0.7rem;">({country})</span></div>'
            f'<div class="econ-meta">{detail}</div>'
            f'</div>'
            f'<div class="econ-date">{date_str}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    if shown == 0:
        st.markdown('<div style="color:#6b7280;font-size:0.82rem;">No High/Medium events found this week.</div>', unsafe_allow_html=True)


def render_rbi_sebi(articles):
    st.markdown('<div class="section-title">RBI / SEBI Watch</div>', unsafe_allow_html=True)
    filtered = [
        a for a in articles
        if any(k in (a["title"] + " " + a.get("summary", "")).lower() for k in RBI_SEBI_KWS)
    ]
    if not filtered:
        st.markdown(
            '<div style="color:#6b7280;font-size:0.82rem;padding:0.5rem 0;">'
            'No RBI/SEBI headlines right now. Check back later.</div>',
            unsafe_allow_html=True,
        )
        return
    for a in filtered[:8]:
        t = a["title"].lower()
        if any(k in t for k in ["rbi", "reserve bank", "repo", "monetary", "mpc"]):
            badge = '<span class="rbi-badge">RBI</span>'
        elif any(k in t for k in ["sebi", "securities board"]):
            badge = '<span class="sebi-badge">SEBI</span>'
        else:
            badge = '<span class="pol-badge">POLICY</span>'
        st.markdown(
            f'<div class="news-card" style="border-left-color:#ef4444;">'
            f'<div class="news-title">{badge}'
            f'<a href="{a["url"]}" target="_blank">{a["title"]}</a></div>'
            f'<div class="news-meta"><span class="source-badge">{a["source"]}</span>{a["pub"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_ipo_nfo(articles):
    st.markdown('<div class="section-title">IPO & NFO Tracker</div>', unsafe_allow_html=True)
    ipos = [a for a in articles if any(k in (a["title"] + " " + a.get("summary","")).lower() for k in IPO_KWS)]
    nfos = [a for a in articles if any(k in (a["title"] + " " + a.get("summary","")).lower() for k in NFO_KWS)]

    if not ipos and not nfos:
        st.markdown(
            '<div style="color:#6b7280;font-size:0.82rem;padding:0.5rem 0;">'
            'No IPO/NFO news right now. '
            '<a href="https://www.amfiindia.com/net-asset-value/nfo-detail-page" target="_blank" '
            'style="color:#8b5cf6;">AMFI NFO page ↗</a> &nbsp;·&nbsp; '
            '<a href="https://www.nseindia.com/market-data/upcoming-ipo" target="_blank" '
            'style="color:#10b981;">NSE IPO page ↗</a></div>',
            unsafe_allow_html=True,
        )
        return

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div style="font-size:0.75rem;color:#10b981;font-weight:600;margin-bottom:6px;">IPOs</div>', unsafe_allow_html=True)
        if ipos:
            for a in ipos[:5]:
                st.markdown(
                    f'<div class="ipo-card">'
                    f'<div style="font-size:0.84rem;font-weight:500;">'
                    f'<a href="{a["url"]}" target="_blank" style="color:#f0f0ff;text-decoration:none;">{a["title"]}</a></div>'
                    f'<div style="font-size:0.7rem;color:#6b7280;margin-top:2px;">'
                    f'<span class="source-badge">{a["source"]}</span>{a["pub"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div style="color:#6b7280;font-size:0.8rem;">No IPO news right now.</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div style="font-size:0.75rem;color:#8b5cf6;font-weight:600;margin-bottom:6px;">NFOs (New Fund Offers)</div>', unsafe_allow_html=True)
        if nfos:
            for a in nfos[:5]:
                st.markdown(
                    f'<div class="nfo-card">'
                    f'<div style="font-size:0.84rem;font-weight:500;">'
                    f'<a href="{a["url"]}" target="_blank" style="color:#f0f0ff;text-decoration:none;">{a["title"]}</a></div>'
                    f'<div style="font-size:0.7rem;color:#6b7280;margin-top:2px;">'
                    f'<span class="source-badge">{a["source"]}</span>{a["pub"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div style="color:#6b7280;font-size:0.8rem;">No NFO news right now. '
                '<a href="https://www.amfiindia.com/net-asset-value/nfo-detail-page" '
                'target="_blank" style="color:#8b5cf6;">Check AMFI ↗</a></div>',
                unsafe_allow_html=True,
            )


def render_earnings(articles):
    st.markdown('<div class="section-title">Earnings Calendar — Company Results</div>', unsafe_allow_html=True)
    filtered = [
        a for a in articles
        if any(k in (a["title"] + " " + a.get("summary", "")).lower() for k in EARN_KWS)
    ]
    if not filtered:
        st.markdown(
            '<div style="color:#6b7280;font-size:0.82rem;padding:0.4rem 0;">'
            'No earnings news right now. '
            '<a href="https://www.nseindia.com/market-data/upcoming-results" target="_blank" '
            'style="color:#f59e0b;">NSE Upcoming Results ↗</a></div>',
            unsafe_allow_html=True,
        )
        return
    for a in filtered[:10]:
        st.markdown(
            f'<div class="earn-card">'
            f'<div style="font-size:0.84rem;font-weight:500;">'
            f'<a href="{a["url"]}" target="_blank" style="color:#f0f0ff;text-decoration:none;">{a["title"]}</a></div>'
            f'<div style="font-size:0.7rem;color:#6b7280;margin-top:2px;">'
            f'<span class="source-badge">{a["source"]}</span>{a["pub"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_weekly_preview(events, articles):
    now = _now_ist()
    week_start = now - timedelta(days=now.weekday())
    week_end   = week_start + timedelta(days=4)

    # High-impact events this week
    event_lines = ""
    for e in events:
        if e.get("impact") != "High":
            continue
        d = _parse_ff_date(e.get("date", ""))
        if d:
            past = "~~" if d < now else ""
            event_lines += (
                f'<div class="week-item">🗓️ <strong>{e.get("title","")} '
                f'({e.get("country","")})</strong> — {d.strftime("%a %d %b, %I:%M %p IST")}</div>'
            )

    if not event_lines:
        event_lines = '<div class="week-item" style="color:#374151;">No major events data — calendar may be loading.</div>'

    # F&O expiry: last Thursday of this month
    import calendar as _cal
    last_day = _cal.monthrange(now.year, now.month)[1]
    expiry_day = max(
        d for d in range(1, last_day + 1)
        if datetime(now.year, now.month, d).weekday() == 3
    )
    expiry_str = datetime(now.year, now.month, expiry_day).strftime("%d %b %Y")

    earn_count = sum(1 for a in articles
                     if any(k in a["title"].lower() for k in EARN_KWS))
    ipo_count  = sum(1 for a in articles
                     if any(k in a["title"].lower() for k in IPO_KWS))

    st.markdown(
        f'<div class="week-card">'
        f'<div class="week-title">📅 This Week in Markets &nbsp;·&nbsp; '
        f'<span style="font-size:0.8rem;font-weight:400;color:#6b7280;">'
        f'{week_start.strftime("%d %b")} – {week_end.strftime("%d %b %Y")}</span></div>'
        f'{event_lines}'
        f'<div style="border-top:1px solid rgba(139,92,246,0.1);margin:8px 0;"></div>'
        f'<div class="week-item">📊 <strong>F&O Monthly Expiry:</strong> {expiry_str}</div>'
        f'<div class="week-item">📰 <strong>Earnings in news:</strong> {earn_count} articles</div>'
        f'<div class="week-item">🏢 <strong>IPO news:</strong> {ipo_count} articles</div>'
        f'<div style="margin-top:8px;">'
        f'<a href="https://www.nseindia.com/market-data/upcoming-results" target="_blank" '
        f'style="color:#8b5cf6;font-size:0.75rem;">NSE Results ↗</a>'
        f' &nbsp;·&nbsp; '
        f'<a href="https://www.amfiindia.com/net-asset-value/nfo-detail-page" target="_blank" '
        f'style="color:#8b5cf6;font-size:0.75rem;">AMFI NFOs ↗</a>'
        f' &nbsp;·&nbsp; '
        f'<a href="https://www.forexfactory.com/calendar" target="_blank" '
        f'style="color:#8b5cf6;font-size:0.75rem;">Full Calendar ↗</a>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_news_card(a):
    return (
        f'<div class="news-card">'
        f'<div class="news-title"><a href="{a["url"]}" target="_blank">{a["title"]}</a></div>'
        f'<div class="news-meta"><span class="source-badge">{a["source"]}</span>{a["pub"]}</div>'
        f'</div>'
    )


# ── PAGE ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="mkt-header">📰 Financial News Hub</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="mkt-sub">Live markets · Economic calendar · RBI/SEBI · '
    'IPO/NFO · Earnings · 8 sources · auto-refresh</div>',
    unsafe_allow_html=True,
)

# Refresh button
hd, ref = st.columns([9, 1])
with ref:
    if st.button("↻ Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Fetch data ────────────────────────────────────────────────────────────────
with st.spinner("Loading market data & headlines…"):
    mkt_data     = fetch_market_data()
    econ_events  = fetch_econ_calendar()
    all_articles = fetch_rss(max_per_feed=10)

# 1. Global Market Pulse ticker (top)
render_market_ticker(mkt_data)

# 2. Weekly Market Preview
with st.expander("📅 This Week in Markets", expanded=True):
    render_weekly_preview(econ_events, all_articles)

# 3. Economic Calendar | RBI/SEBI Watch
col_econ, col_reg = st.columns([1.3, 1])
with col_econ:
    render_econ_calendar(econ_events)
with col_reg:
    render_rbi_sebi(all_articles)
    render_ipo_nfo(all_articles)

# 4. Main news feed + sidebar
main_col, side_col = st.columns([2, 1])

with main_col:
    st.markdown('<div class="section-title">Top Headlines</div>', unsafe_allow_html=True)
    sel_filter = st.radio(
        "Filter:", list(FILTERS.keys()),
        horizontal=True, label_visibility="collapsed",
    )
    articles = filter_articles(all_articles, sel_filter)
    st.markdown(
        f'<div style="font-size:0.72rem;color:#6b7280;margin-bottom:0.6rem;">'
        f'{len(articles)} headlines · {sel_filter} · {len(RSS_FEEDS)} sources</div>',
        unsafe_allow_html=True,
    )
    if not articles:
        st.info("No articles found for this filter. Try 'All' or hit Refresh.")
    else:
        for a in articles[:20]:
            st.markdown(render_news_card(a), unsafe_allow_html=True)

with side_col:
    # AI Summary
    st.markdown('<div class="section-title">AI Market Summary</div>', unsafe_allow_html=True)
    api_key = ""
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if st.button("✦ Summarise Today's Market", use_container_width=True):
        if not api_key:
            st.warning("Add ANTHROPIC_API_KEY to .streamlit/secrets.toml to enable AI summaries.")
        else:
            with st.spinner("Asking Claude…"):
                st.session_state["ai_summary"] = get_ai_summary(
                    [a["title"] for a in all_articles[:8]], api_key
                )

    if st.session_state.get("ai_summary"):
        st.markdown(
            f'<div class="ai-box">'
            f'<div class="ai-label">✦ Claude\'s Analysis</div>'
            f'{st.session_state["ai_summary"]}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Source breakdown
    st.markdown('<div class="section-title">News Sources</div>', unsafe_allow_html=True)
    for source, _ in RSS_FEEDS:
        count = sum(1 for a in all_articles if a["source"] == source)
        bar_w = int(count / max(1, max(
            sum(1 for a in all_articles if a["source"] == s) for s, _ in RSS_FEEDS
        )) * 100)
        st.markdown(
            f'<div style="padding:4px 0;border-bottom:1px solid rgba(139,92,246,0.07);">'
            f'<div style="display:flex;justify-content:space-between;font-size:0.76rem;">'
            f'<span style="color:#9ca3af">{source}</span>'
            f'<span style="color:#8b5cf6;font-weight:600">{count}</span></div>'
            f'<div style="height:2px;background:rgba(139,92,246,0.08);border-radius:2px;margin-top:3px;">'
            f'<div style="width:{bar_w}%;height:100%;background:#8b5cf6;border-radius:2px;"></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    ts = _now_ist().strftime("%I:%M %p IST")
    st.markdown(
        f'<div style="margin-top:1rem;font-size:0.68rem;color:#374151;text-align:center;">'
        f'Fetched at {ts} · headlines cache 30 min · market data 5 min</div>',
        unsafe_allow_html=True,
    )

# 5. Earnings Calendar
render_earnings(all_articles)

# Footer
st.markdown(
    '<div style="text-align:center;padding:2rem 0 1rem;color:#374151;font-size:0.7rem;">'
    'News: public RSS feeds · Calendar: Forex Factory · Market data: Yahoo Finance · '
    'No paid API required · SipCheck v2.0'
    '</div>',
    unsafe_allow_html=True,
)
