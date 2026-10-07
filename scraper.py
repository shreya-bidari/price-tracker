"""
Scraping logic: fetches category pages and extracts (name, url, price)
for each product using requests + BeautifulSoup.
"""

import re
import time
import logging

import requests
from bs4 import BeautifulSoup

from config import HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES, RETRY_BACKOFF

logger = logging.getLogger("price_tracker.scraper")


def fetch_page(url: str) -> str:
    """GET a page, retrying with exponential backoff on network/HTTP errors."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES:
                raise
            wait = RETRY_BACKOFF ** attempt
            logger.warning("Attempt %d/%d failed for %s (%s). Retrying in %ds",
                           attempt, MAX_RETRIES, url, exc, wait)
            time.sleep(wait)


def parse_products(html: str, page_url: str):
    """
    Parse a category page and return a list of dicts:
    {"name": str, "url": str, "price": float}

    Selectors match webscraper.io's sandbox markup:
        <div class="thumbnail">
            <a class="title" href="..." title="Full Product Name">...</a>
            <h4 class="price pull-right">$1029.00</h4>
        </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select(".thumbnail"):
        title_tag = card.select_one(".title")
        price_tag = card.select_one(".price")

        if not title_tag or not price_tag:
            continue  # skip malformed cards instead of crashing the run

        name = title_tag.get("title") or title_tag.get_text(strip=True)
        href = title_tag.get("href", "")
        product_url = requests.compat.urljoin(page_url, href)

        price = parse_price(price_tag.get_text())
        if price is None:
            logger.warning("Could not parse price for %s, skipping", name)
            continue

        products.append({"name": name, "url": product_url, "price": price})

    return products


def parse_price(raw_text: str):
    """Turn '$1,029.00' into 1029.00. Returns None if no number is found."""
    match = re.search(r"[\d,]+\.?\d*", raw_text)
    if not match:
        return None
    return float(match.group().replace(",", ""))


def scrape_all(category_urls):
    """Fetch every configured category page and return a combined product list."""
    all_products = []
    for url in category_urls:
        try:
            html = fetch_page(url)
            products = parse_products(html, url)
            logger.info("Scraped %d products from %s", len(products), url)
            all_products.extend(products)
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
        time.sleep(REQUEST_DELAY)  # be polite between requests
    return all_products
