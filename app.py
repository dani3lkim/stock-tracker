import streamlit as st
import yfinance as yf
import pandas as pd
from db import init_db, get_counts, get_stocks_with_tags, get_portfolio, get_tracked_stocks

st.set_page_config(page_title="Stock Tracker", layout="wide")
init_db()

st.title("Stock Tracker — Dashboard")

# --- Live Ticker Tape ---
@st.fragment(run_every=30)
def ticker_tape():
    tickers = get_tracked_stocks()
    if not tickers:
        return
    items = []
    for t in tickers:
        try:
            hist = yf.Ticker(t["ticker"]).history(period="2d")
            if not hist.empty and len(hist) >= 2:
                price = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                change_pct = ((price - prev) / prev) * 100
                color = "#00cc66" if change_pct >= 0 else "#ff4444"
                arrow = "▲" if change_pct >= 0 else "▼"
                items.append(
                    f'<span style="margin:0 24px; color:white; font-weight:bold;">'
                    f'{t["ticker"]} '
                    f'<span style="color:{color};">${price:.2f} {arrow}{abs(change_pct):.2f}%</span>'
                    f'</span>'
                )
        except Exception:
            pass

    if not items:
        return

    content = "".join(items * 3)
    st.markdown(f"""
    <div style="
        background:#1a1a2e;
        border:1px solid #333;
        border-radius:6px;
        padding:10px 0;
        overflow:hidden;
        white-space:nowrap;
        margin-bottom:16px;
    ">
        <div style="
            display:inline-block;
            animation:ticker 20s linear infinite;
            font-size:14px;
            font-family:monospace;
        ">
            {content}
        </div>
    </div>
    <style>
        @keyframes ticker {{
            0%   {{ transform: translateX(0); }}
            100% {{ transform: translateX(-33.33%); }}
        }}
    </style>
    """, unsafe_allow_html=True)

ticker_tape()

# --- Metrics ---
stock_count, position_count, tag_count = get_counts()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Watchlist Stocks", stock_count)
m2.metric("Portfolio Positions", position_count)
m3.metric("Tags", tag_count)

positions = get_portfolio()
total_value = 0.0
total_cost = 0.0
for pos in positions:
    try:
        hist = yf.Ticker(pos["ticker"]).history(period="1d")
        if not hist.empty:
            current_price = hist["Close"].iloc[-1]
            total_value += float(pos["shares"]) * current_price
            total_cost += float(pos["shares"]) * float(pos["buy_price"])
    except Exception:
        pass

gain = total_value - total_cost
gain_pct = (gain / total_cost * 100) if total_cost else 0
m4.metric("Portfolio Value", f"${total_value:,.2f}", f"{gain_pct:+.1f}%")

st.divider()

# --- Watchlist Table ---
st.subheader("Watchlist")

def get_price_row(ticker, tags):
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        if hist.empty:
            raise ValueError("No data")
        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2] if len(hist) >= 2 else price
        day_high = hist["High"].iloc[-1]
        day_low = hist["Low"].iloc[-1]
        high_52w = hist["High"].max()
        low_52w = hist["Low"].min()
        change = price - prev
        change_pct = (change / prev) * 100
        return {
            "Ticker": ticker,
            "Price": f"${price:.2f}",
            "Change": f"${change:+.2f} ({change_pct:+.1f}%)",
            "Day High": f"${day_high:.2f}",
            "Day Low": f"${day_low:.2f}",
            "52W High": f"${high_52w:.2f}",
            "52W Low": f"${low_52w:.2f}",
            "Tags": tags or "",
        }
    except Exception:
        return {
            "Ticker": ticker,
            "Price": "N/A", "Change": "-",
            "Day High": "-", "Day Low": "-",
            "52W High": "-", "52W Low": "-",
            "Tags": tags or "",
        }

rows = get_stocks_with_tags()
if rows:
    table = [get_price_row(r["ticker"], r["tags"]) for r in rows]
    st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)
else:
    st.info("No stocks on watchlist yet.")
