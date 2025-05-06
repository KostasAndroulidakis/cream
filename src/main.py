from __future__ import annotations

from datetime import datetime


class Wallet:

    def __init__(self, *, balance: float = 0.0, history: list | None = None):
        self.balance = balance
        self.history = history if history is not None else []

    def add_transaction(self, transaction):
        """Add a transaction to history and update balance"""
        self.history.append(transaction)

        # Update balance based on transaction type
        if isinstance(transaction, Incoming):
            self.balance += transaction.amount
        elif isinstance(transaction, Outgoing):
            self.balance -= transaction.amount

        return transaction

    def remove_transaction(self, transaction):
        """Remove a transaction and update balance"""
        if transaction in self.history:
            self.history.remove(transaction)

            # Reverse the balance effect
            if isinstance(transaction, Incoming):
                self.balance -= transaction.amount
            elif isinstance(transaction, Outgoing):
                self.balance += transaction.amount

            return True
        return False

    def get_balance(self) -> float:
        """Return current balance"""
        return self.balance

    def recalculate_balance(self) -> float:
        """Verify balance matches transaction history"""
        # Start with zero balance
        calculated_balance = 0.0

        # Add up all transactions
        for transaction in self.history:
            if isinstance(transaction, Incoming):
                calculated_balance += transaction.amount
            elif isinstance(transaction, Outgoing):
                calculated_balance -= transaction.amount

        # Update the stored balance
        self.balance = calculated_balance
        return self.balance


class Transaction:

    def __init__(self, *, amount: float, entity: str, datetime: datetime, description: str):
        self.amount = amount
        self.entity = entity
        self.datetime = datetime
        self.description = description


class Incoming(Transaction):

    def __init__(self, *, source: str, **kwargs):
        super().__init__(entity = source, **kwargs)

    @property
    def source(self) -> str:
        return self.entity


class Outgoing(Transaction):

    def __init__(self, *, target: str, **kwargs):
        super().__init__(entity = target, **kwargs)

    @property
    def target(self) -> str:
        return self.entity


class Salary(Incoming):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Entity():

    def __init__(self, name: str):
        self.name = name
        self.transaction_history = []

    def add_transaction(self, transaction):
        self.transaction_history.append(transaction)


class Person(Entity):
    def __init__(self, name: str, relationship: str = "other", **kwargs):
        super().__init__(name=name, **kwargs)
        self.relationship = relationship  # family, friend, colleague, etc.
        self.is_individual = True


class Business(Entity):
    def __init__(self, name: str, business_type: str = "", website: str = "", **kwargs):
        super().__init__(name=name, **kwargs)
        self.business_type = business_type  # retail, service, utility, etc.
        self.website = website


class Government(Entity):
    def __init__(self, name: str, jurisdiction: str = "", tax_related: bool = False, **kwargs):
        super().__init__(name=name, **kwargs)
        self.jurisdiction = jurisdiction  # federal, state, local
        self.tax_related = tax_related