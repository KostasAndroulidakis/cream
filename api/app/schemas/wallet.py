from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, model_validator

from app.models.wallet import SUBTYPE_MAX, AccountClass, WalletType
from app.services.account_types import resolve_subtype
from app.services.currencies import DEFAULT_CURRENCY, ensure_supported

CURRENCY_CODE_PATTERN = r"^[A-Z]{3}$"


def _normalize_currency(value: object) -> object:
    return value.strip().upper() if isinstance(value, str) else value


# ISO 4217 style code, accepted in any case ("eur" -> "EUR"), and one CREAM supports
CurrencyCode = Annotated[
    str,
    BeforeValidator(_normalize_currency),
    Field(pattern=CURRENCY_CODE_PATTERN, description="ISO 4217 currency code; only EUR for now"),
    AfterValidator(ensure_supported),
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
    """Edit Account. Fields left out stay as they are."""

    name: str | None = Field(None, min_length=1, max_length=100)
    # A new type without a subtype starts at that type's first subtype
    type: WalletType | None = None
    subtype: Subtype | None = None
    currency: CurrencyCode | None = None
    # The balance the account should show now; the starting balance absorbs the difference
    balance: Decimal | None = None
    # Credit cards only; null clears it
    credit_limit: Decimal | None = Field(None, ge=0)
    # Turning it on or off flips the balance's sign (after `balance`, when both are sent)
    invert_balance: bool | None = None
    is_hidden: bool | None = None
    exclude_balance: bool | None = None
    hide_transactions: bool | None = None


class WalletRead(BaseModel):
    id: int
    name: str
    type: WalletType
    subtype: str
    currency: str
    initial_balance: Decimal
    balance: Decimal
    credit_limit: Decimal | None
    invert_balance: bool
    is_hidden: bool
    exclude_balance: bool
    hide_transactions: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CurrencyTotal(BaseModel):
    """Combined balance of all wallets in one currency. Currencies are never mixed."""

    currency: str
    balance: Decimal
    wallet_count: int


class TypeTotal(BaseModel):
    """What the accounts of one type add up to (an asset or a liability), per currency."""

    type: WalletType
    account_class: AccountClass
    totals: list[CurrencyTotal]


class AccountsSummary(BaseModel):
    """The Accounts page's numbers: net worth, and each type's total, in Monarch's order of types.

    Accounts set to "Exclude account balance" count in neither.
    """

    net_worth: list[CurrencyTotal]
    # Only types the user has accounts of
    types: list[TypeTotal]


class SubtypeRead(BaseModel):
    key: str
    label: str


class AccountTypeRead(BaseModel):
    """One kind of account and its subtypes, in Monarch's order (the first subtype is the default)."""

    type: WalletType
    label: str
    account_class: AccountClass
    subtypes: list[SubtypeRead]
