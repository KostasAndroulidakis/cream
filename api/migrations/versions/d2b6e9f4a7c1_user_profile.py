"""user profile

Adds the optional Settings › Profile fields to `users`: `display_name`, `birthday`, `timezone`.
Existing users start with none of them set.

Revision ID: d2b6e9f4a7c1
Revises: c9f4b2e8a6d1
Create Date: 2026-10-03 16:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "d2b6e9f4a7c1"
down_revision: Union[str, Sequence[str], None] = "c9f4b2e8a6d1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("display_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("birthday", sa.Date(), nullable=True))
    op.add_column("users", sa.Column("timezone", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "timezone")
    op.drop_column("users", "birthday")
    op.drop_column("users", "display_name")
