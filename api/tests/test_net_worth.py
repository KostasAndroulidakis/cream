"""Net worth over time, worked out from the transactions (GET /wallets/net-worth)."""

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from app.services.net_worth import NetWorthRange, range_start

WALLETS_URL = "/api/v1/wallets"
NET_WORTH_URL = f"{WALLETS_URL}/net-worth"
DAY = timedelta(days=1)


def _today_utc() -> date:
    return datetime.now(timezone.utc).date()


@pytest.fixture
def category(client, auth_headers):
    return client.post("/api/v1/categories", json={"name": "Misc", "type": "expense"}, headers=auth_headers).json()


def _wallet(client, headers, **fields):
    return client.post(WALLETS_URL, json={"name": "Account", **fields}, headers=headers).json()


def _transaction(client, headers, wallet_id, category_id, amount, when: datetime):
    response = client.post(
        "/api/v1/transactions",
        json={"wallet_id": wallet_id, "category_id": category_id, "amount": amount, "occurred_at": when.isoformat()},
        headers=headers,
    )
    assert response.status_code == 201


def _noon(day: date) -> datetime:
    return datetime.combine(day, time(12), tzinfo=timezone.utc)


def _points(client, headers, period="1M"):
    [series] = client.get(NET_WORTH_URL, params={"range": period}, headers=headers).json()["series"]
    return {point["date"]: point["balance"] for point in series["points"]}


class TestRangeStart:
    @pytest.mark.parametrize(
        ("period", "today", "expected"),
        [
            ("1M", date(2026, 10, 3), date(2026, 9, 3)),
            ("1M", date(2026, 3, 31), date(2026, 2, 28)),
            ("3M", date(2026, 5, 31), date(2026, 2, 28)),
            ("6M", date(2026, 1, 15), date(2025, 7, 15)),
            ("1Y", date(2024, 2, 29), date(2023, 2, 28)),
            ("YTD", date(2026, 10, 3), date(2026, 1, 1)),
        ],
    )
    def test_months_back_and_year_to_date(self, period, today, expected):
        assert range_start(NetWorthRange(period), today, None) == expected

    def test_all_time_starts_at_the_first_transaction(self):
        assert range_start(NetWorthRange.ALL_TIME, date(2026, 10, 3), date(2025, 4, 1)) == date(2025, 4, 1)
        assert range_start(NetWorthRange.ALL_TIME, date(2026, 10, 3), None) == date(2026, 10, 3)


class TestNetWorthHistory:
    def test_each_day_is_today_minus_what_came_after(self, client, auth_headers, category):
        today = _today_utc()
        wallet = _wallet(client, auth_headers, initial_balance="1000")
        _transaction(client, auth_headers, wallet["id"], category["id"], "-100", _noon(today - 5 * DAY))
        _transaction(client, auth_headers, wallet["id"], category["id"], "50", _noon(today - 2 * DAY))

        points = _points(client, auth_headers)

        assert points[str(today)] == "950.0000"
        assert points[str(today - 3 * DAY)] == "900.0000"
        assert points[str(today - 6 * DAY)] == "1000.0000"
        assert list(points)[0] == str(range_start(NetWorthRange.ONE_MONTH, today, None))
        assert list(points) == sorted(points)

    def test_excluded_accounts_dont_count(self, client, auth_headers):
        _wallet(client, auth_headers, initial_balance="100")
        excluded = _wallet(client, auth_headers, initial_balance="900")
        client.patch(f"{WALLETS_URL}/{excluded['id']}", json={"exclude_balance": True}, headers=auth_headers)

        assert set(_points(client, auth_headers).values()) == {"100.0000"}

    def test_all_time_starts_at_the_first_transaction(self, client, auth_headers, category):
        today = _today_utc()
        wallet = _wallet(client, auth_headers)
        _transaction(client, auth_headers, wallet["id"], category["id"], "-1", _noon(today - 400 * DAY))

        points = _points(client, auth_headers, "ALL")

        assert list(points)[0] == str(today - 400 * DAY) and len(points) == 401

    def test_days_follow_the_users_time_zone(self, client, auth_headers, category):
        zone = "Pacific/Kiritimati"  # UTC+14: late evening UTC is already the next day there
        assert client.patch("/api/v1/auth/me", json={"timezone": zone}, headers=auth_headers).status_code == 200
        wallet = _wallet(client, auth_headers)
        when = datetime.combine(_today_utc() - 3 * DAY, time(23), tzinfo=timezone.utc)
        _transaction(client, auth_headers, wallet["id"], category["id"], "-10", when)
        local_day = when.astimezone(ZoneInfo(zone)).date()

        points = _points(client, auth_headers)

        # Counted by UTC, the -10 would land a day earlier
        assert points[str(local_day - DAY)] == "0.0000" and points[str(local_day)] == "-10.0000"

    def test_no_accounts_no_series(self, client, auth_headers):
        assert client.get(NET_WORTH_URL, headers=auth_headers).json() == {"range": "1M", "series": []}

    def test_unknown_range_and_login(self, client, auth_headers):
        assert client.get(NET_WORTH_URL, params={"range": "2W"}, headers=auth_headers).status_code == 422
        assert client.get(NET_WORTH_URL).status_code == 401
