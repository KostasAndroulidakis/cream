"""Wallet business logic."""

from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.models import Transaction, Wallet
from app.schemas import CurrencyTotal


def get_user_wallets(user_id: int, db: Session) -> list[Wallet]:
    """All wallets of a user, oldest first."""
    return db.query(Wallet).filter(Wallet.user_id == user_id).order_by(Wallet.id).all()


def calculate_currency_totals(wallets: list[Wallet]) -> list[CurrencyTotal]:
    """Sum wallet balances per currency (no conversion between currencies)."""
    balances: dict[str, Decimal] = defaultdict(Decimal)
    counts: dict[str, int] = defaultdict(int)
    for wallet in wallets:
        balances[wallet.currency] += wallet.balance
        counts[wallet.currency] += 1
    return [
        CurrencyTotal(currency=currency, balance=balances[currency], wallet_count=counts[currency])
        for currency in sorted(balances)
    ]


def has_transactions(wallet_id: int, db: Session) -> bool:
    return bool(db.scalar(select(exists().where(Transaction.wallet_id == wallet_id))))


def ensure_currency_change_allowed(wallet: Wallet, new_currency: str | None, db: Session) -> None:
    """Existing amounts were recorded in the old currency, so changing it would corrupt them."""
    if new_currency is None or new_currency == wallet.currency:
        return
    if has_transactions(wallet.id, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Currency can't be changed once an account has transactions",
        )
