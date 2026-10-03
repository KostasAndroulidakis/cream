from datetime import datetime

from pydantic import BaseModel, Field

from app.models.category import CategoryType

NAME_MAX = 100
# One emoji, which can be several code points (e.g. a flag or a skin tone)
ICON_MAX = 16


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=NAME_MAX)
    type: CategoryType
    parent_id: int | None = None
    icon: str | None = Field(None, max_length=ICON_MAX)


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=NAME_MAX)
    parent_id: int | None = None
    icon: str | None = Field(None, max_length=ICON_MAX)


class CategoryRead(BaseModel):
    id: int
    name: str
    type: CategoryType
    parent_id: int | None
    key: str | None
    is_group: bool
    icon: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryOrder(BaseModel):
    """Every category of one group, in the order the user wants them."""

    category_ids: list[int] = Field(..., min_length=1)
