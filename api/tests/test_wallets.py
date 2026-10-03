from decimal import Decimal

import pytest


@pytest.fixture
def wallet_data():
    """Sample wallet data."""
    return {
        "name": "Test Wallet",
        "type": "cash",
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
        for wallet_type in ["cash", "investment", "real_estate", "credit_card", "loan", "other_liability"]:
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


def _set_currency(db_session, wallet_id, currency):
    """An account from before CREAM went EUR-only: the API no longer creates these."""
    from app.models import Wallet

    db_session.get(Wallet, wallet_id).currency = currency
    db_session.commit()


class TestWalletCurrency:
    """Currency codes are normalized and validated."""

    def test_currency_is_uppercased(self, client, auth_headers):
        wallet = _create_wallet(client, auth_headers, currency=" eur ")

        assert wallet["currency"] == "EUR"

    def test_only_eur_for_now(self, client, auth_headers, created_wallet):
        created = client.post(WALLETS_URL, json={"name": "W", "currency": "USD"}, headers=auth_headers)
        changed = client.patch(f"{WALLETS_URL}/{created_wallet['id']}", json={"currency": "USD"}, headers=auth_headers)

        assert created.status_code == changed.status_code == 422
        assert "EUR" in str(created.json())

    @pytest.mark.parametrize("currency", ["EU", "EURO", "E1R", "€€€"])
    def test_invalid_currency_rejected(self, client, auth_headers, currency):
        response = client.post(WALLETS_URL, json={"name": "W", "currency": currency}, headers=auth_headers)

        assert response.status_code == 422

    def test_older_account_moves_to_eur_without_transactions(self, client, auth_headers, created_wallet, db_session):
        _set_currency(db_session, created_wallet["id"], "USD")

        response = client.patch(
            f"{WALLETS_URL}/{created_wallet['id']}", json={"currency": "EUR"}, headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["currency"] == "EUR"

    def test_currency_change_blocked_with_transactions(self, client, auth_headers, created_wallet, db_session):
        _add_transaction(client, auth_headers, created_wallet["id"], "-10.00")
        _set_currency(db_session, created_wallet["id"], "USD")

        response = client.patch(
            f"{WALLETS_URL}/{created_wallet['id']}", json={"currency": "EUR"}, headers=auth_headers
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

    def test_totals_grouped_by_currency(self, client, auth_headers, db_session):
        # Accounts created before CREAM went EUR-only may still be in other currencies
        first = _create_wallet(client, auth_headers, currency="EUR", initial_balance="100.50")
        _create_wallet(client, auth_headers, currency="EUR", initial_balance="200.25")
        older = _create_wallet(client, auth_headers, initial_balance="50")
        _set_currency(db_session, older["id"], "USD")
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


TYPES_URL = f"{WALLETS_URL}/types"


def _create(client, headers, **fields):
    return client.post(WALLETS_URL, json={"name": "Account", **fields}, headers=headers)


class TestAccountTypes:
    def test_catalog_in_monarchs_order_with_asset_or_liability(self, client, auth_headers):
        catalog = client.get(TYPES_URL, headers=auth_headers).json()

        assert [(t["type"], t["account_class"]) for t in catalog] == [
            ("cash", "asset"), ("investment", "asset"), ("real_estate", "asset"), ("vehicle", "asset"),
            ("valuables", "asset"), ("other_asset", "asset"), ("credit_card", "liability"),
            ("mortgage", "liability"), ("loan", "liability"), ("other_liability", "liability"),
        ]
        assert all(t["subtypes"] for t in catalog)

    def test_catalog_requires_login(self, client):
        assert client.get(TYPES_URL).status_code == 401

    def test_subtype_defaults_to_the_types_first(self, client, auth_headers):
        catalog = {t["type"]: t for t in client.get(TYPES_URL, headers=auth_headers).json()}

        created = _create(client, auth_headers, type="vehicle").json()

        assert created["subtype"] == catalog["vehicle"]["subtypes"][0]["key"] == "car"

    def test_subtype_of_the_type_is_kept(self, client, auth_headers):
        assert _create(client, auth_headers, type="cash", subtype="savings").json()["subtype"] == "savings"

    @pytest.mark.parametrize("subtype", ["car", "nonsense", ""])
    def test_subtype_of_another_type_refused(self, client, auth_headers, subtype):
        assert _create(client, auth_headers, type="cash", subtype=subtype).status_code == 422

    def test_new_type_alone_starts_at_its_default(self, client, auth_headers):
        wallet = _create(client, auth_headers, type="cash", subtype="savings").json()

        updated = client.patch(f"{WALLETS_URL}/{wallet['id']}", json={"type": "loan"}, headers=auth_headers).json()

        assert (updated["type"], updated["subtype"]) == ("loan", "auto")

    def test_subtype_alone_must_fit_the_current_type(self, client, auth_headers):
        wallet = _create(client, auth_headers, type="cash").json()
        url = f"{WALLETS_URL}/{wallet['id']}"

        assert client.patch(url, json={"subtype": "checking"}, headers=auth_headers).json()["subtype"] == "checking"
        assert client.patch(url, json={"subtype": "car"}, headers=auth_headers).status_code == 422

    def test_other_changes_keep_type_and_subtype(self, client, auth_headers):
        wallet = _create(client, auth_headers, type="vehicle", subtype="boat").json()

        updated = client.patch(f"{WALLETS_URL}/{wallet['id']}", json={"name": "Sailboat"}, headers=auth_headers).json()

        assert (updated["type"], updated["subtype"]) == ("vehicle", "boat")


class TestEditAccount:
    """PATCH /api/v1/wallets/{id} with Edit Account's fields."""

    def _patch(self, client, headers, wallet_id, **changes):
        response = client.patch(f"{WALLETS_URL}/{wallet_id}", json=changes, headers=headers)
        assert response.status_code == 200, response.text
        return response.json()

    def test_new_account_shows_everything(self, client, auth_headers):
        wallet = _create_wallet(client, auth_headers)

        assert (wallet["is_hidden"], wallet["exclude_balance"], wallet["hide_transactions"]) == (False, False, False)
        assert (wallet["invert_balance"], wallet["credit_limit"]) == (False, None)

    def test_set_balance_keeps_transactions(self, client, auth_headers):
        wallet = _create_wallet(client, auth_headers, initial_balance="100")
        _add_transaction(client, auth_headers, wallet["id"], "-30")

        updated = self._patch(client, auth_headers, wallet["id"], balance="500")

        assert Decimal(updated["balance"]) == Decimal("500")
        assert Decimal(updated["initial_balance"]) == Decimal("530")

    def test_invert_flips_the_balance_once(self, client, auth_headers):
        wallet = _create_wallet(client, auth_headers, initial_balance="200")

        inverted = self._patch(client, auth_headers, wallet["id"], invert_balance=True)
        again = self._patch(client, auth_headers, wallet["id"], invert_balance=True)
        back = self._patch(client, auth_headers, wallet["id"], invert_balance=False)

        assert Decimal(inverted["balance"]) == Decimal("-200")
        assert Decimal(again["balance"]) == Decimal("-200")
        assert Decimal(back["balance"]) == Decimal("200")

    def test_new_balance_then_invert(self, client, auth_headers):
        wallet = _create_wallet(client, auth_headers)

        updated = self._patch(client, auth_headers, wallet["id"], balance="75", invert_balance=True)

        assert Decimal(updated["balance"]) == Decimal("-75")

    def test_credit_limit(self, client, auth_headers):
        wallet = _create_wallet(client, auth_headers, type="credit_card")

        updated = self._patch(client, auth_headers, wallet["id"], credit_limit="5000")
        cleared = self._patch(client, auth_headers, wallet["id"], credit_limit=None)

        assert Decimal(updated["credit_limit"]) == Decimal("5000")
        assert cleared["credit_limit"] is None

    def test_credit_limit_cannot_be_negative(self, client, auth_headers):
        wallet = _create_wallet(client, auth_headers, type="credit_card")

        response = client.patch(f"{WALLETS_URL}/{wallet['id']}", json={"credit_limit": "-1"}, headers=auth_headers)

        assert response.status_code == 422

    def test_excluded_balance_leaves_the_totals(self, client, auth_headers):
        kept = _create_wallet(client, auth_headers, initial_balance="100")
        excluded = _create_wallet(client, auth_headers, initial_balance="900")

        self._patch(client, auth_headers, excluded["id"], exclude_balance=True)

        totals = client.get(TOTALS_URL, headers=auth_headers).json()
        assert [(Decimal(t["balance"]), t["wallet_count"]) for t in totals] == [(Decimal("100"), 1)]
        assert kept["id"] != excluded["id"]

    def test_hidden_transactions_leave_lists_but_not_the_balance(self, client, auth_headers):
        wallet = _create_wallet(client, auth_headers, initial_balance="100")
        _add_transaction(client, auth_headers, wallet["id"], "-30")

        updated = self._patch(client, auth_headers, wallet["id"], hide_transactions=True)

        assert client.get("/api/v1/transactions", headers=auth_headers).json() == []
        assert Decimal(updated["balance"]) == Decimal("70")

    def test_hidden_account_is_still_listed_for_the_app(self, client, auth_headers):
        """The Accounts page leaves it out; pickers and totals still need it."""
        wallet = _create_wallet(client, auth_headers)

        self._patch(client, auth_headers, wallet["id"], is_hidden=True)

        listed = client.get(WALLETS_URL, headers=auth_headers).json()
        assert [w["is_hidden"] for w in listed] == [True]


SUMMARY_URL = f"{WALLETS_URL}/summary"


class TestAccountsSummary:
    def test_net_worth_and_each_types_total(self, client, auth_headers):
        _create(client, auth_headers, type="cash", initial_balance="1000")
        _create(client, auth_headers, type="cash", initial_balance="250.50")
        _create(client, auth_headers, type="vehicle", initial_balance="8000")
        _create(client, auth_headers, type="credit_card", initial_balance="-450")

        summary = client.get(SUMMARY_URL, headers=auth_headers).json()

        assert summary["net_worth"] == [{"currency": "EUR", "balance": "8800.5000", "wallet_count": 4}]
        assert [(t["type"], t["account_class"], t["totals"][0]["balance"]) for t in summary["types"]] == [
            ("cash", "asset", "1250.5000"),
            ("vehicle", "asset", "8000.0000"),
            ("credit_card", "liability", "-450.0000"),
        ]

    def test_excluded_balances_count_nowhere(self, client, auth_headers):
        _create(client, auth_headers, type="cash", initial_balance="100")
        excluded = _create(client, auth_headers, type="cash", initial_balance="900").json()
        client.patch(f"{WALLETS_URL}/{excluded['id']}", json={"exclude_balance": True}, headers=auth_headers)

        summary = client.get(SUMMARY_URL, headers=auth_headers).json()

        assert summary["net_worth"][0]["balance"] == summary["types"][0]["totals"][0]["balance"] == "100.0000"

    def test_empty_and_only_own(self, client, auth_headers, second_auth_headers):
        _create(client, second_auth_headers, initial_balance="5")

        assert client.get(SUMMARY_URL, headers=auth_headers).json() == {"net_worth": [], "types": []}

    def test_requires_login(self, client):
        assert client.get(SUMMARY_URL).status_code == 401
