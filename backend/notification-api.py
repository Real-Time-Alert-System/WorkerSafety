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
    <title>Worker Safety Monitoring Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #1a237e;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
            margin-bottom: 20px;
        }
        .stats-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 200px;
        }
        .stat-title {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #1a237e;
        }
        .charts-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }
        .chart-card {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 400px;
        }
        .chart-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .alerts-container {
            background-color: white;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .alert-list {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }
        .alert-card {
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
            width: 270px;
        }
        .alert-image {
            width: 100%;
            height: 180px;
            object-fit: cover;
        }
        .alert-details {
            padding: 10px;
        }
        .alert-time {
            font-size: 12px;
            color: #666;
        }
        .alert-message {
            font-size: 14px;
            margin-top: 5px;
        }
        .refresh-button {
            background-color: #1a237e;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .refresh-button:hover {
            background-color: #0e1442;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Worker Safety Monitoring Dashboard</h1>
            <p>Real-time safety compliance monitoring system</p>
        </div>
        
        <button class="refresh-button" onclick="window.location.reload()">Refresh Dashboard</button>
        
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-title">Total Violations</div>
                <div class="stat-value">{{ stats['violations_detected'] }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Alerts Sent</div>
                <div class="stat-value">{{ stats['notifications_sent'] }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Frames Processed</div>
                <div class="stat-value">{{ stats['total_frames'] }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Uptime</div>
                <div class="stat-value">{{ uptime }}</div>
            </div>
        </div>
        
        <div class="charts-container">
            <div class="chart-card">
                <div class="chart-title">Violations Over Time</div>
                <img src="data:image/png;base64,{{ violation_chart }}" style="width:100%;">
            </div>
            <div class="chart-card">
                <div class="chart-title">Missing Equipment Types</div>
                <img src="data:image/png;base64,{{ equipment_chart }}" style="width:100%;">
            </div>
        </div>
        
        <div class="alerts-container">
            <div class="chart-title">Recent Alerts</div>
            <div class="alert-list">
                {% for alert in recent_alerts %}
                <div class="alert-card">
                    <img src="/alert/{{ alert['filename'] }}" class="alert-image">
                    <div class="alert-details">
                        <div class="alert-time">{{ alert['time'] }}</div>
                        <div class="alert-message">{{ alert['message'] }}</div>
                    </div>
                </div>
                {% endfor %}
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
            return base64.b64encode(buf
