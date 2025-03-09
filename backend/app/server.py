# app.py (main application file with Auth0 integration)
from flask import Flask, redirect, render_template, session, url_for, jsonify
from config import Config
import os
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from functools import wraps

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Auth decorator for route protection
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Secret key for session management
    app.secret_key = env.get("APP_SECRET_KEY")
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Set up Auth0
    oauth = OAuth(app)
    
    oauth.register(
        "auth0",
        client_id=env.get("AUTH0_CLIENT_ID"),
        client_secret=env.get("AUTH0_CLIENT_SECRET"),
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
    )
    
    # Main routes
    @app.route("/")
    def index():
        return render_template('index.html', session=session.get('user'))
    
    # Auth0 routes
    @app.route("/login")
    def login():
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("callback", _external=True)
        )
    
    @app.route("/callback", methods=["GET", "POST"])
    def callback():
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        return redirect("/dashboard")
    
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(
            "https://" + env.get("AUTH0_DOMAIN")
            + "/v2/logout?"
            + urlencode(
                {
                    "returnTo": url_for("index", _external=True),
                    "client_id": env.get("AUTH0_CLIENT_ID"),
                },
                quote_via=quote_plus,
            )
        )
    
    # Dashboard route
    @app.route("/dashboard")
    @requires_auth
    def dashboard():
        return render_template("dashboard.html", session=session.get('user'))
    
    # Register blueprints
    from routes.main import main_bp
    from routes.api import api_bp
    
    app.register_blueprint(main_bp, url_prefix='/main')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=env.get("PORT", 3000))
