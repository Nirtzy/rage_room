"""Utility functions for message handling"""
from collections import deque
from typing import Dict
from datetime import datetime
import time
from backend.config import MAX_MESSAGES_PER_MINUTE, MAX_MESSAGE_LENGTH

# Rate limiting: track messages per user
user_message_timestamps: Dict[str, deque] = {}


def is_rate_limited(user: str) -> bool:
    """Check if user is sending too many messages"""
    now = time.time()

    if user not in user_message_timestamps:
        user_message_timestamps[user] = deque(maxlen=MAX_MESSAGES_PER_MINUTE)

    # Remove timestamps older than 1 minute
    user_timestamps = user_message_timestamps[user]
    while user_timestamps and now - user_timestamps[0] > 60:
        user_timestamps.popleft()

    # Check if user exceeded limit
    if len(user_timestamps) >= MAX_MESSAGES_PER_MINUTE:
        return True

    user_timestamps.append(now)
    return False


def sanitize_message(msg_data: dict) -> dict:
    """Sanitize and validate message data"""
    # Validate user field
    user = str(msg_data.get("user", "Anonymous"))[:50]  # Max 50 chars

    # Validate text field
    text = str(msg_data.get("text", ""))[:MAX_MESSAGE_LENGTH]
    if not text.strip():
        raise ValueError("Empty message")

    # Create sanitized message
    return {
        "user": user,
        "text": text,
        "timestamp": datetime.now().isoformat(),
        "date_created": datetime.now().strftime("%Y-%m-%d")
    }

