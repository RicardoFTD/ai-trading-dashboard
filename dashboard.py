# AI STOCK OPTION DASHBOARD (Streamlit Version)
# Save this as `dashboard.py` and run with: streamlit run dashboard.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_authenticator import Authenticate
import datetime

# -------------------------- AUTHENTICATION -------------------------- #
credentials = {
    "usernames": {
        "ricardo": {
            "name": "Ricardo Simon",
            "password": "123456"  # Change this before deploying
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

# -------------------------- DASHBOARD CONTENT -------------------------- #
# Set page title
st.set_page_config(page_title="AI Options Dashboard", layout="wide")
st.title(f"📊 AI Stock & Options Dashboard - Welcome {name}")

# Define popular tickers
tickers = ['SPY', 'TSLA', 'PLTR', 'META', 'AAPL', 'NVDA', 'AMZN', 'MSFT', 'GOOGL', 'QQQ']
st.sidebar.title("Select Ticker")
ticker = st.sidebar.selectbox("Choose a stock:", tickers)

# Download stock data
data = yf.download(ticker, period='5d', interval='1h')
data['RSI'] = data['Close'].rolling(window=14).mean() / data['Close'] * 100

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"{ticker} Price Chart with RSI")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'], high=data['High'],
                                 low=data['Low'], close=data['Close'],
                                 name='Price'))
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Latest Snapshot")
    st.metric("Last Price", f"${data['Close'][-1]:.2f}")
    st.metric("RSI", f"{data['RSI'][-1]:.2f}")
    st.metric("Volume", f"{data['Volume'][-1]:,.0f}")

    if data['RSI'][-1] > 70:
        st.warning("Overbought Zone – Potential PUT signal ⚠️")
    elif data['RSI'][-1] < 30:
        st.success("Oversold Zone – Potential CALL signal ✅")
    else:
        st.info("Neutral RSI")

# Table View
st.subheader("📈 Last 5 Entries")
st.dataframe(data.tail().round(2))

# Sentiment Mock Section (AI Placeholder)
st.subheader("🔍 AI Sentiment Analysis (Beta)")
st.info("🧠 AI model detects positive options flow sentiment on TSLA and META. Watch for call volume increase above $X strike this week.")

st.caption("Powered by yFinance • R. Simon AI Dashboard")
