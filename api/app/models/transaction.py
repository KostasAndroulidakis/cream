from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text, UniqueConstraint, and_, false
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.wallet import Wallet
    from app.models.category import Category
    from app.models.merchant import Merchant


class CategorySource(str, Enum):
    """Who chose a transaction's category. Automatic choices never override the user's."""

    # The user picked it (manual entry or an explicit change)
    MANUAL = "manual"
    # A merchant rule the user created
    RULE = "rule"
    # The bank's merchant category code (MCC)
    MCC = "mcc"
    # Paired with its other side in another of the user's accounts (see categorization/transfers.py)
    TRANSFER = "transfer"
    # Nothing matched on import: the transaction stays in Uncategorized
    DEFAULT = "default"


class Transaction(TimestampMixin, Base):
    __tablename__ = "transactions"
    # A bank transaction is imported into a wallet at most once
    __table_args__ = (UniqueConstraint("wallet_id", "external_id", name="uq_transactions_wallet_external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True)
    category_source: Mapped[CategorySource] = mapped_column(
        default=CategorySource.MANUAL, server_default=CategorySource.MANUAL.value
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4))
    description: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(index=True)
    # Set only for transactions imported from a bank
    external_id: Mapped[str | None] = mapped_column(String(255))
    counterparty: Mapped[str | None] = mapped_column(String(255))
    merchant_category_code: Mapped[str | None] = mapped_column(String(4))
    # Normalized merchant identity of an imported transaction; merchant rules match on it
    merchant_key: Mapped[str | None] = mapped_column(String(255), index=True)
    # The merchant the user sees; starts as the bank's, and the user can change it
    merchant_id: Mapped[int | None] = mapped_column(ForeignKey("merchants.id", ondelete="SET NULL"), index=True)
    # Hidden from lists and statistics, but still part of the wallet balance (so it matches the bank).
    # Bank transactions are hidden instead of deleted: a deleted one would come back on the next sync.
    is_hidden: Mapped[bool] = mapped_column(default=False, server_default=false())
    # Waiting in the review inbox until the user marks it reviewed; independent of category and hiding
    needs_review: Mapped[bool] = mapped_column(default=False, server_default=false())
    # The other side of a transfer between the user's own accounts; each side points at the other
    transfer_pair_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id", ondelete="SET NULL"))

    wallet: Mapped["Wallet"] = relationship(back_populates="transactions")
    category: Mapped["Category"] = relationship(back_populates="transactions")
    # Loaded together with the transaction: every transaction response shows its merchant
    merchant: Mapped["Merchant | None"] = relationship(lazy="joined")
    # Loaded together too: a transfer side with no text of its own is shown by its pair's account
    transfer_pair: Mapped["Transaction | None"] = relationship(
        remote_side=[id], foreign_keys=[transfer_pair_id], lazy="joined", join_depth=1
    )

    @property
    def is_imported(self) -> bool:
        return self.external_id is not None

    @property
    def transfer_account_name(self) -> str | None:
        """For a transfer between the user's accounts: the account on the other side."""
        return self.transfer_pair.wallet.name if self.transfer_pair is not None else None

    @hybrid_property
    def is_visible(self) -> bool:
        """Shown in lists and counted in statistics (usable in queries too).

        Not when hidden itself, nor when its account hides all its transactions.
        """
        return not self.is_hidden and not self.wallet.hide_transactions

    @is_visible.inplace.expression
    @classmethod
    def _is_visible_expression(cls):
        from app.models.wallet import Wallet

        return and_(cls.is_hidden.is_(False), ~cls.wallet.has(Wallet.hide_transactions.is_(True)))
