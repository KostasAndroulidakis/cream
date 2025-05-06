from __future__ import annotations


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