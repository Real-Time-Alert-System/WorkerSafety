# app.py (Main Flask Application)
from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import cv2
import numpy as np
import datetime
import sqlite3
import json
from werkzeug.utils import secure_filename
from notification import send_notification
from routes.api import register_ppe_with_app

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
VIOLATION_FOLDER = 'violations'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIOLATION_FOLDER'] = VIOLATION_FOLDER

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIOLATION_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME,
        equipment_type TEXT,
        image_path TEXT,
        location TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Import PPE detection model
from model.ppe_detector import PPEDetector
ppe_detector = PPEDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    location = request.form.get('location', 'Unknown')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file (image or video)
        if filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}:
            process_image(filepath, location)
        else:
            process_video(filepath, location)
            
        return jsonify({'success': 'File processed successfully'}), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

def process_image(image_path, location):
    image = cv2.imread(image_path)
    if image is None:
        return
    
    # Detect PPE violations
    results = ppe_detector.detect(image)
    
    # Check for violations
    if results['violations']:
        timestamp = datetime.datetime.now()
        
        # Save the violation image
        violation_filename = f"violation_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        violation_path = os.path.join(app.config['VIOLATION_FOLDER'], violation_filename)
        
        # Draw bounding boxes around violations
        for violation in results['violations']:
            equipment_type = violation['type']
            bbox = violation['bbox']  # [x, y, width, height]
            cv2.rectangle(image, 
                         (bbox[0], bbox[1]), 
                         (bbox[0] + bbox[2], bbox[1] + bbox[3]), 
                         (0, 0, 255), 2)
            cv2.putText(image, f"Missing: {equipment_type}", 
                       (bbox[0], bbox[1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Save to database
            save_violation(timestamp, equipment_type, violation_path, location)
        
        # Save the annotated image
        cv2.imwrite(violation_path, image)
        
        # Send notification for each violation
        for violation in results['violations']:
            send_notification(
                subject="PPE Violation Detected",
                message=f"Missing {violation['type']} detected at {location}",
                image_path=violation_path
            )

def process_video(video_path, location):
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        return
    
    frame_count = 0
    sample_rate = 30  # Process every 30th frame
    
    while True:
        ret, frame = video.read()
        
        if not ret:
            break
        
        frame_count += 1
        
        # Process every nth frame
        if frame_count % sample_rate == 0:
            # Save frame temporarily
            temp_frame_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_frame_{frame_count}.jpg")
            cv2.imwrite(temp_frame_path, frame)
            
            # Process the frame
            process_image(temp_frame_path, location)
            
            # Remove temporary frame
            os.remove(temp_frame_path)
    
    video.release()

def save_violation(timestamp, equipment_type, image_path, location):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO violations (timestamp, equipment_type, image_path, location) VALUES (?, ?, ?, ?)",
        (timestamp, equipment_type, image_path, location)
    )
    conn.commit()
    conn.close()

@app.route('/statistics')
def statistics():
    # Get statistics from database
    conn = sqlite3.connect('test.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Equipment types count
    cursor.execute("""
    SELECT equipment_type, COUNT(*) as count
    FROM violations
    GROUP BY equipment_type
    ORDER BY count DESC
    """)
    equipment_stats = cursor.fetchall()
    
    # Time of day analysis
    cursor.execute("""
    SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
    FROM violations
    GROUP BY hour
    ORDER BY hour
    """)
    hourly_stats = cursor.fetchall()
    
    conn.close()
    
    # Prepare data for charts
    equipment_labels = [row['equipment_type'] for row in equipment_stats]
    equipment_counts = [row['count'] for row in equipment_stats]
    
    hours = [row['hour'] for row in hourly_stats]
    hourly_counts = [row['count'] for row in hourly_stats]
    
    chart_data = {
        'equipment': {
            'labels': equipment_labels,
            'counts': equipment_counts
        },
        'hourly': {
            'labels': hours,
            'counts': hourly_counts
        }
    }
    
    return render_template('statistics.html', chart_data=json.dumps(chart_data))

@app.route('/violations')
def view_violations():
    conn = sqlite3.connect('test.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, timestamp, equipment_type, image_path, location
    FROM violations
    ORDER BY timestamp DESC
    """)
    
    violations = cursor.fetchall()
    conn.close()
    
    return render_template('violations.html', violations=violations)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
