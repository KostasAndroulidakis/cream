"""Merchants CREAM knows: their proper name, website, and how banks write them. Pure module.

Enable Banking passes on only the bank's text ("efood*019cc465dd*Irakleio Atti"); Monarch gets names
and logos from Plaid's enrichment. This catalog fills that gap for known merchants: the website gives
the logo (see services/logos.py), and the name gathers the bank's spellings into one merchant on
import ("efood*019cc…" and "Refund from efood" are both efood).
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
    # Whether the bank's texts it matches are all this merchant, and so import as it. Not for go-betweens
    # (banks, payment services): there the logo fits, but the text names something else, e.g. an ATM
    # ("Cash at Alpha Bank") or the shop paid through PayPal ("Paypal *spotify")
    gathers_spellings: bool = True
    # The institution (its key in banking/institutions.py) holding the account the money moves to or
    # from, when the user can link that account too (PayPal). Not for an ATM: there the money leaves as cash
    account_institution: str | None = None


def _known(name: str, website: str, pattern: str, *, gathers_spellings: bool = True) -> KnownMerchant:
    return KnownMerchant(name, website, re.compile(pattern), gathers_spellings)


def _institution(
    name: str, institution: str, pattern: str, *, gathers_spellings: bool = False, holds_the_money: bool = False
) -> KnownMerchant:
    """An institution as a merchant, with the website from the banks' catalog.

    `holds_the_money`: the money moves to or from the user's account there (PayPal), rather than passing
    through it (an ATM: "Cash at Alpha Bank").
    """
    known = find_institution(institution)
    assert known is not None, institution
    website = known.website.removeprefix("https://").removeprefix("www.")
    account_institution = known.key if holds_the_money else None
    return KnownMerchant(name, website, re.compile(pattern), gathers_spellings, account_institution)


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
    # Canva Pty Ltd, often cut short ("canvaptylim"); not every "canvas"
    _known("Canva", "canva.com", r"\bcanva(\b|pty)"),
    # PayPal itself (the company, or "Paypal *paypal"): money moved to or from the PayPal account
    _institution("PayPal", "PayPal", r"^paypal (europe\b|paypal$)", gathers_spellings=True, holds_the_money=True),
    # Any other "Paypal *…" is a shop paid through PayPal: it lends only the logo
    _institution("PayPal", "PayPal", r"^paypal\b", holds_the_money=True),
    _institution("Alpha Bank", "Alpha Bank", r"\balpha bank\b"),
    _institution("Piraeus Bank", "Piraeus Bank", r"\bpiraeus bank\b"),
    _institution("Eurobank", "Eurobank", r"\beurobank\b"),
)


def _normalize(text: str) -> str:
    return " ".join(re.sub(r"[^\w]+", " ", text.casefold()).replace("_", " ").split())


def find_known_merchant(text: str) -> KnownMerchant | None:
    """The known merchant a bank's text or a merchant's name stands for, if any."""
    normalized = _normalize(text)
    return next((known for known in CATALOG if known.pattern.search(normalized)), None)


def known_merchant_name(bank_text: str) -> str | None:
    """The proper name to import the bank's text as, when it's one of a known merchant's spellings."""
    known = find_known_merchant(bank_text)
    return known.name if known is not None and known.gathers_spellings else None


def account_institution(bank_text: str) -> str | None:
    """The institution whose account (of the user's) the money moves to or from, e.g. "paypal" for
    "Paypal *spotify"; None when the text names a shop, or an ATM the money leaves through as cash.

    Looks past the first match: "Paypal *canvaptylim" is Canva as a merchant, yet paid from PayPal.
    """
    normalized = _normalize(bank_text)
    return next(
        (
            known.account_institution
            for known in CATALOG
            if known.account_institution is not None and known.pattern.search(normalized)
        ),
        None,
    )
