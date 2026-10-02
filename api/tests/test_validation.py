"""Tests for transaction validation service."""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app.services.validation import (
    ValidationError,
    ValidationResult,
    TransactionValidator,
    validate_transaction,
)


class TestValidationError:
    """Tests for ValidationError dataclass."""

    def test_creation(self):
        """Test ValidationError creation."""
        error = ValidationError(field="amount", message="Amount must not be zero")
        assert error.field == "amount"
        assert error.message == "Amount must not be zero"


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_empty_result_is_valid(self):
        """Test that empty result is valid."""
        result = ValidationResult()
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_add_error_makes_invalid(self):
        """Test that adding an error makes result invalid."""
        result = ValidationResult()
        result.add_error("field", "message")
        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_multiple_errors(self):
        """Test multiple errors."""
        result = ValidationResult()
        result.add_error("field1", "message1")
        result.add_error("field2", "message2")
        assert result.is_valid is False
        assert len(result.errors) == 2


class TestTransactionValidatorAmount:
    """Tests for amount validation."""

    def test_valid_positive_amount(self):
        """Test valid positive amount (income)."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is True

    def test_valid_negative_amount(self):
        """Test valid negative amount (expense)."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("-50.00"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is True

    def test_zero_amount_fails(self):
        """Test that zero amount fails validation."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("0"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is False
        assert any(e.field == "amount" for e in result.errors)
        assert any("zero" in e.message.lower() for e in result.errors)

    def test_amount_below_minimum_fails(self):
        """Test that amount below minimum fails."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("0.00001"),  # Below 0.0001
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is False
        assert any(e.field == "amount" for e in result.errors)

    def test_amount_at_minimum_passes(self):
        """Test that amount at minimum passes."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("0.0001"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is True

    def test_negative_amount_at_minimum_passes(self):
        """Test that negative amount at minimum passes."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("-0.0001"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is True

    def test_amount_above_maximum_fails(self):
        """Test that amount above maximum fails."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("9999999999.9999"),  # Above max
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is False
        assert any(e.field == "amount" for e in result.errors)

    def test_amount_at_maximum_passes(self):
        """Test that amount at maximum passes."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("999999999.9999"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is True

    def test_custom_min_amount(self):
        """Test custom minimum amount."""
        validator = TransactionValidator().set_min_amount(Decimal("1.00"))
        result = validator.validate(
            amount=Decimal("0.50"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is False

    def test_custom_max_amount(self):
        """Test custom maximum amount."""
        validator = TransactionValidator().set_max_amount(Decimal("100.00"))
        result = validator.validate(
            amount=Decimal("150.00"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is False


class TestTransactionValidatorDate:
    """Tests for date validation."""

    def test_past_date_passes(self):
        """Test that past date passes."""
        validator = TransactionValidator()
        past = datetime.now(timezone.utc) - timedelta(days=30)
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=past,
        )
        assert result.is_valid is True

    def test_current_date_passes(self):
        """Test that current date passes."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is True

    def test_future_date_fails(self):
        """Test that future date fails by default."""
        validator = TransactionValidator()
        future = datetime.now(timezone.utc) + timedelta(days=1)
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=future,
        )
        assert result.is_valid is False
        assert any(e.field == "occurred_at" for e in result.errors)
        assert any("future" in e.message.lower() for e in result.errors)

    def test_future_date_allowed_when_configured(self):
        """Test that future date passes when allowed."""
        validator = TransactionValidator().set_allow_future_dates(True)
        future = datetime.now(timezone.utc) + timedelta(days=1)
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=future,
        )
        assert result.is_valid is True

    def test_naive_datetime_handled(self):
        """Test that naive datetime is handled correctly."""
        validator = TransactionValidator()
        past = datetime.now() - timedelta(days=1)  # Naive datetime
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=past,
        )
        assert result.is_valid is True


class TestTransactionValidatorIds:
    """Tests for ID validation."""

    def test_valid_wallet_id(self):
        """Test valid wallet ID."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=datetime.now(timezone.utc),
            wallet_id=1,
        )
        assert result.is_valid is True

    def test_zero_wallet_id_fails(self):
        """Test that zero wallet ID fails."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=datetime.now(timezone.utc),
            wallet_id=0,
        )
        assert result.is_valid is False
        assert any(e.field == "wallet_id" for e in result.errors)

    def test_negative_wallet_id_fails(self):
        """Test that negative wallet ID fails."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=datetime.now(timezone.utc),
            wallet_id=-1,
        )
        assert result.is_valid is False
        assert any(e.field == "wallet_id" for e in result.errors)

    def test_valid_category_id(self):
        """Test valid category ID."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=datetime.now(timezone.utc),
            category_id=1,
        )
        assert result.is_valid is True

    def test_zero_category_id_fails(self):
        """Test that zero category ID fails."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=datetime.now(timezone.utc),
            category_id=0,
        )
        assert result.is_valid is False
        assert any(e.field == "category_id" for e in result.errors)

    def test_negative_category_id_fails(self):
        """Test that negative category ID fails."""
        validator = TransactionValidator()
        result = validator.validate(
            amount=Decimal("100.00"),
            occurred_at=datetime.now(timezone.utc),
            category_id=-1,
        )
        assert result.is_valid is False
        assert any(e.field == "category_id" for e in result.errors)


class TestTransactionValidatorMultiple:
    """Tests for multiple validation errors."""

    def test_multiple_errors_collected(self):
        """Test that multiple errors are collected."""
        validator = TransactionValidator()
        future = datetime.now(timezone.utc) + timedelta(days=1)
        result = validator.validate(
            amount=Decimal("0"),
            occurred_at=future,
            wallet_id=0,
            category_id=-1,
        )
        assert result.is_valid is False
        assert len(result.errors) >= 3  # amount, occurred_at, wallet_id, category_id


class TestTransactionValidatorBuilder:
    """Tests for builder pattern."""

    def test_builder_chaining(self):
        """Test that builder methods can be chained."""
        validator = (
            TransactionValidator()
            .set_min_amount(Decimal("1.00"))
            .set_max_amount(Decimal("1000.00"))
            .set_allow_future_dates(True)
        )

        # Should fail on min amount
        result = validator.validate(
            amount=Decimal("0.50"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is False

        # Should pass with valid amount
        result = validator.validate(
            amount=Decimal("500.00"),
            occurred_at=datetime.now(timezone.utc) + timedelta(days=1),  # Future allowed
        )
        assert result.is_valid is True


class TestValidateTransactionFunction:
    """Tests for convenience function."""

    def test_valid_transaction(self):
        """Test valid transaction with convenience function."""
        result = validate_transaction(
            amount=Decimal("100.00"),
            occurred_at=datetime.now(timezone.utc),
            wallet_id=1,
            category_id=1,
        )
        assert result.is_valid is True

    def test_invalid_transaction(self):
        """Test invalid transaction with convenience function."""
        result = validate_transaction(
            amount=Decimal("0"),
            occurred_at=datetime.now(timezone.utc),
        )
        assert result.is_valid is False
