"""Which currencies CREAM accepts. Pure module.

EUR only for now: like Monarch, CREAM keeps to one currency, so totals and net worth are plain sums.
To open another currency, add its code here; the rest of the API reads this set.
"""

DEFAULT_CURRENCY = "EUR"
SUPPORTED_CURRENCIES = frozenset({DEFAULT_CURRENCY})
# ISO 4217 "no currency": what banks report for an account holding several currencies (PayPal)
NO_CURRENCY = "XXX"


class UnsupportedCurrencyError(ValueError):
    def __init__(self, currency: str):
        super().__init__(f"CREAM supports {', '.join(sorted(SUPPORTED_CURRENCIES))} accounts only for now, not {currency}")


def is_supported(currency: str) -> bool:
    return currency in SUPPORTED_CURRENCIES


def bank_account_currency(code: str | None) -> str:
    """The currency CREAM keeps a bank account in: its own, or the default for a multi-currency or unset one.

    A multi-currency account is followed in the default currency only: sync imports that currency's
    transactions and balance, and leaves the others out (see banking/sync.py).
    """
    return DEFAULT_CURRENCY if not code or code == NO_CURRENCY else code


def ensure_supported(currency: str) -> str:
    if not is_supported(currency):
        raise UnsupportedCurrencyError(currency)
    return currency
