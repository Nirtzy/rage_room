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
import logging

from backend.config import ALLOWED_ORIGINS, STATIC_DIR, ADMIN_EMAIL, ADMIN_PASSWORD
from backend.database import init_db, SessionLocal
from backend.routes import router
from backend.auth_routes import router as auth_router
from backend.admin_routes import router as admin_router
from backend.websocket import websocket_endpoint, midnight_clear_task, keep_alive_task
from backend.models import User
from backend.auth import get_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    # Startup
    print("=" * 50)
    print("SERVER STARTING UP")
    print(f"Current date: {datetime.now()}")

    # Initialize database
    init_db()

    # Create admin user if it doesn't exist and password is set
    if ADMIN_PASSWORD:
        db = SessionLocal()
        try:
            admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
            if not admin:
                admin = User(
                    email=ADMIN_EMAIL,
                    username="admin",
                    hashed_password=get_password_hash(ADMIN_PASSWORD),
                    is_admin=True,
                    is_active=True
                )
                db.add(admin)
                db.commit()
                logger.info(f"✅ Admin user created: {ADMIN_EMAIL}")
            else:
                # Update password if admin exists (in case password changed)
                admin.hashed_password = get_password_hash(ADMIN_PASSWORD)
                admin.is_admin = True
                admin.is_active = True
                db.commit()
                logger.info(f"ℹ️  Admin user already exists: {ADMIN_EMAIL} (password updated)")
        except Exception as e:
            logger.error(f"⚠️  Error creating/updating admin user: {e}")
            db.rollback()
        finally:
            db.close()
    else:
        logger.warning("⚠️  ADMIN_PASSWORD not set - admin user not created")

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
# When using ["*"], credentials must be False
# For production, set ALLOWED_ORIGINS env var with specific domains
# Note: Authorization headers work with allow_credentials=False, but cookies won't
if ALLOWED_ORIGINS == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # Cannot use True with ["*"]
        allow_methods=["*"],
        allow_headers=["*"],  # This includes Authorization header
        expose_headers=["*"],  # Expose all headers to client
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routes
app.include_router(router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket_endpoint(websocket)

