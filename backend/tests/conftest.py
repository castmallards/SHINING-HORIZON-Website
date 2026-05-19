import os

# Settings() runs at import time (via app.main). CI writes backend/.env from
# .env.example; locally pytest may run without .env — set a valid key first.
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"
os.environ["LOGIN_RATE_LIMIT"] = "1000/minute"

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


def csrf_headers(client: TestClient) -> dict[str, str]:
    """Headers required for POST/PUT/PATCH/DELETE on /api/* (see CSRFMiddleware)."""
    token = client.cookies.get("csrf_token")
    assert token, "CSRF cookie missing — log in before mutating requests"
    return {"X-CSRF-Token": token}


@pytest.fixture
def auth_client(client):
    """API client with an authenticated super-admin session."""
    login = client.post(
        "/api/auth/login",
        json={"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD},
    )
    assert login.status_code == 200
    return client