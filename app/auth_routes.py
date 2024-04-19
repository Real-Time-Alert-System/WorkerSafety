from urllib.parse import urljoin, urlparse

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from .forms import LoginForm, RegistrationForm
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password. Please try again.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)
        flash(f"Welcome back, {user.username}!", "success")

        current_app.logger.info(
            f"Login successful for user '{user.username}'. Redirecting to main.index."
        )
        return redirect(url_for("main.index"))

    current_app.logger.info(
        f"Rendering login page. Method: {request.method}, Form errors: {form.errors}"
    )
    return render_template("auth/login.html", title="Sign In", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        if user:
            flash(
                "Congratulations, you are now a registered user! Please log in.",
                "success",
            )
            return redirect(url_for("auth.login"))
        else:
            flash(
                "Registration failed. Username or email might already be in use.",
                "danger",
            )
    return render_template("auth/register.html", title="Register", form=form)


@auth_bp.cli.command("create-admin")
def create_admin_command():
    """Creates a default admin user."""
    username = current_app.config.get("BASIC_AUTH_USERNAME", "admin")
    email = "admin@example.com"
    password = current_app.config.get("BASIC_AUTH_PASSWORD", "changeme")

    if User.get_by_username(username):
        print(f"Admin user '{username}' already exists.")
        return

    admin = User.create(
        username=username, email=email, password=password, is_admin=True
    )
    if admin:
        print(f"Admin user '{username}' created successfully.")
    else:
        print(f"Failed to create admin user '{username}'.")
