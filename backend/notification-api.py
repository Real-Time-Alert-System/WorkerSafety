import os
import json
import time
import logging
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, abort, request, jsonify, render_template_string
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NotificationAPI")

app = Flask(__name__)

# Configuration
ALERT_FOLDER = os.path.abspath("alerts")
HISTORY_FILE = os.path.join(ALERT_FOLDER, "violation_history.json")
STATS_FILE = os.path.join(ALERT_FOLDER, "detection_stats.json")
AUTH_TOKEN = "your_secure_token_here"  # Replace with a secure token

# Make sure alert folder exists
if not os.path.exists(ALERT_FOLDER):
    os.makedirs(ALERT_FOLDER)

# Initialize history file if it doesn't exist
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)

# Initialize stats file if it doesn't exist
if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, 'w') as f:
        json.dump({
            "total_frames": 0,
            "violations_detected": 0,
            "notifications_sent": 0,
            "started_at": time.time()
        }, f)

# Dashboard HTML template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Acme Corp - Warehouse</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .header-title {
            font-size: 18px;
            font-weight: bold;
        }
        .header-logo {
            display: flex;
            align-items: center;
        }
        .header-icon {
            background-color: #0d1117;
            border-radius: 8px;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
        }
        .header-right {
            display: flex;
            align-items: center;
        }
        .user-icon {
            width: 32px;
            height: 32px;
            background-color: #000;
            border-radius: 50%;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .main-content {
            display: flex;
        }
        .sidebar {
            width: 60px;
            background-color: white;
            padding: 15px 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 25px;
            border-radius: 10px;
            margin-right: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .sidebar-icon {
            color: #666;
            font-size: 24px;
            cursor: pointer;
        }
        .sidebar-icon.active {
            color: #000;
        }
        .content-area {
            flex: 1;
        }
        
        /* Score and metrics section */
        .score-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }
        .score-card {
            background-color: #000;
            border-radius: 10px;
            padding: 20px;
            color: white;
            flex: 1;
            min-width: 200px;
            position: relative;
            overflow: hidden;
        }
        .score-gauge {
            position: relative;
            width: 140px;
            height: 140px;
            margin-right: 20px;
        }
        .score-gauge svg {
            transform: rotate(-90deg);
        }
        .score-value {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 42px;
            font-weight: bold;
        }
        .score-title {
            font-size: 16px;
            margin-top: 5px;
            opacity: 0.8;
        }
        .score-details {
            margin-top: 20px;
        }
        .score-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .score-item-label {
            font-size: 14px;
            opacity: 0.8;
        }
        .score-item-value {
            font-weight: 600;
        }
        .score-item-bar {
            height: 5px;
            background-color: #333;
            border-radius: 5px;
            margin-top: 5px;
            position: relative;
        }
        .score-item-fill {
            height: 100%;
            border-radius: 5px;
            background-color: #4CAF50;
        }
        
        /* Highlighted videos section */
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .section-title {
            font-size: 16px;
            font-weight: bold;
        }
        .view-all {
            font-size: 14px;
            color: #666;
            text-decoration: none;
        }
        .videos-container {
            display: flex;
            gap: 15px;
            overflow-x: auto;
            padding-bottom: 10px;
        }
        .video-card {
            width: 180px;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .video-thumbnail {
            width: 100%;
            height: 100px;
            object-fit: cover;
            display: block;
        }
        .video-details {
            padding: 10px;
        }
        .video-title {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .video-info {
            font-size: 12px;
            color: #666;
            display: flex;
            justify-content: space-between;
        }
        
        /* Incidents section */
        .incidents-container {
            margin-top: 30px;
        }
        .incidents-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        .incidents-title {
            font-size: 16px;
            font-weight: bold;
        }
        .incidents-count {
            font-size: 24px;
            font-weight: bold;
        }
        .incidents-chart {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .chart-bars {
            display: flex;
            align-items: flex-end;
            height: 60px;
            gap: 2px;
        }
        .chart-bar {
            background-color: #000;
            flex: 1;
        }
        
        /* Activity sidebar */
        .activity-sidebar {
            width: 300px;
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-left: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .activity-card {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .activity-title {
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .activity-count {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .activity-subtitle {
            font-size: 12px;
            color: #666;
        }
        .activity-list {
            margin-top: 30px;
        }
        .activity-list-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .activity-item {
            display: flex;
            margin-bottom: 15px;
            align-items: flex-start;
        }
        .activity-icon {
            width: 24px;
            height: 24px;
            background-color: #f1f1f1;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
            flex-shrink: 0;
        }
        .activity-content {
            flex: 1;
        }
        .activity-text {
            font-size: 13px;
            line-height: 1.4;
        }
        .activity-time {
            font-size: 12px;
            color: #666;
            margin-top: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-logo">
                <div class="header-icon">⚙️</div>
                <div class="header-title">Acme Corp - Warehouse</div>
            </div>
            <div class="header-right">
                <div class="user-icon">A</div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="sidebar">
                <div class="sidebar-icon active">🏠</div>
                <div class="sidebar-icon">📊</div>
                <div class="sidebar-icon">📋</div>
                <div class="sidebar-icon">⚙️</div>
            </div>
            
            <div class="content-area">
                <div class="score-container">
                    <div class="score-card">
                        <div style="display: flex;">
                            <div class="score-gauge">
                                <svg width="140" height="140" viewBox="0 0 140 140">
                                    <circle cx="70" cy="70" r="60" fill="none" stroke="#333" stroke-width="10"/>
                                    <circle cx="70" cy="70" r="60" fill="none" stroke="#4CAF50" stroke-width="10" stroke-dasharray="377" stroke-dashoffset="109"/>
                                </svg>
                                <div class="score-value">71</div>
                            </div>
                            <div style="flex: 1;">
                                <div class="score-title">Voxel Site Score</div>
                                
                                <div class="score-details">
                                    <div class="score-item">
                                        <div class="score-item-label">Improper Lifting</div>
                                        <div class="score-item-value">20</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: 20%; background-color: #ff6b6b;"></div>
                                    </div>
                                    
                                    <div class="score-item">
                                        <div class="score-item-label">Overreaching</div>
                                        <div class="score-item-value">43</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: 43%; background-color: #ff9f43;"></div>
                                    </div>
                                    
                                    <div class="score-item">
                                        <div class="score-item-label">No Stop at Aisle</div>
                                        <div class="score-item-value">59</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: 59%; background-color: #feca57;"></div>
                                    </div>
                                    
                                    <div class="score-item">
                                        <div class="score-item-label">No Stop at Intersection</div>
                                        <div class="score-item-value">71</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: 71%; background-color: #1dd1a1;"></div>
                                    </div>
                                    
                                    <div class="score-item">
                                        <div class="score-item-label">No Red Zone</div>
                                        <div class="score-item-value">86</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: 86%; background-color: #2ecc71;"></div>
                                    </div>
                                    
                                    <div class="score-item">
                                        <div class="score-item-label">Safety Vest</div>
                                        <div class="score-item-value">99</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: 99%; background-color: #10ac84;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="section-header">
                    <div class="section-title">Highlighted Videos</div>
                    <a href="#" class="view-all">View All</a>
                </div>
                
                <div class="videos-container">
                    <div class="video-card">
                        <img src="/api/placeholder/180/100" alt="Video thumbnail" class="video-thumbnail">
                        <div class="video-details">
                            <div class="video-title">Improper Lifting</div>
                            <div class="video-info">
                                <span>Aisle 3 Zone 4</span>
                                <span>2 days ago</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="video-card">
                        <img src="/api/placeholder/180/100" alt="Video thumbnail" class="video-thumbnail">
                        <div class="video-details">
                            <div class="video-title">Near Miss</div>
                            <div class="video-info">
                                <span>Forklift Zone</span>
                                <span>10 hrs ago</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="video-card">
                        <img src="/api/placeholder/180/100" alt="Video thumbnail" class="video-thumbnail">
                        <div class="video-details">
                            <div class="video-title">Blocked Aisle</div>
                            <div class="video-info">
                                <span>Loading Zone 3</span>
                                <span>2 days ago</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="incidents-container">
                    <div class="incidents-header">
                        <div>
                            <div class="incidents-title">All Incidents</div>
                            <div class="incidents-count">771</div>
                            <div class="video-info">Total Incidents · Last 30 days</div>
                        </div>
                        <div>
                            <span style="color: #666;">+25%</span>
                        </div>
                    </div>
                    
                    <div class="incidents-chart">
                        <div class="chart-bars">
                            <!-- Generate 30 random height bars -->
                            <div class="chart-bar" style="height: 40%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                            <div class="chart-bar" style="height: 45%;"></div>
                            <div class="chart-bar" style="height: 60%;"></div>
                            <div class="chart-bar" style="height: 20%;"></div>
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 55%;"></div>
                            <div class="chart-bar" style="height: 80%;"></div>
                            <div class="chart-bar" style="height: 75%;"></div>
                            <div class="chart-bar" style="height: 40%;"></div>
                            <div class="chart-bar" style="height: 35%;"></div>
                            <div class="chart-bar" style="height: 50%;"></div>
                            <div class="chart-bar" style="height: 65%;"></div>
                            <div class="chart-bar" style="height: 45%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                            <div class="chart-bar" style="height: 40%;"></div>
                            <div class="chart-bar" style="height: 60%;"></div>
                            <div class="chart-bar" style="height: 80%;"></div>
                            <div class="chart-bar" style="height: 70%;"></div>
                            <div class="chart-bar" style="height: 50%;"></div>
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 45%;"></div>
                            <div class="chart-bar" style="height: 65%;"></div>
                            <div class="chart-bar" style="height: 55%;"></div>
                            <div class="chart-bar" style="height: 75%;"></div>
                            <div class="chart-bar" style="height: 40%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                            <div class="chart-bar" style="height: 35%;"></div>
                            <div class="chart-bar" style="height: 50%;"></div>
                            <div class="chart-bar" style="height: 60%;"></div>
                        </div>
                    </div>
                    
                    <div class="incidents-header">
                        <div>
                            <div class="incidents-title">Improper Lifting</div>
                            <div class="incidents-count">456</div>
                            <div class="video-info">Total Events · Last 30 days</div>
                        </div>
                        <div>
                            <span style="color: #666;">+10%</span>
                        </div>
                    </div>
                    
                    <div class="incidents-chart">
                        <div class="chart-bars">
                            <!-- Generate 30 random height bars -->
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 45%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                            <div class="chart-bar" style="height: 50%;"></div>
                            <div class="chart-bar" style="height: 80%;"></div>
                            <div class="chart-bar" style="height: 60%;"></div>
                            <div class="chart-bar" style="height: 35%;"></div>
                            <div class="chart-bar" style="height: 40%;"></div>
                            <div class="chart-bar" style="height: 65%;"></div>
                            <div class="chart-bar" style="height: 55%;"></div>
                            <div class="chart-bar" style="height: 20%;"></div>
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 75%;"></div>
                            <div class="chart-bar" style="height: 50%;"></div>
                            <div class="chart-bar" style="height: 40%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                            <div class="chart-bar" style="height: 55%;"></div>
                            <div class="chart-bar" style="height: 70%;"></div>
                            <div class="chart-bar" style="height: 60%;"></div>
                            <div class="chart-bar" style="height: 45%;"></div>
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 50%;"></div>
                            <div class="chart-bar" style="height: 35%;"></div>
                            <div class="chart-bar" style="height: 75%;"></div>
                            <div class="chart-bar" style="height: 65%;"></div>
                            <div class="chart-bar" style="height: 20%;"></div>
                            <div class="chart-bar" style="height: 40%;"></div>
                            <div class="chart-bar" style="height: 55%;"></div>
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 45%;"></div>
                        </div>
                    </div>
                    
                    <div class="incidents-header">
                        <div>
                            <div class="incidents-title">Overreaching</div>
                            <div class="incidents-count">62</div>
                            <div class="video-info">Total Events · Last 30 days</div>
                        </div>
                        <div>
                            <span style="color: #666;">No change</span>
                        </div>
                    </div>
                    
                    <div class="incidents-chart">
                        <div class="chart-bars">
                            <!-- Generate 30 random height bars -->
                            <div class="chart-bar" style="height: 15%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                            <div class="chart-bar" style="height: 35%;"></div>
                            <div class="chart-bar" style="height: 20%;"></div>
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 10%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                            <div class="chart-bar" style="height: 40%;"></div>
                            <div class="chart-bar" style="height: 15%;"></div>
                            <div class="chart-bar" style="height: 20%;"></div>
                            <div class="chart-bar" style="height: 35%;"></div>
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 15%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                            <div class="chart-bar" style="height: 20%;"></div>
                            <div class="chart-bar" style="height: 10%;"></div>
                            <div class="chart-bar" style="height: 15%;"></div>
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 40%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                            <div class="chart-bar" style="height: 15%;"></div>
                            <div class="chart-bar" style="height: 20%;"></div>
                            <div class="chart-bar" style="height: 35%;"></div>
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 10%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                            <div class="chart-bar" style="height: 15%;"></div>
                            <div class="chart-bar" style="height: 20%;"></div>
                            <div class="chart-bar" style="height: 30%;"></div>
                            <div class="chart-bar" style="height: 25%;"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="activity-sidebar">
                <div class="activity-card">
                    <div class="activity-title">Assigned to me</div>
                    <div class="activity-count">3</div>
                    <div class="activity-subtitle">Unresolved</div>
                </div>
                
                <div class="activity-card">
                    <div class="activity-title">Assigned to me</div>
                    <div class="activity-count">53</div>
                    <div class="activity-subtitle">Resolved</div>
                </div>
                
                <div class="activity-card">
                    <div class="activity-title">Bookmarked</div>
                    <div class="activity-count">23</div>
                </div>
                
                <div class="activity-list">
                    <div class="activity-list-title">Recent Activity</div>
                    
                    <div class="activity-item">
                        <div class="activity-icon">✓</div>
                        <div class="activity-content">
                            <div class="activity-text">Overreaching event resolved by Alex</div>
                            <div class="activity-time">2h ago</div>
                        </div>
                    </div>
                    
                    <div class="activity-item">
                        <div class="activity-icon">💬</div>
                        <div class="activity-content">
                            <div class="activity-text">Alex commented "Not sure" on a Improper Lifting event</div>
                            <div class="activity-time">3h ago</div>
                        </div>
                    </div>
                    
                    <div class="activity-item">
                        <div class="activity-icon">👤</div>
                        <div class="activity-content">
                            <div class="activity-text">Brian Benson assigned a No Stop at Intersection event to Alex</div>
                            <div class="activity-time">5h ago</div>
                        </div>
                    </div>
                    
                    <div class="activity-item">
                        <div class="activity-icon">💬</div>
                        <div class="activity-content">
                            <div class="activity-text">Brandon commented "Reopened" for a No Red Zone event</div>
                            <div class="activity-time">10h ago</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

def require_auth(f):
    """Decorator to require authentication for API endpoints"""
    def decorated(*args, **kwargs):
        if request.endpoint != 'dashboard':  # Don't require auth for dashboard
            auth_header = request.headers.get('Authorization')
            if not auth_header or auth_header != f"Bearer {AUTH_TOKEN}":
                return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@app.route("/")
def dashboard():
    """Main dashboard view"""
    try:
        # Load violation history
        with open(HISTORY_FILE, 'r') as f:
            violation_history = json.load(f)
        
        # Load stats
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
        
        # Calculate uptime
        uptime_seconds = time.time() - stats.get("started_at", time.time())
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime = f"{int(hours)}h {int(minutes)}m"
        
        # Generate violation chart
        violation_chart = generate_violation_chart(violation_history)
        
        # Generate equipment chart
        equipment_chart = generate_equipment_chart(violation_history)
        
        # Prepare recent alerts data
        recent_alerts = []
        for entry in sorted(violation_history, key=lambda x: x['timestamp'], reverse=True)[:9]:
            # Get equipment count
            equipment_counts = {}
            for v in entry.get('violations', []):
                for eq in v.get('missing_equipment', []):
                    equipment_counts[eq] = equipment_counts.get(eq, 0) + 1
            
            equipment_str = ", ".join([f"{count}x {eq.replace('_', ' ')}" 
                                      for eq, count in equipment_counts.items()])
            
            recent_alerts.append({
                'filename': entry.get('filename', ''),
                'time': datetime.fromtimestamp(entry.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                'message': f"Missing: {equipment_str}"
            })
        
        return render_template_string(
            DASHBOARD_TEMPLATE, 
            stats=stats, 
            uptime=uptime,
            violation_chart=violation_chart,
            equipment_chart=equipment_chart,
            recent_alerts=recent_alerts
        )
        
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return f"Error rendering dashboard: {str(e)}", 500

def generate_violation_chart(violation_history):
    """Generate chart showing violations over time"""
    try:
        if not violation_history:
            # Create empty chart if no data
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, "No violation data available", 
                    horizontalalignment='center', verticalalignment='center')
            ax.set_xlabel('Time')
            ax.set_ylabel('Violations')
            plt.tight_layout()
            
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode('utf-8')
        
        # Prepare data for time series
        timestamps = [entry['timestamp'] for entry in violation_history]
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Count violations per hour
        df = pd.DataFrame({'timestamp': dates})
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_counts = df.groupby('hour').size().reset_index(name='count')
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(hourly_counts['hour'], hourly_counts['count'], marker='o', linestyle='-', color='#1a237e')
        ax.set_xlabel('Time')
        ax.set_ylabel('Violations')
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert plot to base64 string
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error generating violation chart: {e}")
        # Return a placeholder image
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, f"Error generating chart: {str(e)}", 
                horizontalalignment='center', verticalalignment='center')
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

def generate_equipment_chart(violation_history):
    """Generate chart showing missing equipment types"""
    try:
        if not violation_history:
            # Create empty chart if no data
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, "No violation data available", 
                    horizontalalignment='center', verticalalignment='center')
            ax.set_xlabel('Equipment Type')
            ax.set_ylabel('Count')
            plt.tight_layout()
            
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode('utf-8')
        
        # Count missing equipment types
        equipment_counts = {}
        for entry in violation_history:
            for violation in entry.get('violations', []):
                for equipment in violation.get('missing_equipment', []):
                    equipment = equipment.replace('_', ' ').title()
                    equipment_counts[equipment] = equipment_counts.get(equipment, 0) + 1
        
        # Sort by count
        equipment_items = sorted(equipment_counts.items(), key=lambda x: x[1], reverse=True)
        equipment_types = [item[0] for item in equipment_items]
        counts = [item[1] for item in equipment_items]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(equipment_types, counts, color='#3949ab')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        ax.set_xlabel('Equipment Type')
        ax.set_ylabel('Number of Violations')
        ax.set_title('Missing Safety Equipment Types')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Convert plot to base64 string
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error generating equipment chart: {e}")
        # Return a placeholder image
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, f"Error generating chart: {str(e)}", 
                horizontalalignment='center', verticalalignment='center')
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

@app.route("/alert/<filename>")
def serve_alert_image(filename):
    """Serve alert images"""
    # Ensure that the file exists in the alert folder and has a valid image extension
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        abort(400, description="Invalid file type requested.")
    
    file_path = os.path.join(ALERT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_from_directory(ALERT_FOLDER, filename)
    else:
        abort(404, description="File not found.")

@app.route("/api/alert", methods=["POST"])
@require_auth
def receive_alert():
    """Receive alert data from detection system"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ["timestamp", "filename", "violations"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Load existing history
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        # Add new entry
        history.append(data)
        
        # Save updated history
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
        
        # Update stats if provided
        if "stats" in data:
            with open(STATS_FILE, 'w') as f:
                json.dump(data["stats"], f)
        
        return jsonify({"success": True, "message": "Alert received and stored"}), 201
        
    except Exception as e:
        logger.error(f"Error processing alert: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats", methods=["GET"])
@require_auth
def get_stats():
    """Get current system stats"""
    try:
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
        
        # Calculate uptime
        uptime_seconds = time.time() - stats.get("started_at", time.time())
        stats["uptime_seconds"] = uptime_seconds
        stats["uptime_formatted"] = str(timedelta(seconds=int(uptime_seconds)))
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/alerts", methods=["GET"])
@require_auth
def get_alerts():
    """Get alerts with optional filtering"""
    try:
        # Load alert history
        with open(HISTORY_FILE, 'r') as f:
            alerts = json.load(f)
        
        # Filter by time range if provided
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        if start_time:
            start_time = float(start_time)
            alerts = [a for a in alerts if a.get('timestamp', 0) >= start_time]
        
        if end_time:
            end_time = float(end_time)
            alerts = [a for a in alerts if a.get('timestamp', 0) <= end_time]
        
        # Limit results if specified
        limit = request.args.get('limit')
        if limit:
            limit = int(limit)
            alerts = sorted(alerts, key=lambda x: x.get('timestamp', 0), reverse=True)[:limit]
        
        return jsonify(alerts), 200
        
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "timestamp": time.time()}), 200

if __name__ == "__main__":
    # Create alert folder if it doesn't exist
    if not os.path.exists(ALERT_FOLDER):
        os.makedirs(ALERT_FOLDER)
        
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    
    logger.info(f"Starting Notification API Server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
