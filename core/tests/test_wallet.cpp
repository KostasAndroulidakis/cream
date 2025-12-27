#include <gtest/gtest.h>
#include "wallet.hpp"

using namespace cream;

// =============================================================================
// Construction Tests
// =============================================================================

TEST(Wallet, DefaultConstruction) {
    Wallet w;
    EXPECT_EQ(w.id, 0);
    EXPECT_EQ(w.user_id, 0);
    EXPECT_TRUE(w.name.empty());
    EXPECT_EQ(w.type, WalletType::Bank);
    EXPECT_EQ(w.currency, "EUR");
    EXPECT_TRUE(w.initial_balance.is_zero());
}

TEST(Wallet, ParameterizedConstruction) {
    Money balance = Money::from_double(1000.00);
    Wallet w(1, 2, "My Wallet", WalletType::Digital, "USD", balance);

    EXPECT_EQ(w.id, 1);
    EXPECT_EQ(w.user_id, 2);
    EXPECT_EQ(w.name, "My Wallet");
    EXPECT_EQ(w.type, WalletType::Digital);
    EXPECT_EQ(w.currency, "USD");
    EXPECT_EQ(w.initial_balance, balance);
}

// =============================================================================
// WalletType Enum Tests
// =============================================================================

TEST(Wallet, WalletTypeToString) {
    EXPECT_STREQ(wallet_type_to_string(WalletType::Bank), "bank");
    EXPECT_STREQ(wallet_type_to_string(WalletType::Cash), "cash");
    EXPECT_STREQ(wallet_type_to_string(WalletType::Digital), "digital");
    EXPECT_STREQ(wallet_type_to_string(WalletType::Stash), "stash");
}

TEST(Wallet, WalletTypeFromString) {
    EXPECT_EQ(wallet_type_from_string("bank"), WalletType::Bank);
    EXPECT_EQ(wallet_type_from_string("cash"), WalletType::Cash);
    EXPECT_EQ(wallet_type_from_string("digital"), WalletType::Digital);
    EXPECT_EQ(wallet_type_from_string("stash"), WalletType::Stash);
}

TEST(Wallet, WalletTypeFromStringThrowsOnInvalid) {
    EXPECT_THROW(wallet_type_from_string("invalid"), std::invalid_argument);
    EXPECT_THROW(wallet_type_from_string(""), std::invalid_argument);
    EXPECT_THROW(wallet_type_from_string("BANK"), std::invalid_argument);  // Case sensitive
}

// =============================================================================
// Balance Calculation Tests
// =============================================================================

TEST(Wallet, CalculateBalanceWithNoTransactions) {
    Wallet w(1, 1, "Test", WalletType::Bank, "EUR", Money::from_double(500.00));
    std::vector<Transaction> transactions;

    Money balance = w.calculate_balance(transactions);
    EXPECT_DOUBLE_EQ(balance.to_double(), 500.00);
}

TEST(Wallet, CalculateBalanceWithIncome) {
    Wallet w(1, 1, "Test", WalletType::Bank, "EUR", Money::from_double(100.00));

    std::vector<Transaction> transactions;
    Transaction tx;
    tx.wallet_id = 1;
    tx.amount = Money::from_double(50.00);  // Income
    transactions.push_back(tx);

    Money balance = w.calculate_balance(transactions);
    EXPECT_DOUBLE_EQ(balance.to_double(), 150.00);
}

TEST(Wallet, CalculateBalanceWithExpense) {
    Wallet w(1, 1, "Test", WalletType::Bank, "EUR", Money::from_double(100.00));

    std::vector<Transaction> transactions;
    Transaction tx;
    tx.wallet_id = 1;
    tx.amount = Money::from_double(-30.00);  // Expense
    transactions.push_back(tx);

    Money balance = w.calculate_balance(transactions);
    EXPECT_DOUBLE_EQ(balance.to_double(), 70.00);
}

TEST(Wallet, CalculateBalanceWithMixedTransactions) {
    Wallet w(1, 1, "Test", WalletType::Bank, "EUR", Money::from_double(1000.00));

    std::vector<Transaction> transactions;

    Transaction income;
    income.wallet_id = 1;
    income.amount = Money::from_double(200.00);
    transactions.push_back(income);

    Transaction expense1;
    expense1.wallet_id = 1;
    expense1.amount = Money::from_double(-50.00);
    transactions.push_back(expense1);

    Transaction expense2;
    expense2.wallet_id = 1;
    expense2.amount = Money::from_double(-150.00);
    transactions.push_back(expense2);

    // 1000 + 200 - 50 - 150 = 1000
    Money balance = w.calculate_balance(transactions);
    EXPECT_DOUBLE_EQ(balance.to_double(), 1000.00);
}

TEST(Wallet, CalculateBalanceIgnoresOtherWallets) {
    Wallet w(1, 1, "Test", WalletType::Bank, "EUR", Money::from_double(100.00));

    std::vector<Transaction> transactions;

    Transaction tx1;
    tx1.wallet_id = 1;  // This wallet
    tx1.amount = Money::from_double(50.00);
    transactions.push_back(tx1);

    Transaction tx2;
    tx2.wallet_id = 2;  // Different wallet - should be ignored
    tx2.amount = Money::from_double(1000.00);
    transactions.push_back(tx2);

    Transaction tx3;
    tx3.wallet_id = 99;  // Different wallet - should be ignored
    tx3.amount = Money::from_double(-500.00);
    transactions.push_back(tx3);

    Money balance = w.calculate_balance(transactions);
    EXPECT_DOUBLE_EQ(balance.to_double(), 150.00);  // Only 100 + 50
}

TEST(Wallet, CalculateBalanceCanGoNegative) {
    Wallet w(1, 1, "Test", WalletType::Bank, "EUR", Money::from_double(50.00));

    std::vector<Transaction> transactions;
    Transaction tx;
    tx.wallet_id = 1;
    tx.amount = Money::from_double(-100.00);
    transactions.push_back(tx);

    Money balance = w.calculate_balance(transactions);
    EXPECT_DOUBLE_EQ(balance.to_double(), -50.00);
    EXPECT_TRUE(balance.is_negative());
}

TEST(Wallet, CalculateBalanceWithZeroInitial) {
    Wallet w(1, 1, "Test", WalletType::Cash, "EUR", Money());

    std::vector<Transaction> transactions;
    Transaction tx;
    tx.wallet_id = 1;
    tx.amount = Money::from_double(75.50);
    transactions.push_back(tx);

    Money balance = w.calculate_balance(transactions);
    EXPECT_DOUBLE_EQ(balance.to_double(), 75.50);
}

// =============================================================================
// Field Modification Tests
// =============================================================================

TEST(Wallet, CanModifyFields) {
    Wallet w;

    w.id = 42;
    w.user_id = 10;
    w.name = "Updated Wallet";
    w.type = WalletType::Stash;
    w.currency = "GBP";
    w.initial_balance = Money::from_double(999.99);

    EXPECT_EQ(w.id, 42);
    EXPECT_EQ(w.user_id, 10);
    EXPECT_EQ(w.name, "Updated Wallet");
    EXPECT_EQ(w.type, WalletType::Stash);
    EXPECT_EQ(w.currency, "GBP");
    EXPECT_DOUBLE_EQ(w.initial_balance.to_double(), 999.99);
}
