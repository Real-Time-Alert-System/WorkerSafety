import datetime
import os

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import database as db


class Violation:
    def __init__(
        self,
        id,
        timestamp,
        equipment_type,
        image_path,
        location,
        area_type,
        severity,
        status,
    ):
        self.id = id
        self.timestamp = timestamp
        self.equipment_type = equipment_type
        # Store relative path for web serving
        self.image_path = (
            image_path.replace(
                os.path.abspath(current_app.config["VIOLATION_FOLDER"]), ""
            ).lstrip("/")
            if image_path
            else None
        )
        self.location = location
        self.area_type = area_type
        self.severity = severity
        self.status = status

    def __repr__(self):
        return f"<Violation {self.id} - {self.equipment_type} at {self.timestamp}>"

    @property
    def formatted_timestamp(self):
        ts = self.timestamp
        if isinstance(ts, str):
            try:
                ts = datetime.datetime.fromisoformat(ts.replace(" ", "T"))
            except ValueError:
                return "Invalid Date"
        if isinstance(ts, datetime.datetime):
            return ts.strftime("%Y-%m-%d %H:%M:%S")
        return str(ts)


class User(UserMixin):
    def __init__(self, id, username, email, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

    @staticmethod
    def get_by_id(user_id):
        conn = db.get_db()
        user_row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if user_row:
            return User(
                id=user_row["id"],
                username=user_row["username"],
                email=user_row["email"],
                password_hash=user_row["password_hash"],
                is_admin=bool(user_row["is_admin"]),
            )
        return None

    @staticmethod
    def get_by_username(username):
        conn = db.get_db()
        user_row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user_row:
            return User(
                id=user_row["id"],
                username=user_row["username"],
                email=user_row["email"],
                password_hash=user_row["password_hash"],
                is_admin=bool(user_row["is_admin"]),
            )
        return None

    @staticmethod
    def get_by_email(email):
        conn = db.get_db()
        user_row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        if user_row:
            return User(
                id=user_row["id"],
                username=user_row["username"],
                email=user_row["email"],
                password_hash=user_row["password_hash"],
                is_admin=bool(user_row["is_admin"]),
            )
        return None

    @staticmethod
    def create(username, email, password, is_admin=False):
        conn = db.get_db()
        user = User(
            id=None,
            username=username,
            email=email,
            password_hash=None,
            is_admin=is_admin,
        )
        user.set_password(password)
        try:
            cursor = conn.execute(
                "INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
                (
                    user.username,
                    user.email,
                    user.password_hash,
                    1 if user.is_admin else 0,
                ),
            )
            conn.commit()
            user.id = cursor.lastrowid
            current_app.logger.info(
                f"User '{username}' created successfully with ID: {user.id}."
            )
            return user
        except db.sqlite3.IntegrityError:
            current_app.logger.error(
                f"Error: Username '{username}' or email '{email}' already exists."
            )
            conn.rollback()
            return None
        except Exception as e:
            current_app.logger.error(f"Error creating user '{username}': {e}")
            conn.rollback()
            return None
