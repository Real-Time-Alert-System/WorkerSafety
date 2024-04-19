import logging
import os
import time
from datetime import datetime, timedelta

import requests
from flask import current_app

logger = logging.getLogger(__name__)

# Use a simple in-memory cache for cooldowns
last_notification_times = (
    {}
)  # Key: (location, area_type, equipment_type), Value: timestamp


def send_telegram_notification(message: str, image_path: str = None):
    """Sends a notification message via Telegram, optionally with an image."""
    token = current_app.config.get("TELEGRAM_BOT_TOKEN")
    chat_id = current_app.config.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.warning(
            "Telegram token or chat_id not configured. Skipping notification."
        )
        return False

    api_url = f"https://api.telegram.org/bot{token}/"

    try:
        if image_path:
            # Send photo
            files = {"photo": open(image_path, "rb")}
            payload = {"chat_id": chat_id, "caption": message, "parse_mode": "Markdown"}
            response = requests.post(
                f"{api_url}sendPhoto", data=payload, files=files, timeout=20
            )
        else:
            # Send text message
            payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
            response = requests.post(f"{api_url}sendMessage", data=payload, timeout=10)

        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        if response.json().get("ok"):
            logger.info(
                f"Telegram notification sent successfully to chat_id {chat_id}."
            )
            return True
        else:
            logger.error(f"Telegram API error: {response.json().get('description')}")
            return False

    except FileNotFoundError:
        logger.error(
            f"Notification image file not found: {image_path}. Sending text only."
        )
        # Retry sending as text message
        payload = {
            "chat_id": chat_id,
            "text": message + "\n\n(Error: Image not found)",
            "parse_mode": "Markdown",
        }
        try:
            response = requests.post(f"{api_url}sendMessage", data=payload, timeout=10)
            response.raise_for_status()
            if response.json().get("ok"):
                logger.info(f"Telegram text notification sent (image error fallback).")
                return True
            else:
                logger.error(
                    f"Telegram API error (fallback): {response.json().get('description')}"
                )
                return False
        except requests.exceptions.RequestException as e_fallback:
            logger.error(
                f"Error sending Telegram text notification (fallback): {e_fallback}"
            )
            return False
    except requests.exceptions.Timeout:
        logger.error("Telegram API request timed out.")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Telegram notification: {e}")
        # Log detailed error if available
        if hasattr(e, "response") and e.response is not None:
            try:
                logger.error(f"Telegram API response content: {e.response.text}")
            except Exception:  # Handle cases where response text isn't readable
                logger.error("Could not read Telegram API error response content.")
        return False
    except Exception as e:  # Catch any other unexpected errors
        logger.exception(f"Unexpected error during Telegram notification: {e}")
        return False


def notify_violation(
    violation_type: str, location: str, area_type: str, severity: str, image_path: str
):
    """Formats and sends a violation notification, respecting cooldown."""
    cooldown_period = timedelta(
        seconds=current_app.config.get("NOTIFICATION_COOLDOWN", 60)
    )
    now = datetime.now()

    # Cooldown key: Tuple of identifying factors
    cooldown_key = (location, area_type, violation_type)
    last_sent = last_notification_times.get(cooldown_key)

    if last_sent and (now - last_sent) < cooldown_period:
        logger.debug(f"Notification cooldown active for {cooldown_key}. Skipping.")
        return False

    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    severity_emoji = {"high": "🚨", "medium": "⚠️", "low": "ℹ️"}
    emoji = severity_emoji.get(severity.lower(), "⚠️")

    # Format message using Markdown for better readability in Telegram
    message = f"""
{emoji} *PPE Violation Detected* {emoji}

A *{severity.upper()}* severity violation was detected.

*Details:*
- *Violation Type:* {violation_type}
- *Location:* {location}
- *Area Type:* {area_type}
- *Time:* {timestamp_str}

Please investigate and ensure compliance.
"""
    # Use the absolute path for sending
    full_image_path = os.path.join(
        current_app.config["VIOLATION_IMAGE_FOLDER"], os.path.basename(image_path)
    )

    if send_telegram_notification(message, full_image_path):
        last_notification_times[cooldown_key] = now  # Update last sent time on success
        return True
    return False
