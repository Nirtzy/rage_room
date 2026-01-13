"""Application configuration"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./messages.db")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Security
MAX_MESSAGES_PER_MINUTE = 25
MAX_MESSAGE_LENGTH = 500
MAX_CONNECTIONS = 100

# CORS
ALLOWED_ORIGINS = ["*"]  # In production, specify your domain

# Daily Topic Configuration
DAILY_TOPIC = os.getenv("DAILY_TOPIC")
DAILY_RULES = os.getenv("DAILY_RULES")

