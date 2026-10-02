"""Merchant rules: the user's 'always put this merchant in this category' choices."""

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import Category, CategorySource, MerchantRule, Transaction
from app.services.authorization import NotFoundError, get_user_wallet_ids_subquery
from app.services.categorization.assignment import assign_category
from app.services.categorization.merchants import merchant_name


class NoMerchantError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="This transaction has no merchant, so there is nothing similar to match",
        )


@dataclass
class CategorizeOutcome:
    transaction: Transaction
    rule: MerchantRule | None
    # Other transactions of the same merchant moved to the rule's category
    similar_updated: int


def list_rules(user_id: int, db: Session) -> list[MerchantRule]:
    return list(
        db.scalars(select(MerchantRule).where(MerchantRule.user_id == user_id).order_by(MerchantRule.merchant_key))
    )


def get_rule(rule_id: int, user_id: int, db: Session) -> MerchantRule:
    rule = db.get(MerchantRule, rule_id)
    if rule is None or rule.user_id != user_id:
        raise NotFoundError("Rule")
    return rule


def _save_rule(user_id: int, transaction: Transaction, category_id: int, db: Session) -> MerchantRule:
    """Create the merchant's rule, or point the existing one to the new category."""
    rule = db.scalar(
        select(MerchantRule).where(
            MerchantRule.user_id == user_id, MerchantRule.merchant_key == transaction.merchant_key
        )
    )
    if rule is None:
        rule = MerchantRule(user_id=user_id, merchant_key=transaction.merchant_key)
        db.add(rule)
    rule.merchant_name = merchant_name(transaction.counterparty, transaction.description) or transaction.merchant_key
    rule.category_id = category_id
    db.flush()
    return rule


def _apply_rule(rule: MerchantRule, user_id: int, db: Session) -> int:
    """Move the merchant's automatically categorized transactions to the rule's category.

    Transactions the user categorized by hand keep their category: rules never override people.
    """
    result = db.execute(
        update(Transaction)
        .where(
            Transaction.wallet_id.in_(get_user_wallet_ids_subquery(user_id, db)),
            Transaction.merchant_key == rule.merchant_key,
            Transaction.category_source != CategorySource.MANUAL,
            Transaction.category_id != rule.category_id,
        )
        .values(category_id=rule.category_id, category_source=CategorySource.RULE)
        .execution_options(synchronize_session=False)
    )
    return result.rowcount


def categorize_transaction(
    transaction: Transaction, category: Category, apply_to_similar: bool, user_id: int, db: Session
) -> CategorizeOutcome:
    """Set the category the user picked; optionally remember it for the merchant's other transactions."""
    if apply_to_similar and transaction.merchant_key is None:
        raise NoMerchantError()

    assign_category(transaction, category.id, CategorySource.MANUAL)
    db.flush()
    rule = _save_rule(user_id, transaction, category.id, db) if apply_to_similar else None
    similar_updated = _apply_rule(rule, user_id, db) if rule else 0
    db.commit()
    db.refresh(transaction)
    if rule:
        db.refresh(rule)
    return CategorizeOutcome(transaction=transaction, rule=rule, similar_updated=similar_updated)


def delete_rule(rule: MerchantRule, db: Session) -> None:
    """Forget the rule. Transactions keep their categories; future imports fall back to the MCC."""
    db.delete(rule)
    db.commit()
