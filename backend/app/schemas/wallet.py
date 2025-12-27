from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.wallet import WalletType


class WalletCreate(BaseModel):
    name: str
    type: WalletType = WalletType.BANK
    currency: str = "EUR"
    initial_balance: Decimal = Decimal("0")


class WalletUpdate(BaseModel):
    name: str | None = None
    type: WalletType | None = None
    currency: str | None = None


class WalletRead(BaseModel):
    id: int
    name: str
    type: WalletType
    currency: str
    initial_balance: Decimal
    balance: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}
