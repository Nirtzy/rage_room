"""Admin routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from typing import List
from backend.database import get_db
from backend.models import User, Message
from backend.schemas import TopicUpdate, MessageDelete, UserBan
from backend.auth import get_current_admin_user
import os

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get application statistics (admin only)"""
    total_users = db.query(func.count(User.id)).scalar()
    total_messages = db.query(func.count(Message.id)).scalar()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_messages = db.query(func.count(Message.id)).filter(
        Message.date_created == today
    ).scalar()

    return {
        "total_users": total_users,
        "total_messages": total_messages,
        "today_messages": today_messages,
        "current_topic": os.getenv("DAILY_TOPIC", "No topic set"),
        "current_rules": os.getenv("DAILY_RULES", "")
    }


@router.post("/topic")
async def update_topic(
    topic_data: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update daily topic (admin only)"""
    # Note: This will update environment variables for the current session only
    # For persistent changes, you need to update them in Render dashboard
    os.environ["DAILY_TOPIC"] = topic_data.topic
    if topic_data.rules:
        os.environ["DAILY_RULES"] = topic_data.rules

    return {
        "message": "Topic updated successfully",
        "topic": topic_data.topic,
        "rules": topic_data.rules or "",
        "note": "To make this change persistent, update environment variables in Render dashboard"
    }


@router.delete("/message/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a specific message (admin only)"""
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    db.delete(message)
    db.commit()

    return {"message": "Message deleted successfully"}


@router.get("/messages")
async def get_all_messages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all messages with pagination (admin only)"""
    messages = db.query(Message).order_by(
        Message.timestamp.desc()
    ).offset(skip).limit(limit).all()

    return [
        {
            "id": msg.id,
            "user": msg.user,
            "text": msg.text,
            "timestamp": msg.timestamp.isoformat(),
            "date_created": msg.date_created,
            "user_id": msg.user_id
        }
        for msg in messages
    ]


@router.get("/users")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()

    return [user.to_dict() for user in users]


@router.post("/user/ban")
async def ban_user(
    ban_data: UserBan,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Ban or unban a user (admin only)"""
    user = db.query(User).filter(User.id == ban_data.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot ban admin users"
        )

    user.is_active = not ban_data.ban
    db.commit()

    action = "banned" if ban_data.ban else "unbanned"
    return {"message": f"User {user.username} has been {action}"}


@router.delete("/clear-messages")
async def clear_all_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Clear all messages (admin only)"""
    count = db.query(Message).delete()
    db.commit()

    return {"message": f"Cleared {count} messages"}

