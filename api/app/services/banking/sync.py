"""Import booked bank transactions into linked wallets, without duplicates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import as_utc
from app.models import BankAccount, BankConnection, CategorySource, ConnectionStatus, Transaction, UserPreferences
from app.services.banking.client import BankClient
from app.services.banking.mapping import ImportedTransaction, assign_external_ids, parse_transaction, pick_balance
from app.services.categorization.auto import AutoCategorizer
from app.services.categorization.merchants import merchant_key, merchant_name
from app.services.merchants import MerchantDirectory
from app.services.preferences import get_preferences
from app.services.review import needs_review_on_import


@dataclass
class SyncResult:
    bank_account_id: int
    imported: int = 0
    # Transactions (new, or still in Uncategorized) that a rule or the MCC put in a category
    categorized: int = 0
    error: str | None = None


@dataclass(frozen=True)
class Importer:
    """What one user's sync needs in memory: their categorization rules, merchants and preferences."""

    categorizer: AutoCategorizer
    merchants: MerchantDirectory
    preferences: UserPreferences

    @classmethod
    def for_user(cls, user_id: int, db: Session) -> Importer:
        return cls(
            AutoCategorizer.for_user(user_id, db),
            MerchantDirectory.for_user(user_id, db),
            get_preferences(user_id, db),
        )


def _new_transaction(
    wallet_id: int, external_id: str, parsed: ImportedTransaction, importer: Importer, db: Session
) -> Transaction:
    key = merchant_key(parsed.counterparty, parsed.description)
    decision = importer.categorizer.decide(key, parsed.merchant_category_code)
    return Transaction(
        wallet_id=wallet_id,
        category_id=decision.category_id,
        category_source=decision.source,
        needs_review=needs_review_on_import(importer.preferences, decision),
        amount=parsed.amount,
        occurred_at=parsed.occurred_at,
        description=parsed.description,
        counterparty=parsed.counterparty,
        merchant_category_code=parsed.merchant_category_code,
        merchant_key=key,
        merchant=importer.merchants.get_or_create(merchant_name(parsed.counterparty, parsed.description), db),
        external_id=external_id,
    )


def _sync_start_date(account: BankAccount, today: date) -> date:
    if account.last_synced_at is None:
        return today - timedelta(days=settings.bank_initial_history_days)
    return as_utc(account.last_synced_at).date() - timedelta(days=settings.bank_sync_overlap_days)


def _reconcile_initial_balance(account: BankAccount, client: BankClient, db: Session) -> None:
    """Set the wallet's starting balance so CREAM shows exactly what the bank shows.

    Only on the first sync: history before the imported window is unknown, so the
    starting balance absorbs it. Afterwards balances move only through transactions.
    """
    bank_balance = pick_balance(client.get_balances(account.uid))
    if bank_balance is None:
        return
    # "Invert account balance": the bank reports this account with the opposite sign
    if account.wallet.invert_balance:
        bank_balance = -bank_balance
    transactions_total = db.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.wallet_id == account.wallet_id)
    )
    account.wallet.initial_balance = bank_balance - Decimal(transactions_total)


def _consent_expired(connection: BankConnection, now: datetime) -> bool:
    return connection.valid_until is not None and as_utc(connection.valid_until) <= now


def sync_account(account: BankAccount, client: BankClient, importer: Importer, db: Session) -> SyncResult:
    """Import new booked transactions of one linked account, categorizing them on the way in."""
    result = SyncResult(bank_account_id=account.id)
    now = datetime.now(timezone.utc)
    connection = account.connection
    if account.wallet_id is None:
        result.error = "Not linked to an account"
        return result
    if _consent_expired(connection, now):
        connection.status = ConnectionStatus.EXPIRED
        db.commit()
        result.error = "Bank access expired. Reconnect the bank."
        return result

    is_first_sync = account.last_synced_at is None
    known_ids = set(
        db.scalars(
            select(Transaction.external_id).where(
                Transaction.wallet_id == account.wallet_id, Transaction.external_id.is_not(None)
            )
        )
    )
    try:
        raw_transactions = client.iter_transactions(account.uid, _sync_start_date(account, now.date()))
        booked = [parsed for raw in raw_transactions if (parsed := parse_transaction(raw)) is not None]
        for external_id, parsed in assign_external_ids(booked):
            if external_id in known_ids:
                continue
            transaction = _new_transaction(account.wallet_id, external_id, parsed, importer, db)
            db.add(transaction)
            result.imported += 1
            if transaction.category_source is not CategorySource.DEFAULT:
                result.categorized += 1
        db.flush()
        result.categorized += importer.categorizer.retry_uncategorized(account.wallet_id, db)
        if is_first_sync:
            _reconcile_initial_balance(account, client, db)
    except HTTPException as exc:
        # One failing bank must not lose another bank's progress: roll back only this account
        db.rollback()
        result.imported = result.categorized = 0
        result.error = str(exc.detail)
        return result

    account.last_synced_at = now
    db.commit()
    return result


def sync_user_accounts(user_id: int, client: BankClient, db: Session) -> list[SyncResult]:
    """Sync every linked account on the user's active connections."""
    accounts = (
        db.query(BankAccount)
        .join(BankConnection)
        .filter(
            BankConnection.user_id == user_id,
            BankConnection.status == ConnectionStatus.ACTIVE,
            BankAccount.wallet_id.is_not(None),
        )
        .order_by(BankAccount.id)
        .all()
    )
    if not accounts:
        return []
    importer = Importer.for_user(user_id, db)
    return [sync_account(account, client, importer, db) for account in accounts]
