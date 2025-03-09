# notification.py
import requests
import os
import logging
import time
import json
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Telegram settings
BOT_TOKEN = "7800571114:AAFL_RZctHfX0PcYKL3qY2T2uE-YurcFGug"
CHAT_ID = "1613628414"

# Cooldown settings
COOLDOWN_MINUTES = 1
COOLDOWN_FILE = "notification_cooldown.json"

def check_cooldown():
    """
    Check if we're in a cooldown period for notifications
    
    Returns:
        tuple: (bool, remaining_seconds) - True if cooldown is active, and remaining seconds
    """
    try:
        if os.path.exists(COOLDOWN_FILE):
            with open(COOLDOWN_FILE, 'r') as f:
                cooldown_data = json.load(f)
                
            last_notification = datetime.fromisoformat(cooldown_data['last_notification'])
            cooldown_until = last_notification + timedelta(minutes=COOLDOWN_MINUTES)
            
            now = datetime.now()
            
            if now < cooldown_until:
                remaining_seconds = (cooldown_until - now).total_seconds()
                return True, int(remaining_seconds)
    except Exception as e:
        logger.error(f"Error checking cooldown: {str(e)}")
        
    return False, 0

def set_cooldown():
    """Set the cooldown timestamp for notifications"""
    try:
        cooldown_data = {
            'last_notification': datetime.now().isoformat()
        }
        
        with open(COOLDOWN_FILE, 'w') as f:
            json.dump(cooldown_data, f)
            
        logger.info(f"Notification cooldown set for {COOLDOWN_MINUTES} minute(s)")
    except Exception as e:
        logger.error(f"Error setting cooldown: {str(e)}")

def send_notification(message, image_path=None):
    """
    Send a notification about the PPE violation via Telegram
    with cooldown functionality
    
    Args:
        message: The notification message text
        image_path: Path to the image to attach (if any)
    
    Returns:
        bool: Success status
    """
    # Check cooldown first
    in_cooldown, remaining_seconds = check_cooldown()
    if in_cooldown:
        logger.info(f"Notification in cooldown period. {remaining_seconds} seconds remaining.")
        return False
    
    # Send text message
    text_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    text_payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    text_success = False
    image_success = False
    
    try:
        response = requests.post(text_url, data=text_payload)
        if response.status_code == 200:
            logger.info("Telegram text notification sent successfully")
            text_success = True
        else:
            logger.error(f"Text message failed: {response.text}")
    except Exception as e:
        logger.error(f"Text notification error: {str(e)}")
    
    # Send image if provided
    if image_path and os.path.exists(image_path):
        photo_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        try:
            with open(image_path, 'rb') as photo_file:
                files = {'photo': photo_file}
                data = {'chat_id': CHAT_ID}
                response = requests.post(photo_url, files=files, data=data)
                if response.status_code == 200:
                    logger.info("Telegram image notification sent successfully")
                    image_success = True
                else:
                    logger.error(f"Image send failed: {response.text}")
        except Exception as e:
            logger.error(f"Image notification error: {str(e)}")
    
    # If notification was successful, set the cooldown
    if text_success and (image_success if image_path else True):
        set_cooldown()
        
    return text_success and (image_success if image_path else True)
