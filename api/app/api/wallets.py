from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Wallet
from app.schemas import (
    AccountsSummary,
    AccountTypeRead,
    CurrencyTotal,
    NetWorthHistory,
    WalletCreate,
    WalletRead,
    WalletUpdate,
)
from app.services.auth import get_current_user, get_current_user_id
from app.services.net_worth import NetWorthRange, net_worth_history
from app.services.authorization import get_wallet as get_user_wallet
from app.services.helpers import apply_update
from app.services.wallets import (
    account_type_catalog,
    calculate_currency_totals,
    change_type,
    apply_account_settings,
    ensure_currency_change_allowed,
    get_user_wallets,
    summarize_accounts,
)

router = APIRouter()


@router.get("", response_model=list[WalletRead])
def list_wallets(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return get_user_wallets(user_id, db)


# Declared before /{wallet_id} so "types" isn't parsed as an ID
@router.get("/types", response_model=list[AccountTypeRead])
def list_account_types(user_id: int = Depends(get_current_user_id)):
    """What an account can be: the types (asset or liability) and their subtypes, in Monarch's order."""
    return account_type_catalog()


# Declared before /{wallet_id} so "summary" isn't parsed as an ID
@router.get("/summary", response_model=AccountsSummary)
def get_accounts_summary(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Net worth and each account type's total (assets and liabilities), for the Accounts page."""
    return summarize_accounts(get_user_wallets(user_id, db))


# Declared before /{wallet_id} so "net-worth" isn't parsed as an ID
@router.get("/net-worth", response_model=NetWorthHistory)
def get_net_worth_history(
    period: NetWorthRange = Query(NetWorthRange.ONE_MONTH, alias="range"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Net worth at the end of each day of the range (in the user's time zone), for the Accounts chart."""
    history = net_worth_history(user, period, db)
    return {
        "range": period,
        "series": [
            {"currency": currency, "points": [{"date": day, "balance": balance} for day, balance in points]}
            for currency, points in history.items()
        ],
    }


# Declared before /{wallet_id} so "totals" isn't parsed as an ID
@router.get("/totals", response_model=list[CurrencyTotal])
def get_wallet_totals(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Combined balance per currency across the user's wallets."""
    return calculate_currency_totals(get_user_wallets(user_id, db))


@router.post("", response_model=WalletRead, status_code=status.HTTP_201_CREATED)
def create_wallet(
    wallet_in: WalletCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    wallet = Wallet(user_id=user_id, **wallet_in.model_dump())
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


@router.get("/{wallet_id}", response_model=WalletRead)
def get_wallet(
    wallet_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return get_user_wallet(wallet_id, user_id, db)


@router.patch("/{wallet_id}", response_model=WalletRead)
def update_wallet(
    wallet_id: int,
    wallet_in: WalletUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    wallet = get_user_wallet(wallet_id, user_id, db)
    ensure_currency_change_allowed(wallet, wallet_in.currency, db)
    change_type(wallet, wallet_in.type, wallet_in.subtype)
    apply_account_settings(wallet, wallet_in, db)
    apply_update(
        wallet,
        wallet_in,
        exclude={"type", "subtype", "balance", "credit_limit", "invert_balance", "is_hidden", "exclude_balance", "hide_transactions"},
    )
    db.commit()
    db.refresh(wallet)
    return wallet


@router.delete("/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wallet(
    wallet_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    wallet = get_user_wallet(wallet_id, user_id, db)
    db.delete(wallet)
    db.commit()
