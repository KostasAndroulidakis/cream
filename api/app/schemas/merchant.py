from enum import StrEnum

from pydantic import BaseModel


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
