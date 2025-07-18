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

# -------------------------- BOLLINGER BAND -------------------------- #
data['20SMA'] = data['Close'].rolling(window=20).mean()
data['UpperBand'] = data['20SMA'] + 2 * data['Close'].rolling(window=20).std()
data['LowerBand'] = data['20SMA'] - 2 * data['Close'].rolling(window=20).std()

out_of_band_signal = data['Close'].iloc[-1] > data['UpperBand'].iloc[-1] or data['Close'].iloc[-1] < data['LowerBand'].iloc[-1]

data['RSI'] = data['Close'].rolling(window=14).mean() / data['Close'] * 100

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"{ticker} Price Chart with Bollinger Bands and RSI")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'], high=data['High'],
                                 low=data['Low'], close=data['Close'],
                                 name='Price'))
    fig.add_trace(go.Scatter(x=data.index, y=data['UpperBand'], name="Upper Band", line=dict(color='red')))
    fig.add_trace(go.Scatter(x=data.index, y=data['LowerBand'], name="Lower Band", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['20SMA'], name="20 SMA", line=dict(color='gray')))
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Signal Based on Bollinger Band")
    if out_of_band_signal:
        st.success("\u2705 Price is outside Bollinger Band — Signal Detected!")
    else:
        st.info("\u26A0\uFE0F No breakout detected")
