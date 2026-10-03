"""account types and subtypes, as in Monarch

Replaces CREAM's own wallet types (bank, cash, digital, stash) with Monarch's types (cash, investment,
real estate, vehicle, valuables, other asset; credit card, mortgage, loan, other liability) and adds
`wallets.subtype`. Every existing wallet is a Cash account: bank -> Checking, digital -> PayPal;
cash and stash have no Monarch subtype, so they become Savings (the closest), changeable later.

Postgres can't use new enum values in the transaction that adds them, so the column moves to a new type.

Revision ID: c9f4b2e8a6d1
Revises: b8e3f1a7d2c5
Create Date: 2026-10-03 17:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c9f4b2e8a6d1"
down_revision: Union[str, Sequence[str], None] = "b8e3f1a7d2c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Frozen copies on purpose (see the categories migration)
OLD_TYPES = ("bank", "cash", "digital", "stash")
NEW_TYPES = (
    "cash", "investment", "real_estate", "vehicle", "valuables", "other_asset",
    "credit_card", "mortgage", "loan", "other_liability",
)
SUBTYPE_MAX = 50


def _replace_enum(values: tuple[str, ...], using: str) -> None:
    """Point wallets.type at a new `wallettype` enum with these values, converting with `using`."""
    op.execute("ALTER TYPE wallettype RENAME TO wallettype_previous")
    sa.Enum(*values, name="wallettype").create(op.get_bind())
    op.execute(f"ALTER TABLE wallets ALTER COLUMN type TYPE wallettype USING ({using})::wallettype")
    op.execute("DROP TYPE wallettype_previous")


def upgrade() -> None:
    op.add_column("wallets", sa.Column("subtype", sa.String(length=SUBTYPE_MAX), nullable=True))
    op.execute(
        "UPDATE wallets SET subtype = CASE type::text "
        "WHEN 'bank' THEN 'checking' WHEN 'digital' THEN 'paypal' ELSE 'savings' END"
    )
    op.alter_column("wallets", "subtype", nullable=False)
    _replace_enum(NEW_TYPES, "'cash'")


def downgrade() -> None:
    # Only cash accounts map back; everything else becomes the old "bank"
    _replace_enum(
        OLD_TYPES,
        "CASE WHEN type::text <> 'cash' THEN 'bank' "
        "WHEN subtype = 'paypal' THEN 'digital' WHEN subtype = 'savings' THEN 'stash' ELSE 'bank' END",
    )
    op.drop_column("wallets", "subtype")
