"""The order transactions are listed in, shared by every list."""

from sqlalchemy import Select, case
from sqlalchemy.orm import aliased

from app.models import Transaction


def newest_first(query: Select[tuple[Transaction]]) -> Select[tuple[Transaction]]:
    """Newest first. The two sides of a transfer booked the same day sit together: money in right above
    money out, so read upwards (forward in time) the money leaves first and arrives next. Sides booked
    on different days stay on their own day, as the banks booked them.
    """
    pair = aliased(Transaction)
    # A same-day pair takes the outflow's place; everything else keeps its own
    position = case(
        (pair.occurred_at == Transaction.occurred_at, case((Transaction.amount < 0, Transaction.id), else_=pair.id)),
        else_=Transaction.id,
    )
    return query.outerjoin(pair, pair.id == Transaction.transfer_pair_id).order_by(
        Transaction.occurred_at.desc(), position.desc(), Transaction.amount.desc()
    )
