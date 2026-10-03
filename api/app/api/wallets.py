from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Wallet
from app.schemas import AccountTypeRead, CurrencyTotal, WalletCreate, WalletRead, WalletUpdate
from app.services.auth import get_current_user_id
from app.services.authorization import get_wallet as get_user_wallet
from app.services.helpers import apply_update
from app.services.wallets import (
    account_type_catalog,
    calculate_currency_totals,
    change_type,
    ensure_currency_change_allowed,
    get_user_wallets,
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
    apply_update(wallet, wallet_in, exclude={"type", "subtype"})
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
