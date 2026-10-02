"""category groups, transfer type and default categories

Adds the `transfer` category type, `key`/`is_group` columns, and seeds the
system default categories (Monarch's default set) as groups with categories.

The catalog below is a frozen snapshot on purpose: migrations must produce the
same result whenever they run. Later catalog changes belong in new migrations.

Revision ID: b7c1e2d4f5a6
Revises: 8aaba5957b8a
Create Date: 2026-10-02 23:00:00

"""
import re
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b7c1e2d4f5a6"
down_revision: Union[str, Sequence[str], None] = "8aaba5957b8a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (group name, category type, [category names]) in display order
DEFAULT_CATEGORIES: list[tuple[str, str, list[str]]] = [
    ("Income", "income", ["Paychecks", "Interest", "Business Income", "Other Income"]),
    ("Gifts & Donations", "expense", ["Charity", "Gifts"]),
    ("Auto & Transport", "expense", [
        "Auto Payment", "Public Transit", "Gas", "Auto Maintenance", "Parking & Tolls", "Taxi & Ride Shares",
    ]),
    ("Housing", "expense", ["Mortgage", "Rent", "Home Improvement"]),
    ("Bills & Utilities", "expense", ["Garbage", "Water", "Gas & Electric", "Internet & Cable", "Phone"]),
    ("Food & Dining", "expense", ["Groceries", "Restaurants & Bars", "Coffee Shops"]),
    ("Travel & Lifestyle", "expense", [
        "Travel & Vacation", "Entertainment & Recreation", "Personal", "Pets", "Fun Money",
    ]),
    ("Shopping", "expense", ["Shopping", "Clothing", "Furniture & Housewares", "Electronics"]),
    ("Children", "expense", ["Child Care", "Child Activities"]),
    ("Education", "expense", ["Student Loans", "Education"]),
    ("Health & Wellness", "expense", ["Medical", "Dentist", "Fitness"]),
    ("Financial", "expense", [
        "Loan Repayment", "Financial & Legal Services", "Financial Fees", "Cash & ATM", "Insurance", "Taxes",
    ]),
    ("Other", "expense", ["Uncategorized", "Check", "Miscellaneous"]),
    ("Business", "expense", [
        "Advertising & Promotion", "Business Utilities & Communication", "Employee Wages & Contract Labor",
        "Business Travel & Meals", "Business Auto Expenses", "Business Insurance", "Office Supplies & Expenses",
        "Office Rent", "Postage & Shipping",
    ]),
    ("Transfers", "transfer", ["Transfer", "Credit Card Payment", "Balance Adjustments"]),
]


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower().replace("&", "and")).strip("_")


def upgrade() -> None:
    # A new enum value must be committed before rows can use it
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE categorytype ADD VALUE IF NOT EXISTS 'transfer'")

    op.add_column("categories", sa.Column("key", sa.String(length=100), nullable=True))
    op.add_column(
        "categories", sa.Column("is_group", sa.Boolean(), server_default=sa.false(), nullable=False)
    )
    op.create_unique_constraint("uq_categories_key", "categories", ["key"])

    categories = sa.table(
        "categories",
        sa.column("id", sa.Integer),
        sa.column("user_id", sa.Integer),
        sa.column("parent_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("type", sa.Enum("income", "expense", "transfer", name="categorytype", create_type=False)),
        sa.column("key", sa.String),
        sa.column("is_group", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    bind = op.get_bind()
    now = sa.func.now()

    for group_name, category_type, names in DEFAULT_CATEGORIES:
        group_slug = _slug(group_name)
        group_id = bind.execute(
            sa.insert(categories)
            .values(
                user_id=None, parent_id=None, name=group_name, type=category_type,
                key=f"group.{group_slug}", is_group=True, created_at=now,
            )
            .returning(categories.c.id)
        ).scalar_one()
        for name in names:
            bind.execute(
                sa.insert(categories).values(
                    user_id=None, parent_id=group_id, name=name, type=category_type,
                    key=f"{group_slug}.{_slug(name)}", is_group=False, created_at=now,
                )
            )


def downgrade() -> None:
    # Removes the seeded catalog; fails if transactions still use it (ON DELETE RESTRICT)
    op.execute("DELETE FROM categories WHERE user_id IS NULL AND is_group = false")
    op.execute("DELETE FROM categories WHERE user_id IS NULL AND is_group = true")
    op.drop_constraint("uq_categories_key", "categories", type_="unique")
    op.drop_column("categories", "is_group")
    op.drop_column("categories", "key")
    # Postgres can't drop a single enum value; 'transfer' stays in the type (harmless)
