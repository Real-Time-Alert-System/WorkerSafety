import os
import json
import time
import logging
import httpx
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
from collections import defaultdict
from io import BytesIO
import base64

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from jose.constants import ALGORITHMS
from authlib.integrations.starlette_client import OAuth

# SQLAlchemy imports
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NotificationAPI")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

# Application Configuration
ALERT_FOLDER = os.path.abspath(os.getenv("ALERT_FOLDER", "alerts"))
os.makedirs(ALERT_FOLDER, exist_ok=True)

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alerts.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Auth0 Security Setup
security = HTTPBearer()
oauth = OAuth()
oauth.register(
    name='auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'},
)

class AuthError(Exception):
    def __init__(self, error: str, status_code: int):
        self.error = error
        self.status_code = status_code

# Database Models
class AlertImage(Base):
    __tablename__ = "alert_images"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Violation(Base):
    __tablename__ = "violations"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    person_id = Column(String)
    bbox = Column(JSON)
    missing_equipment = Column(JSON)
    alert = relationship("Alert", back_populates="violations")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True)
    image_id = Column(Integer, ForeignKey("alert_images.id"))
    location = Column(String, index=True)
    notification_sent = Column(Integer, default=0)
    violations = relationship("Violation", back_populates="alert")

class Stats(Base):
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True, index=True)
    total_frames = Column(Integer, default=0)
    violations_detected = Column(Integer, default=0)
    notifications_sent = Column(Integer, default=0)
    started_at = Column(Float, default=time.time)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Notification Service
class TelegramNotification:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    async def send_notification(self, message: str, image_path: Optional[str] = None):
        try:
            async with httpx.AsyncClient() as client:
                if image_path and os.path.exists(image_path):
                    with open(image_path, "rb") as photo:
                        files = {"photo": photo}
                        data = {"chat_id": self.chat_id, "caption": message}
                        response = await client.post(
                            f"{self.base_url}/sendPhoto",
                            files=files,
                            data=data
                        )
                else:
                    payload = {
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": "HTML"
                    }
                    response = await client.post(
                        f"{self.base_url}/sendMessage",
                        json=payload
                    )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Telegram notification failed: {str(e)}")
            return None

# Pydantic Models
class ViolationBase(BaseModel):
    person_id: str
    bbox: Dict[str, float]
    missing_equipment: List[str]

class AlertBase(BaseModel):
    timestamp: float
    location: str = "default"
    violations: List[ViolationBase]

class StatsUpdate(BaseModel):
    total_frames: int
    violations_detected: int
    notifications_sent: int

# Application Setup
app = FastAPI(
    title="Worker Safety Monitoring API",
    description="API for monitoring worker safety with Auth0 integration",
    version="2.1.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Utility Functions
async def get_or_create_stats(db: Session):
    stats = db.query(Stats).first()
    if not stats:
        stats = Stats()
        db.add(stats)
        db.commit()
        db.refresh(stats)
    return stats

async def send_alert_notification(alert_id: int):
    db = SessionLocal()
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            logger.error(f"Alert {alert_id} not found")
            return

        image = db.query(AlertImage).filter(AlertImage.id == alert.image_id).first()
        image_path = os.path.join(ALERT_FOLDER, image.filename) if image else None

        violations = db.query(Violation).filter(Violation.alert_id == alert.id).all()
        equipment_counts = {}
        for violation in violations:
            for eq in violation.missing_equipment:
                equipment_counts[eq] = equipment_counts.get(eq, 0) + 1

        message = f"🚨 SAFETY ALERT 🚨\nTime: {datetime.fromtimestamp(alert.timestamp)}\n"
        message += f"Location: {alert.location}\nMissing equipment: {', '.join([f'{v}x {k}' for k, v in equipment_counts.items()])}"

        if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
            service = TelegramNotification(
                os.getenv("TELEGRAM_BOT_TOKEN"),
                os.getenv("TELEGRAM_CHAT_ID")
            )
            await service.send_notification(message, image_path)
            alert.notification_sent = 1
            stats = await get_or_create_stats(db)
            stats.notifications_sent += 1
            db.commit()
    except Exception as e:
        logger.error(f"Notification error: {str(e)}")
    finally:
        db.close()

# Auth Routes
@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

@app.get("/callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.auth0.authorize_access_token(request)
        request.session['user'] = token['userinfo']
        return RedirectResponse(url='/')
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(
        url=f"https://{AUTH0_DOMAIN}/v2/logout?"
        f"returnTo={request.url_for('dashboard')}&"
        f"client_id={AUTH0_CLIENT_ID}"
    )

# Dashboard Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Check authentication
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/login')
    
    # Get stats
    stats = await get_or_create_stats(db)
    
    # Calculate uptime
    uptime_seconds = time.time() - stats.started_at
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime = f"{int(hours)}h {int(minutes)}m"
    
    # Get recent alerts
    recent_alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(6).all()
    
    # Prepare chart data
    alerts = db.query(Alert).all()
    violation_data = []
    violation_labels = []
    equipment_counts = defaultdict(int)
    
    # Process data for charts
    df_data = []
    for alert in alerts:
        timestamp = datetime.fromtimestamp(alert.timestamp)
        for violation in alert.violations:
            df_data.append({'timestamp': timestamp, 'count': 1})
            for eq in violation.missing_equipment:
                equipment_counts[eq] += 1
    
    # Time series data
    if df_data:
        df = pd.DataFrame(df_data)
        df.set_index('timestamp', inplace=True)
        hourly_counts = df.resample('H').sum().fillna(0)
        violation_labels = hourly_counts.index.strftime('%H:%M').tolist()
        violation_data = hourly_counts['count'].tolist()
    else:
        violation_labels = []
        violation_data = []

    # Equipment data
    equipment_labels = [eq.title().replace('_', ' ') for eq in equipment_counts.keys()]
    equipment_data = list(equipment_counts.values())

    # Format recent alerts
    formatted_alerts = []
    for alert in recent_alerts:
        image = db.query(AlertImage).filter(AlertImage.id == alert.image_id).first()
        violations = db.query(Violation).filter(Violation.alert_id == alert.id).all()
        formatted_alerts.append({
            "timestamp": datetime.fromtimestamp(alert.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "location": alert.location,
            "image_filename": image.filename if image else "default.jpg",
            "violations": [{
                "person_id": v.person_id,
                "missing_equipment": [eq.title().replace('_', ' ') for eq in v.missing_equipment]
            } for v in violations]
        })

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "uptime": uptime,
        "recent_alerts": formatted_alerts,
        "violation_labels": json.dumps(violation_labels),
        "violation_data": json.dumps(violation_data),
        "equipment_labels": json.dumps(equipment_labels),
        "equipment_data": json.dumps(equipment_data)
    })

@app.get("/alert-image/{filename}")
async def get_alert_image(filename: str):
    file_path = os.path.join(ALERT_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Image not found")

# API Endpoints
@app.post("/api/alert", status_code=status.HTTP_201_CREATED)
async def receive_alert(
    alert: AlertBase,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    token: dict = Depends(validate_token)
):
    try:
        db_alert = Alert(
            timestamp=alert.timestamp,
            location=alert.location,
            notification_sent=0
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)

        for v in alert.violations:
            db_violation = Violation(
                alert_id=db_alert.id,
                person_id=v.person_id,
                bbox=v.bbox,
                missing_equipment=v.missing_equipment
            )
            db.add(db_violation)

        stats = await get_or_create_stats(db)
        stats.violations_detected += len(alert.violations)
        stats.total_frames += 1
        db.commit()

        background_tasks.add_task(send_alert_notification, db_alert.id)
        return {"message": "Alert processed", "alert_id": db_alert.id}

    except Exception as e:
        logger.error(f"Alert processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: dict = Depends(validate_token)
):
    try:
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail="Invalid file type")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(ALERT_FOLDER, filename)

        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        try:
            db_image = AlertImage(filename=filename)
            db.add(db_image)
            db.commit()
            return {"filename": filename, "image_id": db_image.id}
        except Exception as e:
            os.remove(file_path)
            raise e

    except Exception as e:
        logger.error(f"Image upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": time.time(), "version": "2.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
