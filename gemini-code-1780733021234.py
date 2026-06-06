import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="BullRun - Stock Simulator", page_icon="📈", layout="wide")

# -----------------------------------------------------------------------------
# 1. GLOBAL STATE INITIALIZATION (Simulated Database)
# -----------------------------------------------------------------------------
if "users_db" not in st.session_state:
    st.session_state.users_db = {} # Format: {username: {password, name, email, bank, bank_acc, wallet, pin, portfolio, pref}}
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "auth" # auth, dashboard, admin, settings
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"

# Expanded Real-World Market Data
if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "RELIANCE": {"price": 2850.0, "prev": 2820.0},
        "TCS": {"price": 3950.0, "prev": 3965.0},
        "HDFCBANK": {"price": 1450.0, "prev": 1435.0},
        "INFY": {"price": 1620.0, "prev": 1600.0},
        "ICICIBANK": {"price": 1050.0, "prev": 1042.0},
        "BHARTIARTL": {"price": 1150.0, "prev": 1165.0},
        "SBIN": {"price": 760.0, "prev": 755.0},
        "LT": {"price": 3650.0, "prev": 3610.0},
        "ITC": {"price": 420.0, "prev": 415.0},
        "HINDUNILVR": {"price": 2350.0, "prev": 2365.0},
        "AXISBANK": {"price": 1080.0, "prev": 1070.0},
        "KOTAKBANK": {"price": 1780.0, "prev": 1795.0},
        "TATAMOTORS": {"price": 980.0, "prev": 965.0},
        "MARUTI": {"price": 11500.0, "prev": 11400.0},
    }
if "indices" not in st.session_state:
    st.session_state.indices = {
        "NIFTY 50": {"price": 22500.0, "prev": 22410.0},
        "SENSEX": {"price": 74100.0, "prev": 73850.0}
    }

# Bank Data Mapping
BANK_PREFIXES = {
    "State Bank of India": "SBIN0",
    "HDFC Bank": "HDFC0",
    "ICICI Bank": "ICIC0",
    "Axis Bank": "UTIB0",
    "Kotak Mahindra Bank": "KKBK0",
    "IndusInd Bank": "INDB0"
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
# 2. AUTHENTICATION & ONBOARDING (LOGIN / SIGNUP)
# -----------------------------------------------------------------------------
def render_auth():
    st.title("🛡️ BullRun Institutional Trading")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    # Existing User Login
    with col1:
        st.subheader("Login to Environment")
        with st.form("login_form"):
            login_user = st.text_input("User ID (Username)")
            login_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Authenticate Session"):
                if login_user in st.session_state.users_db and st.session_state.users_db[login_user]["password"] == login_pass:
                    st.session_state.current_user = login_user
                    st.session_state.view_mode = "dashboard"
                    st.rerun()
                else:
                    st.error("Authentication Failed: Invalid ID or Password.")
                    
    # New User Signup Pipeline
    with col2:
        st.subheader("New Entity Registration (KYC)")
        with st.form("signup_form"):
            new_name = st.text_input("Full Legal Name")
            new_email = st.text_input("Email Address")
            new_user = st.text_input("Choose User ID")
            new_pass = st.text_input("Create Password", type="password")
            
            st.markdown("##### Identity & Banking Link")
            pan_num = st.text_input("10-Digit PAN Card Number", max_chars=10)
            
            sel_bank = st.selectbox("Select Core Bank", list(BANK_PREFIXES.keys()))
            acc_num = st.text_input("Bank Account Number", type="password")
            
            # Dynamic IFSC layout
            ifsc_prefix = BANK_PREFIXES[sel_bank]
            st.markdown(f"**IFSC Prefix:** `{ifsc_prefix}`")
            ifsc_suffix = st.text_input("Enter remaining 6 digits of IFSC", max_chars=6)
            
            st.markdown("##### Security Setup")
            new_pin = st.text_input("Create 4-Digit Secure PIN (For Wallet/Trades)", type="password", max_chars=4)
            
            if st.form_submit_button("Complete Registration & Verification"):
                if new_user in st.session_state.users_db:
                    st.error("User ID already exists. Choose another.")
                elif len(pan_num) != 10 or len(ifsc_suffix) != 6 or len(new_pin) != 4 or not new_pin.isdigit():
                    st.error("Validation Error: Ensure PAN is 10 chars, IFSC suffix is 6 chars, and PIN is exactly 4 digits.")
                elif new_name and new_user and new_pass and acc_num:
                    st.session_state.users_db[new_user] = {
                        "name": new_name, "email": new_email, "password": new_pass,
                        "bank": sel_bank, "bank_acc": acc_num, "ifsc": f"{ifsc_prefix}{ifsc_suffix}",
                        "wallet": 0.0, "pin": new_pin, "portfolio": {},
                        "pref": "Always Ask" # Settlement preference
                    }
                    st.success("Verification complete. You may now login.")
                else:
                    st.error("Please fill all fields.")

    # Discreet Admin Login (Hidden in plain sight)
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    with st.expander("System Administration", expanded=False):
        admin_pass = st.text_input("Admin Access Key", type="password")
        if st.button("Access Node"):
            if admin_pass == "admin123": # Hardcoded admin password
                st.session_state.current_user = "admin"
                st.session_state.view_mode = "admin"
                st.rerun()
            else:
                st.error("Access Denied.")

# -----------------------------------------------------------------------------
# 3. ADMIN PORTAL
# -----------------------------------------------------------------------------
def render_admin():
    st.title("⚙️ System Administrator Portal")
    col1, col2 = st.columns([8, 2])
    col1.subheader("Registered Entity Database")
    if col2.button("Log Out Admin"):
        st.session_state.current_user = None
        st.session_state.view_mode = "auth"
        st.rerun()

    st.warning("Privacy Protocol Enforced: Individual holding metrics are hidden from administrative view.")
    
    admin_data = []
    for uid, data in st.session_state.users_db.items():
        admin_data.append({
            "User ID": uid,
            "Legal Name": data["name"],
            "Linked Bank": data["bank"],
            "Wallet Liquidity": f"₹{data['wallet']:,.2f}",
            "Active Positions": "RESTRICTED (Privacy Lock)"
        })
        
    if admin_data:
        st.table(pd.DataFrame(admin_data))
    else:
        st.info("No users registered in the database.")

# -----------------------------------------------------------------------------
# 4. USER SETTINGS
# -----------------------------------------------------------------------------
def render_settings():
    u_data = st.session_state.users_db[st.session_state.current_user]
    st.title("⚙️ Profile & Preferences")
    if st.button("⬅ Back to Dashboard"):
        st.session_state.view_mode = "dashboard"
        st.rerun()
        
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Update Identity")
        new_username = st.text_input("Change User ID", value=st.session_state.current_user)
        if st.button("Update ID"):
            if new_username != st.session_state.current_user:
                if new_username in st.session_state.users_db:
                    st.error("User ID taken.")
                else:
                    # Swap dictionary keys safely
                    st.session_state.users_db[new_username] = st.session_state.users_db.pop(st.session_state.current_user)
                    st.session_state.current_user = new_username
                    st.success("User ID updated successfully.")
                    st.rerun()

    with col2:
        st.subheader("Trading Preferences")
        pref_options = ["Always Ask", "Directly to Wallet", "Directly to Linked Bank Account"]
        current_idx = pref_options.index(u_data["pref"]) if u_data["pref"] in pref_options else 0
        new_pref = st.selectbox("Sales Settlement Routing Preference", pref_options, index=current_idx)
        if st.button("Save Preferences"):
            st.session_state.users_db[st.session_state.current_user]["pref"] = new_pref
            st.success("Routing preferences updated.")

# -----------------------------------------------------------------------------
# 5. MAIN TRADING DASHBOARD
# -----------------------------------------------------------------------------
def render_dashboard():
    u_data = st.session_state.users_db[st.session_state.current_user]
    
    # Top Utility Status Bar
    col_u, col_set, col_out, col_ref = st.columns([6, 1.5, 1, 1.5])
    col_u.markdown(f"👤 **Active Entity:** `{st.session_state.current_user}` | 🏦 **Bank:** `{u_data['bank']} (..{u_data['bank_acc'][-4:]})`")
    
    if col_set.button("⚙️ Settings"):
        st.session_state.view_mode = "settings"
        st.rerun()
    if col_out.button("🚪 Logout"):
        st.session_state.current_user = None
        st.session_state.view_mode = "auth"
        st.rerun()
    if col_ref.button("🔄 Sync Market"):
        update_market_prices()
        st.rerun()

    st.markdown("---")

    # Real-Time Global Indices Header
    idx_cols = st.columns(len(st.session_state.indices))
    for i, (name, metrics) in enumerate(st.session_state.indices.items()):
        change_val = metrics["price"] - metrics["prev"]
        pct_change = (change_val / metrics["prev"]) * 100
        idx_cols[i].metric(label=name, value=f"₹{metrics['price']:,}", delta=f"{change_val:+.2f} ({pct_change:+.2f}%)")
        
    st.markdown("---")

    # Section 1: Capital Wallet (PIN Verified)
    st.subheader("💳 Secure Clearing Wallet")
    w_col1, w_col2, w_col3 = st.columns([3, 4, 4])
    
    w_col1.metric("Available Liquidity Reserve", f"₹{u_data['wallet']:,.2f}")
    
    with w_col2:
        dep_amount = st.number_input("Transaction Volume (INR)", min_value=100.0, step=500.0, value=5000.0)
        wallet_pin = st.text_input("Enter 4-Digit Wallet PIN", type="password", max_chars=4, key="w_pin")
        
    with w_col3:
        st.markdown("<br>", unsafe_allow_html=True) # Spacing
        w_act1, w_act2 = st.columns(2)
        if w_act1.button("📥 Add Funds"):
            if wallet_pin == u_data["pin"]:
                st.session_state.users_db[st.session_state.current_user]["wallet"] += dep_amount
                st.success("Transfer authenticated. Funds added.")
                st.rerun()
            else:
                st.error("Authentication Failed: Incorrect PIN.")
                
        if w_act2.button("📤 Withdraw"):
            if wallet_pin == u_data["pin"]:
                if u_data["wallet"] >= dep_amount:
                    st.session_state.users_db[st.session_state.current_user]["wallet"] -= dep_amount
                    st.success(f"Withdrawn to {u_data['bank']}.")
                    st.rerun()
                else:
                    st.error("Overdraft Error: Insufficient funds.")
            else:
                st.error("Authentication Failed: Incorrect PIN.")

    st.markdown("---")

    # Section 2 & 3: Market Watchlist & Execution Terminal
    m_col, t_col = st.columns([1, 1])
    
    with m_col:
        st.subheader("📊 Primary Market Board")
        market_data = []
        for ticker, values in st.session_state.stocks.items():
            change = values["price"] - values["prev"]
            pct = (change / values["prev"]) * 100
            market_data.append({
                "Asset": ticker,
                "Spot Price": f"₹{values['price']:.2f}",
                "Daily Chg": f"{change:+.2f} ({pct:+.2f}%)"
            })
        st.dataframe(pd.DataFrame(market_data), use_container_width=True, hide_index=True)

    with t_col:
        st.subheader("⚡ Execution Terminal")
        with st.container(border=True):
            target_stock = st.selectbox("Select Asset", list(st.session_state.stocks.keys()))
            order_type = st.radio("Order Direction", ["BUY", "SELL"], horizontal=True)
            trade_qty = st.number_input("Quantity", min_value=1, step=1, value=1)
            
            current_unit_p = st.session_state.stocks[target_stock]["price"]
            total_est_cost = current_unit_p * trade_qty
            
            st.markdown(f"**Gross Settlement Capital:** `₹{total_est_cost:,.2f}`")
            
            # Settlement Preference Logic for Selling
            route_dest = u_data["pref"]
            if order_type == "SELL" and u_data["pref"] == "Always Ask":
                route_dest = st.selectbox("Route Sale Proceeds To:", ["Virtual Wallet", "Linked Bank Account"])
                
            entered_pin = st.text_input("Terminal Authorization PIN", type="password", max_chars=4, key="t_pin")
            
            if st.button(f"Commit {order_type} Sequence", use_container_width=True):
                if entered_pin != u_data["pin"]:
                    st.error("Execution Refused: Incorrect PIN.")
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
                            st.success(f"Acquired {trade_qty} blocks of {target_stock}.")
                            st.rerun()
                        else:
                            st.error("Execution Terminated: Insufficient Wallet Balance.")
                    
                    elif order_type == "SELL":
                        if target_stock in u_data["portfolio"] and u_data["portfolio"][target_stock]["qty"] >= trade_qty:
                            # Deduct from portfolio
                            st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock]["qty"] -= trade_qty
                            if st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock]["qty"] == 0:
                                del st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock]
                                
                            # Handle Settlement routing
                            if route_dest in ["Directly to Wallet", "Virtual Wallet"]:
                                st.session_state.users_db[st.session_state.current_user]["wallet"] += total_est_cost
                                st.success(f"Sold {trade_qty} {target_stock}. Proceeds added to Wallet.")
                            else:
                                st.success(f"Sold {trade_qty} {target_stock}. Proceeds routed to {u_data['bank']}.")
                            st.rerun()
                        else:
                            st.error("Execution Terminated: Insufficient portfolio inventory.")

    st.markdown("---")

    # Section 4: Customer Asset Portfolio
    st.subheader("💼 Active Asset Holdings Matrix")
    if not u_data["portfolio"]:
        st.info("No active positions held in ledger.")
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
                "Asset": ticker,
                "Qty": qty,
                "Avg Entry": f"₹{avg_p:,.2f}",
                "Current Value": f"₹{current_value:,.2f}",
                "Unrealized PnL": f"₹{pnl:+,.2f}"
            })
            
        st.dataframe(pd.DataFrame(portfolio_rows), use_container_width=True, hide_index=True)
        st.metric("Net Unrealized Portfolio Return", f"₹{total_pnl:+,.2f}")

# -----------------------------------------------------------------------------
# 6. APP CONTROLLER
# -----------------------------------------------------------------------------
if st.session_state.view_mode == "auth":
    render_auth()
elif st.session_state.view_mode == "dashboard" and st.session_state.current_user:
    render_dashboard()
elif st.session_state.view_mode == "settings" and st.session_state.current_user:
    render_settings()
elif st.session_state.view_mode == "admin" and st.session_state.current_user == "admin":
    render_admin()
else:
    # Failsafe
    st.session_state.view_mode = "auth"
    st.rerun()
