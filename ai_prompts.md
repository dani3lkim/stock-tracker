# AI Prompts & Process Log

This document records the prompts given to Claude (claude-sonnet-4-6) during the development of the Stock Tracker app, along with notes on what worked and what needed fixing.

---

## Prompt 1 — Initial Assessment

**Prompt:**
> does this meet the project requirements?

**What happened:**
Claude reviewed the existing stock tracker app (which only had a watchlist and portfolio in a single file) and identified the following gaps: only 2 tables (needed 3+ with many-to-many), no update functionality, no delete confirmation, no form validation, no search/filter, no dashboard, and the database credentials were hardcoded in db.py instead of using st.secrets.

**Result:** Good diagnostic. All gaps were accurately identified.

---

## Prompt 2 — Full App Rebuild

**Prompt:**
> yes (fix all the gaps)

**Context provided to Claude:**
- Existing app.py and db.py code
- Full project requirements from the assignment

**What Claude built:**
- Updated `db.py` to use `st.secrets["DB_URL"]` instead of hardcoded credentials
- Added `tags` table and `stock_tags` junction table (many-to-many between stocks and tags)
- Restructured into multi-page app:
  - `app.py` — dashboard with `st.metric()` counts and portfolio value
  - `pages/1_Watchlist.py` — watchlist with search, tag assignment, price chart, delete confirmation
  - `pages/2_Portfolio.py` — portfolio with search, edit form, delete confirmation, validation
  - `pages/3_Tags.py` — tag CRUD with validation
- Created `.streamlit/secrets.toml` for local development
- Created `.gitignore` to prevent secrets from being committed

**What worked on first try:** Everything except the form validation placement (see Prompt 3).

---

## Prompt 3 — Fix Form Error

**Prompt:**
> Missing Submit Button — This form has no submit button, which means that user interactions will never be sent to your Streamlit app.

**What happened:**
The error was on the Tags page. The root cause was that `st.error()` and `st.success()` calls were placed inside `st.form()` blocks. Streamlit requires that message displays be outside the form context.

**Fix:**
Claude moved all `if submitted:` validation and success/error logic to outside the `with st.form():` block across all three pages. This is the correct Streamlit pattern — the form only contains input widgets and the submit button.

**What had to be changed manually:** Nothing — the fix worked on the first try after diagnosis.

---

## Prompt 4 — Deployment

**Prompts:**
> step by step (deploy to Streamlit Community Cloud)

**Process:**
- Initialized git repo in the stock-tracker folder
- Created public GitHub repository at github.com/dani3lkim/stock-tracker
- Pushed code with `git push`
- Deployed on share.streamlit.io by connecting the GitHub repo and pasting the DB_URL into the Secrets field

**Issue encountered:** The secrets weren't saved on first deployment attempt, causing a `StreamlitSecretNotFoundError`. Fixed by going back into app Settings → Secrets and re-saving the DB_URL.

---

## Prompt 5 — Design Documents & README

**Prompt:**
> yes (write the design documents and README)

**What Claude generated:**
- System description paragraph
- Entity list with all 4 tables, columns, types, and constraints
- Relationships description
- Page-by-page plan for all 4 pages
- Validation rules for all forms
- dbdiagram.io ERD code (diagram was drawn manually by student)
- Full README.md with table descriptions, setup instructions, and live URL

**What worked:** All documents generated accurately on first try, matching the actual app schema.

---

## Summary: What the LLM Got Right vs. What Needed Fixing

| Area | Result |
|---|---|
| Database schema design | Correct on first try |
| Multi-page app structure | Correct on first try |
| Parameterized SQL | Correct on first try |
| Secrets management | Correct on first try |
| Form validation logic | Had to fix placement (inside vs. outside `st.form`) |
| Deployment steps | Required one manual fix (re-entering secrets) |
| Design documents | Correct on first try |
| README | Correct on first try, URL updated after deployment |
