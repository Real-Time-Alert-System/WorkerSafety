# routes/dashboard.py
from flask import Blueprint, render_template, render_template_string, current_app
from utils import generate_violation_chart, generate_equipment_chart, logger
import json
import time
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

# This template can be moved to a separate HTML file in templates/dashboard.html
DASHBOARD_TEMPLATE = """<!DOCTYPE html>
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

        /* PPE Violations Chart */
        .chart-container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .chart-container h3 {
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 16px;
        }
        .chart-img {
            max-width: 100%;
            height: auto;
        }
        
        /* Recent Alerts Section */
        .alerts-container {
            margin-top: 30px;
        }
        .alert-item {
            display: flex;
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .alert-thumbnail {
            width: 120px;
            height: 90px;
            object-fit: cover;
            border-radius: 8px;
            margin-right: 15px;
        }
        .alert-details {
            flex: 1;
        }
        .alert-title {
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .alert-description {
            font-size: 13px;
            color: #666;
            margin-bottom: 8px;
        }
        .alert-tags {
            display: flex;
            gap: 8px;
        }
        .alert-tag {
            background-color: #f1f1f1;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .alert-time {
            margin-left: auto;
            font-size: 12px;
            color: #666;
            flex-shrink: 0;
            align-self: flex-start;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-logo">
                <div class="header-icon">⚙️</div>
                <div class="header-title">Acme Corp - Warehouse Safety Dashboard</div>
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
                                    <circle cx="70" cy="70" r="60" fill="none" stroke="#4CAF50" stroke-width="10" stroke-dasharray="377" stroke-dashoffset="{{ dashoffset }}"/>
                                </svg>
                                <div class="score-value">{{ compliance_score }}</div>
                            </div>
                            <div style="flex: 1;">
                                <div class="score-title">PPE Compliance Score</div>
                                
                                <div class="score-details">
                                    <div class="score-item">
                                        <div class="score-item-label">Helmet</div>
                                        <div class="score-item-value">{{ helmet_score }}</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: {{ helmet_score }}%; background-color: {{ helmet_color }};"></div>
                                    </div>
                                    
                                    <div class="score-item">
                                        <div class="score-item-label">Safety Vest</div>
                                        <div class="score-item-value">{{ vest_score }}</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: {{ vest_score }}%; background-color: {{ vest_color }};"></div>
                                    </div>
                                    
                                    <div class="score-item">
                                        <div class="score-item-label">Gloves</div>
                                        <div class="score-item-value">{{ gloves_score }}</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: {{ gloves_score }}%; background-color: {{ gloves_color }};"></div>
                                    </div>
                                    
                                    <div class="score-item">
                                        <div class="score-item-label">Safety Goggles</div>
                                        <div class="score-item-value">{{ goggles_score }}</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: {{ goggles_score }}%; background-color: {{ goggles_color }};"></div>
                                    </div>
                                    
                                    <div class="score-item">
                                        <div class="score-item-label">Boots</div>
                                        <div class="score-item-value">{{ boots_score }}</div>
                                    </div>
                                    <div class="score-item-bar">
                                        <div class="score-item-fill" style="width: {{ boots_score }}%; background-color: {{ boots_color }};"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="section-header">
                    <div class="section-title">Recent PPE Violations</div>
                    <a href="#" class="view-all">View All</a>
                </div>
                
                <div class="videos-container">
                    {% for alert in recent_alerts[:4] %}
                    <div class="video-card">
                        <img src="/api/alert/{{ alert.filename }}" onerror="this.src='/api/placeholder/180/100'" alt="Violation thumbnail" class="video-thumbnail">
                        <div class="video-details">
                            <div class="video-title">{{ alert.violations[0].type if alert.violations else 'PPE Violation' }}</div>
                            <div class="video-info">
                                <span>{{ alert.location if alert.location else 'Warehouse' }}</span>
                                <span>{{ alert.time_ago }}</span>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                <div class="chart-container">
                    <h3>Violations Over Time</h3>
                    <img src="data:image/png;base64,{{ violations_chart }}" alt="Violations chart" class="chart-img">
                </div>
                
                <div class="chart-container">
                    <h3>Missing Equipment Types</h3>
                    <img src="data:image/png;base64,{{ equipment_chart }}" alt="Equipment chart" class="chart-img">
                </div>
                
                <div class="alerts-container">
                    <div class="section-header">
                        <div class="section-title">Recent Alerts</div>
                        <div class="incidents-count">{{ alert_count }}</div>
                    </div>
                    
                    {% for alert in recent_alerts %}
                    <div class="alert-item">
                        <img src="/api/alert/{{ alert.filename }}" onerror="this.src='/api/placeholder/120/90'" alt="Alert thumbnail" class="alert-thumbnail">
                        <div class="alert-details">
                            <div class="alert-title">{{ alert.violations[0].type if alert.violations else 'PPE Violation' }}</div>
                            <div class="alert-description">
                                {% if alert.violations %}
                                Worker missing: {{ ', '.join(alert.violations[0].missing_equipment) }}
                                {% else %}
                                PPE compliance violation detected
                                {% endif %}
                            </div>
                            <div class="alert-tags">
                                {% for equipment in alert.violations[0].missing_equipment if alert.violations %}
                                <div class="alert-tag">{{ equipment.replace('_', ' ').title() }}</div>
                                {% endfor %}
                            </div>
                        </div>
                        <div class="alert-time">{{ alert.time_ago }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="activity-sidebar">
                <div class="activity-card">
                    <div class="activity-title">Total Violations Today</div>
                    <div class="activity-count">{{ today_count }}</div>
                    <div class="activity-subtitle">{{ today_percentage }}% change from yesterday</div>
                </div>
                
                <div class="activity-card">
                    <div class="activity-title">Compliance Rate</div>
                    <div class="activity-count">{{ compliance_rate }}%</div>
                    <div class="activity-subtitle">Last 7 days</div>
                </div>
                
                <div class="activity-list">
                    <div class="activity-list-title">System Activity</div>
                    
                    {% for activity in system_activities %}
                    <div class="activity-item">
                        <div class="activity-icon">{{ activity.icon }}</div>
                        <div class="activity-content">
                            <div class="activity-text">{{ activity.text }}</div>
                            <div class="activity-time">{{ activity.time }}</div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@dashboard_bp.route('/')
def index():
    """Display the main dashboard"""
    try:
        # Load violation history
        try:
            with open(current_app.config['HISTORY_FILE'], 'r') as f:
                violation_history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create empty history file if not exists
            violation_history = []
            os.makedirs(os.path.dirname(current_app.config['HISTORY_FILE']), exist_ok=True)
            with open(current_app.config['HISTORY_FILE'], 'w') as f:
                json.dump(violation_history, f)
                
        # Generate charts
        violations_chart = generate_violation_chart(violation_history)
        equipment_chart = generate_equipment_chart(violation_history)
        
        # Process recent alerts
        recent_alerts = sorted(violation_history, key=lambda x: x.get('timestamp', 0), reverse=True)[:10]
        
        # Add relative time to alerts
        current_time = time.time()
        for alert in recent_alerts:
            timestamp = alert.get('timestamp', current_time)
            time_diff = current_time - timestamp
            
            if time_diff < 60:
                alert['time_ago'] = "Just now"
            elif time_diff < 3600:
                mins = int(time_diff // 60)
                alert['time_ago'] = f"{mins} min{'s' if mins != 1 else ''} ago"
            elif time_diff < 86400:
                hours = int(time_diff // 3600)
                alert['time_ago'] = f"{hours} hr{'s' if hours != 1 else ''} ago"
            else:
                days = int(time_diff // 86400)
                alert['time_ago'] = f"{days} day{'s' if days != 1 else ''} ago"
        
        # Calculate compliance scores
        equipment_types = {
            'helmet': {'score': 0, 'total': 0},
            'safety_vest': {'score': 0, 'total': 0},
            'gloves': {'score': 0, 'total': 0},
            'safety_goggles': {'score': 0, 'total': 0},
            'safety_boots': {'score': 0, 'total': 0}
        }
        
        # Count last 7 days for compliance metrics
        week_ago = current_time - (7 * 86400)
        recent_violations = [v for v in violation_history if v.get('timestamp', 0) >= week_ago]
        
        total_detections = 0
        total_violations = 0
        
        for entry in recent_violations:
            if 'stats' in entry:
                if 'total_detections' in entry['stats']:
                    total_detections += entry['stats']['total_detections']
                if 'violations' in entry['stats']:
                    total_violations += entry['stats']['violations']
                    
            for violation in entry.get('violations', []):
                missing = violation.get('missing_equipment', [])
                
                # Update equipment stats
                for eq_type in equipment_types:
                    if eq_type in missing or eq_type.replace('_', ' ') in missing:
                        equipment_types[eq_type]['total'] += 1
                    else:
                        equipment_types[eq_type]['score'] += 1
                        equipment_types[eq_type]['total'] += 1
        
        # Calculate scores and colors
        for eq_type in equipment_types:
            if equipment_types[eq_type]['total'] > 0:
                equipment_types[eq_type]['score'] = int((equipment_types[eq_type]['score'] / equipment_types[eq_type]['total']) * 100)
            else:
                equipment_types[eq_type]['score'] = 100  # Default to 100% if no data
                
            # Determine color based on score
            score = equipment_types[eq_type]['score']
            if score < 30:
                equipment_types[eq_type]['color'] = "#ff6b6b"  # Red
            elif score < 50:
                equipment_types[eq_type]['color'] = "#ff9f43"  # Orange
            elif score < 70:
                equipment_types[eq_type]['color'] = "#feca57"  # Yellow
            elif score < 90:
                equipment_types[eq_type]['color'] = "#1dd1a1"  # Light green
            else:
                equipment_types[eq_type]['color'] = "#10ac84"  # Dark green
        
        # Calculate overall compliance score
        if total_detections > 0:
            compliance_score = int(((total_detections - total_violations) / total_detections) * 100)
            compliance_rate = compliance_score
        else:
            compliance_score = 85  # Default value if no data
            compliance_rate = 85
        
        # Calculate dashboard offset (for circular gauge)
        dashoffset = 377 - ((compliance_score / 100) * 377)
        
        # Count today's violations
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        today_count = len([v for v in violation_history if v.get('timestamp', 0) >= today_start])
        
        # Calculate percentage change from yesterday
        yesterday_start = today_start - 86400
        yesterday_count = len([v for v in violation_history if yesterday_start <= v.get('timestamp', 0) < today_start])
        
        if yesterday_count > 0:
            today_percentage = int(((today_count - yesterday_count) / yesterday_count) * 100)
        else:
            today_percentage = 0
            
        # Generate system activities
        system_activities = [
            {
                'icon': '🔔',
                'text': 'System detected 3 workers without proper PPE in Zone B.',
                'time': '10 minutes ago'
            },
            {
                'icon': '🛠️',
                'text': 'Daily system maintenance completed.',
                'time': '1 hour ago'
            },
            {
                'icon': '📊',
                'text': 'Weekly safety report generated and emailed to management.',
                'time': '3 hours ago'
            },
            {
                'icon': '🏆',
                'text': 'Zone A achieved 100% PPE compliance for the week.',
                'time': '5 hours ago'
            },
            {
                'icon': '⚙️',
                'text': 'Camera #12 in loading area recalibrated.',
                'time': '6 hours ago'
            }
        ]
        
        # Render template with data
        return render_template_string(DASHBOARD_TEMPLATE, 
            violations_chart=violations_chart,
            equipment_chart=equipment_chart,
            recent_alerts=recent_alerts,
            alert_count=len(violation_history),
            today_count=today_count,
            today_percentage=today_percentage,
            compliance_rate=compliance_rate,
            compliance_score=compliance_score,
            dashoffset=dashoffset,
            system_activities=system_activities,
            helmet_score=equipment_types['helmet']['score'],
            helmet_color=equipment_types['helmet']['color'],
            vest_score=equipment_types['safety_vest']['score'],
            vest_color=equipment_types['safety_vest']['color'],
            gloves_score=equipment_types['gloves']['score'],
            gloves_color=equipment_types['gloves']['color'],
            goggles_score=equipment_types['safety_goggles']['score'],
            goggles_color=equipment_types['safety_goggles']['color'],
            boots_score=equipment_types['safety_boots']['score'],
            boots_color=equipment_types['safety_boots']['color']
        )
        
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return f"Error rendering dashboard: {str(e)}", 500

@dashboard_bp.route('/stats')
def stats():
    """Display more detailed statistics"""
    try:
        # Load violation history
        with open(current_app.config['HISTORY_FILE'], 'r') as f:
            violation_history = json.load(f)
            
        # Load system stats
        try:
            with open(current_app.config['STATS_FILE'], 'r') as f:
                stats = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            stats = {
                "started_at": time.time(),
                "total_processed": 0,
                "violations_detected": 0,
                "cameras_online": 8,
                "system_status": "operational"
            }
        
        # Here you would generate more detailed statistics
        # This is a placeholder for a more detailed stats page
        return render_template('stats.html', 
            stats=stats,
            violation_count=len(violation_history)
        )
    
    except Exception as e:
        logger.error(f"Error rendering stats page: {e}")
        return f"Error rendering stats page: {str(e)}", 500
