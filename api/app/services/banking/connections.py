"""Connecting banks: start the bank login, finish it, and link accounts to wallets."""

import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models import BankAccount, BankConnection, ConnectionStatus, Wallet, WalletType
from app.services.account_types import resolve_subtype
from app.services.currencies import UnsupportedCurrencyError, bank_account_currency, ensure_supported
from app.services.authorization import NotFoundError, get_wallet
from app.services.banking.client import BankClient
from app.services.banking.mapping import account_display_name, iban_last4

logger = logging.getLogger(__name__)

STATE_BYTES = 32
# What a linked bank account is when CREAM creates an account for it
BANK_ACCOUNT_SUBTYPE = "checking"


class CurrencyMismatchError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Link the bank account to an account in the same currency",
        )


class InvalidAuthorizationError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="This bank login link is invalid or was already used")


class WalletAlreadyLinkedError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="This account is already linked to a bank account")


def list_connections(user_id: int, db: Session) -> list[BankConnection]:
    return (
        db.query(BankConnection)
        .filter(BankConnection.user_id == user_id, BankConnection.status != ConnectionStatus.PENDING)
        .order_by(BankConnection.id)
        .all()
    )


def get_connection(connection_id: int, user_id: int, db: Session) -> BankConnection:
    connection = db.get(BankConnection, connection_id)
    if connection is None or connection.user_id != user_id:
        raise NotFoundError("Bank connection")
    return connection


def get_bank_account(account_id: int, user_id: int, db: Session) -> BankAccount:
    account = db.get(BankAccount, account_id)
    if account is None or account.connection.user_id != user_id:
        raise NotFoundError("Bank account")
    return account


def start_connection(user_id: int, aspsp_name: str, country: str, client: BankClient, db: Session) -> str:
    """Create a pending connection and return the bank login URL to send the user to."""
    state = secrets.token_urlsafe(STATE_BYTES)
    valid_until = datetime.now(timezone.utc) + timedelta(days=settings.bank_consent_days)
    url = client.start_authorization(aspsp_name, country, state, valid_until, settings.enablebanking_redirect_url)
    db.add(
        BankConnection(
            user_id=user_id,
            aspsp_name=aspsp_name,
            aspsp_country=country,
            status=ConnectionStatus.PENDING,
            auth_state=state,
        )
    )
    db.commit()
    return url


def complete_connection(user_id: int, state: str, code: str, client: BankClient, db: Session) -> BankConnection:
    """Exchange the code from the bank redirect for a session and store the shared accounts."""
    connection = (
        db.query(BankConnection)
        .filter(
            BankConnection.auth_state == state,
            BankConnection.user_id == user_id,
            BankConnection.status == ConnectionStatus.PENDING,
        )
        .first()
    )
    if connection is None:
        raise InvalidAuthorizationError()

    session = client.create_session(code)
    # Some banks authorize without sharing any account (seen with PayPal): worth knowing when it happens
    if not session.get("accounts"):
        logger.warning(
            "Enable Banking session for %s (%s) shared no accounts: %s",
            connection.aspsp_name,
            connection.aspsp_country,
            {key: value for key, value in session.items() if key != "session_id"},
        )
    connection.session_id = session["session_id"]
    connection.valid_until = datetime.fromisoformat(session["access"]["valid_until"])
    connection.status = ConnectionStatus.ACTIVE
    connection.auth_state = None  # single use
    for raw in session.get("accounts", []):
        connection.accounts.append(
            BankAccount(
                uid=raw["uid"],
                name=account_display_name(raw),
                currency=bank_account_currency(raw.get("currency")),
                iban_last4=iban_last4(raw),
            )
        )
    db.commit()
    db.refresh(connection)
    return connection


def link_account(account: BankAccount, wallet_id: int | None, user_id: int, db: Session) -> BankAccount:
    """Link to an existing wallet in the same currency, or create one for this account when wallet_id is None."""
    try:
        ensure_supported(account.currency)
    except UnsupportedCurrencyError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error
    if wallet_id is None:
        wallet = Wallet(
            user_id=user_id,
            name=f"{account.connection.aspsp_name} {account.name}".strip(),
            # A bank account starts as checking; the user can change it
            type=WalletType.CASH,
            subtype=resolve_subtype(WalletType.CASH, BANK_ACCOUNT_SUBTYPE),
            currency=account.currency,
        )
        db.add(wallet)
        db.flush()
    else:
        wallet = get_wallet(wallet_id, user_id, db)
        if wallet.currency != account.currency:
            raise CurrencyMismatchError()
        if db.query(BankAccount).filter(BankAccount.wallet_id == wallet.id, BankAccount.id != account.id).first():
            raise WalletAlreadyLinkedError()
    account.wallet_id = wallet.id
    db.commit()
    db.refresh(account)
    return account


def delete_connection(connection: BankConnection, client: BankClient, db: Session) -> None:
    """Revoke the consent at the provider (best effort) and forget the connection.

    Wallets and already-imported transactions stay: they are the user's records now.
    """
    if connection.session_id:
        try:
            client.delete_session(connection.session_id)
        except HTTPException:
            pass  # the consent expires on its own; never block the user from disconnecting
    db.delete(connection)
    db.commit()
