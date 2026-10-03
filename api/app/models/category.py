from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, utc_now

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.transaction import Transaction


class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    # Money moving between your own wallets: excluded from income and expense totals
    TRANSFER = "transfer"


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("key", name="uq_categories_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[CategoryType]
    # Stable identifier of a system category (e.g. "food_and_dining.groceries"); used for
    # translations and automatic categorization. NULL for user-created categories.
    key: Mapped[str | None] = mapped_column(String(100))
    # Groups organize categories; transactions are always recorded in a non-group category
    is_group: Mapped[bool] = mapped_column(default=False, server_default=false())
    # An emoji shown next to the name, as in Monarch
    icon: Mapped[str | None] = mapped_column(String(16), default=None)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)

    user: Mapped["User | None"] = relationship(back_populates="categories")
    parent: Mapped["Category | None"] = relationship(back_populates="children", remote_side="Category.id")
    children: Mapped[list["Category"]] = relationship(back_populates="parent")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")


class CategoryPosition(Base):
    """Where a user put a category within its group (Settings › Categories, drag and drop).

    Per user, because system categories are shared: one user's order never moves another's.
    Categories without a row keep the default order, after the ones that have one.
    """

    __tablename__ = "category_positions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    position: Mapped[int]
