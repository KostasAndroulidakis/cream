"""bank connections, bank accounts and imported transaction fields

Revision ID: c3d9a1f0e7b2
Revises: b7c1e2d4f5a6
Create Date: 2026-10-02 23:45:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "c3d9a1f0e7b2"
down_revision: Union[str, Sequence[str], None] = "b7c1e2d4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

connection_status = sa.Enum("pending", "active", "expired", name="connectionstatus")


def upgrade() -> None:
    op.create_table(
        "bank_connections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("aspsp_name", sa.String(length=255), nullable=False),
        sa.Column("aspsp_country", sa.String(length=2), nullable=False),
        sa.Column("status", connection_status, nullable=False),
        sa.Column("auth_state", sa.String(length=64), nullable=True),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("auth_state"),
    )
    op.create_index(op.f("ix_bank_connections_user_id"), "bank_connections", ["user_id"], unique=False)

    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("uid", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("iban_last4", sa.String(length=4), nullable=True),
        sa.Column("wallet_id", sa.Integer(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["bank_connections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uid"),
        sa.UniqueConstraint("wallet_id"),
    )
    op.create_index(op.f("ix_bank_accounts_connection_id"), "bank_accounts", ["connection_id"], unique=False)

    op.add_column("transactions", sa.Column("external_id", sa.String(length=255), nullable=True))
    op.add_column("transactions", sa.Column("counterparty", sa.String(length=255), nullable=True))
    op.add_column("transactions", sa.Column("merchant_category_code", sa.String(length=4), nullable=True))
    op.create_unique_constraint(
        "uq_transactions_wallet_external_id", "transactions", ["wallet_id", "external_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_transactions_wallet_external_id", "transactions", type_="unique")
    op.drop_column("transactions", "merchant_category_code")
    op.drop_column("transactions", "counterparty")
    op.drop_column("transactions", "external_id")
    op.drop_index(op.f("ix_bank_accounts_connection_id"), table_name="bank_accounts")
    op.drop_table("bank_accounts")
    op.drop_index(op.f("ix_bank_connections_user_id"), table_name="bank_connections")
    op.drop_table("bank_connections")
    connection_status.drop(op.get_bind(), checkfirst=True)
