import streamlit as st
import yfinance as yf
from db import init_db, get_counts, get_stocks_with_tags, get_portfolio

st.set_page_config(page_title="Stock Tracker", layout="wide")
init_db()

st.title("Stock Tracker — Dashboard")

stock_count, position_count, tag_count = get_counts()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Watchlist Stocks", stock_count)
m2.metric("Portfolio Positions", position_count)
m3.metric("Tags", tag_count)

# Compute total portfolio value
positions = get_portfolio()
total_value = 0.0
total_cost = 0.0
for pos in positions:
    try:
        current_price = yf.Ticker(pos["ticker"]).fast_info.last_price
        total_value += float(pos["shares"]) * current_price
        total_cost += float(pos["shares"]) * float(pos["buy_price"])
    except Exception:
        pass

gain = total_value - total_cost
gain_pct = (gain / total_cost * 100) if total_cost else 0
m4.metric(
    "Portfolio Value",
    f"${total_value:,.2f}",
    f"{gain_pct:+.1f}%"
)

st.divider()

st.subheader("Watchlist")
rows = get_stocks_with_tags()
if rows:
    import pandas as pd
    df = pd.DataFrame([{"Ticker": r["ticker"], "Tags": r["tags"] or ""} for r in rows])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No stocks on watchlist yet.")
