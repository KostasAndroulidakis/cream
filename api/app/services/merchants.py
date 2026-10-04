"""The user's merchants: found by any of their names, created the first time a name appears."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models import Merchant, MerchantAlias, Transaction
from app.schemas.merchant import MerchantOrder, MerchantSummary
from app.services.categorization.merchants import merchant_name_key, tidy_merchant_name
from app.services.merchant_catalog import known_merchant_name
from app.services.websites import InvalidWebsiteError, website_domain


class MerchantNameTakenError(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another merchant is already called {name}. Use Merge & delete to combine them.",
        )


class MerchantInUseError(HTTPException):
    def __init__(self, transaction_count: int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{transaction_count} transactions are still tied to this merchant. "
            "Choose a merchant to move them to.",
        )


class SelfMergeError(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="A merchant can't merge into itself")


class MerchantDirectory:
    """Holds one user's merchants by alias in memory, so a sync makes no per-row queries."""

    def __init__(self, user_id: int, merchants_by_key: dict[str, Merchant]):
        self._user_id = user_id
        self._by_key = merchants_by_key

    @classmethod
    def for_user(cls, user_id: int, db: Session) -> MerchantDirectory:
        aliases = db.scalars(select(MerchantAlias).where(MerchantAlias.user_id == user_id))
        return cls(user_id, {alias.key: alias.merchant for alias in aliases})

    @classmethod
    def for_name(cls, user_id: int, name: str, db: Session) -> MerchantDirectory:
        """Only the merchant with this name, if it exists: enough for one edit."""
        tidy_name = tidy_merchant_name(name)
        if tidy_name is None:
            return cls(user_id, {})
        key = merchant_name_key(tidy_name)
        merchant = _merchant_named(user_id, key, db)
        return cls(user_id, {key: merchant} if merchant else {})

    def get_or_create(self, name: str | None, db: Session) -> Merchant | None:
        """The user's merchant known by this name (in any case or spacing), new if there is none yet."""
        tidy_name = tidy_merchant_name(name)
        if tidy_name is None:
            return None
        key = merchant_name_key(tidy_name)
        merchant = self._by_key.get(key)
        if merchant is None:
            merchant = Merchant(user_id=self._user_id, name=tidy_name)
            merchant.aliases.append(MerchantAlias(user_id=self._user_id, key=key))
            db.add(merchant)
            self._by_key[key] = merchant
        return merchant

    def from_bank(self, bank_text: str | None, db: Session) -> Merchant | None:
        """The merchant behind the bank's text, for an import.

        A text the user already gave a merchant (by renaming or merging) stays theirs; else a known
        merchant's spelling joins that merchant ("efood*019cc…" → efood); else it's a merchant of its own.
        """
        tidy_text = tidy_merchant_name(bank_text)
        if tidy_text is None:
            return None
        key = merchant_name_key(tidy_text)
        proper_name = known_merchant_name(tidy_text)
        if key in self._by_key or proper_name is None:
            return self.get_or_create(tidy_text, db)
        merchant = self.get_or_create(proper_name, db)
        if key not in self._by_key:
            # The spelling now means this merchant, as if merged into it
            merchant.aliases.append(MerchantAlias(user_id=self._user_id, key=key))
            self._by_key[key] = merchant
        return merchant


def _merchant_named(user_id: int, key: str, db: Session) -> Merchant | None:
    alias = db.scalar(select(MerchantAlias).where(MerchantAlias.user_id == user_id, MerchantAlias.key == key))
    return alias.merchant if alias else None


def update_merchant(merchant: Merchant, name: str, website: str | None, db: Session) -> Merchant:
    """Edit merchant: its name, and its website (empty: the catalog's, if it knows the merchant).

    The merchant's old names keep meaning it, so imports still find it: the new name becomes one of
    its aliases. A name another merchant goes by is refused: that's a merge.
    """
    try:
        domain = website_domain(website) if website and website.strip() else None
    except InvalidWebsiteError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error
    tidy_name = tidy_merchant_name(name)
    if tidy_name is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Give the merchant a name")
    key = merchant_name_key(tidy_name)
    owner = _merchant_named(merchant.user_id, key, db)
    if owner is not None and owner.id != merchant.id:
        raise MerchantNameTakenError(owner.name)
    if owner is None:
        merchant.aliases.append(MerchantAlias(user_id=merchant.user_id, key=key))
    merchant.name = tidy_name
    merchant.website = domain
    db.commit()
    db.refresh(merchant)
    return merchant


def delete_merchant(merchant: Merchant, move_to: Merchant | None, db: Session) -> None:
    """Merge & delete: the merchant's transactions and names go to `move_to`, then it's deleted.

    Its names keep meaning the merchant it merged into, so later imports land there too. Without a
    merchant to move to, only a merchant with no transactions can go (as in Monarch).
    """
    if move_to is None:
        transaction_count = _transaction_count(merchant, db)
        if transaction_count:
            raise MerchantInUseError(transaction_count)
    elif move_to.id == merchant.id:
        raise SelfMergeError()
    else:
        _move_relations(merchant, move_to, db)
    db.delete(merchant)
    db.commit()


def _transaction_count(merchant: Merchant, db: Session) -> int:
    return db.scalar(select(func.count(Transaction.id)).where(Transaction.merchant_id == merchant.id)) or 0


def _move_relations(source: Merchant, target: Merchant, db: Session) -> None:
    """Everything tied to `source` (its transactions and its names) now belongs to `target`."""
    db.execute(update(Transaction).where(Transaction.merchant_id == source.id).values(merchant_id=target.id))
    for alias in list(source.aliases):
        alias.merchant = target


def list_merchants(user_id: int, order: MerchantOrder, db: Session) -> list[MerchantSummary]:
    """The user's merchants that have transactions, with how many (a merchant left with none drops out).

    By transaction count, most first, or alphabetically; ties and equal counts go by name.
    """
    count = func.count(Transaction.id).label("transaction_count")
    by_name = func.lower(Merchant.name)
    query = (
        select(Merchant, count)
        .join(Transaction, Transaction.merchant_id == Merchant.id)
        .where(Merchant.user_id == user_id)
        .group_by(Merchant.id)
    )
    if order is MerchantOrder.TRANSACTION_COUNT:
        query = query.order_by(count.desc(), by_name)
    else:
        query = query.order_by(by_name)
    return [
        MerchantSummary(
            id=merchant.id, name=merchant.name, shown_website=merchant.shown_website, transaction_count=transactions
        )
        for merchant, transactions in db.execute(query)
    ]
