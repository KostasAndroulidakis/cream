"""The review inbox: transactions waiting for the user to look at them ("Needs review")."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Transaction, UserPreferences
from app.services.authorization import get_user_wallet_ids_subquery
from app.services.categorization.auto import Decision


def needs_review_on_import(preferences: UserPreferences, decision: Decision) -> bool:
    """Whether a new bank transaction waits in the inbox, as the user's preferences say."""
    return preferences.review_new_transactions or (
        preferences.review_uncategorized_transactions and not decision.is_categorized
    )


def inbox_page(user_id: int, limit: int, offset: int, db: Session) -> tuple[int, list[Transaction]]:
    """Total count and one page (newest first) of the user's transactions that need review.

    Hidden ones are left out but keep their status: shown again, they are back in the inbox.
    """
    condition = (
        Transaction.wallet_id.in_(get_user_wallet_ids_subquery(user_id, db)),
        Transaction.needs_review,
        Transaction.is_visible,
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
