# Worker Safety Detection System

An AI-powered system that monitors workplace safety compliance through computer vision. This system detects workers without proper safety equipment (helmets, safety goggles, safety vests) and sends real-time alerts to supervisors.

## Features

- **Real-time Detection**: Monitors video feeds to identify safety violations in real-time
- **Multi-Equipment Detection**: Detects absence of helmets, safety goggles, safety vests, and more
- **Telegram Notifications**: Sends instant alerts with violation screenshots
- **Web Dashboard**: Visual interface to monitor compliance stats and review alerts
- **API Integration**: RESTful API for integration with other systems
- **False-Positive Reduction**: Requires violations to persist across multiple frames to reduce false alerts
- **Regions of Interest**: Define specific areas to monitor within the video feed
- **Configurable**: Adjust detection confidence, notification cooldown, and more

## System Architecture

The system consists of two main components:

1. **Detection System** (`detection_mvp.py`): Processes video feeds, detects safety violations, and sends alerts
2. **Notification API** (`notification_api.py`): Serves dashboard, stores alert history, and provides APIs

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Webcam or video feed
- Telegram bot (for notifications)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/worker-safety-detection.git
   cd worker-safety-detection
   ```

2. Run the setup script:
   ```
   python setup.py --all
   ```
   
   This will:
   - Install required dependencies
   - Create a configuration file
   - Download the YOLO model
   - Create necessary folders

3. Update your Telegram bot information in `config.json`

### Usage

1. Start the notification API server:
   ```
   python notification_api.py
   ```

2. Start the detection system:
   ```
   python detection_mvp.py
   ```

3. Access the dashboard at `http://localhost:5000`

## Configuration

Edit `config.json` to customize system behavior:

```json
{
  "model_path": "yolov8x.pt",              // Path to YOLO model
  "confidence_threshold": 0.45,            // Detection confidence threshold (0-1)
  "notification_cooldown": 60,             // Seconds between notifications
  "violation_persistence": 5,              // Frames a violation must persist
  "regions_of_interest": [],               // Define specific regions to monitor
  "api_base_url": "http://localhost:5000", // Base URL for API
  "alert_folder": "alerts",                // Folder to store alert images
  "notification_services": {
    "telegram": {
      "enabled": true,                     // Enable/disable Telegram
      "bot_token": "YOUR_BOT_TOKEN",       // Telegram bot token
      "chat_id": "YOUR_CHAT_ID"            // Telegram chat ID
    },
    "webhook": {
      "enabled": false,                    // Enable/disable webhook
      "url": "https://your-webhook.com"    // Webhook URL
    }
  },
  "video_source": 0,                       // Camera index or video path
  "record_violations": true,               // Save violation screenshots
  "display_feed": true                     // Show live video feed
}
```

## API Endpoints

- `GET /` - Web dashboard
- `GET /alert/[filename]` - Serve alert images
- `GET /api/stats` - Get system statistics
- `GET /api/alerts` - Get alert history
- `POST /api/alert` - Receive new alerts
- `GET /health` - Health check endpoint

## Customizing Detection

The system is configured to detect:
- Helmets (hard hats)
- Safety goggles (eye protection)
- Safety vests (high-visibility vests)
- Gloves (optional)

To change which equipment is required or to add new equipment types, modify the `SAFETY_EQUIPMENT` dictionary in `detection_mvp.py`.

## Training Custom Models

For more accurate detection, you can train your own custom YOLOv8 model:

1. Collect and label images of your specific safety equipment
2. Train using Ultralytics YOLOv8:
   ```
   yolo train model=yolov8n.pt data=your_dataset.yaml epochs=100
   ```
3. Update the model path in your config file

## Hackathon Enhancements

This system includes several enhancements that make it hackathon-ready:

1. **Interactive Dashboard**: Visual monitoring of safety compliance
2. **Analytics & Charts**: Visualize violation trends and equipment types
3. **Multi-Equipment Detection**: Beyond just helmets
4. **Configurable Zones**: Set up specific monitoring areas
5. **False-Positive Reduction**: Persistence tracking reduces false alarms
6. **Multi-Channel Notifications**: Supports Telegram and webhooks
7. **API-First Design**: Easy integration with other systems
8. **Comprehensive Documentation**: Well-documented for judges and users

## License

MIT License
