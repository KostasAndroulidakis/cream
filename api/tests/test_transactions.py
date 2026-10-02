import pytest
from datetime import datetime, timezone


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
    client.post("/api/v1/auth/signup", json=second_user_data)
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


@pytest.fixture
def second_wallet(client, auth_headers):
    """Create a second wallet for the same user."""
    response = client.post(
        "/api/v1/wallets",
        json={"name": "Second Wallet", "type": "cash"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def other_user_wallet(client, second_auth_headers):
    """Create a wallet owned by the second user."""
    response = client.post(
        "/api/v1/wallets",
        json={"name": "Other User Wallet", "type": "bank"},
        headers=second_auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def category_data():
    """Sample category data."""
    return {
        "name": "Groceries",
        "type": "expense",
    }


@pytest.fixture
def created_category(client, auth_headers, category_data):
    """Create and return a category."""
    response = client.post(
        "/api/v1/categories",
        json=category_data,
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def transaction_data(created_wallet, created_category):
    """Sample transaction data."""
    return {
        "wallet_id": created_wallet["id"],
        "category_id": created_category["id"],
        "amount": "-50.00",
        "description": "Weekly groceries",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def created_transaction(client, auth_headers, transaction_data):
    """Create and return a transaction."""
    response = client.post(
        "/api/v1/transactions",
        json=transaction_data,
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


class TestListTransactions:
    """Tests for GET /api/v1/transactions"""

    def test_list_transactions_empty(self, client, auth_headers, created_wallet):
        """Test listing transactions when none exist."""
        response = client.get("/api/v1/transactions", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_list_transactions_returns_user_transactions(
        self, client, auth_headers, created_transaction
    ):
        """Test listing transactions returns user's transactions."""
        response = client.get("/api/v1/transactions", headers=auth_headers)

        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) == 1
        assert transactions[0]["id"] == created_transaction["id"]

    def test_list_transactions_filtered_by_wallet(
        self, client, auth_headers, created_wallet, second_wallet, created_category
    ):
        """Test filtering transactions by wallet_id."""
        # Create transaction in first wallet
        client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": created_wallet["id"],
                "category_id": created_category["id"],
                "amount": "-10.00",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
            headers=auth_headers,
        )
        # Create transaction in second wallet
        client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": second_wallet["id"],
                "category_id": created_category["id"],
                "amount": "-20.00",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
            headers=auth_headers,
        )

        # Filter by first wallet
        response = client.get(
            f"/api/v1/transactions?wallet_id={created_wallet['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) == 1
        assert transactions[0]["wallet_id"] == created_wallet["id"]

    def test_list_transactions_filter_other_user_wallet_denied(
        self, client, auth_headers, other_user_wallet
    ):
        """Test filtering by another user's wallet is denied."""
        response = client.get(
            f"/api/v1/transactions?wallet_id={other_user_wallet['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_list_transactions_unauthenticated(self, client):
        """Test listing transactions without auth fails."""
        response = client.get("/api/v1/transactions")

        assert response.status_code == 401

    def test_list_transactions_does_not_include_other_user(
        self, client, auth_headers, second_auth_headers, created_transaction, other_user_wallet
    ):
        """Test that listing doesn't include other user's transactions."""
        # Create a category for second user
        cat_response = client.post(
            "/api/v1/categories",
            json={"name": "Other Category", "type": "expense"},
            headers=second_auth_headers,
        )
        other_category_id = cat_response.json()["id"]

        # Create transaction for second user
        client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": other_user_wallet["id"],
                "category_id": other_category_id,
                "amount": "-100.00",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
            headers=second_auth_headers,
        )

        # First user should only see their own transaction
        response = client.get("/api/v1/transactions", headers=auth_headers)

        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) == 1
        assert transactions[0]["id"] == created_transaction["id"]


class TestCreateTransaction:
    """Tests for POST /api/v1/transactions"""

    def test_create_transaction_success(
        self, client, auth_headers, transaction_data
    ):
        """Test successful transaction creation."""
        response = client.post(
            "/api/v1/transactions",
            json=transaction_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["wallet_id"] == transaction_data["wallet_id"]
        assert data["category_id"] == transaction_data["category_id"]
        assert data["amount"] == "-50.0000"  # NUMERIC(19,4) precision
        assert data["description"] == transaction_data["description"]
        assert "id" in data
        assert "created_at" in data

    def test_create_transaction_income(
        self, client, auth_headers, created_wallet, created_category
    ):
        """Test creating income transaction (positive amount)."""
        response = client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": created_wallet["id"],
                "category_id": created_category["id"],
                "amount": "1500.00",
                "description": "Salary",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["amount"] == "1500.0000"

    def test_create_transaction_without_description(
        self, client, auth_headers, created_wallet, created_category
    ):
        """Test creating transaction without description."""
        response = client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": created_wallet["id"],
                "category_id": created_category["id"],
                "amount": "-25.00",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["description"] is None

    def test_create_transaction_other_user_wallet_denied(
        self, client, auth_headers, other_user_wallet, created_category
    ):
        """Test creating transaction in another user's wallet is denied."""
        response = client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": other_user_wallet["id"],
                "category_id": created_category["id"],
                "amount": "-50.00",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_create_transaction_nonexistent_wallet(
        self, client, auth_headers, created_category
    ):
        """Test creating transaction with non-existent wallet fails."""
        response = client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": 99999,
                "category_id": created_category["id"],
                "amount": "-50.00",
                "occurred_at": datetime.now(timezone.utc).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "Wallet not found" in response.json()["detail"]

    def test_create_transaction_unauthenticated(self, client, transaction_data):
        """Test creating transaction without auth fails."""
        response = client.post("/api/v1/transactions", json=transaction_data)

        assert response.status_code == 401

    def test_create_transaction_missing_fields(self, client, auth_headers):
        """Test creating transaction with missing fields fails."""
        response = client.post(
            "/api/v1/transactions",
            json={"amount": "-50.00"},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetTransaction:
    """Tests for GET /api/v1/transactions/{id}"""

    def test_get_transaction_success(
        self, client, auth_headers, created_transaction
    ):
        """Test getting own transaction."""
        response = client.get(
            f"/api/v1/transactions/{created_transaction['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == created_transaction["id"]
        assert response.json()["amount"] == created_transaction["amount"]

    def test_get_transaction_not_found(self, client, auth_headers):
        """Test getting non-existent transaction."""
        response = client.get("/api/v1/transactions/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_get_transaction_access_denied(
        self, client, auth_headers, second_auth_headers, created_transaction
    ):
        """Test accessing another user's transaction is denied."""
        response = client.get(
            f"/api/v1/transactions/{created_transaction['id']}",
            headers=second_auth_headers,
        )

        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_get_transaction_unauthenticated(self, client, created_transaction):
        """Test getting transaction without auth fails."""
        response = client.get(f"/api/v1/transactions/{created_transaction['id']}")

        assert response.status_code == 401


class TestUpdateTransaction:
    """Tests for PATCH /api/v1/transactions/{id}"""

    def test_update_transaction_success(
        self, client, auth_headers, created_transaction
    ):
        """Test updating own transaction."""
        response = client.patch(
            f"/api/v1/transactions/{created_transaction['id']}",
            json={"amount": "-75.00"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["amount"] == "-75.0000"

    def test_update_transaction_partial(
        self, client, auth_headers, created_transaction
    ):
        """Test partial update only changes specified fields."""
        original_amount = created_transaction["amount"]

        response = client.patch(
            f"/api/v1/transactions/{created_transaction['id']}",
            json={"description": "Updated description"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"
        assert response.json()["amount"] == original_amount

    def test_update_transaction_category(
        self, client, auth_headers, created_transaction
    ):
        """Test updating transaction category."""
        # Create another category
        cat_response = client.post(
            "/api/v1/categories",
            json={"name": "Dining", "type": "expense"},
            headers=auth_headers,
        )
        new_category_id = cat_response.json()["id"]

        response = client.patch(
            f"/api/v1/transactions/{created_transaction['id']}",
            json={"category_id": new_category_id},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["category_id"] == new_category_id

    def test_update_transaction_access_denied(
        self, client, auth_headers, second_auth_headers, created_transaction
    ):
        """Test updating another user's transaction is denied."""
        response = client.patch(
            f"/api/v1/transactions/{created_transaction['id']}",
            json={"amount": "-999.00"},
            headers=second_auth_headers,
        )

        assert response.status_code == 403

    def test_update_transaction_not_found(self, client, auth_headers):
        """Test updating non-existent transaction."""
        response = client.patch(
            "/api/v1/transactions/99999",
            json={"amount": "-10.00"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_transaction_unauthenticated(self, client, created_transaction):
        """Test updating transaction without auth fails."""
        response = client.patch(
            f"/api/v1/transactions/{created_transaction['id']}",
            json={"amount": "-10.00"},
        )

        assert response.status_code == 401


class TestDeleteTransaction:
    """Tests for DELETE /api/v1/transactions/{id}"""

    def test_delete_transaction_success(
        self, client, auth_headers, created_transaction
    ):
        """Test deleting own transaction."""
        response = client.delete(
            f"/api/v1/transactions/{created_transaction['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(
            f"/api/v1/transactions/{created_transaction['id']}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_transaction_access_denied(
        self, client, auth_headers, second_auth_headers, created_transaction
    ):
        """Test deleting another user's transaction is denied."""
        response = client.delete(
            f"/api/v1/transactions/{created_transaction['id']}",
            headers=second_auth_headers,
        )

        assert response.status_code == 403

    def test_delete_transaction_not_found(self, client, auth_headers):
        """Test deleting non-existent transaction."""
        response = client.delete("/api/v1/transactions/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_transaction_unauthenticated(self, client, created_transaction):
        """Test deleting transaction without auth fails."""
        response = client.delete(f"/api/v1/transactions/{created_transaction['id']}")

        assert response.status_code == 401
