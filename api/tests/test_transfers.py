"""Transfers between the user's own accounts: both sides found and filed as Transfers › Transfer."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.models import Category, CategoryOverride, CategorySource, CategoryType, Transaction
from app.services.categorization.transfers import MATCH_WINDOW, TRANSFER_KEY, match_transfers
from tests.bank_fakes import connect_and_link, raw_transaction, sync

WALLETS_URL = "/api/v1/wallets"
DAY = datetime(2026, 9, 20, 12, tzinfo=timezone.utc)


@pytest.fixture
def transfer_category(db_session):
    category = Category(user_id=None, name="Transfer", type=CategoryType.TRANSFER, key=TRANSFER_KEY)
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def wallets(client, auth_headers):
    """Two of the user's accounts, e.g. Revolut and PayPal."""
    return [client.post(WALLETS_URL, json={"name": name}, headers=auth_headers).json()["id"] for name in ("A", "B")]


@pytest.fixture
def add(db_session, uncategorized):
    """Add a transaction as an import leaves it: in Uncategorized, chosen by no one."""

    def add_transaction(wallet_id, amount, when=DAY, source=CategorySource.DEFAULT):
        transaction = Transaction(
            wallet_id=wallet_id,
            category_id=uncategorized.id,
            category_source=source,
            amount=Decimal(amount),
            occurred_at=when,
        )
        db_session.add(transaction)
        db_session.commit()
        return transaction

    return add_transaction


def _match(db_session, user):
    paired = match_transfers(user["id"], db_session)
    db_session.commit()
    return paired


def _is_transfer(transaction, category):
    return transaction.category_id == category.id and transaction.category_source is CategorySource.TRANSFER


class TestMatchTransfers:
    def test_money_out_of_one_account_into_another_is_a_transfer(
        self, db_session, registered_user, wallets, add, transfer_category
    ):
        out, into = add(wallets[0], "-1060.00"), add(wallets[1], "1060.00", DAY + timedelta(days=1))

        assert _match(db_session, registered_user) == 2

        assert _is_transfer(out, transfer_category) and _is_transfer(into, transfer_category)

    def test_too_far_apart_is_not(self, db_session, registered_user, wallets, add, transfer_category):
        add(wallets[0], "-20.00")
        add(wallets[1], "20.00", DAY + MATCH_WINDOW + timedelta(hours=1))

        assert _match(db_session, registered_user) == 0

    def test_same_account_is_not(self, db_session, registered_user, wallets, add, transfer_category):
        add(wallets[0], "-20.00")
        add(wallets[0], "20.00")

        assert _match(db_session, registered_user) == 0

    def test_different_amounts_are_not(self, db_session, registered_user, wallets, add, transfer_category):
        add(wallets[0], "-12.75")
        add(wallets[1], "12.00")

        assert _match(db_session, registered_user) == 0

    def test_the_closest_inflow_is_the_pair(self, db_session, registered_user, wallets, add, transfer_category):
        out = add(wallets[0], "-50.00")
        later = add(wallets[1], "50.00", DAY + timedelta(days=2))
        closer = add(wallets[1], "50.00", DAY + timedelta(hours=3))

        _match(db_session, registered_user)

        assert _is_transfer(out, transfer_category) and _is_transfer(closer, transfer_category)
        assert not _is_transfer(later, transfer_category)

    def test_each_side_pairs_once(self, db_session, registered_user, wallets, add, transfer_category):
        add(wallets[0], "-50.00")
        add(wallets[0], "-50.00", DAY + timedelta(hours=1))
        add(wallets[1], "50.00")

        assert _match(db_session, registered_user) == 2

    @pytest.mark.parametrize("source", [CategorySource.MANUAL, CategorySource.RULE])
    def test_the_users_own_choice_stays(self, db_session, registered_user, wallets, add, transfer_category, source):
        add(wallets[0], "-20.00", source=source)
        add(wallets[1], "20.00")

        assert _match(db_session, registered_user) == 0

    def test_an_mcc_guess_gives_way(self, db_session, registered_user, wallets, add, transfer_category):
        add(wallets[0], "-20.00", source=CategorySource.MCC)
        add(wallets[1], "20.00")

        assert _match(db_session, registered_user) == 2

    def test_nothing_when_the_user_deleted_transfer(
        self, db_session, registered_user, wallets, add, transfer_category
    ):
        hidden = CategoryOverride(user_id=registered_user["id"], category_id=transfer_category.id, is_hidden=True)
        db_session.add(hidden)
        add(wallets[0], "-20.00")
        add(wallets[1], "20.00")

        assert _match(db_session, registered_user) == 0

    def test_only_the_users_own_accounts(
        self, client, db_session, registered_user, second_auth_headers, wallets, add, transfer_category
    ):
        theirs = client.post(WALLETS_URL, json={"name": "Theirs"}, headers=second_auth_headers).json()["id"]
        add(wallets[0], "-20.00")
        add(theirs, "20.00")

        assert _match(db_session, registered_user) == 0


def test_sync_pairs_an_import_with_its_other_side(
    client, auth_headers, db_session, bank, wallets, add, transfer_category
):
    """The PayPal → Revolut case: the inflow arrives by sync, the outflow is already in another account."""
    out = add(wallets[0], "-370.62", datetime(2026, 9, 19, 12, tzinfo=timezone.utc))
    connect_and_link(client, auth_headers, bank)
    bank.transactions = [raw_transaction("t1", "370.62", indicator="CRDT", debtor={"name": "PAYPAL EUROPE"})]

    sync(client, auth_headers)

    db_session.refresh(out)
    imported = client.get("/api/v1/transactions", headers=auth_headers).json()
    assert _is_transfer(out, transfer_category)
    assert next(t for t in imported if Decimal(t["amount"]) > 0)["category_source"] == "transfer"


def test_each_side_points_at_the_other(db_session, registered_user, wallets, add, transfer_category):
    out, into = add(wallets[0], "-20.00"), add(wallets[1], "20.00")

    _match(db_session, registered_user)

    assert (out.transfer_pair_id, into.transfer_pair_id) == (into.id, out.id)


def test_transfers_filed_before_pairs_were_kept_are_paired(
    db_session, registered_user, wallets, add, transfer_category
):
    out = add(wallets[0], "-20.00", source=CategorySource.TRANSFER)
    into = add(wallets[1], "20.00", source=CategorySource.TRANSFER)

    _match(db_session, registered_user)

    assert (out.transfer_pair_id, into.transfer_pair_id) == (into.id, out.id)


class TestListOrder:
    """Within a day the list is otherwise in import order, so a pair could land far apart."""

    def _amounts(self, client, headers):
        return [Decimal(t["amount"]) for t in client.get("/api/v1/transactions", headers=headers).json()]

    def test_a_same_day_pair_sits_together_money_in_right_above_money_out(
        self, client, auth_headers, db_session, registered_user, wallets, add, transfer_category
    ):
        add(wallets[1], "1.36")
        add(wallets[0], "-2.00")
        add(wallets[0], "-7.77")
        add(wallets[0], "-1.36")
        _match(db_session, registered_user)

        assert self._amounts(client, auth_headers) == [Decimal(a) for a in ("1.36", "-1.36", "-7.77", "-2.00")]

    def test_a_pair_on_different_days_stays_on_its_days(
        self, client, auth_headers, db_session, registered_user, wallets, add, transfer_category
    ):
        add(wallets[0], "-370.62")
        add(wallets[1], "-5.00")
        add(wallets[1], "370.62", DAY + timedelta(days=1))
        _match(db_session, registered_user)

        assert self._amounts(client, auth_headers) == [Decimal(a) for a in ("370.62", "-5.00", "-370.62")]


def test_a_side_without_text_is_shown_by_its_pairs_account(
    client, auth_headers, db_session, registered_user, wallets, add, transfer_category
):
    """PayPal's side of a withdrawal to Revolut comes with no text at all."""
    add(wallets[0], "-20.00")
    add(wallets[1], "20.00")
    _match(db_session, registered_user)

    listed = client.get("/api/v1/transactions", headers=auth_headers).json()
    names = {Decimal(t["amount"]): t["transfer_account_name"] for t in listed}

    assert names == {Decimal("-20.00"): "B", Decimal("20.00"): "A"}
