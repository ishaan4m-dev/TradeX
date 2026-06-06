import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="BullRun - Stock Simulator", page_icon="📈", layout="wide")

# -----------------------------------------------------------------------------
# 1. GLOBAL STATE INITIALIZATION (Simulated Database)
# -----------------------------------------------------------------------------
if "users_db" not in st.session_state:
    st.session_state.users_db = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "auth"
    
# State for interactive table buttons to auto-fill the trading terminal
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
    st.title("🛡️ BullRun Institutional Trading")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    # Login Module (Handles both Users and Admin)
    with col1:
        st.subheader("Login to Environment")
        with st.form("login_form"):
            login_user = st.text_input("User ID (Username)")
            login_pass = st.text_input("Password", type="password")
            
            if st.form_submit_button("Authenticate Session"):
                # Admin Login Bypass Check
                if login_user == "123456" and login_pass == "121212":
                    st.session_state.current_user = "admin"
                    st.session_state.view_mode = "admin"
                    st.rerun()
                # Standard User Check
                elif login_user in st.session_state.users_db and st.session_state.users_db[login_user]["password"] == login_pass:
                    st.session_state.current_user = login_user
                    st.session_state.view_mode = "dashboard"
                    st.rerun()
                else:
                    st.error("Authentication Failed: Invalid ID or Password.")
                    
    # Signup Module
    with col2:
        st.subheader("New Entity Registration (KYC)")
        
        # We put the bank selection OUTSIDE the form so it can dynamically update the IFSC display in real-time
        sel_bank = st.selectbox("Select Core Bank", list(BANK_PREFIXES.keys()))
        ifsc_prefix = BANK_PREFIXES[sel_bank]
        
        with st.form("signup_form"):
            new_name = st.text_input("Full Legal Name")
            new_email = st.text_input("Email Address")
            new_user = st.text_input("Choose User ID")
            new_pass = st.text_input("Create Password", type="password")
            
            st.markdown("##### Identity & Banking Link")
            pan_num = st.text_input("10-Digit PAN Card Number", max_chars=10)
            acc_num = st.text_input("Bank Account Number", type="password")
            
            # Show dynamic prefix and ask for suffix
            st.markdown(f"**Bank IFSC Prefix:** `{ifsc_prefix}`")
            ifsc_suffix = st.text_input("Enter remaining 6 digits of IFSC", max_chars=6)
            
            st.markdown("##### Security Setup")
            new_pin = st.text_input("Create 4-Digit Secure PIN", type="password", max_chars=4)
            
            if st.form_submit_button("Complete Registration"):
                if new_user == "123456" or new_user == "admin":
                    st.error("Reserved Admin ID cannot be used.")
                elif new_user in st.session_state.users_db:
                    st.error("User ID already exists.")
                elif len(pan_num) != 10 or len(ifsc_suffix) != 6 or len(new_pin) != 4:
                    st.error("Ensure PAN is 10 chars, IFSC suffix is 6 chars, and PIN is 4 digits.")
                elif new_name and new_user and new_pass and acc_num:
                    st.session_state.users_db[new_user] = {
                        "name": new_name, "email": new_email, "password": new_pass,
                        "bank": sel_bank, "bank_acc": acc_num, "ifsc": f"{ifsc_prefix}{ifsc_suffix}",
                        "wallet": 0.0, "pin": new_pin, "portfolio": {}, "pref": "Always Ask"
                    }
                    st.success("Verification complete. You may now login on the left.")
                else:
                    st.error("Please fill all fields.")

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

    st.warning("Privacy Protocol Enforced: Individual holdings are hidden.")
    
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
        st.info("No users registered yet.")

# -----------------------------------------------------------------------------
# 4. MAIN TRADING DASHBOARD
# -----------------------------------------------------------------------------
def render_dashboard():
    u_data = st.session_state.users_db[st.session_state.current_user]
    
    # Top Bar
    col_u, col_out, col_ref = st.columns([8, 1, 1.5])
    col_u.markdown(f"👤 **{st.session_state.current_user}** | 🏦 `{u_data['bank']}` | IFSC: `{u_data['ifsc']}`")
    
    if col_out.button("🚪 Logout"):
        st.session_state.current_user = None
        st.session_state.view_mode = "auth"
        st.rerun()
    if col_ref.button("🔄 Sync Market"):
        update_market_prices()
        st.rerun()
    st.markdown("---")

    # Indices
    idx_cols = st.columns(len(st.session_state.indices))
    for i, (name, metrics) in enumerate(st.session_state.indices.items()):
        change_val = metrics["price"] - metrics["prev"]
        pct_change = (change_val / metrics["prev"]) * 100
        idx_cols[i].metric(label=name, value=f"₹{metrics['price']:,}", delta=f"{change_val:+.2f} ({pct_change:+.2f}%)")
    st.markdown("---")

    # Wallet
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
                st.success("Funds added successfully.")
                st.rerun()
            else:
                st.error("Incorrect PIN.")
        if w_act2.button("📤 Withdraw", use_container_width=True):
            if wallet_pin == u_data["pin"]:
                if u_data["wallet"] >= dep_amount:
                    st.session_state.users_db[st.session_state.current_user]["wallet"] -= dep_amount
                    st.success("Withdrawal processed.")
                    st.rerun()
                else:
                    st.error("Insufficient funds.")
            else:
                st.error("Incorrect PIN.")
    st.markdown("---")

    # Market Board & Execution Split
    m_col, t_col = st.columns([1.2, 0.8])
    
    with m_col:
        st.subheader("📊 Live Market Board")
        # Creating an interactive table using Streamlit columns
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
            
            # Interactive Trade Buttons
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
            # Auto-populates based on the button clicked in the Market Board
            stock_list = list(st.session_state.stocks.keys())
            default_stock_idx = stock_list.index(st.session_state.selected_ticker) if st.session_state.selected_ticker in stock_list else 0
            
            target_stock = st.selectbox("Select Asset", stock_list, index=default_stock_idx)
            
            action_list = ["BUY", "SELL"]
            default_action_idx = action_list.index(st.session_state.trade_action)
            order_type = st.radio("Order Direction", action_list, index=default_action_idx, horizontal=True)
            
            trade_qty = st.number_input("Quantity", min_value=1, step=1, value=1)
            
            current_unit_p = st.session_state.stocks[target_stock]["price"]
            total_est_cost = current_unit_p * trade_qty
            st.markdown(f"**Total Capital:** `₹{total_est_cost:,.2f}`")
            
            entered_pin = st.text_input("Authorization PIN", type="password", max_chars=4, key="t_pin")
            
            btn_color = "primary" if order_type == "BUY" else "secondary"
            if st.button(f"Commit {order_type} Sequence", use_container_width=True, type=btn_color):
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
                            st.error("Insufficient Wallet Balance.")
                    
                    elif order_type == "SELL":
                        if target_stock in u_data["portfolio"] and u_data["portfolio"][target_stock]["qty"] >= trade_qty:
                            st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock]["qty"] -= trade_qty
                            st.session_state.users_db[st.session_state.current_user]["wallet"] += total_est_cost
                            if st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock]["qty"] == 0:
                                del st.session_state.users_db[st.session_state.current_user]["portfolio"][target_stock]
                            st.success(f"Sold {trade_qty} {target_stock}. Added to Wallet.")
                            st.rerun()
                        else:
                            st.error("Insufficient portfolio inventory.")

    st.markdown("---")

    # Section 4: Holdings
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
                "Asset": ticker, "Qty": qty, "Avg Entry": f"₹{avg_p:,.2f}",
                "Current Value": f"₹{current_value:,.2f}", "Unrealized PnL": f"₹{pnl:+,.2f}"
            })
            
        st.dataframe(pd.DataFrame(portfolio_rows), use_container_width=True, hide_index=True)
        st.metric("Net Unrealized Portfolio Return", f"₹{total_pnl:+,.2f}")

# -----------------------------------------------------------------------------
# 5. APP CONTROLLER
# -----------------------------------------------------------------------------
if st.session_state.view_mode == "auth":
    render_auth()
elif st.session_state.view_mode == "dashboard" and st.session_state.current_user:
    render_dashboard()
elif st.session_state.view_mode == "admin" and st.session_state.current_user == "admin":
    render_admin()
else:
    st.session_state.view_mode = "auth"
    st.rerun()
