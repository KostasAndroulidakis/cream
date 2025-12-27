from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryRead

router = APIRouter()


@router.get("", response_model=list[CategoryRead])
def list_categories(user_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Category)
    if user_id is not None:
        query = query.filter((Category.user_id == user_id) | (Category.user_id.is_(None)))
    else:
        query = query.filter(Category.user_id.is_(None))
    return query.all()


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(user_id: int, category_in: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(user_id=user_id, **category_in.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
