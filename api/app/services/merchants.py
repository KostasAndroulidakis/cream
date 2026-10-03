"""The user's merchants: found by name, created the first time a name appears."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Merchant, Transaction
from app.services.categorization.merchants import merchant_name_key, tidy_merchant_name


class MerchantDirectory:
    """Holds one user's merchants in memory, so a sync makes no per-row queries."""

    def __init__(self, user_id: int, merchants_by_key: dict[str, Merchant]):
        self._user_id = user_id
        self._by_key = merchants_by_key

    @classmethod
    def for_user(cls, user_id: int, db: Session) -> MerchantDirectory:
        merchants = db.scalars(select(Merchant).where(Merchant.user_id == user_id))
        return cls(user_id, {merchant.key: merchant for merchant in merchants})

    @classmethod
    def for_name(cls, user_id: int, name: str, db: Session) -> MerchantDirectory:
        """Only the merchant with this name, if it exists: enough for one edit."""
        tidy_name = tidy_merchant_name(name)
        if tidy_name is None:
            return cls(user_id, {})
        key = merchant_name_key(tidy_name)
        merchant = db.scalar(select(Merchant).where(Merchant.user_id == user_id, Merchant.key == key))
        return cls(user_id, {key: merchant} if merchant else {})

    def get_or_create(self, name: str | None, db: Session) -> Merchant | None:
        """The user's merchant with this name (in any case or spacing), new if there is none yet."""
        tidy_name = tidy_merchant_name(name)
        if tidy_name is None:
            return None
        key = merchant_name_key(tidy_name)
        merchant = self._by_key.get(key)
        if merchant is None:
            merchant = Merchant(user_id=self._user_id, name=tidy_name, key=key)
            db.add(merchant)
            self._by_key[key] = merchant
        return merchant


def list_merchants(user_id: int, db: Session) -> list[Merchant]:
    """The user's merchants that have transactions, by name (a merchant left with none drops out)."""
    has_transactions = select(Transaction.id).where(Transaction.merchant_id == Merchant.id).exists()
    query = select(Merchant).where(Merchant.user_id == user_id, has_transactions).order_by(Merchant.key)
    return list(db.scalars(query))
