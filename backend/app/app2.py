# app.py
import sys
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
import cv2
import numpy as np
import datetime
import sqlite3
import json
from werkzeug.utils import secure_filename
import shutil

# Configure Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
project_root = os.path.abspath(os.path.join(parent_dir, '..'))

# Add necessary paths to system
sys.path.append(project_root)  # Root directory (WorkerSafety/)
sys.path.append(current_dir)   # App directory (backend/app/)

# Now import your modules
from notification import send_notification
from model.ppe_detector import PPEDetector

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
VIOLATION_FOLDER = os.path.join(parent_dir, 'alerts')  # Store violations in parent/alerts
DB_FOLDER = os.path.join(parent_dir, 'db')  # Store DB in parent/db
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIOLATION_FOLDER'] = VIOLATION_FOLDER
app.config['DB_FOLDER'] = DB_FOLDER

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIOLATION_FOLDER, exist_ok=True)
os.makedirs(DB_FOLDER, exist_ok=True)

# Set the database path
DB_PATH = os.path.join(DB_FOLDER, 'violations.db')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create violations table with more detailed information
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
    
    # Create a table for equipment statistics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_type TEXT UNIQUE,
        violation_count INTEGER DEFAULT 0,
        last_updated DATETIME
    )
    ''')
    
    # Create a table for location statistics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS location_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT UNIQUE,
        violation_count INTEGER DEFAULT 0,
        last_updated DATETIME
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Initialize the PPE detector
ppe_detector = PPEDetector()

@app.route('/')
def index():
    return render_template('charts.html')

@app.route('/upload', methods=['POST'])
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
        
        if filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}:
            violations = process_image(filepath, location, area_type)
            violation_count = len(violations)
        else:
            violation_count = process_video(filepath, location, area_type)
            
        return jsonify({
            'success': 'File processed successfully',
            'violations_detected': violation_count
        }), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

def process_image(image_path, location, area_type='default'):
    """Process a single image for PPE violations"""
    image = cv2.imread(image_path)
    if image is None:
        return []
    
    # Run detection with the specified area type
    results = ppe_detector.detect(image, area_type)
    
    violations = results.get('violations', [])
    if violations:
        # The image with annotations is already saved in the alerts folder by the detector
        # We just need to update the database
        for violation in violations:
            equipment_type = violation.get('type', 'Unknown')
            severity = determine_severity(equipment_type)
            
            # Get the most recent violation image for this equipment type
            files = os.listdir(app.config['VIOLATION_FOLDER'])
            violation_files = [f for f in files if f.startswith('violation_')]
            violation_files.sort(reverse=True)  # Sort by newest first
            
            if violation_files:
                violation_path = os.path.join(app.config['VIOLATION_FOLDER'], violation_files[0])
                save_violation(datetime.datetime.now(), equipment_type, violation_path, location, area_type, severity)
                
                # Build notification message
                notification_message = create_notification_message(equipment_type, location, area_type, severity)
                send_notification(notification_message, violation_path)
    
    return violations

def process_video(video_path, location, area_type='default'):
    """Process a video file for PPE violations"""
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        return 0
    
    total_violations = 0
    frame_count = 0
    fps = video.get(cv2.CAP_PROP_FPS)
    sample_rate = int(fps)  # Process one frame per second
    
    while True:
        ret, frame = video.read()
        if not ret:
            break
        
        frame_count += 1
        if frame_count % sample_rate == 0:
            temp_frame_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_frame_{frame_count}.jpg")
            cv2.imwrite(temp_frame_path, frame)
            violations = process_image(temp_frame_path, location, area_type)
            total_violations += len(violations)
            os.remove(temp_frame_path)
    
    video.release()
    return total_violations

def determine_severity(equipment_type):
    """Determine the severity of a violation based on equipment type"""
    high_severity = ['helmet', 'safety_goggles']
    medium_severity = ['safety_vest', 'gloves']
    
    if equipment_type in high_severity:
        return 'high'
    elif equipment_type in medium_severity:
        return 'medium'
    else:
        return 'low'

def create_notification_message(equipment_type, location, area_type, severity):
    """Create a formatted notification message"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    severity_emoji = {
        'high': '🚨',
        'medium': '⚠️',
        'low': '📝'
    }
    
    emoji = severity_emoji.get(severity, '⚠️')
    
    message = f"""{emoji} *PPE Violation Detected* {emoji}
    
    Missing {equipment_type} detected at {location}.
    
    *Details:*
    - Location: {location}
    - Area Type: {area_type}
    - Equipment: {equipment_type}
    - Severity: {severity.upper()}
    - Time: {timestamp}
    
    [View Details](http://your-domain.com/violations)"""
    
    return message

def save_violation(timestamp, equipment_type, image_path, location, area_type, severity):
    """Save violation to database and update statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Insert the violation record
        cursor.execute(
            "INSERT INTO violations (timestamp, equipment_type, image_path, location, area_type, severity) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, equipment_type, image_path, location, area_type, severity)
        )
        
        # Update equipment statistics
        cursor.execute(
            """
            INSERT INTO equipment_stats (equipment_type, violation_count, last_updated)
            VALUES (?, 1, ?)
            ON CONFLICT(equipment_type) DO UPDATE SET
            violation_count = violation_count + 1,
            last_updated = ?
            """,
            (equipment_type, timestamp, timestamp)
        )
        
        # Update location statistics
        cursor.execute(
            """
            INSERT INTO location_stats (location, violation_count, last_updated)
            VALUES (?, 1, ?)
            ON CONFLICT(location) DO UPDATE SET
            violation_count = violation_count + 1,
            last_updated = ?
            """,
            (location, timestamp, timestamp)
        )
        
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

@app.route('/statistics')
def statistics():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get equipment violation statistics
    cursor.execute("""
    SELECT equipment_type, COUNT(*) as count
    FROM violations
    GROUP BY equipment_type
    ORDER BY count DESC
    """)
    equipment_stats = cursor.fetchall()
    
    # Get hourly violation statistics
    cursor.execute("""
    SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
    FROM violations
    GROUP BY hour
    ORDER BY hour
    """)
    hourly_stats = cursor.fetchall()
    
    # Get location statistics
    cursor.execute("""
    SELECT location, COUNT(*) as count
    FROM violations
    GROUP BY location
    ORDER BY count DESC
    """)
    location_stats = cursor.fetchall()
    
    # Get severity statistics
    cursor.execute("""
    SELECT severity, COUNT(*) as count
    FROM violations
    GROUP BY severity
    ORDER BY CASE severity
             WHEN 'high' THEN 1
             WHEN 'medium' THEN 2
             WHEN 'low' THEN 3
             ELSE 4
             END
    """)
    severity_stats = cursor.fetchall()
    
    # Get daily trend for last 30 days
    cursor.execute("""
    SELECT date(timestamp) as day, COUNT(*) as count
    FROM violations
    WHERE timestamp >= date('now', '-30 days')
    GROUP BY day
    ORDER BY day
    """)
    daily_trend = cursor.fetchall()
    
    conn.close()
    
    chart_data = {
        'equipment': {
            'labels': [row['equipment_type'] for row in equipment_stats],
            'counts': [row['count'] for row in equipment_stats]
        },
        'hourly': {
            'labels': [row['hour'] for row in hourly_stats],
            'counts': [row['count'] for row in hourly_stats]
        },
        'location': {
            'labels': [row['location'] for row in location_stats],
            'counts': [row['count'] for row in location_stats]
        },
        'severity': {
            'labels': [row['severity'] for row in severity_stats],
            'counts': [row['count'] for row in severity_stats]
        },
        'daily': {
            'labels': [row['day'] for row in daily_trend],
            'counts': [row['count'] for row in daily_trend]
        }
    }
    
    return render_template('statistics.html', chart_data=json.dumps(chart_data))

@app.route('/violations')
def view_violations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, timestamp, equipment_type, image_path, location, area_type, severity, status
    FROM violations
    ORDER BY timestamp DESC
    """)
    
    violations = cursor.fetchall()
    conn.close()
    
    return render_template('violations.html', violations=violations)

@app.route('/update_violation/<int:violation_id>', methods=['POST'])
def update_violation(violation_id):
    """Update the status of a violation"""
    status = request.form.get('status', 'resolved')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE violations SET status = ? WHERE id = ?",
        (status, violation_id)
    )
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('view_violations'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
