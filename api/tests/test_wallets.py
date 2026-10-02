import pytest


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


WALLETS_URL = "/api/v1/wallets"
TOTALS_URL = f"{WALLETS_URL}/totals"


def _create_wallet(client, headers, **fields):
    response = client.post(WALLETS_URL, json={"name": "Wallet", **fields}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def _add_transaction(client, headers, wallet_id, amount):
    category = client.post(
        "/api/v1/categories", json={"name": "Misc", "type": "expense"}, headers=headers
    ).json()
    response = client.post(
        "/api/v1/transactions",
        json={
            "wallet_id": wallet_id,
            "category_id": category["id"],
            "amount": amount,
            "occurred_at": "2026-01-15T10:00:00Z",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text


class TestWalletCurrency:
    """Currency codes are normalized and validated."""

    def test_currency_is_uppercased(self, client, auth_headers):
        wallet = _create_wallet(client, auth_headers, currency=" usd ")

        assert wallet["currency"] == "USD"

    @pytest.mark.parametrize("currency", ["EU", "EURO", "E1R", "€€€"])
    def test_invalid_currency_rejected(self, client, auth_headers, currency):
        response = client.post(WALLETS_URL, json={"name": "W", "currency": currency}, headers=auth_headers)

        assert response.status_code == 422

    def test_currency_change_allowed_without_transactions(self, client, auth_headers, created_wallet):
        response = client.patch(
            f"{WALLETS_URL}/{created_wallet['id']}", json={"currency": "USD"}, headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["currency"] == "USD"

    def test_currency_change_blocked_with_transactions(self, client, auth_headers, created_wallet):
        _add_transaction(client, auth_headers, created_wallet["id"], "-10.00")

        response = client.patch(
            f"{WALLETS_URL}/{created_wallet['id']}", json={"currency": "USD"}, headers=auth_headers
        )

        assert response.status_code == 409

    def test_same_currency_update_allowed_with_transactions(self, client, auth_headers, created_wallet):
        _add_transaction(client, auth_headers, created_wallet["id"], "-10.00")

        response = client.patch(
            f"{WALLETS_URL}/{created_wallet['id']}",
            json={"currency": "eur", "name": "Renamed"},
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestWalletTotals:
    """Tests for GET /api/v1/wallets/totals"""

    def test_totals_empty(self, client, auth_headers):
        response = client.get(TOTALS_URL, headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_totals_grouped_by_currency(self, client, auth_headers):
        first = _create_wallet(client, auth_headers, currency="EUR", initial_balance="100.50")
        _create_wallet(client, auth_headers, currency="EUR", initial_balance="200.25")
        _create_wallet(client, auth_headers, currency="USD", initial_balance="50")
        _add_transaction(client, auth_headers, first["id"], "-0.75")

        totals = client.get(TOTALS_URL, headers=auth_headers).json()

        assert totals == [
            {"currency": "EUR", "balance": "300.0000", "wallet_count": 2},
            {"currency": "USD", "balance": "50.0000", "wallet_count": 1},
        ]

    def test_totals_only_include_own_wallets(self, client, auth_headers, second_auth_headers):
        _create_wallet(client, second_auth_headers, initial_balance="999")

        assert client.get(TOTALS_URL, headers=auth_headers).json() == []

    def test_totals_unauthenticated(self, client):
        assert client.get(TOTALS_URL).status_code == 401
