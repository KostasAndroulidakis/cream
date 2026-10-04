"""Purchases paid through a go-between whose account the user links too (PayPal), with a card of theirs.

PayPal shows the purchase ("Canva Pty Limited" −12.00), and the bank shows what PayPal took from the
card ("Paypal *canvaptylim" −12.75): one purchase, seen twice. The bank's amount is what the user paid,
conversion and fees included, so the bank's line stays the purchase and PayPal's becomes a hidden
transfer: the money only passed through PayPal, and the list shows the purchase once. A purchase found
on one side only stays as it is.
Pairing (transfers.py) runs first: money moved to or from the PayPal balance is paired there.
"""

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BankAccount, BankConnection, CategorySource, Transaction
from app.services.authorization import get_user_wallet_ids_subquery
from app.services.banking.institutions import find_institution
from app.services.categorization.assignment import assign_category
from app.services.categorization.transfers import MATCH_WINDOW, REPLACEABLE_SOURCES, transfer_category_id
from app.services.merchant_catalog import account_institution

# How much more than the go-between's amount the bank may take: currency conversion plus the card's fees
# (Canva: 12.00 on PayPal, 12.62 + 0.13 fee at Revolut)
MAX_PAYMENT_COST = Decimal("0.10")


def match_go_between_payments(user_id: int, db: Session) -> int:
    """Pair each bank line paid through a linked go-between ("Paypal *canvaptylim") with the go-between's
    purchase it paid for; the go-between's side passes the money on (see `_pass_on`).

    The purchase is the go-between's outflow at most MATCH_WINDOW from the bank's, for the same amount or
    up to MAX_PAYMENT_COST less (the closest in time, then in amount). Only automatic categories on the
    go-between's side give way. Returns how many go-between purchases became transfers.
    """
    category_id = transfer_category_id(user_id, db)
    if category_id is None:
        return 0
    wallets_by_institution = _linked_wallets_by_institution(user_id, db)
    if not wallets_by_institution:
        return 0
    outflows = db.scalars(
        select(Transaction)
        .where(
            Transaction.wallet_id.in_(get_user_wallet_ids_subquery(user_id, db)),
            Transaction.amount < 0,
            Transaction.transfer_pair_id.is_(None),
        )
        .order_by(Transaction.occurred_at, Transaction.id)
    ).all()
    purchases_by_wallet: dict[int, list[Transaction]] = defaultdict(list)
    for outflow in outflows:
        if outflow.category_source in REPLACEABLE_SOURCES:
            purchases_by_wallet[outflow.wallet_id].append(outflow)
    paired = 0
    for bank_line in outflows:
        go_between_wallets = _go_between_wallets(bank_line, wallets_by_institution)
        if not go_between_wallets:
            continue
        purchases = [purchase for wallet_id in go_between_wallets for purchase in purchases_by_wallet[wallet_id]]
        purchase = _closest_purchase(bank_line, purchases)
        if purchase is None:
            continue
        purchases_by_wallet[purchase.wallet_id].remove(purchase)
        _pass_on(purchase, bank_line, category_id)
        paired += 1
    return paired


def _pass_on(purchase: Transaction, bank_line: Transaction, transfer_category_id: int) -> None:
    """The go-between's purchase becomes a transfer, hidden (the bank's line is the one shown), and each
    side points at the other. Hidden only now: if the user shows it again, it stays shown."""
    assign_category(purchase, transfer_category_id, CategorySource.TRANSFER)
    purchase.is_hidden = True
    purchase.transfer_pair_id, bank_line.transfer_pair_id = bank_line.id, purchase.id


def _go_between_wallets(bank_line: Transaction, wallets_by_institution: dict[str, set[int]]) -> set[int]:
    """The user's accounts at the go-between a bank line was paid through; none when it wasn't, or when
    the line is the go-between's own."""
    institution = account_institution(bank_line.merchant_key) if bank_line.merchant_key else None
    wallets = wallets_by_institution.get(institution, set()) if institution else set()
    return set() if bank_line.wallet_id in wallets else wallets


def _closest_purchase(bank_line: Transaction, purchases: list[Transaction]) -> Transaction | None:
    """The purchase the bank line paid for: within MATCH_WINDOW, the bank taking the purchase's amount
    or up to MAX_PAYMENT_COST more; the closest in time, then in amount."""
    paid = -bank_line.amount

    def distance(purchase: Transaction) -> tuple[timedelta, Decimal]:
        return abs(purchase.occurred_at - bank_line.occurred_at), paid + purchase.amount

    fitting = [
        purchase
        for purchase in purchases
        if -purchase.amount <= paid <= -purchase.amount * (1 + MAX_PAYMENT_COST)
        and distance(purchase)[0] <= MATCH_WINDOW
    ]
    return min(fitting, key=distance, default=None)


def _linked_wallets_by_institution(user_id: int, db: Session) -> dict[str, set[int]]:
    """The user's accounts linked to a bank connection, by the institution (catalog key) they're at."""
    rows = db.execute(
        select(BankConnection.aspsp_name, BankAccount.wallet_id)
        .join(BankAccount.connection)
        .where(BankConnection.user_id == user_id, BankAccount.wallet_id.is_not(None))
    ).all()
    wallets: dict[str, set[int]] = defaultdict(set)
    for aspsp_name, wallet_id in rows:
        institution = find_institution(aspsp_name)
        if institution is not None:
            wallets[institution.key].add(wallet_id)
    return wallets
