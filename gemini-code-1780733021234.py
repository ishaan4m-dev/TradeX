import streamlit as st
import random
import pandas as pd

# Set up page configuration
st.set_page_config(page_title="BullRun - Stock Simulator", page_icon="📈", layout="wide")

# -----------------------------------------------------------------------------
# 1. STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = "register"  # register, kyc, bank, wallet, completed
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "wallet_balance" not in st.session_state:
    st.session_state.wallet_balance = 0.0
if "bank_linked" not in st.session_state:
    st.session_state.bank_linked = False
if "bank_account" not in st.session_state:
    st.session_state.bank_account = ""
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}  # Format: {"TICKER": {"qty": int, "avg_price": float}}
if "secure_pin" not in st.session_state:
    st.session_state.secure_pin = ""

# Initialize a fixed market baseline if not present
if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "RELIANCE": {"price": 2450.0, "prev": 2420.0},
        "TCS": {"price": 3200.0, "prev": 3215.0},
        "INFY": {"price": 1420.0, "prev": 1400.0},
        "HDFCBANK": {"price": 1650.0, "prev": 1665.0},
        "TATAMOTORS": {"price": 610.0, "prev": 595.0},
        "ICICIBANK": {"price": 950.0, "prev": 942.0},
    }
if "indices" not in st.session_state:
    st.session_state.indices = {
        "NIFTY 50": {"price": 22120.0, "prev": 22010.0},
        "SENSEX": {"price": 72800.0, "prev": 72550.0}
    }

# Function to simulate market price fluctuations
def update_market_prices():
    for ticker in st.session_state.stocks:
        change = random.uniform(-0.015, 0.015) # Max 1.5% movement
        st.session_state.stocks[ticker]["prev"] = st.session_state.stocks[ticker]["price"]
        st.session_state.stocks[ticker]["price"] = round(st.session_state.stocks[ticker]["price"] * (1 + change), 2)
    
    for index in st.session_state.indices:
        change = random.uniform(-0.008, 0.008) # Indices move slightly less
        st.session_state.indices[index]["prev"] = st.session_state.indices[index]["price"]
        st.session_state.indices[index]["price"] = round(st.session_state.indices[index]["price"] * (1 + change), 2)

# -----------------------------------------------------------------------------
# 2. ONBOARDING PIPELINE
# -----------------------------------------------------------------------------
def render_onboarding():
    st.title("🛡️ Welcome to BullRun Simulator")
    st.subheader("Complete your verification pipeline to begin trading.")
    
    # Progress visualization indicator
    steps = ["Registration", "KYC Verification", "Link Bank Account", "Setup Secure Pin"]
    current_idx = ["register", "kyc", "bank", "pin"].index(st.session_state.onboarding_step)
    
    cols = st.columns(4)
    for idx, name in enumerate(steps):
        if idx < current_idx:
            cols[idx].success(f"✓ {name}")
        elif idx == current_idx:
            cols[idx].info(f"👉 {name}")
        else:
            cols[idx].text(f"⚪ {name}")
            
    st.markdown("---")

    # Step A: Standard Registration
    if st.session_state.onboarding_step == "register":
        st.markdown("### Step 1: User Account Registration")
        with st.form("reg_form"):
            full_name = st.text_input("Full Name (As per PAN/Aadhaar)")
            email = st.text_input("Email Address")
            username = st.text_input("Choose Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Proceed to KYC"):
                if full_name and email and username and password:
                    st.session_state.user_profile = {"name": full_name, "email": email, "username": username}
                    st.session_state.onboarding_step = "kyc"
                    st.rerun()
                else:
                    st.error("Please fill out all initialization fields.")

    # Step B: Identity Verification Checklist
    elif st.session_state.onboarding_step == "kyc":
        st.markdown("### Step 2: Zero-Trust Identity & KYC Verification")
        st.info("As a strict prototype deployment rule, confirm authenticity documents below.")
        
        pan_num = st.text_input("Enter 10-Digit PAN Card Number", max_chars=10, help="Example: ABCDE1234F")
        aadhaar_num = st.text_input("Enter 12-Digit Aadhaar Card Number", max_chars=12)
        
        c1 = st.checkbox("I verify that the uploaded credentials belong to me.")
        c2 = st.checkbox("I agree to open a non-commercial simulated brokerage account.")
        
        if st.button("Submit Verification Protocol"):
            if len(pan_num) == 10 and len(aadhaar_num) == 12 and c1 and c2:
                st.session_state.onboarding_step = "bank"
                st.rerun()
            else:
                st.error("Please provide valid document lengths and check all certification fields.")

    # Step C: Bank Account Integration Link
    elif st.session_state.onboarding_step == "bank":
        st.markdown("### Step 3: Centralized Node Bank Linkage")
        st.warning("This links a virtual credit line interface for handling instant wallet settlements.")
        
        bank_name = st.selectbox("Select Core Banking Institution", ["State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank"])
        acc_num = st.text_input("Enter Routing Account Number", type="password")
        ifsc_code = st.text_input("Enter IFSC Branch Code Code")
        
        if st.button("Link Liquidity Provider"):
            if acc_num and ifsc_code:
                st.session_state.bank_linked = True
                st.session_state.bank_account = f"{bank_name} (Acc: *******{acc_num[-4:] if len(acc_num)>4 else '1234'})"
                st.session_state.onboarding_step = "pin"
                st.rerun()
            else:
                st.error("Account variables cannot be left unassigned.")

    # Step D: Secure Terminal Access Key (PIN)
    elif st.session_state.onboarding_step == "pin":
        st.markdown("### Step 4: Configure Secure Transaction PIN")
        st.info("This numeric string prevents accidental executions and fat-finger errors during order entry.")
        
        pin = st.text_input("Create 4-Digit Security PIN", type="password", max_chars=4)
        confirm_pin = st.text_input("Confirm Security PIN", type="password", max_chars=4)
        
        if st.button("Finalize Core Environment"):
            if len(pin) == 4 and pin.isdigit() and pin == confirm_pin:
                st.session_state.secure_pin = pin
                st.session_state.onboarding_step = "completed"
                st.success("Environment setup finalized successfully.")
                st.rerun()
            else:
                st.error("PIN elements must be numeric, exactly 4-digits, and perfectly matching.")

# -----------------------------------------------------------------------------
# 3. TRADING & LEDGER ENGINE
# -----------------------------------------------------------------------------
def render_dashboard():
    # Top Utility Status Bar
    col_user, col_refresh = st.columns([8, 2])
    col_user.markdown(f"👤 **Account Active:** {st.session_state.user_profile.get('name')} | Linked Bank Node: `{st.session_state.bank_account}`")
    if col_refresh.button("🔄 Sync Live Market Feeds"):
        update_market_prices()
        st.rerun()

    st.markdown("---")

    # Real-Time Global Indices Metrics Header
    idx_cols = st.columns(len(st.session_state.indices))
    for i, (name, metrics) in enumerate(st.session_state.indices.items()):
        change_val = metrics["price"] - metrics["prev"]
        pct_change = (change_val / metrics["prev"]) * 100
        idx_cols[i].metric(
            label=name,
            value=f"₹{metrics['price']:,}",
            delta=f"{change_val:+.2f} ({pct_change:+.2f}%)"
        )
        
    st.markdown("---")

    # Section 1: Capital Wallet Controller
    st.subheader("💳 Virtual Clearing Account Balance Ledger")
    w_col1, w_col2, w_col3 = st.columns([4, 4, 4])
    
    w_col1.metric("Available Liquidity Reserve", f"₹{st.session_state.wallet_balance:,.2f}")
    
    dep_amount = w_col2.number_input("Transaction Volume Config (INR)", min_value=100.0, step=500.0, value=10000.0)
    
    w_actions = w_col3.columns(2)
    if w_actions[0].button("📥 Add Funds"):
        st.session_state.wallet_balance += dep_amount
        st.success(f"Deposited ₹{dep_amount:,.2f} via {st.session_state.bank_account}")
        st.rerun()
        
    if w_actions[1].button("📤 Withdraw"):
        if st.session_state.wallet_balance >= dep_amount:
            st.session_state.wallet_balance -= dep_amount
            st.info(f"Transferred ₹{dep_amount:,.2f} out to linked banking portal.")
            st.rerun()
        else:
            st.error("Overdraft Protection Warning: Insufficient wallet liquidity limits.")

    st.markdown("---")

    # Section 2: Spot Market Watchlist
    st.subheader("📊 Primary Market Board (No Charts)")
    
    market_data = []
    for ticker, values in st.session_state.stocks.items():
        change = values["price"] - values["prev"]
        pct = (change / values["prev"]) * 100
        market_data.append({
            "Asset Symbol": ticker,
            "Spot Price (INR)": f"₹{values['price']:.2f}",
            "Daily Fluctuations": f"{change:+.2f} ({pct:+.2f}%)"
        })
    st.table(pd.DataFrame(market_data))

    # Section 3: Trade Order Input Terminal
    st.subheader("⚡ Secure Execution Terminal")
    t_col1, t_col2, t_col3, t_col4 = st.columns([3, 2, 3, 4])
    
    target_stock = t_col1.selectbox("Select Asset Vehicle", list(st.session_state.stocks.keys()))
    order_type = t_col2.radio("Order Type", ["BUY", "SELL"])
    trade_qty = t_col3.number_input("Share Multiplier Volume", min_value=1, step=1, value=1)
    
    current_unit_p = st.session_state.stocks[target_stock]["price"]
    total_est_cost = current_unit_p * trade_qty
    
    t_col4.markdown(f"**Unit Spot Value:** ₹{current_unit_p:,.2f}")
    t_col4.markdown(f"**Gross Settlement Capital:** `₹{total_est_cost:,.2f}`")
    
    entered_pin = t_col4.text_input("Enter 4-Digit Transaction Pin for Authorization", type="password", max_chars=4)
    
    if t_col4.button(f"Commit {order_type} Order Sequence"):
        if entered_pin != st.session_state.secure_pin:
            st.error("Execution Refused: Security PIN confirmation mismatch.")
        else:
            if order_type == "BUY":
                if st.session_state.wallet_balance >= total_est_cost:
                    st.session_state.wallet_balance -= total_est_cost
                    
                    # Update holding record matrices
                    if target_stock in st.session_state.portfolio:
                        existing_qty = st.session_state.portfolio[target_stock]["qty"]
                        existing_avg = st.session_state.portfolio[target_stock]["avg_price"]
                        new_qty = existing_qty + trade_qty
                        new_avg = ((existing_avg * existing_qty) + total_est_cost) / new_qty
                        st.session_state.portfolio[target_stock] = {"qty": new_qty, "avg_price": round(new_avg, 2)}
                    else:
                        st.session_state.portfolio[target_stock] = {"qty": trade_qty, "avg_price": current_unit_p}
                        
                    st.success(f"Asset Purchase Locked: Acquired {trade_qty} unit blocks of {target_stock}.")
                    st.rerun()
                else:
                    st.error("Execution Terminated: Insufficient Wallet Balance limits.")
            
            elif order_type == "SELL":
                if target_stock in st.session_state.portfolio and st.session_state.portfolio[target_stock]["qty"] >= trade_qty:
                    st.session_state.portfolio[target_stock]["qty"] -= trade_qty
                    st.session_state.wallet_balance += total_est_cost
                    
                    if st.session_state.portfolio[target_stock]["qty"] == 0:
                        del st.session_state.portfolio[target_stock]
                        
                    st.success(f"Liquidation Confirmed: Disposed {trade_qty} blocks of {target_stock}.")
                    st.rerun()
                else:
                    st.error("Execution Terminated: Short positions forbidden. Insufficient portfolio inventory.")

    st.markdown("---")

    # Section 4: Customer Asset Portfolio Metrics Ledger
    st.subheader("💼 Active Asset Holdings Matrix")
    if not st.session_state.portfolio:
        st.info("No active open trading parameters verified inside the ledger.")
    else:
        portfolio_rows = []
        total_pnl = 0.0
        for ticker, data in st.session_state.portfolio.items():
            qty = data["qty"]
            avg_p = data["avg_price"]
            current_p = st.session_state.stocks[ticker]["price"]
            invested_cap = qty * avg_p
            current_value = qty * current_p
            pnl = current_value - invested_cap
            total_pnl += pnl
            
            portfolio_rows.append({
                "Asset Symbol": ticker,
                "Quantity Held": qty,
                "Average Entry Price": f"₹{avg_p:,.2f}",
                "Current Valuation": f"₹{current_p:,.2f}",
                "Total Capital Allocation": f"₹{invested_cap:,.2f}",
                "Unrealized Gain/Loss": f"₹{pnl:+,.2f}"
            })
            
        st.table(pd.DataFrame(portfolio_rows))
        st.metric("Aggregate Net Realized Return Portfolio Metric", f"₹{total_pnl:+,.2f}", delta=f"{total_pnl:+.2f}")

# -----------------------------------------------------------------------------
# 4. CONTROLLER ORCHESTRATION
# -----------------------------------------------------------------------------
if st.session_state.onboarding_step != "completed":
    render_onboarding()
else:
    render_dashboard()