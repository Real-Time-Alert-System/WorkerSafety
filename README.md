# 🛡️ WorkerShield AI — Real-Time Industrial PPE Safety Monitoring System

[![Live Demo](https://img.shields.io/badge/%F0%9F%9A%80%20Live%20Demo-Try%20WorkerShield%20AI-00D2FF?style=for-the-badge&logo=rocket)](https://workershield-ai.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Frontend: React + Vite](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB.svg)](frontend/)
[![Backend: Node.js + Express](https://img.shields.io/badge/Backend-Node.js%20%2B%20Express-339933.svg)](backend/)
[![AI Service: Python + FastAPI](https://img.shields.io/badge/AI%20Service-Python%20%2B%20FastAPI-009688.svg)](ai_service/)
[![AI Model: YOLOv8](https://img.shields.io/badge/AI%20Model-YOLOv8-FF6F00.svg)](https://ultralytics.com)
[![Database: PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1.svg)](backend/database.js)

WorkerShield AI is an enterprise-grade, microservice-architected industrial safety system that performs real-time Personal Protective Equipment (PPE) compliance monitoring using computer vision (YOLOv8). It identifies safety violations (missing hardhats, safety vests, masks) across live CCTV streams, USB webcams, and mobile cameras, immediately logging audit events into PostgreSQL and dispatching visual alerts to supervisors via Telegram.

---

## 🌐 Live Interactive Demo & Application Links

Anyone can explore and try the live application features directly:

* **🚀 Live Demo Website**: [https://workershield-ai.vercel.app](https://workershield-ai.vercel.app)
* **📱 Mobile Inspection Link**: Open [https://workershield-ai.vercel.app?mobile=true](https://workershield-ai.vercel.app?mobile=true) on your phone camera.
* **⚡ Local Development URL**: `http://localhost:5173` (after running `npm run dev`)

---

## 👤 Author Information

* **Project Author & Creator**: **Vishal Agrahari**
* **GitHub Profile**: [@quantumva23](https://github.com/quantumva23)
* **Email**: `va203015@gmail.com`
* **Repository**: [Real-Time-Alert-System/WorkerSafety](https://github.com/Real-Time-Alert-System/WorkerSafety)

---

## 📸 Interactive Demo Features Walkthrough

| Feature | Description | How to Try It in Demo |
| :--- | :--- | :--- |
| **🤖 Model Verification Test Bench** | Upload site snapshot images to run YOLOv8 PPE neural network detection. | Go to **Live Monitoring** → Upload any image file → Click **Run AI Test Analysis**. |
| **📹 Hardware USB & Webcam Feed** | Connect live USB webcams or laptop cameras for instant frame capture. | Go to **Live Monitoring** → Select camera device → Click **▶ Start Live Camera**. |
| **📱 Mobile QR Code Stream Pairing** | Turn any Android/iPhone into a live site inspection camera via QR scan. | Click **📱 Send Phone Camera Link** → Scan the generated QR Code on your phone. |
| **✈️ Instant Telegram Alert Bot** | Automatic telegram photo alerts sent on PPE non-compliance detection. | Go to **Settings** → Enable Telegram → Click **🔗 Connect via Telegram Link**. |
| **📊 PostgreSQL Live Analytics** | Real-time hazard hotspot tracking & supervisor resolution response rates. | Go to **Analytics** tab to view auto-polling PostgreSQL statistics. |

---

## 💡 What WorkerShield AI Does

1. **Real-Time PPE Detection**: Uses a trained **YOLOv8** computer vision model to detect workers and non-compliant safety gear (`NO-Hardhat`, `NO-Safety Vest`, `NO-Mask`) with sub-200ms latency.
2. **Multi-Source Video Stream Ingestion**: Connects directly to external USB cameras, integrated laptop webcams, live CCTV RTSP feeds, and QR-code-paired mobile smartphone cameras.
3. **Instant Telegram Alert Channel**: Sends instant alert notifications with snapshot evidence, time, location, and hazard severity directly to supervisors' personal Telegram accounts via deep links (`/start <token>`).
4. **PostgreSQL Event Auditing**: Stores compliant logs and violation records in PostgreSQL with UTF-8 client encoding for legal OSHA compliance audits.
5. **Interactive Safety Analytics**: Auto-polling real-time dashboard displaying hazard hotspots, site compliance scores, supervisor response rates, and equipment violation breakdowns.

---

## 🏗️ Microservices Architecture

```text
               +----------------------------------+
               |   React + Vite Frontend (UI)     |
               |  (Dashboard, Live Stream, Audit) |
               +----------------+-----------------+
                                |
                                v
               +----------------+-----------------+
               |   Node.js Express API Gateway    |
               | (Auth, Settings, PostgreSQL DB)  |
               +-------+------------------+-------+
                       |                  |
                       v                  v
+----------------------+------+    +------+-------------------------+
|  Python FastAPI AI Service  |    | Telegram Bot API Alert Channel |
|  (YOLOv8 Vision Inference)  |    |  (Instant Supervisor Alerts)   |
+-----------------------------+    +--------------------------------+
```

---

## 📁 Repository Directory Structure

```text
WorkerSafety/
├── ai_service/             # Python FastAPI YOLOv8 computer vision service (Port 8008)
│   ├── app.py              # Vision inference endpoint & model executor
│   └── models/             # YOLOv8 weights (.pt files)
├── backend/                # Node.js Express REST API Gateway (Port 5000)
│   ├── server.js           # API endpoints, JWT auth, setting storage
│   ├── database.js         # PostgreSQL connection pool with UTF-8 guards
│   └── notificationService.js # Telegram Bot alert dispatcher & rate-limiter
├── frontend/               # React 19 + Vite Single Page Application (Port 5173)
│   ├── src/
│   │   ├── components/     # LiveMonitoringView, DashboardView, SubViews, Profile Card
│   │   ├── App.jsx         # Router & navigation layout
│   │   └── index.css       # Industrial glassmorphic responsive design system
├── .env                    # Runtime credentials (DB, Telegram, JWT secrets)
├── requirements.txt        # Python AI service dependencies
└── README.md               # Documentation
```

---

## ⚙️ Hardware & Stream Compatibility

* **Integrated Webcams**: Standard laptop cameras (`getUserMedia`).
* **External USB Cameras**: Plug-and-play USB cameras & inspection borescopes.
* **Mobile Smartphones**: iPhone & Android cameras via scannable QR Code or Telegram deep links.
* **CCTV & Network Cameras**: RTSP / WebRTC CCTV streams.

---

## 🚀 Quick Start Guide (How Anyone Can Run & Test Demo)

### 1. Prerequisites
Ensure you have the following installed on your machine:
* **Node.js**: `v18.0.0` or higher
* **Python**: `v3.10` or higher
* **PostgreSQL Database**: `v13` or higher
* **Git**

---

### 2. Installation Steps

#### Step 1: Clone the Repository
```bash
git clone https://github.com/Real-Time-Alert-System/WorkerSafety.git
cd WorkerSafety
```

#### Step 2: Configure Environment Variables
Create a `.env` file in the root folder with your PostgreSQL and Telegram credentials:

```env
# Server Port Configuration
PORT=5000
AI_SERVICE_URL=http://localhost:8008

# PostgreSQL Database Credentials
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=workersafety

# JWT Secret
JWT_SECRET=super_secret_workershield_jwt_key

# Telegram Bot Alert Credentials
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id
NOTIFICATION_COOLDOWN=60
```

#### Step 3: Initialize Python AI Service
```bash
# Create and activate virtual environment
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate

# Install Python requirements
pip install -r requirements.txt

# Start FastAPI AI Service (Runs on port 8008)
python ai_service/app.py
```

#### Step 4: Initialize Node.js Backend API
In a new terminal window:
```bash
cd backend
npm install

# Start Express Backend API Gateway (Runs on port 5000)
npm start
```

#### Step 5: Initialize React Frontend Application
In a new terminal window:
```bash
cd frontend
npm install

# Start Vite React Dev Server (Runs on port 5173)
npm run dev
```

---

## 🖥️ How to Use & Test the Live Demo

1. **Access the Web Dashboard**:
   Open your browser and navigate to `http://localhost:5173`.

2. **Model Verification Test Bench (Image Upload Analysis)**:
   * Go to **Live Monitoring** tab.
   * Under **Model Verification Test Bench**, select any test site image or worker snapshot.
   * Click **Run AI Test Analysis**.
   * The system will detect PPE compliance, output confidence percentages, log the incident into PostgreSQL, and send a Telegram alert notification.

3. **Live Hardware USB / Laptop Webcam Testing**:
   * Under **Live Hardware Camera Connection**, select your USB camera or laptop webcam from the dropdown.
   * Click **▶ Start Live Camera**.
   * Click **📸 Capture & Run AI Detection** to analyze the live camera frame in real time.

4. **Mobile Phone Camera Connection (QR Code & Telegram Link)**:
   * Click **📱 Send Phone Camera Link**.
   * A **Scannable QR Code** modal will pop up on your screen.
   * Point your iPhone or Android camera at the QR code (or tap the direct link sent to your Telegram bot) to turn your phone into a portable site inspection camera!

5. **Real-Time Safety Analytics & Audit Logs**:
   * Navigate to **Analytics** to view live site hazard hotspots and supervisor resolution rates fed directly from PostgreSQL.
   * Navigate to **Alerts & Incidents** to review the top 20 recent violations in a scrollable audit window.
   * Click on your username/avatar in the sidebar to open your **Safety Profile Settings** card.

---

## 📜 License

This project is released under the **MIT License**. Created with passion by **Vishal Agrahari**.
