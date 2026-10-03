from __future__ import annotations

from sqlalchemy import ForeignKey, false, true
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin


class UserPreferences(TimestampMixin, Base):
    """How the app behaves for one user (Settings › Preferences). A user without a row gets the defaults."""

    __tablename__ = "user_preferences"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    # Every new bank transaction waits in the review inbox
    review_new_transactions: Mapped[bool] = mapped_column(default=False, server_default=false())
    # New bank transactions that no rule or MCC could categorize wait in the review inbox
    review_uncategorized_transactions: Mapped[bool] = mapped_column(default=True, server_default=true())
