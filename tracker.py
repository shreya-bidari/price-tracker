"""
Comparison engine: compares each scraped price with the last stored one,
raises an alert on a meaningful drop, and stores the price only if it changed.
"""
import logging

from config import MIN_DROP_PERCENT
from database import insert_price_if_changed, get_last_price, log_alert
from notifier import send_price_drop

logger = logging.getLogger("price_tracker.tracker")


def process_product(product: dict) -> bool:
    """product: {"name", "url", "price"}. Returns True if an alert was raised."""
    last = get_last_price(product["url"])
    dropped = False

    if last is None:
        logger.info("%s: $%.2f (first time seen)", product["name"], product["price"])
    elif product["price"] < last["price"]:
        drop_percent = (last["price"] - product["price"]) / last["price"] * 100
        if drop_percent >= MIN_DROP_PERCENT:
            log_alert(product["name"], last["price"], product["price"])
            send_price_drop(product["name"], last["price"], product["price"], product["url"])
            dropped = True
        else:
            logger.info("%s dropped only %.2f%%, below threshold", product["name"], drop_percent)
    elif product["price"] > last["price"]:
        logger.info("%s price increased: $%.2f -> $%.2f",
                    product["name"], last["price"], product["price"])

    insert_price_if_changed(product["name"], product["url"], product["price"])
    return dropped


def process_products(products: list) -> int:
    """Run process_product for a batch. Returns number of alerts raised."""
    return sum(1 for p in products if process_product(p))
