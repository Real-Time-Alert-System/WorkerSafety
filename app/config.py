import json
import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(basedir, ".."))
load_dotenv(os.path.join(project_root, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    DEBUG = FLASK_ENV == "development"

    UPLOAD_FOLDER = os.path.join(
        project_root, os.environ.get("UPLOAD_FOLDER", "uploads")
    )
    VIOLATION_FOLDER = os.path.join(
        project_root, os.environ.get("VIOLATION_FOLDER", "violation_data")
    )
    VIOLATION_IMAGE_FOLDER = os.path.join(VIOLATION_FOLDER, "images")
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", f'sqlite:///{os.path.join(VIOLATION_FOLDER, "violations.db")}'
    )
    MODEL_PATH = os.path.join(
        project_root, os.environ.get("MODEL_PATH", "models/yolov8s_ppe_custom.pt")
    )

    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
    NOTIFICATION_COOLDOWN = int(os.environ.get("NOTIFICATION_COOLDOWN", 60))

    try:
        PPE_CLASS_MAPPING = json.loads(os.environ.get("PPE_CLASS_MAPPING", "{}"))
        PPE_CLASS_MAPPING = {int(k): v for k, v in PPE_CLASS_MAPPING.items()}
    except json.JSONDecodeError:
        print("Warning: Invalid PPE_CLASS_MAPPING in .env file. Using empty mapping.")
        PPE_CLASS_MAPPING = {}

    try:
        VIOLATION_CLASSES = json.loads(os.environ.get("VIOLATION_CLASSES", "[]"))
    except json.JSONDecodeError:
        print("Warning: Invalid VIOLATION_CLASSES in .env file. Using empty list.")
        VIOLATION_CLASSES = []

    try:
        AREA_REQUIREMENTS = json.loads(os.environ.get("AREA_REQUIREMENTS", "{}"))
    except json.JSONDecodeError:
        print("Warning: Invalid AREA_REQUIREMENTS in .env file. Using empty dict.")
        AREA_REQUIREMENTS = {}

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "mp4", "avi", "mov", "webm"}
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB limit

    @staticmethod
    def init_app(app):
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        os.makedirs(app.config["VIOLATION_FOLDER"], exist_ok=True)
        os.makedirs(app.config["VIOLATION_IMAGE_FOLDER"], exist_ok=True)

        if not os.path.exists(app.config["MODEL_PATH"]):
            app.logger.error(
                f"FATAL: YOLO model not found at {app.config['MODEL_PATH']}"
            )

        if not app.config["TELEGRAM_BOT_TOKEN"] or not app.config["TELEGRAM_CHAT_ID"]:
            app.logger.warning(
                "Telegram BOT_TOKEN or CHAT_ID not set. Notifications will be disabled."
            )

        if not app.config["PPE_CLASS_MAPPING"]:
            app.logger.warning(
                "PPE_CLASS_MAPPING is not configured. Detection might not work as expected."
            )
