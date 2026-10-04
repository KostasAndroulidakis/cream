"""Merchants CREAM knows: their proper name, website, and how banks write them. Pure module.

Enable Banking passes on only the bank's text ("efood*019cc465dd*Irakleio Atti"); Monarch gets names
and logos from Plaid's enrichment. This catalog fills that gap for known merchants: the website gives
the logo (see services/logos.py), and the name will tidy the bank's spellings into one merchant.
Order matters: the first match wins (Apple before PayPal, for "Paypal *itunesappst").
"""

import re
from dataclasses import dataclass

from app.services.banking.institutions import find_institution


@dataclass(frozen=True)
class KnownMerchant:
    name: str
    # Domain only, e.g. "wolt.com": what logos are looked up by
    website: str
    # Matched against the bank's text, normalized (see _normalize): lower case, words split by spaces
    pattern: re.Pattern[str]


def _known(name: str, website: str, pattern: str) -> KnownMerchant:
    return KnownMerchant(name, website, re.compile(pattern))


def _bank(name: str, institution: str, pattern: str) -> KnownMerchant:
    """A bank as a merchant (e.g. "Cash at Alpha Bank"), with the website from the banks' catalog."""
    known = find_institution(institution)
    assert known is not None, institution
    return _known(name, known.website.removeprefix("https://").removeprefix("www."), pattern)


CATALOG: tuple[KnownMerchant, ...] = (
    # Delivery Hero runs efood in Greece; refunds are efood's too
    _known("efood", "e-food.gr", r"\be ?food\b|\bdelivery hero\b"),
    _known("Wolt", "wolt.com", r"\bwolt\b"),
    _known("Apple", "apple.com", r"^apple (com|services)\b|\bitunes"),
    _known("Skroutz", "skroutz.gr", r"\bskroutz\b"),
    _known("Sklavenitis", "sklavenitis.gr", r"\bsklavenitis\b"),
    _known("Domino's Pizza", "dominos.gr", r"\bdomino ?s\b"),
    _known("Vodafone", "vodafone.gr", r"\bvodafone\b"),
    _known("ΔΕΗ", "dei.gr", r"^dei\b"),
    _known("ΟΑΣΑ", "oasa.gr", r"^oasa\b"),
    _known("ΕΛΤΑ", "elta.gr", r"^elta\b"),
    _known("Bandcamp", "bandcamp.com", r"\bbandcamp\b"),
    _known("Nespresso", "nespresso.com", r"\bnespresso\b"),
    _known("Anthropic", "anthropic.com", r"\banthropic\b|\bclaude ai\b"),
    _known("OpenAI", "openai.com", r"\bopenai\b"),
    _known("GitHub", "github.com", r"\bgithub\b"),
    _known("Scribd", "scribd.com", r"\bscribd\b"),
    _known("edX", "edx.org", r"\bedx\b"),
    _known("OpenEDG", "openedg.org", r"^openedg\b"),
    _known("BOX NOW", "boxnow.gr", r"\bbox ?now\b"),
    # Housemarket runs IKEA in Greece
    _known("IKEA", "ikea.gr", r"\bikea\b|\bhousemarket\b"),
    _known("Market In", "market-in.gr", r"\bmarket in\b"),
    _known("PayPal", "paypal.com", r"^paypal\b"),
    _bank("Alpha Bank", "Alpha Bank", r"\balpha bank\b"),
    _bank("Piraeus Bank", "Piraeus Bank", r"\bpiraeus bank\b"),
    _bank("Eurobank", "Eurobank", r"\beurobank\b"),
)


def _normalize(text: str) -> str:
    return " ".join(re.sub(r"[^\w]+", " ", text.casefold()).replace("_", " ").split())


def find_known_merchant(text: str) -> KnownMerchant | None:
    """The known merchant a bank's text or a merchant's name stands for, if any."""
    normalized = _normalize(text)
    return next((known for known in CATALOG if known.pattern.search(normalized)), None)
