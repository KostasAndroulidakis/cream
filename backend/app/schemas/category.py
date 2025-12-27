from datetime import datetime

from pydantic import BaseModel

from app.models.category import CategoryType


class CategoryCreate(BaseModel):
    name: str
    type: CategoryType
    parent_id: int | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    type: CategoryType
    parent_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
