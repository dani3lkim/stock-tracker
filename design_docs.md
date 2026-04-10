# Systems Analysis & Design Documents

## 1. System Description

This system is a personal stock tracking application designed for individual investors who want to monitor their watchlist and manage their portfolio in one place. Users can add stock tickers to a watchlist and view live price data including daily highs, lows, and 52-week ranges. Stocks on the watchlist can be categorized with custom tags (such as "Tech," "Dividend," or "Speculative"), and because a stock can have many tags and a tag can apply to many stocks, this relationship is managed through a junction table. The portfolio section allows users to log positions with a purchase price and share count, then see their current value and gain/loss calculated from live market data. The dashboard provides a summary of total watchlist stocks, portfolio positions, tags, and overall portfolio value at a glance.

---

## 2. Entity List with Attributes

**stocks** — id (SERIAL, PRIMARY KEY), ticker (VARCHAR 10, UNIQUE, NOT NULL), added_at (TIMESTAMP, DEFAULT NOW)

**portfolio** — id (SERIAL, PRIMARY KEY), ticker (VARCHAR 10, NOT NULL), shares (NUMERIC, NOT NULL), buy_price (NUMERIC, NOT NULL), added_at (TIMESTAMP, DEFAULT NOW)

**tags** — id (SERIAL, PRIMARY KEY), name (VARCHAR 50, UNIQUE, NOT NULL)

**stock_tags** — stock_id (INTEGER, FK → stocks.id, ON DELETE CASCADE), tag_id (INTEGER, FK → tags.id, ON DELETE CASCADE), PRIMARY KEY (stock_id, tag_id)

---

## 3. Relationships

- One stock can have many tags; one tag can apply to many stocks → **many-to-many**, implemented via the `stock_tags` junction table
- `stock_tags.stock_id` references `stocks.id` — if a stock is deleted, its tag assignments are deleted automatically (CASCADE)
- `stock_tags.tag_id` references `tags.id` — if a tag is deleted, it is removed from all stocks automatically (CASCADE)
- `portfolio` is independent — positions are tracked by ticker string, not linked to the `stocks` table, so a user can hold a position without it being on their watchlist

---

## 4. Page-by-Page Plan

**Dashboard (app.py)**
Shows 4 live metrics at the top: total watchlist stocks, total portfolio positions, total tags, and total portfolio value with overall gain/loss percentage. Below the metrics, displays a full live price table of all watchlist stocks showing ticker, current price, day change ($ and %), day high, day low, 52-week high, 52-week low, and assigned tags.

**Watchlist (pages/1_Watchlist.py)**
- Form at the top to add a new ticker symbol to the watchlist
- Search/filter bar to narrow the list by ticker or tag name
- Live price table showing ticker, tags, current price, day high, day low, 52-week high, and 52-week low for each stock
- Tag assignment section: select a stock from a dropdown, pick tags from a multiselect (options pulled from the tags table), click Save Tags
- Price chart: select a ticker and a time period (1mo, 3mo, 6mo, 1y, 2y, 5y) to view a closing price line chart
- Remove section: select a ticker from a dropdown, click Remove, confirm before deletion

**Portfolio (pages/2_Portfolio.py)**
- Expandable "Add Position" section with a form for ticker, number of shares, and buy price per share
- Search bar to filter positions by ticker
- Table showing each position: ticker, shares, buy price, current price, total current value, and gain/loss ($ and %)
- Summary metrics below the table: total portfolio value, total cost basis, total gain/loss ($ and %)
- Edit Position section: select a position from a dropdown, edit shares and buy price in a pre-filled form, save changes
- Delete Position section: select a position, click Delete, confirm before deletion

**Tags (pages/3_Tags.py)**
- Form to add a new tag by name
- Table showing all existing tags
- Edit section: select a tag from a dropdown, enter a new name in a form, click Rename
- Delete section: select a tag from a dropdown, click Delete Tag, confirm before deletion (deleting a tag removes it from all stocks automatically)

---

## 5. Validation Rules

**Add Stock (Watchlist)**
- Ticker is required — cannot be blank
- Ticker must be 10 characters or fewer

**Add Position (Portfolio)**
- Ticker is required — cannot be blank
- Ticker must be 10 characters or fewer
- Shares must be a positive number (> 0)
- Buy price must be a positive number (> 0)

**Edit Position (Portfolio)**
- Shares must be a positive number (> 0)
- Buy price must be a positive number (> 0)

**Add Tag**
- Tag name is required — cannot be blank
- Tag name must be 50 characters or fewer

**Edit Tag**
- New tag name is required — cannot be blank
- New tag name must be 50 characters or fewer

---

## 6. ERD

See `erd.png` in this repository.
