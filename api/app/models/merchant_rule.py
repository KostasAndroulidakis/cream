from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category


class MerchantRule(TimestampMixin, Base):
    """'Transactions from this merchant go to this category', created by the user."""

    __tablename__ = "merchant_rules"
    # One rule per merchant per user; the unique index also serves lookups by user
    __table_args__ = (UniqueConstraint("user_id", "merchant_key", name="uq_merchant_rules_user_merchant"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    merchant_key: Mapped[str] = mapped_column(String(255))
    # The merchant as the bank wrote it, for display
    merchant_name: Mapped[str] = mapped_column(String(255))
    # Deleting a user category removes the rules that point to it
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), index=True)

    category: Mapped["Category"] = relationship()
