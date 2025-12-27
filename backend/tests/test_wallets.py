import pytest


@pytest.fixture
def second_user_data():
    """Second user for testing access denial."""
    return {
        "username": "otheruser",
        "email": "other@example.com",
        "password": "otherpassword123",
        "first_name": "Other",
        "last_name": "User",
    }


@pytest.fixture
def second_user_token(client, second_user_data):
    """Create second user and get auth token."""
    # Register
    client.post("/api/v1/auth/signup", json=second_user_data)
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": second_user_data["username"],
            "password": second_user_data["password"],
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def second_auth_headers(second_user_token):
    """Headers for second user."""
    return {"Authorization": f"Bearer {second_user_token}"}


@pytest.fixture
def wallet_data():
    """Sample wallet data."""
    return {
        "name": "Test Wallet",
        "type": "bank",
        "currency": "EUR",
        "initial_balance": "1000.00",
    }


@pytest.fixture
def created_wallet(client, auth_headers, wallet_data):
    """Create and return a wallet."""
    response = client.post(
        "/api/v1/wallets",
        json=wallet_data,
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


class TestListWallets:
    """Tests for GET /api/v1/wallets"""

    def test_list_wallets_empty(self, client, auth_headers):
        """Test listing wallets when none exist."""
        response = client.get("/api/v1/wallets", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_list_wallets_returns_user_wallets(self, client, auth_headers, created_wallet):
        """Test listing wallets returns user's wallets."""
        response = client.get("/api/v1/wallets", headers=auth_headers)

        assert response.status_code == 200
        wallets = response.json()
        assert len(wallets) == 1
        assert wallets[0]["name"] == created_wallet["name"]

    def test_list_wallets_unauthenticated(self, client):
        """Test listing wallets without auth fails."""
        response = client.get("/api/v1/wallets")

        assert response.status_code == 401


class TestCreateWallet:
    """Tests for POST /api/v1/wallets"""

    def test_create_wallet_success(self, client, auth_headers, wallet_data):
        """Test successful wallet creation."""
        response = client.post(
            "/api/v1/wallets",
            json=wallet_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == wallet_data["name"]
        assert data["type"] == wallet_data["type"]
        assert data["currency"] == wallet_data["currency"]
        assert "id" in data
        assert "balance" in data

    def test_create_wallet_different_types(self, client, auth_headers):
        """Test creating wallets with different types."""
        for wallet_type in ["bank", "cash", "digital", "stash"]:
            response = client.post(
                "/api/v1/wallets",
                json={"name": f"{wallet_type} wallet", "type": wallet_type},
                headers=auth_headers,
            )
            assert response.status_code == 201
            assert response.json()["type"] == wallet_type

    def test_create_wallet_unauthenticated(self, client, wallet_data):
        """Test creating wallet without auth fails."""
        response = client.post("/api/v1/wallets", json=wallet_data)

        assert response.status_code == 401

    def test_create_wallet_invalid_type(self, client, auth_headers):
        """Test creating wallet with invalid type fails."""
        response = client.post(
            "/api/v1/wallets",
            json={"name": "Bad Wallet", "type": "invalid"},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetWallet:
    """Tests for GET /api/v1/wallets/{id}"""

    def test_get_wallet_success(self, client, auth_headers, created_wallet):
        """Test getting own wallet."""
        response = client.get(
            f"/api/v1/wallets/{created_wallet['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == created_wallet["id"]
        assert response.json()["name"] == created_wallet["name"]

    def test_get_wallet_not_found(self, client, auth_headers):
        """Test getting non-existent wallet."""
        response = client.get("/api/v1/wallets/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_get_wallet_access_denied(
        self, client, auth_headers, second_auth_headers, created_wallet
    ):
        """Test accessing another user's wallet is denied."""
        # Try to access first user's wallet with second user's token
        response = client.get(
            f"/api/v1/wallets/{created_wallet['id']}",
            headers=second_auth_headers,
        )

        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_get_wallet_unauthenticated(self, client, created_wallet):
        """Test getting wallet without auth fails."""
        response = client.get(f"/api/v1/wallets/{created_wallet['id']}")

        assert response.status_code == 401


class TestUpdateWallet:
    """Tests for PATCH /api/v1/wallets/{id}"""

    def test_update_wallet_success(self, client, auth_headers, created_wallet):
        """Test updating own wallet."""
        response = client.patch(
            f"/api/v1/wallets/{created_wallet['id']}",
            json={"name": "Updated Wallet"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Wallet"

    def test_update_wallet_partial(self, client, auth_headers, created_wallet):
        """Test partial update only changes specified fields."""
        original_type = created_wallet["type"]

        response = client.patch(
            f"/api/v1/wallets/{created_wallet['id']}",
            json={"name": "New Name"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "New Name"
        assert response.json()["type"] == original_type

    def test_update_wallet_access_denied(
        self, client, auth_headers, second_auth_headers, created_wallet
    ):
        """Test updating another user's wallet is denied."""
        response = client.patch(
            f"/api/v1/wallets/{created_wallet['id']}",
            json={"name": "Hacked"},
            headers=second_auth_headers,
        )

        assert response.status_code == 403

    def test_update_wallet_not_found(self, client, auth_headers):
        """Test updating non-existent wallet."""
        response = client.patch(
            "/api/v1/wallets/99999",
            json={"name": "Ghost"},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestDeleteWallet:
    """Tests for DELETE /api/v1/wallets/{id}"""

    def test_delete_wallet_success(self, client, auth_headers, created_wallet):
        """Test deleting own wallet."""
        response = client.delete(
            f"/api/v1/wallets/{created_wallet['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(
            f"/api/v1/wallets/{created_wallet['id']}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_wallet_access_denied(
        self, client, auth_headers, second_auth_headers, created_wallet
    ):
        """Test deleting another user's wallet is denied."""
        response = client.delete(
            f"/api/v1/wallets/{created_wallet['id']}",
            headers=second_auth_headers,
        )

        assert response.status_code == 403

    def test_delete_wallet_not_found(self, client, auth_headers):
        """Test deleting non-existent wallet."""
        response = client.delete("/api/v1/wallets/99999", headers=auth_headers)

        assert response.status_code == 404
