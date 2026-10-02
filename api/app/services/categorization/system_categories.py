"""Look up the seeded system categories by their stable keys."""

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category

# Imported transactions land here until the user (or a rule) categorizes them
UNCATEGORIZED_KEY = "other.uncategorized"


class MissingSystemCategoryError(RuntimeError):
    def __init__(self, key: str):
        super().__init__(f"System category '{key}' is missing; run the migrations")


def system_category_ids(keys: Iterable[str], db: Session) -> dict[str, int]:
    """IDs of the system categories with these keys (keys that don't exist are left out)."""
    rows = db.execute(select(Category.key, Category.id).where(Category.user_id.is_(None), Category.key.in_(set(keys))))
    return {key: category_id for key, category_id in rows}


def system_category_id(key: str, db: Session) -> int:
    category_id = system_category_ids([key], db).get(key)
    if category_id is None:
        raise MissingSystemCategoryError(key)
    return category_id
