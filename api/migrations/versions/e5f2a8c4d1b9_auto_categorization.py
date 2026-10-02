"""auto-categorization: category source, merchant key and merchant rules

Adds `transactions.category_source` and `transactions.merchant_key`, the `merchant_rules`
table, and backfills existing rows: imported transactions still in Uncategorized become
`default` (the review inbox), every other transaction counts as the user's own choice.

The merchant normalization below is a frozen copy on purpose (see the categories migration):
migrations must produce the same result whenever they run.

Revision ID: e5f2a8c4d1b9
Revises: c3d9a1f0e7b2
Create Date: 2026-10-03 00:30:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "e5f2a8c4d1b9"
down_revision: Union[str, Sequence[str], None] = "c3d9a1f0e7b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

category_source = sa.Enum("manual", "rule", "mcc", "default", name="categorysource")
UNCATEGORIZED_KEY = "other.uncategorized"
MERCHANT_MAX = 255


def _merchant_key(counterparty: str | None, description: str | None) -> str | None:
    name = " ".join((counterparty or description or "").split())[:MERCHANT_MAX]
    return name.casefold() or None


def upgrade() -> None:
    bind = op.get_bind()
    category_source.create(bind, checkfirst=True)
    op.add_column(
        "transactions",
        sa.Column(
            "category_source",
            sa.Enum(name="categorysource", create_type=False),
            server_default="manual",
            nullable=False,
        ),
    )
    op.add_column("transactions", sa.Column("merchant_key", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_transactions_merchant_key"), "transactions", ["merchant_key"], unique=False)

    op.create_table(
        "merchant_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("merchant_key", sa.String(length=255), nullable=False),
        sa.Column("merchant_name", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "merchant_key", name="uq_merchant_rules_user_merchant"),
    )
    op.create_index(op.f("ix_merchant_rules_category_id"), "merchant_rules", ["category_id"], unique=False)

    # Backfill: imported transactions waiting in Uncategorized go to the review inbox
    op.execute(
        sa.text(
            "UPDATE transactions SET category_source = 'default' "
            "WHERE external_id IS NOT NULL "
            "AND category_id = (SELECT id FROM categories WHERE key = :key AND user_id IS NULL)"
        ).bindparams(key=UNCATEGORIZED_KEY)
    )
    # Backfill: merchant keys of imported transactions
    transactions = sa.table(
        "transactions",
        sa.column("id", sa.Integer),
        sa.column("counterparty", sa.String),
        sa.column("description", sa.Text),
        sa.column("external_id", sa.String),
        sa.column("merchant_key", sa.String),
    )
    rows = bind.execute(
        sa.select(transactions.c.id, transactions.c.counterparty, transactions.c.description).where(
            transactions.c.external_id.is_not(None)
        )
    ).all()
    for row in rows:
        key = _merchant_key(row.counterparty, row.description)
        if key is not None:
            bind.execute(sa.update(transactions).where(transactions.c.id == row.id).values(merchant_key=key))


def downgrade() -> None:
    op.drop_index(op.f("ix_merchant_rules_category_id"), table_name="merchant_rules")
    op.drop_table("merchant_rules")
    op.drop_index(op.f("ix_transactions_merchant_key"), table_name="transactions")
    op.drop_column("transactions", "merchant_key")
    op.drop_column("transactions", "category_source")
    category_source.drop(op.get_bind(), checkfirst=True)
