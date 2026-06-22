"""News & Pulse — SipCheck v3.0  (RSS-only, zero API keys)"""
import streamlit as st
import feedparser
import requests
import re
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
    def _now(): return datetime.now(IST)
except ImportError:
    import pytz
    IST = pytz.timezone("Asia/Kolkata")
    def _now(): return datetime.now(IST)

st.set_page_config(page_title="News & Pulse — SipCheck", page_icon="📰", layout="wide")
from sidebar_v2 import render_sidebar
from theme import apply_theme, theme_toggle_button
render_sidebar()
apply_theme()

# ── Constants ─────────────────────────────────────────────────────────────────

BULLISH_KW = [
    "rally","surge","soar","gain","rise","bull","high","record","jump","climb",
    "positive","strong","growth","profit","beat","boost","recover","advance","green",
]
BEARISH_KW = [
    "fall","drop","crash","decline","down","bear","low","slip","tank","plunge",
    "sink","weak","loss","miss","drag","selloff","pressure","slide","tumble","red",
]

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

SOURCE_COLORS = {
    "Economic Times":    "#f59e0b",
    "Moneycontrol":      "#3b82f6",
    "Business Standard": "#8b5cf6",
    "LiveMint":          "#10b981",
    "Reuters India":     "#ef4444",
    "NDTV Profit":       "#06b6d4",
    "CNBC TV18":         "#f97316",
    "Financial Express": "#a855f7",
}

SECTORS = {
    "Banking":  ["hdfc bank","sbi","icici","kotak","axis bank","indusind","pnb","banking","bank nifty"],
    "IT":       ["tcs","infosys","wipro","hcl","tech mahindra","ltimindtree","nifty it","it sector"],
    "Pharma":   ["sun pharma","dr reddy","cipla","divis","lupin","biocon","pharma"],
    "Auto":     ["tata motors","maruti","bajaj auto","hero motocorp","mahindra","eicher","tvs motor"],
    "FMCG":     ["hul","itc","nestle","britannia","dabur","marico","fmcg"],
    "Energy":   ["reliance","ongc","bpcl","ntpc","power grid","coal india","adani power"],
    "Metal":    ["tata steel","hindalco","jsw steel","sail","vedanta","metal"],
    "Realty":   ["dlf","godrej prop","prestige","brigade","sobha","realty"],
}

SECTOR_PALETTE = {
    "Banking": "#3b82f6", "IT": "#8b5cf6", "Pharma": "#10b981",
    "Auto": "#f59e0b",   "FMCG": "#ec4899", "Energy": "#f97316",
    "Metal": "#6b7280",  "Realty": "#06b6d4",
}

CATEGORIES = {
    "All":          [],
    "Equities":     ["nifty","sensex","bse","nse","stock","equity","share","index"],
    "Mutual Funds": ["mutual fund","nav","sip","amfi","scheme","fund house","amc"],
    "RBI / Policy": ["rbi","repo","inflation","gdp","monetary","policy","rate cut","rate hike","mpc"],
    "Global":       ["fed","us market","global","nasdaq","dow","s&p","china","europe","dollar","forex"],
    "Commodities":  ["gold","silver","crude","oil","commodity","mcx","copper"],
    "IPO / NFO":    ["ipo","nfo","new fund offer","listing","allotment","subscription"],
    "Crypto":       ["bitcoin","crypto","ethereum","blockchain","btc","eth","defi","web3"],
}

STOP_WORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with","by","from",
    "is","are","was","were","be","been","has","have","had","will","would","could","should",
    "this","that","these","those","it","its","as","up","down","over","under","after","before",
    "than","then","also","if","not","all","more","new","says","said","say","can","may","via",
    "amid","after","we","our","you","your","their","which","who","its","into","out","about",
}


# ── Data ──────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_rss(max_per_feed=12):
    articles = []
    for source, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                pub_dt = None
                if hasattr(entry, "published"):
                    try:
                        pub_dt = parsedate_to_datetime(entry.published)
                    except Exception:
                        pass
                title = entry.get("title", "").strip()
                if not title:
                    continue
                summary = ""
                if hasattr(entry, "summary") and entry.summary:
                    summary = re.sub(r"<[^>]+>", "", entry.summary)[:300]
                articles.append({
                    "title":  title,
                    "source": source,
                    "url":    entry.get("link", "#"),
                    "pub_dt": pub_dt,
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


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_econ_calendar():
    try:
        r = requests.get(
            "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
            headers={"User-Agent": "Mozilla/5.0 SipCheck/3.0"},
            timeout=10,
        )
        if r.status_code == 200:
            return [
                e for e in r.json()
                if e.get("impact") in ("High", "Medium")
                and e.get("country", "").upper() in ("USD","INR","EUR","GBP","JPY","CNY","AUD")
            ]
    except Exception:
        pass
    return []


# ── Analysis helpers ──────────────────────────────────────────────────────────

def _text(a):
    return (a["title"] + " " + a.get("summary", "")).lower()


def analyze_sentiment(articles):
    bull = bear = 0
    sector_counts = {s: 0 for s in SECTORS}
    source_counts = Counter()
    for a in articles:
        t = _text(a)
        bull += sum(1 for k in BULLISH_KW if k in t)
        bear += sum(1 for k in BEARISH_KW if k in t)
        source_counts[a["source"]] += 1
        for sec, kws in SECTORS.items():
            if any(k in t for k in kws):
                sector_counts[sec] += 1
    top_sec = max(sector_counts, key=sector_counts.get) if any(sector_counts.values()) else "Mixed"
    top_src = source_counts.most_common(1)[0][0] if source_counts else "—"
    total = bull + bear
    score = (bull / total * 100) if total else 50
    if   score >= 65: mood, mc = "Bullish",       "#10b981"
    elif score >= 55: mood, mc = "Mildly Bullish", "#34d399"
    elif score >= 45: mood, mc = "Neutral",        "#9ca3af"
    elif score >= 35: mood, mc = "Mildly Bearish", "#fbbf24"
    else:             mood, mc = "Bearish",         "#ef4444"
    return dict(bull=bull, bear=bear, score=score, mood=mood, mood_color=mc,
                top_sector=top_sec, top_source=top_src,
                sector_counts=sector_counts, source_counts=source_counts)


def get_trending(articles, n=8):
    words = Counter()
    for a in articles:
        for w in re.sub(r"[^a-z\s]", " ", a["title"].lower()).split():
            if len(w) >= 4 and w not in STOP_WORDS:
                words[w] += 1
    return [w for w, _ in words.most_common(n)]


def article_sentiment(a):
    t = _text(a)
    b = sum(1 for k in BULLISH_KW if k in t)
    d = sum(1 for k in BEARISH_KW if k in t)
    if b > d:   return "#10b981"
    if d > b:   return "#ef4444"
    return "#6b7280"


def rel_time(pub_dt):
    if not pub_dt:
        return ""
    try:
        now = datetime.now(pub_dt.tzinfo) if pub_dt.tzinfo else datetime.now(timezone.utc)
        mins = max(0, int((now - pub_dt).total_seconds() / 60))
        if mins < 60:   return f"{mins}m ago"
        if mins < 1440: return f"{mins//60}h ago"
        return f"{mins//1440}d ago"
    except Exception:
        return ""


def _hex_rgb(h):
    h = h.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


def _parse_ff_date(s):
    try:
        s2 = re.sub(r'([+-]\d{2})(\d{2})$', r'\1:\2', str(s))
        d  = datetime.fromisoformat(s2)
        try:
            return d.astimezone(IST)
        except Exception:
            return d
    except Exception:
        return None


# ── CSS ───────────────────────────────────────────────────────────────────────

def _css():
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

#MainMenu{visibility:hidden;} footer{visibility:hidden;}
.stApp{background:#0d0d24;color:#f0f0ff;font-family:'Inter',sans-serif;}
section[data-testid="stSidebar"]{background:#0d0d24;border-right:1px solid rgba(139,92,246,0.15);}
.block-container{padding:1.1rem 2rem 2rem;}

/* ── Breaking news carousel ── */
.car-wrap{
    background:linear-gradient(135deg,rgba(139,92,246,0.1),rgba(16,185,129,0.06));
    border:1px solid rgba(139,92,246,0.28);border-radius:14px;
    padding:0.85rem 1.3rem 2.2rem;margin-bottom:1rem;
    position:relative;overflow:hidden;min-height:88px;
}
.car-label{font-size:0.6rem;font-weight:700;color:#ef4444;
           text-transform:uppercase;letter-spacing:0.12em;margin-bottom:8px;
           display:flex;align-items:center;gap:5px;}
.car-dot-live{width:6px;height:6px;background:#ef4444;border-radius:50%;
              animation:livePulse 1.4s ease-in-out infinite;}
@keyframes livePulse{0%,100%{opacity:1;transform:scale(1);}50%{opacity:0.4;transform:scale(0.7);}}
.car-slide{
    position:absolute;width:calc(100% - 2.6rem);
    opacity:0;animation:cSlide 12s infinite ease-in-out;
}
.car-slide:nth-child(1){animation-delay:0s;}
.car-slide:nth-child(2){animation-delay:4s;}
.car-slide:nth-child(3){animation-delay:8s;}
@keyframes cSlide{
    0%,3%{opacity:0;transform:translateY(10px);}
    9%,27%{opacity:1;transform:translateY(0);}
    33%,100%{opacity:0;transform:translateY(-10px);}
}
.car-headline{font-size:0.92rem;font-weight:600;color:#f0f0ff;line-height:1.42;}
.car-headline a{color:#f0f0ff;text-decoration:none;}
.car-headline a:hover{color:#8b5cf6;}
.car-meta{font-size:0.68rem;color:#6b7280;margin-top:3px;}
.car-dots{
    position:absolute;bottom:0.6rem;left:50%;transform:translateX(-50%);
    display:flex;gap:6px;
}
.c-dot{
    width:6px;height:6px;border-radius:3px;
    background:rgba(139,92,246,0.25);
    animation:dotAct 12s infinite ease-in-out;transition:all 0.3s;
}
.c-dot:nth-child(1){animation-delay:0s;}
.c-dot:nth-child(2){animation-delay:4s;}
.c-dot:nth-child(3){animation-delay:8s;}
@keyframes dotAct{
    0%,8%{background:rgba(139,92,246,0.25);width:6px;}
    12%,28%{background:#8b5cf6;width:18px;box-shadow:0 0 6px rgba(139,92,246,0.5);}
    33%,100%{background:rgba(139,92,246,0.25);width:6px;}
}

/* ── Mood card ── */
.mood-card{
    background:linear-gradient(135deg,rgba(15,15,40,0.98),rgba(17,17,48,0.95));
    border:1px solid rgba(139,92,246,0.18);border-radius:14px;
    padding:1rem 1.25rem;
}
.mood-hdr{font-size:0.62rem;font-weight:700;color:#8b5cf6;
          text-transform:uppercase;letter-spacing:0.1em;margin-bottom:7px;}
.mood-txt{font-size:0.86rem;color:#e5e7eb;font-weight:500;line-height:1.5;margin-bottom:10px;}
.mood-bar-bg{background:rgba(255,255,255,0.06);border-radius:20px;height:8px;
             position:relative;margin-bottom:3px;overflow:visible;}
.mood-fill{height:100%;border-radius:20px;
           background:linear-gradient(90deg,#ef4444 0%,#f59e0b 40%,#10b981 100%);}
.mood-pin{
    position:absolute;top:50%;transform:translate(-50%,-50%);
    width:14px;height:14px;border-radius:50%;border:2px solid #0d0d24;
}
.mood-lbl{display:flex;justify-content:space-between;
          font-size:0.6rem;color:#4b5563;margin-top:3px;}
.mood-nums{font-size:0.72rem;color:#9ca3af;margin-top:7px;
           font-family:'JetBrains Mono',monospace;}

/* ── Stats strip ── */
.stats-strip{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:0.9rem;}
.stat-cell{background:#111130;border:1px solid rgba(139,92,246,0.1);
           border-radius:10px;padding:0.6rem 0.8rem;text-align:center;}
.stat-v{font-size:1.05rem;font-weight:800;color:#f0f0ff;
        font-family:'JetBrains Mono',monospace;line-height:1.2;}
.stat-l{font-size:0.58rem;color:#6b7280;margin-top:2px;letter-spacing:0.04em;text-transform:uppercase;}

/* ── Trending pills ── */
.trend-wrap{display:flex;gap:7px;flex-wrap:wrap;margin:0.5rem 0 1rem;}
.t-pill{
    display:inline-block;background:rgba(139,92,246,0.07);
    border:1px solid rgba(139,92,246,0.18);border-radius:20px;
    padding:3px 11px;font-size:0.73rem;color:#c4b5fd;font-weight:500;
    white-space:nowrap;
}

/* ── Source radio → pill look ── */
div[data-testid="stRadio"] label{
    background:rgba(139,92,246,0.06)!important;border:1px solid rgba(139,92,246,0.15)!important;
    border-radius:20px!important;padding:3px 12px!important;margin:0 3px 4px 0!important;
    font-size:0.74rem!important;color:#9ca3af!important;cursor:pointer!important;
    transition:all 0.15s!important;
}
div[data-testid="stRadio"] label:hover{
    border-color:rgba(139,92,246,0.4)!important;color:#f0f0ff!important;
    box-shadow:0 0 7px rgba(139,92,246,0.2)!important;
}
div[data-testid="stRadio"] [data-baseweb="radio"] input:checked + div + label,
div[data-testid="stRadio"] label[aria-checked="true"]{
    background:rgba(139,92,246,0.22)!important;border-color:#8b5cf6!important;
    color:#f0f0ff!important;box-shadow:0 0 10px rgba(139,92,246,0.3)!important;
}
div[data-testid="stRadio"] [data-baseweb="radio"] div[class*="checkmark"]{display:none!important;}
div[data-testid="stRadio"] > div{display:flex!important;flex-wrap:wrap!important;gap:0!important;}
div[data-testid="stRadio"] > label{display:none!important;}

/* ── News card ── */
.nc{
    background:#111130;border:1px solid rgba(139,92,246,0.1);
    border-radius:10px;padding:0.7rem 0.85rem;margin-bottom:0.4rem;
    transition:border-color 0.18s,box-shadow 0.18s,transform 0.18s;
    display:flex;flex-direction:column;gap:6px;
    word-wrap:break-word;overflow-wrap:break-word;overflow:visible;
}
.nc:hover{
    border-color:rgba(139,92,246,0.38);
    box-shadow:0 4px 18px rgba(139,92,246,0.13);
    transform:translateY(-1px);
}
.nc-hl{font-size:0.81rem;font-weight:500;color:#f0f0ff;line-height:1.45;
        word-wrap:break-word;overflow-wrap:break-word;white-space:normal;}
.nc-hl a{color:#f0f0ff;text-decoration:none;}
.nc-hl a:hover{color:#8b5cf6;}
.nc-foot{display:flex;align-items:center;gap:5px;margin-top:5px;}
.nc-sdot{width:6px;height:6px;border-radius:50%;flex-shrink:0;}
.nc-src{font-size:0.58rem;font-weight:700;padding:1px 5px;border-radius:5px;letter-spacing:0.03em;}
.nc-ts{font-size:0.62rem;color:#4b5563;font-family:'JetBrains Mono',monospace;margin-left:auto;}

/* ── Bookmark button miniaturize ── */
div[data-testid="column"] div[data-testid="stButton"] > button[title="bm"]{
    background:transparent!important;border:none!important;
    padding:0!important;font-size:0.75rem!important;
    color:#4b5563!important;min-height:0!important;height:auto!important;
    line-height:1!important;
}

/* ── Econ horizontal scroll ── */
.econ-scroll{display:flex;gap:10px;overflow-x:auto;padding:4px 2px 10px;
             scrollbar-width:thin;scrollbar-color:rgba(139,92,246,0.25) transparent;}
.econ-scroll::-webkit-scrollbar{height:4px;}
.econ-scroll::-webkit-scrollbar-thumb{background:rgba(139,92,246,0.25);border-radius:2px;}
.eh-card{
    flex-shrink:0;width:138px;background:#0f0f2a;
    border:1px solid rgba(139,92,246,0.13);border-radius:10px;
    padding:0.65rem 0.75rem;
}
.eh-imp{font-size:0.7rem;margin-bottom:3px;}
.eh-title{font-size:0.75rem;font-weight:600;color:#f0f0ff;line-height:1.3;
          margin-bottom:4px;display:-webkit-box;-webkit-line-clamp:2;
          -webkit-box-orient:vertical;overflow:hidden;}
.eh-date{font-size:0.6rem;color:#8b5cf6;font-weight:600;
         font-family:'JetBrains Mono',monospace;margin-bottom:3px;}
.eh-vals{font-size:0.6rem;color:#6b7280;}
.eh-vals strong{color:#10b981;}

/* ── Sector heatmap ── */
.sec-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:1rem;}
.sec-cell{border-radius:10px;padding:0.7rem 0.85rem;text-align:center;transition:transform 0.2s;}
.sec-cell:hover{transform:scale(1.03);}
.sec-n{font-size:0.76rem;font-weight:600;color:#f0f0ff;margin-bottom:2px;}
.sec-c{font-size:1rem;font-weight:800;font-family:'JetBrains Mono',monospace;}
.sec-l{font-size:0.57rem;color:rgba(255,255,255,0.35);margin-top:1px;}

/* ── Bookmark section ── */
.bm-card{background:#0f0f2a;border:1px solid rgba(245,158,11,0.18);
         border-left:3px solid #f59e0b;border-radius:8px;
         padding:0.6rem 0.85rem;margin-bottom:0.35rem;}
.bm-card a{font-size:0.81rem;color:#f0f0ff;text-decoration:none;}
.bm-card a:hover{color:#f59e0b;}
.bm-src{font-size:0.64rem;color:#6b7280;margin-top:2px;}

/* ── Section label ── */
.slbl{font-size:0.65rem;font-weight:700;color:#8b5cf6;text-transform:uppercase;
      letter-spacing:0.1em;margin:1.1rem 0 0.6rem;border-left:3px solid #8b5cf6;padding-left:8px;}

/* ── Tabs glass style ── */
.stTabs [data-baseweb="tab-list"]{
    background:#111130;border-radius:10px;padding:3px;gap:2px;
    border:1px solid rgba(139,92,246,0.1);
}
.stTabs [data-baseweb="tab"]{
    background:transparent!important;border-radius:8px!important;
    color:#6b7280!important;font-size:0.76rem!important;
    font-weight:500!important;padding:5px 13px!important;border:none!important;
}
.stTabs [aria-selected="true"]{
    background:rgba(139,92,246,0.2)!important;color:#f0f0ff!important;
    font-weight:600!important;
}
.stTabs [data-baseweb="tab-highlight"]{display:none!important;}
.stTabs [data-baseweb="tab-border"]{display:none!important;}

/* ── Load more button ── */
div[data-testid="stButton"] > button[kind="secondary"]{
    background:rgba(139,92,246,0.08)!important;
    border:1px solid rgba(139,92,246,0.2)!important;
    border-radius:20px!important;color:#c4b5fd!important;
    font-size:0.78rem!important;padding:6px 20px!important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover{
    background:rgba(139,92,246,0.18)!important;
    border-color:rgba(139,92,246,0.45)!important;color:#f0f0ff!important;
}

/* ── MOBILE RESPONSIVE ── */
@media (max-width: 768px) {
    .block-container{padding:0.6rem 0.8rem 2rem!important;}
    /* Stats strip: 2 cols instead of 4 */
    .stats-strip{grid-template-columns:repeat(2,1fr)!important;}
    /* Sector heatmap: 2 cols instead of 4 */
    .sec-grid{grid-template-columns:repeat(2,1fr)!important;}
    /* Breaking news carousel: remove fixed min-height */
    .car-wrap{min-height:auto!important;padding:0.7rem 1rem 2.2rem!important;}
    /* News cards: tighter padding */
    .nc{padding:0.55rem 0.7rem!important;}
    .nc-hl{font-size:0.78rem!important;}
    /* Stack ALL Streamlit columns vertically (news grid, mood+sectors, header) */
    div[data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:5px!important;}
    div[data-testid="stHorizontalBlock"]>div[data-testid="column"]{
        min-width:100%!important;flex:none!important;width:100%!important;
    }
    /* Make econ calendar scroll cards slightly smaller */
    .eh-card{width:120px!important;}
    .stButton>button{min-height:44px;}
}
@media (max-width: 480px) {
    .nc-hl{font-size:0.75rem!important;}
    .stat-v{font-size:0.9rem!important;}
    .mood-txt{font-size:0.78rem!important;}
}
</style>""", unsafe_allow_html=True)


# ── Section renderers ─────────────────────────────────────────────────────────

def render_carousel(articles):
    top3 = articles[:3]
    if not top3:
        return
    slides = ""
    for a in top3:
        sc = SOURCE_COLORS.get(a["source"], "#8b5cf6")
        rt = rel_time(a.get("pub_dt"))
        slides += (
            f'<div class="car-slide">'
            f'<div class="car-headline"><a href="{a["url"]}" target="_blank">{a["title"]}</a></div>'
            f'<div class="car-meta">'
            f'<span style="color:{sc};font-weight:600;">{a["source"]}</span>'
            f'{"&nbsp;·&nbsp;" + rt if rt else ""}'
            f'</div></div>'
        )
    st.markdown(
        f'<div class="car-wrap">'
        f'<div class="car-label"><div class="car-dot-live"></div>Breaking News</div>'
        f'{slides}'
        f'<div class="car-dots"><div class="c-dot"></div><div class="c-dot"></div><div class="c-dot"></div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_mood_card(sent):
    sc, bull, bear = sent["score"], sent["bull"], sent["bear"]
    mood, mc = sent["mood"], sent["mood_color"]
    sec       = sent["top_sector"]
    total     = bull + bear

    if   sc >= 60: txt = f"Markets showing <strong style='color:{mc}'>{mood.lower()}</strong> sentiment · {bull} positive vs {bear} negative signals · {sec} sector most active"
    elif sc <= 40: txt = f"Markets showing <strong style='color:{mc}'>{mood.lower()}</strong> sentiment · {bear} negative vs {bull} positive signals · {sec} sector under pressure"
    else:          txt = f"Markets <strong style='color:{mc}'>mixed</strong> · {bull} positive vs {bear} negative signals · {sec} sector most active · Watch key levels"

    st.markdown(
        f'<div class="mood-card">'
        f'<div class="mood-hdr">📊 Auto Market Summary</div>'
        f'<div class="mood-txt">{txt}</div>'
        f'<div class="mood-bar-bg">'
        f'<div class="mood-fill" style="width:{sc:.0f}%;height:100%;"></div>'
        f'<div class="mood-pin" style="left:{sc:.0f}%;background:{mc};color:{mc};box-shadow:0 0 8px {mc};"></div>'
        f'</div>'
        f'<div class="mood-lbl"><span>◀ Bearish</span><span>Neutral</span><span>Bullish ▶</span></div>'
        f'<div class="mood-nums">'
        f'<span style="color:{mc};font-weight:700;">{mood}</span>&nbsp;·&nbsp;'
        f'<span style="color:#10b981;">▲ {bull} bullish</span>&nbsp;·&nbsp;'
        f'<span style="color:#ef4444;">▼ {bear} bearish</span>&nbsp;·&nbsp;'
        f'{total} signals'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def render_stats_strip(articles, sent):
    total    = len(articles)
    top_src  = sent["top_source"]
    co_kws   = {
        "Reliance": ["reliance"], "HDFC": ["hdfc bank"], "TCS": ["tcs"],
        "Infosys": ["infosys"], "SBI": ["sbi "], "ICICI": ["icici"],
        "Nifty": ["nifty"], "RBI": ["rbi "],
    }
    co_cnt = Counter()
    for a in articles:
        t = a["title"].lower()
        for co, kws in co_kws.items():
            if any(k in t for k in kws):
                co_cnt[co] += 1
    top_co   = co_cnt.most_common(1)[0][0] if co_cnt else "—"
    bull_col = "#10b981" if sent["score"] >= 50 else "#ef4444"

    st.markdown(
        f'<div class="stats-strip">'
        f'<div class="stat-cell"><div class="stat-v">{total}</div><div class="stat-l">Headlines</div></div>'
        f'<div class="stat-cell"><div class="stat-v" style="font-size:0.82rem;">{top_src.split()[0]}</div><div class="stat-l">Top Source</div></div>'
        f'<div class="stat-cell"><div class="stat-v" style="font-size:0.88rem;">{top_co}</div><div class="stat-l">Most Mentioned</div></div>'
        f'<div class="stat-cell"><div class="stat-v" style="color:{bull_col};">{sent["score"]:.0f}%</div><div class="stat-l">Bullish Score</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_trending(articles):
    topics = get_trending(articles, n=8)
    if not topics:
        return
    pills = "".join(f'<span class="t-pill">#{w.title()}</span>' for w in topics)
    st.markdown(f'<div class="slbl">🔥 Trending Topics</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="trend-wrap">{pills}</div>', unsafe_allow_html=True)


def render_news_grid(articles, cat_key="all"):
    if "bookmarks" not in st.session_state:
        st.session_state["bookmarks"] = []

    show_key = f"show_all_{cat_key}"
    if show_key not in st.session_state:
        st.session_state[show_key] = False

    display = articles if st.session_state[show_key] else articles[:12]

    if not display:
        st.markdown(
            '<div style="color:#6b7280;font-size:0.82rem;padding:0.8rem 0;">'
            'No articles found for this filter.</div>',
            unsafe_allow_html=True,
        )
        return

    bm_urls = {b["url"] for b in st.session_state["bookmarks"]}

    for row_start in range(0, len(display), 3):
        batch = display[row_start:row_start + 3]
        cols  = st.columns(3)
        for col, a in zip(cols, batch):
            with col:
                sc   = SOURCE_COLORS.get(a["source"], "#8b5cf6")
                rt   = rel_time(a.get("pub_dt"))
                sdot = article_sentiment(a)
                is_bm = a["url"] in bm_urls
                src_short = a["source"].split()[0]

                st.markdown(
                    f'<div class="nc">'
                    f'<div class="nc-hl"><a href="{a["url"]}" target="_blank">{a["title"]}</a></div>'
                    f'<div class="nc-foot">'
                    f'<div class="nc-sdot" style="background:{sdot};box-shadow:0 0 4px {sdot};"></div>'
                    f'<span class="nc-src" style="background:{sc}20;color:{sc};">{src_short}</span>'
                    f'<span class="nc-ts">{rt}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
                bm_lbl = "🔖" if is_bm else "🔗"
                if st.button(bm_lbl, key=f"bm_{cat_key}_{a['url'][-28:]}", help="bm"):
                    if a["url"] in bm_urls:
                        st.session_state["bookmarks"] = [
                            b for b in st.session_state["bookmarks"] if b["url"] != a["url"]
                        ]
                    else:
                        st.session_state["bookmarks"].append(a)
                    st.rerun()

    remaining = len(articles) - 12
    if not st.session_state[show_key] and remaining > 0:
        _, mc, _ = st.columns([2, 1, 2])
        with mc:
            if st.button(f"Load {remaining} more ↓", key=f"load_{cat_key}", use_container_width=True):
                st.session_state[show_key] = True
                st.rerun()
    elif st.session_state[show_key] and remaining > 0:
        _, mc, _ = st.columns([2, 1, 2])
        with mc:
            if st.button("Show less ↑", key=f"less_{cat_key}", use_container_width=True):
                st.session_state[show_key] = False
                st.rerun()


def render_econ_horizontal(events):
    st.markdown('<div class="slbl">📅 Economic Calendar — This Week</div>', unsafe_allow_html=True)
    if not events:
        st.markdown(
            '<div style="color:#6b7280;font-size:0.8rem;">'
            'Calendar unavailable. <a href="https://www.forexfactory.com/calendar" '
            'target="_blank" style="color:#8b5cf6;">Forex Factory ↗</a></div>',
            unsafe_allow_html=True,
        )
        return

    show_full = st.session_state.get("econ_full", False)
    pool      = events if show_full else events[:7]
    now       = _now()

    cards = ""
    for e in pool:
        impact  = e.get("impact", "")
        d       = _parse_ff_date(e.get("date", ""))
        if not d:
            continue
        try:
            is_past = d < now
        except Exception:
            is_past = False
        dot      = "🔴" if impact == "High" else "🟡"
        date_str = d.strftime("%d %b %H:%M")
        actual   = e.get("actual", "")
        fore     = e.get("forecast", "—")
        prev_v   = e.get("previous", "—")
        val_html = (f'<strong>{actual}</strong>' if actual
                    else f'F:{fore} P:{prev_v}')
        op = "0.42" if is_past else "1"
        cards += (
            f'<div class="eh-card" style="opacity:{op};">'
            f'<div class="eh-imp">{dot} <span style="font-size:0.58rem;color:#6b7280;">{e.get("country","")}</span></div>'
            f'<div class="eh-title">{e.get("title","")}</div>'
            f'<div class="eh-date">{date_str} IST</div>'
            f'<div class="eh-vals">{val_html}</div>'
            f'</div>'
        )

    st.markdown(f'<div class="econ-scroll">{cards}</div>', unsafe_allow_html=True)
    lbl = f"Show all {len(events)} events ▸" if not show_full else "Show less ▴"
    if st.button(lbl, key="econ_tog"):
        st.session_state["econ_full"] = not show_full
        st.rerun()


def render_sector_heatmap(articles):
    st.markdown('<div class="slbl">🏭 Sector Heatmap</div>', unsafe_allow_html=True)
    counts = {s: 0 for s in SECTORS}
    for a in articles:
        t = _text(a)
        for sec, kws in SECTORS.items():
            if any(k in t for k in kws):
                counts[sec] += 1
    mx = max(counts.values()) if any(counts.values()) else 1
    cells = ""
    for sec, cnt in counts.items():
        base  = SECTOR_PALETTE.get(sec, "#8b5cf6")
        rgb   = _hex_rgb(base)
        inten = cnt / mx
        bg    = f"rgba({rgb},{0.05 + inten * 0.35:.2f})"
        bord  = f"rgba({rgb},{0.08 + inten * 0.38:.2f})"
        col   = base if inten > 0.05 else "#374151"
        cells += (
            f'<div class="sec-cell" style="background:{bg};border:1px solid {bord};">'
            f'<div class="sec-n" style="color:{col};">{sec}</div>'
            f'<div class="sec-c" style="color:{base};">{cnt}</div>'
            f'<div class="sec-l">mentions</div>'
            f'</div>'
        )
    st.markdown(f'<div class="sec-grid">{cells}</div>', unsafe_allow_html=True)


def render_bookmarks():
    bms = st.session_state.get("bookmarks", [])
    if not bms:
        return
    st.markdown('<div class="slbl">🔖 Bookmarks</div>', unsafe_allow_html=True)
    for b in bms:
        st.markdown(
            f'<div class="bm-card">'
            f'<a href="{b["url"]}" target="_blank">{b["title"]}</a>'
            f'<div class="bm-src">{b["source"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    if st.button("✕ Clear all bookmarks", key="clr_bm"):
        st.session_state["bookmarks"] = []
        st.rerun()


# ── Page ──────────────────────────────────────────────────────────────────────

_css()

# Header
h1, h2 = st.columns([10, 1])
with h1:
    st.markdown(
        '<div style="font-size:1.5rem;font-weight:800;color:#f0f0ff;margin-bottom:0.1rem;">📰 News & Pulse</div>'
        '<div style="font-size:0.78rem;color:#4b5563;margin-bottom:0.7rem;">'
        'Live market intelligence · 8 RSS sources · keyword-powered · zero API keys</div>',
        unsafe_allow_html=True,
    )
with h2:
    if st.button("↻", help="Refresh"):
        st.cache_data.clear()
        st.rerun()

# Fetch
with st.spinner("Loading headlines…"):
    all_articles = fetch_rss(max_per_feed=12)
    econ_events  = fetch_econ_calendar()

sent    = analyze_sentiment(all_articles)
sources = ["All"] + [s for s, _ in RSS_FEEDS]

# 1. Breaking News Carousel
render_carousel(all_articles)

# 2. Mood + Stats | Sector heatmap
left, right = st.columns([3, 2])
with left:
    render_mood_card(sent)
    render_stats_strip(all_articles, sent)
with right:
    render_sector_heatmap(all_articles)
    render_econ_horizontal(econ_events)

# 3. Trending topics
render_trending(all_articles)

# 4. Source filter pills
st.markdown('<div class="slbl">Sources</div>', unsafe_allow_html=True)
src_counts = Counter(a["source"] for a in all_articles)
src_labels = ["All"] + [f"{s}  {src_counts.get(s,0)}" for s, _ in RSS_FEEDS]
sel_src = st.radio("src", src_labels, horizontal=True, label_visibility="collapsed")
active_src = "" if sel_src == "All" else sel_src.rsplit("  ", 1)[0]

# 5. Category tabs + news grid
st.markdown('<div class="slbl">Headlines</div>', unsafe_allow_html=True)
tabs = st.tabs(list(CATEGORIES.keys()))
for tab, (cat, kws) in zip(tabs, CATEGORIES.items()):
    with tab:
        filtered = all_articles
        if active_src:
            filtered = [a for a in filtered if a["source"] == active_src]
        if kws:
            filtered = [a for a in filtered
                        if any(k in _text(a) for k in kws)]
        cat_key  = re.sub(r"\W+", "_", cat.lower())
        render_news_grid(filtered, cat_key=cat_key)

# 6. Bookmarks
render_bookmarks()

# Footer
st.markdown(
    '<div style="text-align:center;padding:1.5rem 0 0.3rem;color:#374151;font-size:0.67rem;">'
    'Data: 8 public RSS feeds · Calendar: Forex Factory free API · '
    'No paid API key required · auto-refreshes every 30 min · SipCheck v3.0'
    '</div>',
    unsafe_allow_html=True,
)
