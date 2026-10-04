"""Transfers between the user's own accounts: money out of one, and the same money into another.

Monarch gets these from Plaid as the Transfer category; CREAM pairs the two sides itself. Both go to
Transfers › Transfer, which cash flow and budgets leave out. A payment to someone else has no other
side among the user's accounts, so it stays an expense.
"""

from collections import defaultdict
from collections.abc import Iterable
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import CategorySource, Transaction
from app.services.authorization import get_user_wallet_ids_subquery
from app.services.categorization.assignment import assign_category
from app.services.categorization.system_categories import hidden_category_ids, system_category_ids

TRANSFER_KEY = "transfers.transfer"
# Banks book the two sides up to a few days apart (PayPal → Revolut: often the next day)
MATCH_WINDOW = timedelta(days=3)
# Only automatic choices give way to a transfer, never the user's own or their rules'
REPLACEABLE_SOURCES = (CategorySource.DEFAULT, CategorySource.MCC)


def match_transfers(user_id: int, db: Session) -> int:
    """Pair each outflow with an inflow of the same amount in another of the user's accounts, at most
    MATCH_WINDOW apart (the closest in time), and file both as a transfer.

    Each side remembers the other (`transfer_pair_id`). Returns how many transactions became transfers.
    A side whose pair arrives in a later sync is paired then.
    """
    category_id = transfer_category_id(user_id, db)
    if category_id is None:
        return 0
    candidates = db.scalars(
        select(Transaction)
        .where(
            Transaction.wallet_id.in_(get_user_wallet_ids_subquery(user_id, db)),
            or_(
                Transaction.category_source.in_(REPLACEABLE_SOURCES),
                # Filed as a transfer before pairs were kept: paired again
                Transaction.category_source == CategorySource.TRANSFER,
            ),
            # Not paired yet; a purchase through PayPal and its bank line are a pair too (go_between_payments.py)
            Transaction.transfer_pair_id.is_(None),
            Transaction.amount != 0,
        )
        .order_by(Transaction.occurred_at, Transaction.id)
    ).all()
    inflows_by_amount = _inflows_by_amount(candidates)
    paired = 0
    for outflow in (transaction for transaction in candidates if transaction.amount < 0):
        inflows = inflows_by_amount[-outflow.amount]
        inflow = _closest_inflow(outflow, inflows)
        if inflow is None:
            continue
        inflows.remove(inflow)
        _pair(outflow, inflow, category_id)
        paired += 2
    return paired


def _pair(outflow: Transaction, inflow: Transaction, category_id: int) -> None:
    for side, other in ((outflow, inflow), (inflow, outflow)):
        assign_category(side, category_id, CategorySource.TRANSFER)
        side.transfer_pair_id = other.id


def transfer_category_id(user_id: int, db: Session) -> int | None:
    """Transfers › Transfer, unless the user deleted it."""
    category_id = system_category_ids([TRANSFER_KEY], db).get(TRANSFER_KEY)
    return None if category_id is None or category_id in hidden_category_ids(user_id, db) else category_id


def _inflows_by_amount(transactions: Iterable[Transaction]) -> dict[Decimal, list[Transaction]]:
    inflows: dict[Decimal, list[Transaction]] = defaultdict(list)
    for transaction in transactions:
        if transaction.amount > 0:
            inflows[transaction.amount].append(transaction)
    return inflows


def _closest_inflow(outflow: Transaction, inflows: list[Transaction]) -> Transaction | None:
    """The inflow in another account nearest in time to the outflow, within MATCH_WINDOW."""

    def distance(inflow: Transaction) -> timedelta:
        return abs(inflow.occurred_at - outflow.occurred_at)

    in_window = [
        inflow for inflow in inflows if inflow.wallet_id != outflow.wallet_id and distance(inflow) <= MATCH_WINDOW
    ]
    return min(in_window, key=distance, default=None)
