from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.wallet import Wallet


class ConnectionStatus(str, Enum):
    # Bank login started, waiting for the user to come back with a code
    PENDING = "pending"
    ACTIVE = "active"
    # Consent ran out (usually after 180 days); the user must reconnect
    EXPIRED = "expired"


class BankConnection(TimestampMixin, Base):
    """One consent at one bank (ASPSP), covering one or more accounts."""

    __tablename__ = "bank_connections"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    aspsp_name: Mapped[str] = mapped_column(String(255))
    aspsp_country: Mapped[str] = mapped_column(String(2))
    status: Mapped[ConnectionStatus]
    # Random value tying the bank's redirect back to this request (CSRF protection)
    auth_state: Mapped[str | None] = mapped_column(String(64), unique=True)
    session_id: Mapped[str | None] = mapped_column(String(255))
    valid_until: Mapped[datetime | None]

    user: Mapped["User"] = relationship()
    accounts: Mapped[list["BankAccount"]] = relationship(back_populates="connection", cascade="all, delete-orphan")


class BankAccount(TimestampMixin, Base):
    """An account the bank shared, optionally linked to a CREAM wallet."""

    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    connection_id: Mapped[int] = mapped_column(ForeignKey("bank_connections.id", ondelete="CASCADE"), index=True)
    # Provider's account identifier, used for balance and transaction calls
    uid: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    currency: Mapped[str] = mapped_column(String(3))
    # Only the last characters, enough to tell accounts apart
    iban_last4: Mapped[str | None] = mapped_column(String(4))
    wallet_id: Mapped[int | None] = mapped_column(ForeignKey("wallets.id", ondelete="SET NULL"), unique=True)
    last_synced_at: Mapped[datetime | None]

    connection: Mapped["BankConnection"] = relationship(back_populates="accounts")
    wallet: Mapped["Wallet | None"] = relationship()
