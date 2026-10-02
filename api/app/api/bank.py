from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.bank import (
    COUNTRY_CODE_PATTERN,
    AspspRead,
    BankAccountRead,
    BankConnectionRead,
    ConnectionComplete,
    ConnectionStart,
    ConnectionStartResponse,
    LinkAccountRequest,
    SyncResultRead,
)
from app.services.auth import get_current_user_id
from app.services.banking import connections as bank_connections
from app.services.banking.client import BankClient, get_bank_client
from app.services.banking.sync import sync_user_accounts

router = APIRouter()


@router.get("/aspsps", response_model=list[AspspRead])
def list_banks(
    country: str = Query(..., pattern=COUNTRY_CODE_PATTERN),
    _user_id: int = Depends(get_current_user_id),
    client: BankClient = Depends(get_bank_client),
):
    """Banks available for connection in a country."""
    return [AspspRead(name=a["name"], country=a["country"], logo=a.get("logo")) for a in client.list_aspsps(country)]


@router.post("/connections", response_model=ConnectionStartResponse)
def start_connection(
    request: ConnectionStart,
    user_id: int = Depends(get_current_user_id),
    client: BankClient = Depends(get_bank_client),
    db: Session = Depends(get_db),
):
    """Start connecting a bank; the client then sends the user to the returned URL."""
    url = bank_connections.start_connection(user_id, request.aspsp_name, request.country, client, db)
    return ConnectionStartResponse(url=url)


@router.post("/connections/complete", response_model=BankConnectionRead)
def complete_connection(
    request: ConnectionComplete,
    user_id: int = Depends(get_current_user_id),
    client: BankClient = Depends(get_bank_client),
    db: Session = Depends(get_db),
):
    """Finish the connection with the code and state the bank sent back."""
    return bank_connections.complete_connection(user_id, request.state, request.code, client, db)


@router.get("/connections", response_model=list[BankConnectionRead])
def list_connections(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return bank_connections.list_connections(user_id, db)


@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(
    connection_id: int,
    user_id: int = Depends(get_current_user_id),
    client: BankClient = Depends(get_bank_client),
    db: Session = Depends(get_db),
):
    """Disconnect a bank. Wallets and imported transactions are kept."""
    connection = bank_connections.get_connection(connection_id, user_id, db)
    bank_connections.delete_connection(connection, client, db)


@router.post("/accounts/{account_id}/link", response_model=BankAccountRead)
def link_account(
    account_id: int,
    request: LinkAccountRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Link a bank account to a wallet (or to a new wallet when wallet_id is null)."""
    account = bank_connections.get_bank_account(account_id, user_id, db)
    return bank_connections.link_account(account, request.wallet_id, user_id, db)


@router.post("/sync", response_model=list[SyncResultRead])
def sync(
    user_id: int = Depends(get_current_user_id),
    client: BankClient = Depends(get_bank_client),
    db: Session = Depends(get_db),
):
    """Import new transactions from every linked bank account."""
    return sync_user_accounts(user_id, client, db)
