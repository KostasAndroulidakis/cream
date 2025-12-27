#ifndef CREAM_LEDGER_HPP
#define CREAM_LEDGER_HPP

#include "types.hpp"
#include "transaction.hpp"
#include "wallet.hpp"
#include "category.hpp"
#include <vector>

namespace cream {

class Ledger {
public:
    Ledger() = default;

    void add_transaction(const Transaction& tx) {
        transactions_.push_back(tx);
    }

    void add_wallet(const Wallet& wallet) {
        wallets_.push_back(wallet);
    }

    void add_category(const Category& category) {
        categories_.push_back(category);
    }

    const std::vector<Transaction>& transactions() const { return transactions_; }
    const std::vector<Wallet>& wallets() const { return wallets_; }
    const std::vector<Category>& categories() const { return categories_; }

    // Get transactions for a specific wallet
    std::vector<Transaction> get_transactions_by_wallet(int64_t wallet_id) const {
        std::vector<Transaction> result;
        for (const auto& tx : transactions_) {
            if (tx.wallet_id == wallet_id) {
                result.push_back(tx);
            }
        }
        return result;
    }

    // Get transactions for a specific category
    std::vector<Transaction> get_transactions_by_category(int64_t category_id) const {
        std::vector<Transaction> result;
        for (const auto& tx : transactions_) {
            if (tx.category_id == category_id) {
                result.push_back(tx);
            }
        }
        return result;
    }

    // Get transactions in a time range
    std::vector<Transaction> get_transactions_in_range(Timestamp start, Timestamp end) const {
        std::vector<Transaction> result;
        for (const auto& tx : transactions_) {
            if (tx.occurred_at >= start && tx.occurred_at <= end) {
                result.push_back(tx);
            }
        }
        return result;
    }

    // Calculate balance for a wallet
    Money get_wallet_balance(int64_t wallet_id) const {
        for (const auto& wallet : wallets_) {
            if (wallet.id == wallet_id) {
                return wallet.calculate_balance(transactions_);
            }
        }
        return Money();
    }

    // Calculate total balance across all wallets
    Money get_total_balance() const {
        Money total;
        for (const auto& wallet : wallets_) {
            total += wallet.calculate_balance(transactions_);
        }
        return total;
    }

    // Get total income
    Money get_total_income() const {
        Money total;
        for (const auto& tx : transactions_) {
            if (tx.is_income()) {
                total += tx.amount;
            }
        }
        return total;
    }

    // Get total expenses
    Money get_total_expenses() const {
        Money total;
        for (const auto& tx : transactions_) {
            if (tx.is_expense()) {
                total += tx.amount.abs();
            }
        }
        return total;
    }

    void clear() {
        transactions_.clear();
        wallets_.clear();
        categories_.clear();
    }

private:
    std::vector<Transaction> transactions_;
    std::vector<Wallet> wallets_;
    std::vector<Category> categories_;
};

} // namespace cream

#endif // CREAM_LEDGER_HPP
