# server.py (consolidated application)
import sys
import os
import cv2
import numpy as np
import datetime
import sqlite3
import json
import time
from flask import Flask, redirect, render_template, session, url_for, jsonify, request
from werkzeug.utils import secure_filename
from config import Config
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from functools import wraps
from urllib.parse import quote_plus, urlencode
from os import environ as env

# Add model directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, '..'))
model_dir = os.path.abspath(os.path.join(backend_dir, '..', 'model'))
sys.path.append(model_dir)

from model.ppe_detector import PPEDetector
from notification import send_notification

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Configure paths
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')
VIOLATION_FOLDER = os.path.join(current_dir, 'alerts')
DB_FOLDER = os.path.join(current_dir, 'db')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png'}

# Auth decorator
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
    app.config.update({
        'UPLOAD_FOLDER': UPLOAD_FOLDER,
        'VIOLATION_FOLDER': VIOLATION_FOLDER,
        'DB_FOLDER': DB_FOLDER,
        'DB_PATH': os.path.join(DB_FOLDER, 'violations.db'),
        'SECRET_KEY': env.get("APP_SECRET_KEY")
    })
    
    # Initialize components
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(VIOLATION_FOLDER, exist_ok=True)
    os.makedirs(DB_FOLDER, exist_ok=True)
    
    # Initialize PPE Detector
    app.ppe_detector = PPEDetector()
    
    # Initialize database
    with app.app_context():
        init_db(app)
    
    # Auth0 setup
    oauth = OAuth(app)
    oauth.register(
        "auth0",
        client_id=env.get("AUTH0_CLIENT_ID"),
        client_secret=env.get("AUTH0_CLIENT_SECRET"),
        client_kwargs={"scope": "openid profile email"},
        server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
    )

    # Routes
    @app.route("/")
    def index():
        return render_template('index.html', session=session.get('user'))

    @app.route("/login")
    def login():
        return oauth.auth0.authorize_redirect(redirect_uri=url_for("callback", _external=True))

    @app.route("/callback", methods=["GET", "POST"])
    def callback():
        token = oauth.auth0.authorize_access_token()
        session["user"] = token
        return redirect("/dashboard")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(f"https://{env.get('AUTH0_DOMAIN')}/v2/logout?" + urlencode({
            "returnTo": url_for("index", _external=True),
            "client_id": env.get("AUTH0_CLIENT_ID"),
        }, quote_via=quote_plus))

    @app.route("/dashboard")
    @requires_auth
    def dashboard():
        return render_template("dashboard.html", session=session.get('user'))

    @app.route("/upload", methods=["POST"])
    @requires_auth
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        location = request.form.get('location', 'Unknown')
        area_type = request.form.get('area_type', 'default')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            if filename.lower().endswith(('png', 'jpg', 'jpeg')):
                violations = process_image(app, filepath, location, area_type)
            else:
                violations = process_video(app, filepath, location, area_type)
            
            return jsonify({
                'violations': violations,
                'message': f'Found {len(violations)} violations'
            })
        
        return jsonify({'error': 'Invalid file'}), 400

    # Add other routes (statistics, violations, etc.) here

    return app

def init_db(app):
    conn = sqlite3.connect(app.config['DB_PATH'])
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            equipment_type TEXT,
            image_path TEXT,
            location TEXT,
            area_type TEXT,
            severity TEXT,
            status TEXT DEFAULT 'unresolved'
        )
    ''')
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(app, image_path, location, area_type):
    image = cv2.imread(image_path)
    if image is None:
        return []
    
    results = app.ppe_detector.detect(image, area_type)
    violations = results.get('violations', [])
    
    if violations:
        violation_path = results['violation_image']
        for violation in violations:
            save_violation(app, violation, violation_path, location, area_type)
        
        send_notification(
            create_notification_message(violations, location, area_type),
            violation_path
        )
    
    return violations

def process_video(app, video_path, location, area_type):
    cap = cv2.VideoCapture(video_path)
    violations = []
    last_notification = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        results = app.ppe_detector.detect(frame, area_type)
        if results['violations']:
            violations.extend(results['violations'])
            
            if time.time() - last_notification >= 60:
                send_notification(
                    create_notification_message(results['violations'], location, area_type),
                    results['violation_image']
                )
                last_notification = time.time()
    
    cap.release()
    return violations

def save_violation(app, violation, image_path, location, area_type):
    conn = sqlite3.connect(app.config['DB_PATH'])
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO violations (timestamp, equipment_type, image_path, location, area_type, severity)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        datetime.datetime.now(),
        violation['type'],
        image_path,
        location,
        area_type,
        determine_severity(violation['type'])
    ))
    conn.commit()
    conn.close()

def determine_severity(equipment_type):
    severity_map = {'helmet': 'high', 'safety_goggles': 'high', 'vest': 'medium', 'gloves': 'medium'}
    return severity_map.get(equipment_type, 'low')

def create_notification_message(violations, location, area_type):
    missing_items = ', '.join({v['type'] for v in violations})
    return f"PPE Violation in {area_type} area ({location}): Missing {missing_items}"

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=env.get("PORT", 3000), debug=True)
