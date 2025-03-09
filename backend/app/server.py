# app.py (main application file with Auth0 integration)
from flask import Flask, redirect, render_template, session, url_for, jsonify, request
from config import Config
import os
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from functools import wraps
import cv2
import time
import datetime
from werkzeug.utils import secure_filename

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

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        client_kwargs={"scope": "openid profile email"},
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
            + urlencode({
                "returnTo": url_for("index", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            }, quote_via=quote_plus)
        )
    
    # Dashboard route
    @app.route("/dashboard")
    @requires_auth
    def dashboard():
        return render_template("dashboard.html", session=session.get('user'))
    
    # Upload route
    @app.route("/upload", methods=["POST"])
    @requires_auth
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        location = request.form.get('location', 'Unknown')
        area_type = request.form.get('area_type', 'default')
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process file based on type
            if filename.lower().endswith(('png', 'jpg', 'jpeg')):
                print(f"Processing image: {filepath}")
                result = process_image(app, filepath, location, area_type)
                file_type = 'image'
            else:
                print(f"Processing video: {filepath}")
                result = process_video(app, filepath, location, area_type)
                file_type = 'video'
            
            return jsonify({
                'file_type': file_type,
                'violations': result,
                'message': f'Found {len(result)} violations in {file_type}'
            })
        
        return jsonify({
            'error': 'Invalid file type. Allowed types: jpg, jpeg, png, mp4, avi, mov'
        }), 400

    # Register blueprints
    from routes.main import main_bp
    from routes.api import api_bp
    app.register_blueprint(main_bp, url_prefix='/main')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

# Video processing function
def process_video(app, video_path, location, area_type):
    """
    Process a video file for PPE violations with optimized frame processing.
    
    Args:
        app: Flask application.
        video_path: Path to the video file.
        location: Location name.
        area_type: Type of work area.
    
    Returns:
        List of violations found.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return []
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_step = max(1, int(fps))  # Process at least 1 frame per second
    
    all_violations = []
    unique_violations = set()  # To track unique violations
    frames_processed = 0
    last_notification_time = 0
    notification_cooldown = 10  # seconds between notifications
    violation_images = []
    
    print(f"Processing video: {video_path}")
    print(f"FPS: {fps}, Total frames: {total_frames}, Processing every {frame_step} frames")
    
    try:
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_step == 0:
                frames_processed += 1
                results = app.ppe_detector.detect(frame, area_type)
                frame_violations = results.get('violations', [])
                
                if frame_violations:
                    current_time = time.time()
                    for violation in frame_violations:
                        violation_key = f"{violation['type']}_{frames_processed}"
                        if violation_key not in unique_violations:
                            unique_violations.add(violation_key)
                            all_violations.append(violation)
                    
                    violation_path = os.path.join(
                        app.config['VIOLATION_FOLDER'], 
                        f"video_violation_{int(current_time)}.jpg"
                    )
                    cv2.imwrite(violation_path, frame)
                    violation_images.append(violation_path)
                    
                    if current_time - last_notification_time >= notification_cooldown:
                        violation_types = ", ".join(set(v['type'] for v in frame_violations))
                        message = f"PPE Violation in {area_type} area ({location}): Missing {violation_types}"
                        send_notification(message, violation_path)
                        last_notification_time = current_time
                        
                        for violation in frame_violations:
                            save_violation(app, violation, violation_path, location, area_type)
            
            frame_idx += 1
            
            if frames_processed > 0 and frames_processed % 10 == 0:
                progress = (frame_idx / total_frames) * 100
                print(f"Video processing progress: {progress:.1f}% ({frames_processed} frames analyzed)")
    
    except Exception as e:
        print(f"Error processing video: {str(e)}")
    finally:
        cap.release()
        
    print(f"Video processing complete. Processed {frames_processed} frames, found {len(all_violations)} violations")
    return all_violations

# Image processing function
def process_image(app, image_path, location, area_type='default'):
    """Process a single image for PPE violations."""
    image = cv2.imread(image_path)
    if image is None:
        return []
    
    results = app.ppe_detector.detect(image, area_type)
    violations = results.get('violations', [])
    
    if violations:
        for violation in violations:
            equipment_type = violation.get('type', 'Unknown')
            severity = determine_severity(equipment_type)
            
            files = os.listdir(app.config['VIOLATION_FOLDER'])
            violation_files = [f for f in files if f.startswith('violation_')]
            violation_files.sort(reverse=True)
            
            if violation_files:
                violation_path = os.path.join(app.config['VIOLATION_FOLDER'], violation_files[0])
                save_violation(
                    datetime.datetime.now(), 
                    equipment_type, 
                    violation_path, 
                    location, 
                    area_type, 
                    severity
                )
                
                if violation == violations[0]:
                    all_equipment = ", ".join([v.get('type', 'Unknown') for v in violations])
                    notification_message = create_notification_message(all_equipment, location, area_type, severity)
                    send_notification(notification_message, violation_path)
    
    return violations

# Placeholder functions for missing implementations.
def send_notification(message, image_path):
    # Implement notification logic here.
    print(f"Notification sent: {message} (Image: {image_path})")

def save_violation(*args, **kwargs):
    # Implement database saving logic here.
    print("Violation saved to database.")

def determine_severity(equipment_type):
    # Implement severity determination logic here.
    return "medium"

def create_notification_message(equipment, location, area_type, severity):
    # Build and return a notification message.
    return f"Alert: {equipment} violation in {location} ({area_type}) - Severity: {severity}"

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=env.get("PORT", 3000))

