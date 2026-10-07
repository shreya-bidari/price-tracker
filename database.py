"""
SQLite storage layer.

Tables:
  - prices: a new row is stored only when a product's price CHANGES
            (this is the de-duplication), so history stays clean.
  - alerts: logged whenever a price drop is detected.
"""
import sqlite3
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist. Safe to call every run."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                product_url TEXT NOT NULL,
                price REAL NOT NULL,
                scraped_at TEXT NOT NULL DEFAULT (datetime('now'))
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                old_price REAL NOT NULL,
                new_price REAL NOT NULL,
                drop_amount REAL NOT NULL,
                detected_at TEXT NOT NULL DEFAULT (datetime('now'))
            )""")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_prices_product_time "
            "ON prices (product_url, scraped_at)"
        )


def get_last_price(product_url: str):
    """Most recent stored price for a product, or None if never seen."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT price, scraped_at FROM prices "
            "WHERE product_url = ? ORDER BY id DESC LIMIT 1",
            (product_url,),
        ).fetchone()
        return dict(row) if row else None


def insert_price_if_changed(product_name: str, product_url: str, price: float) -> bool:
    """
    De-duplication: insert only if this is a new product or the price
    differs from the last stored one. Returns True if a row was inserted.
    """
    last = get_last_price(product_url)
    if last is not None and last["price"] == price:
        return False
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO prices (product_name, product_url, price) VALUES (?, ?, ?)",
            (product_name, product_url, price),
        )
    return True


def log_alert(product_name: str, old_price: float, new_price: float):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO alerts (product_name, old_price, new_price, drop_amount) "
            "VALUES (?, ?, ?, ?)",
            (product_name, old_price, new_price, old_price - new_price),
        )


def get_price_history(product_url: str):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT price, scraped_at FROM prices "
            "WHERE product_url = ? ORDER BY id ASC",
            (product_url,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_recent_alerts(limit: int = 50):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_products():
    """Distinct (name, url) pairs, used by the dashboard dropdown."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT product_name, product_url FROM prices ORDER BY product_name"
        ).fetchall()
        return [dict(r) for r in rows]
