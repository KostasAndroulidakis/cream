"""The review inbox: transactions that still need a category."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Transaction
from app.services.authorization import get_user_wallet_ids_subquery
from app.services.categorization.system_categories import UNCATEGORIZED_KEY, system_category_id


def uncategorized_page(user_id: int, limit: int, offset: int, db: Session) -> tuple[int, list[Transaction]]:
    """Total count and one page (newest first) of the user's uncategorized transactions."""
    condition = (
        Transaction.wallet_id.in_(get_user_wallet_ids_subquery(user_id, db)),
        Transaction.category_id == system_category_id(UNCATEGORIZED_KEY, db),
    )
    total = db.scalar(select(func.count()).select_from(Transaction).where(*condition)) or 0
    items = db.scalars(
        select(Transaction)
        .where(*condition)
        .order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return total, list(items)
