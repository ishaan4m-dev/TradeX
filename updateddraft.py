import streamlit as st
import random
import pandas as pd
import time

# Set layout to wide for a better dashboard experience
st.set_page_config(page_title="BullRun - Stock Simulator", page_icon="📈", layout="wide")

# -----------------------------------------------------------------------------
# 1. GLOBAL STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "users_db" not in st.session_state:
    st.session_state.users_db = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "auth"

# State controllers for the Sidebar Authentication UI
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login"
if "signup_success" not in st.session_state:
    st.session_state.signup_success = False
    
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "RELIANCE"
if "trade_action" not in st.session_state:
    st.session_state.trade_action = "BUY"

if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "RELIANCE": {"price": 2850.0, "prev": 2820.0},
        "TCS": {"price": 3950.0, "prev": 3965.0},
        "HDFCBANK": {"price": 1450.0, "prev": 1435.0},
        "INFY": {"price": 1620.0, "prev": 1600.0},
        "ICICIBANK": {"price": 1050.0, "prev": 1042.0},
        "BHARTIARTL": {"price": 1150.0, "prev": 1165.0},
        "SBIN": {"price": 760.0, "prev": 755.0},
    }
if "indices" not in st.session_state:
    st.session_state.indices = {
        "NIFTY 50": {"price": 22500.0, "prev": 22410.0},
        "SENSEX": {"price": 74100.0, "prev": 73850.0}
    }

BANK_PREFIXES = {
    "State Bank of India": "SBIN0",
    "HDFC Bank": "HDFC0",
    "ICICI Bank": "ICIC0",
    "Axis Bank": "UTIB0",
    "Kotak Mahindra Bank": "KKBK0",
    "Punjab National Bank": "PUNB0",
    "Bank of Baroda": "BARB0"
}

def update_market_prices():
    for ticker in st.session_state.stocks:
        change = random.uniform(-0.015, 0.015)
        st.session_state.stocks[ticker]["prev"] = st.session_state.stocks[ticker]["price"]
        st.session_state.stocks[ticker]["price"] = round(st.session_state.stocks[ticker]["price"] * (1 + change), 2)
    for index in st.session_state.indices:
        change = random.uniform(-0.008, 0.008)
        st.session_state.indices[index]["prev"] = st.session_state.indices[index]["price"]
        st.session_state.indices[index]["price"] = round(st.session_state.indices[index]["price"] * (1 + change), 2)

# -----------------------------------------------------------------------------
# 2. AUTHENTICATION & ONBOARDING
# -----------------------------------------------------------------------------
def render_auth():
    with st.sidebar:
        st.markdown("## 🔐 Access Portal")
        
        # BUG FIX: Safely manage the radio button state without locking the widget key
        current_idx = 0 if st.session_state.auth_mode == "Login" else 1
        selected_action = st.radio("Select Action:", ["Login", "Sign Up"], index=current_idx, label_visibility="collapsed")
        if selected_action != st.session_state.auth_mode:
            st.session_state.auth_
