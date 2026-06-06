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
    # Sidebar: Clean Navigation & Status tied to session_state
    with st.sidebar:
        st.markdown("## 🔐 Access Portal")
        st.radio("Select Action:", ["Login", "Sign Up"], key="auth_mode", label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### 📊 System Status")
        st.success("🟢 Market Open")
        st.info("📡 Live Tracking: Active")

    # Main Area: Colorful Landing Header
    st.markdown(
        """
        <div style='text-align: center; padding: 20px;'>
            <h1 style='font-size: 3.5rem; margin-bottom: 0px;'>📈 <span style='color: #2E86C1;'>BullRun</span> Simulator</h1>
            <p style='color: #808080; font-size: 1.2rem; margin-top: 5px;'>Institutional Grade Real-Time Virtual Trading Environment</p>
        </div>
        <hr>
        """, 
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1]) # Centering the forms
    
    with col2:
        if st.session_state.auth_mode == "Login":
            st.markdown("<h3 style='text-align: center;'>Existing User Login</h3>", unsafe_allow_html=True)
            
            if st.session_state.signup_success:
                st.success("Account created successfully! Please login with your new credentials.")
                st.session_state.signup_success = False 
                
            with st.container(border=True):
                with st.form("login_form"):
                    login_user = st.text_input("User ID (Username)", placeholder="Enter your registered ID")
                    login_pass = st.text_input("Password", type="password", placeholder="••••••••")
                    
                    submit_btn = st.form_submit_button("Secure Login", use_container_width=True)
                    
                    if submit_btn:
                        if login_user == "123456" and login_pass == "121212":
                            st.session_state.current_user = "admin"
                            st.session_state.view_mode = "admin"
                            st.rerun()
                        elif login_user in st.session_state.users_db and st.session_state.users_db[login_user]["password"] == login_pass:
                            st.session_state.current_user = login_user
                            st.session_state.view_mode = "dashboard"
                            st.rerun()
                        else:
                            st.error("Authentication Failed: Invalid ID or Password.")
            
            # Quick Link to Sign Up
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>New to BullRun Simulator?</p>", unsafe_allow_html=True)
            if st.button("New User? Sign Up Here", use_container_width=True):
                st.session_state.auth_mode = "Sign Up"
                st.rerun()
                            
        elif st.session_state.auth_mode == "Sign Up":
            st.markdown("<h3 style='text-align: center;'>New Entity Registration</h3>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("#### 1. Identity Verification")
                new_name = st.text_input("Full Legal Name")
                new_email = st.text_input("Email Address")
                pan_num = st.text_input("10-Digit PAN Card Number", max_chars=10)
                
                st.markdown("---")
                st.markdown("#### 2. Banking Integration")
                sel_bank = st.selectbox("Select Core Bank", list(BANK_PREFIXES.keys()))
                ifsc_prefix = BANK_PREFIXES[sel_bank]
                st.info(f"**Auto-Detected IFSC Prefix:** `{ifsc_prefix}`")
                
                with st.form("signup_form"):
                    ifsc_suffix = st.text_input("Enter remaining 6 digits of IFSC", max_chars=6)
                    acc_num = st.text_input("Bank Account Number", type="password")
                    
                    st.markdown("#### 3. Security Credentials")
                    new_user = st.text_input("Choose User ID")
                    
                    new_pass = st.text_input("Create Password", type="password")
                    confirm_pass = st.text_input("Verify Password", type="password")
                    
                    new_pin = st.text_input("Create 4-Digit Secure PIN (For Trading)", type="password", max_chars=4)
                    
                    if st.form_submit_button("Complete Registration", use_container_width=True):
                        if new_user == "123456" or new_user == "admin":
                            st.error("Reserved Admin ID cannot be used.")
                        elif new_user in st.session_state.users_db:
                            st.error("User ID already exists.")
                        elif new_pass != confirm_pass:
                            st.error("Registration Failed: Passwords do not match.")
                        elif len(pan_num) != 10 or len(ifsc_suffix) != 6 or len(new_pin) != 4:
                            st.error("Ensure PAN is 10 chars, IFSC suffix is 6 chars, and PIN is 4 digits.")
                        elif new_name and new_user and new_pass and acc_num:
                            st.session_state.users_db[new_user] = {
                                "name": new_name, "email": new_email, "password": new_pass,
                                "bank": sel_bank, "bank_acc": acc_num, "ifsc": f"{ifsc_prefix}{ifsc_suffix}",
                                "wallet": 0.0, "pin": new_pin, "portfolio": {}, "pref": "Always Ask"
                            }
                            st.session_state.signup_success = True
                            st.session_state.auth_mode = "Login"
                            st.rerun()
                        else:
                            st.error("Please fill all fields.")
                            
            # Quick Link back to Login
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Already have an account? Login Here", use_container_width=True):
                st.session_state.auth_mode = "Login"
                st.rerun()

# -----------------------------------------------------------------------------
# 3. ADMIN PORTAL
# -----------------------------------------------------------------------------
def render_admin():
    st.title("⚙️ System Administrator Portal")
    col1, col2 = st.columns([8, 2])
    col1.subheader("Registered Entity Database")
    if col2.button("Log Out Admin", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.view_mode = "auth"
        st.rerun()

    st.warning("Privacy Protocol Enforced: Individual holdings are completely hidden from administrative view.")
    
    admin_data = []
    for uid, data in st.session_state.users_db.items():
        admin_data.append({
            "User ID": uid,
            "Legal Name": data["name"],
            "Linked Bank": data["bank"],
            "Wallet Liquidity": f"₹{data['wallet']:,.2f}",
        })
        
    if admin_data:
        st.table(pd.DataFrame(admin_data))
    else:
        st.info("No active users registered in the database yet.")

# -----------------------------------------------------------------------------
# 4. MAIN TRADING DASHBOARD
# -----------------------------------------------------------------------------
def render_dashboard():
    u_data = st.session_state.users_db[st.session_state.current_user]
    
    col_u, col_out, col_ref = st.columns([8, 1, 1.5])
    col_u.markdown(f"👤 Active Profile: **{st.session_state.current_user}** | 🏦 Linked Node: `{u_data['bank']}` | IFSC: `{u_data['ifsc']}`")
    
    if col_out.button("🚪 Logout", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.view_mode = "auth"
        st
