"""Settings › Merchants: the user's merchants with how many transactions each has."""

import pytest

from tests.bank_fakes import connect_and_link, raw_transaction, sync

MERCHANTS_URL = "/api/v1/merchants"


@pytest.fixture
def purchases(client, auth_headers, bank, uncategorized):
    """Three Wolt orders, one Apple and one Bakery purchase, imported from the fake bank."""
    connect_and_link(client, auth_headers, bank)
    bank.transactions = [
        raw_transaction(f"t{index}", "5.00", creditor={"name": name})
        for index, name in enumerate(["Wolt", "Apple", "Wolt", "Bakery", "Wolt"])
    ]
    sync(client, auth_headers)


def _list(client, headers, **params):
    response = client.get(MERCHANTS_URL, params=params, headers=headers)
    assert response.status_code == 200
    return [(merchant["name"], merchant["transaction_count"]) for merchant in response.json()]


class TestMerchantList:
    def test_most_used_first_by_default(self, client, auth_headers, purchases):
        assert _list(client, auth_headers) == [("Wolt", 3), ("Apple", 1), ("Bakery", 1)]

    def test_alphabetical(self, client, auth_headers, purchases):
        assert _list(client, auth_headers, order="alphabetical") == [("Apple", 1), ("Bakery", 1), ("Wolt", 3)]

    def test_empty_without_transactions(self, client, auth_headers):
        assert _list(client, auth_headers) == []

    def test_only_the_users_own(self, client, second_auth_headers, purchases):
        assert _list(client, second_auth_headers) == []

    def test_unknown_order_refused(self, client, auth_headers):
        assert client.get(MERCHANTS_URL, params={"order": "random"}, headers=auth_headers).status_code == 422


def _rename(client, headers, merchant_id, name):
    return client.patch(f"{MERCHANTS_URL}/{merchant_id}", json={"name": name}, headers=headers)


def _merchant_id(client, headers, name):
    return next(m["id"] for m in client.get(MERCHANTS_URL, headers=headers).json() if m["name"] == name)


class TestRename:
    def test_renamed_merchant_shows_under_its_new_name(self, client, auth_headers, purchases):
        merchant_id = _merchant_id(client, auth_headers, "Wolt")

        response = _rename(client, auth_headers, merchant_id, "  Wolt   Greece ")

        assert response.json() == {"id": merchant_id, "name": "Wolt Greece"}
        assert ("Wolt Greece", 3) in _list(client, auth_headers)

    def test_bank_spelling_still_finds_the_renamed_merchant(self, client, auth_headers, bank, purchases):
        merchant_id = _merchant_id(client, auth_headers, "Wolt")
        _rename(client, auth_headers, merchant_id, "Wolt Greece")
        bank.transactions = [raw_transaction("new", "9.00", creditor={"name": "WOLT"}, booking_date="2026-09-25")]

        sync(client, auth_headers)

        assert ("Wolt Greece", 4) in _list(client, auth_headers)
        assert "WOLT" not in [name for name, _ in _list(client, auth_headers)]

    def test_case_change_keeps_one_merchant(self, client, auth_headers, purchases):
        merchant_id = _merchant_id(client, auth_headers, "Wolt")

        assert _rename(client, auth_headers, merchant_id, "WOLT").status_code == 200

    def test_another_merchants_name_is_refused(self, client, auth_headers, purchases):
        merchant_id = _merchant_id(client, auth_headers, "Wolt")

        response = _rename(client, auth_headers, merchant_id, "apple")

        assert response.status_code == 409 and "Merge" in response.json()["detail"]

    @pytest.mark.parametrize("name", ["", "   "])
    def test_blank_name_refused(self, client, auth_headers, purchases, name):
        merchant_id = _merchant_id(client, auth_headers, "Wolt")

        assert _rename(client, auth_headers, merchant_id, name).status_code == 422

    def test_someone_elses_merchant_is_refused(self, client, auth_headers, second_auth_headers, purchases):
        merchant_id = _merchant_id(client, auth_headers, "Wolt")

        response = _rename(client, second_auth_headers, merchant_id, "Mine")

        assert response.status_code == 403
