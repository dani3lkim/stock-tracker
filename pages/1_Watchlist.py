import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import yfinance as yf
import pandas as pd
from db import (
    get_tracked_stocks, add_stock, remove_stock,
    get_tags, get_tags_for_stock, set_stock_tags, get_stocks_with_tags
)

st.set_page_config(page_title="Watchlist", layout="wide")
st.title("Watchlist")

# --- Add Stock ---
with st.form("add_stock"):
    new_ticker = st.text_input("Ticker Symbol *", placeholder="e.g. AAPL")
    submitted = st.form_submit_button("Add to Watchlist")

if submitted:
    new_ticker = new_ticker.upper().strip()
    errors = []
    if not new_ticker:
        errors.append("**Ticker** is required.")
    elif len(new_ticker) > 10:
        errors.append("**Ticker** must be 10 characters or fewer.")
    if errors:
        for e in errors:
            st.error(e)
    else:
        stock_id = add_stock(new_ticker)
        if stock_id:
            st.success(f"{new_ticker} added to watchlist.")
        else:
            st.warning(f"{new_ticker} is already on your watchlist.")
        st.rerun()

st.divider()

# --- Search ---
search = st.text_input("Search watchlist", placeholder="Filter by ticker or tag...")

stocks = get_tracked_stocks()
stocks_with_tags = get_stocks_with_tags()

if search.strip():
    s = search.strip().upper()
    stocks_with_tags = [
        r for r in stocks_with_tags
        if s in r["ticker"] or (r["tags"] and s in r["tags"].upper())
    ]

if not stocks_with_tags:
    st.info("No stocks match your search." if search.strip() else "No stocks on your watchlist yet.")
else:
    # Price table
    rows = []
    for row in stocks_with_tags:
        try:
            info = yf.Ticker(row["ticker"]).fast_info
            rows.append({
                "Ticker": row["ticker"],
                "Tags": row["tags"] or "",
                "Price": f"${info.last_price:.2f}",
                "Day High": f"${info.day_high:.2f}",
                "Day Low": f"${info.day_low:.2f}",
                "52W High": f"${info.fifty_two_week_high:.2f}",
                "52W Low": f"${info.fifty_two_week_low:.2f}",
            })
        except Exception:
            rows.append({
                "Ticker": row["ticker"],
                "Tags": row["tags"] or "",
                "Price": "N/A", "Day High": "-", "Day Low": "-",
                "52W High": "-", "52W Low": "-",
            })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()

    # --- Tag Assignment ---
    st.subheader("Assign Tags")
    all_tags = get_tags()
    if not all_tags:
        st.info("No tags yet. Create some on the Tags page.")
    else:
        ticker_map = {r["ticker"]: r["id"] for r in stocks}
        tag_map = {t["name"]: t["id"] for t in all_tags}

        col1, col2 = st.columns([2, 3])
        with col1:
            selected_ticker = st.selectbox(
                "Select stock to tag",
                options=[r["ticker"] for r in stocks_with_tags]
            )
        if selected_ticker and selected_ticker in ticker_map:
            stock_id = ticker_map[selected_ticker]
            current_tags = [t["name"] for t in get_tags_for_stock(stock_id)]
            with col2:
                chosen = st.multiselect(
                    "Tags",
                    options=list(tag_map.keys()),
                    default=current_tags
                )
            if st.button("Save Tags"):
                set_stock_tags(stock_id, [tag_map[n] for n in chosen])
                st.success("Tags updated.")
                st.rerun()

    st.divider()

    # --- Price Chart ---
    st.subheader("Price Chart")
    chart_ticker = st.selectbox(
        "Select ticker to chart",
        options=[r["ticker"] for r in stocks_with_tags]
    )
    period = st.select_slider("Period", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="3mo")
    if chart_ticker:
        hist = yf.Ticker(chart_ticker).history(period=period)
        if not hist.empty:
            st.line_chart(hist["Close"], use_container_width=True)

    st.divider()

    # --- Remove ---
    st.subheader("Remove from Watchlist")
    ticker_options = [r["ticker"] for r in stocks_with_tags]
    to_remove = st.selectbox("Select ticker to remove", ticker_options, key="remove_sel")

    if "confirm_remove_stock" not in st.session_state:
        st.session_state.confirm_remove_stock = False

    if st.button("Remove"):
        st.session_state.confirm_remove_stock = True

    if st.session_state.confirm_remove_stock:
        st.warning(f"Are you sure you want to remove **{to_remove}** from your watchlist?")
        c1, c2 = st.columns(2)
        if c1.button("Yes, remove it"):
            remove_stock(to_remove)
            st.session_state.confirm_remove_stock = False
            st.success(f"{to_remove} removed.")
            st.rerun()
        if c2.button("Cancel"):
            st.session_state.confirm_remove_stock = False
            st.rerun()
