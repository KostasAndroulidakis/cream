"""Wallet business logic."""

from collections import defaultdict
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.models import Transaction, Wallet, WalletType
from app.schemas import AccountsSummary, AccountTypeRead, CurrencyTotal, WalletUpdate
from app.services.account_types import ACCOUNT_TYPES, InvalidSubtypeError, resolve_subtype


def get_user_wallets(user_id: int, db: Session) -> list[Wallet]:
    """All wallets of a user, oldest first."""
    return db.query(Wallet).filter(Wallet.user_id == user_id).order_by(Wallet.id).all()


def calculate_currency_totals(wallets: list[Wallet]) -> list[CurrencyTotal]:
    """Sum wallet balances per currency (no conversion between currencies).

    Accounts set to "Exclude account balance" are left out.
    """
    balances: dict[str, Decimal] = defaultdict(Decimal)
    counts: dict[str, int] = defaultdict(int)
    for wallet in wallets:
        if wallet.exclude_balance:
            continue
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
            subtypes=[
                {"key": subtype.key, "label": subtype.label, "manual": subtype.manual} for subtype in info.subtypes
            ],
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


def transactions_total(wallet_id: int, db: Session) -> Decimal:
    return Decimal(
        db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.wallet_id == wallet_id))
    )


def set_balance(wallet: Wallet, balance: Decimal, db: Session) -> None:
    """Make the account show this balance now; its transactions stay as they are."""
    wallet.initial_balance = balance - transactions_total(wallet.id, db)


def apply_account_settings(wallet: Wallet, changes: WalletUpdate, db: Session) -> None:
    """Edit Account: the new balance first, then the sign flip if "Invert account balance" changed."""
    values = changes.model_dump(exclude_unset=True)
    balance = values.get("balance")
    current = balance if balance is not None else wallet.initial_balance + transactions_total(wallet.id, db)

    invert = values.get("invert_balance")
    if invert is not None and invert != wallet.invert_balance:
        current = -current
        wallet.invert_balance = invert
    if balance is not None or invert is not None:
        set_balance(wallet, current, db)

    if "credit_limit" in values:
        wallet.credit_limit = values["credit_limit"]
    for flag in ("is_hidden", "exclude_balance", "hide_transactions"):
        if values.get(flag) is not None:
            setattr(wallet, flag, values[flag])


def summarize_accounts(wallets: list[Wallet]) -> AccountsSummary:
    """Net worth and each type's total, from the same rule (calculate_currency_totals) so they always agree."""
    types = [
        {"type": wallet_type, "account_class": info.account_class, "totals": calculate_currency_totals(members)}
        for wallet_type, info in ACCOUNT_TYPES.items()
        if (members := [wallet for wallet in wallets if wallet.type == wallet_type])
    ]
    return AccountsSummary(net_worth=calculate_currency_totals(wallets), types=types)
