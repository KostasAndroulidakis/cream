import pytest
from datetime import datetime, timezone, timedelta


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
    """Create a second wallet."""
    response = client.post(
        "/api/v1/wallets",
        json={"name": "Cash Wallet", "type": "cash", "initial_balance": "500.00"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def expense_category(client, auth_headers):
    """Create an expense category."""
    response = client.post(
        "/api/v1/categories",
        json={"name": "Groceries", "type": "expense"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def income_category(client, auth_headers):
    """Create an income category."""
    response = client.post(
        "/api/v1/categories",
        json={"name": "Salary", "type": "income"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def sample_transactions(client, auth_headers, created_wallet, expense_category, income_category):
    """Create sample transactions for testing."""
    now = datetime.now(timezone.utc)
    transactions = []

    # Income transaction
    response = client.post(
        "/api/v1/transactions",
        json={
            "wallet_id": created_wallet["id"],
            "category_id": income_category["id"],
            "amount": "3000.00",
            "description": "Monthly salary",
            "occurred_at": now.isoformat(),
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    transactions.append(response.json())

    # Expense transactions
    for i in range(3):
        response = client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": created_wallet["id"],
                "category_id": expense_category["id"],
                "amount": "-100.00",
                "description": f"Grocery shopping {i+1}",
                "occurred_at": now.isoformat(),
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        transactions.append(response.json())

    return transactions


class TestGetStatistics:
    """Tests for GET /api/v1/statistics"""

    def test_statistics_empty(self, client, auth_headers):
        """Test statistics with no data."""
        response = client.get("/api/v1/statistics", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_balance"] == "0"
        assert data["total_income"] == "0"
        assert data["total_expenses"] == "0"
        assert data["wallet_balances"] == []
        assert data["spending_by_category"] == []
        assert data["income_by_category"] == []

    def test_statistics_with_wallet_only(self, client, auth_headers, created_wallet):
        """Test statistics with wallet but no transactions."""
        response = client.get("/api/v1/statistics", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_balance"] == "1000.0000"
        # SQLite returns integer 0, PostgreSQL returns 0.0000
        assert float(data["total_income"]) == 0
        assert float(data["total_expenses"]) == 0
        assert len(data["wallet_balances"]) == 1
        assert data["wallet_balances"][0]["wallet_name"] == "Test Wallet"
        assert data["wallet_balances"][0]["balance"] == "1000.0000"

    def test_statistics_with_transactions(
        self, client, auth_headers, created_wallet, sample_transactions
    ):
        """Test statistics with transactions."""
        response = client.get("/api/v1/statistics", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Balance: 1000 (initial) + 3000 (income) - 300 (expenses) = 3700
        assert float(data["total_balance"]) == 3700.0
        assert float(data["total_income"]) == 3000.0
        assert float(data["total_expenses"]) == 300.0

        # Check category breakdowns
        assert len(data["spending_by_category"]) == 1
        assert data["spending_by_category"][0]["category_name"] == "Groceries"
        assert float(data["spending_by_category"][0]["total"]) == 300.0

        assert len(data["income_by_category"]) == 1
        assert data["income_by_category"][0]["category_name"] == "Salary"
        assert float(data["income_by_category"][0]["total"]) == 3000.0

    def test_statistics_multiple_wallets(
        self, client, auth_headers, created_wallet, second_wallet, expense_category
    ):
        """Test statistics with multiple wallets."""
        now = datetime.now(timezone.utc)

        # Add transaction to second wallet
        client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": second_wallet["id"],
                "category_id": expense_category["id"],
                "amount": "-50.00",
                "occurred_at": now.isoformat(),
            },
            headers=auth_headers,
        )

        response = client.get("/api/v1/statistics", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Total: 1000 + 500 - 50 = 1450
        assert data["total_balance"] == "1450.0000"
        assert len(data["wallet_balances"]) == 2

    def test_statistics_unauthenticated(self, client):
        """Test statistics without auth fails."""
        response = client.get("/api/v1/statistics")

        assert response.status_code == 401


class TestGetReport:
    """Tests for GET /api/v1/statistics/report"""

    def test_report_empty(self, client, auth_headers):
        """Test report with no data."""
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=30)
        end = now

        response = client.get(
            "/api/v1/statistics/report",
            params={"start_date": start.isoformat(), "end_date": end.isoformat()},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["summary"]["income"]) == 0
        assert float(data["summary"]["expenses"]) == 0
        assert float(data["summary"]["net_change"]) == 0
        assert data["summary"]["transaction_count"] == 0
        assert data["by_category"] == []
        assert data["by_wallet"] == []

    def test_report_with_transactions(
        self, client, auth_headers, created_wallet, sample_transactions
    ):
        """Test report with transactions in period."""
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=1)
        end = now + timedelta(days=1)

        response = client.get(
            "/api/v1/statistics/report",
            params={"start_date": start.isoformat(), "end_date": end.isoformat()},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert float(data["summary"]["income"]) == 3000.0
        assert float(data["summary"]["expenses"]) == 300.0
        assert float(data["summary"]["net_change"]) == 2700.0
        assert data["summary"]["transaction_count"] == 4

        # Check category breakdown
        assert len(data["by_category"]) == 2

        # Check wallet breakdown
        assert len(data["by_wallet"]) == 1
        assert data["by_wallet"][0]["wallet_name"] == "Test Wallet"
        assert float(data["by_wallet"][0]["income"]) == 3000.0
        assert float(data["by_wallet"][0]["expenses"]) == 300.0
        assert float(data["by_wallet"][0]["net_change"]) == 2700.0

    def test_report_excludes_out_of_range(
        self, client, auth_headers, created_wallet, expense_category
    ):
        """Test report excludes transactions outside date range."""
        now = datetime.now(timezone.utc)

        # Create transaction in the past
        client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": created_wallet["id"],
                "category_id": expense_category["id"],
                "amount": "-100.00",
                "occurred_at": (now - timedelta(days=60)).isoformat(),
            },
            headers=auth_headers,
        )

        # Create transaction in range
        client.post(
            "/api/v1/transactions",
            json={
                "wallet_id": created_wallet["id"],
                "category_id": expense_category["id"],
                "amount": "-50.00",
                "occurred_at": now.isoformat(),
            },
            headers=auth_headers,
        )

        # Query for last 30 days only
        start = now - timedelta(days=30)
        end = now + timedelta(days=1)

        response = client.get(
            "/api/v1/statistics/report",
            params={"start_date": start.isoformat(), "end_date": end.isoformat()},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Only the in-range transaction
        assert float(data["summary"]["expenses"]) == 50.0
        assert data["summary"]["transaction_count"] == 1

    def test_report_missing_dates(self, client, auth_headers):
        """Test report without required date parameters."""
        response = client.get("/api/v1/statistics/report", headers=auth_headers)

        assert response.status_code == 422

    def test_report_unauthenticated(self, client):
        """Test report without auth fails."""
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=30)
        end = now

        response = client.get(
            "/api/v1/statistics/report",
            params={"start_date": start.isoformat(), "end_date": end.isoformat()},
        )

        assert response.status_code == 401
