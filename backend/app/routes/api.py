# routes/api.py
from flask import Blueprint, jsonify, request, send_from_directory, abort
from utils import require_auth, logger
import json
import time
from datetime import timedelta
import os
from flask import current_app

api_bp = Blueprint('api', __name__)

@api_bp.route("/alert/<filename>")
def serve_alert_image(filename):
    """Serve alert images"""
    # Ensure that the file exists in the alert folder and has a valid image extension
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        abort(400, description="Invalid file type requested.")
    
    file_path = os.path.join(current_app.config['ALERT_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(current_app.config['ALERT_FOLDER'], filename)
    else:
        abort(404, description="File not found.")

@api_bp.route("/alert", methods=["POST"])
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
        with open(current_app.config['HISTORY_FILE'], 'r') as f:
            history = json.load(f)
        
        # Add new entry
        history.append(data)
        
        # Save updated history
        with open(current_app.config['HISTORY_FILE'], 'w') as f:
            json.dump(history, f)
        
        # Update stats if provided
        if "stats" in data:
            with open(current_app.config['STATS_FILE'], 'w') as f:
                json.dump(data["stats"], f)
        
        return jsonify({"success": True, "message": "Alert received and stored"}), 201
        
    except Exception as e:
        logger.error(f"Error processing alert: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route("/stats", methods=["GET"])
@require_auth
def get_stats():
    """Get current system stats"""
    try:
        with open(current_app.config['STATS_FILE'], 'r') as f:
            stats = json.load(f)
        
        # Calculate uptime
        uptime_seconds = time.time() - stats.get("started_at", time.time())
        stats["uptime_seconds"] = uptime_seconds
        stats["uptime_formatted"] = str(timedelta(seconds=int(uptime_seconds)))
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route("/alerts", methods=["GET"])
@require_auth
def get_alerts():
    """Get alerts with optional filtering"""
    try:
        # Load alert history
        with open(current_app.config['HISTORY_FILE'], 'r') as f:
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

@api_bp.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "timestamp": time.time()}), 200

@api_bp.route("/placeholder/<width>/<height>")
def placeholder(width, height):
    """Generate a placeholder image for testing"""
    try:
        import matplotlib.pyplot as plt
        from io import BytesIO
        import numpy as np
        from flask import send_file
        
        # Convert string parameters to integers
        width = int(width)
        height = int(height)
        
        # Create a placeholder image
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        ax.set_facecolor('#e0e0e0')
        ax.text(0.5, 0.5, f"{width}x{height}", 
                horizontalalignment='center', verticalalignment='center')
        ax.axis('off')
        plt.tight_layout(pad=0)
        
        # Convert to image
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Error generating placeholder: {e}")
        return jsonify({"error": str(e)}), 500
