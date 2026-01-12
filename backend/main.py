from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, time as dt_time
from collections import deque
import asyncio
import json
from typing import Dict, Set
import time

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Store messages in memory (will be cleared at midnight)
messages = deque(maxlen=1000)  # Limit to 1000 messages max
connected_clients: Set[WebSocket] = set()
last_clear_date = datetime.now().date()

# Rate limiting: track messages per user
user_message_timestamps: Dict[str, deque] = {}
MAX_MESSAGES_PER_MINUTE = 25
MAX_MESSAGE_LENGTH = 500
MAX_CONNECTIONS = 100

@app.on_event("startup")
async def startup_event():
    """Start the midnight clearing task"""
    asyncio.create_task(midnight_clear_task())

async def midnight_clear_task():
    """Clear messages at midnight every day"""
    global messages, last_clear_date
    while True:
        now = datetime.now()

        # Check if it's a new day
        if now.date() != last_clear_date:
            # Clear messages at midnight
            if now.time() >= dt_time(0, 0) and now.time() < dt_time(0, 5):
                messages.clear()
                last_clear_date = now.date()
                print(f"Messages cleared at midnight: {now}")

                # Notify all connected clients
                await broadcast_system_message("Messages have been cleared for a new day!")

        # Check every minute
        await asyncio.sleep(60)

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.get("/api/today")
async def get_today():
    now = datetime.now()
    return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "title": "today's topic: what you think about ICE?",
            "rules": "no rules, just speak your mind!",
            "image_url": "/static/ice_image.jpg"
        }

@app.get("/api/messages")
async def get_messages():
    """Get message history for new users"""
    return {"messages": list(messages)}

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
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Check connection limit
    if len(connected_clients) >= MAX_CONNECTIONS:
        await websocket.close(code=1008, reason="Server full")
        return

    await websocket.accept()
    connected_clients.add(websocket)

    try:
        # Small delay to ensure WebSocket is fully ready
        await asyncio.sleep(0.1)

        # Send message history to new user
        print(f"Sending {len(messages)} messages to new user")
        for msg in messages:
            await websocket.send_text(json.dumps(msg))

        while True:
            data = await websocket.receive_text()

            try:
                msg_data = json.loads(data)

                # Rate limiting
                user = msg_data.get("user", "Anonymous")
                if is_rate_limited(user):
                    await websocket.send_text(json.dumps({
                        "user": "System",
                        "text": "You're sending messages too quickly. Please slow down.",
                        "timestamp": datetime.now().isoformat()
                    }))
                    continue

                # Sanitize message
                sanitized_msg = sanitize_message(msg_data)

                # Store message
                messages.append(sanitized_msg)

                # Broadcast to all clients
                await broadcast(sanitized_msg)

            except (json.JSONDecodeError, ValueError) as e:
                # Invalid message format
                await websocket.send_text(json.dumps({
                    "user": "System",
                    "text": "Invalid message format",
                    "timestamp": datetime.now().isoformat()
                }))

    except WebSocketDisconnect:
        connected_clients.discard(websocket)

async def broadcast(message: dict):
    """Broadcast message to all connected clients"""
    message_json = json.dumps(message)
    to_remove = []

    for client in connected_clients:
        try:
            await client.send_text(message_json)
        except Exception:
            to_remove.append(client)

    for c in to_remove:
        connected_clients.discard(c)

async def broadcast_system_message(text: str):
    """Send a system message to all connected clients"""
    msg = {
        "user": "System",
        "text": text,
        "timestamp": datetime.now().isoformat()
    }
    await broadcast(msg)
