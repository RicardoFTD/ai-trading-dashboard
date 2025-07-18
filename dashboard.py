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

# NOTE: Pa bliye mete API NewsAPI ou an (ranplase `YOUR_VALID_NEWSAPI_KEY`)
# NOTE: Mete webhook Telegram ou si ou vle notifikasyon yo fonksyone (ranplase <your-bot-token> ak <your-chat-id>)
