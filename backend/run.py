# run.py
from app import create_app
import os
import json

app = create_app()

# Create necessary directories and default files for first run
def initialize_app():
    """Initialize application with default data files"""
    # Create alerts directory
    os.makedirs(app.config['ALERT_FOLDER'], exist_ok=True)
    
    # Create uploads directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create empty history file if not exists
    if not os.path.exists(app.config['HISTORY_FILE']):
        with open(app.config['HISTORY_FILE'], 'w') as f:
            json.dump([], f)
    
    # Create empty stats file if not exists
    if not os.path.exists(app.config['STATS_FILE']):
        default_stats = {
            "started_at": os.path.getmtime(app.config['HISTORY_FILE']),
            "total_processed": 0,
            "violations_detected": 0,
            "cameras_online": 8,
            "system_status": "operational"
        }
        with open(app.config['STATS_FILE'], 'w') as f:
            json.dump(default_stats, f)
    
    print("Application initialized with default directories and files.")

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
