"""Authorization service for ownership verification.

Centralizes all ownership and access control checks to ensure SSOT.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Category, Transaction, Wallet


class NotFoundError(HTTPException):
    """Resource not found."""

    def __init__(self, resource: str):
        super().__init__(status_code=404, detail=f"{resource} not found")


class AccessDeniedError(HTTPException):
    """User does not have access to this resource."""

    def __init__(self):
        super().__init__(status_code=403, detail="Access denied")


class SystemResourceError(HTTPException):
    """Cannot modify system resource."""

    def __init__(self, resource: str):
        super().__init__(status_code=403, detail=f"Cannot modify system default {resource}")


def get_wallet(wallet_id: int, user_id: int, db: Session) -> Wallet:
    """Get a wallet and verify the user owns it.

    Args:
        wallet_id: The wallet ID to fetch
        user_id: The authenticated user's ID
        db: Database session

    Returns:
        The wallet if found and owned by user

    Raises:
        NotFoundError: Wallet does not exist
        AccessDeniedError: User does not own the wallet
    """
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise NotFoundError("Wallet")
    if wallet.user_id != user_id:
        raise AccessDeniedError()
    return wallet


def get_category(
    category_id: int,
    user_id: int,
    db: Session,
    *,
    allow_system: bool = True,
    require_ownership: bool = False,
) -> Category:
    """Get a category with configurable access control.

    Args:
        category_id: The category ID to fetch
        user_id: The authenticated user's ID
        db: Database session
        allow_system: If True, system default categories are accessible
        require_ownership: If True, user must own the category (for mutations)

    Returns:
        The category if accessible

    Raises:
        NotFoundError: Category does not exist
        AccessDeniedError: User does not have access
        SystemResourceError: Cannot modify system category (when require_ownership=True)
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise NotFoundError("Category")

    # System default category
    if category.user_id is None:
        if require_ownership:
            raise SystemResourceError("category")
        if allow_system:
            return category
        raise AccessDeniedError()

    # User-owned category
    if category.user_id != user_id:
        raise AccessDeniedError()

    return category


def get_transaction(transaction_id: int, user_id: int, db: Session) -> Transaction:
    """Get a transaction and verify the user owns its wallet.

    Args:
        transaction_id: The transaction ID to fetch
        user_id: The authenticated user's ID
        db: Database session

    Returns:
        The transaction if found and user owns its wallet

    Raises:
        NotFoundError: Transaction does not exist
        AccessDeniedError: User does not own the transaction's wallet
    """
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise NotFoundError("Transaction")

    # Verify user owns the wallet
    wallet = db.query(Wallet).filter(Wallet.id == transaction.wallet_id).first()
    if not wallet or wallet.user_id != user_id:
        raise AccessDeniedError()

    return transaction


def get_user_wallet_ids(user_id: int, db: Session) -> list[int]:
    """Get all wallet IDs owned by a user.

    Args:
        user_id: The authenticated user's ID
        db: Database session

    Returns:
        List of wallet IDs owned by the user
    """
    return [w.id for w in db.query(Wallet.id).filter(Wallet.user_id == user_id).all()]


def get_user_wallet_ids_subquery(user_id: int, db: Session):
    """Get a subquery for user's wallet IDs.

    More efficient than get_user_wallet_ids() for filtering - avoids loading
    IDs into Python memory and lets the database optimize the query.

    Args:
        user_id: The authenticated user's ID
        db: Database session

    Returns:
        SQLAlchemy subquery that can be used with .in_()
    """
    return db.query(Wallet.id).filter(Wallet.user_id == user_id).scalar_subquery()


def verify_wallet_access(wallet_id: int, user_id: int, db: Session) -> None:
    """Verify user has access to a wallet without returning it.

    Raises:
        NotFoundError: Wallet does not exist
        AccessDeniedError: User does not own the wallet
    """
    get_wallet(wallet_id, user_id, db)


def verify_category_access(
    category_id: int,
    user_id: int,
    db: Session,
    *,
    allow_system: bool = True,
) -> None:
    """Verify user has access to a category without returning it.

    Raises:
        NotFoundError: Category does not exist
        AccessDeniedError: User does not have access
    """
    get_category(category_id, user_id, db, allow_system=allow_system)
