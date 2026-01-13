"""Utility functions for message handling"""
from collections import deque
from typing import Dict
import time
from backend.config import MAX_MESSAGES_PER_MINUTE

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


