from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
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
from app.services import statistics as stats_service

router = APIRouter()


@router.get("", response_model=StatisticsResponse)
def get_statistics(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get overall statistics for the current user."""
    data = stats_service.calculate_statistics(user_id, db)

    return StatisticsResponse(
        total_balance=data.total_balance,
        total_income=data.total_income,
        total_expenses=data.total_expenses,
        wallet_balances=[
            WalletBalance(
                wallet_id=wb.wallet_id,
                wallet_name=wb.wallet_name,
                balance=wb.balance,
            )
            for wb in data.wallet_balances
        ],
        spending_by_category=[
            CategoryTotal(
                category_id=ct.category_id,
                category_name=ct.category_name,
                total=ct.total,
            )
            for ct in data.spending_by_category
        ],
        income_by_category=[
            CategoryTotal(
                category_id=ct.category_id,
                category_name=ct.category_name,
                total=ct.total,
            )
            for ct in data.income_by_category
        ],
    )


@router.get("/report", response_model=ReportResponse)
def get_report(
    start_date: datetime = Query(..., description="Start date for the report period"),
    end_date: datetime = Query(..., description="End date for the report period"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get a financial report for a specific period."""
    data = stats_service.calculate_report(user_id, start_date, end_date, db)

    return ReportResponse(
        period=ReportPeriod(start_date=data.start_date, end_date=data.end_date),
        summary=ReportSummary(
            income=data.summary.income,
            expenses=data.summary.expenses,
            net_change=data.summary.net_change,
            transaction_count=data.summary.transaction_count,
        ),
        by_category=[
            CategoryBreakdown(
                category_id=cb.category_id,
                category_name=cb.category_name,
                type=cb.category_type,
                total=cb.total,
                count=cb.count,
            )
            for cb in data.by_category
        ],
        by_wallet=[
            WalletBreakdown(
                wallet_id=wb.wallet_id,
                wallet_name=wb.wallet_name,
                income=wb.income,
                expenses=wb.expenses,
                net_change=wb.net_change,
            )
            for wb in data.by_wallet
        ],
    )
