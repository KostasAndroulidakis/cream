"""Merchant identity: which transactions count as 'the same merchant'. Pure functions."""

MERCHANT_MAX = 255


def tidy_merchant_name(text: str | None) -> str | None:
    """A merchant name with its spacing tidied and cut to fit; None when there is nothing left."""
    name = " ".join((text or "").split())
    return name[:MERCHANT_MAX] or None


def merchant_name_key(name: str) -> str:
    """Case-insensitive identity of a tidied name: "SKLAVENITIS ATHENS" matches "Sklavenitis Athens"."""
    return name.casefold()


def merchant_name(counterparty: str | None, description: str | None) -> str | None:
    """The merchant as the bank wrote it (counterparty, else the transaction text), tidied for display."""
    return tidy_merchant_name(counterparty or description)


def merchant_key(counterparty: str | None, description: str | None) -> str | None:
    """Case- and spacing-insensitive identity of the bank's merchant."""
    name = merchant_name(counterparty, description)
    return merchant_name_key(name) if name else None
