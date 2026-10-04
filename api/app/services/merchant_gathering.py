"""Known merchants gather their bank spellings, also among merchants imported before the catalog knew them.

Monarch never has this backlog: Plaid names every transaction's merchant on the way in. CREAM's catalog
grows over time, so what it learns must also reach the transactions already imported.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Merchant
from app.services.categorization.merchants import merchant_name_key
from app.services.merchant_catalog import known_merchant_name
from app.services.merchants import merchant_named, merge_into, rename_merchant


def gather_known_merchants(user_id: int, db: Session) -> None:
    """Each merchant still under a known merchant's bank spelling ("Wolt*Wolt*Athens") joins that merchant,
    as Merge & delete would, or takes its proper name ("Wolt") when the user has none by it yet.

    Merchants the user named stay as they are, and so do go-betweens' texts ("Cash at Alpha Bank").
    No transaction is added or removed: they only point at the merchant they belong to.
    """
    bank_named = db.scalars(
        select(Merchant).where(Merchant.user_id == user_id, Merchant.named_by_user.is_(False)).order_by(Merchant.id)
    ).all()
    for merchant in bank_named:
        proper_name = known_merchant_name(merchant.name)
        if proper_name is None or proper_name == merchant.name:
            continue
        target = merchant_named(user_id, merchant_name_key(proper_name), db)
        if target is None or target.id == merchant.id:
            rename_merchant(merchant, proper_name, db)
        else:
            merge_into(merchant, target, db)
        # The sessions don't autoflush: the next merchant's lookup must see this one's new name
        db.flush()
    db.commit()
