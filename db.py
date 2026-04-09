import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor


def get_conn():
    return psycopg2.connect(st.secrets["DB_URL"], cursor_factory=RealDictCursor)


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(10) UNIQUE NOT NULL,
                    added_at TIMESTAMP DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS portfolio (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(10) NOT NULL,
                    shares NUMERIC NOT NULL,
                    buy_price NUMERIC NOT NULL,
                    added_at TIMESTAMP DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS tags (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL
                );
                CREATE TABLE IF NOT EXISTS stock_tags (
                    stock_id INTEGER REFERENCES stocks(id) ON DELETE CASCADE,
                    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                    PRIMARY KEY (stock_id, tag_id)
                );
            """)
        conn.commit()


# --- Watchlist ---

def get_tracked_stocks():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, ticker FROM stocks ORDER BY added_at DESC;")
            return cur.fetchall()


def add_stock(ticker):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO stocks (ticker) VALUES (%s) ON CONFLICT DO NOTHING RETURNING id;",
                (ticker.upper(),)
            )
            row = cur.fetchone()
        conn.commit()
        return row["id"] if row else None


def remove_stock(ticker):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM stocks WHERE ticker = %s;", (ticker.upper(),))
        conn.commit()


# --- Portfolio ---

def get_portfolio():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM portfolio ORDER BY added_at DESC;")
            return cur.fetchall()


def add_position(ticker, shares, buy_price):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO portfolio (ticker, shares, buy_price) VALUES (%s, %s, %s);",
                (ticker.upper(), shares, buy_price)
            )
        conn.commit()


def update_position(position_id, shares, buy_price):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE portfolio SET shares = %s, buy_price = %s WHERE id = %s;",
                (shares, buy_price, position_id)
            )
        conn.commit()


def remove_position(position_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM portfolio WHERE id = %s;", (position_id,))
        conn.commit()


# --- Tags ---

def get_tags():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM tags ORDER BY name;")
            return cur.fetchall()


def add_tag(name):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tags (name) VALUES (%s) ON CONFLICT DO NOTHING;",
                (name.strip(),)
            )
        conn.commit()


def remove_tag(tag_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tags WHERE id = %s;", (tag_id,))
        conn.commit()


def update_tag(tag_id, name):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE tags SET name = %s WHERE id = %s;", (name.strip(), tag_id))
        conn.commit()


# --- Stock Tags (junction) ---

def get_tags_for_stock(stock_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.id, t.name FROM tags t
                JOIN stock_tags st ON t.id = st.tag_id
                WHERE st.stock_id = %s ORDER BY t.name;
            """, (stock_id,))
            return cur.fetchall()


def set_stock_tags(stock_id, tag_ids):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM stock_tags WHERE stock_id = %s;", (stock_id,))
            for tag_id in tag_ids:
                cur.execute(
                    "INSERT INTO stock_tags (stock_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                    (stock_id, tag_id)
                )
        conn.commit()


def get_stocks_with_tags():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.id, s.ticker, STRING_AGG(t.name, ', ' ORDER BY t.name) AS tags
                FROM stocks s
                LEFT JOIN stock_tags st ON s.id = st.stock_id
                LEFT JOIN tags t ON st.tag_id = t.id
                GROUP BY s.id, s.ticker
                ORDER BY s.added_at DESC;
            """)
            return cur.fetchall()


# --- Dashboard counts ---

def get_counts():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS cnt FROM stocks;")
            stock_count = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) AS cnt FROM portfolio;")
            position_count = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) AS cnt FROM tags;")
            tag_count = cur.fetchone()["cnt"]
        return stock_count, position_count, tag_count
