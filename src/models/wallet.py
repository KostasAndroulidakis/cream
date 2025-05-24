from __future__ import annotations

from transaction import Incoming, Outgoing, Transaction


class Wallet:

    def __init__(self, *, balance: float = 0.0, history: list[Transaction] | None = None):
        self.balance = balance
        self.history = history if history is not None else []
        self.initial_balance = balance

    def add_transaction(self, transaction: Transaction):
        """Add a transaction to history and update balance"""
        self.history.append(transaction)

        # Update balance based on transaction type
        if isinstance(transaction, Incoming):
            self.balance += transaction.amount

        elif isinstance(transaction, Outgoing):
            self.balance -= transaction.amount

        return transaction

    def remove_transaction(self, transaction: Transaction):
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
        """Verify balance matches transaction history plus initial balance"""
        # Start with initial balance
        calculated_balance = self.initial_balance

        # Add up all transactions
        for transaction in self.history:
            if isinstance(transaction, Incoming):
                calculated_balance += transaction.amount

            elif isinstance(transaction, Outgoing):
                calculated_balance -= transaction.amount

        # Update the stored balance
        self.balance = calculated_balance

        return self.balance
