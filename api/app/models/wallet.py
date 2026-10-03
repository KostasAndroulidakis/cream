from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, false, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.transaction import Transaction


# Longest subtype key the catalog may use
SUBTYPE_MAX = 50


class AccountClass(str, Enum):
    """What an account means for net worth: something you own, or something you owe."""

    ASSET = "asset"
    LIABILITY = "liability"


class WalletType(str, Enum):
    """The kind of account, as Monarch groups them; the subtypes are in `services/account_types.py`."""

    CASH = "cash"
    INVESTMENT = "investment"
    REAL_ESTATE = "real_estate"
    VEHICLE = "vehicle"
    VALUABLES = "valuables"
    OTHER_ASSET = "other_asset"
    CREDIT_CARD = "credit_card"
    MORTGAGE = "mortgage"
    LOAN = "loan"
    OTHER_LIABILITY = "other_liability"


class Wallet(TimestampMixin, Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[WalletType]
    # One of the type's subtypes (e.g. "checking" for cash), checked against the catalog on every change
    subtype: Mapped[str] = mapped_column(String(SUBTYPE_MAX))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4), default=Decimal("0"))
    # Credit cards only; informational (Monarch's "Credit limit")
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), default=None)
    # The bank reports this account's balance with the wrong sign: CREAM flips it
    invert_balance: Mapped[bool] = mapped_column(default=False, server_default=false())
    # Left off the Accounts page (and the dashboard's account list)
    is_hidden: Mapped[bool] = mapped_column(default=False, server_default=false())
    # Left out of the total balance and the account group totals
    exclude_balance: Mapped[bool] = mapped_column(default=False, server_default=false())
    # Its transactions are left out of every list and statistic (they still make up its balance)
    hide_transactions: Mapped[bool] = mapped_column(default=False, server_default=false())

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
