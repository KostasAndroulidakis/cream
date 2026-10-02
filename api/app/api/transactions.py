from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CategorySource, Transaction
from app.schemas import (
    CategorizeRequest,
    CategorizeResultRead,
    TransactionCreate,
    TransactionPage,
    TransactionRead,
    TransactionUpdate,
    ValidationErrorDetail,
)
from app.services.auth import get_current_user_id
from app.services.authorization import (
    get_transaction as get_user_transaction,
    get_wallet as verify_wallet_ownership,
    get_assignable_category,
    get_user_wallet_ids_subquery,
    verify_wallet_access,
)
from app.services.categorization.assignment import assign_category
from app.services.categorization.inbox import uncategorized_page
from app.services.categorization.rules import categorize_transaction
from app.services.helpers import apply_update
from app.services.validation import ValidationResult, validate_transaction

router = APIRouter()

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


def _raise_if_invalid(result: ValidationResult) -> None:
    if not result.is_valid:
        errors = [ValidationErrorDetail(field=e.field, message=e.message).model_dump() for e in result.errors]
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=errors)


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    wallet_id: int | None = None,
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List transactions for the user's wallets, newest first."""
    if wallet_id is not None:
        # Filter by specific wallet - verify ownership first
        verify_wallet_access(wallet_id, user_id, db)
        query = db.query(Transaction).filter(Transaction.wallet_id == wallet_id)
    else:
        # List all transactions - use subquery for efficiency
        wallet_ids_subquery = get_user_wallet_ids_subquery(user_id, db)
        query = db.query(Transaction).filter(Transaction.wallet_id.in_(wallet_ids_subquery))

    return (
        query.order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


# Declared before /{transaction_id} so "uncategorized" isn't read as an ID
@router.get("/uncategorized", response_model=TransactionPage)
def list_uncategorized(
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """The review inbox: transactions still waiting for a category, newest first."""
    total, items = uncategorized_page(user_id, limit, offset, db)
    return {"total": total, "items": items}


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
    _raise_if_invalid(validation_result)

    # Verify user owns the wallet
    verify_wallet_ownership(transaction_in.wallet_id, user_id, db)

    # Category must be accessible (own or system) and not a group
    get_assignable_category(transaction_in.category_id, user_id, db)

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
    _raise_if_invalid(validation_result)

    # Verify user has access to the new category if being changed
    if "category_id" in update_data and update_data["category_id"] is not None:
        get_assignable_category(update_data["category_id"], user_id, db)

    apply_update(transaction, transaction_in)
    if "category_id" in update_data:
        # The user chose this category: automatic categorization leaves it alone from now on
        assign_category(transaction, transaction.category_id, CategorySource.MANUAL)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.post("/{transaction_id}/categorize", response_model=CategorizeResultRead)
def categorize(
    transaction_id: int,
    request: CategorizeRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Set the category; with apply_to_similar, also for the merchant's other and future transactions."""
    transaction = get_user_transaction(transaction_id, user_id, db)
    category = get_assignable_category(request.category_id, user_id, db)
    return categorize_transaction(transaction, category, request.apply_to_similar, user_id, db)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    transaction = get_user_transaction(transaction_id, user_id, db)
    db.delete(transaction)
    db.commit()
