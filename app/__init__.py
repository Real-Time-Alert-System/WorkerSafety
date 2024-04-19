import datetime
import logging
import os

from flask import Flask, abort, send_from_directory
from flask_login import LoginManager

from . import database
from .auth import requires_auth
from .config import Config
from .models import User
from .routes import main_bp
from .services.detection_service import DetectionService

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)

detection_service = None


def create_app(config_class=Config):
    global detection_service

    app = Flask(__name__)
    app.config.from_object(config_class)

    config_class.init_app(app)
    database.init_app(app)
    login_manager.init_app(app)

    if detection_service is None:
        with app.app_context():
            detection_service = DetectionService()
            app.detection_service = detection_service
    else:
        app.detection_service = detection_service

    from .routes import main_bp

    app.register_blueprint(main_bp)

    from .auth_routes import auth_bp

    app.register_blueprint(auth_bp)

    @app.context_processor
    def inject_now():
        return {"now": datetime.datetime.utcnow()}

    # Route to serve violation images
    @app.route("/violations/images/<path:filename>")
    @requires_auth
    def serve_violation_image(filename):
        image_dir = app.config["VIOLATION_IMAGE_FOLDER"]
        safe_path = os.path.join(image_dir, filename)
        if not os.path.abspath(safe_path).startswith(os.path.abspath(image_dir)):
            app.logger.warning(f"Attempted directory traversal: {filename}")
            abort(404)

        if not os.path.exists(safe_path):
            app.logger.warning(f"Violation image not found: {safe_path}")
            abort(404)
        return send_from_directory(image_dir, filename)

    app.logger.info("Flask App Created")
    app.logger.info(f"Running in {app.config['FLASK_ENV']} mode")
    app.logger.info(f"Violation image folder: {app.config['VIOLATION_IMAGE_FOLDER']}")
    app.logger.info(f"Database URL: {app.config['DATABASE_URL']}")

    return app
