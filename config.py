"""
Configuration for the price tracker.
Targets a public sandbox e-commerce site built for scraping practice.
"""
import os

CATEGORY_URLS = [
    "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
    "https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

DB_PATH = "price_tracker.db"

REQUEST_TIMEOUT = 10        # seconds
REQUEST_DELAY = 1.5         # polite delay between pages
RUN_INTERVAL_MINUTES = 60

# --- NEW: reliability ---
MAX_RETRIES = 3             # attempts per page
RETRY_BACKOFF = 2           # wait 2s, 4s, 8s ... between attempts

# --- NEW: alert rules ---
MIN_DROP_PERCENT = 1.0      # ignore drops smaller than 1%

# --- NEW: email alerts (off unless you set these environment variables) ---
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")   # Gmail app password
EMAIL_TO = os.getenv("EMAIL_TO", "")
