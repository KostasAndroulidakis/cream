from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.category import CategoryType


class WalletBalance(BaseModel):
    """Balance information for a single wallet."""
    wallet_id: int
    wallet_name: str
    balance: Decimal

    model_config = {"from_attributes": True}


class CategoryTotal(BaseModel):
    """Total amount for a single category."""
    category_id: int
    category_name: str
    total: Decimal

    model_config = {"from_attributes": True}


class StatisticsResponse(BaseModel):
    """Overall statistics for a user."""
    total_balance: Decimal
    total_income: Decimal
    total_expenses: Decimal
    wallet_balances: list[WalletBalance]
    spending_by_category: list[CategoryTotal]
    income_by_category: list[CategoryTotal]


class ReportPeriod(BaseModel):
    """Time period for a report."""
    start_date: datetime
    end_date: datetime


class ReportSummary(BaseModel):
    """Summary statistics for a report period."""
    income: Decimal
    expenses: Decimal
    net_change: Decimal
    transaction_count: int


class CategoryBreakdown(BaseModel):
    """Category breakdown for a report."""
    category_id: int
    category_name: str
    type: CategoryType
    total: Decimal
    count: int

    model_config = {"from_attributes": True}


class WalletBreakdown(BaseModel):
    """Wallet breakdown for a report."""
    wallet_id: int
    wallet_name: str
    income: Decimal
    expenses: Decimal
    net_change: Decimal

    model_config = {"from_attributes": True}


class ReportResponse(BaseModel):
    """Period-based financial report."""
    period: ReportPeriod
    summary: ReportSummary
    by_category: list[CategoryBreakdown]
    by_wallet: list[WalletBreakdown]
