"""Transaction validation service.

Implements business rules for transaction validation:
- Amount must not be zero
- Amount must be within allowed range
- Date must not be in the future
- IDs must be positive
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional


@dataclass
class ValidationError:
    """A single validation error."""
    field: str
    message: str


@dataclass
class ValidationResult:
    """Result of validation containing any errors."""
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, field_name: str, message: str) -> None:
        self.errors.append(ValidationError(field=field_name, message=message))


class TransactionValidator:
    """Validates transactions according to business rules.

    Default configuration:
    - min_amount: 0.0001 (minimum precision for NUMERIC(19,4))
    - max_amount: 999,999,999.9999
    - allow_future_dates: False

    Usage:
        validator = TransactionValidator()
        result = validator.validate(amount, occurred_at, wallet_id, category_id)
        if not result.is_valid:
            raise ValidationException(result.errors)

    Builder pattern for custom configuration:
        validator = (TransactionValidator()
            .set_min_amount(Decimal("1.00"))
            .set_max_amount(Decimal("10000.00"))
            .set_allow_future_dates(True))
    """

    DEFAULT_MIN_AMOUNT = Decimal("0.0001")
    DEFAULT_MAX_AMOUNT = Decimal("999999999.9999")

    def __init__(self):
        self._min_amount = self.DEFAULT_MIN_AMOUNT
        self._max_amount = self.DEFAULT_MAX_AMOUNT
        self._allow_future_dates = False

    def set_min_amount(self, amount: Decimal) -> "TransactionValidator":
        """Set minimum allowed absolute amount."""
        self._min_amount = amount
        return self

    def set_max_amount(self, amount: Decimal) -> "TransactionValidator":
        """Set maximum allowed absolute amount."""
        self._max_amount = amount
        return self

    def set_allow_future_dates(self, allow: bool) -> "TransactionValidator":
        """Set whether future dates are allowed."""
        self._allow_future_dates = allow
        return self

    def validate(
        self,
        amount: Decimal,
        occurred_at: datetime,
        wallet_id: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> ValidationResult:
        """Validate transaction data.

        Args:
            amount: Transaction amount (positive for income, negative for expense)
            occurred_at: When the transaction occurred
            wallet_id: Optional wallet ID to validate
            category_id: Optional category ID to validate

        Returns:
            ValidationResult with any validation errors
        """
        result = ValidationResult()

        # Amount validation
        self._validate_amount(amount, result)

        # Date validation
        self._validate_date(occurred_at, result)

        # ID validation (if provided)
        if wallet_id is not None:
            self._validate_wallet_id(wallet_id, result)

        if category_id is not None:
            self._validate_category_id(category_id, result)

        return result

    def _validate_amount(self, amount: Decimal, result: ValidationResult) -> None:
        """Validate amount according to business rules."""
        # Amount must not be zero
        if amount == Decimal("0"):
            result.add_error("amount", "Amount must not be zero")
            return

        # Check absolute value against bounds
        abs_amount = abs(amount)

        if abs_amount < self._min_amount:
            result.add_error(
                "amount",
                f"Amount must be at least {self._min_amount}"
            )

        if abs_amount > self._max_amount:
            result.add_error(
                "amount",
                f"Amount must not exceed {self._max_amount}"
            )

    def _validate_date(self, occurred_at: datetime, result: ValidationResult) -> None:
        """Validate date according to business rules."""
        if self._allow_future_dates:
            return

        # Ensure datetime is timezone-aware for comparison
        now = datetime.now(timezone.utc)

        # Convert naive datetime to UTC if needed
        if occurred_at.tzinfo is None:
            # Assume naive datetime is UTC
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        if occurred_at > now:
            result.add_error("occurred_at", "Transaction date cannot be in the future")

    def _validate_wallet_id(self, wallet_id: int, result: ValidationResult) -> None:
        """Validate wallet ID."""
        if wallet_id <= 0:
            result.add_error("wallet_id", "Wallet ID must be a positive integer")

    def _validate_category_id(self, category_id: int, result: ValidationResult) -> None:
        """Validate category ID."""
        if category_id <= 0:
            result.add_error("category_id", "Category ID must be a positive integer")


def validate_transaction(
    amount: Decimal,
    occurred_at: datetime,
    wallet_id: Optional[int] = None,
    category_id: Optional[int] = None,
) -> ValidationResult:
    """Convenience function to validate a transaction with default settings.

    Args:
        amount: Transaction amount
        occurred_at: When the transaction occurred
        wallet_id: Optional wallet ID
        category_id: Optional category ID

    Returns:
        ValidationResult with any validation errors
    """
    validator = TransactionValidator()
    return validator.validate(amount, occurred_at, wallet_id, category_id)
