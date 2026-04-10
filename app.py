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
import pandas as pd

def fmt(val):
    return f"${val:.2f}" if val is not None else "N/A"

rows = get_stocks_with_tags()
if rows:
    table = []
    for r in rows:
        try:
            info = yf.Ticker(r["ticker"]).fast_info
            price = info.last_price
            prev = info.previous_close
            if price is not None and prev is not None and prev != 0:
                change = price - prev
                change_pct = (change / prev) * 100
                change_str = f"${change:+.2f} ({change_pct:+.1f}%)"
            else:
                change_str = "N/A"
            table.append({
                "Ticker": r["ticker"],
                "Price": fmt(price),
                "Change": change_str,
                "Day High": fmt(info.day_high),
                "Day Low": fmt(info.day_low),
                "52W High": fmt(info.fifty_two_week_high),
                "52W Low": fmt(info.fifty_two_week_low),
                "Tags": r["tags"] or "",
            })
        except Exception:
            table.append({
                "Ticker": r["ticker"],
                "Price": "N/A", "Change": "-",
                "Day High": "-", "Day Low": "-",
                "52W High": "-", "52W Low": "-",
                "Tags": r["tags"] or "",
            })
    st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)
else:
    st.info("No stocks on watchlist yet.")
