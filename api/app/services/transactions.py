"""Rules for changing transactions, shared by single and bulk edits."""

from collections.abc import Iterable

from fastapi import HTTPException, status

from app.models import Transaction

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
