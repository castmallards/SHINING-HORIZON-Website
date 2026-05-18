import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.services.auth import AuthService


# Matches init_db.py defaults — tests reset this user so login is deterministic.
TEST_ADMIN_USERNAME = "admin"
TEST_ADMIN_PASSWORD = "admin123"


@pytest.fixture(scope="session", autouse=True)
def ensure_known_admin_user():
    """Guarantee a super-admin exists with known credentials for auth tests."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == TEST_ADMIN_USERNAME).first()
        if user:
            user.password_hash = AuthService.hash_password(TEST_ADMIN_PASSWORD)
            user.role = UserRole.SUPER_ADMIN
            user.is_active = True
        else:
            db.add(
                User(
                    username=TEST_ADMIN_USERNAME,
                    email="admin@shininghorizon.com",
                    full_name="Test Super Admin",
                    role=UserRole.SUPER_ADMIN,
                    password_hash=AuthService.hash_password(TEST_ADMIN_PASSWORD),
                )
            )
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    """Share Test Client for API/router tests."""
    # What to TODO: add test database

    with TestClient(app) as client:
        yield client