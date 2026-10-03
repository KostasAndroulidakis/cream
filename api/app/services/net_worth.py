"""Net worth over time, worked out from the transactions: no stored history needed.

A day's balance is today's balance minus everything booked after that day. Exact for accounts that move
through transactions (bank accounts); a hand-set balance (Edit Account) shifts that account's whole history.
"""

import calendar
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone, tzinfo
from decimal import Decimal
from enum import Enum
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import as_utc
from app.models import Transaction, User, Wallet

DAY = timedelta(days=1)


class NetWorthRange(str, Enum):
    """The chart's periods (Monarch's dateRange=1M and the like)."""

    ONE_MONTH = "1M"
    THREE_MONTHS = "3M"
    SIX_MONTHS = "6M"
    YEAR_TO_DATE = "YTD"
    ONE_YEAR = "1Y"
    ALL_TIME = "ALL"


# Months back for the ranges that are a number of months
_MONTHS_BACK = {
    NetWorthRange.ONE_MONTH: 1,
    NetWorthRange.THREE_MONTHS: 3,
    NetWorthRange.SIX_MONTHS: 6,
    NetWorthRange.ONE_YEAR: 12,
}


def _months_before(day: date, months: int) -> date:
    """The same day `months` earlier, or that month's last day when it is shorter (Mar 31 -> Feb 28)."""
    year, month_index = divmod(day.year * 12 + day.month - 1 - months, 12)
    month = month_index + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def user_zone(user: User) -> tzinfo:
    """The user's time zone (Settings › Profile), or UTC when they haven't set one."""
    return ZoneInfo(user.timezone) if user.timezone else timezone.utc


def range_start(period: NetWorthRange, today: date, first_day: date | None) -> date:
    """The first day the chart shows; "All time" starts at the first transaction."""
    if period is NetWorthRange.YEAR_TO_DATE:
        return today.replace(month=1, day=1)
    if period is NetWorthRange.ALL_TIME:
        return min(first_day or today, today)
    return _months_before(today, _MONTHS_BACK[period])


def net_worth_history(user: User, period: NetWorthRange, db: Session) -> dict[str, list[tuple[date, Decimal]]]:
    """Net worth at the end of each day of the period, per currency (oldest day first).

    Counts the same accounts as the net worth figure: every account but those set to "Exclude account balance".
    """
    zone = user_zone(user)
    today = datetime.now(zone).date()
    wallets = list(db.scalars(select(Wallet).where(Wallet.user_id == user.id, Wallet.exclude_balance.is_(False))))
    currency_of = {wallet.id: wallet.currency for wallet in wallets}

    # Each transaction's amount on its day, as the user's clock saw it
    booked: dict[str, dict[date, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    rows = db.execute(
        select(Transaction.wallet_id, Transaction.occurred_at, Transaction.amount).where(
            Transaction.wallet_id.in_(currency_of)
        )
    )
    first_day = None
    for wallet_id, occurred_at, amount in rows:
        day = as_utc(occurred_at).astimezone(zone).date()
        booked[currency_of[wallet_id]][day] += amount
        first_day = day if first_day is None else min(first_day, day)

    start = range_start(period, today, first_day)
    history: dict[str, list[tuple[date, Decimal]]] = {}
    for currency in sorted(set(currency_of.values())):
        balance = sum((wallet.balance for wallet in wallets if wallet.currency == currency), Decimal("0"))
        # Walk back from today: the day before holds today's balance minus today's transactions
        points = []
        day = today
        while day >= start:
            points.append((day, balance))
            balance -= booked[currency].get(day, Decimal("0"))
            day -= DAY
        history[currency] = points[::-1]
    return history
