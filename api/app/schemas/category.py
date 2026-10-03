from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.category import BudgetBy, CategoryType

NAME_MAX = 100
# One emoji, which can be several code points (e.g. a flag or a skin tone)
ICON_MAX = 16


def _strip(value):
    return value.strip() if isinstance(value, str) else value


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=NAME_MAX)
    type: CategoryType
    parent_id: int | None = None
    icon: str | None = Field(None, max_length=ICON_MAX)
    # A group organizes categories; it has no parent and holds no transactions
    is_group: bool = False
    # Groups only; a new group budgets category by category unless told otherwise
    budget_by: BudgetBy | None = None
    # Categories only
    exclude_from_budget: bool = False

    _strip_name = field_validator("name", mode="before")(_strip)


class CategoryUpdate(BaseModel):
    """Fields left out stay as they are. For system categories, only `name` and `budget_by` can change."""

    name: str | None = Field(None, min_length=1, max_length=NAME_MAX)
    parent_id: int | None = None
    icon: str | None = Field(None, max_length=ICON_MAX)
    budget_by: BudgetBy | None = None
    exclude_from_budget: bool | None = None

    _strip_name = field_validator("name", mode="before")(_strip)


class CategoryRead(BaseModel):
    id: int
    # The user's own name for a system category, when they renamed it
    name: str
    type: CategoryType
    parent_id: int | None
    key: str | None
    is_group: bool
    icon: str | None
    budget_by: BudgetBy | None
    exclude_from_budget: bool
    # False for system categories: shared, so only some of their fields can change (per user)
    is_custom: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryOrder(BaseModel):
    """Every category of one group, in the order the user wants them."""

    category_ids: list[int] = Field(..., min_length=1)
