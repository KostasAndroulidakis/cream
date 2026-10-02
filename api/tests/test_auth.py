import pytest


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
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

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
