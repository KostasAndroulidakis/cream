"""Which currencies CREAM accepts. Pure module.

EUR only for now: like Monarch, CREAM keeps to one currency, so totals and net worth are plain sums.
To open another currency, add its code here; the rest of the API reads this set.
"""

DEFAULT_CURRENCY = "EUR"
SUPPORTED_CURRENCIES = frozenset({DEFAULT_CURRENCY})


class UnsupportedCurrencyError(ValueError):
    def __init__(self, currency: str):
        super().__init__(f"CREAM supports {', '.join(sorted(SUPPORTED_CURRENCIES))} accounts only for now, not {currency}")


def is_supported(currency: str) -> bool:
    return currency in SUPPORTED_CURRENCIES


def ensure_supported(currency: str) -> str:
    if not is_supported(currency):
        raise UnsupportedCurrencyError(currency)
    return currency
