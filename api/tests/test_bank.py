"""Bank connections and sync, with a fake Open Banking provider (no network)."""

from collections.abc import Iterator
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.config import settings
from app.main import app
from app.models import Category, CategoryType
from app.services.banking.client import BankProviderError, get_bank_client
from app.services.banking.mapping import assign_external_ids, parse_transaction, pick_balance
from app.services.banking.sync import UNCATEGORIZED_KEY

BANK_URL = "/api/v1/bank"
ACCOUNT_UID = "acc-uid-1"


class FakeBankClient:
    def __init__(self):
        self.started: list[dict] = []
        self.deleted_sessions: list[str] = []
        self.transactions: list[dict] = []
        self.balance = "1000.00"
        self.fail_transactions = False

    def list_aspsps(self, country):
        return [{"name": "Mock ASPSP", "country": country, "logo": "https://logo"}]

    def start_authorization(self, aspsp_name, country, state, valid_until, redirect_url):
        self.started.append({"aspsp": aspsp_name, "state": state, "valid_until": valid_until})
        return f"https://bank.example/login?state={state}"

    def create_session(self, code):
        return {
            "session_id": "session-1",
            "access": {"valid_until": (datetime.now(timezone.utc) + timedelta(days=180)).isoformat()},
            "accounts": [
                {"uid": ACCOUNT_UID, "details": "Current account", "currency": "EUR",
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


def _raw(tx_id, amount, indicator="DBIT", status="BOOK", **extra):
    return {
        "transaction_id": tx_id,
        "transaction_amount": {"currency": "EUR", "amount": amount},
        "credit_debit_indicator": indicator,
        "status": status,
        "booking_date": "2026-09-20",
        **extra,
    }


@pytest.fixture
def bank(client):
    fake = FakeBankClient()
    app.dependency_overrides[get_bank_client] = lambda: fake
    return fake


@pytest.fixture
def uncategorized(db_session):
    category = Category(user_id=None, name="Uncategorized", type=CategoryType.EXPENSE, key=UNCATEGORIZED_KEY)
    db_session.add(category)
    db_session.commit()
    return category


def _connect(client, headers, bank):
    response = client.post(f"{BANK_URL}/connections", json={"aspsp_name": "Mock ASPSP", "country": "FI"}, headers=headers)
    assert response.status_code == 200
    state = bank.started[-1]["state"]
    response = client.post(f"{BANK_URL}/connections/complete", json={"state": state, "code": "abc"}, headers=headers)
    assert response.status_code == 200
    return response.json()


def _connect_and_link(client, headers, bank):
    connection = _connect(client, headers, bank)
    account_id = connection["accounts"][0]["id"]
    linked = client.post(f"{BANK_URL}/accounts/{account_id}/link", json={}, headers=headers)
    assert linked.status_code == 200
    return linked.json()


def _sync(client, headers):
    response = client.post(f"{BANK_URL}/sync", headers=headers)
    assert response.status_code == 200
    return response.json()


class TestMapping:
    def test_debit_is_negative_credit_positive(self):
        assert parse_transaction(_raw("1", "12.50")).amount == Decimal("-12.50")
        assert parse_transaction(_raw("2", "12.50", indicator="CRDT")).amount == Decimal("12.50")

    def test_pending_is_skipped(self):
        assert parse_transaction(_raw("1", "5", status="PDNG")) is None

    def test_counterparty_description_and_mcc(self):
        parsed = parse_transaction(
            _raw("1", "45.30", creditor={"name": "SKLAVENITIS"}, remittance_information=["Card ", "1234"],
                 merchant_category_code="5411")
        )
        assert (parsed.counterparty, parsed.description, parsed.merchant_category_code) == ("SKLAVENITIS", "Card 1234", "5411")

    def test_missing_ids_get_a_stable_fingerprint(self):
        raw = _raw(None, "3.00", remittance_information=["Coffee"])
        assert parse_transaction(raw).base_key == parse_transaction(dict(raw)).base_key
        assert parse_transaction(raw).base_key.startswith("hash:")

    def test_reused_entry_reference_does_not_merge_transactions(self):
        # Real banks reuse entry_reference, e.g. for every monthly salary from the same sender
        salaries = [
            _raw(None, "2000", indicator="CRDT", entry_reference="SAL", booking_date=day)
            for day in ("2026-07-17", "2026-08-17")
        ]
        ids = [external_id for external_id, _ in assign_external_ids([parse_transaction(r) for r in salaries])]
        assert len(set(ids)) == 2

    def test_identical_transactions_on_same_day_are_numbered(self):
        coffees = [parse_transaction(_raw(None, "3.00", remittance_information=["Coffee"])) for _ in range(2)]
        first, second = (external_id for external_id, _ in assign_external_ids(coffees))
        assert second == f"{first}#2"

    def test_booked_balance_preferred(self):
        balances = [
            {"balance_type": "ITAV", "balance_amount": {"amount": "90"}},
            {"balance_type": "CLBD", "balance_amount": {"amount": "100"}},
        ]
        assert pick_balance(balances) == Decimal("100")


class TestConnections:
    def test_list_banks(self, client, auth_headers, bank):
        response = client.get(f"{BANK_URL}/aspsps", params={"country": "GR"}, headers=auth_headers)

        assert response.json() == [{"name": "Mock ASPSP", "country": "GR", "logo": "https://logo"}]

    def test_connect_stores_accounts_without_full_iban(self, client, auth_headers, bank):
        connection = _connect(client, auth_headers, bank)

        assert connection["status"] == "active"
        assert connection["accounts"][0]["iban_last4"] == "0695"
        assert connection["accounts"][0]["wallet_id"] is None

    def test_state_is_single_use(self, client, auth_headers, bank):
        _connect(client, auth_headers, bank)
        state = bank.started[-1]["state"]

        response = client.post(f"{BANK_URL}/connections/complete", json={"state": state, "code": "x"}, headers=auth_headers)

        assert response.status_code == 400

    def test_state_of_another_user_rejected(self, client, auth_headers, second_auth_headers, bank):
        client.post(f"{BANK_URL}/connections", json={"aspsp_name": "Mock ASPSP", "country": "FI"}, headers=auth_headers)
        state = bank.started[-1]["state"]

        response = client.post(
            f"{BANK_URL}/connections/complete", json={"state": state, "code": "x"}, headers=second_auth_headers
        )

        assert response.status_code == 400

    def test_pending_connections_are_not_listed(self, client, auth_headers, bank):
        client.post(f"{BANK_URL}/connections", json={"aspsp_name": "Mock ASPSP", "country": "FI"}, headers=auth_headers)

        assert client.get(f"{BANK_URL}/connections", headers=auth_headers).json() == []

    def test_link_creates_wallet_in_account_currency(self, client, auth_headers, bank):
        linked = _connect_and_link(client, auth_headers, bank)
        wallets = client.get("/api/v1/wallets", headers=auth_headers).json()

        assert [w["id"] for w in wallets] == [linked["wallet_id"]]
        assert wallets[0]["currency"] == "EUR" and wallets[0]["type"] == "bank"

    def test_cannot_link_to_another_users_wallet(self, client, auth_headers, second_auth_headers, bank):
        other_wallet = client.post("/api/v1/wallets", json={"name": "Theirs"}, headers=second_auth_headers).json()
        account_id = _connect(client, auth_headers, bank)["accounts"][0]["id"]

        response = client.post(
            f"{BANK_URL}/accounts/{account_id}/link", json={"wallet_id": other_wallet["id"]}, headers=auth_headers
        )

        assert response.status_code == 403

    def test_disconnect_keeps_wallet_and_revokes_session(self, client, auth_headers, bank, uncategorized):
        linked = _connect_and_link(client, auth_headers, bank)
        connection_id = client.get(f"{BANK_URL}/connections", headers=auth_headers).json()[0]["id"]

        response = client.delete(f"{BANK_URL}/connections/{connection_id}", headers=auth_headers)

        assert response.status_code == 204
        assert bank.deleted_sessions == ["session-1"]
        assert client.get(f"/api/v1/wallets/{linked['wallet_id']}", headers=auth_headers).status_code == 200

    def test_not_configured_returns_503(self, client, auth_headers, monkeypatch):
        # Independent of the developer's .env: simulate bank sync not being set up
        monkeypatch.setattr(settings, "enablebanking_app_id", None)

        response = client.get(f"{BANK_URL}/aspsps", params={"country": "GR"}, headers=auth_headers)

        assert response.status_code == 503


class TestSync:
    def test_first_sync_imports_booked_and_matches_bank_balance(self, client, auth_headers, bank, uncategorized):
        linked = _connect_and_link(client, auth_headers, bank)
        bank.transactions = [_raw("t1", "40.00"), _raw("t2", "500.00", indicator="CRDT"), _raw("t3", "9", status="PDNG")]

        results = _sync(client, auth_headers)

        assert results == [{"bank_account_id": linked["id"], "imported": 2, "error": None}]
        wallet = client.get(f"/api/v1/wallets/{linked['wallet_id']}", headers=auth_headers).json()
        assert Decimal(wallet["balance"]) == Decimal("1000.00")
        transactions = client.get("/api/v1/transactions", headers=auth_headers).json()
        assert all(t["is_imported"] and t["category_id"] == uncategorized.id for t in transactions)

    def test_second_sync_skips_duplicates_and_keeps_balance_moving(self, client, auth_headers, bank, uncategorized):
        linked = _connect_and_link(client, auth_headers, bank)
        bank.transactions = [_raw("t1", "40.00")]
        _sync(client, auth_headers)
        bank.transactions = [_raw("t1", "40.00"), _raw("t2", "10.00")]

        results = _sync(client, auth_headers)

        assert results[0]["imported"] == 1
        wallet = client.get(f"/api/v1/wallets/{linked['wallet_id']}", headers=auth_headers).json()
        assert Decimal(wallet["balance"]) == Decimal("990.00")

    def test_repeated_identical_transactions_all_imported_once(self, client, auth_headers, bank, uncategorized):
        _connect_and_link(client, auth_headers, bank)
        coffee = _raw(None, "3.00", entry_reference="REF", remittance_information=["Coffee"])
        bank.transactions = [coffee, dict(coffee), _raw(None, "3.00", entry_reference="REF", booking_date="2026-09-21")]

        assert _sync(client, auth_headers)[0]["imported"] == 3
        assert _sync(client, auth_headers)[0]["imported"] == 0

    def test_provider_failure_is_reported_not_raised(self, client, auth_headers, bank, uncategorized):
        _connect_and_link(client, auth_headers, bank)
        bank.fail_transactions = True

        results = _sync(client, auth_headers)

        assert results[0]["imported"] == 0 and results[0]["error"]

    def test_expired_consent_marks_connection(self, client, auth_headers, bank, uncategorized, db_session):
        from app.models import BankConnection

        _connect_and_link(client, auth_headers, bank)
        connection = db_session.query(BankConnection).one()
        connection.valid_until = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()

        results = _sync(client, auth_headers)

        assert "expired" in results[0]["error"]
        assert client.get(f"{BANK_URL}/connections", headers=auth_headers).json()[0]["status"] == "expired"

    def test_unlinked_accounts_are_not_synced(self, client, auth_headers, bank, uncategorized):
        _connect(client, auth_headers, bank)

        assert _sync(client, auth_headers) == []
