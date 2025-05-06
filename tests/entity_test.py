import unittest
from datetime import datetime
from src.models.entity import Entity, Person, Business, Government
from src.models.transaction import Transaction

class TestEntity(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now()
        self.transaction = Transaction(amount=100.0, entity="Test", datetime=self.now, description="Test transaction")

    def test_entity_creation(self):
        entity = Entity(name="Test Entity")
        self.assertEqual(entity.name, "Test Entity")
        self.assertEqual(entity.transaction_history, [])

    def test_add_transaction(self):
        entity = Entity(name="Test Entity")
        entity.add_transaction(self.transaction)
        self.assertEqual(len(entity.transaction_history), 1)
        self.assertEqual(entity.transaction_history[0], self.transaction)

    def test_person_entity(self):
        person = Person(name="John Doe", relationship="family")
        self.assertEqual(person.name, "John Doe")
        self.assertEqual(person.relationship, "family")
        self.assertTrue(person.is_individual)

    def test_business_entity(self):
        business = Business(name="ACME Corp", business_type="retail", website="acme.com")
        self.assertEqual(business.name, "ACME Corp")
        self.assertEqual(business.business_type, "retail")
        self.assertEqual(business.website, "acme.com")

    def test_government_entity(self):
        gov = Government(name="IRS", jurisdiction="federal", tax_related=True)
        self.assertEqual(gov.name, "IRS")
        self.assertEqual(gov.jurisdiction, "federal")
        self.assertTrue(gov.tax_related)

if __name__ == "__main__":
    unittest.main()