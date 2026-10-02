"""Common helper utilities.

Centralizes common patterns to ensure SSOT compliance.
"""

from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


def apply_update(model: T, schema: BaseModel) -> T:
    """Apply partial update from a Pydantic schema to a SQLAlchemy model.

    Only updates fields that were explicitly set in the schema.

    Args:
        model: The SQLAlchemy model instance to update
        schema: The Pydantic schema with update data

    Returns:
        The updated model instance

    Example:
        wallet = apply_update(wallet, wallet_update_schema)
    """
    for key, value in schema.model_dump(exclude_unset=True).items():
        setattr(model, key, value)
    return model
