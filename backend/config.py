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

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Admin Configuration
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@rageroom.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")  # Set this in environment variables

# CORS
# Note: When allow_credentials=True, cannot use ["*"]
# For production, specify your actual domain(s)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]

# Daily Topic Configuration
DAILY_TOPIC = os.getenv("DAILY_TOPIC")
DAILY_RULES = os.getenv("DAILY_RULES")

