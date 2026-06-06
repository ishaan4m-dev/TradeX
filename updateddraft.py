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
        st.radio("Select Action:", ["Login", "Sign Up"], key="auth_mode", label_visibility="collapsed")
        st.markdown("---")
        st.markdown("### 📊 System Status")
        st.success("🟢 Market Open")
        st.info("📡 Live Tracking: Active")

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
    
    col1, col2, col3 = st.columns([1, 2, 1]) 
    
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
            
            st.markdown("<br>", unsafe_allow_html=True)
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
                    
                    # Double Verification for PIN generation
                    new_pin = st.text_input("Create 4-Digit Secure PIN (For Trading)", type="password", max_chars=4)
                    confirm_pin = st.text_input("Verify 4-Digit Secure PIN", type="password", max_chars=4)
                    
                    if st.form_submit_button("Complete Registration", use_container_width=True):
                        if new_user == "123456" or new_user == "admin":
                            st.error("Reserved Admin ID cannot be used.")
                        elif new_user in st.session_state.users_db:
                            st.error("User ID already exists.")
                        elif new_pass != confirm_pass:
                            st.error("Registration Failed: Passwords do not match.")
                        elif new_pin != confirm_pin:
                            st.error("Registration Failed: Secure PINs do not match.")
                        elif not new_pin.isdigit() or len(new_pin) != 4:
                            st.error("Secure PIN must be exactly 4 numeric digits.")
                        elif len(pan_num) != 10 or len(ifsc_suffix) != 6:
                            st.error("Ensure PAN is 10 chars and IFSC suffix is 6 chars.")
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
                            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Already have an account? Login Here", use_container_width=True):
                st.session_state.auth_mode = "Login"
                st.rerun()

# -----------------------------------------------------------------------------
# 3. PROFILE & SECURITY PORTAL
# -----------------------------------------------------------------------------
def render_profile():
    u_data = st.session_state.users_db[st.session_state.current_user]
    
    st.title("👤 Account Profile & Security Center")
    if st.button("⬅ Back to Dashboard"):
        st.session_state.view_mode = "dashboard"
        st.rerun()
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    # Left Column: Identity Updates
    with col1:
        st.subheader("Edit Profile Information")
        with st.container(border=True):
            new_username = st.text_input("Change User ID", value=st.session_state.current_user)
            if st.button("Update User ID"):
                if new_username == st.session_state.current_user:
                    st.info("No changes detected.")
                elif new_username == "123456" or new_username == "admin":
                    st.error("Reserved Admin ID cannot be used.")
                elif new_username in st.session_state.users_db:
                    st.error("This User ID is already taken. Please choose another.")
                else:
                    # Safely transfer data to new dictionary key
                    st.session_state.users_db[new_username] = st.session_state.users_db.pop(st.session_state.current_user)
                    st.session_state.current_user = new_username
                    st.success("User ID updated successfully!")
                    time.sleep(1)
                    st.rerun()
                    
    # Right Column: Security Resets
    with col2:
        st.subheader("Security & Credential Management")
        
        # Password Reset
        with st.expander("Reset Account Password", expanded=False):
            with st.form("pwd_reset_form"):
                current_pwd = st.text_input("Current Password", type="password")
                new_pwd = st.text_input("New Password", type="password")
                verify_pwd = st.text_input("Verify New Password", type="password")
                
                if st.form_submit_button("Update Password"):
                    if current_pwd != u_data["password"]:
                        st.error("Authentication Failed: Current password is incorrect.")
                    elif new_pwd != verify_pwd:
                        st.error("Verification Failed: New passwords do not match.")
                    elif len(new_pwd) < 4:
                        st.error("Password must be at least 4 characters long.")
                    else:
                        st.session_state.users_db[st.session_state.current_user]["password"] = new_pwd
                        st.success("Password successfully updated.")
                        
        # PIN Reset
        with st.expander("Reset Transaction PIN", expanded=False):
            with st.form("pin_reset_form"):
                current_pin = st.text_input("Current 4-Digit PIN", type="password", max_chars=4)
                new_pin = st.text_input("New 4-Digit PIN", type="password", max_chars=4)
                verify_pin = st.text_input("Verify New PIN", type="password", max_chars=4)
                
                if st.form_submit_button("Update Transaction PIN"):
                    if current_pin != u_data["pin"]:
                        st.error("Authentication Failed: Current PIN is incorrect.")
                    elif new_pin != verify_pin:
                        st.error("Verification Failed: New PINs do not match.")
                    elif not new_pin.isdigit() or len(new_pin) != 4:
                        st.error("Format Error: PIN must be exactly 4 numeric digits.")
                    else:
                        st.session_state.users_db[st.session_state.current_user]["pin"] = new_pin
                        st.success("Transaction PIN successfully updated.")

# -----------------------------------------------------------------------------
# 4. ADMIN PORTAL
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
# 5. MAIN TRADING DASHBOARD
# -----------------------------------------------------------------------------
def render_dashboard():
    u_data = st.session_state.users_db[st.session_state.current_user]
    
    # Updated Top Navigation Bar to include Profile button
    col_u, col_prof, col_out, col_ref = st.columns([6, 1.5, 1, 1.5])
    col_u.markdown(f"👤 Active Profile: **{st.session_state.current_user}** | 🏦 Linked Node: `{u_data['bank']}` | IFSC: `{u_data['ifsc']}`")
    
    if col_prof.button("👤 Profile", use_container_width=True):
        st.session_state.view_mode = "profile"
        st.rerun()
    if col_out.button("🚪 Logout", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.view_mode = "auth"
        st.rerun()
    if col_ref.button("🔄 Sync Market", use_container_width=True):
        update_market_prices()
        st.rerun()
    st.markdown("---")

    idx_cols = st.columns(len(st.session_state.indices))
    for i, (name, metrics) in enumerate(st.session_state.indices.items()):
        change_val = metrics["price"] - metrics["prev"]
        pct_change = (change_val / metrics["prev"]) * 100
        idx_cols[i].metric(label=name, value=f"₹{metrics['price']:,}", delta=f"{change_val:+.2f} ({pct_change:+.2f}%)")
    st.markdown("---")

    st.subheader("💳 Secure Clearing Wallet")
    w_col1, w_col2, w_col3 = st.columns([3, 4, 4])
    w_col1.metric("Available Liquidity Reserve", f"₹{u_data['wallet']:,.2f}")
    with w_col2:
        dep_amount = st.number_input("Transaction Volume (INR)", min_value=100.0, step=500.0, value=5000.0)
        wallet_pin = st.text_input("Enter 4-Digit Wallet PIN", type="password", max_chars=4, key="w_pin")
    with w_col3:
        st.markdown("<br>", unsafe_allow_html=True)
        w_act1, w_act2 = st.columns(2)
        if w_act1.button("📥 Add Funds", use_container_width=True):
            if wallet_pin == u_data["pin"]:
                st.session_state.users_db[st.session_state.current_user]["wallet"] += dep_amount
                st.success("Transfer authenticated. Funds added securely.")
                st.rerun()
            else:
                st.error("Authentication Failed: Incorrect PIN.")
        if w_act2.button("📤 Withdraw", use_container_width=True):
            if wallet_pin == u_data["pin"]:
                if u_data["wallet"] >= dep_amount:
                    st.session_state.users_db[st.session_state.current_user]["wallet"] -= dep_amount
                    st.success("Withdrawal processed to linked account.")
                    st.rerun()
                else:
                    st.error("Overdraft Error: Insufficient wallet liquidity.")
            else:
                st.error("Authentication Failed: Incorrect PIN.")
    st.markdown("---")

    m_col, t_col = st.columns([1.3, 0.7])
    
    with m_col:
        st.subheader("📊 Live Market Board")
        h1, h2, h3, h4, h5 = st.columns([2.5, 2, 2.5, 1.5, 1.5])
        h1.write("**Asset**")
        h2.write("**Price**")
        h3.write("**Daily Chg**")
        h4.write("**Buy**")
        h5.write("**Sell**")
        st.markdown("<hr style='margin:0px; padding:0px;'>", unsafe_allow_html=True)
        
        for ticker, values in st.session_state.stocks.items():
            c1, c2, c3, c4, c5 = st.columns([2.5, 2, 2.5, 1.5, 1.5])
            c1.write(f"**{ticker}**")
            c2.write(f"₹{values['price']:.2f}")
            
            change = values["price"] - values["prev"]
            pct = (change / values["prev"]) * 100
            color = "#00C853" if change >= 0 else "#D50000"
            arrow = "▲" if change >= 0 else "▼"
            c3.markdown(f"<span style='color:{color}; font-weight:bold;'>{arrow} {abs(change):.2f} ({pct:+.2f}%)</span>", unsafe_allow_html=True)
            
            if c4.button("🟢 Buy", key=f"buy_{ticker}", use_container_width=True):
                st.session_state.selected_ticker = ticker
                st.session_state.trade_action = "BUY"
                st.rerun()
            if c5.button("🔴 Sell", key=f"sell_{ticker}", use_container_width=True):
                st.session_state.selected_ticker = ticker
                st.session_state.trade_action = "SELL"
                st.rerun()

    with t_col:
        st.subheader("⚡ Execution Terminal")
        with st.container(border=True):
            stock_list = list(st.session_state.stocks.keys())
            default_stock_idx = stock_list.index(st.session_state.selected_ticker) if st.session_state.selected_ticker in stock_list else 0
            
            target_stock = st.selectbox("Select Asset", stock_list, index=default_stock_idx)
            
            action_list = ["BUY", "SELL"]
            default_action_idx = action_list.index(st.session_state.trade_action)
            order_type = st.radio("Order Direction", action_list, index=default_action_idx, horizontal=True)
            
            trade_qty = st.number_input("Share Quantity", min_value=1, step=1, value=1)
            
            current_unit_p = st.session_state.stocks[target_stock]["price"]
            total_est_cost = current_unit_p * trade_qty
            st.markdown(f"**Gross Settlement Capital:** `₹{total_est_cost:,.2f}`")
            
            entered_pin = st.text_input("Terminal Authorization PIN", type="password", max_chars=4, key="t_pin")
            
            btn_color = "primary" if order_type == "BUY" else "secondary"
            if st.button(f"Commit {order_type} Sequence", use_container_width=True, type=btn_color):
                if entered_pin != u_data["pin"]:
                    st.error("Execution Refused: Incorrect authorization PIN.")
                else:
                    if order_type == "BUY":
                        if u_data["wallet"] >= total_est_cost:
                            st.session_state.users_db[st.session_state.current_user]["wallet"] -= total_est_cost
                            if target_stock in u_data["portfolio"]:
                                ex_qty = u_data["portfolio"][target_stock]["qty"]
                                ex_avg = u_data["portfolio"][target_stock]["avg_price"]
                                new_qty = ex_qty + trade_qty
                                new_avg = ((ex_avg * ex_qty) + total_est_cost) / new_qty
                                st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock] = {"qty": new_qty, "avg_price": round(new_avg, 2)}
                            else:
                                st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock] = {"qty": trade_qty, "avg_price": current_unit_p}
                            st.success(f"Acquisition Locked: {trade_qty} blocks of {target_stock}.")
                            st.rerun()
                        else:
                            st.error("Execution Terminated: Insufficient Wallet Balance.")
                    
                    elif order_type == "SELL":
                        if target_stock in u_data["portfolio"] and u_data["portfolio"][target_stock]["qty"] >= trade_qty:
                            st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock]["qty"] -= trade_qty
                            st.session_state.users_db[st.session_state.current_user]["wallet"] += total_est_cost
                            if st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock]["qty"] == 0:
                                del st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock]
                            st.success(f"Liquidation Confirmed: {trade_qty} {target_stock} sold. Proceeds added to Wallet.")
                            st.rerun()
                        else:
                            st.error("Execution Terminated: Insufficient portfolio inventory.")

    st.markdown("---")

    st.subheader("💼 Active Asset Holdings Matrix")
    if not u_data["portfolio"]:
        st.info("No active open trading parameters verified inside the ledger.")
    else:
        portfolio_rows = []
        total_pnl = 0.0
        for ticker, data in u_data["portfolio"].items():
            qty = data["qty"]
            avg_p = data["avg_price"]
            current_p = st.session_state.stocks[ticker]["price"]
            invested_cap = qty * avg_p
            current_value = qty * current_p
            pnl = current_value - invested_cap
            total_pnl += pnl
            
            portfolio_rows.append({
                "Asset Symbol": ticker, "Quantity Held": qty, "Average Entry Price": f"₹{avg_p:,.2f}",
                "Current Valuation": f"₹{current_value:,.2f}", "Unrealized Gain/Loss": f"₹{pnl:+,.2f}"
            })
            
        st.dataframe(pd.DataFrame(portfolio_rows), use_container_width=True, hide_index=True)
        st.metric("Aggregate Net Realized Return", f"₹{total_pnl:+,.2f}")

# -----------------------------------------------------------------------------
# 6. CONTROLLER ORCHESTRATION
# -----------------------------------------------------------------------------
if st.session_state.view_mode == "auth":
    render_auth()
elif st.session_state.view_mode == "dashboard" and st.session_state.current_user:
    render_dashboard()
elif st.session_state.view_mode == "profile" and st.session_state.current_user:
    render_profile()
elif st.session_state.view_mode == "admin" and st.session_state.current_user == "admin":
    render_admin()
else:
    st.session_state.view_mode = "auth"
    st.rerun()
