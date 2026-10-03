from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CategoryCreate, CategoryOrder, CategoryRead, CategoryUpdate
from app.services.auth import get_current_user_id
from app.services.authorization import get_category
from app.services.categories import (
    create_category,
    delete_category,
    read_for_user,
    to_read,
    update_category,
    user_overrides,
)
from app.services.category_order import set_group_order, visible_categories

router = APIRouter()


@router.get("", response_model=list[CategoryRead])
def list_categories(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List user's categories and system defaults (with the user's changes), in the user's order."""
    overrides = user_overrides(user_id, db)
    return [to_read(category, overrides.get(category.id)) for category in visible_categories(user_id, db)]


@router.put("/order", status_code=status.HTTP_204_NO_CONTENT)
def reorder_categories(
    order: CategoryOrder,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    """Put one group's categories in this order (drag and drop in Settings › Categories)."""
    set_group_order(order.category_ids, user_id, db)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(
    category_in: CategoryCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a category, or a group (`is_group`) to organize categories."""
    return to_read(create_category(category_in, user_id, db))


@router.get("/{category_id}", response_model=CategoryRead)
def get_category_endpoint(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return read_for_user(get_category(category_id, user_id, db, allow_system=True), user_id, db)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category_endpoint(
    category_id: int,
    category_in: CategoryUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Change a category or group. On a system one only `name` and `budget_by` change, for this user."""
    category = get_category(category_id, user_id, db, allow_system=True)
    update_category(category, category_in, user_id, db)
    db.refresh(category)
    return read_for_user(category, user_id, db)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_endpoint(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Delete a category, or a group with its categories; refused while they hold transactions.

    A system category is deleted for this user only.
    """
    delete_category(get_category(category_id, user_id, db, allow_system=True), user_id, db)
