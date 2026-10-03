"""Bulk edit and bulk delete: the same change on many transactions, all or nothing."""

from decimal import Decimal

import pytest

from tests.bank_fakes import connect_and_link, raw_transaction, sync

TRANSACTIONS_URL = "/api/v1/transactions"
BULK_UPDATE_URL = f"{TRANSACTIONS_URL}/bulk-update"
BULK_DELETE_URL = f"{TRANSACTIONS_URL}/bulk-delete"
PAST_DATE = "2026-09-01T12:00:00Z"


@pytest.fixture
def linked(client, auth_headers, bank, uncategorized):
    return connect_and_link(client, auth_headers, bank)


@pytest.fixture
def imported(client, auth_headers, bank, linked):
    """Two transactions from the fake bank."""
    bank.transactions = [raw_transaction("t1", "40.00"), raw_transaction("t2", "10.00")]
    sync(client, auth_headers)
    return client.get(TRANSACTIONS_URL, headers=auth_headers).json()


@pytest.fixture
def own_category(client, auth_headers):
    response = client.post("/api/v1/categories", json={"name": "Snacks", "type": "expense"}, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def manual(client, auth_headers, linked, own_category):
    """Two transactions entered by hand in the linked wallet."""
    created = []
    for amount in ("-3.00", "-5.00"):
        response = client.post(
            TRANSACTIONS_URL,
            json={"wallet_id": linked["wallet_id"], "category_id": own_category["id"], "amount": amount,
                  "occurred_at": PAST_DATE},
            headers=auth_headers,
        )
        assert response.status_code == 201
        created.append(response.json())
    return created


def _ids(transactions):
    return [transaction["id"] for transaction in transactions]


def _get(client, headers, transaction_id):
    return client.get(f"{TRANSACTIONS_URL}/{transaction_id}", headers=headers).json()


def _bulk_update(client, headers, ids, changes):
    return client.post(BULK_UPDATE_URL, json={"transaction_ids": ids, "changes": changes}, headers=headers)


class TestBulkUpdate:
    def test_category_on_all_becomes_the_users_choice(self, client, auth_headers, imported, own_category):
        response = _bulk_update(client, auth_headers, _ids(imported), {"category_id": own_category["id"]})

        assert response.json() == {"affected": 2}
        for transaction_id in _ids(imported):
            after = _get(client, auth_headers, transaction_id)
            assert (after["category_id"], after["category_source"]) == (own_category["id"], "manual")

    def test_hide_and_notes(self, client, auth_headers, imported):
        _bulk_update(client, auth_headers, _ids(imported), {"is_hidden": True, "description": "Duplicate"})

        for transaction_id in _ids(imported):
            after = _get(client, auth_headers, transaction_id)
            assert (after["is_hidden"], after["description"]) == (True, "Duplicate")

    def test_notes_can_be_cleared(self, client, auth_headers, imported):
        _bulk_update(client, auth_headers, _ids(imported), {"description": "Temporary"})

        _bulk_update(client, auth_headers, _ids(imported), {"description": None})

        assert all(_get(client, auth_headers, i)["description"] is None for i in _ids(imported))

    def test_date_of_manual_transactions(self, client, auth_headers, manual):
        new_date = "2026-08-15T12:00:00Z"

        response = _bulk_update(client, auth_headers, _ids(manual), {"occurred_at": new_date})

        assert response.status_code == 200
        assert all(_get(client, auth_headers, i)["occurred_at"].startswith("2026-08-15") for i in _ids(manual))

    def test_date_refused_for_all_when_one_is_from_a_bank(self, client, auth_headers, imported, manual):
        ids = [manual[0]["id"], imported[0]["id"]]

        response = _bulk_update(client, auth_headers, ids, {"occurred_at": "2026-08-15T12:00:00Z"})

        assert response.status_code == 422
        # Nothing changed, not even the manual one
        assert _get(client, auth_headers, manual[0]["id"])["occurred_at"] == manual[0]["occurred_at"]

    def test_future_date_refused(self, client, auth_headers, manual):
        response = _bulk_update(client, auth_headers, _ids(manual), {"occurred_at": "2999-01-01T12:00:00Z"})

        assert response.status_code == 422

    def test_another_users_transaction_refuses_all(self, client, auth_headers, second_auth_headers, imported):
        wallet = client.post("/api/v1/wallets", json={"name": "Theirs"}, headers=second_auth_headers).json()
        categories = client.get("/api/v1/categories", headers=second_auth_headers).json()
        theirs = client.post(
            TRANSACTIONS_URL,
            json={"wallet_id": wallet["id"], "category_id": categories[0]["id"], "amount": "-1", "occurred_at": PAST_DATE},
            headers=second_auth_headers,
        ).json()

        response = _bulk_update(client, auth_headers, [imported[0]["id"], theirs["id"]], {"is_hidden": True})

        assert response.status_code == 404
        assert _get(client, auth_headers, imported[0]["id"])["is_hidden"] is False

    def test_same_id_twice_counts_once(self, client, auth_headers, imported):
        response = _bulk_update(client, auth_headers, [imported[0]["id"]] * 2, {"is_hidden": True})

        assert response.json() == {"affected": 1}

    @pytest.mark.parametrize(
        "body",
        [
            {"transaction_ids": [], "changes": {"is_hidden": True}},
            {"transaction_ids": [1], "changes": {}},
            {"transaction_ids": [1], "changes": {"category_id": None}},
            {"transaction_ids": [1], "changes": {"is_hidden": None}},
        ],
    )
    def test_invalid_requests(self, client, auth_headers, body):
        assert client.post(BULK_UPDATE_URL, json=body, headers=auth_headers).status_code == 422


class TestBulkDelete:
    def test_deletes_manual_transactions_and_moves_the_balance(self, client, auth_headers, linked, manual):
        wallet_url = f"/api/v1/wallets/{linked['wallet_id']}"
        balance_before = Decimal(client.get(wallet_url, headers=auth_headers).json()["balance"])

        response = client.post(BULK_DELETE_URL, json={"transaction_ids": _ids(manual)}, headers=auth_headers)

        assert response.json() == {"affected": 2}
        assert all(client.get(f"{TRANSACTIONS_URL}/{i}", headers=auth_headers).status_code == 404 for i in _ids(manual))
        assert Decimal(client.get(wallet_url, headers=auth_headers).json()["balance"]) == balance_before + Decimal("8")

    def test_refused_for_all_when_one_is_from_a_bank(self, client, auth_headers, imported, manual):
        ids = [manual[0]["id"], imported[0]["id"]]

        response = client.post(BULK_DELETE_URL, json={"transaction_ids": ids}, headers=auth_headers)

        assert response.status_code == 409
        assert client.get(f"{TRANSACTIONS_URL}/{manual[0]['id']}", headers=auth_headers).status_code == 200
