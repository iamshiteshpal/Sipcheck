# News page - placeholder
import streamlit as st
import feedparser
import requests
import os
from datetime import datetime

st.set_page_config(page_title="News — CAS 360", page_icon="📰", layout="wide")
from sidebar_v2 import render_sidebar
render_sidebar()


st.markdown("""
<style>
#MainMenu {visibility:hidden;} footer {visibility:hidden;}
.stApp { background:#0d0d24; color:#f0f0ff; }
section[data-testid="stSidebar"] { background:#0d0d24; border-right:1px solid rgba(139,92,246,0.15); }
.block-container { padding:1.5rem 2rem; }
.mkt-header { font-size:1.6rem; font-weight:700; color:#f0f0ff; margin-bottom:0.25rem; }
.mkt-sub { font-size:0.82rem; color:#6b7280; margin-bottom:1.5rem; }
.section-title {
    font-size:0.72rem; font-weight:600; color:#8b5cf6;
    text-transform:uppercase; letter-spacing:0.08em;
    margin:1.5rem 0 0.75rem; border-left:3px solid #8b5cf6; padding-left:10px;
}
.news-card {
    background:#111130; border:1px solid rgba(139,92,246,0.12);
    border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:0.5rem;
    border-left:3px solid #8b5cf6; transition:all 0.2s;
}
.news-card:hover { border-left-color:#10b981; }
.news-title {
    font-size:0.88rem; font-weight:500; color:#f0f0ff;
    line-height:1.4; margin-bottom:5px;
}
.news-title a { color:#f0f0ff; text-decoration:none; }
.news-title a:hover { color:#8b5cf6; }
.news-meta { font-size:0.72rem; color:#6b7280; }
.source-badge {
    display:inline-block; background:rgba(139,92,246,0.15);
    color:#8b5cf6; font-size:0.65rem; font-weight:600;
    padding:1px 7px; border-radius:8px; margin-right:6px;
}
.ai-box {
    background:#0a0a1f; border:1px solid rgba(139,92,246,0.3);
    border-radius:12px; padding:1rem 1.2rem; margin-bottom:1rem;
}
.ai-label { font-size:0.7rem; font-weight:700; color:#8b5cf6;
            text-transform:uppercase; letter-spacing:0.08em; margin-bottom:6px; }
.filter-pill {
    display:inline-block; background:#111130; border:1px solid rgba(139,92,246,0.2);
    border-radius:20px; padding:3px 12px; font-size:0.78rem;
    color:#9ca3af; margin:0 4px 6px 0; cursor:pointer;
}
</style>
""", unsafe_allow_html=True)

# ── RSS Sources — free, no API key, unlimited ─────────────────────────────────
RSS_FEEDS = [
    ("Economic Times", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
    ("Moneycontrol",   "https://www.moneycontrol.com/rss/latestnews.xml"),
    ("Business Standard","https://www.business-standard.com/rss/markets-106.rss"),
    ("LiveMint",       "https://www.livemint.com/rss/markets"),
]

FILTERS = {
    "All":         [],
    "Nifty/Sensex":["nifty","sensex","bse","nse","index"],
    "Mutual Funds":["mutual fund","nav","sip","amfi","scheme","mf"],
    "RBI/Policy":  ["rbi","repo","inflation","gdp","monetary","rupee","rbi"],
    "Gold":        ["gold","mcx","xauusd","precious"],
    "Global":      ["fed","us market","global","nasdaq","dow","s&p","china","europe"],
    "IT/Stocks":   ["infosys","tcs","wipro","hdfc","reliance","it sector","tech"],
}

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_rss(max_items=30):
    articles = []
    for source, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                pub = ""
                if hasattr(entry, "published"):
                    try:
                        from email.utils import parsedate_to_datetime
                        pub = parsedate_to_datetime(entry.published).strftime("%d %b, %I:%M %p")
                    except: pub = entry.get("published","")
                title = entry.get("title","").strip()
                if not title: continue
                articles.append({
                    "title":   title,
                    "source":  source,
                    "url":     entry.get("link","#"),
                    "pub":     pub,
                    "summary": entry.get("summary","")[:200] if hasattr(entry,"summary") else "",
                })
        except: continue
    seen, unique = set(), []
    for a in articles:
        k = a["title"][:40]
        if k not in seen: seen.add(k); unique.append(a)
    return unique[:max_items]

def filter_articles(articles, category):
    kws = FILTERS.get(category, [])
    if not kws: return articles
    out = [a for a in articles if any(k in (a["title"]+a.get("summary","")).lower() for k in kws)]
    return out if out else articles

def get_ai_summary(headlines, api_key):
    if not api_key: return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=200,
            messages=[{"role":"user","content":
                f"Summarise today's Indian financial market mood in 3 short sentences "
                f"based on these headlines:\n" + "\n".join(f"- {h}" for h in headlines[:6])}],
        )
        return msg.content[0].text.strip()
    except: return None

# ── PAGE ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="mkt-header">📰 Financial News</div>', unsafe_allow_html=True)
st.markdown('<div class="mkt-sub">Live headlines from Economic Times, Moneycontrol, Business Standard & LiveMint</div>',
            unsafe_allow_html=True)

# Refresh
c1, c2 = st.columns([8,1])
with c2:
    if st.button("↻ Refresh"):
        st.cache_data.clear(); st.rerun()

# Fetch news
with st.spinner("Loading latest headlines…"):
    all_articles = fetch_rss(30)

main_col, side_col = st.columns([2, 1])

with main_col:
    # Filter tabs
    sel_filter = st.radio("Filter by:", list(FILTERS.keys()),
                           horizontal=True, label_visibility="collapsed")
    articles = filter_articles(all_articles, sel_filter)

    st.markdown(f'<div class="section-title">{len(articles)} headlines · {sel_filter}</div>',
                unsafe_allow_html=True)

    if not articles:
        st.info("No articles found. Try 'All' or refresh.")
    else:
        for a in articles[:15]:
            st.markdown(f"""
            <div class="news-card">
                <div class="news-title">
                    <a href="{a['url']}" target="_blank">{a['title']}</a>
                </div>
                <div class="news-meta">
                    <span class="source-badge">{a['source']}</span>
                    {a['pub']}
                </div>
            </div>""", unsafe_allow_html=True)

with side_col:
    st.markdown('<div class="section-title">AI Market Summary</div>', unsafe_allow_html=True)

    api_key = ""
    try: api_key = st.secrets.get("ANTHROPIC_API_KEY","")
    except: api_key = os.getenv("ANTHROPIC_API_KEY","")

    if st.button("✦ Summarise Today's Market", use_container_width=True):
        if not api_key:
            st.warning("Add ANTHROPIC_API_KEY to .streamlit/secrets.toml to enable AI summaries.")
        else:
            with st.spinner("Asking Claude…"):
                headlines = [a["title"] for a in all_articles[:6]]
                summary = get_ai_summary(headlines, api_key)
            if summary:
                st.session_state["ai_summary"] = summary

    if "ai_summary" in st.session_state:
        st.markdown(f"""
        <div class="ai-box">
            <div class="ai-label">✦ Claude's Analysis</div>
            {st.session_state['ai_summary']}
        </div>""", unsafe_allow_html=True)

    # Source breakdown
    st.markdown('<div class="section-title">Sources</div>', unsafe_allow_html=True)
    for source, _ in RSS_FEEDS:
        count = sum(1 for a in all_articles if a["source"]==source)
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:5px 0;
                    border-bottom:1px solid rgba(139,92,246,0.1);font-size:0.8rem;">
            <span style="color:#9ca3af">{source}</span>
            <span style="color:#8b5cf6;font-weight:600">{count}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:1rem;font-size:0.72rem;color:#374151;text-align:center;">
        Last fetched {datetime.now().strftime("%I:%M %p")}
    </div>""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;color:#374151;font-size:0.72rem;">
    News sourced from public RSS feeds · No API key required · Refreshes every 30 min
</div>""", unsafe_allow_html=True)