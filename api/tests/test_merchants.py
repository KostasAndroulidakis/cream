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


def _update(client, headers, merchant_id, changes):
    return client.patch(f"{MERCHANTS_URL}/{merchant_id}", json=changes, headers=headers)


def _rename(client, headers, merchant_id, name):
    return _update(client, headers, merchant_id, {"name": name})


def _merchant_id(client, headers, name):
    return next(m["id"] for m in client.get(MERCHANTS_URL, headers=headers).json() if m["name"] == name)


class TestRename:
    def test_renamed_merchant_shows_under_its_new_name(self, client, auth_headers, purchases):
        merchant_id = _merchant_id(client, auth_headers, "Wolt")

        response = _rename(client, auth_headers, merchant_id, "  Wolt   Greece ")

        # Still Wolt to the catalog, so it keeps its website
        assert response.json() == {"id": merchant_id, "name": "Wolt Greece", "website": "wolt.com"}
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


class TestWebsite:
    def test_known_merchant_gets_the_catalogs_website(self, client, auth_headers, purchases):
        websites = {m["name"]: m["website"] for m in client.get(MERCHANTS_URL, headers=auth_headers).json()}

        assert websites == {"Wolt": "wolt.com", "Apple": None, "Bakery": None}

    def test_users_website_is_kept_as_a_domain(self, client, auth_headers, purchases):
        merchant_id = _merchant_id(client, auth_headers, "Bakery")

        changes = {"name": "Bakery", "website": " https://www.My-Bakery.gr/el/menu "}

        response = _update(client, auth_headers, merchant_id, changes)

        assert response.json()["website"] == "my-bakery.gr"

    def test_empty_website_falls_back_to_the_catalog(self, client, auth_headers, purchases):
        merchant_id = _merchant_id(client, auth_headers, "Wolt")
        _update(client, auth_headers, merchant_id, {"name": "Wolt", "website": "wolt.gr"})

        response = _update(client, auth_headers, merchant_id, {"name": "Wolt", "website": ""})

        assert response.json()["website"] == "wolt.com"

    def test_transactions_carry_the_merchants_website(self, client, auth_headers, purchases):
        transactions = client.get("/api/v1/transactions", headers=auth_headers).json()

        assert {t["merchant"]["name"]: t["merchant"]["website"] for t in transactions}["Wolt"] == "wolt.com"

    @pytest.mark.parametrize("website", ["not a website", "http://", "wolt"])
    def test_invalid_website_refused(self, client, auth_headers, purchases, website):
        merchant_id = _merchant_id(client, auth_headers, "Bakery")

        response = _update(client, auth_headers, merchant_id, {"name": "Bakery", "website": website})

        assert response.status_code == 422
