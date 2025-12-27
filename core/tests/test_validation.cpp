#include <gtest/gtest.h>
#include "validation.hpp"
#include <chrono>

using namespace cream;

// Helper to create timestamps
static Timestamp make_timestamp(int days_offset) {
    return std::chrono::system_clock::now() + std::chrono::hours(24 * days_offset);
}

// Helper to create a valid transaction
static Transaction make_valid_transaction() {
    Transaction tx;
    tx.id = 1;
    tx.wallet_id = 1;
    tx.category_id = 1;
    tx.amount = Money::from_double(50.00);
    tx.description = "Valid";
    tx.occurred_at = make_timestamp(-1);  // Yesterday
    return tx;
}

// =============================================================================
// ValidationError Tests
// =============================================================================

TEST(ValidationError, Construction) {
    ValidationError err("amount", "Amount is invalid");

    EXPECT_EQ(err.field, "amount");
    EXPECT_EQ(err.message, "Amount is invalid");
}

// =============================================================================
// ValidationResult Tests
// =============================================================================

TEST(ValidationResult, DefaultIsValid) {
    ValidationResult result;

    EXPECT_TRUE(result.is_valid());
    EXPECT_TRUE(result.valid);
    EXPECT_TRUE(result.errors.empty());
}

TEST(ValidationResult, AddErrorMakesInvalid) {
    ValidationResult result;

    result.add_error("field1", "Error 1");

    EXPECT_FALSE(result.is_valid());
    EXPECT_FALSE(result.valid);
    EXPECT_EQ(result.errors.size(), 1);
    EXPECT_EQ(result.errors[0].field, "field1");
    EXPECT_EQ(result.errors[0].message, "Error 1");
}

TEST(ValidationResult, MultipleErrors) {
    ValidationResult result;

    result.add_error("field1", "Error 1");
    result.add_error("field2", "Error 2");

    EXPECT_FALSE(result.is_valid());
    EXPECT_EQ(result.errors.size(), 2);
}

// =============================================================================
// TransactionValidator - Valid Transaction Tests
// =============================================================================

TEST(TransactionValidator, ValidTransactionPasses) {
    TransactionValidator validator;
    Transaction tx = make_valid_transaction();

    ValidationResult result = validator.validate(tx);

    EXPECT_TRUE(result.is_valid());
    EXPECT_TRUE(result.errors.empty());
}

TEST(TransactionValidator, ValidNegativeAmountPasses) {
    TransactionValidator validator;
    Transaction tx = make_valid_transaction();
    tx.amount = Money::from_double(-50.00);  // Expense

    ValidationResult result = validator.validate(tx);

    EXPECT_TRUE(result.is_valid());
}

// =============================================================================
// TransactionValidator - Amount Validation Tests
// =============================================================================

TEST(TransactionValidator, ZeroAmountFails) {
    TransactionValidator validator;
    Transaction tx = make_valid_transaction();
    tx.amount = Money();  // Zero

    ValidationResult result = validator.validate(tx);

    EXPECT_FALSE(result.is_valid());
    EXPECT_EQ(result.errors[0].field, "amount");
}

TEST(TransactionValidator, BelowMinAmountFails) {
    TransactionValidator validator;
    validator.set_min_amount(Money::from_double(10.00));

    Transaction tx = make_valid_transaction();
    tx.amount = Money::from_double(5.00);  // Below min

    ValidationResult result = validator.validate(tx);

    EXPECT_FALSE(result.is_valid());
    // Should have error about being below minimum
    bool found = false;
    for (const auto& err : result.errors) {
        if (err.field == "amount" && err.message.find("below") != std::string::npos) {
            found = true;
        }
    }
    EXPECT_TRUE(found);
}

TEST(TransactionValidator, AboveMaxAmountFails) {
    TransactionValidator validator;
    validator.set_max_amount(Money::from_double(100.00));

    Transaction tx = make_valid_transaction();
    tx.amount = Money::from_double(200.00);  // Above max

    ValidationResult result = validator.validate(tx);

    EXPECT_FALSE(result.is_valid());
    // Should have error about exceeding maximum
    bool found = false;
    for (const auto& err : result.errors) {
        if (err.field == "amount" && err.message.find("exceeds") != std::string::npos) {
            found = true;
        }
    }
    EXPECT_TRUE(found);
}

TEST(TransactionValidator, SmallestValidAmountPasses) {
    TransactionValidator validator;
    Transaction tx = make_valid_transaction();
    tx.amount = Money::from_raw(1);  // 0.0001 - default minimum

    ValidationResult result = validator.validate(tx);

    EXPECT_TRUE(result.is_valid());
}

// =============================================================================
// TransactionValidator - Date Validation Tests
// =============================================================================

TEST(TransactionValidator, FutureDateFailsByDefault) {
    TransactionValidator validator;
    Transaction tx = make_valid_transaction();
    tx.occurred_at = make_timestamp(5);  // 5 days in future

    ValidationResult result = validator.validate(tx);

    EXPECT_FALSE(result.is_valid());
    EXPECT_EQ(result.errors[0].field, "occurred_at");
}

TEST(TransactionValidator, FutureDatePassesWhenAllowed) {
    TransactionValidator validator;
    validator.set_allow_future_dates(true);

    Transaction tx = make_valid_transaction();
    tx.occurred_at = make_timestamp(5);  // 5 days in future

    ValidationResult result = validator.validate(tx);

    EXPECT_TRUE(result.is_valid());
}

TEST(TransactionValidator, PastDateAlwaysPasses) {
    TransactionValidator validator;
    Transaction tx = make_valid_transaction();
    tx.occurred_at = make_timestamp(-365);  // 1 year ago

    ValidationResult result = validator.validate(tx);

    EXPECT_TRUE(result.is_valid());
}

// =============================================================================
// TransactionValidator - ID Validation Tests
// =============================================================================

TEST(TransactionValidator, InvalidWalletIdFails) {
    TransactionValidator validator;
    Transaction tx = make_valid_transaction();
    tx.wallet_id = 0;

    ValidationResult result = validator.validate(tx);

    EXPECT_FALSE(result.is_valid());
    EXPECT_EQ(result.errors[0].field, "wallet_id");
}

TEST(TransactionValidator, NegativeWalletIdFails) {
    TransactionValidator validator;
    Transaction tx = make_valid_transaction();
    tx.wallet_id = -1;

    ValidationResult result = validator.validate(tx);

    EXPECT_FALSE(result.is_valid());
    EXPECT_EQ(result.errors[0].field, "wallet_id");
}

TEST(TransactionValidator, InvalidCategoryIdFails) {
    TransactionValidator validator;
    Transaction tx = make_valid_transaction();
    tx.category_id = 0;

    ValidationResult result = validator.validate(tx);

    EXPECT_FALSE(result.is_valid());
    EXPECT_EQ(result.errors[0].field, "category_id");
}

TEST(TransactionValidator, NegativeCategoryIdFails) {
    TransactionValidator validator;
    Transaction tx = make_valid_transaction();
    tx.category_id = -1;

    ValidationResult result = validator.validate(tx);

    EXPECT_FALSE(result.is_valid());
    EXPECT_EQ(result.errors[0].field, "category_id");
}

// =============================================================================
// TransactionValidator - Builder Pattern Tests
// =============================================================================

TEST(TransactionValidator, BuilderPatternChaining) {
    TransactionValidator validator;

    // Should return reference for chaining
    auto& ref = validator
        .set_min_amount(Money::from_double(1.00))
        .set_max_amount(Money::from_double(1000.00))
        .set_allow_future_dates(true);

    EXPECT_EQ(&ref, &validator);
}

TEST(TransactionValidator, CustomMinMaxRange) {
    TransactionValidator validator;
    validator.set_min_amount(Money::from_double(10.00));
    validator.set_max_amount(Money::from_double(100.00));

    Transaction txBelow = make_valid_transaction();
    txBelow.amount = Money::from_double(5.00);

    Transaction txWithin = make_valid_transaction();
    txWithin.amount = Money::from_double(50.00);

    Transaction txAbove = make_valid_transaction();
    txAbove.amount = Money::from_double(150.00);

    EXPECT_FALSE(validator.validate(txBelow).is_valid());
    EXPECT_TRUE(validator.validate(txWithin).is_valid());
    EXPECT_FALSE(validator.validate(txAbove).is_valid());
}

// =============================================================================
// TransactionValidator - Multiple Errors Tests
// =============================================================================

TEST(TransactionValidator, CollectsMultipleErrors) {
    TransactionValidator validator;

    Transaction tx;
    tx.id = 1;
    tx.wallet_id = 0;      // Invalid
    tx.category_id = 0;    // Invalid
    tx.amount = Money();   // Zero - invalid
    tx.occurred_at = make_timestamp(5);  // Future - invalid

    ValidationResult result = validator.validate(tx);

    EXPECT_FALSE(result.is_valid());
    EXPECT_GE(result.errors.size(), 3);  // At least 3 errors
}

// =============================================================================
// Convenience Function Tests
// =============================================================================

TEST(TransactionValidator, ConvenienceFunctionWorks) {
    Transaction valid = make_valid_transaction();
    Transaction invalid = make_valid_transaction();
    invalid.amount = Money();  // Zero

    EXPECT_TRUE(validate_transaction(valid).is_valid());
    EXPECT_FALSE(validate_transaction(invalid).is_valid());
}
