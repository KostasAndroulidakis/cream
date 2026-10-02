"""The single place that sets a transaction's category, always together with its source."""

from app.models import CategorySource, Transaction


def assign_category(transaction: Transaction, category_id: int, source: CategorySource) -> None:
    transaction.category_id = category_id
    transaction.category_source = source
