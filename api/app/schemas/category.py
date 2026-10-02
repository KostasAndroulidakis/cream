from datetime import datetime

from pydantic import BaseModel, Field

from app.models.category import CategoryType

NAME_MAX = 100


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=NAME_MAX)
    type: CategoryType
    parent_id: int | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=NAME_MAX)
    parent_id: int | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    type: CategoryType
    parent_id: int | None
    key: str | None
    is_group: bool
    created_at: datetime

    model_config = {"from_attributes": True}
