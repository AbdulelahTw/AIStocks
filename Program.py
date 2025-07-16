import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ── 1. PAGE & DATA PATHS ────────────────────────
st.set_page_config(page_title="AI Market Dashboard", layout="wide")
DATA_DIR = "data"
STOCK_CSV = os.path.join(DATA_DIR, "ai_stock_data.csv")
NEWS_CSV = os.path.join(DATA_DIR, "ai_news_feed.csv")

# ── 2. LOAD DATA ────────────────────────────────
stocks = pd.read_csv(STOCK_CSV, parse_dates=["Date"])
news = pd.read_csv(NEWS_CSV).dropna(subset=["Title", "URL"])

# ── 3. HEADER ───────────────────────────────────
st.markdown("""
    <h1 style='font-size:2.5rem; font-weight:800; letter-spacing:-2px; margin-bottom:0; color:white'>
         AI Market Intelligence Dashboard
    </h1>
    <span style='font-size:1.2rem; color: #aaa;'>All your AI market insights. One snap.</span>
    <br><br>
""", unsafe_allow_html=True)

# ── 4. TICKER SELECTOR (NVDA as default) ────────
tickers = stocks["Ticker"].unique().tolist()
default_ticker = "NVDA" if "NVDA" in tickers else tickers[0]
ticker = st.selectbox("Select ticker", tickers, index=tickers.index(default_ticker))
sel_df = stocks[stocks["Ticker"] == ticker].copy()
latest = sel_df.iloc[-1]

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# ── 5. METRIC STRIP ────────────────────────────
mcol1, mcol2, mcol3 = st.columns([2,2,2])
mcol1.metric("1‑Day %", f"{latest['% Change (1d)']:.2f}%")
mcol2.metric("5‑Day %", f"{latest['% Change (5d)']:.2f}%")
mcol3.metric("Last Close", f"${latest['Close']:.2f}")

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ── 6. CHART TOGGLES ───────────────────────────
if "plot_type" not in st.session_state:
    st.session_state.plot_type = "Close"

toggle_labels = {
    "Close": "Price",
    "% Change (1d)": "1‑Day %",
    "Volume": "Volume"
}
toggle_cols = st.columns([1,1,1])
for i, (col, label) in enumerate(toggle_labels.items()):
    toggle_cols[i].button(
        label, 
        key=label,
        on_click=lambda c=col: st.session_state.update(plot_type=c), 
        type="primary" if st.session_state.plot_type==col else "secondary"
    )

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ── 7. CHART ───────────────────────────────────
y_field = st.session_state.plot_type
if y_field == "Volume":
    fig = px.bar(sel_df, x="Date", y="Volume", title=f"{ticker} – Daily Volume (30 d)")
else:
    fig = px.line(sel_df, x="Date", y=y_field, 
                  title=f"{ticker} – {toggle_labels[y_field]} (30 d)",
                  labels={y_field: toggle_labels[y_field]})
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── 8. NEWS FEED — CLEANED & DEDUPLICATED ──────
def clean_articles(news_df, n):
    seen_titles = set()
    articles = []
    for _, art in news_df.iterrows():
        title = str(art["Title"]).strip()
        url = art["URL"]
        source = art["Source"]
        date = art["PublishedAt"]
        desc = str(art.get("Description", "") or "").replace("\n", " ").replace("  ", " ").strip()

        # Deduplicate by title+source
        uniq_key = (title.lower(), source.lower())
        if uniq_key in seen_titles:
            continue
        seen_titles.add(uniq_key)

        # Remove headers and garbage phrases
        for bad_phrase in ["In This Article:", "Key Points", "#", "##"]:
            desc = desc.replace(bad_phrase, "")
        desc = desc.strip()

        # Remove if desc is just title or starts with title
        if desc.lower() == title.lower() or desc.lower().startswith(title.lower()):
            desc = ""

        # Truncate description for layout
        if len(desc) > 180:
            desc = desc[:177] + "..."

        # Skip super-repetitive blocks
        if desc and (desc.count("Super Micro") > 2 or desc.count("AI") > 6):
            desc = ""
        desc = desc.rstrip(". ").strip()

        articles.append(dict(Date=date, Title=title, URL=url, Source=source, Desc=desc))
        if len(articles) >= n:
            break
    return articles

st.markdown("<h2 style='text-align:center'>📰 Latest AI Headlines</h2>", unsafe_allow_html=True)
max_articles = min(30, len(news))
n = st.slider("Articles to show", 1, max_articles, min(10, max_articles))

for art in clean_articles(news, n):
    st.markdown(f"**{art['Date']}** — [{art['Title']}]({art['URL']})  *{art['Source']}*")
    if art["Desc"]:
        st.caption(art["Desc"])

st.markdown("---")
st.caption("@Tw_Abdulelah")
