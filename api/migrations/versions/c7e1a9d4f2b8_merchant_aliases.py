"""merchant aliases: a merchant has many names

A merchant's identity moves from its one `key` to `merchant_aliases` (the bank's spellings and the
user's names), so renaming keeps imports matching and merging can move names. Each merchant's key
becomes its first alias. Downgrade puts each merchant's first alias back as its key.

Revision ID: c7e1a9d4f2b8
Revises: b3e8d1f5a7c2
Create Date: 2026-10-04 10:40:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c7e1a9d4f2b8"
down_revision: Union[str, Sequence[str], None] = "b3e8d1f5a7c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Frozen here (app.services.categorization.merchants.MERCHANT_MAX at the time)
MERCHANT_MAX = 255


def upgrade() -> None:
    op.create_table(
        "merchant_aliases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=MERCHANT_MAX), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "key", name="uq_merchant_aliases_user_key"),
    )
    op.create_index(op.f("ix_merchant_aliases_merchant_id"), "merchant_aliases", ["merchant_id"], unique=False)
    op.execute("INSERT INTO merchant_aliases (user_id, merchant_id, key) SELECT user_id, id, key FROM merchants")
    op.drop_constraint("uq_merchants_user_key", "merchants", type_="unique")
    op.drop_column("merchants", "key")
    # The unique (user_id, key) index used to serve lookups by user
    op.create_index(op.f("ix_merchants_user_id"), "merchants", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_merchants_user_id"), table_name="merchants")
    op.add_column("merchants", sa.Column("key", sa.String(length=MERCHANT_MAX), nullable=True))
    op.execute(
        "UPDATE merchants SET key = (SELECT key FROM merchant_aliases a WHERE a.merchant_id = merchants.id "
        "ORDER BY a.id LIMIT 1)"
    )
    op.alter_column("merchants", "key", nullable=False)
    op.create_unique_constraint("uq_merchants_user_key", "merchants", ["user_id", "key"])
    op.drop_index(op.f("ix_merchant_aliases_merchant_id"), table_name="merchant_aliases")
    op.drop_table("merchant_aliases")
