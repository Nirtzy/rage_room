from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, time as dt_time
from collections import deque
import asyncio
import json
from typing import Dict, Set
import time
from pathlib import Path

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

# File to store messages
MESSAGES_FILE = Path("messages.json")
METADATA_FILE = Path("messages_metadata.json")

# Store messages in memory (will be cleared at midnight)
messages = deque(maxlen=1000)  # Limit to 1000 messages max
connected_clients: Set[WebSocket] = set()
last_clear_date = datetime.now().date()

# Rate limiting: track messages per user
user_message_timestamps: Dict[str, deque] = {}
MAX_MESSAGES_PER_MINUTE = 25
MAX_MESSAGE_LENGTH = 500
MAX_CONNECTIONS = 100

def load_messages():
    """Load messages from file on startup"""
    global messages, last_clear_date

    try:
        # Load metadata
        if METADATA_FILE.exists():
            with open(METADATA_FILE, 'r') as f:
                metadata = json.load(f)
                stored_date = datetime.fromisoformat(metadata['last_clear_date']).date()

                # If it's a new day, don't load old messages
                if stored_date != datetime.now().date():
                    print(f"New day detected. Not loading messages from {stored_date}")
                    last_clear_date = datetime.now().date()
                    save_messages()  # Clear the file
                    return

                last_clear_date = stored_date

        # Load messages
        if MESSAGES_FILE.exists():
            with open(MESSAGES_FILE, 'r') as f:
                stored_messages = json.load(f)
                messages.extend(stored_messages)
                print(f"Loaded {len(messages)} messages from file")
        else:
            print("No existing messages file found")
    except Exception as e:
        print(f"Error loading messages: {e}")

def save_messages():
    """Save messages to file"""
    try:
        # Save messages
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(list(messages), f)

        # Save metadata
        with open(METADATA_FILE, 'w') as f:
            json.dump({
                'last_clear_date': last_clear_date.isoformat(),
                'message_count': len(messages)
            }, f)

        print(f"Saved {len(messages)} messages to file")
    except Exception as e:
        print(f"Error saving messages: {e}")

@app.on_event("startup")
async def startup_event():
    """Start the midnight clearing task and load messages"""
    print("=" * 50)
    print("SERVER STARTING UP")
    print(f"Current date: {datetime.now()}")
    load_messages()
    print(f"Messages loaded: {len(messages)}")
    print("Starting background tasks...")
    asyncio.create_task(midnight_clear_task())
    asyncio.create_task(periodic_save_task())
    asyncio.create_task(keep_alive_task())
    print("Server startup complete!")
    print("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Save messages before shutdown"""
    print("=" * 50)
    print("SERVER SHUTTING DOWN")
    save_messages()
    print(f"Final save: {len(messages)} messages saved")
    print("=" * 50)

async def keep_alive_task():
    """Keep the server alive by logging heartbeat"""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        print(f"[HEARTBEAT] Server alive - {len(messages)} messages, {len(connected_clients)} clients")

async def periodic_save_task():
    """Save messages every 30 seconds"""
    while True:
        await asyncio.sleep(30)
        save_messages()

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
                save_messages()  # Save after clearing
                print(f"Messages cleared at midnight: {now}")

                # Notify all connected clients
                await broadcast_system_message("Messages have been cleared for a new day!")

        # Check every minute
        await asyncio.sleep(60)

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "message_count": len(messages),
        "connected_clients": len(connected_clients),
        "last_clear_date": last_clear_date.isoformat()
    }

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
