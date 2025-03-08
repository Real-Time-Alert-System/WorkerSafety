import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# SQLAlchemy imports
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# Authentication imports
from jose import JWTError, jwt
from passlib.context import CryptContext

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

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "please-change-this-to-secure-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
ALERT_FOLDER = os.path.abspath(os.getenv("ALERT_FOLDER", "alerts"))

# Ensure alert folder exists
os.makedirs(ALERT_FOLDER, exist_ok=True)

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alerts.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Notification services
class NotificationService:
    async def send_notification(self, message: str, image_path: Optional[str] = None):
        """Base notification service class. Override for specific implementations."""
        pass

class TelegramNotification(NotificationService):
    def __init__(self, token: str, chat_id: str):
        import requests
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.requests = requests
    
    async def send_notification(self, message: str, image_path: Optional[str] = None):
        try:
            if image_path and os.path.exists(image_path):
                url = f"{self.base_url}/sendPhoto"
                with open(image_path, "rb") as photo:
                    files = {"photo": photo}
                    data = {"chat_id": self.chat_id, "caption": message}
                    response = self.requests.post(url, files=files, data=data)
            else:
                url = f"{self.base_url}/sendMessage"
                payload = {
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
                response = self.requests.post(url, json=payload)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return None

# Database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Integer, default=1)
    
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
    bbox = Column(JSON)  # x, y, width, height
    missing_equipment = Column(JSON)  # List of missing equipment
    
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
    
# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()

async def authenticate_user(username: str, password: str, db: Session):
    user = await get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username, db)
    if user is None:
        raise credentials_exception
    return user

# Initialize FastAPI app
app = FastAPI(
    title="Worker Safety Monitoring API",
    description="API for monitoring worker safety and managing violations",
    version="2.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_active: bool
    
    class Config:
        orm_mode = True

class MissingEquipment(BaseModel):
    equipment_type: str
    confidence: float

class ViolationBase(BaseModel):
    person_id: str
    bbox: Dict[str, float]
    missing_equipment: List[str]

class AlertBase(BaseModel):
    timestamp: float
    location: str = "default"
    violations: List[ViolationBase]

class AlertCreate(AlertBase):
    pass

class AlertInDB(AlertBase):
    id: int
    notification_sent: bool
    
    class Config:
        orm_mode = True

class StatsUpdate(BaseModel):
    total_frames: int
    violations_detected: int
    notifications_sent: int

# Utilities for dashboard
def generate_violation_chart(db: Session):
    """Generate chart showing violations over time"""
    try:
        # Query alerts from database
        alerts = db.query(Alert).all()
        
        if not alerts:
            # Create empty chart if no data
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, "No violation data available", 
                    horizontalalignment='center', verticalalignment='center')
            ax.set_xlabel('Time')
            ax.set_ylabel('Violations')
            plt.tight_layout()
            
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode('utf-8')
        
        # Prepare data for time series
        timestamps = [alert.timestamp for alert in alerts]
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Count violations per hour
        df = pd.DataFrame({'timestamp': dates})
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_counts = df.groupby('hour').size().reset_index(name='count')
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(hourly_counts['hour'], hourly_counts['count'], marker='o', linestyle='-', color='#1a237e')
        ax.set_xlabel('Time')
        ax.set_ylabel('Violations')
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert plot to base64 string
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error generating violation chart: {e}")
        # Return a placeholder image
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, f"Error generating chart: {str(e)}", 
                horizontalalignment='center', verticalalignment='center')
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

def generate_equipment_chart(db: Session):
    """Generate chart showing missing equipment types"""
    try:
        # Query violations from database
        violations = db.query(Violation).all()
        
        if not violations:
            # Create empty chart if no data
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.text(0.5, 0.5, "No violation data available", 
                    horizontalalignment='center', verticalalignment='center')
            ax.set_xlabel('Equipment Type')
            ax.set_ylabel('Count')
            plt.tight_layout()
            
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            return base64.b64encode(buf.read()).decode('utf-8')
        
        # Count missing equipment types
        equipment_counts = {}
        for violation in violations:
            for equipment in violation.missing_equipment:
                equipment = equipment.replace('_', ' ').title()
                equipment_counts[equipment] = equipment_counts.get(equipment, 0) + 1
        
        # Sort by count
        equipment_items = sorted(equipment_counts.items(), key=lambda x: x[1], reverse=True)
        equipment_types = [item[0] for item in equipment_items]
        counts = [item[1] for item in equipment_items]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(equipment_types, counts, color='#3949ab')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        ax.set_xlabel('Equipment Type')
        ax.set_ylabel('Number of Violations')
        ax.set_title('Missing Safety Equipment Types')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Convert plot to base64 string
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error generating equipment chart: {e}")
        # Return a placeholder image
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, f"Error generating chart: {str(e)}", 
                horizontalalignment='center', verticalalignment='center')
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

# Background task for sending notifications
async def send_alert_notification(alert_id: int, db: Session):
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            logger.error(f"Alert {alert_id} not found for notification")
            return
        
        # Get the image
        image = db.query(AlertImage).filter(AlertImage.id == alert.image_id).first()
        image_path = os.path.join(ALERT_FOLDER, image.filename) if image else None
        
        # Get violations
        violations = db.query(Violation).filter(Violation.alert_id == alert.id).all()
        
        # Format notification message
        equipment_counts = {}
        for violation in violations:
            for eq in violation.missing_equipment:
                equipment_counts[eq] = equipment_counts.get(eq, 0) + 1
        
        equipment_str = ", ".join([f"{count}x {eq.replace('_', ' ')}" 
                                  for eq, count in equipment_counts.items()])
        
        message = f"🚨 SAFETY ALERT 🚨\nTime: {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}\nLocation: {alert.location}\nMissing equipment: {equipment_str}"
        
        # Initialize notification service
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if telegram_token and telegram_chat_id:
            notification_service = TelegramNotification(telegram_token, telegram_chat_id)
            await notification_service.send_notification(message, image_path)
            
            # Update notification status
            alert.notification_sent = 1
            db.commit()
            
            # Update stats
            stats = db.query(Stats).order_by(Stats.id.desc()).first()
            if stats:
                stats.notifications_sent += 1
                db.commit()
            
            logger.info(f"Notification sent for alert {alert_id}")
        else:
            logger.warning("Telegram credentials not configured, notification not sent")
    
    except Exception as e:
        logger.error(f"Error sending notification for alert {alert_id}: {e}")

# API Routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=UserInDB)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = await get_user(user.username, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Any, db: Session = Depends(get_db)):
    """Main dashboard view"""
    try:
        # Load stats
        stats = db.query(Stats).order_by(Stats.id.desc()).first()
        if not stats:
            stats = Stats(
                total_frames=0,
                violations_detected=0,
                notifications_sent=0,
                started_at=time.time()
            )
            db.add(stats)
            db.commit()
            db.refresh(stats)
        
        # Calculate uptime
        uptime_seconds = time.time() - stats.started_at
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime = f"{int(hours)}h {int(minutes)}m"
        
        # Generate charts
        violation_chart = generate_violation_chart(db)
        equipment_chart = generate_equipment_chart(db)
        
        # Get recent alerts
        recent_alerts = []
        alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(9).all()
        
        for alert in alerts:
            # Get equipment count
            violations = db.query(Violation).filter(Violation.alert_id == alert.id).all()
            equipment_counts = {}
            for v in violations:
                for eq in v.missing_equipment:
                    equipment_counts[eq] = equipment_counts.get(eq, 0) + 1
            
            equipment_str = ", ".join([f"{count}x {eq.replace('_', ' ')}" 
                                      for eq, count in equipment_counts.items()])
            
            # Get image filename
            image = db.query(AlertImage).filter(AlertImage.id == alert.image_id).first()
            filename = image.filename if image else ""
            
            recent_alerts.append({
                'filename': filename,
                'time': datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                'message': f"Missing: {equipment_str}"
            })
        
        # Define template context
        context = {
            "request": request,
            "stats": {
                "violations_detected": stats.violations_detected,
                "notifications_sent": stats.notifications_sent,
                "total_frames": stats.total_frames
            },
            "uptime": uptime,
            "violation_chart": violation_chart,
            "equipment_chart": equipment_chart,
            "recent_alerts": recent_alerts
        }
        
        return templates.TemplateResponse("dashboard.html", context)
    
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return HTMLResponse(content=f"<h1>Error rendering dashboard</h1><p>{str(e)}</p>", status_code=500)

@app.get("/alert/{filename}")
async def serve_alert_image(filename: str):
    """Serve alert images"""
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Invalid file type requested")
    
    file_path = os.path.join(ALERT_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.post("/api/alert", status_code=status.HTTP_201_CREATED)
async def receive_alert(
    alert: AlertCreate, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Receive alert data from detection system"""
    try:
        # Handle image upload separately if needed
        
        # Create new alert
        db_alert = Alert(
            timestamp=alert.timestamp,
            location=alert.location,
            notification_sent=0
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        
        # Add violations
        for v in alert.violations:
            db_violation = Violation(
                alert_id=db_alert.id,
                person_id=v.person_id,
                bbox=v.bbox,
                missing_equipment=v.missing_equipment
            )
            db.add(db_violation)
        
        # Update stats
        stats = db.query(Stats).order_by(Stats.id.desc()).first()
        if not stats:
            stats = Stats(
                total_frames=1,
                violations_detected=len(alert.violations),
                notifications_sent=0,
                started_at=time.time()
            )
            db.add(stats)
        else:
            stats.violations_detected += len(alert.violations)
            stats.total_frames += 1
            
        db.commit()
        
        # Schedule notification task
        background_tasks.add_task(send_alert_notification, db_alert.id, db)
        
        return {"success": True, "message": "Alert received and stored", "alert_id": db_alert.id}
        
    except Exception as e:
        logger.error(f"Error processing alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload alert image"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(ALERT_FOLDER, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        # Save to database
        db_image = AlertImage(filename=filename)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        return {"success": True, "filename": filename, "image_id": db_image.id}
    
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current system stats"""
    try:
        stats = db.query(Stats).order_by(Stats.id.desc()).first()
        if not stats:
            stats = Stats(started_at=time.time())
            db.add(stats)
            db.commit()
            db.refresh(stats)
        
        # Calculate uptime
        uptime_seconds = time.time() - stats.started_at
        
        return {
            "total_frames": stats.total_frames,
            "violations_detected": stats.violations_detected,
            "notifications_sent": stats.notifications_sent,
            "uptime_seconds": uptime_seconds,
            "uptime_formatted": str(timedelta(seconds=int(uptime_seconds)))
        }
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts")
async def get_alerts(
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    limit: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alerts with optional filtering"""
    try:
        query = db.query(Alert)
        
        if start_time:
            query = query.filter(Alert.timestamp >= start_time)
        
        if end_time:
            query = query.filter(Alert.timestamp <= end_time)
        
        query = query.order_by(Alert.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        alerts = query.all()
        
        # Format results
        result = []
        for alert in alerts:
            # Get violations
            violations = db.query(Violation).filter(Violation.alert_id == alert.id).all()
            violation_list = []
            
            for v in violations:
                violation_list.append({
                    "person_id": v.person_id,
                    "bbox": v.bbox,
                    "missing_equipment": v.missing_equipment
                })
            
            # Get image
            image = db.query(AlertImage).filter(AlertImage.id == alert.image_id).first()
            
            result.append({
                "id": alert.id,
                "timestamp": alert.timestamp,
                "location": alert.location,
                "filename": image.filename if image else None,
                "violations": violation_list,
                "notification_sent": bool(alert.notification_sent)
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": time.time(), "version": "2.0.0"}

# Run the application if the script is executed directly
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"Starting Notification API Server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
