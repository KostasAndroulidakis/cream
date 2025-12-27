from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.auth import get_current_user_id
from app.services.authorization import get_category, verify_category_access
from app.services.helpers import apply_update

router = APIRouter()


@router.get("", response_model=list[CategoryRead])
def list_categories(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """List user's categories and system defaults."""
    return db.query(Category).filter(
        (Category.user_id == user_id) | (Category.user_id.is_(None))
    ).all()


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # Verify user has access to the parent category if specified
    if category_in.parent_id is not None:
        verify_category_access(category_in.parent_id, user_id, db)

    category = Category(user_id=user_id, **category_in.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryRead)
def get_category_endpoint(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return get_category(category_id, user_id, db, allow_system=True)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    category = get_category(category_id, user_id, db, require_ownership=True)

    # Verify user has access to the new parent category if being changed
    update_data = category_in.model_dump(exclude_unset=True)
    if "parent_id" in update_data and update_data["parent_id"] is not None:
        verify_category_access(update_data["parent_id"], user_id, db)

    apply_update(category, category_in)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    category = get_category(category_id, user_id, db, require_ownership=True)
    db.delete(category)
    db.commit()
