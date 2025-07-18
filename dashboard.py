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

# -------------------------- DASHBOARD CONTENT -------------------------- #
# Set page title
st.set_page_config(page_title="AI Options Dashboard", layout="wide")
st.title(f"📊 AI Stock & Options Dashboard - Welcome {name}")

# Define popular tickers
tickers = ['SPY', 'TSLA', 'PLTR', 'META', 'AAPL', 'NVDA', 'AMZN', 'MSFT', 'GOOGL', 'QQQ', 'ARKK', 'XLF', 'DIA', 'TQQQ', 'SOXL', 'BABA', 'SHOP']
st.sidebar.title("💲 Chwazi Tikè")
ticker = st.sidebar.selectbox("Chwazi yon stock:", tickers)

# Add start and end date inputs
st.sidebar.markdown("### Chwazi Dat")
def_date = datetime.date.today() - datetime.timedelta(days=7)
start_date = st.sidebar.date_input("Start Date", def_date)
end_date = st.sidebar.date_input("End Date", datetime.date.today())

# Download stock data
data = yf.download(ticker, start=start_date, end=end_date)

# Prevent error if download failed
if data.empty or 'Close' not in data.columns:
    st.error("Failed to load data for selected ticker. Please try again later or choose another ticker.")
    st.stop()

# Add RSI and EMAs
data['RSI'] = data['Close'].rolling(window=14).mean() / data['Close'] * 100
data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()

# Layout
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

    if isinstance(last_price, (int, float)):
        st.metric("Last Price", f"${last_price:.2f}")
    else:
        st.metric("Last Price", "N/A")

    st.metric("RSI", f"{last_rsi:.2f}")

    if isinstance(last_volume, (int, float)):
        st.metric("Volume", f"{last_volume:,.0f}")
    else:
        st.metric("Volume", "N/A")

    st.subheader("AI Signal Detector")
    a_plus = (last_rsi < 30 and data['EMA50'].iloc[-1] > data['EMA200'].iloc[-1])
    if a_plus:
        st.success("✅ A+ Signal Detected: RSI < 30 and EMA50 > EMA200")
    else:
        st.info("⚠️ No A+ signal currently")

    if last_rsi > 70:
        st.warning("Overbought Zone – Potential PUT signal ⚠️")
    elif last_rsi < 30:
        st.success("Oversold Zone – Potential CALL signal ✅")
    else:
        st.info("Neutral RSI")

    st.subheader("🔮 Prediksyon Pwoschen Pri")
    X = np.arange(len(data)).reshape(-1, 1)
    y = data['Close'].values
    model = LinearRegression().fit(X, y)
    predicted_price = model.predict([[len(data)]])[0]
    st.metric("Predicted Next Close", f"${predicted_price:.2f}")

# Final message
st.caption("Powered by WIWI (Ricardo Simon).AI Dashboard")
