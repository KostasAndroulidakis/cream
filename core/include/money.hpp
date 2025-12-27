#ifndef CREAM_MONEY_HPP
#define CREAM_MONEY_HPP

#include <cstdint>
#include <string>
#include <stdexcept>
#include <cmath>

namespace cream {

// Fixed-point decimal with 4 decimal places (matches PostgreSQL NUMERIC(19,4))
// Stores value as integer in units of 0.0001
class Money {
public:
    static constexpr int64_t SCALE = 10000;  // 4 decimal places
    static constexpr int DECIMAL_PLACES = 4;

    Money() : value_(0) {}

    explicit Money(int64_t cents) : value_(cents * (SCALE / 100)) {}

    static Money from_raw(int64_t raw_value) {
        Money m;
        m.value_ = raw_value;
        return m;
    }

    static Money from_double(double amount) {
        return Money::from_raw(static_cast<int64_t>(std::round(amount * SCALE)));
    }

    static Money from_string(const std::string& str) {
        size_t dot_pos = str.find('.');
        if (dot_pos == std::string::npos) {
            return Money(std::stoll(str) * 100);  // No decimal, treat as whole units
        }

        std::string integer_part = str.substr(0, dot_pos);
        std::string decimal_part = str.substr(dot_pos + 1);

        // Pad or truncate to 4 decimal places
        while (decimal_part.length() < DECIMAL_PLACES) {
            decimal_part += '0';
        }
        if (decimal_part.length() > DECIMAL_PLACES) {
            decimal_part = decimal_part.substr(0, DECIMAL_PLACES);
        }

        int64_t int_val = integer_part.empty() ? 0 : std::stoll(integer_part);
        int64_t dec_val = std::stoll(decimal_part);

        int64_t raw = int_val * SCALE + (str[0] == '-' ? -dec_val : dec_val);
        return Money::from_raw(raw);
    }

    // Getters
    int64_t raw() const { return value_; }
    double to_double() const { return static_cast<double>(value_) / SCALE; }

    std::string to_string() const {
        bool negative = value_ < 0;
        int64_t abs_val = negative ? -value_ : value_;
        int64_t integer_part = abs_val / SCALE;
        int64_t decimal_part = abs_val % SCALE;

        std::string result = (negative ? "-" : "") +
                            std::to_string(integer_part) + "." +
                            std::string(DECIMAL_PLACES - std::to_string(decimal_part).length(), '0') +
                            std::to_string(decimal_part);
        return result;
    }

    // Arithmetic operators
    Money operator+(const Money& other) const {
        return Money::from_raw(value_ + other.value_);
    }

    Money operator-(const Money& other) const {
        return Money::from_raw(value_ - other.value_);
    }

    Money operator*(int64_t multiplier) const {
        return Money::from_raw(value_ * multiplier);
    }

    Money operator/(int64_t divisor) const {
        if (divisor == 0) throw std::invalid_argument("Division by zero");
        return Money::from_raw(value_ / divisor);
    }

    Money operator-() const {
        return Money::from_raw(-value_);
    }

    // Compound assignment
    Money& operator+=(const Money& other) {
        value_ += other.value_;
        return *this;
    }

    Money& operator-=(const Money& other) {
        value_ -= other.value_;
        return *this;
    }

    // Comparison operators
    bool operator==(const Money& other) const { return value_ == other.value_; }
    bool operator!=(const Money& other) const { return value_ != other.value_; }
    bool operator<(const Money& other) const { return value_ < other.value_; }
    bool operator<=(const Money& other) const { return value_ <= other.value_; }
    bool operator>(const Money& other) const { return value_ > other.value_; }
    bool operator>=(const Money& other) const { return value_ >= other.value_; }

    // Utility
    bool is_zero() const { return value_ == 0; }
    bool is_positive() const { return value_ > 0; }
    bool is_negative() const { return value_ < 0; }
    Money abs() const { return Money::from_raw(value_ < 0 ? -value_ : value_); }

private:
    int64_t value_;  // Value in units of 0.0001
};

} // namespace cream

#endif // CREAM_MONEY_HPP
