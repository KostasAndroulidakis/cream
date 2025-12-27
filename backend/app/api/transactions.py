from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction, Wallet
from app.schemas import TransactionCreate, TransactionRead, TransactionUpdate
from app.services.auth import get_current_user_id

router = APIRouter()


def verify_wallet_ownership(wallet_id: int, user_id: int, db: Session) -> Wallet:
    """Verify that the user owns the wallet."""
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if wallet.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return wallet


def get_user_transaction(transaction_id: int, user_id: int, db: Session) -> Transaction:
    """Get a transaction and verify the user owns its wallet."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    # Verify user owns the wallet
    wallet = db.query(Wallet).filter(Wallet.id == transaction.wallet_id).first()
    if not wallet or wallet.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return transaction


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    wallet_id: int | None = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List transactions for user's wallets."""
    # Get all wallet IDs owned by user
    user_wallet_ids = [w.id for w in db.query(Wallet.id).filter(Wallet.user_id == user_id).all()]

    query = db.query(Transaction).filter(Transaction.wallet_id.in_(user_wallet_ids))

    if wallet_id is not None:
        # Verify user owns this specific wallet
        if wallet_id not in user_wallet_ids:
            raise HTTPException(status_code=403, detail="Access denied")
        query = query.filter(Transaction.wallet_id == wallet_id)

    return query.order_by(Transaction.occurred_at.desc()).all()


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_in: TransactionCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # Verify user owns the wallet
    verify_wallet_ownership(transaction_in.wallet_id, user_id, db)

    transaction = Transaction(**transaction_in.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return get_user_transaction(transaction_id, user_id, db)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    transaction_in: TransactionUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    transaction = get_user_transaction(transaction_id, user_id, db)

    for key, value in transaction_in.model_dump(exclude_unset=True).items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    transaction = get_user_transaction(transaction_id, user_id, db)
    db.delete(transaction)
    db.commit()
