#include <gtest/gtest.h>
#include "ledger.hpp"
#include <chrono>

using namespace cream;

// Helper to create timestamps
Timestamp make_timestamp(int days_offset) {
    return std::chrono::system_clock::now() + std::chrono::hours(24 * days_offset);
}

// =============================================================================
// Construction Tests
// =============================================================================

TEST(Ledger, DefaultConstructionIsEmpty) {
    Ledger ledger;
    EXPECT_TRUE(ledger.transactions().empty());
    EXPECT_TRUE(ledger.wallets().empty());
    EXPECT_TRUE(ledger.categories().empty());
}

// =============================================================================
// Add and Retrieve Tests
// =============================================================================

TEST(Ledger, AddAndRetrieveTransactions) {
    Ledger ledger;

    Transaction tx1(1, 1, 1, Money::from_double(100.00), "First", make_timestamp(0));
    Transaction tx2(2, 1, 1, Money::from_double(200.00), "Second", make_timestamp(0));

    ledger.add_transaction(tx1);
    ledger.add_transaction(tx2);

    EXPECT_EQ(ledger.transactions().size(), 2);
    EXPECT_EQ(ledger.transactions()[0].id, 1);
    EXPECT_EQ(ledger.transactions()[1].id, 2);
}

TEST(Ledger, AddAndRetrieveWallets) {
    Ledger ledger;

    Wallet w1(1, 1, "Wallet1", WalletType::Bank, "EUR", Money::from_double(1000.00));
    Wallet w2(2, 1, "Wallet2", WalletType::Cash, "USD", Money::from_double(500.00));

    ledger.add_wallet(w1);
    ledger.add_wallet(w2);

    EXPECT_EQ(ledger.wallets().size(), 2);
    EXPECT_EQ(ledger.wallets()[0].name, "Wallet1");
    EXPECT_EQ(ledger.wallets()[1].name, "Wallet2");
}

TEST(Ledger, AddAndRetrieveCategories) {
    Ledger ledger;

    Category c1(1, 1, std::nullopt, "Food", CategoryType::Expense);
    Category c2(2, 1, std::nullopt, "Salary", CategoryType::Income);

    ledger.add_category(c1);
    ledger.add_category(c2);

    EXPECT_EQ(ledger.categories().size(), 2);
    EXPECT_EQ(ledger.categories()[0].name, "Food");
    EXPECT_EQ(ledger.categories()[1].name, "Salary");
}

// =============================================================================
// Filter by Wallet Tests
// =============================================================================

TEST(Ledger, GetTransactionsByWallet) {
    Ledger ledger;

    Transaction tx1(1, 1, 1, Money::from_double(100.00), "W1", make_timestamp(0));
    Transaction tx2(2, 2, 1, Money::from_double(200.00), "W2", make_timestamp(0));
    Transaction tx3(3, 1, 1, Money::from_double(300.00), "W1", make_timestamp(0));

    ledger.add_transaction(tx1);
    ledger.add_transaction(tx2);
    ledger.add_transaction(tx3);

    auto wallet1Txs = ledger.get_transactions_by_wallet(1);
    auto wallet2Txs = ledger.get_transactions_by_wallet(2);
    auto wallet3Txs = ledger.get_transactions_by_wallet(3);

    EXPECT_EQ(wallet1Txs.size(), 2);
    EXPECT_EQ(wallet2Txs.size(), 1);
    EXPECT_TRUE(wallet3Txs.empty());
}

// =============================================================================
// Filter by Category Tests
// =============================================================================

TEST(Ledger, GetTransactionsByCategory) {
    Ledger ledger;

    Transaction tx1(1, 1, 1, Money::from_double(100.00), "C1", make_timestamp(0));
    Transaction tx2(2, 1, 2, Money::from_double(200.00), "C2", make_timestamp(0));
    Transaction tx3(3, 1, 1, Money::from_double(300.00), "C1", make_timestamp(0));

    ledger.add_transaction(tx1);
    ledger.add_transaction(tx2);
    ledger.add_transaction(tx3);

    auto cat1Txs = ledger.get_transactions_by_category(1);
    auto cat2Txs = ledger.get_transactions_by_category(2);
    auto cat3Txs = ledger.get_transactions_by_category(3);

    EXPECT_EQ(cat1Txs.size(), 2);
    EXPECT_EQ(cat2Txs.size(), 1);
    EXPECT_TRUE(cat3Txs.empty());
}

// =============================================================================
// Filter by Time Range Tests
// =============================================================================

TEST(Ledger, GetTransactionsInRange) {
    Ledger ledger;

    auto past = make_timestamp(-10);
    auto recent = make_timestamp(-1);
    auto future = make_timestamp(10);

    Transaction tx1(1, 1, 1, Money::from_double(100.00), "Past", past);
    Transaction tx2(2, 1, 1, Money::from_double(200.00), "Recent", recent);
    Transaction tx3(3, 1, 1, Money::from_double(300.00), "Future", future);

    ledger.add_transaction(tx1);
    ledger.add_transaction(tx2);
    ledger.add_transaction(tx3);

    // Get transactions from last 5 days
    auto start = make_timestamp(-5);
    auto end = make_timestamp(0);
    auto ranged = ledger.get_transactions_in_range(start, end);

    EXPECT_EQ(ranged.size(), 1);
    EXPECT_EQ(ranged[0].description, "Recent");
}

TEST(Ledger, GetTransactionsInRangeIncludesBoundaries) {
    Ledger ledger;

    auto time1 = make_timestamp(-2);
    auto time2 = make_timestamp(-1);

    Transaction tx1(1, 1, 1, Money::from_double(100.00), "T1", time1);
    Transaction tx2(2, 1, 1, Money::from_double(200.00), "T2", time2);

    ledger.add_transaction(tx1);
    ledger.add_transaction(tx2);

    // Range exactly matching both timestamps
    auto ranged = ledger.get_transactions_in_range(time1, time2);

    EXPECT_EQ(ranged.size(), 2);
}

// =============================================================================
// Wallet Balance Tests
// =============================================================================

TEST(Ledger, GetWalletBalance) {
    Ledger ledger;

    Wallet w(1, 1, "Test", WalletType::Bank, "EUR", Money::from_double(1000.00));
    ledger.add_wallet(w);

    Transaction tx1(1, 1, 1, Money::from_double(500.00), "Income", make_timestamp(0));
    Transaction tx2(2, 1, 1, Money::from_double(-200.00), "Expense", make_timestamp(0));

    ledger.add_transaction(tx1);
    ledger.add_transaction(tx2);

    Money balance = ledger.get_wallet_balance(1);
    EXPECT_DOUBLE_EQ(balance.to_double(), 1300.00);  // 1000 + 500 - 200
}

TEST(Ledger, GetWalletBalanceReturnsZeroForUnknownWallet) {
    Ledger ledger;

    Money balance = ledger.get_wallet_balance(999);
    EXPECT_TRUE(balance.is_zero());
}

// =============================================================================
// Total Balance Tests
// =============================================================================

TEST(Ledger, GetTotalBalance) {
    Ledger ledger;

    Wallet w1(1, 1, "W1", WalletType::Bank, "EUR", Money::from_double(1000.00));
    Wallet w2(2, 1, "W2", WalletType::Cash, "EUR", Money::from_double(500.00));

    ledger.add_wallet(w1);
    ledger.add_wallet(w2);

    Transaction tx1(1, 1, 1, Money::from_double(100.00), "Income", make_timestamp(0));
    Transaction tx2(2, 2, 1, Money::from_double(-50.00), "Expense", make_timestamp(0));

    ledger.add_transaction(tx1);
    ledger.add_transaction(tx2);

    Money total = ledger.get_total_balance();
    EXPECT_DOUBLE_EQ(total.to_double(), 1550.00);  // (1000+100) + (500-50)
}

TEST(Ledger, GetTotalBalanceWithNoWallets) {
    Ledger ledger;
    Money total = ledger.get_total_balance();
    EXPECT_TRUE(total.is_zero());
}

// =============================================================================
// Income/Expense Tests
// =============================================================================

TEST(Ledger, GetTotalIncome) {
    Ledger ledger;

    Transaction tx1(1, 1, 1, Money::from_double(100.00), "Income1", make_timestamp(0));
    Transaction tx2(2, 1, 1, Money::from_double(200.00), "Income2", make_timestamp(0));
    Transaction tx3(3, 1, 1, Money::from_double(-50.00), "Expense", make_timestamp(0));

    ledger.add_transaction(tx1);
    ledger.add_transaction(tx2);
    ledger.add_transaction(tx3);

    Money income = ledger.get_total_income();
    EXPECT_DOUBLE_EQ(income.to_double(), 300.00);  // 100 + 200
}

TEST(Ledger, GetTotalExpenses) {
    Ledger ledger;

    Transaction tx1(1, 1, 1, Money::from_double(100.00), "Income", make_timestamp(0));
    Transaction tx2(2, 1, 1, Money::from_double(-50.00), "Expense1", make_timestamp(0));
    Transaction tx3(3, 1, 1, Money::from_double(-30.00), "Expense2", make_timestamp(0));

    ledger.add_transaction(tx1);
    ledger.add_transaction(tx2);
    ledger.add_transaction(tx3);

    Money expenses = ledger.get_total_expenses();
    EXPECT_DOUBLE_EQ(expenses.to_double(), 80.00);  // 50 + 30 (absolute values)
}

TEST(Ledger, GetTotalIncomeWithNoTransactions) {
    Ledger ledger;
    Money income = ledger.get_total_income();
    EXPECT_TRUE(income.is_zero());
}

TEST(Ledger, GetTotalExpensesWithNoTransactions) {
    Ledger ledger;
    Money expenses = ledger.get_total_expenses();
    EXPECT_TRUE(expenses.is_zero());
}

// =============================================================================
// Clear Tests
// =============================================================================

TEST(Ledger, Clear) {
    Ledger ledger;

    ledger.add_transaction(Transaction(1, 1, 1, Money::from_double(100.00), "T", make_timestamp(0)));
    ledger.add_wallet(Wallet(1, 1, "W", WalletType::Bank, "EUR", Money()));
    ledger.add_category(Category(1, 1, std::nullopt, "C", CategoryType::Expense));

    EXPECT_FALSE(ledger.transactions().empty());
    EXPECT_FALSE(ledger.wallets().empty());
    EXPECT_FALSE(ledger.categories().empty());

    ledger.clear();

    EXPECT_TRUE(ledger.transactions().empty());
    EXPECT_TRUE(ledger.wallets().empty());
    EXPECT_TRUE(ledger.categories().empty());
}
