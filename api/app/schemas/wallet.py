from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

from app.models.wallet import WalletType

DEFAULT_CURRENCY = "EUR"
CURRENCY_CODE_PATTERN = r"^[A-Z]{3}$"


def _normalize_currency(value: object) -> object:
    return value.strip().upper() if isinstance(value, str) else value


# ISO 4217 style code, accepted in any case ("eur" -> "EUR")
CurrencyCode = Annotated[
    str,
    BeforeValidator(_normalize_currency),
    Field(pattern=CURRENCY_CODE_PATTERN, description="ISO 4217 currency code, e.g. EUR"),
]


class WalletCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: WalletType = WalletType.BANK
    currency: CurrencyCode = DEFAULT_CURRENCY
    initial_balance: Decimal = Decimal("0")


class WalletUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    type: WalletType | None = None
    currency: CurrencyCode | None = None


class WalletRead(BaseModel):
    id: int
    name: str
    type: WalletType
    currency: str
    initial_balance: Decimal
    balance: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class CurrencyTotal(BaseModel):
    """Combined balance of all wallets in one currency. Currencies are never mixed."""

    currency: str
    balance: Decimal
    wallet_count: int
