import unittest
from datetime import datetime
from src.models.transaction import Transaction, Incoming, Outgoing, Salary

class TestTransaction(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now()

    def test_base_transaction(self):
        t = Transaction(amount=100.0, entity="Test", datetime=self.now, description="Test transaction")
        self.assertEqual(t.amount, 100.0)
        self.assertEqual(t.entity, "Test")
        self.assertEqual(t.datetime, self.now)
        self.assertEqual(t.description, "Test transaction")

    def test_incoming_transaction(self):
        income = Incoming(amount=200.0, source="Employer", datetime=self.now, description="Salary")
        self.assertEqual(income.amount, 200.0)
        self.assertEqual(income.entity, "Employer")
        self.assertEqual(income.source, "Employer")  # Testing the property accessor

    def test_outgoing_transaction(self):
        expense = Outgoing(amount=50.0, target="Store", datetime=self.now, description="Groceries")
        self.assertEqual(expense.amount, 50.0)
        self.assertEqual(expense.entity, "Store")
        self.assertEqual(expense.target, "Store")  # Testing the property accessor

    def test_salary_transaction(self):
        salary = Salary(amount=1000.0, source="Company", datetime=self.now, description="Monthly salary")
        self.assertEqual(salary.amount, 1000.0)
        self.assertEqual(salary.source, "Company")
        # Verify Salary is a subclass of Incoming
        self.assertTrue(isinstance(salary, Incoming))

if __name__ == "__main__":
    unittest.main()