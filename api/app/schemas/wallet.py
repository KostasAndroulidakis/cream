from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, model_validator

from app.models.wallet import SUBTYPE_MAX, AccountClass, WalletType
from app.services.account_types import resolve_subtype

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


Subtype = Annotated[str, Field(min_length=1, max_length=SUBTYPE_MAX)]


class WalletCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: WalletType = WalletType.CASH
    # One of the type's subtypes; left out, the type's first (as Monarch preselects it)
    subtype: Subtype | None = None
    currency: CurrencyCode = DEFAULT_CURRENCY
    initial_balance: Decimal = Decimal("0")

    @model_validator(mode="after")
    def subtype_of_its_type(self):
        self.subtype = resolve_subtype(self.type, self.subtype)
        return self


class WalletUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    # A new type without a subtype starts at that type's first subtype
    type: WalletType | None = None
    subtype: Subtype | None = None
    currency: CurrencyCode | None = None


class WalletRead(BaseModel):
    id: int
    name: str
    type: WalletType
    subtype: str
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


class SubtypeRead(BaseModel):
    key: str
    label: str


class AccountTypeRead(BaseModel):
    """One kind of account and its subtypes, in Monarch's order (the first subtype is the default)."""

    type: WalletType
    label: str
    account_class: AccountClass
    subtypes: list[SubtypeRead]
