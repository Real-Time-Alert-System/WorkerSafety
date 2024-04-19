import logging
import os

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from . import database as db
from .models import Violation

# from .services.detection_service import detection_service # its global no import

main_bp = Blueprint("main", __name__)
logger = logging.getLogger(__name__)


@main_bp.before_request
@login_required
def before_request_auth():
    """Protects all routes in this blueprint."""
    pass


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@main_bp.route("/")
def index():
    """Serves the main upload page."""
    return render_template("index.html", title="PPE Detection Upload")


@main_bp.route("/upload", methods=["POST"])
def upload_and_process():
    """Handles file uploads and initiates processing."""
    if "file" not in request.files:
        flash("No file part in the request.", "error")
        return redirect(request.url)

    file = request.files["file"]
    location = request.form.get("location", "Default Site")
    area_type = request.form.get("area_type", "default")

    if file.filename == "":
        flash("No file selected for upload.", "warning")
        return redirect(url_for("main.index"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

        try:
            file.save(filepath)
            logger.info(
                f"File '{filename}' saved to '{filepath}'. Initiating processing."
            )

            # Determine file type and process
            _, extension = os.path.splitext(filename)
            extension = extension.lower()
            results = None

            # Access detection service via current_app
            detection_service = current_app.detection_service

            if extension in [".jpg", ".jpeg", ".png"]:
                results = detection_service.process_image(filepath, location, area_type)
                result_type = "image"
            elif extension in [".mp4", ".avi", ".mov", ".webm"]:
                results = detection_service.process_video(filepath, location, area_type)
                result_type = "video"
            else:
                flash("Unsupported file type.", "error")
                return redirect(url_for("main.index"))

            # Clean up uploaded file
            try:
                os.remove(filepath)
                logger.info(f"Cleaned up uploaded file: {filepath}")
            except OSError as e:
                logger.error(f"Error removing uploaded file {filepath}: {e}")

            # Check results and provide feedback
            if results and "error" in results:
                flash(f"Processing Error: {results['error']}", "error")
                return redirect(url_for("main.index"))

            violation_count = (
                results.get("total_violations", len(results.get("violations", [])))
                if result_type == "video"
                else len(results.get("violations", []))
            )

            if violation_count > 0:
                flash(
                    f"Processing complete. {violation_count} violation(s) detected and logged.",
                    "success",
                )
            else:
                flash("Processing complete. No violations detected.", "info")

            # Redirect to violations page to see the results
            return redirect(url_for("main.violations_log"))

        except Exception as e:
            logger.exception(f"Error during file upload or processing: {e}")
            flash("An unexpected error occurred during processing.", "danger")
            # Clean up partial uploads
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError:
                    pass
            return redirect(url_for("main.index"))

    else:
        flash("File type not allowed.", "warning")
        return redirect(url_for("main.index"))


@main_bp.route("/dashboard")
def dashboard():
    """Displays statistics and charts."""
    try:
        stats_data = db.get_violation_stats()
        if "error" in stats_data:
            flash(f"Error fetching statistics: {stats_data['error']}", "danger")
            # Provide empty data structure to avoid template errors
            stats_data = {
                "by_equipment": [],
                "by_severity": [],
                "by_location": [],
                "by_status": [],
                "daily_trend": [],
            }

        # Pass raw data to template for Chart.js
        return render_template("dashboard.html", title="Dashboard", stats=stats_data)
    except Exception as e:
        logger.exception("Error loading dashboard data.")
        flash("Could not load dashboard statistics.", "danger")
        # Pass empty data on general exception
        return render_template(
            "dashboard.html",
            title="Dashboard",
            stats={
                "by_equipment": [],
                "by_severity": [],
                "by_location": [],
                "by_status": [],
                "daily_trend": [],
            },
        )


@main_bp.route("/violations")
def violations_log():
    """Displays the list of recorded violations."""
    try:
        violations_raw = db.get_all_violations(limit=200)  # Get more for display
        # Map raw rows to Violation objects for easier template access
        violations = [
            Violation(
                id=row["id"],
                timestamp=row["timestamp"],
                equipment_type=row["equipment_type"],
                image_path=row["image_path"],
                location=row["location"],
                area_type=row["area_type"],
                severity=row["severity"],
                status=row["status"],
            )
            for row in violations_raw
        ]

        return render_template(
            "violations.html", title="Violation Log", violations=violations
        )
    except Exception as e:
        logger.exception("Error loading violations log.")
        flash("Could not load violation log.", "danger")
        return render_template("violations.html", title="Violation Log", violations=[])


@main_bp.route("/violations/update/<int:violation_id>", methods=["POST"])
@login_required
def update_violation_status_route(violation_id):
    """Updates the status of a specific violation."""
    new_status = request.form.get("status")
    if not new_status:
        flash("No status provided for update.", "warning")
        return redirect(url_for("main.violations_log"))

    try:
        success = db.update_violation_status(violation_id, new_status)
        if success:
            flash(
                f"Violation {violation_id} status updated to '{new_status}'.", "success"
            )
        else:
            flash(
                f"Failed to update status for violation {violation_id}. It might not exist or status is invalid.",
                "error",
            )
    except Exception as e:
        logger.exception(f"Error updating status for violation {violation_id}.")
        flash("An error occurred while updating violation status.", "danger")

    return redirect(url_for("main.violations_log"))


active_streams = {}
stream_frame_generators = {}


def generate_stream_frames(stream_url, stream_id, area_type):
    """
    Generator function to capture frames from a live stream, process them,
    and yield them as JPEG bytes for MJPEG streaming.
    """
    cap = None
    detection_service = current_app.detection_service
    stream_label = f"Stream_{stream_id}"

    try:
        logger.info(f"Attempting to connect to stream ({stream_id}): {stream_url}")
        cap = cv2.VideoCapture(stream_url)
        active_streams[stream_id] = cap  # Store the capture object

        if not cap.isOpened():
            logger.error(f"Cannot open stream ({stream_id}): {stream_url}")
            # Yield a placeholder image or error message
            # For simplicity, we'll just let the loop not run / break
            error_msg = "Error: Could not connect to stream."
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(
                frame,
                error_msg,
                (50, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )
            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            if flag:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + bytearray(encodedImage)
                    + b"\r\n"
                )
            return

        logger.info(
            f"Successfully connected to stream ({stream_id}): {stream_url}. Starting frame generation."
        )
        frame_time_offset = 0  # Simple counter or time tracker
        last_processed_time = time.time()

        while cap.isOpened() and stream_id in active_streams:
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"Stream ({stream_id}) ended or frame not read.")
                break

            # Throttle processing to avoid overwhelming CPU if desired, e.g., 5 FPS
            # current_time = time.time()
            # if current_time - last_processed_time < 0.2: # (1/5 FPS)
            #     time.sleep(0.05) # Small sleep
            #     continue
            # last_processed_time = current_time

            annotated_frame, violations = detection_service.process_live_stream_frame(
                frame,
                stream_url_label=stream_label,
                area_type=area_type,
                frame_time_offset=frame_time_offset,
            )
            frame_time_offset += 1

            (flag, encodedImage) = cv2.imencode(".jpg", annotated_frame)
            if not flag:
                logger.warning(
                    f"Stream ({stream_id}): JPEG encoding failed for a frame."
                )
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + bytearray(encodedImage) + b"\r\n"
            )

    except Exception as e:
        logger.exception(f"Exception in stream ({stream_id}) generator: {e}")
    finally:
        if cap and cap.isOpened():
            cap.release()
        if stream_id in active_streams:
            del active_streams[stream_id]
        if stream_id in stream_frame_generators:
            del stream_frame_generators[stream_id]
        logger.info(f"Stream ({stream_id}) processing stopped and resources released.")


@main_bp.route("/video_feed/<stream_id>")
@login_required
def video_feed(stream_id):
    """Route to serve the MJPEG stream for a given stream_id."""
    if stream_id not in stream_frame_generators:
        logger.error(
            f"Attempted to access video_feed for non-existent stream_id: {stream_id}"
        )
        return Response("Stream not found or not started.", status=404)

    logger.info(f"Serving video_feed for stream_id: {stream_id}")
    return Response(
        stream_frame_generators[stream_id](),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@main_bp.route("/start_stream", methods=["POST"])
@login_required
def start_stream():
    """
    API endpoint to initiate a new live stream.
    It will store the stream URL and assign a unique ID.
    """
    data = request.get_json()
    if not data or "stream_url" not in data:
        return jsonify({"status": "error", "message": "stream_url not provided"}), 400

    stream_url = data["stream_url"]
    area_type = data.get("area_type", "default")
    # Validate stream_url format (basic check)
    if not (
        stream_url.startswith("rtsp://")
        or stream_url.startswith("http://")
        or stream_url.startswith("https://")
    ):
        # Also allow integer for local camera index
        try:
            int(stream_url)  # Check if it's a camera index
        except ValueError:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Invalid stream URL format. Must start with rtsp://, http(s):// or be a camera index.",
                    }
                ),
                400,
            )

    import uuid

    stream_id = str(uuid.uuid4())

    stream_frame_generators[stream_id] = lambda: generate_stream_frames(
        stream_url, stream_id, area_type
    )

    logger.info(
        f"Live stream processing initiated for URL: {stream_url} with stream_id: {stream_id}, Area: {area_type}"
    )
    return jsonify(
        {
            "status": "success",
            "stream_id": stream_id,
            "feed_url": url_for("main.video_feed", stream_id=stream_id, _external=True),
        }
    )


@main_bp.route("/stop_stream/<stream_id>", methods=["POST"])
@login_required
def stop_stream(stream_id):
    """API endpoint to stop an active stream."""
    if stream_id in active_streams:
        cap = active_streams.pop(stream_id)
        if cap and cap.isOpened():
            cap.release()
        if stream_id in stream_frame_generators:
            del stream_frame_generators[stream_id]
        logger.info(f"Stream {stream_id} stopped by user request.")
        return jsonify({"status": "success", "message": f"Stream {stream_id} stopped."})
    else:
        logger.warning(
            f"Attempt to stop non-existent or already stopped stream: {stream_id}"
        )
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Stream {stream_id} not found or already stopped.",
                }
            ),
            404,
        )
