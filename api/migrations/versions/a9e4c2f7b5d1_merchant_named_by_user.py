"""merchant named by user: names the user chose, which known merchants never gather

Adds `merchants.named_by_user`. Existing merchants count as the user's when their name is none of their
transactions' bank texts (renamed in Edit merchant, or typed in); the rest still carry a bank's text.

Revision ID: a9e4c2f7b5d1
Revises: d2b6f8a3e9c4
Create Date: 2026-10-04 14:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "a9e4c2f7b5d1"
down_revision: Union[str, Sequence[str], None] = "d2b6f8a3e9c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# A bank-named merchant is named after a transaction's bank text (the counterparty, else the
# description), tidied as the import tidies it: spacing collapsed, case aside
_MARK_USER_NAMED = r"""
UPDATE merchants SET named_by_user = true
WHERE NOT EXISTS (
    SELECT 1 FROM transactions
    WHERE transactions.merchant_id = merchants.id
      AND lower(regexp_replace(
            btrim(coalesce(nullif(transactions.counterparty, ''), transactions.description, '')), '\s+', ' ', 'g'
          )) = lower(merchants.name)
)
"""


def upgrade() -> None:
    op.add_column(
        "merchants", sa.Column("named_by_user", sa.Boolean(), nullable=False, server_default=sa.false())
    )
    op.execute(_MARK_USER_NAMED)


def downgrade() -> None:
    op.drop_column("merchants", "named_by_user")
