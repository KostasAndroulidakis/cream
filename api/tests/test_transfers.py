"""Transfers between the user's own accounts: both sides found and filed as Transfers › Transfer."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.models import (
    BankAccount,
    BankConnection,
    Category,
    CategoryOverride,
    CategorySource,
    CategoryType,
    ConnectionStatus,
    Transaction,
)
from app.services.categorization.go_between_payments import MAX_PAYMENT_COST, match_go_between_payments
from app.services.categorization.merchants import merchant_key
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

    def add_transaction(wallet_id, amount, when=DAY, source=CategorySource.DEFAULT, text=None):
        transaction = Transaction(
            wallet_id=wallet_id,
            category_id=uncategorized.id,
            category_source=source,
            amount=Decimal(amount),
            occurred_at=when,
            description=text,
            merchant_key=merchant_key(None, text),
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


@pytest.fixture
def link(db_session, registered_user):
    """Link one of the user's accounts to a bank connection at the institution Enable Banking names."""

    def link_wallet(wallet_id, aspsp_name, status=ConnectionStatus.ACTIVE):
        connection = BankConnection(
            user_id=registered_user["id"], aspsp_name=aspsp_name, aspsp_country="GR", status=status
        )
        connection.accounts.append(
            BankAccount(uid=f"{aspsp_name}-{wallet_id}", name="Account", currency="EUR", wallet_id=wallet_id)
        )
        db_session.add(connection)
        db_session.commit()

    return link_wallet


class TestGoBetweenPayments:
    """A purchase through PayPal with a bank card: PayPal shows the purchase, the bank what it took."""

    @pytest.fixture
    def paypal(self, wallets, link):
        """Account B is the user's PayPal."""
        link(wallets[1], "PayPal")
        return wallets[1]

    def _match(self, db_session, user):
        paired = match_go_between_payments(user["id"], db_session)
        db_session.commit()
        return paired

    def test_the_bank_line_is_the_purchase_and_paypals_side_a_transfer(
        self, db_session, registered_user, wallets, paypal, add, transfer_category
    ):
        """Canva: 12.00 on PayPal; Revolut took 12.75 (conversion and a fee), what it really cost."""
        purchase = add(paypal, "-12.00", text="Canva Pty Limited")
        bank_line = add(wallets[0], "-12.75", text="Paypal *canvaptylim")

        assert self._match(db_session, registered_user) == 1

        assert _is_transfer(purchase, transfer_category)
        assert not _is_transfer(bank_line, transfer_category)
        assert (purchase.transfer_pair_id, bank_line.transfer_pair_id) == (bank_line.id, purchase.id)

    def test_the_list_shows_the_purchase_once(
        self, client, auth_headers, db_session, registered_user, wallets, paypal, add, transfer_category
    ):
        """PayPal's side is hidden: still in PayPal's balance, out of the list."""
        purchase = add(paypal, "-12.00", text="Canva Pty Limited")
        add(wallets[0], "-12.75", text="Paypal *canvaptylim")
        self._match(db_session, registered_user)

        listed = client.get("/api/v1/transactions", headers=auth_headers).json()

        assert purchase.is_hidden
        assert [Decimal(t["amount"]) for t in listed] == [Decimal("-12.75")]

    def test_shown_again_by_the_user_it_stays_shown(
        self, db_session, registered_user, wallets, paypal, add, transfer_category
    ):
        purchase = add(paypal, "-12.00", text="Canva Pty Limited")
        add(wallets[0], "-12.75", text="Paypal *canvaptylim")
        self._match(db_session, registered_user)
        purchase.is_hidden = False
        db_session.commit()

        self._match(db_session, registered_user)

        assert not purchase.is_hidden

    def test_the_same_amount(self, db_session, registered_user, wallets, paypal, add, transfer_category):
        purchase = add(paypal, "-9.99", DAY + timedelta(days=1), text="Spotify AB")
        add(wallets[0], "-9.99", text="Paypal *spotify")

        self._match(db_session, registered_user)

        assert _is_transfer(purchase, transfer_category)

    @pytest.mark.parametrize("paid", ["-11.99", str(Decimal("-12.01") * (1 + MAX_PAYMENT_COST))])
    def test_not_when_the_bank_took_less_or_far_more(
        self, db_session, registered_user, wallets, paypal, add, transfer_category, paid
    ):
        add(paypal, "-12.00", text="Canva Pty Limited")
        add(wallets[0], paid, text="Paypal *canvaptylim")

        assert self._match(db_session, registered_user) == 0

    def test_not_too_far_apart(self, db_session, registered_user, wallets, paypal, add, transfer_category):
        add(paypal, "-12.00", DAY + MATCH_WINDOW + timedelta(hours=1), text="Canva Pty Limited")
        add(wallets[0], "-12.75", text="Paypal *canvaptylim")

        assert self._match(db_session, registered_user) == 0

    def test_a_purchase_paypal_doesnt_show_stays_on_the_bank(
        self, db_session, registered_user, wallets, paypal, add, transfer_category
    ):
        """E.g. "Paypal *a148246": the purchase is on the bank's side only, so it still counts."""
        add(wallets[0], "-36.52", text="Paypal *a148246")

        assert self._match(db_session, registered_user) == 0

    def test_not_without_paypal_linked(self, db_session, registered_user, wallets, add, transfer_category):
        add(wallets[1], "-12.00", text="Canva Pty Limited")
        add(wallets[0], "-12.75", text="Paypal *canvaptylim")

        assert self._match(db_session, registered_user) == 0

    def test_only_a_line_paid_through_paypal(
        self, db_session, registered_user, wallets, paypal, add, transfer_category
    ):
        add(paypal, "-12.00", text="Canva Pty Limited")
        add(wallets[0], "-12.00", text="Canva")

        assert self._match(db_session, registered_user) == 0

    def test_the_closest_in_time(self, db_session, registered_user, wallets, paypal, add, transfer_category):
        later = add(paypal, "-12.00", DAY + timedelta(days=2), text="Canva Pty Limited")
        closer = add(paypal, "-12.00", DAY + timedelta(hours=1), text="Canva Pty Limited")
        add(wallets[0], "-12.75", text="Paypal *canvaptylim")

        self._match(db_session, registered_user)

        assert _is_transfer(closer, transfer_category) and not _is_transfer(later, transfer_category)

    @pytest.mark.parametrize("source", [CategorySource.MANUAL, CategorySource.RULE])
    def test_the_users_own_choice_on_paypal_stays(
        self, db_session, registered_user, wallets, paypal, add, transfer_category, source
    ):
        add(paypal, "-12.00", source=source, text="Canva Pty Limited")
        add(wallets[0], "-12.75", text="Paypal *canvaptylim")

        assert self._match(db_session, registered_user) == 0

    def test_an_atm_at_a_linked_bank_is_not(
        self, client, auth_headers, db_session, registered_user, wallets, link, add, transfer_category
    ):
        """The cash leaves through the bank's ATM; it doesn't go into the user's account there."""
        alpha = client.post(WALLETS_URL, json={"name": "Alpha"}, headers=auth_headers).json()["id"]
        link(alpha, "Alpha Bank")
        add(alpha, "-50.00")
        add(wallets[0], "-50.00", text="Cash at Alpha Bank")

        assert self._match(db_session, registered_user) == 0

    def test_a_paired_bank_line_isnt_paired_again_as_a_transfer(
        self, client, auth_headers, db_session, registered_user, wallets, paypal, add, transfer_category
    ):
        third = client.post(WALLETS_URL, json={"name": "C"}, headers=auth_headers).json()["id"]
        add(paypal, "-12.00", text="Canva Pty Limited")
        bank_line = add(wallets[0], "-12.75", text="Paypal *canvaptylim")
        self._match(db_session, registered_user)
        add(third, "12.75")

        assert _match(db_session, registered_user) == 0
        assert not _is_transfer(bank_line, transfer_category)


def test_sync_pairs_a_purchase_through_paypal(
    client, auth_headers, db_session, bank, wallets, add, link, transfer_category
):
    # Expired, so the fake bank's lines are synced into the other account only
    link(wallets[1], "PayPal", ConnectionStatus.EXPIRED)
    purchase = add(wallets[1], "-12.00", text="Canva Pty Limited")
    connect_and_link(client, auth_headers, bank)
    bank.transactions = [raw_transaction("t1", "12.75", creditor={"name": "Paypal *canvaptylim"})]

    sync(client, auth_headers)

    db_session.refresh(purchase)
    listed = client.get("/api/v1/transactions", headers=auth_headers).json()
    assert _is_transfer(purchase, transfer_category)
    assert next(t for t in listed if t["counterparty"] == "Paypal *canvaptylim")["category_source"] != "transfer"
