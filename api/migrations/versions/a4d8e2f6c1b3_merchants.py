"""merchants

Adds the `merchants` table and `transactions.merchant_id`, and backfills them: every bank merchant
of an imported transaction becomes a merchant of that user, named as the bank wrote it (the first
transaction's spelling). Manual transactions start without a merchant.

The merchant normalization below is a frozen copy on purpose (see the categories migration):
migrations must produce the same result whenever they run.

Revision ID: a4d8e2f6c1b3
Revises: f1a7c3e9b2d4
Create Date: 2026-10-03 14:45:00

"""
from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a4d8e2f6c1b3"
down_revision: Union[str, Sequence[str], None] = "f1a7c3e9b2d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MERCHANT_MAX = 255


def _merchant_name(counterparty: str | None, description: str | None) -> str | None:
    name = " ".join((counterparty or description or "").split())
    return name[:MERCHANT_MAX] or None


def upgrade() -> None:
    op.create_table(
        "merchants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=MERCHANT_MAX), nullable=False),
        sa.Column("key", sa.String(length=MERCHANT_MAX), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "key", name="uq_merchants_user_key"),
    )
    op.add_column(
        "transactions",
        sa.Column("merchant_id", sa.Integer(), sa.ForeignKey("merchants.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index(op.f("ix_transactions_merchant_id"), "transactions", ["merchant_id"], unique=False)

    # Backfill: one merchant per bank merchant per user, then link the transactions to it
    bind = op.get_bind()
    transactions = sa.table(
        "transactions",
        sa.column("id", sa.Integer),
        sa.column("wallet_id", sa.Integer),
        sa.column("counterparty", sa.String),
        sa.column("description", sa.Text),
        sa.column("merchant_key", sa.String),
        sa.column("merchant_id", sa.Integer),
    )
    wallets = sa.table("wallets", sa.column("id", sa.Integer), sa.column("user_id", sa.Integer))
    merchants = sa.table(
        "merchants",
        sa.column("id", sa.Integer),
        sa.column("user_id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("key", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    rows = bind.execute(
        sa.select(
            transactions.c.id,
            wallets.c.user_id,
            transactions.c.counterparty,
            transactions.c.description,
            transactions.c.merchant_key,
        )
        .join(wallets, wallets.c.id == transactions.c.wallet_id)
        .where(transactions.c.merchant_key.is_not(None))
        .order_by(transactions.c.id)
    ).all()
    now = datetime.now(timezone.utc)
    merchant_ids: dict[tuple[int, str], int] = {}
    for row in rows:
        identity = (row.user_id, row.merchant_key)
        if identity not in merchant_ids:
            merchant_ids[identity] = bind.execute(
                sa.insert(merchants)
                .values(
                    user_id=row.user_id,
                    name=_merchant_name(row.counterparty, row.description),
                    key=row.merchant_key,
                    created_at=now,
                    updated_at=now,
                )
                .returning(merchants.c.id)
            ).scalar_one()
        bind.execute(
            sa.update(transactions).where(transactions.c.id == row.id).values(merchant_id=merchant_ids[identity])
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_transactions_merchant_id"), table_name="transactions")
    op.drop_column("transactions", "merchant_id")
    op.drop_table("merchants")
