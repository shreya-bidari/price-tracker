"""
Entry point. Runs one scrape immediately, then repeats on a schedule
using the `schedule` library so the tool keeps monitoring prices
without manual intervention.

Usage:
    python main.py            # run continuously on a schedule
    python main.py --once     # run a single scrape and exit
"""

import sys
import time
import logging

import schedule

from config import CATEGORY_URLS, RUN_INTERVAL_MINUTES
from database import init_db
from scraper import scrape_all
from tracker import process_products

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("price_tracker.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("price_tracker.main")


def run_job():
    logger.info("Starting scrape run...")
    products = scrape_all(CATEGORY_URLS)
    if not products:
        logger.warning("No products scraped this run.")
        return
    drops = process_products(products)
    logger.info(
        "Run complete: %d products checked, %d price drop(s) detected.",
        len(products), drops,
    )


def main():
    init_db()

    if "--once" in sys.argv:
        run_job()
        return

    run_job()  # run immediately on startup, then follow the schedule
    schedule.every(RUN_INTERVAL_MINUTES).minutes.do(run_job)

    logger.info("Scheduler started: running every %d minute(s). Ctrl+C to stop.",
                RUN_INTERVAL_MINUTES)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopped by user.")


if __name__ == "__main__":
    main()
