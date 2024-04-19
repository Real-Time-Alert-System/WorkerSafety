import datetime
import logging
import os
import time

import cv2
from flask import current_app
from ultralytics import YOLO

from .. import database as db
from .notification_service import notify_violation

logger = logging.getLogger(__name__)


class DetectionService:
    def __init__(self):
        self.model = None
        self.load_model()
        self.ppe_class_mapping = current_app.config["PPE_CLASS_MAPPING"]
        self.violation_classes = current_app.config["VIOLATION_CLASSES"]
        self.area_requirements = current_app.config["AREA_REQUIREMENTS"]
        self.violation_image_folder = current_app.config["VIOLATION_IMAGE_FOLDER"]

        if not self.ppe_class_mapping:
            logger.warning(
                "PPE Class Mapping is empty. Detection results may be incorrect."
            )
        if not self.violation_classes:
            logger.warning(
                "Violation Classes list is empty. No violations may be flagged."
            )
        if not self.area_requirements:
            logger.warning("Area Requirements are not defined. Using default only.")

    def load_model(self):
        model_path = current_app.config["MODEL_PATH"]
        if not os.path.exists(model_path):
            logger.error(f"YOLO Model file not found at: {model_path}")
            self.model = None
            return
        try:
            self.model = YOLO(model_path)
            logger.info(f"YOLOv8 model loaded successfully from {model_path}")
        except Exception as e:
            logger.exception(f"Failed to load YOLO model from {model_path}: {e}")
            self.model = None

    def _determine_severity(self, equipment_type):
        if "NO-Hardhat" in equipment_type:
            return "high"
        if "NO-Mask" in equipment_type and "lab" in current_app.config.get(
            "AREA_REQUIREMENTS", {}
        ):  # Example context
            return "high"
        if "NO-Safety Vest" in equipment_type:
            return "medium"
        return "medium"

    def _save_violation_image(self, image, violation_details, location, area_type):
        """Saves annotated image and returns the relative path."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"violation_{location}_{area_type}_{timestamp}.jpg"
        absolute_filepath = os.path.join(self.violation_image_folder, filename)

        annotated_img = image.copy()
        # This needs refinement based on actual detection results structure
        for detail in violation_details:
            if "bbox" in detail and len(detail["bbox"]) == 4:
                x1, y1, x2, y2 = map(int, detail["bbox"])
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(
                    annotated_img,
                    f"Violation: {detail.get('type', 'Unknown')}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

        try:
            cv2.imwrite(absolute_filepath, annotated_img)
            logger.info(f"Violation image saved: {absolute_filepath}")
            relative_filepath = os.path.join("images", filename)
            return relative_filepath
        except Exception as e:
            logger.error(f"Error saving violation image {absolute_filepath}: {e}")
            return None

    def process_image(self, image_path, location="Unknown", area_type="default"):
        if not self.model:
            logger.error("Model not loaded. Cannot process image.")
            return {"error": "Model not loaded"}

        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image file: {image_path}")
                return {"error": "Failed to read image"}

            results = self.model(image, conf=0.35)

            detected_violations = []
            processed_frame_info = {"detections": [], "violations": []}

            if results and results[0].boxes is not None:
                boxes = results[0].boxes
                for i in range(len(boxes)):
                    cls_id = int(boxes.cls[i].item())
                    label = self.ppe_class_mapping.get(cls_id, f"Unknown_{cls_id}")
                    confidence = boxes.conf[i].item()
                    bbox_coords = boxes.xyxy[i].tolist()  # [x1, y1, x2, y2]

                    processed_frame_info["detections"].append(
                        {"label": label, "confidence": confidence, "bbox": bbox_coords}
                    )

                    if label in self.violation_classes:
                        severity = self._determine_severity(label)
                        violation_detail = {
                            "type": label,
                            "severity": severity,
                            "confidence": confidence,
                            "bbox": bbox_coords,
                            "timestamp": datetime.datetime.now(),
                        }
                        detected_violations.append(violation_detail)
                        processed_frame_info["violations"].append(violation_detail)

            if detected_violations:
                saved_image_path_relative = self._save_violation_image(
                    image, detected_violations, location, area_type
                )

                if saved_image_path_relative:
                    for violation in detected_violations:
                        db.add_violation(
                            timestamp=violation["timestamp"],
                            equipment_type=violation["type"],
                            image_path=saved_image_path_relative,
                            location=location,
                            area_type=area_type,
                            severity=violation["severity"],
                        )
                        notify_violation(
                            violation_type=violation["type"],
                            location=location,
                            area_type=area_type,
                            severity=violation["severity"],
                            image_path=saved_image_path_relative,
                        )
                else:
                    logger.error(
                        "Failed to save violation image, skipping DB logging and notification for this image."
                    )

            return processed_frame_info

        except Exception as e:
            logger.exception(f"Error processing image {image_path}: {e}")
            return {"error": str(e)}

    def process_video(self, video_path, location="Unknown", area_type="default"):
        if not self.model:
            logger.error("Model not loaded. Cannot process video.")
            return {"error": "Model not loaded", "total_violations": 0}

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Error opening video file: {video_path}")
            return {"error": "Could not open video file", "total_violations": 0}

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_step = max(1, int(fps if fps > 0 else 30))
        logger.info(
            f"Processing video: {video_path}, FPS: {fps:.2f}, Frame Step: {frame_step}"
        )

        total_violations_count = 0
        processed_frames = 0
        start_time = time.time()

        all_results = {
            "frames_analyzed": 0,
            "total_violations": 0,
            "violations_by_frame": [],
        }

        try:
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % frame_step == 0:
                    processed_frames += 1
                    frame_time = frame_idx / fps if fps > 0 else 0

                    frame_result = self.process_image_frame(
                        frame, location, area_type, frame_time
                    )

                    if frame_result.get("violations"):
                        num_violations_in_frame = len(frame_result["violations"])
                        total_violations_count += num_violations_in_frame
                        all_results["violations_by_frame"].append(
                            {
                                "frame_index": frame_idx,
                                "timestamp_sec": frame_time,
                                "violations": frame_result["violations"],
                            }
                        )

                frame_idx += 1

        except Exception as e:
            logger.exception(f"Error during video processing: {e}")
            all_results["error"] = str(e)
        finally:
            cap.release()

        end_time = time.time()
        processing_duration = end_time - start_time
        all_results["frames_analyzed"] = processed_frames
        all_results["total_violations"] = total_violations_count
        logger.info(
            f"Video processing finished. Analyzed {processed_frames} frames in {processing_duration:.2f}s. Found {total_violations_count} violations."
        )

        return all_results

    def process_image_frame(self, frame, location, area_type, frame_time_sec):
        """Processes a single video frame (similar to process_image but takes frame array)."""
        if not self.model:
            return {"error": "Model not loaded"}

        try:
            results = self.model(frame, conf=0.35)
            detected_violations = []
            processed_frame_info = {"detections": [], "violations": []}

            if results and results[0].boxes is not None:
                boxes = results[0].boxes
                for i in range(len(boxes)):
                    cls_id = int(boxes.cls[i].item())
                    label = self.ppe_class_mapping.get(cls_id, f"Unknown_{cls_id}")
                    confidence = boxes.conf[i].item()
                    bbox_coords = boxes.xyxy[i].tolist()

                    processed_frame_info["detections"].append(
                        {"label": label, "confidence": confidence, "bbox": bbox_coords}
                    )

                    if label in self.violation_classes:
                        severity = self._determine_severity(label)
                        violation_detail = {
                            "type": label,
                            "severity": severity,
                            "confidence": confidence,
                            "bbox": bbox_coords,
                            "timestamp": datetime.datetime.now(),
                            "frame_time_sec": frame_time_sec,
                        }
                        detected_violations.append(violation_detail)
                        processed_frame_info["violations"].append(violation_detail)

            if detected_violations:
                saved_image_path_relative = self._save_violation_image(
                    frame, detected_violations, location, area_type
                )
                if saved_image_path_relative:
                    for violation in detected_violations:
                        db.add_violation(
                            timestamp=violation["timestamp"],
                            equipment_type=violation["type"],
                            image_path=saved_image_path_relative,
                            location=location,
                            area_type=area_type,
                            severity=violation["severity"],
                        )
                        notify_violation(
                            violation_type=violation["type"],
                            location=location,
                            area_type=area_type,
                            severity=violation["severity"],
                            image_path=saved_image_path_relative,
                        )
                else:
                    logger.error(
                        "Failed to save violation image for frame, skipping DB/notification."
                    )

            return processed_frame_info

        except Exception as e:
            logger.exception(f"Error processing frame at ~{frame_time_sec:.2f}s: {e}")
            return {"error": str(e)}

    def process_live_stream_frame(
        self,
        frame,
        stream_url_label="LiveStream",
        area_type="default",
        frame_time_offset=0,
    ):
        """
        Processes a single frame from a live stream.
        This is very similar to process_image_frame but tailored for streams.
        Returns the annotated frame and any detected violations for this frame.
        """
        if not self.model:
            logger.error("Live stream: Model not loaded.")
            return frame, []
        """
        Processes a single frame from a live stream.
        This is very similar to process_image_frame but tailored for streams.
        Returns the annotated frame and any detected violations for this frame.
        """
        if not self.model:
            logger.error("Live stream: Model not loaded.")
            return frame, []

        annotated_frame = frame.copy()
        detected_violations_in_frame = []

        try:
            results = self.model(frame, conf=0.35)

            if results and results[0].boxes is not None:
                boxes = results[0].boxes
                for i in range(len(boxes)):
                    cls_id = int(boxes.cls[i].item())
                    label = self.ppe_class_mapping.get(cls_id, f"Unknown_{cls_id}")
                    confidence = boxes.conf[i].item()
                    bbox_coords = boxes.xyxy[i].tolist()
                    x1, y1, x2, y2 = map(int, bbox_coords)

                    color = (0, 255, 0)
                    if label in self.violation_classes:
                        color = (0, 0, 255)

                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(
                        annotated_frame,
                        f"{label} ({confidence:.2f})",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2,
                    )

                    if label in self.violation_classes:
                        severity = self._determine_severity(label)
                        violation_detail = {
                            "type": label,
                            "severity": severity,
                            "confidence": confidence,
                            "bbox": bbox_coords,
                            "timestamp": datetime.datetime.now(),
                            "stream_url": stream_url_label,
                            "frame_time_offset": frame_time_offset,
                        }
                        detected_violations_in_frame.append(violation_detail)

            if detected_violations_in_frame:
                # Save an image for the first detected violation in this batch of violations
                # To avoid saving too many images from a continuous stream
                # Cooldown for saving images from the same stream can be added
                saved_image_path_relative = self._save_violation_image(
                    frame, detected_violations_in_frame, stream_url_label, area_type
                )
                if saved_image_path_relative:
                    for violation in detected_violations_in_frame:
                        db.add_violation(
                            timestamp=violation["timestamp"],
                            equipment_type=violation["type"],
                            image_path=saved_image_path_relative,
                            location=stream_url_label,
                            area_type=area_type,
                            severity=violation["severity"],
                        )
                        notify_violation(
                            violation_type=violation["type"],
                            location=stream_url_label,
                            area_type=area_type,
                            severity=violation["severity"],
                            image_path=saved_image_path_relative,
                        )
                else:
                    logger.error(
                        f"Live stream ({stream_url_label}): Failed to save violation image for frame."
                    )

            return annotated_frame, detected_violations_in_frame

        except Exception as e:
            logger.exception(
                f"Live stream ({stream_url_label}): Error processing frame: {e}"
            )
            return frame, []

        annotated_frame = frame.copy()  # Work on a copy
        detected_violations_in_frame = []

        try:
            results = self.model(
                frame, conf=0.35
            )  # Use the original frame for detection

            if results and results[0].boxes is not None:
                boxes = results[0].boxes
                for i in range(len(boxes)):
                    cls_id = int(boxes.cls[i].item())
                    label = self.ppe_class_mapping.get(cls_id, f"Unknown_{cls_id}")
                    confidence = boxes.conf[i].item()
                    bbox_coords = boxes.xyxy[i].tolist()
                    x1, y1, x2, y2 = map(int, bbox_coords)

                    # Annotate the copied frame
                    color = (0, 255, 0)  # Green for all detections initially
                    if label in self.violation_classes:
                        color = (0, 0, 255)  # Red for violations

                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(
                        annotated_frame,
                        f"{label} ({confidence:.2f})",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2,
                    )

                    if label in self.violation_classes:
                        severity = self._determine_severity(label)
                        violation_detail = {
                            "type": label,
                            "severity": severity,
                            "confidence": confidence,
                            "bbox": bbox_coords,
                            "timestamp": datetime.datetime.now(),
                            "stream_url": stream_url_label,  # Identify the stream
                            "frame_time_offset": frame_time_offset,  # If keeping track
                        }
                        detected_violations_in_frame.append(violation_detail)

            if detected_violations_in_frame:
                # Save an image for the first detected violation in this batch of violations
                # To avoid saving too many images from a continuous stream
                # Cooldown for saving images from the same stream can be added
                saved_image_path_relative = self._save_violation_image(
                    frame, detected_violations_in_frame, stream_url_label, area_type
                )
                if saved_image_path_relative:
                    for violation in detected_violations_in_frame:
                        db.add_violation(
                            timestamp=violation["timestamp"],
                            equipment_type=violation["type"],
                            image_path=saved_image_path_relative,
                            location=stream_url_label,  # Use stream label as location
                            area_type=area_type,
                            severity=violation["severity"],
                        )
                        notify_violation(  # Notification service handles its own cooldown
                            violation_type=violation["type"],
                            location=stream_url_label,
                            area_type=area_type,
                            severity=violation["severity"],
                            image_path=saved_image_path_relative,
                        )
                else:
                    logger.error(
                        f"Live stream ({stream_url_label}): Failed to save violation image for frame."
                    )

            return annotated_frame, detected_violations_in_frame

        except Exception as e:
            logger.exception(
                f"Live stream ({stream_url_label}): Error processing frame: {e}"
            )
            return frame, []
