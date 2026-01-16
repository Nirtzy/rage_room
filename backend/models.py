"""Database models"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
from backend.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat()
        }


class Message(Base):
    """Message model for storing chat messages"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(50), nullable=False)
    text = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    date_created = Column(String(10), nullable=False)  # YYYY-MM-DD for daily clearing
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional link to registered user

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "user": self.user,
            "text": self.text,
            "timestamp": self.timestamp.isoformat()
        }

