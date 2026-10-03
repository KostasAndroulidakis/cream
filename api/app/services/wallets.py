"""Wallet business logic."""

from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.models import Transaction, Wallet, WalletType
from app.schemas import AccountTypeRead, CurrencyTotal
from app.services.account_types import ACCOUNT_TYPES, InvalidSubtypeError, resolve_subtype


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


def account_type_catalog() -> list[AccountTypeRead]:
    """Every kind of account with its subtypes, in Monarch's order."""
    return [
        AccountTypeRead(
            type=wallet_type,
            label=info.label,
            account_class=info.account_class,
            subtypes=[{"key": subtype.key, "label": subtype.label} for subtype in info.subtypes],
        )
        for wallet_type, info in ACCOUNT_TYPES.items()
    ]


def change_type(wallet: Wallet, new_type: WalletType | None, new_subtype: str | None) -> None:
    """Set the type and subtype together: the subtype must belong to the type; a new type alone starts at its default."""
    wallet_type = new_type or wallet.type
    if new_subtype is None and wallet_type == wallet.type:
        return
    try:
        wallet.subtype = resolve_subtype(wallet_type, new_subtype)
    except InvalidSubtypeError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error
    wallet.type = wallet_type
