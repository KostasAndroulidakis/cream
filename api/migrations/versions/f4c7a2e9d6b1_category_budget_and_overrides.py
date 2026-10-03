"""category budget settings and per-user overrides

Adds `categories.budget_by` (groups: budget the group as a whole or by category; the seeded
groups budget by category, as in Monarch) and `categories.exclude_from_budget`, plus
`category_overrides`: one user's name, budget choice or deletion of a shared system category.

Revision ID: f4c7a2e9d6b1
Revises: e8a3c5f1b9d2
Create Date: 2026-10-03 21:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f4c7a2e9d6b1"
down_revision: Union[str, Sequence[str], None] = "e8a3c5f1b9d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("categories", sa.Column("budget_by", sa.String(length=16), nullable=True))
    op.add_column(
        "categories", sa.Column("exclude_from_budget", sa.Boolean(), server_default=sa.false(), nullable=False)
    )
    op.execute("UPDATE categories SET budget_by = 'category' WHERE is_group = true")

    op.create_table(
        "category_overrides",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("budget_by", sa.String(length=16), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), server_default=sa.false(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("category_overrides")
    op.drop_column("categories", "exclude_from_budget")
    op.drop_column("categories", "budget_by")
