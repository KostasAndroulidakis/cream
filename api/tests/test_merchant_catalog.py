"""The catalog of known merchants, against spellings seen in real bank data."""

import pytest

from app.services.merchant_catalog import find_known_merchant, known_merchant_name


@pytest.mark.parametrize(
    ("bank_text", "name"),
    [
        ("Efood", "efood"),
        ("efood*019cc465dd377d69934*Irakleio Atti", "efood"),
        ("Refund from efood", "efood"),
        ("Delivery Hero Payments Single Member Societe Anonyme", "efood"),
        ("Wolt*Wolt*Athens", "Wolt"),
        ("Wolt License Services Oy", "Wolt"),
        ("Apple.com", "Apple"),
        ("Apple Services", "Apple"),
        ("Paypal *itunesappst Ap", "Apple"),
        ("www.skroutz.gr*Nea Ionia", "Skroutz"),
        ("Sklavenitis_abelokipoi", "Sklavenitis"),
        ("Sklavenitis Alexa.", "Sklavenitis"),
        ("Domino's Pizza", "Domino's Pizza"),
        ("Dei Bill Payment Epos", "ΔΕΗ"),
        ("Oasa Eticket Pos", "ΟΑΣΑ"),
        ("Claude.ai Subscription", "Anthropic"),
        ("Openai *chatgpt Subscr", "OpenAI"),
        ("Housemarket A.e.", "IKEA"),
        ("Paypal *paypal", "PayPal"),
        ("PAYPAL EUROPE S.A.R.L. ET CIE S.C.A", "PayPal"),
        ("Cash at Alpha Bank", "Alpha Bank"),
        ("Cash at Piraeus Bank,s1d15582", "Piraeus Bank"),
    ],
)
def test_bank_spellings_find_the_merchant(bank_text, name):
    known = find_known_merchant(bank_text)
    assert known is not None and known.name == name


@pytest.mark.parametrize(
    "bank_text",
    [
        # A Revolut top-up paid with Apple Pay is not a purchase from Apple
        "Apple Pay Top-Up by *0211",
        "Antonios Androulidakis",
        "Mini_kiosk_ampelokhpoi",
        "Pet 4 U",
        "Canvas Coffee",
    ],
)
def test_unknown_text_matches_nothing(bank_text):
    assert find_known_merchant(bank_text) is None


def test_bank_websites_come_from_the_banks_catalog():
    assert find_known_merchant("Cash at Alpha Bank").website == "alpha.gr"


@pytest.mark.parametrize(
    ("bank_text", "name"),
    [
        ("efood*019cc465dd377d69934*Irakleio Atti", "efood"),
        ("Wolt*Wolt*Athens", "Wolt"),
        ("Paypal *itunesappst Ap", "Apple"),
        # Go-betweens: the logo fits, but the text names an ATM or the shop paid through them
        ("Cash at Alpha Bank", None),
        ("Paypal *spotify", None),
        ("Paypal *onlinedeliv", None),
        ("Paypal *paypal", "PayPal"),
        ("PAYPAL EUROPE S.A.R.L. ET CIE S.C.A", "PayPal"),
        ("PAYPAL (EUROPE) S.A R.L. ET CIE, S.C.A.", "PayPal"),
        ("Paypal *canvaptylim", "Canva"),
        ("Mini_kiosk_ampelokhpoi", None),
    ],
)
def test_import_names_gather_only_a_merchants_own_spellings(bank_text, name):
    assert known_merchant_name(bank_text) == name
