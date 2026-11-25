import streamlit as st
import yfinance as yf
import feedparser
from datetime import datetime

st.set_page_config(page_title="Mon Suivi", layout="wide")
st.title("📊 Suivi Quotidien : Cours (€) & RSI")
st.caption(f"Mis à jour le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")

if st.button("🔄 Actualiser les données"):
    st.cache_data.clear()
    st.rerun()

# --- 1. TES VALEURS À SUIVRE ---
ACTIFS = {
    "MSCI World (CW8)": "CW8.PA",
    "Nvidia (Xetra €)": "NVD.DE",
    "ASML": "ASML.AS",
    "Alphabet (Xetra €)": "ABEA.DE",
    "Interparfums": "ITP.PA",
    "FDJ": "FDJ.PA",
    "Coca-Cola": "KO",
    "Ethereum": "ETH-EUR"
}

def calculer_rsi(series_close, periode=14):
    delta = series_close.diff()
    gain = delta.clip(lower=0)
    perte = -delta.clip(upper=0)
    moy_gain = gain.ewm(alpha=1 / periode, min_periods=periode, adjust=False).mean()
    moy_perte = perte.ewm(alpha=1 / periode, min_periods=periode, adjust=False).mean()
    rs = moy_gain / moy_perte
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

@st.cache_data(ttl=600)
def get_taux_eur_usd():
    try:
        hist = yf.Ticker("EURUSD=X").history(period="5d")
        if not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])
    except Exception:
        pass
    return 1.08

@st.cache_data(ttl=600)
def charger_actif(ticker):
    t = yf.Ticker(ticker)
    data = t.history(period="3mo")
    if data is None or data.empty or "Close" not in data:
        raise ValueError("Pas de données historiques")
    close = data["Close"].dropna()
    if len(close) < 16:
        raise ValueError("Historique insuffisant pour RSI")

    # Déterminer si le ticker est déjà en EUR ou s'il faut convertir depuis USD
    est_deja_eur = ticker.endswith((".PA", ".DE", ".AS", "-EUR", ".BR", ".MI"))
    devise = "EUR" if est_deja_eur else "USD"
    return float(close.iloc[-1]), float(close.iloc[-2]), calculer_rsi(close, 14), devise

taux_eur_usd = get_taux_eur_usd()

st.subheader("📈 Cours en euros & RSI (14 jours)")
cols = st.columns(2)

for idx, (nom, ticker) in enumerate(ACTIFS.items()):
    col = cols[idx % 2]
    try:
        cours, veille, rsi_val, devise = charger_actif(ticker)

        if devise == "USD":
            cours = cours / taux_eur_usd
            veille = veille / taux_eur_usd

        var = ((cours - veille) / veille) * 100

        if rsi_val >= 70:
            etat_rsi = f"🔴 RSI {rsi_val:.0f} (Surachat)"
        elif rsi_val <= 30:
            etat_rsi = f"🟢 RSI {rsi_val:.0f} (Survente)"
        else:
            etat_rsi = f"⚪ RSI {rsi_val:.0f} (Neutre)"

        with col.container(border=True):
            st.metric(
                label=nom,
                value=f"{cours:.2f} €",
                delta=f"{var:+.2f} %"
            )
            st.write(etat_rsi)
    except Exception as e:
        with col.container(border=True):
            st.metric(label=nom, value="Indispo", delta="N/A")
            st.caption(f"Détail : {e}")

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
