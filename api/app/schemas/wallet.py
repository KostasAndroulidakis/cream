from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.wallet import WalletType


class WalletCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: WalletType = WalletType.BANK
    currency: str = Field("EUR", min_length=3, max_length=3)
    initial_balance: Decimal = Decimal("0")


class WalletUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    type: WalletType | None = None
    currency: str | None = Field(None, min_length=3, max_length=3)


class WalletRead(BaseModel):
    id: int
    name: str
    type: WalletType
    currency: str
    initial_balance: Decimal
    balance: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}
