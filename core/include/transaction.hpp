#ifndef CREAM_TRANSACTION_HPP
#define CREAM_TRANSACTION_HPP

#include "money.hpp"
#include "types.hpp"
#include <cstdint>
#include <string>

namespace cream {

struct Transaction {
    int64_t id;
    int64_t wallet_id;
    int64_t category_id;
    Money amount;
    std::string description;
    Timestamp occurred_at;

    Transaction()
        : id(0), wallet_id(0), category_id(0), amount(), description(), occurred_at() {}

    Transaction(int64_t id, int64_t wallet_id, int64_t category_id,
                Money amount, std::string description, Timestamp occurred_at)
        : id(id), wallet_id(wallet_id), category_id(category_id),
          amount(amount), description(std::move(description)), occurred_at(occurred_at) {}

    bool is_income() const { return amount.is_positive(); }
    bool is_expense() const { return amount.is_negative(); }
};

} // namespace cream

#endif // CREAM_TRANSACTION_HPP
