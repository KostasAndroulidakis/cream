from __future__ import annotations

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin
from app.services.categorization.merchants import MERCHANT_MAX


class Merchant(TimestampMixin, Base):
    """Who a transaction's money went to or came from, under the name the user sees and can change."""

    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(MERCHANT_MAX))
    aliases: Mapped[list[MerchantAlias]] = relationship(back_populates="merchant", cascade="all, delete-orphan")


class MerchantAlias(Base):
    """A name that means this merchant: how a bank writes it ("WOLT*ATHENS") or what the user called it.

    Matching goes by alias, so renaming a merchant keeps the bank's spellings pointing at it,
    and merging moves them to the merchant they now mean.
    """

    __tablename__ = "merchant_aliases"
    # A name means one merchant per user; the unique index also serves lookups by user
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_merchant_aliases_user_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id", ondelete="CASCADE"), index=True)
    # Case-insensitive identity of the name (see merchant_name_key)
    key: Mapped[str] = mapped_column(String(MERCHANT_MAX))
    merchant: Mapped[Merchant] = relationship(back_populates="aliases")
