from datetime import datetime

from pydantic import BaseModel, Field

from app.models.bank import ConnectionStatus

COUNTRY_CODE_PATTERN = r"^[A-Z]{2}$"


class AspspRead(BaseModel):
    """A bank (ASPSP = Account Servicing Payment Service Provider) available for connection."""

    name: str
    country: str
    logo: str | None = None


class ConnectionStart(BaseModel):
    aspsp_name: str = Field(..., min_length=1, max_length=255)
    country: str = Field(..., pattern=COUNTRY_CODE_PATTERN)


class ConnectionStartResponse(BaseModel):
    # Bank login page to send the user to
    url: str


class ConnectionComplete(BaseModel):
    state: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)


class BankAccountRead(BaseModel):
    id: int
    name: str
    currency: str
    iban_last4: str | None
    wallet_id: int | None
    last_synced_at: datetime | None

    model_config = {"from_attributes": True}


class BankConnectionRead(BaseModel):
    id: int
    aspsp_name: str
    aspsp_country: str
    status: ConnectionStatus
    valid_until: datetime | None
    accounts: list[BankAccountRead]

    model_config = {"from_attributes": True}


class LinkAccountRequest(BaseModel):
    # Existing wallet to link; omit (null) to create a new wallet for this account
    wallet_id: int | None = None


class SyncResultRead(BaseModel):
    bank_account_id: int
    imported: int
    error: str | None

    model_config = {"from_attributes": True}
