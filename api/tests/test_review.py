"""The review inbox ("Needs review"): set on import by the user's preferences, independent of category and hiding."""

import pytest

from app.models import CategorySource, UserPreferences
from app.services.categorization.auto import Decision
from app.services.review import needs_review_on_import
from tests.bank_fakes import connect_and_link, raw_transaction, sync
from tests.conftest import REVIEW_INBOX_URL

TRANSACTIONS_URL = "/api/v1/transactions"
CATEGORIZED = Decision(category_id=1, source=CategorySource.MCC)
UNCATEGORIZED = Decision(category_id=2, source=CategorySource.DEFAULT)


@pytest.fixture
def linked(client, auth_headers, bank, uncategorized):
    return connect_and_link(client, auth_headers, bank)


@pytest.fixture
def imported(client, auth_headers, bank, linked):
    """One bank transaction that found no category (so it needs review by default)."""
    bank.transactions = [raw_transaction("t1", "40.00")]
    sync(client, auth_headers)
    [transaction] = client.get(TRANSACTIONS_URL, headers=auth_headers).json()
    return transaction


def _inbox_ids(client, headers):
    return [transaction["id"] for transaction in client.get(REVIEW_INBOX_URL, headers=headers).json()["items"]]


def _patch(client, headers, transaction_id, changes):
    return client.patch(f"{TRANSACTIONS_URL}/{transaction_id}", json=changes, headers=headers)


class TestOnImport:
    @pytest.mark.parametrize(
        ("review_new", "review_uncategorized", "decision", "expected"),
        [
            (False, True, UNCATEGORIZED, True),
            (False, True, CATEGORIZED, False),
            (True, False, CATEGORIZED, True),
            (False, False, UNCATEGORIZED, False),
        ],
    )
    def test_follows_the_preferences(self, review_new, review_uncategorized, decision, expected):
        preferences = UserPreferences(
            review_new_transactions=review_new, review_uncategorized_transactions=review_uncategorized
        )

        assert needs_review_on_import(preferences, decision) is expected

    def test_defaults_review_only_the_uncategorized(self):
        defaults = UserPreferences.defaults(user_id=1)

        assert needs_review_on_import(defaults, UNCATEGORIZED) and not needs_review_on_import(defaults, CATEGORIZED)

    def test_sync_uses_the_users_saved_preferences(self, client, auth_headers, registered_user, bank, linked, db_session):
        db_session.add(UserPreferences(user_id=registered_user["id"], review_uncategorized_transactions=False))
        db_session.commit()
        bank.transactions = [raw_transaction("t1", "40.00")]

        sync(client, auth_headers)

        assert _inbox_ids(client, auth_headers) == []

    def test_without_saved_preferences_the_defaults_apply(self, client, auth_headers, imported):
        assert imported["needs_review"] is True
        assert _inbox_ids(client, auth_headers) == [imported["id"]]


class TestMarkReviewed:
    def test_reviewed_leaves_the_inbox_and_can_come_back(self, client, auth_headers, imported):
        reviewed = _patch(client, auth_headers, imported["id"], {"needs_review": False}).json()
        assert reviewed["needs_review"] is False and _inbox_ids(client, auth_headers) == []

        _patch(client, auth_headers, imported["id"], {"needs_review": True})

        assert _inbox_ids(client, auth_headers) == [imported["id"]]

    def test_needs_a_true_or_false(self, client, auth_headers, imported):
        assert _patch(client, auth_headers, imported["id"], {"needs_review": None}).status_code == 422

    def test_choosing_a_category_keeps_it_in_the_inbox(self, client, auth_headers, imported, uncategorized):
        other = client.post("/api/v1/categories", json={"name": "Snacks", "type": "expense"}, headers=auth_headers).json()

        client.post(
            f"{TRANSACTIONS_URL}/{imported['id']}/categorize", json={"category_id": other["id"]}, headers=auth_headers
        )

        assert _inbox_ids(client, auth_headers) == [imported["id"]]

    def test_hiding_keeps_the_status(self, client, auth_headers, imported):
        _patch(client, auth_headers, imported["id"], {"is_hidden": True})
        assert _inbox_ids(client, auth_headers) == []

        shown = _patch(client, auth_headers, imported["id"], {"is_hidden": False}).json()

        assert shown["needs_review"] is True and _inbox_ids(client, auth_headers) == [imported["id"]]

    def test_in_bulk(self, client, auth_headers, imported):
        response = client.post(
            f"{TRANSACTIONS_URL}/bulk-update",
            json={"transaction_ids": [imported["id"]], "changes": {"needs_review": False}},
            headers=auth_headers,
        )

        assert response.json() == {"affected": 1} and _inbox_ids(client, auth_headers) == []

    def test_bulk_needs_a_true_or_false(self, client, auth_headers, imported):
        response = client.post(
            f"{TRANSACTIONS_URL}/bulk-update",
            json={"transaction_ids": [imported["id"]], "changes": {"needs_review": None}},
            headers=auth_headers,
        )

        assert response.status_code == 422


MARK_ALL_URL = f"{REVIEW_INBOX_URL}/mark-all-reviewed"


class TestMarkAllReviewed:
    def test_empties_the_inbox_but_not_hidden_ones(self, client, auth_headers, bank, linked):
        bank.transactions = [raw_transaction(f"t{n}", "1.00") for n in range(3)]
        sync(client, auth_headers)
        hidden_id, *_ = _inbox_ids(client, auth_headers)
        _patch(client, auth_headers, hidden_id, {"is_hidden": True})

        response = client.post(MARK_ALL_URL, headers=auth_headers)

        assert response.json() == {"affected": 2} and _inbox_ids(client, auth_headers) == []
        shown = _patch(client, auth_headers, hidden_id, {"is_hidden": False}).json()
        assert shown["needs_review"] is True

    def test_only_the_users_own(self, client, auth_headers, second_auth_headers, imported):
        assert client.post(MARK_ALL_URL, headers=second_auth_headers).json() == {"affected": 0}

        assert _inbox_ids(client, auth_headers) == [imported["id"]]
