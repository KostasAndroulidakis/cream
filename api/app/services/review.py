"""The review inbox: transactions waiting for the user to look at them ("Needs review")."""

from sqlalchemy import ColumnElement, func, select, update
from sqlalchemy.orm import Session

from app.models import Transaction, UserPreferences
from app.services.authorization import get_user_wallet_ids_subquery
from app.services.categorization.auto import Decision
from app.services.transaction_order import newest_first


def needs_review_on_import(preferences: UserPreferences, decision: Decision) -> bool:
    """Whether a new bank transaction waits in the inbox, as the user's preferences say."""
    return preferences.review_new_transactions or (
        preferences.review_uncategorized_transactions and not decision.is_categorized
    )


def _in_inbox(user_id: int, db: Session) -> tuple[ColumnElement[bool], ...]:
    """The inbox: the user's visible transactions that need review.

    Hidden ones are left out but keep their status: shown again, they are back in the inbox.
    """
    return (
        Transaction.wallet_id.in_(get_user_wallet_ids_subquery(user_id, db)),
        Transaction.needs_review,
        Transaction.is_visible,
    )


def inbox_page(user_id: int, limit: int, offset: int, db: Session) -> tuple[int, list[Transaction]]:
    """Total count and one page (newest first) of the inbox."""
    condition = _in_inbox(user_id, db)
    total = db.scalar(select(func.count()).select_from(Transaction).where(*condition)) or 0
    items = db.scalars(newest_first(select(Transaction).where(*condition)).offset(offset).limit(limit))
    return total, list(items)


def mark_all_reviewed(user_id: int, db: Session) -> int:
    """Empty the inbox in one go; returns how many transactions were marked reviewed."""
    result = db.execute(
        update(Transaction)
        .where(*_in_inbox(user_id, db))
        .values(needs_review=False)
        # Nothing loaded needs to follow: the request ends here
        .execution_options(synchronize_session=False)
    )
    db.commit()
    return result.rowcount
