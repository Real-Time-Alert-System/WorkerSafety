import os
import json
import argparse
import subprocess
import sys

# Configuration template
CONFIG_TEMPLATE = {
    "model_path": "yolov8x.pt",
    "confidence_threshold": 0.45,
    "notification_cooldown": 60,
    "violation_persistence": 5,
    "regions_of_interest": [],
    "api_base_url": "http://localhost:5000",
    "alert_folder": "alerts",
    "notification_services": {
        "telegram": {
            "enabled": True,
            "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
            "chat_id": "YOUR_TELEGRAM_CHAT_ID"
        },
        "webhook": {
            "enabled": False,
            "url": "https://your-webhook-endpoint.com/safety-alerts"
        }
    },
    "video_source": 0,
    "record_violations": True,
    "display_feed": True
}

def create_config_file():
    """Create a config.json file with default values"""
    if os.path.exists("config.json"):
        print("Config file already exists. Do you want to overwrite it? (y/n)")
        choice = input().lower()
        if choice != 'y':
            print("Exiting without modifying config.json")
            return
    
    print("Creating config.json file...")
    # Ask for Telegram bot token and chat ID
    print("\nTelegram Notification Settings:")
    enable_telegram = input("Enable Telegram notifications? (y/n): ").lower() == 'y'
    
    if enable_telegram:
        bot_token = input("Enter your Telegram Bot Token: ")
        chat_id = input("Enter your Telegram Chat ID: ")
        
        CONFIG_TEMPLATE["notification_services"]["telegram"]["enabled"] = True
        CONFIG_TEMPLATE["notification_services"]["telegram"]["bot_token"] = bot_token
        CONFIG_TEMPLATE["notification_services"]["telegram"]["chat_id"] = chat_id
    else:
        CONFIG_TEMPLATE["notification_services"]["telegram"]["enabled"] = False
    
    # Ask for video source
    print("\nVideo Source Settings:")
    print("0 = Default Webcam")
    print("1, 2, etc. = Alternative Camera Indexes")
    print("rtsp://... = RTSP Stream URL")
    print("path/to/video.mp4 = Video File")
    video_source = input("Enter your video source: ")
    
    # Convert to int if it's a number
    if video_source.isdigit():
        CONFIG_TEMPLATE["video_source"] = int(video_source)
    else:
        CONFIG_TEMPLATE["video_source"] = video_source
    
    # Write the config file
    with open("config.json", "w") as f:
        json.dump(CONFIG_TEMPLATE, f, indent=4)
    
    print("Config file created successfully!")

def install_dependencies():
    """Install required Python packages"""
    print("Installing required dependencies...")
    
    requirements = [
        "opencv-python",
        "ultralytics",
        "flask",
        "requests",
        "pandas",
        "matplotlib",
        "numpy"
    ]
    
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + requirements)
    print("Dependencies installed successfully!")

def download_yolo_model():
    """Download YOLOv8x model if it doesn't exist"""
    model_path = CONFIG_TEMPLATE["model_path"]
    if os.path.exists(model_path):
        print(f"YOLO model already exists at {model_path}")
        return
    
    print(f"Downloading YOLO model ({model_path})...")
    try:
        from ultralytics import YOLO
        model = YOLO(model_path)
        print("Model downloaded successfully!")
    except Exception as e:
        print(f"Error downloading model: {e}")

def create_folder_structure():
    """Create necessary folders"""
    folders = ["alerts"]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")

def main():
    parser = argparse.ArgumentParser(description="Setup Safety Detection System")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--config", action="store_true", help="Create config file")
    parser.add_argument("--model", action="store_true", help="Download YOLO model")
    parser.add_argument("--all", action="store_true", help="Perform all setup steps")
    
    args = parser.parse_args()
    
    # If no arguments provided, assume --all
    if not (args.install or args.config or args.model or args.all):
        args.all = True
    
    print("===== Worker Safety Detection System Setup =====")
    
    if args.install or args.all:
        install_dependencies()
    
    if args.config or args.all:
        create_config_file()
    
    if args.model or args.all:
        download_yolo_model()
    
    create_folder_structure()
    
    print("\nSetup completed! You can start the system with:")
    print("1. Start the notification API server: python backend/notification-api.py")
    print("2. Start the detection system: python model/detection_mvp.py")
    print("\nAccess the dashboard at http://localhost:5000")

if __name__ == "__main__":
    main()

