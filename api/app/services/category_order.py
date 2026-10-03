"""The order of categories within their groups, chosen per user (Settings › Categories)."""

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session

from app.models import Category, CategoryOverride, CategoryPosition


class CategoryOrderError(HTTPException):
    """The new order must list exactly the categories of one group."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail)


def visible_categories(user_id: int, db: Session) -> list[Category]:
    """The user's categories and the system ones they haven't deleted, in the user's order.

    Categories the user placed come first, by position; the rest keep the default order (by ID),
    so a category created after a reorder lands at the end of its group.
    """
    position = CategoryPosition.position
    return list(
        db.scalars(
            select(Category)
            .outerjoin(
                CategoryPosition,
                and_(CategoryPosition.category_id == Category.id, CategoryPosition.user_id == user_id),
            )
            .where((Category.user_id == user_id) | (Category.user_id.is_(None)))
            .where(
                Category.id.not_in(
                    select(CategoryOverride.category_id).where(
                        CategoryOverride.user_id == user_id, CategoryOverride.is_hidden.is_(True)
                    )
                )
            )
            .order_by(position.is_(None), position, Category.id)
        )
    )


def set_group_order(category_ids: list[int], user_id: int, db: Session) -> None:
    """Save the order of one group's categories for this user.

    The list must hold every category of the group the user can see, each once: a partial
    list would leave the rest in an order nobody chose.
    """
    if len(set(category_ids)) != len(category_ids):
        raise CategoryOrderError("Each category can appear only once")

    visible = {category.id: category for category in visible_categories(user_id, db)}
    listed = [visible.get(category_id) for category_id in category_ids]
    if any(category is None for category in listed):
        raise CategoryOrderError("Unknown category")
    if any(category.is_group for category in listed):
        raise CategoryOrderError("Groups can't be reordered here")

    # Ungrouped categories (no parent) share a "group" per type
    first = listed[0]
    group = (first.parent_id, first.type)
    siblings = {
        category.id
        for category in visible.values()
        if not category.is_group and (category.parent_id, category.type) == group
    }
    if set(category_ids) != siblings:
        raise CategoryOrderError("List every category of one group, and only those")

    db.execute(
        delete(CategoryPosition).where(
            CategoryPosition.user_id == user_id, CategoryPosition.category_id.in_(category_ids)
        )
    )
    db.add_all(
        CategoryPosition(user_id=user_id, category_id=category_id, position=index)
        for index, category_id in enumerate(category_ids)
    )
    db.commit()
