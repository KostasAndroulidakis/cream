"""Pick a category for imported transactions: the user's merchant rule, then the MCC, then Uncategorized."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CategorySource, MerchantRule, Transaction
from app.services.categorization.assignment import assign_category
from app.services.categorization.mcc import MCC_CATEGORY_KEYS, category_key_for_mcc
from app.services.categorization.system_categories import (
    UNCATEGORIZED_KEY,
    hidden_category_ids,
    system_category_id,
    system_category_ids,
)


@dataclass(frozen=True)
class Decision:
    category_id: int
    source: CategorySource

    @property
    def is_categorized(self) -> bool:
        return self.source is not CategorySource.DEFAULT


class AutoCategorizer:
    """Holds one user's rules and the MCC categories in memory, so a sync makes no per-row queries."""

    def __init__(self, rules: dict[str, int], mcc_category_ids: dict[str, int], uncategorized_id: int):
        self._rules = rules
        self._mcc_category_ids = mcc_category_ids
        self._uncategorized = Decision(uncategorized_id, CategorySource.DEFAULT)

    @classmethod
    def for_user(cls, user_id: int, db: Session) -> AutoCategorizer:
        rules = db.execute(
            select(MerchantRule.merchant_key, MerchantRule.category_id).where(MerchantRule.user_id == user_id)
        )
        # A system category the user deleted never receives transactions
        hidden = hidden_category_ids(user_id, db)
        mcc_category_ids = {
            key: category_id
            for key, category_id in system_category_ids(MCC_CATEGORY_KEYS, db).items()
            if category_id not in hidden
        }
        return cls(
            rules={key: category_id for key, category_id in rules},
            mcc_category_ids=mcc_category_ids,
            uncategorized_id=system_category_id(UNCATEGORIZED_KEY, db),
        )

    def decide(self, merchant_key: str | None, mcc: str | None) -> Decision:
        if merchant_key is not None and merchant_key in self._rules:
            return Decision(self._rules[merchant_key], CategorySource.RULE)
        mcc_category_id = self._mcc_category_ids.get(category_key_for_mcc(mcc) or "")
        if mcc_category_id is not None:
            return Decision(mcc_category_id, CategorySource.MCC)
        return self._uncategorized

    def retry_uncategorized(self, wallet_id: int, db: Session) -> int:
        """Categorize the wallet's transactions still in Uncategorized; returns how many found a category.

        They may have been imported before a matching rule or MCC mapping existed.
        """
        waiting = db.scalars(
            select(Transaction).where(
                Transaction.wallet_id == wallet_id, Transaction.category_source == CategorySource.DEFAULT
            )
        )
        categorized = 0
        for transaction in waiting:
            decision = self.decide(transaction.merchant_key, transaction.merchant_category_code)
            if decision.is_categorized:
                assign_category(transaction, decision.category_id, decision.source)
                categorized += 1
        return categorized
