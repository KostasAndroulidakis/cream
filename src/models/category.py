from __future__ import annotations

from transaction import Transaction


class Category:

    def __init__(
        self,
        name: str,
        type: str,
        parent: Category | None = None,
        description: str = "",
    ):
        """Initialize a Category object.

        Args:
            name: Name of the category
            type: Type of category (e.g., 'income', 'expense', 'loan', 'debt')
            parent: Parent category if this is a subcategory
            description: Optional description of the category
        """
        self.name = name
        self.type = type
        self.description = description
        self.parent = parent
        self.children: list[Category] = []
        self.transactions: list[Transaction] = []

        # If this is a subcategory, add it to parent's subcategories
        if parent:
            parent.add_subcategory(self)

    def add_subcategory(self, subcategory: Category):
        """Add a subcategory to this category"""
        if subcategory not in self.children:
            self.children.append(subcategory)

    def add_transaction(self, transaction: Transaction):
        """Add a transaction to this category"""
        self.transactions.append(transaction)

    def get_all_transactions(self):
        """Get all transactions for this category and its subcategories"""
        all_transactions = self.transactions.copy()

        for subcategory in self.children:
            all_transactions.extend(subcategory.get_all_transactions())

        return all_transactions
