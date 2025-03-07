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
