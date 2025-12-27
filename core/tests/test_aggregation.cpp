#include <gtest/gtest.h>
#include "aggregation.hpp"
#include <chrono>

using namespace cream;

// Helper to create timestamps
static Timestamp make_timestamp(int days_offset) {
    return std::chrono::system_clock::now() + std::chrono::hours(24 * days_offset);
}

// Helper to create a transaction
static Transaction make_tx(int64_t id, int64_t wallet_id, int64_t category_id,
                           double amount, int days_offset = 0) {
    Transaction tx;
    tx.id = id;
    tx.wallet_id = wallet_id;
    tx.category_id = category_id;
    tx.amount = Money::from_double(amount);
    tx.occurred_at = make_timestamp(days_offset);
    return tx;
}

// =============================================================================
// sum_by_category Tests
// =============================================================================

TEST(Aggregation, SumByCategoryEmpty) {
    std::vector<Transaction> txs;
    auto result = sum_by_category(txs);
    EXPECT_TRUE(result.empty());
}

TEST(Aggregation, SumByCategorySingleCategory) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00),
        make_tx(2, 1, 1, 50.00),
        make_tx(3, 1, 1, -30.00),
    };

    auto result = sum_by_category(txs);

    EXPECT_EQ(result.size(), 1);
    EXPECT_DOUBLE_EQ(result[1].to_double(), 120.00);  // 100 + 50 - 30
}

TEST(Aggregation, SumByCategoryMultipleCategories) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00),
        make_tx(2, 1, 2, 200.00),
        make_tx(3, 1, 1, 50.00),
        make_tx(4, 1, 3, -75.00),
    };

    auto result = sum_by_category(txs);

    EXPECT_EQ(result.size(), 3);
    EXPECT_DOUBLE_EQ(result[1].to_double(), 150.00);
    EXPECT_DOUBLE_EQ(result[2].to_double(), 200.00);
    EXPECT_DOUBLE_EQ(result[3].to_double(), -75.00);
}

// =============================================================================
// sum_by_wallet Tests
// =============================================================================

TEST(Aggregation, SumByWalletEmpty) {
    std::vector<Transaction> txs;
    auto result = sum_by_wallet(txs);
    EXPECT_TRUE(result.empty());
}

TEST(Aggregation, SumByWalletMultipleWallets) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00),
        make_tx(2, 2, 1, 200.00),
        make_tx(3, 1, 1, -50.00),
        make_tx(4, 2, 1, 75.00),
    };

    auto result = sum_by_wallet(txs);

    EXPECT_EQ(result.size(), 2);
    EXPECT_DOUBLE_EQ(result[1].to_double(), 50.00);   // 100 - 50
    EXPECT_DOUBLE_EQ(result[2].to_double(), 275.00);  // 200 + 75
}

// =============================================================================
// total_income Tests
// =============================================================================

TEST(Aggregation, TotalIncomeEmpty) {
    std::vector<Transaction> txs;
    Money result = total_income(txs);
    EXPECT_TRUE(result.is_zero());
}

TEST(Aggregation, TotalIncomeOnlyPositive) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00),
        make_tx(2, 1, 1, 200.00),
        make_tx(3, 1, 1, -50.00),  // Expense - ignored
    };

    Money result = total_income(txs);
    EXPECT_DOUBLE_EQ(result.to_double(), 300.00);
}

TEST(Aggregation, TotalIncomeNoIncome) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, -100.00),
        make_tx(2, 1, 1, -50.00),
    };

    Money result = total_income(txs);
    EXPECT_TRUE(result.is_zero());
}

// =============================================================================
// total_expenses Tests
// =============================================================================

TEST(Aggregation, TotalExpensesEmpty) {
    std::vector<Transaction> txs;
    Money result = total_expenses(txs);
    EXPECT_TRUE(result.is_zero());
}

TEST(Aggregation, TotalExpensesOnlyNegative) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, -100.00),
        make_tx(2, 1, 1, -50.00),
        make_tx(3, 1, 1, 200.00),  // Income - ignored
    };

    Money result = total_expenses(txs);
    EXPECT_DOUBLE_EQ(result.to_double(), 150.00);  // Absolute values
}

TEST(Aggregation, TotalExpensesNoExpenses) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00),
        make_tx(2, 1, 1, 50.00),
    };

    Money result = total_expenses(txs);
    EXPECT_TRUE(result.is_zero());
}

// =============================================================================
// sum_in_period Tests
// =============================================================================

TEST(Aggregation, SumInPeriodEmpty) {
    std::vector<Transaction> txs;
    auto start = make_timestamp(-10);
    auto end = make_timestamp(0);

    Money result = sum_in_period(txs, start, end);
    EXPECT_TRUE(result.is_zero());
}

TEST(Aggregation, SumInPeriodFiltersCorrectly) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00, -15),  // Before range
        make_tx(2, 1, 1, 200.00, -5),   // In range
        make_tx(3, 1, 1, 300.00, -3),   // In range
        make_tx(4, 1, 1, 400.00, 5),    // After range
    };

    auto start = make_timestamp(-10);
    auto end = make_timestamp(0);

    Money result = sum_in_period(txs, start, end);
    EXPECT_DOUBLE_EQ(result.to_double(), 500.00);  // 200 + 300
}

TEST(Aggregation, SumInPeriodIncludesBoundaries) {
    auto time1 = make_timestamp(-5);
    auto time2 = make_timestamp(-3);

    std::vector<Transaction> txs = {
        Transaction(1, 1, 1, Money::from_double(100.00), "", time1),
        Transaction(2, 1, 1, Money::from_double(200.00), "", time2),
    };

    Money result = sum_in_period(txs, time1, time2);
    EXPECT_DOUBLE_EQ(result.to_double(), 300.00);
}

// =============================================================================
// income_in_period Tests
// =============================================================================

TEST(Aggregation, IncomeInPeriod) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00, -5),   // Income in range
        make_tx(2, 1, 1, -50.00, -5),   // Expense in range - ignored
        make_tx(3, 1, 1, 200.00, -3),   // Income in range
        make_tx(4, 1, 1, 300.00, -15),  // Income before range - ignored
    };

    auto start = make_timestamp(-10);
    auto end = make_timestamp(0);

    Money result = income_in_period(txs, start, end);
    EXPECT_DOUBLE_EQ(result.to_double(), 300.00);  // 100 + 200
}

// =============================================================================
// expenses_in_period Tests
// =============================================================================

TEST(Aggregation, ExpensesInPeriod) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, -100.00, -5),  // Expense in range
        make_tx(2, 1, 1, 50.00, -5),    // Income in range - ignored
        make_tx(3, 1, 1, -200.00, -3),  // Expense in range
        make_tx(4, 1, 1, -300.00, -15), // Expense before range - ignored
    };

    auto start = make_timestamp(-10);
    auto end = make_timestamp(0);

    Money result = expenses_in_period(txs, start, end);
    EXPECT_DOUBLE_EQ(result.to_double(), 300.00);  // 100 + 200 (absolute)
}

// =============================================================================
// count_by_category Tests
// =============================================================================

TEST(Aggregation, CountByCategoryEmpty) {
    std::vector<Transaction> txs;
    auto result = count_by_category(txs);
    EXPECT_TRUE(result.empty());
}

TEST(Aggregation, CountByCategoryMultiple) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00),
        make_tx(2, 1, 2, 200.00),
        make_tx(3, 1, 1, 50.00),
        make_tx(4, 1, 1, 75.00),
        make_tx(5, 1, 3, 25.00),
    };

    auto result = count_by_category(txs);

    EXPECT_EQ(result.size(), 3);
    EXPECT_EQ(result[1], 3);
    EXPECT_EQ(result[2], 1);
    EXPECT_EQ(result[3], 1);
}

// =============================================================================
// average_amount Tests
// =============================================================================

TEST(Aggregation, AverageAmountEmpty) {
    std::vector<Transaction> txs;
    Money result = average_amount(txs);
    EXPECT_TRUE(result.is_zero());
}

TEST(Aggregation, AverageAmountSingle) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00),
    };

    Money result = average_amount(txs);
    EXPECT_DOUBLE_EQ(result.to_double(), 100.00);
}

TEST(Aggregation, AverageAmountMultiple) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00),
        make_tx(2, 1, 1, 200.00),
        make_tx(3, 1, 1, 300.00),
    };

    Money result = average_amount(txs);
    EXPECT_DOUBLE_EQ(result.to_double(), 200.00);  // (100 + 200 + 300) / 3
}

TEST(Aggregation, AverageAmountUsesAbsoluteValues) {
    std::vector<Transaction> txs = {
        make_tx(1, 1, 1, 100.00),
        make_tx(2, 1, 1, -100.00),
    };

    Money result = average_amount(txs);
    EXPECT_DOUBLE_EQ(result.to_double(), 100.00);  // (100 + 100) / 2
}
