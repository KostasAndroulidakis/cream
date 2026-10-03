"""hidden transactions

Adds `transactions.is_hidden`: hidden transactions stay in the wallet balance but are left
out of lists and statistics. Existing transactions start visible.

Revision ID: f1a7c3e9b2d4
Revises: e5f2a8c4d1b9
Create Date: 2026-10-03 10:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "f1a7c3e9b2d4"
down_revision: Union[str, Sequence[str], None] = "e5f2a8c4d1b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column("is_hidden", sa.Boolean(), server_default=sa.false(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("transactions", "is_hidden")
