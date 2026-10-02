from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

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
    # True when imported from a bank (not entered by hand)
    is_imported: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionPage(BaseModel):
    # All matching transactions, not just this page
    total: int
    items: list[TransactionRead]
