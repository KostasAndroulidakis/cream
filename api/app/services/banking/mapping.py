"""Turn provider JSON into CREAM values. Pure functions: no database, no network."""

import hashlib
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Any

Json = dict[str, Any]

BOOKED_STATUS = "BOOK"
CREDIT_INDICATOR = "CRDT"
# Preferred balance types, most authoritative first (ISO 20022 codes)
BALANCE_TYPE_PRIORITY = ("CLBD", "ITBD", "XPCD", "ITAV", "CLAV")
COUNTERPARTY_MAX = 255
MCC_LENGTH = 4
IBAN_SUFFIX_LENGTH = 4


@dataclass(frozen=True)
class ImportedTransaction:
    # Identity before repeats are numbered; see assign_external_ids
    base_key: str
    amount: Decimal
    occurred_at: datetime
    description: str | None
    counterparty: str | None
    merchant_category_code: str | None
    # As the bank reports it; a multi-currency account (PayPal) mixes several
    currency: str | None


def _signed_amount(raw: Json) -> Decimal:
    amount = abs(Decimal(raw["transaction_amount"]["amount"]))
    return amount if raw.get("credit_debit_indicator") == CREDIT_INDICATOR else -amount


def _booking_date(raw: Json) -> date:
    for field in ("booking_date", "transaction_date", "value_date"):
        if raw.get(field):
            return date.fromisoformat(raw[field])
    raise ValueError("Transaction has no date")


def _counterparty(raw: Json, amount: Decimal) -> str | None:
    # Money out goes to the creditor; money in comes from the debtor
    party = raw.get("creditor") if amount < 0 else raw.get("debtor")
    name = (party or {}).get("name")
    return name[:COUNTERPARTY_MAX] if name else None


def _description(raw: Json) -> str | None:
    lines = [line.strip() for line in raw.get("remittance_information") or [] if line and line.strip()]
    return " ".join(lines) or None


def _base_key(raw: Json, booked_on: date, amount: Decimal, description: str | None) -> str:
    """Identity of a transaction before disambiguating repeats.

    entry_reference is NOT unique in practice (banks reuse it, e.g. for every monthly salary
    from the same sender), so it is only one ingredient of a fingerprint, never the ID itself.
    """
    if raw.get("transaction_id"):
        return f"transaction_id:{raw['transaction_id']}"
    parts = (raw.get("entry_reference") or "", booked_on.isoformat(), str(amount), description or "")
    return "hash:" + hashlib.sha256("|".join(parts).encode()).hexdigest()


def parse_transaction(raw: Json) -> ImportedTransaction | None:
    """None for pending transactions: they can still change, so only booked ones are imported."""
    if raw.get("status", BOOKED_STATUS) != BOOKED_STATUS:
        return None
    amount = _signed_amount(raw)
    booked_on = _booking_date(raw)
    description = _description(raw)
    mcc = raw.get("merchant_category_code")
    return ImportedTransaction(
        base_key=_base_key(raw, booked_on, amount, description),
        amount=amount,
        # Banks report dates, not times; midday UTC stays on the same calendar day across Europe
        occurred_at=datetime.combine(booked_on, time(12), tzinfo=timezone.utc),
        description=description,
        counterparty=_counterparty(raw, amount),
        merchant_category_code=mcc if mcc and len(mcc) == MCC_LENGTH else None,
        currency=raw["transaction_amount"].get("currency"),
    )


def assign_external_ids(transactions: list[ImportedTransaction]) -> list[tuple[str, ImportedTransaction]]:
    """Give every transaction a stable ID, numbering genuine repeats (two identical coffees).

    Syncs always fetch whole days, so the same day yields the same order and the same
    numbers on every sync: re-fetched transactions get their old IDs and are skipped.
    """
    seen: dict[str, int] = {}
    result = []
    for transaction in transactions:
        occurrence = seen.get(transaction.base_key, 0) + 1
        seen[transaction.base_key] = occurrence
        suffix = "" if occurrence == 1 else f"#{occurrence}"
        result.append((transaction.base_key + suffix, transaction))
    return result


def pick_balance(balances: list[Json], currency: str) -> Decimal | None:
    """The account's current balance in a currency, preferring booked balance types.

    A multi-currency account (PayPal) reports one balance per currency; only the account's own counts.
    """
    balances = [b for b in balances if b["balance_amount"].get("currency") in (None, currency)]
    by_type = {balance.get("balance_type"): balance for balance in balances}
    for balance_type in BALANCE_TYPE_PRIORITY:
        if balance_type in by_type:
            return Decimal(by_type[balance_type]["balance_amount"]["amount"])
    return Decimal(balances[0]["balance_amount"]["amount"]) if balances else None


def account_display_name(raw: Json) -> str:
    return raw.get("details") or raw.get("product") or raw.get("name") or "Bank account"


def iban_last4(raw: Json) -> str | None:
    iban = (raw.get("account_id") or {}).get("iban")
    return iban[-IBAN_SUFFIX_LENGTH:] if iban else None
