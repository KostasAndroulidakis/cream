"""Rules for changing transactions, shared by single and bulk edits."""

from collections.abc import Iterable, Mapping
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import CategorySource, Transaction
from app.services.authorization import ImportedTransactionError, get_assignable_category
from app.services.categorization.assignment import assign_category
from app.services.validation import raise_if_invalid, validate_transaction

# What the bank decides for its own transactions; changing them would break the match with the bank balance
BANK_OWNED_FIELDS = frozenset({"amount", "occurred_at"})


class BankOwnedFieldError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The bank sets the amount and date of its transactions",
        )


def ensure_editable(transaction: Transaction, fields: Iterable[str]) -> None:
    """Refuse changes to bank-owned fields of an imported transaction."""
    if transaction.is_imported and BANK_OWNED_FIELDS.intersection(fields):
        raise BankOwnedFieldError()


def bulk_update(transactions: list[Transaction], changes: Mapping[str, Any], user_id: int, db: Session) -> int:
    """Apply the same changes to every transaction, or to none of them if any change is refused."""
    # Check everything first, so a refusal leaves nothing half-changed
    for transaction in transactions:
        ensure_editable(transaction, changes)
        if "occurred_at" in changes:
            raise_if_invalid(validate_transaction(amount=transaction.amount, occurred_at=changes["occurred_at"]))
    if "category_id" in changes:
        get_assignable_category(changes["category_id"], user_id, db)

    for transaction in transactions:
        for field, value in changes.items():
            if field == "category_id":
                # The user chose it: automatic categorization leaves it alone from now on
                assign_category(transaction, value, CategorySource.MANUAL)
            else:
                setattr(transaction, field, value)
    db.commit()
    return len(transactions)


def bulk_delete(transactions: list[Transaction], db: Session) -> int:
    """Delete transactions entered by hand; refuse all if any came from a bank."""
    if any(transaction.is_imported for transaction in transactions):
        raise ImportedTransactionError()
    for transaction in transactions:
        db.delete(transaction)
    db.commit()
    return len(transactions)
