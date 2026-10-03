"""transaction review

Adds `transactions.needs_review` (the review inbox, independent of category and hiding) and the
`user_preferences` table with the two review preferences. Backfill: every transaction in
Uncategorized needs review, so the inbox shows what it showed before. Users get their preferences
row when they first change one; until then the defaults apply.

Revision ID: b8e3f1a7d2c5
Revises: a4d8e2f6c1b3
Create Date: 2026-10-03 15:30:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b8e3f1a7d2c5"
down_revision: Union[str, Sequence[str], None] = "a4d8e2f6c1b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Frozen copy on purpose (see the categories migration)
UNCATEGORIZED_KEY = "other.uncategorized"


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("needs_review", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.create_table(
        "user_preferences",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("review_new_transactions", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("review_uncategorized_transactions", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    # Backfill: the inbox keeps what it showed before (everything in Uncategorized)
    op.execute(
        sa.text(
            "UPDATE transactions SET needs_review = true "
            "WHERE category_id = (SELECT id FROM categories WHERE key = :key AND user_id IS NULL)"
        ).bindparams(key=UNCATEGORIZED_KEY)
    )


def downgrade() -> None:
    op.drop_table("user_preferences")
    op.drop_column("transactions", "needs_review")
