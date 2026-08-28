import os
import base64
import json
import logging
import cv2
import numpy as np
from flask import Flask, request, jsonify
from ultralytics import YOLO
from dotenv import load_dotenv

# Load env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_service")

app = Flask(__name__)

# Load model path from env or use default
MODEL_PATH = os.environ.get("MODEL_PATH", "../models/yolov8s_ppe_custom.pt")
model = None

try:
    # Resolve relative path if needed
    resolved_path = MODEL_PATH
    if not os.path.isabs(MODEL_PATH):
        resolved_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", MODEL_PATH))
        
    if os.path.exists(resolved_path):
        model = YOLO(resolved_path)
        logger.info(f"YOLOv8 Model loaded successfully from {resolved_path}")
    else:
        logger.error(f"YOLOv8 Model file not found at: {resolved_path}")
except Exception as e:
    logger.exception(f"Failed to load YOLOv8 model: {e}")

# Load default class mapping and violation classes
try:
    default_mapping = json.loads(os.environ.get("PPE_CLASS_MAPPING", "{}"))
    PPE_CLASS_MAPPING = {int(k): v for k, v in default_mapping.items()}
except Exception:
    PPE_CLASS_MAPPING = {}

try:
    VIOLATION_CLASSES = json.loads(os.environ.get("VIOLATION_CLASSES", "[]"))
except Exception:
    VIOLATION_CLASSES = []

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    if model is None:
        return jsonify({"error": "YOLO model is not loaded on server."}), 500
    
    if "image" not in request.files:
        return jsonify({"error": "No image file provided in request."}), 400
    
    file = request.files["image"]
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return jsonify({"error": "Invalid image file format."}), 400

    # Parse optional mapping and violations from the request
    mapping_str = request.form.get("class_mapping")
    violations_str = request.form.get("violation_classes")
    conf_val = float(request.form.get("confidence", 0.35))

    mapping = PPE_CLASS_MAPPING
    if mapping_str:
        try:
            req_mapping = json.loads(mapping_str)
            mapping = {int(k): v for k, v in req_mapping.items()}
        except Exception:
            pass

    violations = VIOLATION_CLASSES
    if violations_str:
        try:
            violations = json.loads(violations_str)
        except Exception:
            pass

    annotated_img = img.copy()
    detections = []
    
    try:
        results = model(img, conf=conf_val)
        if results and results[0].boxes is not None:
            boxes = results[0].boxes
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())
                label = mapping.get(cls_id, f"Unknown_{cls_id}")
                confidence = float(boxes.conf[i].item())
                bbox = boxes.xyxy[i].tolist() # [x1, y1, x2, y2]
                
                is_violation = label in violations
                detections.append({
                    "class_id": cls_id,
                    "label": label,
                    "confidence": confidence,
                    "bbox": bbox,
                    "is_violation": is_violation
                })

                # Draw bounding box and label
                x1, y1, x2, y2 = map(int, bbox)
                color = (0, 0, 255) if is_violation else (0, 255, 0) # Red for violation, Green for okay
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    annotated_img,
                    f"{label} ({confidence:.2f})",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )
                
        # Encode annotated image as base64
        _, buffer = cv2.imencode(".jpg", annotated_img)
        img_base64 = base64.b64encode(buffer).decode("utf-8")
        
        return jsonify({
            "detections": detections,
            "image": img_base64
        })

    except Exception as e:
        logger.exception(f"Error during model inference: {e}")
        return jsonify({"error": f"Inference error: {str(e)}"}), 500
if __name__ == "__main__":
    port = int(os.environ.get("AI_PORT", 8000))
    logger.info(f"Starting AI service on port {port}")
    try:
        from waitress import serve
        logger.info("Using Waitress production WSGI server")
        serve(app, host="0.0.0.0", port=port)
    except ImportError:
        logger.info("Waitress not found. Falling back to Flask development server")
        app.run(host="0.0.0.0", port=port, debug=False)
