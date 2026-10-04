"""transfer category source: transactions paired with their other side in another account

Adds 'transfer' to `categorysource`: a transaction filed as a transfer because CREAM found the same
money leaving one of the user's accounts and arriving in another (categorization/transfers.py).

Revision ID: b5d8e1a3c7f2
Revises: a9e4c2f7b5d1
Create Date: 2026-10-04 16:00:00

"""
from typing import Sequence, Union

from alembic import op


revision: str = "b5d8e1a3c7f2"
down_revision: Union[str, Sequence[str], None] = "a9e4c2f7b5d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # A new enum value must be committed before rows can use it
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE categorysource ADD VALUE IF NOT EXISTS 'transfer'")


def downgrade() -> None:
    # Postgres can't drop a single enum value; 'transfer' stays in the type (harmless). Paired
    # transactions keep their Transfer category, now as if the user had chosen it
    op.execute("UPDATE transactions SET category_source = 'manual' WHERE category_source = 'transfer'")
