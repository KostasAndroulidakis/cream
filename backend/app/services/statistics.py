"""Statistics service for aggregation calculations.

Extracts business logic from API handlers to ensure SRP compliance.
All SQL aggregations and calculations are centralized here.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models import Category, Transaction, Wallet


@dataclass
class WalletBalanceData:
    """Wallet balance information."""

    wallet_id: int
    wallet_name: str
    balance: Decimal


@dataclass
class CategoryTotalData:
    """Category total information."""

    category_id: int
    category_name: str
    total: Decimal


@dataclass
class CategoryBreakdownData:
    """Category breakdown with type and count."""

    category_id: int
    category_name: str
    category_type: str
    total: Decimal
    count: int


@dataclass
class WalletBreakdownData:
    """Wallet breakdown with income/expenses."""

    wallet_id: int
    wallet_name: str
    income: Decimal
    expenses: Decimal
    net_change: Decimal


@dataclass
class StatisticsData:
    """Overall statistics data."""

    total_balance: Decimal
    total_income: Decimal
    total_expenses: Decimal
    wallet_balances: list[WalletBalanceData]
    spending_by_category: list[CategoryTotalData]
    income_by_category: list[CategoryTotalData]


@dataclass
class ReportSummaryData:
    """Report summary data."""

    income: Decimal
    expenses: Decimal
    net_change: Decimal
    transaction_count: int


@dataclass
class ReportData:
    """Full report data."""

    start_date: datetime
    end_date: datetime
    summary: ReportSummaryData
    by_category: list[CategoryBreakdownData]
    by_wallet: list[WalletBreakdownData]


def _to_decimal(value) -> Decimal:
    """Convert query result to Decimal safely."""
    return Decimal(str(value)) if value else Decimal("0")


def _sum_income_expr():
    """SQL expression for summing income (positive amounts)."""
    return func.coalesce(
        func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)), 0
    )


def _sum_expenses_expr():
    """SQL expression for summing expenses (absolute negative amounts)."""
    return func.coalesce(
        func.sum(case((Transaction.amount < 0, func.abs(Transaction.amount)), else_=0)), 0
    )


def get_user_wallets(user_id: int, db: Session) -> list[Wallet]:
    """Get all wallets for a user."""
    return db.query(Wallet).filter(Wallet.user_id == user_id).all()


def get_user_wallet_ids(user_id: int, db: Session) -> list[int]:
    """Get all wallet IDs for a user."""
    return [w.id for w in db.query(Wallet.id).filter(Wallet.user_id == user_id).all()]


def get_user_wallet_ids_subquery(user_id: int, db: Session):
    """Get a subquery for user's wallet IDs (more efficient for large datasets)."""
    return db.query(Wallet.id).filter(Wallet.user_id == user_id).scalar_subquery()


def calculate_wallet_balance(wallet: Wallet, db: Session) -> Decimal:
    """Calculate wallet balance using SQL aggregation."""
    tx_sum = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.wallet_id == wallet.id
    ).scalar()
    return wallet.initial_balance + _to_decimal(tx_sum)


def calculate_statistics(user_id: int, db: Session) -> StatisticsData:
    """Calculate overall statistics for a user.

    Args:
        user_id: The user's ID
        db: Database session

    Returns:
        StatisticsData with all aggregated values
    """
    user_wallets = get_user_wallets(user_id, db)
    wallet_ids = [w.id for w in user_wallets]

    # Empty case
    if not wallet_ids:
        return StatisticsData(
            total_balance=Decimal("0"),
            total_income=Decimal("0"),
            total_expenses=Decimal("0"),
            wallet_balances=[],
            spending_by_category=[],
            income_by_category=[],
        )

    # Calculate wallet balances
    wallet_balances = []
    total_balance = Decimal("0")

    for wallet in user_wallets:
        balance = calculate_wallet_balance(wallet, db)
        wallet_balances.append(
            WalletBalanceData(
                wallet_id=wallet.id,
                wallet_name=wallet.name,
                balance=balance,
            )
        )
        total_balance += balance

    # Calculate total income and expenses
    totals = db.query(
        _sum_income_expr().label("income"),
        _sum_expenses_expr().label("expenses"),
    ).filter(Transaction.wallet_id.in_(wallet_ids)).first()

    total_income = _to_decimal(totals.income)
    total_expenses = _to_decimal(totals.expenses)

    # Spending by category
    spending_by_category = _get_category_totals(
        wallet_ids, db, amount_filter=Transaction.amount < 0, use_abs=True
    )

    # Income by category
    income_by_category = _get_category_totals(
        wallet_ids, db, amount_filter=Transaction.amount > 0, use_abs=False
    )

    return StatisticsData(
        total_balance=total_balance,
        total_income=total_income,
        total_expenses=total_expenses,
        wallet_balances=wallet_balances,
        spending_by_category=spending_by_category,
        income_by_category=income_by_category,
    )


def _get_category_totals(
    wallet_ids: list[int],
    db: Session,
    *,
    amount_filter,
    use_abs: bool,
    limit: int = 50,
) -> list[CategoryTotalData]:
    """Get category totals with configurable amount filter.

    Args:
        wallet_ids: List of wallet IDs to include
        db: Database session
        amount_filter: SQLAlchemy filter for amount (e.g., > 0 or < 0)
        use_abs: Whether to use absolute values
        limit: Maximum number of categories to return (default 50)
    """
    sum_expr = func.sum(func.abs(Transaction.amount)) if use_abs else func.sum(Transaction.amount)

    query = (
        db.query(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.coalesce(sum_expr, 0).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.wallet_id.in_(wallet_ids))
        .filter(amount_filter)
        .group_by(Category.id, Category.name)
        .order_by(sum_expr.desc())
        .limit(limit)
        .all()
    )

    return [
        CategoryTotalData(
            category_id=row.category_id,
            category_name=row.category_name,
            total=_to_decimal(row.total),
        )
        for row in query
    ]


def calculate_report(
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session,
) -> ReportData:
    """Calculate a financial report for a period.

    Args:
        user_id: The user's ID
        start_date: Report period start
        end_date: Report period end
        db: Database session

    Returns:
        ReportData with all period aggregations
    """
    user_wallets = get_user_wallets(user_id, db)
    wallet_ids = [w.id for w in user_wallets]

    # Empty case
    if not wallet_ids:
        return ReportData(
            start_date=start_date,
            end_date=end_date,
            summary=ReportSummaryData(
                income=Decimal("0"),
                expenses=Decimal("0"),
                net_change=Decimal("0"),
                transaction_count=0,
            ),
            by_category=[],
            by_wallet=[],
        )

    # Base filter for transactions in period
    period_filter = [
        Transaction.wallet_id.in_(wallet_ids),
        Transaction.occurred_at >= start_date,
        Transaction.occurred_at <= end_date,
    ]

    # Summary statistics
    summary = _calculate_period_summary(period_filter, db)

    # By category breakdown
    by_category = _calculate_category_breakdown(period_filter, db)

    # By wallet breakdown
    by_wallet = _calculate_wallet_breakdown(period_filter, user_wallets, db)

    return ReportData(
        start_date=start_date,
        end_date=end_date,
        summary=summary,
        by_category=by_category,
        by_wallet=by_wallet,
    )


def _calculate_period_summary(period_filter: list, db: Session) -> ReportSummaryData:
    """Calculate summary statistics for a period."""
    summary_query = db.query(
        _sum_income_expr().label("income"),
        _sum_expenses_expr().label("expenses"),
        func.count(Transaction.id).label("count"),
    ).filter(*period_filter).first()

    income = _to_decimal(summary_query.income)
    expenses = _to_decimal(summary_query.expenses)

    return ReportSummaryData(
        income=income,
        expenses=expenses,
        net_change=income - expenses,
        transaction_count=summary_query.count,
    )


def _calculate_category_breakdown(
    period_filter: list, db: Session, *, limit: int = 50
) -> list[CategoryBreakdownData]:
    """Calculate category breakdown for a period.

    Args:
        period_filter: List of SQLAlchemy filter conditions
        db: Database session
        limit: Maximum number of categories to return (default 50)
    """
    query = (
        db.query(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            Category.type.label("category_type"),
            func.coalesce(func.sum(func.abs(Transaction.amount)), 0).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(*period_filter)
        .group_by(Category.id, Category.name, Category.type)
        .order_by(func.sum(func.abs(Transaction.amount)).desc())
        .limit(limit)
        .all()
    )

    return [
        CategoryBreakdownData(
            category_id=row.category_id,
            category_name=row.category_name,
            category_type=row.category_type.value if hasattr(row.category_type, 'value') else str(row.category_type),
            total=_to_decimal(row.total),
            count=row.count,
        )
        for row in query
    ]


def _calculate_wallet_breakdown(
    period_filter: list, user_wallets: list[Wallet], db: Session
) -> list[WalletBreakdownData]:
    """Calculate wallet breakdown for a period."""
    query = (
        db.query(
            Wallet.id.label("wallet_id"),
            Wallet.name.label("wallet_name"),
            _sum_income_expr().label("income"),
            _sum_expenses_expr().label("expenses"),
        )
        .join(Transaction, Transaction.wallet_id == Wallet.id)
        .filter(*period_filter)
        .group_by(Wallet.id, Wallet.name)
        .all()
    )

    return [
        WalletBreakdownData(
            wallet_id=row.wallet_id,
            wallet_name=row.wallet_name,
            income=_to_decimal(row.income),
            expenses=_to_decimal(row.expenses),
            net_change=_to_decimal(row.income) - _to_decimal(row.expenses),
        )
        for row in query
    ]
