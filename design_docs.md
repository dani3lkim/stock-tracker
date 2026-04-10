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
Shows 4 live metrics: total watchlist stocks, total portfolio positions, total tags, and total portfolio value with gain/loss percentage. Displays a table of all watchlist stocks with their assigned tags.

**Watchlist (pages/1_Watchlist.py)**
- Form to add a new ticker to the watchlist
- Search/filter bar to narrow stocks by ticker or tag name
- Table showing live price, day high/low, 52-week high/low, and tags for each stock
- Tag assignment section: select a stock, pick tags from a multiselect (pulled from tags table), save
- Price chart with selectable time period (1mo to 5y)
- Delete with confirmation step

**Portfolio (pages/2_Portfolio.py)**
- Expandable form to add a new position (ticker, shares, buy price)
- Search bar to filter positions by ticker
- Table showing each position's current price, total value, and gain/loss
- Summary metrics: total portfolio value, cost basis, and overall gain/loss
- Edit form pre-filled with current shares and buy price
- Delete with confirmation step

**Tags (pages/3_Tags.py)**
- Form to add a new tag
- Table showing all existing tags
- Selectbox to choose a tag to rename, with an edit form
- Selectbox to choose a tag to delete, with a confirmation step

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
