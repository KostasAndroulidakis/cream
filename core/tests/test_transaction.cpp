#include <gtest/gtest.h>
#include "transaction.hpp"

using namespace cream;

// =============================================================================
// Construction Tests
// =============================================================================

TEST(Transaction, DefaultConstruction) {
    Transaction tx;
    EXPECT_EQ(tx.id, 0);
    EXPECT_EQ(tx.wallet_id, 0);
    EXPECT_EQ(tx.category_id, 0);
    EXPECT_TRUE(tx.amount.is_zero());
    EXPECT_TRUE(tx.description.empty());
}

TEST(Transaction, ParameterizedConstruction) {
    auto now = std::chrono::system_clock::now();
    Money amount = Money::from_double(100.50);

    Transaction tx(1, 2, 3, amount, "Test transaction", now);

    EXPECT_EQ(tx.id, 1);
    EXPECT_EQ(tx.wallet_id, 2);
    EXPECT_EQ(tx.category_id, 3);
    EXPECT_EQ(tx.amount, amount);
    EXPECT_EQ(tx.description, "Test transaction");
    EXPECT_EQ(tx.occurred_at, now);
}

// =============================================================================
// Income/Expense Classification Tests
// =============================================================================

TEST(Transaction, IsIncomeWithPositiveAmount) {
    Transaction tx;
    tx.amount = Money::from_double(50.00);

    EXPECT_TRUE(tx.is_income());
    EXPECT_FALSE(tx.is_expense());
}

TEST(Transaction, IsExpenseWithNegativeAmount) {
    Transaction tx;
    tx.amount = Money::from_double(-50.00);

    EXPECT_FALSE(tx.is_income());
    EXPECT_TRUE(tx.is_expense());
}

TEST(Transaction, ZeroAmountIsNeitherIncomeNorExpense) {
    Transaction tx;
    tx.amount = Money();  // Zero

    EXPECT_FALSE(tx.is_income());
    EXPECT_FALSE(tx.is_expense());
}

TEST(Transaction, SmallPositiveIsIncome) {
    Transaction tx;
    tx.amount = Money::from_raw(1);  // 0.0001

    EXPECT_TRUE(tx.is_income());
    EXPECT_FALSE(tx.is_expense());
}

TEST(Transaction, SmallNegativeIsExpense) {
    Transaction tx;
    tx.amount = Money::from_raw(-1);  // -0.0001

    EXPECT_FALSE(tx.is_income());
    EXPECT_TRUE(tx.is_expense());
}

// =============================================================================
// Field Modification Tests
// =============================================================================

TEST(Transaction, CanModifyFields) {
    Transaction tx;

    tx.id = 42;
    tx.wallet_id = 10;
    tx.category_id = 5;
    tx.amount = Money::from_double(200.00);
    tx.description = "Updated";
    tx.occurred_at = std::chrono::system_clock::now();

    EXPECT_EQ(tx.id, 42);
    EXPECT_EQ(tx.wallet_id, 10);
    EXPECT_EQ(tx.category_id, 5);
    EXPECT_DOUBLE_EQ(tx.amount.to_double(), 200.00);
    EXPECT_EQ(tx.description, "Updated");
}

TEST(Transaction, DescriptionWithSpecialCharacters) {
    Transaction tx;
    tx.description = "Café & Restaurant — 50% off!";

    EXPECT_EQ(tx.description, "Café & Restaurant — 50% off!");
}

TEST(Transaction, EmptyDescription) {
    Transaction tx(1, 1, 1, Money::from_double(10.00), "", std::chrono::system_clock::now());

    EXPECT_TRUE(tx.description.empty());
}
