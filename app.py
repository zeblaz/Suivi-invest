import streamlit as st
import yfinance as yf
import feedparser
from datetime import datetime

st.set_page_config(page_title="Mon Suivi", layout="wide")
st.title("📊 Suivi Quotidien")
st.caption(f"Mis à jour le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")

if st.button("🔄 Actualiser les données"):
    st.rerun()

# --- 1. TES VALEURS À SUIVRE (modifiables librement) ---
ACTIFS = {
    "MSCI World (CW8)": "CW8.PA",
    "Nvidia": "NVDA",
    "ASML": "ASML.AS",
    "Alphabet": "GOOGL",
    "Ethereum": "ETH-EUR"
}

st.subheader("📈 Cours du jour")
cols = st.columns(2)

for idx, (nom, ticker) in enumerate(ACTIFS.items()):
    try:
        data = yf.Ticker(ticker).history(period="5d")
        if len(data) >= 2:
            cours = data["Close"].iloc[-1]
            veille = data["Close"].iloc[-2]
            var = ((cours - veille) / veille) * 100
            cols[idx % 2].metric(label=nom, value=f"{cours:.2f}", delta=f"{var:+.2f} %")
    except Exception:
        cols[idx % 2].metric(label=nom, value="Erreur", delta="N/A")

st.divider()

# --- 2. TES FLUX D'ACTUALITÉS ---
FLUX_RSS = [
    "https://news.google.com/rss/search?q=Nvidia+OR+ASML+OR+semiconducteurs&hl=fr&gl=FR&ceid=FR:fr",
    "https://news.google.com/rss/search?q=ETF+MSCI+World+OR+BCE+taux&hl=fr&gl=FR&ceid=FR:fr"
]

st.subheader("📰 Actualités ciblées")
for url in FLUX_RSS:
    flux = feedparser.parse(url)
    for entry in flux.entries[:4]:
        st.markdown(f"**[{entry.title}]({entry.link})**")
        st.caption(entry.get("published", ""))
