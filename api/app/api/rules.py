from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MerchantRuleRead
from app.services.auth import get_current_user_id
from app.services.categorization import rules as merchant_rules

router = APIRouter()


@router.get("", response_model=list[MerchantRuleRead])
def list_rules(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """The user's merchant rules, by merchant."""
    return merchant_rules.list_rules(user_id, db)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Forget a rule. Transactions keep their categories."""
    merchant_rules.delete_rule(merchant_rules.get_rule(rule_id, user_id, db), db)
