from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.transaction import Transaction


class WalletType(str, Enum):
    BANK = "bank"
    CASH = "cash"
    DIGITAL = "digital"
    STASH = "stash"


class Wallet(TimestampMixin, Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[WalletType]
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=Decimal("0"))

    user: Mapped["User"] = relationship(back_populates="wallets")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="wallet", cascade="all, delete-orphan")


# Import here to avoid circular imports
from app.models.transaction import Transaction

# Computed column: balance = initial_balance + sum(transactions.amount)
Wallet.balance = column_property(
    Wallet.initial_balance + func.coalesce(
        select(func.sum(Transaction.amount))
        .where(Transaction.wallet_id == Wallet.id)
        .correlate(Wallet)
        .scalar_subquery(),
        0
    )
)
