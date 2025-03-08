import os
import json
import time
import logging
import httpx
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from jose.constants import ALGORITHMS

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

class AuthError(Exception):
    def __init__(self, error: str, status_code: int):
        self.error = error
        self.status_code = status_code

async def get_jwks():
    async with httpx.AsyncClient() as client:
        response = await client.get(JWKS_URL)
        return response.json()

async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        jwks = await get_jwks()
        token = credentials.credentials
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if not rsa_key:
            raise AuthError("Invalid token header", status.HTTP_401_UNAUTHORIZED)
        
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS.RS256,
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        return payload
    except JWTError as exc:
        raise AuthError(str(exc), status.HTTP_401_UNAUTHORIZED)
    except Exception as exc:
        raise AuthError(str(exc), status.HTTP_401_UNAUTHORIZED)

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

# Additional endpoints (dashboard, stats, etc) would follow similar patterns
# using the validate_token dependency for authentication

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
