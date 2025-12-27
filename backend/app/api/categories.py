from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryRead
from app.services.auth import get_current_user_id

router = APIRouter()


def get_accessible_category(category_id: int, user_id: int, db: Session) -> Category:
    """Helper to get a category and verify access.

    System default categories (user_id is None) are accessible to all.
    User categories are only accessible to their owner.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.user_id is not None and category.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return category


def get_user_category(category_id: int, user_id: int, db: Session) -> Category:
    """Helper to get a user-owned category (not system defaults)."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.user_id is None:
        raise HTTPException(status_code=403, detail="Cannot modify system default category")
    if category.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return category


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
    category = Category(user_id=user_id, **category_in.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return get_accessible_category(category_id, user_id, db)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    category = get_user_category(category_id, user_id, db)
    db.delete(category)
    db.commit()
