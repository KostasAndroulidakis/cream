from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Transaction, Wallet
from app.models.category import CategoryType
from app.schemas.statistics import (
    CategoryBreakdown,
    CategoryTotal,
    ReportPeriod,
    ReportResponse,
    ReportSummary,
    StatisticsResponse,
    WalletBalance,
    WalletBreakdown,
)
from app.services.auth import get_current_user_id

router = APIRouter()


@router.get("", response_model=StatisticsResponse)
def get_statistics(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get overall statistics for the current user."""
    # Get user's wallet IDs
    user_wallets = db.query(Wallet).filter(Wallet.user_id == user_id).all()
    wallet_ids = [w.id for w in user_wallets]

    if not wallet_ids:
        return StatisticsResponse(
            total_balance=Decimal("0"),
            total_income=Decimal("0"),
            total_expenses=Decimal("0"),
            wallet_balances=[],
            spending_by_category=[],
            income_by_category=[],
        )

    # Calculate wallet balances (initial_balance + sum of transactions)
    wallet_balances = []
    total_balance = Decimal("0")

    for wallet in user_wallets:
        tx_sum = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.wallet_id == wallet.id
        ).scalar()
        balance = wallet.initial_balance + Decimal(str(tx_sum))
        wallet_balances.append(
            WalletBalance(
                wallet_id=wallet.id,
                wallet_name=wallet.name,
                balance=balance,
            )
        )
        total_balance += balance

    # Calculate total income and expenses
    totals = db.query(
        func.coalesce(func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)), 0).label("income"),
        func.coalesce(func.sum(case((Transaction.amount < 0, func.abs(Transaction.amount)), else_=0)), 0).label("expenses"),
    ).filter(Transaction.wallet_id.in_(wallet_ids)).first()

    total_income = Decimal(str(totals.income))
    total_expenses = Decimal(str(totals.expenses))

    # Spending by category (expenses only, grouped by category)
    spending_query = (
        db.query(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.coalesce(func.sum(func.abs(Transaction.amount)), 0).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.wallet_id.in_(wallet_ids))
        .filter(Transaction.amount < 0)
        .group_by(Category.id, Category.name)
        .order_by(func.sum(func.abs(Transaction.amount)).desc())
        .all()
    )

    spending_by_category = [
        CategoryTotal(
            category_id=row.category_id,
            category_name=row.category_name,
            total=Decimal(str(row.total)),
        )
        for row in spending_query
    ]

    # Income by category (income only, grouped by category)
    income_query = (
        db.query(
            Category.id.label("category_id"),
            Category.name.label("category_name"),
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.wallet_id.in_(wallet_ids))
        .filter(Transaction.amount > 0)
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    income_by_category = [
        CategoryTotal(
            category_id=row.category_id,
            category_name=row.category_name,
            total=Decimal(str(row.total)),
        )
        for row in income_query
    ]

    return StatisticsResponse(
        total_balance=total_balance,
        total_income=total_income,
        total_expenses=total_expenses,
        wallet_balances=wallet_balances,
        spending_by_category=spending_by_category,
        income_by_category=income_by_category,
    )


@router.get("/report", response_model=ReportResponse)
def get_report(
    start_date: datetime = Query(..., description="Start date for the report period"),
    end_date: datetime = Query(..., description="End date for the report period"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a financial report for a specific period."""
    # Get user's wallet IDs
    user_wallets = db.query(Wallet).filter(Wallet.user_id == user_id).all()
    wallet_ids = [w.id for w in user_wallets]

    if not wallet_ids:
        return ReportResponse(
            period=ReportPeriod(start_date=start_date, end_date=end_date),
            summary=ReportSummary(
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
    summary_query = db.query(
        func.coalesce(func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)), 0).label("income"),
        func.coalesce(func.sum(case((Transaction.amount < 0, func.abs(Transaction.amount)), else_=0)), 0).label("expenses"),
        func.count(Transaction.id).label("count"),
    ).filter(*period_filter).first()

    income = Decimal(str(summary_query.income))
    expenses = Decimal(str(summary_query.expenses))
    net_change = income - expenses
    transaction_count = summary_query.count

    # By category breakdown
    category_query = (
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
        .all()
    )

    by_category = [
        CategoryBreakdown(
            category_id=row.category_id,
            category_name=row.category_name,
            type=row.category_type,
            total=Decimal(str(row.total)),
            count=row.count,
        )
        for row in category_query
    ]

    # By wallet breakdown
    wallet_query = (
        db.query(
            Wallet.id.label("wallet_id"),
            Wallet.name.label("wallet_name"),
            func.coalesce(func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)), 0).label("income"),
            func.coalesce(func.sum(case((Transaction.amount < 0, func.abs(Transaction.amount)), else_=0)), 0).label("expenses"),
        )
        .join(Transaction, Transaction.wallet_id == Wallet.id)
        .filter(*period_filter)
        .group_by(Wallet.id, Wallet.name)
        .all()
    )

    by_wallet = [
        WalletBreakdown(
            wallet_id=row.wallet_id,
            wallet_name=row.wallet_name,
            income=Decimal(str(row.income)),
            expenses=Decimal(str(row.expenses)),
            net_change=Decimal(str(row.income)) - Decimal(str(row.expenses)),
        )
        for row in wallet_query
    ]

    return ReportResponse(
        period=ReportPeriod(start_date=start_date, end_date=end_date),
        summary=ReportSummary(
            income=income,
            expenses=expenses,
            net_change=net_change,
            transaction_count=transaction_count,
        ),
        by_category=by_category,
        by_wallet=by_wallet,
    )
