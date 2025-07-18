# AI STOCK OPTION DASHBOARD (Streamlit Version)
# Save this as `dashboard.py` and run with: streamlit run dashboard.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate
import datetime
import requests
import numpy as np
import smtplib
import ssl
from email.message import EmailMessage
import openai

# Make sure scikit-learn is installed in your environment
try:
    from sklearn.linear_model import LinearRegression
except ModuleNotFoundError:
    st.error("ModuleNotFoundError: Please install scikit-learn by running `pip install scikit-learn` in your terminal.")
    st.stop()

# -------------------------- AUTHENTICATION -------------------------- #
credentials = {
    "usernames": {
        "ricardo": {
            "name": "Ricardo Simon",
            "password": "123456"
        },
        "admin": {
            "name": "Admin User",
            "password": "adminpass"
        }
    }
}

authenticator = Authenticate(credentials, 'cookie_name', 'signature_key', cookie_expiry_days=1)
authenticator.login()

if st.session_state.get("authentication_status") is False:
    st.error("Username/password is incorrect")
    st.stop()
elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your username and password")
    st.stop()
else:
    name = st.session_state.get("name")
    authenticator.logout('Logout', 'sidebar')

# -------------------------- DARK MODE / THEME SWITCH -------------------------- #
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    :root {
        color-scheme: dark light;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        color: #fff;
    }
    .stButton button {
        background-color: #1f77b4;
        color: white;
    }
    .stMetric {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
    }
    .element-container:has(.stPlotlyChart) {
        background: #1f1f1f;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    @media screen and (max-width: 768px) {
        .stMetric {
            flex-direction: column;
            align-items: flex-start;
        }
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------- DASHBOARD CONTENT -------------------------- #
st.set_page_config(page_title="AI Options Dashboard", layout="wide")

st.title(f"\U0001F4CA AI Stock & Options Dashboard - Welcome {name}")

tickers = ['SPY', 'TSLA', 'PLTR', 'META', 'AAPL', 'NVDA', 'AMZN', 'MSFT', 'GOOGL', 'QQQ', 'ARKK', 'XLF', 'DIA', 'TQQQ', 'SOXL', 'BABA', 'SHOP']
st.sidebar.title("\U0001F4B2 Chwazi Tikè")
ticker = st.sidebar.selectbox("Chwazi yon stock:", tickers)

st.sidebar.markdown("### Chwazi Dat")
def_date = datetime.date.today() - datetime.timedelta(days=7)
start_date = st.sidebar.date_input("Start Date", def_date)
end_date = st.sidebar.date_input("End Date", datetime.date.today())

data = yf.download(ticker, start=start_date, end=end_date)

if data.empty or 'Close' not in data.columns:
    st.error("Failed to load data for selected ticker. Please try again later or choose another ticker.")
    st.stop()

data['RSI'] = data['Close'].rolling(window=14).mean() / data['Close'] * 100
data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"{ticker} Price Chart with RSI")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'], high=data['High'],
                                 low=data['Low'], close=data['Close'],
                                 name='Price'))
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA50'], name="EMA50", line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'], name="EMA200", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name="RSI", yaxis='y2', line=dict(color='green', dash='dot')))
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Latest Snapshot")
    last_price = data['Close'].iloc[-1] if not data['Close'].empty else None
    last_rsi = data['RSI'].iloc[-1] if not data['RSI'].empty else 0
    last_volume = data['Volume'].iloc[-1] if 'Volume' in data.columns and not data['Volume'].empty else 0

    try:
        st.metric("Last Price", f"${last_price:.2f}" if last_price is not None and not pd.isna(last_price) else "N/A")
    except:
        st.metric("Last Price", "N/A")
    try:
        st.metric("RSI", f"{last_rsi:.2f}" if last_rsi is not None and not pd.isna(last_rsi) else "N/A")
    except:
        st.metric("RSI", "N/A")
    try:
        st.metric("Volume", f"{last_volume:,.0f}" if last_volume is not None and not pd.isna(last_volume) else "N/A")
    except:
        st.metric("Volume", "N/A")

    st.subheader("AI Signal Detector")
    a_plus = (last_rsi < 30 and data['EMA50'].iloc[-1] > data['EMA200'].iloc[-1]) if isinstance(last_rsi, (int, float)) else False
    if a_plus:
        st.success("\u2705 A+ Signal Detected: RSI < 30 and EMA50 > EMA200")
    else:
        st.info("\u26A0\uFE0F No A+ signal currently")

    if isinstance(last_rsi, (int, float)):
        if last_rsi > 70:
            st.warning("Overbought Zone – Potential PUT signal ⚠️")
        elif last_rsi < 30:
            st.success("Oversold Zone – Potential CALL signal ✅")
        else:
            st.info("Neutral RSI")

    st.subheader("\U0001F52E Prediksyon Pwoschen Pri")
    X = np.arange(len(data)).reshape(-1, 1)
    y = data['Close'].values
    model = LinearRegression().fit(X, y)
    predicted_price = model.predict([[len(data)]])[0]
    try:
        st.metric("Predicted Next Close", f"${predicted_price:.2f}" if predicted_price is not None and not pd.isna(predicted_price) else "N/A")
    except:
        st.metric("Predicted Next Close", "N/A")

    if a_plus:
        try:
            requests.get("https://api.telegram.org/b<your-bot-token>/sendMessage", params={
                "chat_id": "<your-chat-id>",
                "text": f"\u2705 A+ Signal Detected on {ticker}! RSI={last_rsi:.2f} | EMA50>{data['EMA200'].iloc[-1]:.2f}"
            })
        except:
            st.warning("Telegram alert failed (check token or chat_id)")

st.subheader("\U0001F4C8 Last 5 Entries")
st.dataframe(data.tail().round(2), use_container_width=True)

st.subheader("\U0001F50D AI Sentiment Analysis (GPT-4)")
news = requests.get(f"https://newsapi.org/v2/everything?q={ticker}&apiKey=a8aa81bbbaaf4a308c0c70dafb84e48d").json()
if 'articles' in news:
    for article in news['articles'][:3]:
        st.write(f"**{article['title']}**")
        st.caption(article['description'])
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst. Summarize the sentiment of the news headline and give a brief impact on the stock."},
                    {"role": "user", "content": article['title'] + "\n" + article['description']}
                ]
            )
            sentiment_summary = response['choices'][0]['message']['content']
            st.info(sentiment_summary)
        except Exception as e:
            st.warning("OpenAI sentiment analysis failed")
else:
    st.info("Sentiment data unavailable.")

st.subheader("\U0001F4CB Watchlist Overview")
watchlist_data = {}
for tk in ['SPY', 'TSLA', 'META', 'PLTR', 'AAPL', 'GOOGL']:
    df = yf.download(tk, period='5d', interval='1h')
    if not df.empty and 'Close' in df.columns:
        rsi = df['Close'].rolling(window=14).mean() / df['Close'] * 100
        watchlist_data[tk] = rsi.iloc[-1] if not rsi.empty else 0
    else:
        watchlist_data[tk] = 0

watch_df = pd.DataFrame.from_dict(watchlist_data, orient='index', columns=['RSI'])
st.dataframe(watch_df.round(2), use_container_width=True)

st.download_button("Download Data as CSV", data.to_csv().encode('utf-8'), file_name=f'{ticker}_data.csv')

st.caption("Powered by WIWI (Ricardo Simon).AI Dashboard")
