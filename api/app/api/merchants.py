from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MerchantOrder, MerchantRead, MerchantSummary, MerchantUpdate
from app.services.auth import get_current_user_id
from app.services.authorization import get_merchant
from app.services.merchants import list_merchants, update_merchant

router = APIRouter()


@router.get("", response_model=list[MerchantSummary])
def list_user_merchants(
    order: MerchantOrder = MerchantOrder.TRANSACTION_COUNT,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """The user's merchants that have transactions, with their counts: most used first, or by name."""
    return list_merchants(user_id, order, db)


@router.patch("/{merchant_id}", response_model=MerchantRead)
def edit_merchant(
    merchant_id: int,
    changes: MerchantUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Edit merchant: its name everywhere (409 if another merchant goes by it) and its website."""
    return update_merchant(get_merchant(merchant_id, user_id, db), changes.name, changes.website, db)
