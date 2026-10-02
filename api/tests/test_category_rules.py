"""Category groups, the transfer type, and how they affect transactions and statistics."""

import pytest

from app.models import Category
from app.models.category import CategoryType

CATEGORIES_URL = "/api/v1/categories"
TRANSACTIONS_URL = "/api/v1/transactions"
STATISTICS_URL = "/api/v1/statistics"
OCCURRED_AT = "2026-01-15T10:00:00Z"


def _system_category(db_session, name, category_type, *, parent=None, is_group=False, key=None):
    category = Category(
        user_id=None,
        parent_id=parent.id if parent else None,
        name=name,
        type=category_type,
        is_group=is_group,
        key=key,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def food_group(db_session):
    return _system_category(db_session, "Food & Dining", CategoryType.EXPENSE, is_group=True, key="group.food_and_dining")


@pytest.fixture
def groceries(db_session, food_group):
    return _system_category(
        db_session, "Groceries", CategoryType.EXPENSE, parent=food_group, key="food_and_dining.groceries"
    )


@pytest.fixture
def transfer_category(db_session):
    return _system_category(db_session, "Transfer", CategoryType.TRANSFER, key="transfers.transfer")


@pytest.fixture
def wallet(client, auth_headers):
    response = client.post("/api/v1/wallets", json={"name": "Main", "initial_balance": "1000"}, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


def _post_transaction(client, headers, wallet_id, category_id, amount):
    return client.post(
        TRANSACTIONS_URL,
        json={"wallet_id": wallet_id, "category_id": category_id, "amount": amount, "occurred_at": OCCURRED_AT},
        headers=headers,
    )


class TestCategoryShape:
    def test_list_includes_key_and_group_flag(self, client, auth_headers, groceries):
        categories = client.get(CATEGORIES_URL, headers=auth_headers).json()

        group, child = categories
        assert group["is_group"] is True and group["key"] == "group.food_and_dining"
        assert child["is_group"] is False and child["parent_id"] == group["id"]

    def test_user_category_has_no_key(self, client, auth_headers):
        response = client.post(CATEGORIES_URL, json={"name": "Vinyl", "type": "expense"}, headers=auth_headers)

        assert response.json()["key"] is None
        assert response.json()["is_group"] is False


class TestParentTypeRule:
    def test_subcategory_under_matching_group(self, client, auth_headers, food_group):
        response = client.post(
            CATEGORIES_URL, json={"name": "Souvlaki", "type": "expense", "parent_id": food_group.id}, headers=auth_headers
        )

        assert response.status_code == 201

    def test_subcategory_type_must_match_parent(self, client, auth_headers, food_group):
        response = client.post(
            CATEGORIES_URL, json={"name": "Royalties", "type": "income", "parent_id": food_group.id}, headers=auth_headers
        )

        assert response.status_code == 400


class TestGroupsAreNotAssignable:
    def test_transaction_in_group_rejected(self, client, auth_headers, wallet, food_group):
        response = _post_transaction(client, auth_headers, wallet["id"], food_group.id, "-10")

        assert response.status_code == 422

    def test_transaction_in_category_accepted(self, client, auth_headers, wallet, groceries):
        response = _post_transaction(client, auth_headers, wallet["id"], groceries.id, "-10")

        assert response.status_code == 201


class TestTransfersInStatistics:
    def test_transfers_change_balance_but_not_income_or_expenses(
        self, client, auth_headers, wallet, groceries, transfer_category
    ):
        _post_transaction(client, auth_headers, wallet["id"], groceries.id, "-40")
        _post_transaction(client, auth_headers, wallet["id"], transfer_category.id, "-200")

        stats = client.get(STATISTICS_URL, headers=auth_headers).json()

        assert float(stats["total_expenses"]) == 40
        assert float(stats["total_balance"]) == 760
        assert [c["category_name"] for c in stats["spending_by_category"]] == ["Groceries"]


class TestTransactionPagination:
    def test_newest_first_with_limit_and_offset(self, client, auth_headers, wallet, groceries):
        for day in ("10", "12", "11"):
            client.post(
                TRANSACTIONS_URL,
                json={
                    "wallet_id": wallet["id"], "category_id": groceries.id, "amount": "-1",
                    "occurred_at": f"2026-01-{day}T10:00:00Z", "description": day,
                },
                headers=auth_headers,
            )

        first_page = client.get(TRANSACTIONS_URL, params={"limit": 2}, headers=auth_headers).json()
        second_page = client.get(TRANSACTIONS_URL, params={"limit": 2, "offset": 2}, headers=auth_headers).json()

        assert [t["description"] for t in first_page] == ["12", "11"]
        assert [t["description"] for t in second_page] == ["10"]

    def test_limit_is_capped(self, client, auth_headers):
        response = client.get(TRANSACTIONS_URL, params={"limit": 10_000}, headers=auth_headers)

        assert response.status_code == 422
