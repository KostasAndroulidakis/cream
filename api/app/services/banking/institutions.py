"""What CREAM knows about banks beyond Enable Banking's list. Pure module: no database, no network.

Enable Banking gives each bank's name and logo, but not its website or how popular it is (Plaid gives
both to Monarch). This catalog adds them for the banks we know; any other bank still shows, just without.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Institution:
    key: str
    website: str
    # Names Enable Banking may give it, compared loosely (see `_normalize`)
    names: tuple[str, ...]


INSTITUTIONS: tuple[Institution, ...] = (
    Institution("nbg", "https://www.nbg.gr", ("National Bank of Greece", "NBG", "Ethniki Trapeza")),
    Institution("piraeus", "https://www.piraeusbank.gr", ("Piraeus Bank", "Piraeus")),
    Institution("alpha", "https://www.alpha.gr", ("Alpha Bank",)),
    Institution("eurobank", "https://www.eurobank.gr", ("Eurobank", "Eurobank Ergasias")),
    Institution("attica", "https://www.atticabank.gr", ("Attica Bank",)),
    Institution("optima", "https://www.optimabank.gr", ("Optima Bank",)),
    Institution("revolut", "https://www.revolut.com", ("Revolut",)),
    Institution("n26", "https://n26.com", ("N26",)),
    Institution("wise", "https://wise.com", ("Wise",)),
    Institution("paypal", "https://www.paypal.com", ("PayPal",)),
    Institution("trade_republic", "https://traderepublic.com", ("Trade Republic",)),
    Institution("viva", "https://www.vivawallet.com", ("Viva Wallet", "Vivabank", "Viva")),
)

# Per country, the most used first. Greece: Enable Banking's own order of significance for Greek banks
# (enablebanking.com/docs/markets/gr), then the neobanks people there use most.
POPULAR: dict[str, tuple[str, ...]] = {
    "GR": ("nbg", "piraeus", "alpha", "eurobank", "revolut", "n26"),
}

# Words that differ between how a bank is written and how Enable Banking lists it ("Piraeus Bank S.A.")
_NOISE = {"bank", "the", "s", "a", "sa", "ae", "ag", "plc", "ltd", "gmbh", "uab", "se", "nv"}


def _normalize(name: str) -> str:
    words = re.sub(r"[^0-9a-z]+", " ", name.lower()).split()
    return " ".join(word for word in words if word not in _NOISE)


_BY_NAME = {_normalize(name): institution for institution in INSTITUTIONS for name in institution.names}


def find_institution(name: str) -> Institution | None:
    """The catalog's entry for a bank as Enable Banking names it, if we know it."""
    return _BY_NAME.get(_normalize(name))


def popularity(country: str, name: str) -> int | None:
    """The bank's place among the country's most popular (0 = first), or None if it isn't one."""
    institution = find_institution(name)
    ranking = POPULAR.get(country, ())
    return ranking.index(institution.key) if institution and institution.key in ranking else None
