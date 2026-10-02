import pytest

from app.config import settings
from tests.conftest import login_session_headers

ME_URL = "/api/v1/auth/me"
LOGOUT_URL = "/api/v1/auth/logout"


class TestSignup:
    """Tests for POST /api/v1/auth/signup"""

    def test_signup_success(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/signup", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["first_name"] == test_user_data["first_name"]
        assert data["last_name"] == test_user_data["last_name"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_signup_duplicate_username(self, client, test_user_data, registered_user):
        """Test signup with existing username fails."""
        # Try to register with same username
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@example.com"

        response = client.post("/api/v1/auth/signup", json=duplicate_data)

        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]

    def test_signup_duplicate_email(self, client, test_user_data, registered_user):
        """Test signup with existing email fails."""
        # Try to register with same email
        duplicate_data = test_user_data.copy()
        duplicate_data["username"] = "differentuser"

        response = client.post("/api/v1/auth/signup", json=duplicate_data)

        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]

    def test_signup_invalid_email(self, client, test_user_data):
        """Test signup with invalid email fails."""
        invalid_data = test_user_data.copy()
        invalid_data["email"] = "not-an-email"

        response = client.post("/api/v1/auth/signup", json=invalid_data)

        assert response.status_code == 422  # Validation error

    def test_signup_missing_fields(self, client):
        """Test signup with missing fields fails."""
        response = client.post("/api/v1/auth/signup", json={})

        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/v1/auth/login"""

    def test_login_success(self, client, test_user_data, registered_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user_data["username"],
                "password": test_user_data["password"],
            },
        )

        assert response.status_code == 200
        assert response.json()["username"] == test_user_data["username"]
        assert "access_token" not in response.json()

        cookie = response.headers["set-cookie"].lower()
        assert cookie.startswith(f"{settings.auth_cookie_name}=")
        assert "httponly" in cookie
        assert "samesite=strict" in cookie
        assert "path=/api" in cookie

    def test_login_wrong_password(self, client, test_user_data, registered_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user_data["username"],
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password",
            },
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_missing_fields(self, client):
        """Test login with missing fields fails."""
        response = client.post("/api/v1/auth/login", json={})

        assert response.status_code == 422


class TestMe:
    """Tests for GET /api/v1/auth/me"""

    def test_me_returns_current_user(self, client, test_user_data, auth_headers):
        response = client.get(ME_URL, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert "password_hash" not in data

    def test_me_identifies_each_user(self, client, auth_headers, second_auth_headers, second_user_data):
        response = client.get(ME_URL, headers=second_auth_headers)

        assert response.json()["username"] == second_user_data["username"]

    def test_me_without_session(self, client):
        response = client.get(ME_URL)

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_me_with_invalid_token(self, client):
        response = client.get(ME_URL, headers={"Cookie": f"{settings.auth_cookie_name}=not-a-jwt"})

        assert response.status_code == 401

    def test_bearer_header_is_not_accepted(self, client, test_user_data, registered_user):
        cookie_header = login_session_headers(client, test_user_data["username"], test_user_data["password"])
        token = cookie_header["Cookie"].split("=", 1)[1]

        response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/v1/auth/logout"""

    def test_logout_clears_cookie(self, client, auth_headers):
        response = client.post(LOGOUT_URL, headers=auth_headers)

        assert response.status_code == 204
        cookie = response.headers["set-cookie"].lower()
        assert cookie.startswith(f"{settings.auth_cookie_name}=")
        assert "max-age=0" in cookie
        assert "path=/api" in cookie

    def test_logout_without_session_is_harmless(self, client):
        response = client.post(LOGOUT_URL)

        assert response.status_code == 204
