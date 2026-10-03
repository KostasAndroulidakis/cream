"""investment subtypes: only those held in Greece

The catalog keeps Brokerage, Cryptocurrency, Mutual Fund, Pension, Stock Plan and Other for investments
(the US/UK/Canada-only ones are gone). An account left with a removed subtype becomes Other.
Downgrade has nothing to undo: Other is valid before and after.

Revision ID: b3e8d1f5a7c2
Revises: a9d3f6b2c8e4
Create Date: 2026-10-03 21:30:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b3e8d1f5a7c2"
down_revision: Union[str, Sequence[str], None] = "a9d3f6b2c8e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Frozen here: the migration must not change if the catalog changes later
KEPT = ("brokerage", "crypto_exchange", "mutual_fund", "pension", "stock_plan", "other")


def upgrade() -> None:
    statement = sa.text(
        "UPDATE wallets SET subtype = 'other' WHERE type::text = 'investment' AND subtype NOT IN :kept"
    ).bindparams(sa.bindparam("kept", expanding=True))
    op.get_bind().execute(statement, {"kept": list(KEPT)})


def downgrade() -> None:
    pass
