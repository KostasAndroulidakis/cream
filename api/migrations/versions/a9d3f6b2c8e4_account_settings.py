"""account settings (Edit Account)

Adds to `wallets`: `credit_limit`, `invert_balance`, and the visibility switches `is_hidden`,
`exclude_balance` and `hide_transactions`. Existing accounts keep showing as before.

Revision ID: a9d3f6b2c8e4
Revises: f4c7a2e9d6b1
Create Date: 2026-10-03 23:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a9d3f6b2c8e4"
down_revision: Union[str, Sequence[str], None] = "f4c7a2e9d6b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FLAGS = ("invert_balance", "is_hidden", "exclude_balance", "hide_transactions")


def upgrade() -> None:
    op.add_column("wallets", sa.Column("credit_limit", sa.Numeric(19, 4), nullable=True))
    for flag in FLAGS:
        op.add_column("wallets", sa.Column(flag, sa.Boolean(), server_default=sa.false(), nullable=False))


def downgrade() -> None:
    for flag in reversed(FLAGS):
        op.drop_column("wallets", flag)
    op.drop_column("wallets", "credit_limit")
