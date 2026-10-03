from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CategorySource, Transaction
from app.schemas import (
    BulkResult,
    BulkTransactionDelete,
    BulkTransactionUpdate,
    CategorizeRequest,
    CategorizeResultRead,
    TransactionCreate,
    TransactionPage,
    TransactionRead,
    TransactionUpdate,
)
from app.services.auth import get_current_user_id
from app.services.authorization import (
    get_transaction as get_user_transaction,
    get_transactions as get_user_transactions,
    get_wallet as verify_wallet_ownership,
    get_assignable_category,
    ImportedTransactionError,
    get_user_wallet_ids_subquery,
    verify_wallet_access,
)
from app.services.categorization.assignment import assign_category
from app.services.categorization.rules import categorize_transaction
from app.services.helpers import apply_update
from app.services.review import inbox_page
from app.services.transactions import bulk_delete, bulk_update, ensure_editable
from app.services.validation import raise_if_invalid, validate_transaction

router = APIRouter()

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    wallet_id: int | None = None,
    include_hidden: bool = False,
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List transactions for the user's wallets, newest first. Hidden ones only on request."""
    if wallet_id is not None:
        # Filter by specific wallet - verify ownership first
        verify_wallet_access(wallet_id, user_id, db)
        query = db.query(Transaction).filter(Transaction.wallet_id == wallet_id)
    else:
        # List all transactions - use subquery for efficiency
        wallet_ids_subquery = get_user_wallet_ids_subquery(user_id, db)
        query = db.query(Transaction).filter(Transaction.wallet_id.in_(wallet_ids_subquery))
    if not include_hidden:
        query = query.filter(Transaction.is_visible)

    return (
        query.order_by(Transaction.occurred_at.desc(), Transaction.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


# Declared before /{transaction_id} so "needs-review" isn't read as an ID
@router.get("/needs-review", response_model=TransactionPage)
def list_needs_review(
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """The review inbox: transactions that need review, newest first. Hidden ones are left out."""
    total, items = inbox_page(user_id, limit, offset, db)
    return {"total": total, "items": items}


# Bulk routes are declared before /{transaction_id} so their names aren't read as IDs
@router.post("/bulk-update", response_model=BulkResult)
def bulk_update_transactions(
    request: BulkTransactionUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Apply the same changes to several transactions: all of them or, if any is refused, none."""
    transactions = get_user_transactions(request.transaction_ids, user_id, db)
    changes = request.changes.model_dump(exclude_unset=True)
    return BulkResult(affected=bulk_update(transactions, changes, user_id, db))


@router.post("/bulk-delete", response_model=BulkResult)
def bulk_delete_transactions(
    request: BulkTransactionDelete,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete several transactions entered by hand; refused (409) if any came from a bank."""
    transactions = get_user_transactions(request.transaction_ids, user_id, db)
    return BulkResult(affected=bulk_delete(transactions, db))


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
    raise_if_invalid(validation_result)

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
    ensure_editable(transaction, update_data)
    amount = update_data.get("amount", transaction.amount)
    occurred_at = update_data.get("occurred_at", transaction.occurred_at)
    category_id = update_data.get("category_id", transaction.category_id)

    # Validate updated transaction data
    validation_result = validate_transaction(
        amount=amount,
        occurred_at=occurred_at,
        category_id=category_id,
    )
    raise_if_invalid(validation_result)

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
    if transaction.is_imported:
        raise ImportedTransactionError()
    db.delete(transaction)
    db.commit()
