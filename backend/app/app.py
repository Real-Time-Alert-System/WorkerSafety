```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SafetyGuard - PPE Detection System</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                <i class="fas fa-hard-hat"></i>
                <h1>SafetyGuard</h1>
            </div>
            <nav>
                <ul>
                    <li><a href="#home" class="active">Home</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#demo">Try It</a></li>
                    <li><a href="#contact">Contact</a></li>
                    {% if session.user %}
                        <li><a href="{{ url_for('dashboard') }}"><i class="fas fa-chart-bar"></i> Dashboard</a></li>
                        <li><a href="{{ url_for('logout') }}"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
                    {% else %}
                        <li><a href="{{ url_for('login') }}" class="btn-login"><i class="fas fa-sign-in-alt"></i> Login</a></li>
                    {% endif %}
                </ul>
            </nav>
        </div>
    </header>

    <section id="home" class="hero">
        <div class="container">
            <div class="hero-content">
                <h1>Advanced PPE Detection for Workplace Safety</h1>
                <p>Ensure compliance and protect your workers with our AI-powered PPE detection system</p>
                <a href="#demo" class="btn-primary">Try It Now</a>
                {% if not session.user %}
                    <a href="{{ url_for('login') }}" class="btn-secondary">Sign In to Access Dashboard</a>
                {% else %}
                    <a href="{{ url_for('dashboard') }}" class="btn-secondary">Go to Your Dashboard</a>
                {% endif %}
            </div>
        </div>
    </section>

    <section id="about" class="features">
        <div class="container">
            <h2>Protecting Your Most Valuable Asset: Your People</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <i class="fas fa-tachometer-alt"></i>
                    <h3>Real-Time Detection</h3>
                    <p>Instant identification of PPE compliance issues</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-chart-line"></i>
                    <h3>Analytics Dashboard</h3>
                    <p>Track compliance trends across your organization</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-bell"></i>
                    <h3>Instant Alerts</h3>
                    <p>Immediate notifications for safety violations</p>
                </div>
                <div class="feature-card">
                    <i class="fas fa-mobile-alt"></i>
                    <h3>Mobile Compatible</h3>
                    <p>Works on any device, anywhere on your site</p>
                </div>
            </div>
        </div>
    </section>

    <section id="demo" class="demo-area">
        <div class="container">
            <h2>See It In Action</h2>
            <p>Upload an image or video to test our PPE detection system</p>
            
            <div class="upload-container">
                <form id="upload-form" enctype="multipart/form-data">
                    <div class="file-drop-area">
                        <span class="fake-btn">Choose files</span>
                        <span class="file-msg">or drag and drop files here</span>
                        <input class="file-input" type="file" name="file" accept=".jpg,.jpeg,.png,.mp4,.avi,.mov">
                    </div>
                    <div class="form-group">
                        <label for="location">Location:</label>
                        <input type="text" id="location" name="location" placeholder="e.g., Building A, Floor 2">
                    </div>
                    <div class="form-group">
                        <label for="area_type">Area Type:</label>
                        <select id="area_type" name="area_type">
                            <option value="construction">Construction</option>
                            <option value="laboratory">Laboratory</option>
                            <option value="warehouse">Warehouse</option>
                            <option value="factory">Factory</option>
                            <option value="default">Other</option>
                        </select>
                    </div>
                    <button type="submit" class="btn-primary">Analyze Safety Compliance</button>
                </form>
            </div>
            
            <div id="results" class="results-container hidden">
                <div class="results-header">
                    <h3>PPE Detection Results</h3>
                </div>
                <div class="results-body">
                    <div class="image-container">
                        <img id="result-image" src="" alt="Analysis result">
                    </div>
                    <div class="results-data">
                        <div id="loading" class="hidden">
                            <div class="spinner"></div>
                            <p>Analyzing file...</p>
                        </div>
                        <div id="result-items"></div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="contact" class="contact">
        <div class="container">
            <h2>Ready to enhance workplace safety?</h2>
            <p>Contact us for a free consultation and demo of our full system</p>
            <a href="mailto:info@safetyguard.com" class="btn-secondary">Get In Touch</a>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2025 SafetyGuard - PPE Detection System. All rights reserved.</p>
        </div>
    </footer>

    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>

```

2. Now, let's update the JavaScript to handle video uploads and display the results:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const fileDropArea = document.querySelector('.file-drop-area');
    const fileInput = fileDropArea.querySelector('.file-input');
    const fileMsg = fileDropArea.querySelector('.file-msg');
    const uploadForm = document.getElementById('upload-form');
    const resultsContainer = document.getElementById('results');
    const loadingIndicator = document.getElementById('loading');
    const resultItems = document.getElementById('result-items');
    const resultImage = document.getElementById('result-image');

    // File drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        fileDropArea.classList.add('highlight');
    }

    function unhighlight() {
        fileDropArea.classList.remove('highlight');
    }

    fileDropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        updateFileMessage(files);
    }

    fileInput.addEventListener('change', function() {
        updateFileMessage(this.files);
    });

    function updateFileMessage(files) {
        if (files.length > 0) {
            fileMsg.textContent = files[0].name;
        } else {
            fileMsg.textContent = 'or drag and drop files here';
        }
    }

    // Form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(uploadForm);
        
        if (!fileInput.files.length) {
            alert('Please select a file to upload');
            return;
        }
        
        // Show loading indicator
        loadingIndicator.classList.remove('hidden');
        resultItems.innerHTML = '';
        resultsContainer.classList.remove('hidden');
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add('hidden');
            
            if (data.error) {
                resultItems.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            if (data.violations && data.violations.length > 0) {
                // Display violation results
                resultImage.src = `/alerts/${data.violations[0].image.split('/').pop()}`;
                
                let resultsHTML = '<h3>Detected Violations:</h3><ul class="violations-list">';
                
                data.violations.forEach(violation => {
                    resultsHTML += `
                        <li class="violation-item ${violation.type}">
                            <i class="fas fa-exclamation-triangle"></i>
                            <span>Missing ${violation.type.replace('_', ' ')}</span>
                            <span class="confidence">Confidence: ${(violation.confidence * 100).toFixed(1)}%</span>
                        </li>
                    `;
                });
                
                resultsHTML += '</ul>';
                resultsHTML += `<p class="notification-sent">Automatic notification has been sent to safety personnel.</p>`;
                
                resultItems.innerHTML = resultsHTML;
            } else {
                resultItems.innerHTML = `
                    <div class="success">
                        <i class="fas fa-check-circle"></i>
                        <p>No PPE violations detected. All safety requirements met!</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            loadingIndicator.classList.add('hidden');
            resultItems.innerHTML = `<div class="error">An error occurred during processing: ${error.message}</div>`;
        });
    });
});
</script>

```

3. Let's add some CSS for the new elements:

```css
/* General Styles */
:root {
    --primary-color: #0056b3;
    --secondary-color: #28a745;
    --dark-color: #333;
    --light-color: #f4f4f4;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--dark-color);
    background-color: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

a {
    text-decoration: none;
    color: var(--primary-color);
}

ul {
    list-style: none;
}

/* Button Styles */
.btn-primary, .btn-secondary {
    display: inline-block;
    padding: 10px 20px;
    margin: 10px 5px;
    border-radius: 5px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    border: none;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}

.btn-secondary {
    background-color: var(--secondary-color);
    color: white;
}

.btn-primary:hover {
    background-color: #004494;
}

.btn-secondary:hover {
    background-color: #218838;
}

/* Header */
header {
    background-color: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}

header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
}

.logo {
    display: flex;
    align-items: center;
}

.logo i {
    font-size: 1.8rem;
    color: var(--primary-color);
    margin-right: 10px;
}

.logo h1 {
    font-size: 1.5rem;
    color: var(--primary-color);
}

nav ul {
    display: flex;
}

nav ul li {
    margin-left: 20px;
}

nav ul li a {
    color: var(--dark-color);
    font-weight: 500;
    padding: 5px;
    transition: all 0.3s ease;
}

nav ul li a:hover, nav ul li a.active {
    color: var(--primary-color);
}

.btn-login {
    background-color: var(--primary-color);
    color: white !important;
    padding: 8px 15px;
    border-radius: 5px;
}

.btn-login:hover {
    background-color: #004494;
}

/* Hero Section */
.hero {
    background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('../img/hero.jpg');
    background-size: cover;
    background-position: center;
    height: 80vh;
    color: white;
    display: flex;
    align-items: center;
    text-align: center;
}

.hero-content {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 20px;
}

.hero p {
    font-size: 1.2rem;
    margin-bottom: 30px;
}

/* Features Section */
.features {
    padding: 80px 0;
    background-color: white;
}

.features h2 {
    text-align: center;
    margin-bottom: 50px;
    font-size: 2.2rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
}

.feature-card {
    text-align: center;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-10px);
}

.feature-card i {
    font-size: 3rem;
    color: var(--primary-color);
    margin-bottom: 20px;
}

.feature-card h3 {
    font-size: 1.5rem;
    margin-bottom: 15px;
}

/* Demo Area */
.demo-area {
    padding: 80px 0;
    background-color: #f8f9fa;
}

.demo-area h2, .demo-area p {
    text-align: center;
}

.demo-area h2 {
    font-size: 2.2rem;
    margin-bottom: 15px;
}

.demo-area > p {
    font-size: 1.1rem;
    margin-bottom: 40px;
}

.upload-container {
    max-width: 700px;
    margin: 0 auto;
    padding: 30px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.file-drop-area {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    max-width: 100%;
    padding: 25px;
    border: 2px dashed #ccc;
    border-radius: 3px;
    transition: 0.2s;
    margin-bottom: 20px;
}

.file-drop-area.highlight {
    border-color: var(--primary-color);
}

.fake-btn {
    flex-shrink: 0;
    background-color: var(--primary-color);
    color: white;
    border-radius: 3px;
    padding: 8px 15px;
    margin-right: 10px;
    font-size: 12px;
    text-transform: uppercase;
}

.file-msg {
    font-size: small;
    font-weight: 300;
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.file-input {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 100%;
    cursor: pointer;
    opacity: 0;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
}

.form-group input, .form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

/* Results Container */
.results-container {
    max-width: 700px;
    margin: 30px auto;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.results-container.hidden {
    display: none;
}

.results-header {
    background-color: var(--primary-color);
    color: white;
    padding: 15px 20px;
}

.results-header h3 {
    margin: 0;
    font-size: 1.2rem;
}

.results-body {
    padding: 20px;
    display: flex;
    flex-direction: column;
}

.image-container {
    margin-bottom: 20px;
    text-align: center;
}

.image-container img {
    max-width: 100%;
    max-height: 400px;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: var(--primary-color);
    animation: spin 1s linear infinite;
    margin: 0 auto 15px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.hidden {
    display: none !important;
}

.violations-list {
    margin-top: 15px;
}

.violation-item {
    display: flex;
    align-items: center;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 5px;
    background-color: #fef0f0;
}

.violation-item i {
    color: var(--danger-color);
    font-size: 1.2rem;
    margin-right: 10px;
}

.violation-item.helmet i {
    color: #e74c3c;
}

.violation-item.safety_goggles i {
    color: #f39c12;
}

.violation-item.vest i {
    color: #e67e22;
}

.violation-item.gloves i {
    color: #d35400;
}

.confidence {
    margin-left: auto;
    font-size: 0.9rem;
    color: #777;
}

.notification-sent {
    margin-top: 20px;
    text-align: center;
    color: var(--primary-color);
    font-weight: 500;
}

.success {
    display: flex;
    align-items: center;
    padding: 15px;
    background-color: #e6f7ed;
    border-radius: 5px;
}

.success i {
    color: var(--secondary-color);
    font-size: 2rem;
    margin-right: 15px;
}

.error {
    padding: 15px;
    background-color: #fef0f0;
    border-radius: 5px;
    color: var(--danger-color);
}

/* Contact Section */
.contact {
    padding: 60px 0;
    background-color: var(--primary-color);
    color: white;
    text-align: center;
}

.contact h2 {
    font-size: 2.2rem;
    margin-bottom: 15px;
}

.contact p {
    font-size: 1.1rem;
    margin-bottom: 30px;
}

.contact .btn-secondary {
    background-color: white;
    color: var(--primary-color);
}

.contact .btn-secondary:hover {
    background-color: #f1f1f1;
}

/* Footer */
footer {
    background-color: var(--dark-color);
    color: white;
    padding: 20px 0;
    text-align: center;
}

/* Responsive */
@media (max-width: 768px) {
    .hero h1 {
        font-size: 2rem;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
    }
    
    .results-body {
        flex-direction: column;
    }
    
    .image-container, .results-data {
        width: 100%;
    }
    
    nav ul {
        flex-direction: column;
        text-align: center;
    }
    
    nav ul li {
        margin: 10px 0;
    }
}

```

4. Now let's update the server.py file to handle video uploads and properly integrate with the PPE detector and notification system:

```python
import sys
import os
import cv2
import numpy as np
import datetime
import sqlite3
import json
import time
import uuid
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
        'SECRET_KEY': env.get("APP_SECRET_KEY", "default-secret-key"),
        'MAX_CONTENT_LENGTH': 50 * 1024 * 1024  # 50 MB max upload
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
        return redirect(f"https://{env.get('AUTH0_DOMAIN', 'domain.auth0.com')}/v2/logout?" + urlencode({
            "returnTo": url_for("index", _external=True),
            "client_id": env.get("AUTH0_CLIENT_ID"),
        }, quote_via=quote_plus))

    @app.route("/dashboard")
    @requires_auth
    def dashboard():
        return render_template("dashboard.html", session=session.get('user'))

    @app.route("/upload", methods=["POST"])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        location = request.form.get('location', 'Unknown')
        area_type = request.form.get('area_type', 'default')
        
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save the uploaded file with a unique name
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the file based on its type
            file_ext = filename.rsplit('.', 1)[1].lower()
            if file_ext in {'jpg', 'jpeg', 'png'}:
                violations = process_image(app, filepath, location, area_type)
            else:  # video file
                violations = process_video(app, filepath, location, area_type)
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            return jsonify({
                'violations': violations,
                'message': f'Found {len(violations)} violations'
            })
        
        except Exception as e:
            # Clean up in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            app.logger.error(f"Error processing file: {str(e)}")
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500

    @app.route("/alerts/<filename>")
    def get_alert_image(filename):
        return send_from_directory(app.config['VIOLATION_FOLDER'], filename)

    @app.route("/api/violations")
    @requires_auth
    def get_violations():
        conn = sqlite3.connect(app.config['DB_PATH'])
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM violations ORDER BY timestamp DESC LIMIT 100
        ''')
        
        violations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(violations)

    @app.route("/api/statistics")
    @requires_auth
    def get_statistics():
        conn = sqlite3.connect(app.config['DB_PATH'])
        cursor = conn.cursor()
        
        # Get violation counts by type
        cursor.execute('''
            SELECT equipment_type, COUNT(*) as count
            FROM violations
            GROUP BY equipment_type
        ''')
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get violation counts by location
        cursor.execute('''
            SELECT location, COUNT(*) as count
            FROM violations
            GROUP BY location
        ''')
        by_location = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get violation counts
```
