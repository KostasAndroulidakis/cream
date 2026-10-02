from datetime import datetime

from pydantic import BaseModel

from app.schemas.transaction import TransactionRead


class CategorizeRequest(BaseModel):
    category_id: int
    # Also remember the choice for this merchant: past automatic categories and future imports
    apply_to_similar: bool = False


class MerchantRuleRead(BaseModel):
    id: int
    merchant_name: str
    category_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CategorizeResultRead(BaseModel):
    transaction: TransactionRead
    # The merchant's rule, when apply_to_similar was requested
    rule: MerchantRuleRead | None
    # Other transactions of the merchant moved to this category
    similar_updated: int

    model_config = {"from_attributes": True}
