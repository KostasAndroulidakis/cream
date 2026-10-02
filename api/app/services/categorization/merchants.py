"""Merchant identity: which transactions count as 'the same merchant'. Pure functions."""

MERCHANT_MAX = 255


def merchant_name(counterparty: str | None, description: str | None) -> str | None:
    """The merchant as the bank wrote it (counterparty, else the transaction text), tidied for display."""
    name = " ".join((counterparty or description or "").split())
    return name[:MERCHANT_MAX] or None


def merchant_key(counterparty: str | None, description: str | None) -> str | None:
    """Case- and spacing-insensitive identity: "SKLAVENITIS  ATHENS" matches "Sklavenitis Athens"."""
    name = merchant_name(counterparty, description)
    return name.casefold() if name else None
