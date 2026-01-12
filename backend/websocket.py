"""WebSocket handling and background tasks"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set
from datetime import datetime, time as dt_time
import asyncio
import json
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import Message
from backend.utils import is_rate_limited, sanitize_message
from backend.config import MAX_CONNECTIONS

# Track connected clients
connected_clients: Set[WebSocket] = set()


async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections"""
    # Check connection limit
    if len(connected_clients) >= MAX_CONNECTIONS:
        await websocket.close(code=1008, reason="Server full")
        return

    await websocket.accept()
    connected_clients.add(websocket)

    # Get database session
    db = SessionLocal()

    try:
        # Small delay to ensure WebSocket is fully ready
        await asyncio.sleep(0.1)

        # Send message history to new user
        today = datetime.now().strftime("%Y-%m-%d")
        messages = db.query(Message).filter(
            Message.date_created == today
        ).order_by(Message.timestamp).all()

        print(f"Sending {len(messages)} messages to new user")
        for msg in messages:
            await websocket.send_text(json.dumps(msg.to_dict()))

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

                # Save to database
                db_message = Message(
                    user=sanitized_msg["user"],
                    text=sanitized_msg["text"],
                    timestamp=datetime.fromisoformat(sanitized_msg["timestamp"]),
                    date_created=sanitized_msg["date_created"]
                )
                db.add(db_message)
                db.commit()
                db.refresh(db_message)

                # Broadcast to all clients
                await broadcast(db_message.to_dict())

            except (json.JSONDecodeError, ValueError) as e:
                # Invalid message format
                await websocket.send_text(json.dumps({
                    "user": "System",
                    "text": "Invalid message format",
                    "timestamp": datetime.now().isoformat()
                }))

    except WebSocketDisconnect:
        connected_clients.discard(websocket)
    finally:
        db.close()


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


async def midnight_clear_task():
    """Clear messages at midnight every day"""
    db = SessionLocal()
    last_clear_date = datetime.now().date()

    try:
        while True:
            now = datetime.now()

            # Check if it's a new day
            if now.date() != last_clear_date:
                # Clear messages at midnight
                if now.time() >= dt_time(0, 0) and now.time() < dt_time(0, 5):
                    yesterday = last_clear_date.strftime("%Y-%m-%d")
                    deleted = db.query(Message).filter(
                        Message.date_created == yesterday
                    ).delete()
                    db.commit()

                    last_clear_date = now.date()
                    print(f"Messages cleared at midnight: {now} - Deleted {deleted} messages")

                    # Notify all connected clients
                    await broadcast_system_message("Messages have been cleared for a new day!")

            # Check every minute
            await asyncio.sleep(60)
    finally:
        db.close()


async def keep_alive_task():
    """Keep the server alive by logging heartbeat"""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes

        db = SessionLocal()
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            message_count = db.query(Message).filter(Message.date_created == today).count()
            print(f"[HEARTBEAT] Server alive - {message_count} messages, {len(connected_clients)} clients")
        finally:
            db.close()

