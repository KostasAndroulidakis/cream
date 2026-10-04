from enum import StrEnum

from pydantic import BaseModel, Field

from app.services.categorization.merchants import MERCHANT_MAX
from app.services.websites import WEBSITE_MAX


class MerchantRead(BaseModel):
    id: int
    name: str
    # Where its logo comes from (GET /logos/{website}): the user's choice, else a known merchant's
    website: str | None = Field(default=None, validation_alias="shown_website")

    model_config = {"from_attributes": True}


class MerchantOrder(StrEnum):
    """How Settings › Merchants sorts the list (Monarch's choices)."""

    TRANSACTION_COUNT = "transaction_count"
    ALPHABETICAL = "alphabetical"


class MerchantSummary(MerchantRead):
    """A merchant in Settings › Merchants: with how many of the user's transactions it has."""

    transaction_count: int


class MerchantUpdate(BaseModel):
    """Edit merchant: the name it shows under everywhere, and its website (empty = the catalog's, if any)."""

    name: str = Field(..., min_length=1, max_length=MERCHANT_MAX)
    website: str | None = Field(default=None, max_length=WEBSITE_MAX)
