"""
Sends price-drop notifications. Always logs; also emails if enabled in config.
Notification failures never crash the tracker.
"""
import logging
import smtplib
from email.message import EmailMessage

from config import (EMAIL_ENABLED, SMTP_HOST, SMTP_PORT,
                    EMAIL_USER, EMAIL_PASSWORD, EMAIL_TO)

logger = logging.getLogger("price_tracker.notifier")


def send_price_drop(name: str, old_price: float, new_price: float, url: str):
    percent = (old_price - new_price) / old_price * 100
    message = (f"{name}\nOld price: ${old_price:.2f}\nNew price: ${new_price:.2f}\n"
               f"Drop: {percent:.1f}%\n{url}")
    logger.info("ALERT -> %s", message.replace("\n", " | "))

    if not EMAIL_ENABLED:
        return
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Price drop: {name} (-{percent:.1f}%)"
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_TO
        msg.set_content(message)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        logger.info("Email alert sent to %s", EMAIL_TO)
    except Exception as exc:
        logger.error("Email alert failed: %s", exc)
