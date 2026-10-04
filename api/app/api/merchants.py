from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MerchantOrder, MerchantRead, MerchantSummary, MerchantUpdate
from app.services.auth import get_current_user_id
from app.services.authorization import get_merchant
from app.services.merchants import delete_merchant, list_merchants, update_merchant

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


@router.delete("/{merchant_id}", status_code=status.HTTP_204_NO_CONTENT)
def merge_and_delete_merchant(
    merchant_id: int,
    move_to: int | None = None,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Merge & delete: its transactions and names move to merchant `move_to`, then it's deleted.

    `move_to` may be left out only when the merchant has no transactions (409 otherwise).
    """
    merchant = get_merchant(merchant_id, user_id, db)
    target = get_merchant(move_to, user_id, db) if move_to is not None else None
    delete_merchant(merchant, target, db)
