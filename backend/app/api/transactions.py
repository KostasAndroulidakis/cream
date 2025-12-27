from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction, Wallet
from app.schemas import TransactionCreate, TransactionRead, TransactionUpdate
from app.services.auth import get_current_user_id
from app.services.authorization import (
    get_transaction as get_user_transaction,
    get_wallet as verify_wallet_ownership,
    get_user_wallet_ids_subquery,
    verify_category_access,
    verify_wallet_access,
)
from app.services.helpers import apply_update
from app.services.validation import validate_transaction

router = APIRouter()


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    wallet_id: int | None = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List transactions for user's wallets."""
    if wallet_id is not None:
        # Filter by specific wallet - verify ownership first
        verify_wallet_access(wallet_id, user_id, db)
        query = db.query(Transaction).filter(Transaction.wallet_id == wallet_id)
    else:
        # List all transactions - use subquery for efficiency
        wallet_ids_subquery = get_user_wallet_ids_subquery(user_id, db)
        query = db.query(Transaction).filter(Transaction.wallet_id.in_(wallet_ids_subquery))

    return query.order_by(Transaction.occurred_at.desc()).all()


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_in: TransactionCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # Validate transaction data
    validation_result = validate_transaction(
        amount=transaction_in.amount,
        occurred_at=transaction_in.occurred_at,
        wallet_id=transaction_in.wallet_id,
        category_id=transaction_in.category_id,
    )
    if not validation_result.is_valid:
        errors = [{"field": e.field, "message": e.message} for e in validation_result.errors]
        raise HTTPException(status_code=422, detail=errors)

    # Verify user owns the wallet
    verify_wallet_ownership(transaction_in.wallet_id, user_id, db)

    # Verify user has access to the category (user-owned or system default)
    if transaction_in.category_id is not None:
        verify_category_access(transaction_in.category_id, user_id, db)

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

    # Get values for validation (use existing if not provided)
    update_data = transaction_in.model_dump(exclude_unset=True)
    amount = update_data.get("amount", transaction.amount)
    occurred_at = update_data.get("occurred_at", transaction.occurred_at)
    category_id = update_data.get("category_id", transaction.category_id)

    # Validate updated transaction data
    validation_result = validate_transaction(
        amount=amount,
        occurred_at=occurred_at,
        category_id=category_id,
    )
    if not validation_result.is_valid:
        errors = [{"field": e.field, "message": e.message} for e in validation_result.errors]
        raise HTTPException(status_code=422, detail=errors)

    # Verify user has access to the new category if being changed
    if "category_id" in update_data and update_data["category_id"] is not None:
        verify_category_access(update_data["category_id"], user_id, db)

    apply_update(transaction, transaction_in)
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
