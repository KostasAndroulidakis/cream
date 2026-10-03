from __future__ import annotations

from sqlalchemy import ForeignKey, false, true
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin

# The defaults, used for new rows and for users who haven't changed anything yet
REVIEW_NEW_TRANSACTIONS = False
REVIEW_UNCATEGORIZED_TRANSACTIONS = True


def _server_default(value: bool):
    return true() if value else false()


class UserPreferences(TimestampMixin, Base):
    """How the app behaves for one user (Settings › Preferences). A user without a row gets the defaults."""

    __tablename__ = "user_preferences"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    # Every new bank transaction waits in the review inbox
    review_new_transactions: Mapped[bool] = mapped_column(
        default=REVIEW_NEW_TRANSACTIONS, server_default=_server_default(REVIEW_NEW_TRANSACTIONS)
    )
    # New bank transactions that no rule or MCC could categorize wait in the review inbox
    review_uncategorized_transactions: Mapped[bool] = mapped_column(
        default=REVIEW_UNCATEGORIZED_TRANSACTIONS, server_default=_server_default(REVIEW_UNCATEGORIZED_TRANSACTIONS)
    )

    @classmethod
    def defaults(cls, user_id: int) -> UserPreferences:
        # Column defaults apply only when a row is inserted, so an unsaved object needs them set here
        return cls(
            user_id=user_id,
            review_new_transactions=REVIEW_NEW_TRANSACTIONS,
            review_uncategorized_transactions=REVIEW_UNCATEGORIZED_TRANSACTIONS,
        )
