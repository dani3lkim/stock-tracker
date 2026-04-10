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
rows = get_stocks_with_tags()
if rows:
    table = []
    for r in rows:
        try:
            info = yf.Ticker(r["ticker"]).fast_info
            change = info.last_price - info.previous_close
            change_pct = (change / info.previous_close) * 100
            table.append({
                "Ticker": r["ticker"],
                "Price": f"${info.last_price:.2f}",
                "Change": f"${change:+.2f} ({change_pct:+.1f}%)",
                "Day High": f"${info.day_high:.2f}",
                "Day Low": f"${info.day_low:.2f}",
                "52W High": f"${info.fifty_two_week_high:.2f}",
                "52W Low": f"${info.fifty_two_week_low:.2f}",
                "Tags": r["tags"] or "",
            })
        except Exception:
            table.append({
                "Ticker": r["ticker"],
                "Price": "N/A",
                "Change": "-",
                "Day High": "-",
                "Day Low": "-",
                "52W High": "-",
                "52W Low": "-",
                "Tags": r["tags"] or "",
            })
    st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)
else:
    st.info("No stocks on watchlist yet.")
