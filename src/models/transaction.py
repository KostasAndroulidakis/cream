from __future__ import annotations

from datetime import datetime
from typing import Any


class Transaction:

    def __init__(self, *, amount: float, category: str, entity: str, datetime: datetime, description: str):
        self.amount = amount
        self.category = category
        self.entity = entity
        self.datetime = datetime
        self.description = description


class Incoming(Transaction):

    def __init__(self, *, source: str, **kwargs: Any):
        super().__init__(entity = source, **kwargs)

    @property
    def source(self) -> str:
        return self.entity


class Outgoing(Transaction):

    def __init__(self, *, target: str, amount: float, **kwargs: Any):
        super().__init__(entity = target, amount = -amount, **kwargs)

    @property
    def target(self) -> str:
        return self.entity


class Salary(Incoming):

    ...
