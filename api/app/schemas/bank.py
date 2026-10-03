from datetime import datetime

from pydantic import BaseModel, Field, computed_field

from app.models.bank import ConnectionStatus
from app.services.currencies import is_supported

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
    # When CREAM first saw the account
    created_at: datetime

    @computed_field
    @property
    def can_link(self) -> bool:
        """Whether CREAM can link this account (its currency is one CREAM supports)."""
        return is_supported(self.currency)

    model_config = {"from_attributes": True}


class BankConnectionRead(BaseModel):
    id: int
    aspsp_name: str
    aspsp_country: str
    status: ConnectionStatus
    valid_until: datetime | None
    # When the bank was connected
    created_at: datetime
    accounts: list[BankAccountRead]

    model_config = {"from_attributes": True}


class LinkAccountRequest(BaseModel):
    # Existing wallet to link; omit (null) to create a new wallet for this account
    wallet_id: int | None = None


class SyncResultRead(BaseModel):
    bank_account_id: int
    imported: int
    # New or previously uncategorized transactions that a rule or the MCC categorized
    categorized: int
    error: str | None

    model_config = {"from_attributes": True}
