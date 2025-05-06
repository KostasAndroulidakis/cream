import unittest
from datetime import datetime
from src.models.wallet import Wallet
from src.models.transaction import Incoming, Outgoing



class TestWallet(unittest.TestCase):
    def setUp(self):
        self.wallet = Wallet(balance=100.0)
        self.income = Incoming(amount=50.0, source="Employer", datetime=datetime.now(), description="Salary")
        self.expense = Outgoing(amount=30.0, target="Store", datetime=datetime.now(), description="Groceries")

    def test_initial_balance(self):
        self.assertEqual(self.wallet.get_balance(), 100.0)

    def test_add_transaction(self):
        self.wallet.add_transaction(self.income)
        self.assertEqual(self.wallet.get_balance(), 150.0)

        self.wallet.add_transaction(self.expense)
        self.assertEqual(self.wallet.get_balance(), 120.0)

    def test_remove_transaction(self):
        self.wallet.add_transaction(self.income)
        self.wallet.add_transaction(self.expense)

        self.wallet.remove_transaction(self.expense)
        self.assertEqual(self.wallet.get_balance(), 150.0)

        self.wallet.remove_transaction(self.income)
        self.assertEqual(self.wallet.get_balance(), 100.0)

    def test_recalculate_balance(self):
        self.wallet.add_transaction(self.income)
        self.wallet.add_transaction(self.expense)

        # Manually change balance to wrong value
        self.wallet.balance = 0

        # Recalculate should fix it
        self.wallet.recalculate_balance()
        self.assertEqual(self.wallet.get_balance(), 120.0)

if __name__ == "__main__":
    unittest.main()