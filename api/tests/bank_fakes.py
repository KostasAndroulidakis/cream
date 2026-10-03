"""A fake Open Banking provider and helpers to connect, link and sync through the API."""

from collections.abc import Iterator
from datetime import date, datetime, timedelta, timezone

from app.services.banking.client import BankProviderError

BANK_URL = "/api/v1/bank"
ACCOUNT_UID = "acc-uid-1"


class FakeBankClient:
    def __init__(self):
        self.started: list[dict] = []
        self.deleted_sessions: list[str] = []
        self.transactions: list[dict] = []
        self.balance = "1000.00"
        self.fail_transactions = False
        # Currency of the account the bank shares
        self.accounts_currency = "EUR"
        self.aspsp_names = ["Mock ASPSP"]

    def list_aspsps(self, country):
        return [{"name": name, "country": country, "logo": "https://logo"} for name in self.aspsp_names]

    def start_authorization(self, aspsp_name, country, state, valid_until, redirect_url):
        self.started.append({"aspsp": aspsp_name, "state": state, "valid_until": valid_until})
        return f"https://bank.example/login?state={state}"

    def create_session(self, code):
        return {
            "session_id": "session-1",
            "access": {"valid_until": (datetime.now(timezone.utc) + timedelta(days=180)).isoformat()},
            "accounts": [
                {"uid": ACCOUNT_UID, "details": "Current account", "currency": self.accounts_currency,
                 "account_id": {"iban": "GR1601101250000000012300695"}},
            ],
        }

    def delete_session(self, session_id):
        self.deleted_sessions.append(session_id)

    def get_balances(self, account_uid):
        return [{"balance_type": "CLBD", "balance_amount": {"currency": "EUR", "amount": self.balance}}]

    def iter_transactions(self, account_uid, date_from: date) -> Iterator[dict]:
        if self.fail_transactions:
            raise BankProviderError()
        yield from self.transactions


def raw_transaction(tx_id, amount, indicator="DBIT", status="BOOK", **extra):
    return {
        "transaction_id": tx_id,
        "transaction_amount": {"currency": "EUR", "amount": amount},
        "credit_debit_indicator": indicator,
        "status": status,
        "booking_date": "2026-09-20",
        **extra,
    }


def connect(client, headers, bank):
    response = client.post(f"{BANK_URL}/connections", json={"aspsp_name": "Mock ASPSP", "country": "FI"}, headers=headers)
    assert response.status_code == 200
    state = bank.started[-1]["state"]
    response = client.post(f"{BANK_URL}/connections/complete", json={"state": state, "code": "abc"}, headers=headers)
    assert response.status_code == 200
    return response.json()


def connect_and_link(client, headers, bank):
    connection = connect(client, headers, bank)
    account_id = connection["accounts"][0]["id"]
    linked = client.post(f"{BANK_URL}/accounts/{account_id}/link", json={}, headers=headers)
    assert linked.status_code == 200
    return linked.json()


def sync(client, headers):
    response = client.post(f"{BANK_URL}/sync", headers=headers)
    assert response.status_code == 200
    return response.json()
