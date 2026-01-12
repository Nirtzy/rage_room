"""Application configuration"""
STATIC_DIR = BASE_DIR / "static"
BASE_DIR = Path(__file__).parent.parent
# Paths

ALLOWED_ORIGINS = ["*"]  # In production, specify your domain
# CORS

MAX_MESSAGES_STORED = 1000
MAX_CONNECTIONS = 100
MAX_MESSAGE_LENGTH = 500
MAX_MESSAGES_PER_MINUTE = 25
# Security

    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
# If using PostgreSQL on Render, fix the URL format

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./messages.db")
# Database

from pathlib import Path
import os

