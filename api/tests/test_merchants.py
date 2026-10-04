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
