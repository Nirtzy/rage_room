"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from datetime import datetime


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


# Authentication Schemas
class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

    @field_validator('username')
    @classmethod
    def sanitize_username(cls, v: str) -> str:
        """Sanitize and validate username"""
        username = v.strip()
        if not username.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        return username


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[int] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    username: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Admin Schemas
class TopicUpdate(BaseModel):
    """Schema for updating daily topic"""
    topic: str = Field(..., min_length=1, max_length=200)
    rules: Optional[str] = Field(None, max_length=500)


class MessageDelete(BaseModel):
    """Schema for deleting a message"""
    message_id: int


class UserBan(BaseModel):
    """Schema for banning a user"""
    user_id: int
    ban: bool = True


