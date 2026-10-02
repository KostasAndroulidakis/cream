"""Automatic categorization: merchant keys, MCC mapping, merchant rules, the review inbox and sync."""

import importlib.util
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.models import Category, CategorySource, CategoryType, MerchantRule, Transaction
from app.services.categorization.mcc import MCC_CATEGORY_KEYS, category_key_for_mcc
from app.services.categorization.merchants import merchant_key, merchant_name
from tests.bank_fakes import connect_and_link, raw_transaction, sync

TRANSACTIONS_URL = "/api/v1/transactions"
INBOX_URL = f"{TRANSACTIONS_URL}/uncategorized"
RULES_URL = "/api/v1/rules"
GROCERIES_MCC = "5411"
RESTAURANTS_MCC = "5812"
UNMAPPED_MCC = "5511"
CATEGORIES_MIGRATION = Path(__file__).parents[1] / "migrations/versions/b7c1e2d4f5a6_category_groups_and_defaults.py"


def _seeded_category_keys() -> set[str]:
    """Keys the categories migration seeds, computed from its frozen catalog."""
    spec = importlib.util.spec_from_file_location("categories_migration", CATEGORIES_MIGRATION)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return {
        f"{migration._slug(group)}.{migration._slug(name)}"
        for group, _type, names in migration.DEFAULT_CATEGORIES
        for name in names
    }


def _system_category(db_session, key, name, *, is_group=False):
    category = Category(user_id=None, name=name, type=CategoryType.EXPENSE, key=key, is_group=is_group)
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def groceries(db_session):
    return _system_category(db_session, "food_and_dining.groceries", "Groceries")


@pytest.fixture
def restaurants(db_session):
    return _system_category(db_session, "food_and_dining.restaurants_and_bars", "Restaurants & Bars")


@pytest.fixture
def linked(client, auth_headers, bank, uncategorized, groceries, restaurants):
    """A linked bank account with the system categories the tests use."""
    return connect_and_link(client, auth_headers, bank)


def _shop(tx_id, merchant, mcc=None, amount="10.00"):
    extra = {"merchant_category_code": mcc} if mcc else {}
    return raw_transaction(tx_id, amount, creditor={"name": merchant}, **extra)


def _transactions(client, headers):
    return {t["id"]: t for t in client.get(TRANSACTIONS_URL, headers=headers).json()}


def _by_merchant(client, headers, merchant):
    return [t for t in _transactions(client, headers).values() if t["counterparty"] == merchant]


def _categorize(client, headers, transaction_id, category_id, apply_to_similar=False):
    return client.post(
        f"{TRANSACTIONS_URL}/{transaction_id}/categorize",
        json={"category_id": category_id, "apply_to_similar": apply_to_similar},
        headers=headers,
    )


class TestMerchantKey:
    def test_ignores_case_and_spacing(self):
        assert merchant_key("  SKLAVENITIS   Athens ", None) == merchant_key("sklavenitis athens", None)

    def test_falls_back_to_description(self):
        assert merchant_key(None, "Coffee Island") == "coffee island"
        assert merchant_name(None, "Coffee Island") == "Coffee Island"

    def test_nothing_to_match(self):
        assert merchant_key(None, None) is None and merchant_key("  ", "") is None


class TestMccMapping:
    def test_single_code_and_range(self):
        assert category_key_for_mcc(GROCERIES_MCC) == "food_and_dining.groceries"
        assert category_key_for_mcc("3100") == "travel_and_lifestyle.travel_and_vacation"  # an airline

    def test_unmapped_or_invalid(self):
        assert category_key_for_mcc(UNMAPPED_MCC) is None
        assert category_key_for_mcc("ABCD") is None and category_key_for_mcc(None) is None

    def test_every_mapped_category_is_seeded(self):
        assert MCC_CATEGORY_KEYS <= _seeded_category_keys()


class TestSyncCategorization:
    def test_mcc_categorizes_and_unknown_waits_in_inbox(self, client, auth_headers, bank, linked, groceries, uncategorized):
        bank.transactions = [_shop("t1", "SKLAVENITIS", GROCERIES_MCC), _shop("t2", "CAR DEALER", UNMAPPED_MCC)]

        results = sync(client, auth_headers)

        assert results[0]["imported"] == 2 and results[0]["categorized"] == 1
        [grocery] = _by_merchant(client, auth_headers, "SKLAVENITIS")
        assert (grocery["category_id"], grocery["category_source"]) == (groceries.id, "mcc")
        [dealer] = _by_merchant(client, auth_headers, "CAR DEALER")
        assert (dealer["category_id"], dealer["category_source"]) == (uncategorized.id, "default")

    def test_rule_beats_mcc(self, client, auth_headers, bank, linked, restaurants):
        bank.transactions = [_shop("t1", "Kiosk", GROCERIES_MCC)]
        sync(client, auth_headers)
        [first] = _by_merchant(client, auth_headers, "Kiosk")
        _categorize(client, auth_headers, first["id"], restaurants.id, apply_to_similar=True)
        bank.transactions = [_shop("t1", "Kiosk", GROCERIES_MCC), _shop("t2", "KIOSK", GROCERIES_MCC)]

        sync(client, auth_headers)

        new = next(t for t in _transactions(client, auth_headers).values() if t["counterparty"] == "KIOSK")
        assert (new["category_id"], new["category_source"]) == (restaurants.id, "rule")

    def test_sync_retries_transactions_waiting_in_inbox(
        self, client, auth_headers, bank, linked, groceries, db_session, registered_user
    ):
        bank.transactions = [_shop("t1", "Corner Shop")]
        sync(client, auth_headers)
        # A rule that exists now but didn't when the transaction arrived
        db_session.add(MerchantRule(
            user_id=registered_user["id"], merchant_key="corner shop", merchant_name="Corner Shop", category_id=groceries.id
        ))
        db_session.commit()

        results = sync(client, auth_headers)

        assert results[0] == {**results[0], "imported": 0, "categorized": 1}
        [shop] = _by_merchant(client, auth_headers, "Corner Shop")
        assert (shop["category_id"], shop["category_source"]) == (groceries.id, "rule")


class TestInbox:
    def test_lists_only_uncategorized_newest_first(self, client, auth_headers, bank, linked):
        bank.transactions = [
            raw_transaction("t1", "1", booking_date="2026-09-01"),
            raw_transaction("t2", "2", booking_date="2026-09-02"),
            _shop("t3", "SKLAVENITIS", GROCERIES_MCC),
        ]
        sync(client, auth_headers)

        page = client.get(INBOX_URL, params={"limit": 1}, headers=auth_headers).json()

        assert page["total"] == 2
        assert [t["amount"] for t in page["items"]] == ["-2.0000"]

    def test_other_users_transactions_not_listed(self, client, auth_headers, second_auth_headers, bank, linked):
        bank.transactions = [raw_transaction("t1", "1")]
        sync(client, auth_headers)

        assert client.get(INBOX_URL, headers=second_auth_headers).json() == {"total": 0, "items": []}


class TestCategorize:
    def test_single_transaction_is_manual_and_creates_no_rule(self, client, auth_headers, bank, linked, groceries):
        bank.transactions = [_shop("t1", "Market"), _shop("t2", "Market")]
        sync(client, auth_headers)
        first, second = _by_merchant(client, auth_headers, "Market")

        result = _categorize(client, auth_headers, first["id"], groceries.id).json()

        assert result["rule"] is None and result["similar_updated"] == 0
        assert (result["transaction"]["category_id"], result["transaction"]["category_source"]) == (groceries.id, "manual")
        assert _transactions(client, auth_headers)[second["id"]]["category_source"] == "default"

    def test_apply_to_similar_updates_automatic_but_not_manual_choices(
        self, client, auth_headers, bank, linked, groceries, restaurants
    ):
        bank.transactions = [
            _shop("t1", "Coffee Island"), _shop("t2", "COFFEE  ISLAND", GROCERIES_MCC), _shop("t3", "coffee island"),
            _shop("t4", "Other Shop"),
        ]
        sync(client, auth_headers)
        first, by_mcc, hand_picked = sorted(
            (t for t in _transactions(client, auth_headers).values() if t["merchant_key"] == "coffee island"),
            key=lambda t: t["id"],
        )
        _categorize(client, auth_headers, hand_picked["id"], groceries.id)

        result = _categorize(client, auth_headers, first["id"], restaurants.id, apply_to_similar=True).json()

        assert result["similar_updated"] == 1
        assert result["rule"]["merchant_name"] == "Coffee Island" and result["rule"]["category_id"] == restaurants.id
        after = _transactions(client, auth_headers)
        assert (after[by_mcc["id"]]["category_id"], after[by_mcc["id"]]["category_source"]) == (restaurants.id, "rule")
        assert after[hand_picked["id"]]["category_id"] == groceries.id
        assert _by_merchant(client, auth_headers, "Other Shop")[0]["category_source"] == "default"

    def test_changing_the_rule_keeps_one_rule_per_merchant(self, client, auth_headers, bank, linked, groceries, restaurants):
        bank.transactions = [_shop("t1", "Market"), _shop("t2", "Market")]
        sync(client, auth_headers)
        first, second = _by_merchant(client, auth_headers, "Market")
        _categorize(client, auth_headers, first["id"], groceries.id, apply_to_similar=True)

        _categorize(client, auth_headers, first["id"], restaurants.id, apply_to_similar=True)

        rules = client.get(RULES_URL, headers=auth_headers).json()
        assert [rule["category_id"] for rule in rules] == [restaurants.id]
        assert _transactions(client, auth_headers)[second["id"]]["category_id"] == restaurants.id

    def test_rules_never_touch_other_users(
        self, client, auth_headers, second_auth_headers, bank, linked, groceries, uncategorized, db_session
    ):
        bank.transactions = [_shop("t1", "Market")]
        sync(client, auth_headers)
        [mine] = _by_merchant(client, auth_headers, "Market")
        other_wallet = client.post("/api/v1/wallets", json={"name": "Theirs"}, headers=second_auth_headers).json()
        theirs = Transaction(
            wallet_id=other_wallet["id"], category_id=uncategorized.id, category_source=CategorySource.DEFAULT,
            amount=-5, occurred_at=datetime.now(timezone.utc), merchant_key="market",
        )
        db_session.add(theirs)
        db_session.commit()

        _categorize(client, auth_headers, mine["id"], groceries.id, apply_to_similar=True)

        db_session.refresh(theirs)
        assert theirs.category_id == uncategorized.id
        assert client.get(RULES_URL, headers=second_auth_headers).json() == []

    def test_apply_to_similar_needs_a_merchant(self, client, auth_headers, bank, linked, groceries):
        bank.transactions = [raw_transaction("t1", "1")]
        sync(client, auth_headers)
        [transaction] = _transactions(client, auth_headers).values()

        response = _categorize(client, auth_headers, transaction["id"], groceries.id, apply_to_similar=True)

        assert response.status_code == 422

    def test_group_is_rejected(self, client, auth_headers, bank, linked, db_session):
        group = _system_category(db_session, "group.food_and_dining", "Food & Dining", is_group=True)
        bank.transactions = [_shop("t1", "Market")]
        sync(client, auth_headers)
        [transaction] = _transactions(client, auth_headers).values()

        assert _categorize(client, auth_headers, transaction["id"], group.id).status_code == 422

    def test_other_users_transaction_is_denied(self, client, auth_headers, second_auth_headers, bank, linked, groceries):
        bank.transactions = [_shop("t1", "Market")]
        sync(client, auth_headers)
        [transaction] = _transactions(client, auth_headers).values()

        assert _categorize(client, second_auth_headers, transaction["id"], groceries.id).status_code == 403

    def test_patching_the_category_makes_it_manual(self, client, auth_headers, bank, linked, groceries):
        bank.transactions = [_shop("t1", "Market")]
        sync(client, auth_headers)
        [transaction] = _transactions(client, auth_headers).values()

        response = client.patch(
            f"{TRANSACTIONS_URL}/{transaction['id']}", json={"category_id": groceries.id}, headers=auth_headers
        )

        assert response.json()["category_source"] == "manual"


class TestRules:
    def test_delete_keeps_categories_and_stops_matching(self, client, auth_headers, bank, linked, groceries, uncategorized):
        bank.transactions = [_shop("t1", "Market")]
        sync(client, auth_headers)
        [transaction] = _transactions(client, auth_headers).values()
        rule = _categorize(client, auth_headers, transaction["id"], groceries.id, apply_to_similar=True).json()["rule"]

        assert client.delete(f"{RULES_URL}/{rule['id']}", headers=auth_headers).status_code == 204

        assert client.get(RULES_URL, headers=auth_headers).json() == []
        assert _transactions(client, auth_headers)[transaction["id"]]["category_id"] == groceries.id
        bank.transactions = [_shop("t1", "Market"), _shop("t2", "Market")]
        sync(client, auth_headers)
        newest = max(_transactions(client, auth_headers).values(), key=lambda t: t["id"])
        assert newest["category_id"] == uncategorized.id

    def test_cannot_delete_another_users_rule(self, client, auth_headers, second_auth_headers, bank, linked, groceries):
        bank.transactions = [_shop("t1", "Market")]
        sync(client, auth_headers)
        [transaction] = _transactions(client, auth_headers).values()
        rule = _categorize(client, auth_headers, transaction["id"], groceries.id, apply_to_similar=True).json()["rule"]

        assert client.delete(f"{RULES_URL}/{rule['id']}", headers=second_auth_headers).status_code == 404
