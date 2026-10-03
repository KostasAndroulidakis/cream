from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MerchantRead
from app.services.auth import get_current_user_id
from app.services.merchants import list_merchants

router = APIRouter()


@router.get("", response_model=list[MerchantRead])
def list_user_merchants(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """The user's merchants that have transactions, by name."""
    return list_merchants(user_id, db)
