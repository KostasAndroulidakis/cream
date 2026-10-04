"""Bank connections and sync, with a fake Open Banking provider (no network)."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import httpx2 as httpx
import pytest

from app.config import settings
from app.services.banking.client import _error_reason
from app.services.banking.mapping import assign_external_ids, parse_transaction, pick_balance
from tests.conftest import SIGNUP_URL
from tests.bank_fakes import BANK_URL, connect, connect_and_link, raw_transaction, sync


class TestMapping:
    def test_debit_is_negative_credit_positive(self):
        assert parse_transaction(raw_transaction("1", "12.50")).amount == Decimal("-12.50")
        assert parse_transaction(raw_transaction("2", "12.50", indicator="CRDT")).amount == Decimal("12.50")

    def test_pending_is_skipped(self):
        assert parse_transaction(raw_transaction("1", "5", status="PDNG")) is None

    def test_counterparty_description_and_mcc(self):
        parsed = parse_transaction(
            raw_transaction("1", "45.30", creditor={"name": "SKLAVENITIS"}, remittance_information=["Card ", "1234"],
                 merchant_category_code="5411")
        )
        assert (parsed.counterparty, parsed.description, parsed.merchant_category_code) == ("SKLAVENITIS", "Card 1234", "5411")

    def test_missing_ids_get_a_stable_fingerprint(self):
        raw = raw_transaction(None, "3.00", remittance_information=["Coffee"])
        assert parse_transaction(raw).base_key == parse_transaction(dict(raw)).base_key
        assert parse_transaction(raw).base_key.startswith("hash:")

    def test_reused_entry_reference_does_not_merge_transactions(self):
        # Real banks reuse entry_reference, e.g. for every monthly salary from the same sender
        salaries = [
            raw_transaction(None, "2000", indicator="CRDT", entry_reference="SAL", booking_date=day)
            for day in ("2026-07-17", "2026-08-17")
        ]
        ids = [external_id for external_id, _ in assign_external_ids([parse_transaction(r) for r in salaries])]
        assert len(set(ids)) == 2

    def test_identical_transactions_on_same_day_are_numbered(self):
        coffees = [parse_transaction(raw_transaction(None, "3.00", remittance_information=["Coffee"])) for _ in range(2)]
        first, second = (external_id for external_id, _ in assign_external_ids(coffees))
        assert second == f"{first}#2"

    def test_booked_balance_preferred(self):
        balances = [
            {"balance_type": "ITAV", "balance_amount": {"amount": "90"}},
            {"balance_type": "CLBD", "balance_amount": {"amount": "100"}},
        ]
        assert pick_balance(balances, "EUR") == Decimal("100")

    def test_balance_in_the_accounts_currency_only(self):
        # A multi-currency account (PayPal) reports one balance per currency
        balances = [
            {"balance_type": "CLBD", "balance_amount": {"currency": "USD", "amount": "70"}},
            {"balance_type": "ITAV", "balance_amount": {"currency": "EUR", "amount": "25"}},
        ]
        assert pick_balance(balances, "EUR") == Decimal("25")


class TestProviderErrors:
    def test_reason_from_the_providers_message(self):
        response = httpx.Response(422, json={"code": 422, "message": "Wrong transactions period requested"})
        assert _error_reason(response) == "Wrong transactions period requested"

    def test_no_reason_when_the_body_isnt_json(self):
        assert _error_reason(httpx.Response(502, text="Bad gateway")) is None


class TestConnections:
    def test_list_banks(self, client, auth_headers, bank):
        response = client.get(f"{BANK_URL}/aspsps", params={"country": "GR"}, headers=auth_headers)

        assert response.json() == [
            {"name": "Mock ASPSP", "country": "GR", "logo": "https://logo", "website": None, "popular": False}
        ]

    def test_popular_banks_first_in_their_order_with_websites(self, client, auth_headers, bank):
        bank.aspsp_names = [
            "Attica Bank", "Eurobank Ergasias S.A.", "Mock ASPSP", "Piraeus Bank", "National Bank of Greece",
        ]

        banks = client.get(f"{BANK_URL}/aspsps", params={"country": "GR"}, headers=auth_headers).json()

        assert [(b["name"], b["popular"]) for b in banks] == [
            ("National Bank of Greece", True), ("Piraeus Bank", True), ("Eurobank Ergasias S.A.", True),
            ("Attica Bank", False), ("Mock ASPSP", False),
        ]
        assert banks[2]["website"] == "https://www.eurobank.gr"
        assert banks[3]["website"] == "https://www.atticabank.gr"

    def test_no_popular_list_for_other_countries(self, client, auth_headers, bank):
        bank.aspsp_names = ["Revolut"]

        [revolut] = client.get(f"{BANK_URL}/aspsps", params={"country": "FI"}, headers=auth_headers).json()

        assert (revolut["popular"], revolut["website"]) == (False, "https://www.revolut.com")

    def test_connect_stores_accounts_without_full_iban(self, client, auth_headers, bank):
        connection = connect(client, auth_headers, bank)

        assert connection["status"] == "active"
        assert connection["accounts"][0]["iban_last4"] == "0695"
        assert connection["accounts"][0]["wallet_id"] is None

    def test_state_is_single_use(self, client, auth_headers, bank):
        connect(client, auth_headers, bank)
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
        linked = connect_and_link(client, auth_headers, bank)
        wallets = client.get("/api/v1/wallets", headers=auth_headers).json()

        assert [w["id"] for w in wallets] == [linked["wallet_id"]]
        assert wallets[0]["currency"] == "EUR" and (wallets[0]["type"], wallets[0]["subtype"]) == ("cash", "checking")

    def test_cannot_link_to_another_users_wallet(self, client, auth_headers, second_auth_headers, bank):
        other_wallet = client.post("/api/v1/wallets", json={"name": "Theirs"}, headers=second_auth_headers).json()
        account_id = connect(client, auth_headers, bank)["accounts"][0]["id"]

        response = client.post(
            f"{BANK_URL}/accounts/{account_id}/link", json={"wallet_id": other_wallet["id"]}, headers=auth_headers
        )

        assert response.status_code == 403

    def test_disconnect_keeps_wallet_and_revokes_session(self, client, auth_headers, bank, uncategorized):
        linked = connect_and_link(client, auth_headers, bank)
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
        linked = connect_and_link(client, auth_headers, bank)
        bank.transactions = [raw_transaction("t1", "40.00"), raw_transaction("t2", "500.00", indicator="CRDT"), raw_transaction("t3", "9", status="PDNG")]

        results = sync(client, auth_headers)

        assert results == [{"bank_account_id": linked["id"], "imported": 2, "categorized": 0, "error": None}]
        wallet = client.get(f"/api/v1/wallets/{linked['wallet_id']}", headers=auth_headers).json()
        assert Decimal(wallet["balance"]) == Decimal("1000.00")
        transactions = client.get("/api/v1/transactions", headers=auth_headers).json()
        assert all(t["is_imported"] and t["category_id"] == uncategorized.id for t in transactions)

    def test_inverted_account_takes_the_opposite_of_the_bank_balance(
        self, client, auth_headers, bank, uncategorized
    ):
        linked = connect_and_link(client, auth_headers, bank)
        client.patch(f"/api/v1/wallets/{linked['wallet_id']}", json={"invert_balance": True}, headers=auth_headers)

        sync(client, auth_headers)

        wallet = client.get(f"/api/v1/wallets/{linked['wallet_id']}", headers=auth_headers).json()
        assert Decimal(wallet["balance"]) == Decimal("-1000.00")

    def test_second_sync_skips_duplicates_and_keeps_balance_moving(self, client, auth_headers, bank, uncategorized):
        linked = connect_and_link(client, auth_headers, bank)
        bank.transactions = [raw_transaction("t1", "40.00")]
        sync(client, auth_headers)
        bank.transactions = [raw_transaction("t1", "40.00"), raw_transaction("t2", "10.00")]

        results = sync(client, auth_headers)

        assert results[0]["imported"] == 1
        wallet = client.get(f"/api/v1/wallets/{linked['wallet_id']}", headers=auth_headers).json()
        assert Decimal(wallet["balance"]) == Decimal("990.00")

    def test_repeated_identical_transactions_all_imported_once(self, client, auth_headers, bank, uncategorized):
        connect_and_link(client, auth_headers, bank)
        coffee = raw_transaction(None, "3.00", entry_reference="REF", remittance_information=["Coffee"])
        bank.transactions = [coffee, dict(coffee), raw_transaction(None, "3.00", entry_reference="REF", booking_date="2026-09-21")]

        assert sync(client, auth_headers)[0]["imported"] == 3
        assert sync(client, auth_headers)[0]["imported"] == 0

    def test_provider_failure_is_reported_not_raised(self, client, auth_headers, bank, uncategorized):
        connect_and_link(client, auth_headers, bank)
        bank.fail_transactions = True

        results = sync(client, auth_headers)

        assert results[0]["imported"] == 0 and results[0]["error"]

    def test_expired_consent_marks_connection(self, client, auth_headers, bank, uncategorized, db_session):
        from app.models import BankConnection

        connect_and_link(client, auth_headers, bank)
        connection = db_session.query(BankConnection).one()
        connection.valid_until = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()

        results = sync(client, auth_headers)

        assert "expired" in results[0]["error"]
        assert client.get(f"{BANK_URL}/connections", headers=auth_headers).json()[0]["status"] == "expired"

    def test_imported_transactions_cannot_be_deleted(self, client, auth_headers, bank, uncategorized):
        connect_and_link(client, auth_headers, bank)
        bank.transactions = [raw_transaction("t1", "40.00")]
        sync(client, auth_headers)
        [transaction] = client.get("/api/v1/transactions", headers=auth_headers).json()

        response = client.delete(f"/api/v1/transactions/{transaction['id']}", headers=auth_headers)

        assert response.status_code == 409
        assert client.get(f"/api/v1/transactions/{transaction['id']}", headers=auth_headers).status_code == 200

    @pytest.mark.parametrize("change", [{"amount": "-1.00"}, {"occurred_at": "2026-09-01T12:00:00Z"}])
    def test_bank_sets_amount_and_date_of_its_transactions(self, client, auth_headers, bank, uncategorized, change):
        connect_and_link(client, auth_headers, bank)
        bank.transactions = [raw_transaction("t1", "40.00")]
        sync(client, auth_headers)
        [transaction] = client.get("/api/v1/transactions", headers=auth_headers).json()

        response = client.patch(f"/api/v1/transactions/{transaction['id']}", json=change, headers=auth_headers)

        assert response.status_code == 422
        unchanged = client.get(f"/api/v1/transactions/{transaction['id']}", headers=auth_headers).json()
        assert (unchanged["amount"], unchanged["occurred_at"]) == (transaction["amount"], transaction["occurred_at"])

    def test_notes_of_bank_transactions_can_change(self, client, auth_headers, bank, uncategorized):
        connect_and_link(client, auth_headers, bank)
        bank.transactions = [raw_transaction("t1", "40.00")]
        sync(client, auth_headers)
        [transaction] = client.get("/api/v1/transactions", headers=auth_headers).json()

        response = client.patch(
            f"/api/v1/transactions/{transaction['id']}", json={"description": "Team lunch"}, headers=auth_headers
        )

        assert response.status_code == 200 and response.json()["description"] == "Team lunch"

    def test_unlinked_accounts_are_not_synced(self, client, auth_headers, bank, uncategorized):
        connect(client, auth_headers, bank)

        assert sync(client, auth_headers) == []


class TestSyncMerchants:
    def _merchants(self, client, headers):
        return {t["counterparty"]: t["merchant"] for t in client.get("/api/v1/transactions", headers=headers).json()}

    def test_imported_transactions_get_the_banks_merchant(self, client, auth_headers, bank, uncategorized):
        connect_and_link(client, auth_headers, bank)
        bank.transactions = [raw_transaction("t1", "4.00", creditor={"name": "  Coffee   Island "})]

        sync(client, auth_headers)

        assert self._merchants(client, auth_headers)["  Coffee   Island "]["name"] == "Coffee Island"

    def test_spellings_of_one_merchant_share_it_across_syncs(self, client, auth_headers, bank, uncategorized):
        connect_and_link(client, auth_headers, bank)
        bank.transactions = [raw_transaction("t1", "4.00", creditor={"name": "CORNER KIOSK ATHENS"})]
        sync(client, auth_headers)
        bank.transactions.append(raw_transaction("t2", "6.00", creditor={"name": "Corner Kiosk  Athens"}))

        sync(client, auth_headers)

        merchants = self._merchants(client, auth_headers)
        assert merchants["CORNER KIOSK ATHENS"] == merchants["Corner Kiosk  Athens"]
        # The first spelling seen names the merchant
        assert merchants["CORNER KIOSK ATHENS"]["name"] == "CORNER KIOSK ATHENS"

    def test_merchants_are_per_user(self, client, registered_user, second_user_data, db_session):
        from app.services.merchants import MerchantDirectory

        other_id = client.post(SIGNUP_URL, json=second_user_data).json()["id"]
        theirs = MerchantDirectory.for_user(other_id, db_session).get_or_create("Kiosk", db_session)
        db_session.commit()

        mine = MerchantDirectory.for_user(registered_user["id"], db_session).get_or_create("KIOSK", db_session)

        assert mine is not theirs and mine.user_id == registered_user["id"]

    def test_manual_transactions_have_no_merchant(self, client, auth_headers, uncategorized):
        wallet = client.post("/api/v1/wallets", json={"name": "Cash"}, headers=auth_headers).json()
        created = client.post(
            "/api/v1/transactions",
            json={"wallet_id": wallet["id"], "category_id": uncategorized.id, "amount": "-2", "occurred_at": "2026-09-20T10:00:00Z"},
            headers=auth_headers,
        ).json()

        assert created["merchant"] is None


class TestHistory:
    def test_first_sync_asks_for_the_longest_history_later_ones_only_whats_new(
        self, client, auth_headers, bank, uncategorized
    ):
        connect_and_link(client, auth_headers, bank)

        sync(client, auth_headers)
        sync(client, auth_headers)

        (first_from, first_longest), (later_from, later_longest) = bank.transaction_requests
        assert first_longest is True and later_longest is False
        assert first_from < later_from


class TestLinkCurrency:
    def _account(self, client, headers, bank, currency):
        bank.accounts_currency = currency
        return connect(client, headers, bank)["accounts"][0]

    def test_other_currency_cant_be_linked(self, client, auth_headers, bank, uncategorized):
        account = self._account(client, auth_headers, bank, "USD")

        response = client.post(f"{BANK_URL}/accounts/{account['id']}/link", json={}, headers=auth_headers)

        assert account["can_link"] is False
        assert response.status_code == 422 and "EUR" in response.json()["detail"]

    def test_eur_account_can_be_linked(self, client, auth_headers, bank, uncategorized):
        assert self._account(client, auth_headers, bank, "EUR")["can_link"] is True

    def test_multi_currency_account_is_kept_in_eur(self, client, auth_headers, bank, uncategorized):
        # PayPal reports XXX ("no currency") for an account holding several currencies
        account = self._account(client, auth_headers, bank, "XXX")

        assert (account["currency"], account["can_link"]) == ("EUR", True)

    def test_multi_currency_account_imports_its_eur_transactions_only(
        self, client, auth_headers, bank, uncategorized
    ):
        bank.accounts_currency = "XXX"
        bank.transactions = [
            raw_transaction("eur", "10.00"),
            {**raw_transaction("usd", "99.00"), "transaction_amount": {"currency": "USD", "amount": "99.00"}},
        ]
        connect_and_link(client, auth_headers, bank)

        [result] = sync(client, auth_headers)

        assert result["imported"] == 1

    def test_existing_account_must_share_the_currency(self, client, auth_headers, bank, uncategorized, db_session):
        from app.models import Wallet

        wallet = client.post("/api/v1/wallets", json={"name": "Old USD"}, headers=auth_headers).json()
        db_session.get(Wallet, wallet["id"]).currency = "USD"
        db_session.commit()
        account = self._account(client, auth_headers, bank, "EUR")

        response = client.post(
            f"{BANK_URL}/accounts/{account['id']}/link", json={"wallet_id": wallet["id"]}, headers=auth_headers
        )

        assert response.status_code == 422
