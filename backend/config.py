# config.py
import os

class Config:
    # PPE detection app config
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Dashboard/notification config
    ALERT_FOLDER = os.path.abspath("alerts")
    HISTORY_FILE = os.path.join(ALERT_FOLDER, "violation_history.json")
    STATS_FILE = os.path.join(ALERT_FOLDER, "detection_stats.json")
    AUTH_TOKEN = "your_secure_token_here"  # Replace with a secure token
