"""transfer pairs: each side of a transfer between the user's own accounts points at the other

Adds `transactions.transfer_pair_id`. Transactions already filed as transfers (`category_source`
'transfer') are paired again by the next sync.

Revision ID: c8f3a6d2e9b4
Revises: b5d8e1a3c7f2
Create Date: 2026-10-04 16:30:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c8f3a6d2e9b4"
down_revision: Union[str, Sequence[str], None] = "b5d8e1a3c7f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column(
            "transfer_pair_id", sa.Integer(), sa.ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True
        ),
    )


def downgrade() -> None:
    op.drop_column("transactions", "transfer_pair_id")
