from tests.conftest import TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME


def test_login_rejects_invalid_credentials(client):
    payload = {
        "username": "invalid_user",
        "password": "invalid_password",
    }

    response = client.post("/api/auth/login", json=payload)

    assert response.status_code == 401
    body = response.json()
    assert "detail" in body
    assert body["detail"] == "Invalid username or password"


def test_login_success_returns_token_and_sets_session_cookie(client):
    payload = {"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD}

    response = client.post("/api/auth/login", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body.get("token_type") == "bearer"
    assert isinstance(body.get("access_token"), str) and body["access_token"]

    user = body.get("user") or {}
    assert user.get("username") == TEST_ADMIN_USERNAME
    assert user.get("role") == "super_admin"

    set_cookie = response.headers.get("set-cookie", "")
    assert "sh_session=" in set_cookie
    assert "HttpOnly" in set_cookie


def test_me_returns_current_user_after_login(client):
    login = client.post(
        "/api/auth/login",
        json={"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD},
    )
    assert login.status_code == 200

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    data = me.json()
    assert data["username"] == TEST_ADMIN_USERNAME
    assert data["role"] == "super_admin"


def test_me_requires_authentication(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    body = response.json()
    assert "detail" in body


def test_logout_clears_session_and_me_requires_auth_again(client):
    login = client.post(
        "/api/auth/login",
        json={"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD},
    )
    assert login.status_code == 200

    csrf_token = client.cookies.get("csrf_token")
    assert csrf_token

    logout = client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert logout.status_code == 200

    me = client.get("/api/auth/me")
    assert me.status_code == 401