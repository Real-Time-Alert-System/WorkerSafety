import datetime
import logging
import sqlite3

from flask import current_app, g

logger = logging.getLogger(__name__)


def get_db():
    if "db" not in g:
        try:
            db_path = current_app.config["DATABASE_URL"].replace("sqlite:///", "")
            g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            g.db.row_factory = sqlite3.Row
            logger.info(f"Database connection established to {db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise e
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
        logger.info("Database connection closed.")


def init_db():
    db = get_db()
    try:
        with current_app.open_resource("../schema.sql") as f:
            # Check if script content exists before executing
            script = f.read().decode("utf8")
            if script:
                db.executescript(script)
                logger.info("Database schema initialized/updated.")
            else:
                logger.warning("schema.sql is empty or could not be read.")
    except FileNotFoundError:
        logger.warning("schema.sql not found. Creating tables directly.")
        create_tables_directly(db)
    except sqlite3.Error as e:
        logger.error(f"Error initializing database schema: {e}")


def create_tables_directly(db):
    """Creates tables if schema.sql is not found."""
    cursor = db.cursor()
    try:
        cursor.execute(
            """
         CREATE TABLE IF NOT EXISTS violations (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
             equipment_type TEXT NOT NULL,
             image_path TEXT,
             location TEXT,
             area_type TEXT,
             severity TEXT,
             status TEXT DEFAULT 'unresolved' NOT NULL
         )
         """
        )
        db.commit()
        logger.info("Created 'violations' table directly.")
    except sqlite3.Error as e:
        logger.error(f"Error creating tables directly: {e}")
        db.rollback()


def add_violation(
    timestamp: datetime.datetime,
    equipment_type: str,
    image_path: str,
    location: str,
    area_type: str,
    severity: str,
):
    db = get_db()
    try:
        db.execute(
            """INSERT INTO violations (timestamp, equipment_type, image_path, location, area_type, severity)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (timestamp, equipment_type, image_path, location, area_type, severity),
        )
        db.commit()
        logger.info(f"Added violation: {equipment_type} at {location}")
    except sqlite3.Error as e:
        logger.error(f"Error adding violation to database: {e}")
        db.rollback()


def get_all_violations(limit=100):
    db = get_db()
    try:
        cursor = db.execute(
            "SELECT * FROM violations ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        violations = cursor.fetchall()
        return violations
    except sqlite3.Error as e:
        logger.error(f"Error fetching violations: {e}")
        return []


def get_violation_by_id(violation_id):
    db = get_db()
    try:
        cursor = db.execute("SELECT * FROM violations WHERE id = ?", (violation_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Error fetching violation by ID {violation_id}: {e}")
        return None


def update_violation_status(violation_id, status):
    db = get_db()
    allowed_statuses = ["resolved", "unresolved", "investigating"]
    if status not in allowed_statuses:
        logger.warning(f"Invalid status '{status}' provided for violation update.")
        return False

    try:
        cursor = db.execute(
            "UPDATE violations SET status = ? WHERE id = ?", (status, violation_id)
        )
        db.commit()
        if cursor.rowcount == 0:
            logger.warning(
                f"Attempted to update status for non-existent violation ID: {violation_id}"
            )
            return False
        logger.info(f"Updated status for violation {violation_id} to {status}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error updating violation status for ID {violation_id}: {e}")
        db.rollback()
        return False


def get_violation_stats():
    db = get_db()
    stats = {}
    try:
        # By Equipment Type
        cursor = db.execute(
            """
            SELECT equipment_type, COUNT(*) as count
            FROM violations
            GROUP BY equipment_type ORDER BY count DESC
        """
        )
        stats["by_equipment"] = [dict(row) for row in cursor.fetchall()]

        # By Severity
        cursor = db.execute(
            """
            SELECT severity, COUNT(*) as count FROM violations
            GROUP BY severity ORDER BY CASE severity WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END
        """
        )
        stats["by_severity"] = [dict(row) for row in cursor.fetchall()]

        # By Location
        cursor = db.execute(
            """
            SELECT location, COUNT(*) as count FROM violations GROUP BY location ORDER BY count DESC
        """
        )
        stats["by_location"] = [dict(row) for row in cursor.fetchall()]

        # By Status
        cursor = db.execute(
            """
            SELECT status, COUNT(*) as count FROM violations GROUP BY status ORDER BY count DESC
        """
        )
        stats["by_status"] = [dict(row) for row in cursor.fetchall()]

        # Daily Trend (Last 30 days)
        cursor = db.execute(
            """
            SELECT DATE(timestamp) as day, COUNT(*) as count
            FROM violations
            WHERE timestamp >= DATE('now', '-30 days')
            GROUP BY day ORDER BY day ASC
        """
        )
        stats["daily_trend"] = [dict(row) for row in cursor.fetchall()]

        return stats

    except sqlite3.Error as e:
        logger.error(f"Error fetching violation stats: {e}")
        return {
            "by_equipment": [],
            "by_severity": [],
            "by_location": [],
            "by_status": [],
            "daily_trend": [],
            "error": str(e),
        }


def init_app(app):
    app.teardown_appcontext(close_db)
    # No need to call init_db() here, let's call it explicitly in run.py or via a CLI command
