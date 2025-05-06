from __future__ import annotations

from datetime import datetime


class Wallet:

    def __init__(self, *, balance: float = 0.0, history: list | None = None):
        self.balance = balance
        self.history = history if history is not None else []


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

    def __init__(self):
        ...
