"""Database models"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.database import Base


class Message(Base):
    """Message model for storing chat messages"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(50), nullable=False)
    text = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_created = Column(String(10), nullable=False)  # YYYY-MM-DD for daily clearing

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "user": self.user,
            "text": self.text,
            "timestamp": self.timestamp.isoformat()
        }

