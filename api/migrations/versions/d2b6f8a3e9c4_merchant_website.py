"""merchant website: the user's choice of where a merchant's logo comes from

Adds `merchants.website` (a domain, e.g. "wolt.com"). Empty for everyone: known merchants get the
catalog's website without it (services/merchant_catalog.py).

Revision ID: d2b6f8a3e9c4
Revises: c7e1a9d4f2b8
Create Date: 2026-10-04 11:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "d2b6f8a3e9c4"
down_revision: Union[str, Sequence[str], None] = "c7e1a9d4f2b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Frozen here (app.services.websites.WEBSITE_MAX at the time)
WEBSITE_MAX = 255


def upgrade() -> None:
    op.add_column("merchants", sa.Column("website", sa.String(length=WEBSITE_MAX), nullable=True))


def downgrade() -> None:
    op.drop_column("merchants", "website")
