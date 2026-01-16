"""
Initialize admin user from environment variables
Run this script once to create the admin account
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal, init_db
from backend.models import User
from backend.auth import get_password_hash
from backend.config import ADMIN_EMAIL, ADMIN_PASSWORD


def create_admin_user():
    """Create or update admin user from environment variables"""
    if not ADMIN_PASSWORD:
        print("ERROR: ADMIN_PASSWORD environment variable is not set!")
        print("Please set ADMIN_PASSWORD before running this script.")
        return False

    # Initialize database
    init_db()

    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()

        if admin:
            print(f"Admin user already exists: {ADMIN_EMAIL}")
            # Update password if changed
            admin.hashed_password = get_password_hash(ADMIN_PASSWORD)
            admin.is_admin = True
            admin.is_active = True
            print("Admin password updated!")
        else:
            # Create new admin user
            admin = User(
                email=ADMIN_EMAIL,
                username="admin",
                hashed_password=get_password_hash(ADMIN_PASSWORD),
                is_admin=True,
                is_active=True
            )
            db.add(admin)
            print(f"Created new admin user: {ADMIN_EMAIL}")

        db.commit()
        print("✅ Admin user initialized successfully!")
        return True

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()

