from __future__ import annotations

from transaction import Transaction


# TODO: Add exception handling

class Wallet:

    def __init__(self, *, balance: float = 0.0, history: list[Transaction] | None = None):
        self.history = history if history is not None else []
        self.initial_balance = balance

    @property
    def balance(self) -> float:
        return sum(transaction.amount for transaction in self.history)

    def add_transaction(self, transaction: Transaction):
        """Add a transaction to history and update balance"""
        self.history.append(transaction)

    def remove_transaction(self, transaction: Transaction):
        """Remove a transaction and update balance"""
        if transaction in self.history:
            self.history.remove(transaction)
