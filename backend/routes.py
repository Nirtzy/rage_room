"""API routes"""
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Message
from backend.config import STATIC_DIR, DAILY_TOPIC, DAILY_RULES

router = APIRouter()


@router.get("/")
async def get_index():
    """Serve the main HTML page"""
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for Render"""
    from backend.websocket import connected_clients

    today = datetime.now().strftime("%Y-%m-%d")
    message_count = db.query(Message).filter(Message.date_created == today).count()

    return {
        "status": "healthy",
        "message_count": message_count,
        "connected_clients": len(connected_clients),
        "date": today
    }


@router.get("/api/today")
async def get_today():
    """Get today's topic information"""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "title": f"today's topic: {DAILY_TOPIC}",
        "rules": f"{DAILY_RULES}",
        "image_url": "/static/ice_image.jpg"
    }


@router.get("/api/messages", response_model=dict)
async def get_messages(db: Session = Depends(get_db)):
    """Get message history for new users"""
    today = datetime.now().strftime("%Y-%m-%d")
    messages = db.query(Message).filter(
        Message.date_created == today
    ).order_by(Message.timestamp).all()

    return {"messages": [msg.to_dict() for msg in messages]}

