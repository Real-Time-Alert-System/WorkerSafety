# PPE Compliance Monitoring System

## Project Overview

This system detects Personal Protective Equipment (PPE) compliance using computer vision (YOLOv8) and provides a web interface for monitoring violations, viewing statistics, and managing alerts. It includes real-time notifications via Telegram.

This project was refactored to meet industry standards, improve reliability, and provide a professional user interface suitable for demonstration purposes.

## Features

- **Media Upload:** Upload images (JPG, PNG) or videos (MP4, AVI, MOV, WebM) via a web interface.
- **PPE Detection:** Utilizes a fine-tuned YOLOv8 model to detect various PPE items and identify violations (e.g., missing hard hats, vests, masks based on configured rules).
- **Violation Logging:** Records detected violations in an SQLite database, including timestamp, violation type, location, severity, and a snapshot image.
- **Web Dashboard:** Displays key statistics about violations:
  - Counts by equipment type
  - Counts by severity (High, Medium, Low)
  - Counts by location
  - Counts by status (Unresolved, Investigating, Resolved)
  - Daily violation trend chart (last 30 days)
- **Violation Log:** A filterable/sortable table view of all recorded violations with links to evidence images and status update capability.
- **Telegram Notifications:** Sends real-time alerts to a configured Telegram chat when violations are detected (includes violation details and image). Features a cooldown mechanism to prevent notification spam.
- **Configurable:** Easily configure model paths, database location, Telegram credentials, PPE class mappings, violation rules, and area requirements via a `.env` file.

## Project Structure

ppe-detection-project/
├── app/ # Main Flask application package
│ ├── init.py # Application factory
│ ├── routes.py # Web routes (Blueprint)
│ ├── services/ # Business logic (detection, notification)
│ ├── models.py # Data structures
│ ├── database.py # Database interaction layer
│ ├── static/ # CSS, JS, Images
│ ├── templates/ # Jinja2 templates
│ └── config.py # Configuration class
├── models/ # ML models
│ └── yolov8s_ppe_custom.pt # Trained YOLOv8 model
├── uploads/ # Temporary uploads (gitignore this)
├── violation_data/ # Saved violation images & DB (gitignore this)
│ ├── images/
│ └── violations.db
├── .env # Environment variables (Create from .env.example)
├── .env.example # Example environment file
├── requirements.txt # Python dependencies
├── run.py # Script to run the app
├── schema.sql # Database schema definition
└── README.md # This file

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd ppe-detection-project
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    _Note: `ultralytics` and `opencv-python-headless` can be large._

4.  **Configure Environment Variables:**

    - Copy `.env.example` to `.env`: `cp .env.example .env`
    - **Edit `.env`** and fill in the required values:
      - `SECRET_KEY`: Generate a strong secret key (`python -c 'import os; print(os.urandom(24).hex())'`).
      - `TELEGRAM_BOT_TOKEN`: Your Telegram Bot token.
      - `TELEGRAM_CHAT_ID`: The chat ID where notifications should be sent.
      - `MODEL_PATH`: Verify the path to your trained `.pt` file.
      - `PPE_CLASS_MAPPING`: **Crucially, update this JSON string to match the class IDs and names from the `data.yaml` file used to train your specific YOLOv8 model.**
      - `VIOLATION_CLASSES`: Update this JSON list with the _exact_ class names (from the mapping above) that represent a violation (e.g., "NO-Hardhat").
      - `AREA_REQUIREMENTS`: Define required PPE for different work areas if needed.
      - Review other paths if you changed the structure.

5.  **Place the Trained Model:**

    - Ensure your working trained YOLOv8 model file (e.g., `last.pt` or `best.pt`) is placed in the `models/` directory and renamed to match the `MODEL_PATH` in your `.env` file (e.g., `models/yolov8s_ppe_custom.pt`).

6.  **Initialize the Database:**
    - The database (`violations.db`) and schema will be created automatically when you first run the application using `run.py`.

## Running the Application

1.  **Activate the virtual environment:**

    ```bash
    source venv/bin/activate
    ```

2.  **Run the Flask development server:**

    ```bash
    python run.py
    ```

3.  **Access the application:** Open your web browser and navigate to `http://127.0.0.1:5000` (or `http://<your-server-ip>:5000`).

## Usage

1.  Navigate to the **Upload** page.
2.  Enter the **Location** and select the **Area Type**.
3.  Choose an image or video file and click **Upload and Analyze**.
4.  Wait for processing. You will be redirected to the **Violations Log**.
5.  Check the **Dashboard** for statistics and charts.
6.  Monitor your configured **Telegram chat** for real-time violation notifications.
7.  On the **Violations Log** page, you can view violation details, see the evidence image, and update the status (Unresolved, Investigating, Resolved).
