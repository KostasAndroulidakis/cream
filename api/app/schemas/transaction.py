from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.transaction import CategorySource


class TransactionCreate(BaseModel):
    wallet_id: int
    category_id: int
    amount: Decimal
    description: str | None = None
    occurred_at: datetime


class TransactionUpdate(BaseModel):
    category_id: int | None = None
    amount: Decimal | None = None
    description: str | None = None
    occurred_at: datetime | None = None
    # Not nullable: a transaction is either hidden or not. Omit the field to leave it unchanged.
    is_hidden: bool = False


class MerchantRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class TransactionRead(BaseModel):
    id: int
    wallet_id: int
    category_id: int
    category_source: CategorySource
    amount: Decimal
    description: str | None
    occurred_at: datetime
    counterparty: str | None
    merchant_category_code: str | None
    # Normalized merchant of an imported transaction; null when there is nothing to match rules on
    merchant_key: str | None
    # Who the money went to or came from, as the user sees it; null when unknown
    merchant: MerchantRead | None
    # True when imported from a bank (not entered by hand)
    is_imported: bool
    # Left out of lists and statistics, still part of the wallet balance
    is_hidden: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionPage(BaseModel):
    # All matching transactions, not just this page
    total: int
    items: list[TransactionRead]


# Upper bound for one bulk request (a few pages of the transactions list)
MAX_BULK_TRANSACTIONS = 500
BulkTransactionIds = Field(..., min_length=1, max_length=MAX_BULK_TRANSACTIONS)


class BulkTransactionChanges(BaseModel):
    """Changes for every selected transaction. A field left out means "no change"."""

    category_id: int | None = None
    occurred_at: datetime | None = None
    # null clears the notes
    description: str | None = None
    is_hidden: bool | None = None

    @field_validator("category_id", "occurred_at", "is_hidden")
    @classmethod
    def not_null(cls, value):
        # Only the notes can be cleared; for the rest, leave the field out to keep it as it is
        if value is None:
            raise ValueError("Leave the field out to keep it as it is")
        return value

    @model_validator(mode="after")
    def has_a_change(self):
        if not self.model_fields_set:
            raise ValueError("Nothing to change")
        return self


class BulkTransactionUpdate(BaseModel):
    transaction_ids: list[int] = BulkTransactionIds
    changes: BulkTransactionChanges


class BulkTransactionDelete(BaseModel):
    transaction_ids: list[int] = BulkTransactionIds


class BulkResult(BaseModel):
    # How many transactions were changed or deleted
    affected: int
