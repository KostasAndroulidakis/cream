from enum import StrEnum

from pydantic import BaseModel, Field

from app.services.categorization.merchants import MERCHANT_MAX


class MerchantRead(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class MerchantOrder(StrEnum):
    """How Settings › Merchants sorts the list (Monarch's choices)."""

    TRANSACTION_COUNT = "transaction_count"
    ALPHABETICAL = "alphabetical"


class MerchantSummary(MerchantRead):
    """A merchant in Settings › Merchants: with how many of the user's transactions it has."""

    transaction_count: int


class MerchantUpdate(BaseModel):
    """Edit merchant: the name it shows under everywhere."""

    name: str = Field(..., min_length=1, max_length=MERCHANT_MAX)
