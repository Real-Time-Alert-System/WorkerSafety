
import cv2
import time
import requests
from ultralytics import YOLO
# --- Configuration ---
MODEL_PATH = "yolov8x.pt"  # Use YOLOv8x for highest accuracy (CPU mode will be slower)
CONFIDENCE_THRESHOLD = 0.5
NOTIFICATION_COOLDOWN = 60  # seconds
# Replace these with your Telegram Bot credentials
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # e.g., "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"      # e.g., "987654321"
# The base URL of the API endpoint that serves alert images.
# For local testing, you might use: "http://localhost:5000"
API_BASE_URL = "http://:5000"
# --- Notification Function ---
def send_notification(screenshot, detection_details):
    """
    Save the screenshot, then push a notification via Telegram with a link to the image.
    """
    timestamp = int(time.time())
    screenshot_filename = f"alert_{timestamp}.jpg"
    cv2.imwrite(screenshot_filename, screenshot)
    # Construct the URL where the image can be viewed via our Flask API endpoint.
    image_url = f"{API_BASE_URL}/alert/{screenshot_filename}"
    message = f"ALERT: {detection_details}. View image: {image_url}"
    # Send a Telegram message.
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(telegram_url, data=payload)
    if response.status_code == 200:
        print(f"Notification sent: {message}")
    else:
        print("Failed to send notification:", response.text)
# --- Initialize Model and Video Capture ---
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(0)  # Change to video file path if needed
last_notification_time = 0
print("Starting detection. Press 'q' to exit.")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Run inference on the frame
    results = model(frame, conf=CONFIDENCE_THRESHOLD)
    detections = results[0].boxes.data.cpu().numpy() if results and results[0].boxes is not None else []
    persons = []
    helmets = []
    goggles = []
    names = model.model.names  # Mapping: e.g., {0: 'person', 1: 'helmet', 2: 'safety goggles'}
    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        label = names.get(int(cls), "").lower()
        bbox = (int(x1), int(y1), int(x2), int(y2))
        if label == "person":
            persons.append(bbox)
        elif label == "helmet":
            helmets.append(bbox)
        elif label in ["safety goggles", "goggles"]:
            goggles.append(bbox)
    violation_found = False
    # Check each person for the presence of a helmet and safety goggles
    for (px1, py1, px2, py2) in persons:
        person_mid = py1 + (py2 - py1) // 2
        has_helmet = any(hx1 >= px1 and hx2 <= px2 and hy2 < person_mid for (hx1, hy1, hx2, hy2) in helmets)
        has_goggles = any(gx1 >= px1 and gx2 <= px2 and gy2 < person_mid for (gx1, gy1, gx2, gy2) in goggles)
        
        if not has_helmet or not has_goggles:
            violation_found = True
            # Mark violation on the frame
            cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 0, 255), 2)
            cv2.putText(frame, "Violation", (px1, py1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    current_time = time.time()
    if violation_found and (current_time - last_notification_time > NOTIFICATION_COOLDOWN):
        send_notification(frame, "Detected lack of helmet or safety goggles")
        last_notification_time = current_time
    cv2.imshow("Safety Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()


notification_api.py
from flask import Flask, send_from_directory, abort
import os
app = Flask(__name__)
# Folder where alert images are saved (in this example, the current directory)
ALERT_FOLDER = os.path.abspath(".")
@app.route("/alert/")
def serve_alert_image(filename):
    # Ensure that the file exists in the alert folder
    file_path = os.path.join(ALERT_FOLDER, filename)
    if os.path.exists(file_path):
        return send_from_directory(ALERT_FOLDER, filename)
    else:
        abort(404, description="File not found.")
if **name** == "__main__":
    app.run(host="0.0.0.0", port=5000)
