"""Hidden transactions: left out of lists and the review inbox, still part of the wallet balance."""

from decimal import Decimal

import pytest

from tests.bank_fakes import connect_and_link, raw_transaction, sync

TRANSACTIONS_URL = "/api/v1/transactions"
INBOX_URL = f"{TRANSACTIONS_URL}/uncategorized"


@pytest.fixture
def linked(client, auth_headers, bank, uncategorized):
    return connect_and_link(client, auth_headers, bank)


@pytest.fixture
def imported(client, auth_headers, bank, linked):
    """One uncategorized transaction imported from the fake bank."""
    bank.transactions = [raw_transaction("t1", "40.00")]
    sync(client, auth_headers)
    [transaction] = client.get(TRANSACTIONS_URL, headers=auth_headers).json()
    return transaction


def _hide(client, headers, transaction_id, hidden=True):
    return client.patch(f"{TRANSACTIONS_URL}/{transaction_id}", json={"is_hidden": hidden}, headers=headers)


class TestHideAndShow:
    def test_hidden_and_shown_again(self, client, auth_headers, imported):
        hidden = _hide(client, auth_headers, imported["id"]).json()
        shown = _hide(client, auth_headers, imported["id"], hidden=False).json()

        assert imported["is_hidden"] is False
        assert hidden["is_hidden"] is True and shown["is_hidden"] is False

    def test_other_changes_keep_it_hidden(self, client, auth_headers, imported):
        _hide(client, auth_headers, imported["id"])

        updated = client.patch(
            f"{TRANSACTIONS_URL}/{imported['id']}", json={"description": "Duplicate"}, headers=auth_headers
        ).json()

        assert updated["is_hidden"] is True

    def test_needs_a_true_or_false(self, client, auth_headers, imported):
        response = client.patch(
            f"{TRANSACTIONS_URL}/{imported['id']}", json={"is_hidden": None}, headers=auth_headers
        )

        assert response.status_code == 422


class TestWhereHiddenShows:
    def test_left_out_of_the_list(self, client, auth_headers, imported):
        _hide(client, auth_headers, imported["id"])

        assert client.get(TRANSACTIONS_URL, headers=auth_headers).json() == []

    def test_listed_on_request(self, client, auth_headers, imported):
        _hide(client, auth_headers, imported["id"])

        listed = client.get(TRANSACTIONS_URL, params={"include_hidden": True}, headers=auth_headers).json()

        assert [t["id"] for t in listed] == [imported["id"]]

    def test_left_out_of_the_review_inbox(self, client, auth_headers, imported):
        _hide(client, auth_headers, imported["id"])

        assert client.get(INBOX_URL, headers=auth_headers).json() == {"total": 0, "items": []}

    def test_still_counts_in_the_wallet_balance(self, client, auth_headers, linked, imported):
        wallet_url = f"/api/v1/wallets/{linked['wallet_id']}"
        balance_before = Decimal(client.get(wallet_url, headers=auth_headers).json()["balance"])

        _hide(client, auth_headers, imported["id"])

        assert Decimal(client.get(wallet_url, headers=auth_headers).json()["balance"]) == balance_before


class TestStatistics:
    """The imported fixture is a 40.00 expense booked on 2026-09-20, in a wallet the bank says holds 1000.00."""

    STATISTICS_URL = "/api/v1/statistics"
    REPORT_PERIOD = {"start_date": "2026-09-01T00:00:00Z", "end_date": "2026-09-30T23:59:59Z"}

    def test_left_out_of_totals_but_not_balance(self, client, auth_headers, imported):
        before = client.get(self.STATISTICS_URL, headers=auth_headers).json()

        _hide(client, auth_headers, imported["id"])

        after = client.get(self.STATISTICS_URL, headers=auth_headers).json()
        assert Decimal(before["total_expenses"]) == Decimal("40")
        assert Decimal(after["total_expenses"]) == 0
        assert after["spending_by_category"] == []
        assert Decimal(after["total_balance"]) == Decimal(before["total_balance"]) == Decimal("1000")

    def test_left_out_of_the_report(self, client, auth_headers, imported):
        _hide(client, auth_headers, imported["id"])

        report = client.get(f"{self.STATISTICS_URL}/report", params=self.REPORT_PERIOD, headers=auth_headers).json()

        assert report["summary"]["transaction_count"] == 0
        assert Decimal(report["summary"]["expenses"]) == 0
        assert report["by_category"] == [] and report["by_wallet"] == []
