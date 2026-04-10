import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import yfinance as yf
import pandas as pd
from db import get_portfolio, add_position, update_position, remove_position

st.set_page_config(page_title="Portfolio", layout="wide")
st.title("Portfolio")

# --- Add Position ---
with st.expander("Add Position"):
    with st.form("add_position"):
        c1, c2, c3 = st.columns(3)
        with c1:
            p_ticker = st.text_input("Ticker *")
        with c2:
            p_shares = st.number_input("Shares *", min_value=0.0, step=1.0, format="%.4f")
        with c3:
            p_price = st.number_input("Buy Price ($) *", min_value=0.0, step=0.01, format="%.2f")
        submitted = st.form_submit_button("Add Position")

if submitted:
    p_ticker = p_ticker.upper().strip()
    errors = []
    if not p_ticker:
        errors.append("**Ticker** is required.")
    elif len(p_ticker) > 10:
        errors.append("**Ticker** must be 10 characters or fewer.")
    if p_shares <= 0:
        errors.append("**Shares** must be a positive number.")
    if p_price <= 0:
        errors.append("**Buy Price** must be a positive number.")
    if errors:
        for e in errors:
            st.error(e)
    else:
        add_position(p_ticker, p_shares, p_price)
        st.success(f"Position in {p_ticker} added.")
        st.rerun()

st.divider()

# --- Search ---
search = st.text_input("Search positions", placeholder="Filter by ticker...")

positions = get_portfolio()
if search.strip():
    s = search.strip().upper()
    positions = [p for p in positions if s in p["ticker"].upper()]

if not positions:
    st.info("No positions match your search." if search.strip() else "No positions yet. Add one above.")
else:
    rows = []
    total_value = 0.0
    total_cost = 0.0
    for pos in positions:
        try:
            hist = yf.Ticker(pos["ticker"]).history(period="1d")
            current_price = hist["Close"].iloc[-1] if not hist.empty else None
            if current_price is None:
                raise ValueError("No price")
            cost = float(pos["shares"]) * float(pos["buy_price"])
            value = float(pos["shares"]) * current_price
            gain = value - cost
            gain_pct = (gain / cost) * 100
            total_value += value
            total_cost += cost
            rows.append({
                "ID": pos["id"],
                "Ticker": pos["ticker"],
                "Shares": pos["shares"],
                "Buy Price": f"${float(pos['buy_price']):.2f}",
                "Current Price": f"${current_price:.2f}",
                "Value": f"${value:.2f}",
                "Gain/Loss": f"${gain:+.2f} ({gain_pct:+.1f}%)",
            })
        except Exception:
            rows.append({
                "ID": pos["id"],
                "Ticker": pos["ticker"],
                "Shares": pos["shares"],
                "Buy Price": f"${float(pos['buy_price']):.2f}",
                "Current Price": "N/A",
                "Value": "N/A",
                "Gain/Loss": "N/A",
            })

    df = pd.DataFrame(rows).drop(columns=["ID"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    if total_cost > 0:
        total_gain = total_value - total_cost
        total_gain_pct = total_gain / total_cost * 100
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Value", f"${total_value:,.2f}")
        m2.metric("Total Cost", f"${total_cost:,.2f}")
        m3.metric("Total Gain/Loss", f"${total_gain:+,.2f}", f"{total_gain_pct:+.1f}%")

    st.divider()

    # --- Edit Position ---
    st.subheader("Edit Position")
    pos_options = {f"{p['ticker']} (ID {p['id']})": p for p in positions}
    selected_label = st.selectbox("Select position to edit", list(pos_options.keys()))
    selected_pos = pos_options[selected_label]

    with st.form("edit_position"):
        e1, e2 = st.columns(2)
        with e1:
            new_shares = st.number_input(
                "Shares *",
                value=float(selected_pos["shares"]),
                min_value=0.0001,
                step=1.0,
                format="%.4f"
            )
        with e2:
            new_price = st.number_input(
                "Buy Price ($) *",
                value=float(selected_pos["buy_price"]),
                min_value=0.01,
                step=0.01,
                format="%.2f"
            )
        edit_submitted = st.form_submit_button("Save Changes")

    if edit_submitted:
        errors = []
        if new_shares <= 0:
            errors.append("**Shares** must be a positive number.")
        if new_price <= 0:
            errors.append("**Buy Price** must be a positive number.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            update_position(selected_pos["id"], new_shares, new_price)
            st.success("Position updated.")
            st.rerun()

    st.divider()

    # --- Delete Position ---
    st.subheader("Delete Position")
    del_options = {f"{p['ticker']} (ID {p['id']})": p["id"] for p in positions}
    del_label = st.selectbox("Select position to delete", list(del_options.keys()), key="del_sel")

    if "confirm_del_pos" not in st.session_state:
        st.session_state.confirm_del_pos = False

    if st.button("Delete"):
        st.session_state.confirm_del_pos = True

    if st.session_state.confirm_del_pos:
        st.warning(f"Are you sure you want to delete **{del_label}**?")
        c1, c2 = st.columns(2)
        if c1.button("Yes, delete it"):
            remove_position(del_options[del_label])
            st.session_state.confirm_del_pos = False
            st.success("Position deleted.")
            st.rerun()
        if c2.button("Cancel"):
            st.session_state.confirm_del_pos = False
            st.rerun()
