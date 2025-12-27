#ifndef CREAM_VALIDATION_HPP
#define CREAM_VALIDATION_HPP

#include "money.hpp"
#include "transaction.hpp"
#include <string>
#include <vector>
#include <chrono>

namespace cream {

struct ValidationError {
    std::string field;
    std::string message;

    ValidationError(std::string field, std::string message)
        : field(std::move(field)), message(std::move(message)) {}
};

struct ValidationResult {
    bool valid;
    std::vector<ValidationError> errors;

    ValidationResult() : valid(true) {}

    void add_error(const std::string& field, const std::string& message) {
        valid = false;
        errors.emplace_back(field, message);
    }

    bool is_valid() const { return valid; }
};

class TransactionValidator {
public:
    TransactionValidator()
        : min_amount_(Money::from_raw(1))  // 0.0001 minimum
        , max_amount_(Money::from_double(999999999.9999))  // ~1 billion max
        , allow_future_dates_(false) {}

    TransactionValidator& set_min_amount(Money min) {
        min_amount_ = min;
        return *this;
    }

    TransactionValidator& set_max_amount(Money max) {
        max_amount_ = max;
        return *this;
    }

    TransactionValidator& set_allow_future_dates(bool allow) {
        allow_future_dates_ = allow;
        return *this;
    }

    ValidationResult validate(const Transaction& tx) const {
        ValidationResult result;

        // Amount validation
        if (tx.amount.is_zero()) {
            result.add_error("amount", "Amount cannot be zero");
        }

        Money abs_amount = tx.amount.abs();
        if (abs_amount < min_amount_) {
            result.add_error("amount", "Amount is below minimum allowed");
        }

        if (abs_amount > max_amount_) {
            result.add_error("amount", "Amount exceeds maximum allowed");
        }

        // Date validation
        if (!allow_future_dates_) {
            auto now = std::chrono::system_clock::now();
            if (tx.occurred_at > now) {
                result.add_error("occurred_at", "Transaction date cannot be in the future");
            }
        }

        // Wallet ID validation
        if (tx.wallet_id <= 0) {
            result.add_error("wallet_id", "Invalid wallet ID");
        }

        // Category ID validation
        if (tx.category_id <= 0) {
            result.add_error("category_id", "Invalid category ID");
        }

        return result;
    }

private:
    Money min_amount_;
    Money max_amount_;
    bool allow_future_dates_;
};

// Convenience function for quick validation with defaults
inline ValidationResult validate_transaction(const Transaction& tx) {
    return TransactionValidator().validate(tx);
}

} // namespace cream

#endif // CREAM_VALIDATION_HPP
