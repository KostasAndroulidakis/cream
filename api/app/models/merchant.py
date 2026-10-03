from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin
from app.services.categorization.merchants import MERCHANT_MAX


class Merchant(TimestampMixin, Base):
    """Who a transaction's money went to or came from, under the name the user sees and can change."""

    __tablename__ = "merchants"
    # One merchant per name per user; the unique index also serves lookups by user
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_merchants_user_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(MERCHANT_MAX))
    # Case- and spacing-insensitive identity of the name, so "STARBUCKS" and "Starbucks" are one merchant
    key: Mapped[str] = mapped_column(String(MERCHANT_MAX))
