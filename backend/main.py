"""
Rage Room - Daily Chat Application
Main application entry point
"""
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import asyncio

from backend.config import ALLOWED_ORIGINS, STATIC_DIR
from backend.database import init_db
from backend.routes import router
from backend.websocket import websocket_endpoint, midnight_clear_task, keep_alive_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    # Startup
    print("=" * 50)
    print("SERVER STARTING UP")
    print(f"Current date: {datetime.now()}")

    # Initialize database
    init_db()

    # Start background tasks
    print("Starting background tasks...")
    asyncio.create_task(midnight_clear_task())
    asyncio.create_task(keep_alive_task())

    print("Server startup complete!")
    print("=" * 50)

    yield  # Server runs here

    # Shutdown
    print("=" * 50)
    print("SERVER SHUTTING DOWN")
    print("=" * 50)


# Initialize FastAPI app with lifespan
app = FastAPI(title="Rage Room", version="1.0.0", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routes
app.include_router(router)


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket_endpoint(websocket)

