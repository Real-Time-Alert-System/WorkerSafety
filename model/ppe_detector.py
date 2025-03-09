# model/ppe_detector.py
import cv2
import numpy as np
import os
import torch
from ultralytics import YOLO
import time
from datetime import datetime

class PPEDetector:
    def __init__(self):
        # Paths to model files
        self.model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weights')
        self.model_path = os.path.join(self.model_dir, 'yolov8s.pt')
        
        # Ensure weights directory exists
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Download YOLOv8s if it doesn't exist (first run)
        if not os.path.exists(self.model_path):
            print("Downloading YOLOv8s model for the first time...")
            # Either download manually or let YOLO handle it
            self.model = YOLO('yolov8s.pt')
            self.model.save(self.model_path)
        else:
            # Load the model
            self.model = YOLO(self.model_path)
        
        # Define class mapping for PPE items (YOLOv8 COCO classes relevant to PPE)
        # We'll map standard YOLO classes to PPE items where appropriate
        self.ppe_mapping = {
            0: 'person',  # Person detection is useful for associating PPE with individuals
            38: 'safety_vest',  # Map 'sports ball' to 'safety_vest' for demonstration
            44: 'helmet',  # Map 'bottle' to 'helmet' for demonstration
            56: 'gloves',  # Map 'chair' to 'gloves' for demonstration
            46: 'safety_goggles',  # Map 'wine glass' to 'safety_goggles' for demonstration
            65: 'mask'    # Map 'bed' to 'mask' for demonstration
        }
        
        # In a production environment, you should train a custom YOLOv8 model on PPE data
        # The above mapping is just for demonstration purposes
        
        # Define required PPE for different areas
        self.area_requirements = {
            'construction': ['helmet', 'safety_vest', 'gloves'],
            'chemical': ['safety_goggles', 'gloves', 'mask'],
            'general': ['safety_vest'],
            'welding': ['helmet', 'gloves', 'safety_goggles'],
            'default': ['helmet', 'safety_vest']
        }
        
        # Create alerts directory in parent directory if it doesn't exist
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
        self.alerts_dir = os.path.join(parent_dir, 'alerts')
        os.makedirs(self.alerts_dir, exist_ok=True)
        
        print("PPE Detector initialized with YOLOv8")
        
    def detect(self, image, area_type='default'):
        """
        Detect PPE violations in the image
        
        Args:
            image: numpy array of the image
            area_type: type of work area to determine required PPE
            
        Returns:
            dictionary containing:
                - detections: list of all PPE equipment detected
                - violations: list of missing PPE equipment
        """
        # Get required PPE for this area
        required_ppe = self.get_required_ppe(area_type)
        
        # Run YOLOv8 detection
        results = self.model(image, conf=0.25)  # Lower confidence threshold for PPE detection
        
        # Process results
        detections = []
        found_ppe = set()
        persons = []
        
        # First, find all persons
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0].item())
                conf = box.conf[0].item()
                xyxy = box.xyxy[0].tolist()  # Convert to [x1, y1, x2, y2] format
                
                # Store person detections for later use
                if cls_id == 0:  # Person class
                    x1, y1, x2, y2 = map(int, xyxy)
                    persons.append({
                        'bbox': [x1, y1, x2-x1, y2-y1],  # Convert to [x, y, w, h] format
                        'ppe_found': set()
                    })
        
        # Then process PPE detections
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0].item())
                conf = box.conf[0].item()
                xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                
                # Skip if not a PPE class we're interested in
                if cls_id not in self.ppe_mapping:
                    continue
                    
                ppe_type = self.ppe_mapping[cls_id]
                if ppe_type == 'person':
                    continue  # Already processed persons
                
                x1, y1, x2, y2 = map(int, xyxy)
                
                # For each PPE detection, find the closest person and associate it
                if persons:
                    ppe_center = [(x1 + x2) / 2, (y1 + y2) / 2]
                    min_dist = float('inf')
                    closest_person = None
                    
                    for i, person in enumerate(persons):
                        p_x = person['bbox'][0] + person['bbox'][2] / 2
                        p_y = person['bbox'][1] + person['bbox'][3] / 2
                        dist = ((ppe_center[0] - p_x) ** 2 + (ppe_center[1] - p_y) ** 2) ** 0.5
                        
                        if dist < min_dist:
                            min_dist = dist
                            closest_person = i
                    
                    # Only associate if reasonably close
                    if min_dist < 200:  # This threshold may need adjustment
                        persons[closest_person]['ppe_found'].add(ppe_type)
                        found_ppe.add(ppe_type)
                
                detection = {
                    'type': ppe_type,
                    'confidence': conf,
                    'bbox': [x1, y1, x2-x1, y2-y1]  # Convert to [x, y, w, h] format
                }
                detections.append(detection)
        
        # Check for violations (missing required PPE)
        violations = []
        for i, person in enumerate(persons):
            missing_ppe = set(required_ppe) - person['ppe_found']
            
            for ppe_type in missing_ppe:
                violation = {
                    'type': ppe_type,
                    'bbox': person['bbox'],
                    'message': f"Missing {ppe_type}"
                }
                violations.append(violation)
        
        # Save violation image if any violations detected
        if violations:
            self.save_violation_image(image, violations, area_type)
        
        return {
            'detections': detections,
            'violations': violations
        }
    
    def save_violation_image(self, image, violations, area_type):
        """
        Save violation image to alerts folder with annotations
        
        Args:
            image: numpy array of the image
            violations: list of violations detected
            area_type: type of work area
        
        Returns:
            path to saved image
        """
        # Create a copy of the image for annotations
        annotated_img = image.copy()
        
        # Draw bounding boxes and labels for each violation
        for violation in violations:
            bbox = violation['bbox']
            ppe_type = violation['type']
            
            x, y, w, h = bbox
            
            # Draw red rectangle for violation
            cv2.rectangle(annotated_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # Add text label
            text = f"Missing: {ppe_type}"
            cv2.putText(annotated_img, text, (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"violation_{area_type}_{timestamp}.jpg"
        filepath = os.path.join(self.alerts_dir, filename)
        
        # Save the annotated image
        cv2.imwrite(filepath, annotated_img)
        
        print(f"Violation saved to {filepath}")
        return filepath
        
    def get_required_ppe(self, area_type):
        """
        Get the required PPE for a specific work area type
        
        Args:
            area_type: string indicating the type of work area
            
        Returns:
            list of required PPE equipment
        """
        return self.area_requirements.get(area_type, self.area_requirements['default'])
