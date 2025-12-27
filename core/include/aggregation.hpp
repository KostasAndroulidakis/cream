#ifndef CREAM_AGGREGATION_HPP
#define CREAM_AGGREGATION_HPP

#include "types.hpp"
#include "money.hpp"
#include "transaction.hpp"
#include <vector>
#include <unordered_map>

namespace cream {

// Sum transactions by category
inline std::unordered_map<int64_t, Money> sum_by_category(
    const std::vector<Transaction>& transactions) {
    std::unordered_map<int64_t, Money> result;
    for (const auto& tx : transactions) {
        result[tx.category_id] += tx.amount;
    }
    return result;
}

// Sum transactions by wallet
inline std::unordered_map<int64_t, Money> sum_by_wallet(
    const std::vector<Transaction>& transactions) {
    std::unordered_map<int64_t, Money> result;
    for (const auto& tx : transactions) {
        result[tx.wallet_id] += tx.amount;
    }
    return result;
}

// Get total for a time period
inline Money sum_in_period(const std::vector<Transaction>& transactions,
                           Timestamp start, Timestamp end) {
    Money total;
    for (const auto& tx : transactions) {
        if (tx.occurred_at >= start && tx.occurred_at <= end) {
            total += tx.amount;
        }
    }
    return total;
}

// Get income total for a time period
inline Money income_in_period(const std::vector<Transaction>& transactions,
                              Timestamp start, Timestamp end) {
    Money total;
    for (const auto& tx : transactions) {
        if (tx.occurred_at >= start && tx.occurred_at <= end && tx.is_income()) {
            total += tx.amount;
        }
    }
    return total;
}

// Get expenses total for a time period
inline Money expenses_in_period(const std::vector<Transaction>& transactions,
                                Timestamp start, Timestamp end) {
    Money total;
    for (const auto& tx : transactions) {
        if (tx.occurred_at >= start && tx.occurred_at <= end && tx.is_expense()) {
            total += tx.amount.abs();
        }
    }
    return total;
}

// Count transactions by category
inline std::unordered_map<int64_t, size_t> count_by_category(
    const std::vector<Transaction>& transactions) {
    std::unordered_map<int64_t, size_t> result;
    for (const auto& tx : transactions) {
        result[tx.category_id]++;
    }
    return result;
}

// Average transaction amount
inline Money average_amount(const std::vector<Transaction>& transactions) {
    if (transactions.empty()) {
        return Money();
    }
    Money total;
    for (const auto& tx : transactions) {
        total += tx.amount.abs();
    }
    return total / static_cast<int64_t>(transactions.size());
}

} // namespace cream

#endif // CREAM_AGGREGATION_HPP
