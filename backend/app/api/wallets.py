from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Wallet
from app.schemas import WalletCreate, WalletRead, WalletUpdate
from app.services.auth import get_current_user_id

router = APIRouter()


def get_user_wallet(wallet_id: int, user_id: int, db: Session) -> Wallet:
    """Helper to get a wallet and verify ownership."""
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if wallet.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return wallet


@router.get("", response_model=list[WalletRead])
def list_wallets(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return db.query(Wallet).filter(Wallet.user_id == user_id).all()


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

    for key, value in wallet_in.model_dump(exclude_unset=True).items():
        setattr(wallet, key, value)

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
