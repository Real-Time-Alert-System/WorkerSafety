# utils.py
from flask import current_app
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import json
import time
from datetime import datetime
import pandas as pd
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WarehouseSafety")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

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

def require_auth(f):
    """Decorator to require authentication for API endpoints"""
    from flask import request, jsonify
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.endpoint and 'dashboard' not in request.endpoint:
            auth_header = request.headers.get('Authorization')
            if not auth_header or auth_header != f"Bearer {current_app.config['AUTH_TOKEN']}":
                return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
