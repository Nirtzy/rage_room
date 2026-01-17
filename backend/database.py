"""Database configuration and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from backend.config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create engine with appropriate connection args
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
elif "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
    # PostgreSQL connection pooling
    connect_args = {"connect_timeout": 10}

try:
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,  # Verify connections before using
        echo=False  # Set to True for SQL query logging
    )
    logger.info(f"Database engine created for: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'local'}")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from backend.models import Message, User  # Import here to avoid circular imports
    from sqlalchemy import inspect, text
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
        
        # Check if user_id column exists in messages table, add it if missing
        # This handles databases created before user_id was added
        try:
            inspector = inspect(engine)
            if 'messages' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('messages')]
                if 'user_id' not in columns:
                    logger.info("Adding user_id column to messages table...")
                    with engine.begin() as conn:  # begin() auto-commits
                        conn.execute(text("ALTER TABLE messages ADD COLUMN user_id INTEGER"))
                    logger.info("user_id column added successfully")
        except Exception as migration_error:
            # If migration fails, log but don't crash - column might already exist
            logger.warning(f"Could not add user_id column (may already exist): {migration_error}")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

