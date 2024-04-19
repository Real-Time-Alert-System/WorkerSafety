import logging

from app import Config, create_app, database

app = create_app()
logger = logging.getLogger(__name__)

with app.app_context():
    logger.info("Initializing Database Schema...")
    try:
        database.init_db()
        logger.info("Database initialization complete.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        exit("Database initialization failed. Exiting.")


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000
    debug = app.config["DEBUG"]
    logger.info(f"Starting Flask server on {host}:{port} (Debug: {debug})")
    app.run(host=host, port=port, debug=debug)
