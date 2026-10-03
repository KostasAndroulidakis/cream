"""category icons and per-user order

Adds `categories.icon` (an emoji) with Monarch's emoji for the system categories, and
`category_positions`: where each user put each category within its group.

Revision ID: e8a3c5f1b9d2
Revises: d2b6e9f4a7c1
Create Date: 2026-10-03 19:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "e8a3c5f1b9d2"
down_revision: Union[str, Sequence[str], None] = "d2b6e9f4a7c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# System category key -> Monarch's emoji (frozen snapshot, like the catalog itself)
SYSTEM_ICONS: dict[str, str] = {
    "income.paychecks": "💵",
    "income.interest": "💸",
    "income.business_income": "💰",
    "income.other_income": "💰",
    "gifts_and_donations.charity": "🎗️",
    "gifts_and_donations.gifts": "🎁",
    "auto_and_transport.auto_payment": "🚗",
    "auto_and_transport.public_transit": "🚃",
    "auto_and_transport.gas": "⛽",
    "auto_and_transport.auto_maintenance": "🔧",
    "auto_and_transport.parking_and_tolls": "🏢",
    "auto_and_transport.taxi_and_ride_shares": "🚕",
    "housing.mortgage": "🏠",
    "housing.rent": "🏠",
    "housing.home_improvement": "🔨",
    "bills_and_utilities.garbage": "🗑️",
    "bills_and_utilities.water": "💧",
    "bills_and_utilities.gas_and_electric": "⚡",
    "bills_and_utilities.internet_and_cable": "🌐",
    "bills_and_utilities.phone": "📱",
    "food_and_dining.groceries": "🍏",
    "food_and_dining.restaurants_and_bars": "🍽️",
    "food_and_dining.coffee_shops": "☕",
    "travel_and_lifestyle.travel_and_vacation": "🏝️",
    "travel_and_lifestyle.entertainment_and_recreation": "🎥",
    "travel_and_lifestyle.personal": "👑",
    "travel_and_lifestyle.pets": "🐶",
    "travel_and_lifestyle.fun_money": "😜",
    "shopping.shopping": "🛍️",
    "shopping.clothing": "👕",
    "shopping.furniture_and_housewares": "🪑",
    "shopping.electronics": "🖥️",
    "children.child_care": "👶",
    "children.child_activities": "⚽",
    "education.student_loans": "🎓",
    "education.education": "🏫",
    "health_and_wellness.medical": "💊",
    "health_and_wellness.dentist": "🦷",
    "health_and_wellness.fitness": "💪",
    "financial.loan_repayment": "💰",
    "financial.financial_and_legal_services": "🗄️",
    "financial.financial_fees": "🏦",
    "financial.cash_and_atm": "🏧",
    "financial.insurance": "☂️",
    "financial.taxes": "🏛️",
    "other.uncategorized": "❓",
    "other.check": "💸",
    "other.miscellaneous": "💲",
    "business.advertising_and_promotion": "📣",
    "business.business_utilities_and_communication": "📞",
    "business.employee_wages_and_contract_labor": "💵",
    "business.business_travel_and_meals": "✈️",
    "business.business_auto_expenses": "🚘",
    "business.business_insurance": "🗂️",
    "business.office_supplies_and_expenses": "📎",
    "business.office_rent": "🏢",
    "business.postage_and_shipping": "📦",
    "transfers.transfer": "🔁",
    "transfers.credit_card_payment": "💳",
    "transfers.balance_adjustments": "⚖️",
}


def upgrade() -> None:
    op.add_column("categories", sa.Column("icon", sa.String(length=16), nullable=True))

    categories = sa.table("categories", sa.column("key", sa.String), sa.column("icon", sa.String))
    for key, icon in SYSTEM_ICONS.items():
        op.execute(sa.update(categories).where(categories.c.key == key).values(icon=icon))

    op.create_table(
        "category_positions",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("position", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("category_positions")
    op.drop_column("categories", "icon")
