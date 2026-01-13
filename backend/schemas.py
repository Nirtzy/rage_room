"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field, field_validator


class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    user: str = Field(..., min_length=1, max_length=50)
    text: str = Field(..., min_length=1, max_length=500)

    @field_validator('user')
    @classmethod
    def sanitize_user(cls, v: str) -> str:
        """Sanitize username"""
        return v.strip()

    @field_validator('text')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        """Sanitize message text"""
        text = v.strip()
        if not text:
            raise ValueError("Message cannot be empty")
        return text


class MessageResponse(BaseModel):
    """Schema for message response"""
    user: str
    text: str
    timestamp: str

    class Config:
        from_attributes = True


class MessageInDB(MessageResponse):
    """Schema for message in database"""
    id: int
    date_created: str

