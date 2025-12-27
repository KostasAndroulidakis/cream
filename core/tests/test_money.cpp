#include <gtest/gtest.h>
#include "money.hpp"

using namespace cream;

// =============================================================================
// Construction Tests
// =============================================================================

TEST(Money, DefaultConstructorIsZero) {
    Money m;
    EXPECT_EQ(m.raw(), 0);
    EXPECT_TRUE(m.is_zero());
}

TEST(Money, ConstructFromCents) {
    Money m(100);  // 100 cents = 1.00
    EXPECT_EQ(m.raw(), 10000);  // 1.0000 in raw (SCALE=10000)
    EXPECT_DOUBLE_EQ(m.to_double(), 1.0);
}

TEST(Money, FromRaw) {
    Money m = Money::from_raw(12345);
    EXPECT_EQ(m.raw(), 12345);
    EXPECT_DOUBLE_EQ(m.to_double(), 1.2345);
}

TEST(Money, FromDouble) {
    Money m = Money::from_double(123.4567);
    EXPECT_EQ(m.raw(), 1234567);
    EXPECT_DOUBLE_EQ(m.to_double(), 123.4567);
}

TEST(Money, FromDoubleRounding) {
    // Should round to 4 decimal places
    Money m = Money::from_double(1.23456789);
    EXPECT_EQ(m.raw(), 12346);  // Rounded from 12345.6789
}

TEST(Money, FromStringWholeNumber) {
    Money m = Money::from_string("42");
    EXPECT_DOUBLE_EQ(m.to_double(), 42.0);
}

TEST(Money, FromStringWithDecimals) {
    Money m = Money::from_string("123.45");
    EXPECT_DOUBLE_EQ(m.to_double(), 123.45);
}

TEST(Money, FromStringPadsDecimals) {
    Money m = Money::from_string("5.5");
    EXPECT_EQ(m.raw(), 55000);  // 5.5000
}

TEST(Money, FromStringTruncatesDecimals) {
    Money m = Money::from_string("1.234567");
    EXPECT_EQ(m.raw(), 12345);  // Truncated to 1.2345
}

TEST(Money, FromStringNegative) {
    Money m = Money::from_string("-50.25");
    EXPECT_DOUBLE_EQ(m.to_double(), -50.25);
    EXPECT_TRUE(m.is_negative());
}

// =============================================================================
// Conversion Tests
// =============================================================================

TEST(Money, ToStringPositive) {
    Money m = Money::from_double(123.45);
    EXPECT_EQ(m.to_string(), "123.4500");
}

TEST(Money, ToStringNegative) {
    Money m = Money::from_double(-99.99);
    EXPECT_EQ(m.to_string(), "-99.9900");
}

TEST(Money, ToStringZero) {
    Money m;
    EXPECT_EQ(m.to_string(), "0.0000");
}

TEST(Money, ToStringSmallDecimal) {
    Money m = Money::from_raw(1);  // 0.0001
    EXPECT_EQ(m.to_string(), "0.0001");
}

// =============================================================================
// Arithmetic Tests
// =============================================================================

TEST(Money, Addition) {
    Money a = Money::from_double(10.50);
    Money b = Money::from_double(5.25);
    Money result = a + b;
    EXPECT_DOUBLE_EQ(result.to_double(), 15.75);
}

TEST(Money, Subtraction) {
    Money a = Money::from_double(10.50);
    Money b = Money::from_double(5.25);
    Money result = a - b;
    EXPECT_DOUBLE_EQ(result.to_double(), 5.25);
}

TEST(Money, SubtractionResultsInNegative) {
    Money a = Money::from_double(5.00);
    Money b = Money::from_double(10.00);
    Money result = a - b;
    EXPECT_DOUBLE_EQ(result.to_double(), -5.0);
    EXPECT_TRUE(result.is_negative());
}

TEST(Money, MultiplicationByPositive) {
    Money m = Money::from_double(10.00);
    Money result = m * 3;
    EXPECT_DOUBLE_EQ(result.to_double(), 30.0);
}

TEST(Money, MultiplicationByNegative) {
    Money m = Money::from_double(10.00);
    Money result = m * (-2);
    EXPECT_DOUBLE_EQ(result.to_double(), -20.0);
}

TEST(Money, MultiplicationByZero) {
    Money m = Money::from_double(100.00);
    Money result = m * 0;
    EXPECT_TRUE(result.is_zero());
}

TEST(Money, Division) {
    Money m = Money::from_double(100.00);
    Money result = m / 4;
    EXPECT_DOUBLE_EQ(result.to_double(), 25.0);
}

TEST(Money, DivisionByZeroThrows) {
    Money m = Money::from_double(100.00);
    EXPECT_THROW(m / 0, std::invalid_argument);
}

TEST(Money, UnaryNegation) {
    Money m = Money::from_double(50.00);
    Money negated = -m;
    EXPECT_DOUBLE_EQ(negated.to_double(), -50.0);
}

TEST(Money, UnaryNegationOfNegative) {
    Money m = Money::from_double(-50.00);
    Money negated = -m;
    EXPECT_DOUBLE_EQ(negated.to_double(), 50.0);
}

// =============================================================================
// Compound Assignment Tests
// =============================================================================

TEST(Money, PlusEquals) {
    Money m = Money::from_double(10.00);
    m += Money::from_double(5.50);
    EXPECT_DOUBLE_EQ(m.to_double(), 15.50);
}

TEST(Money, MinusEquals) {
    Money m = Money::from_double(10.00);
    m -= Money::from_double(3.25);
    EXPECT_DOUBLE_EQ(m.to_double(), 6.75);
}

// =============================================================================
// Comparison Tests
// =============================================================================

TEST(Money, Equality) {
    Money a = Money::from_double(10.00);
    Money b = Money::from_double(10.00);
    EXPECT_TRUE(a == b);
    EXPECT_FALSE(a != b);
}

TEST(Money, Inequality) {
    Money a = Money::from_double(10.00);
    Money b = Money::from_double(10.01);
    EXPECT_FALSE(a == b);
    EXPECT_TRUE(a != b);
}

TEST(Money, LessThan) {
    Money a = Money::from_double(5.00);
    Money b = Money::from_double(10.00);
    EXPECT_TRUE(a < b);
    EXPECT_FALSE(b < a);
    EXPECT_FALSE(a < a);
}

TEST(Money, LessThanOrEqual) {
    Money a = Money::from_double(5.00);
    Money b = Money::from_double(10.00);
    Money c = Money::from_double(5.00);
    EXPECT_TRUE(a <= b);
    EXPECT_TRUE(a <= c);
    EXPECT_FALSE(b <= a);
}

TEST(Money, GreaterThan) {
    Money a = Money::from_double(10.00);
    Money b = Money::from_double(5.00);
    EXPECT_TRUE(a > b);
    EXPECT_FALSE(b > a);
    EXPECT_FALSE(a > a);
}

TEST(Money, GreaterThanOrEqual) {
    Money a = Money::from_double(10.00);
    Money b = Money::from_double(5.00);
    Money c = Money::from_double(10.00);
    EXPECT_TRUE(a >= b);
    EXPECT_TRUE(a >= c);
    EXPECT_FALSE(b >= a);
}

// =============================================================================
// Utility Method Tests
// =============================================================================

TEST(Money, IsZero) {
    EXPECT_TRUE(Money().is_zero());
    EXPECT_TRUE(Money::from_double(0.0).is_zero());
    EXPECT_FALSE(Money::from_double(0.0001).is_zero());
    EXPECT_FALSE(Money::from_double(-0.0001).is_zero());
}

TEST(Money, IsPositive) {
    EXPECT_TRUE(Money::from_double(1.00).is_positive());
    EXPECT_TRUE(Money::from_double(0.0001).is_positive());
    EXPECT_FALSE(Money().is_positive());
    EXPECT_FALSE(Money::from_double(-1.00).is_positive());
}

TEST(Money, IsNegative) {
    EXPECT_TRUE(Money::from_double(-1.00).is_negative());
    EXPECT_TRUE(Money::from_double(-0.0001).is_negative());
    EXPECT_FALSE(Money().is_negative());
    EXPECT_FALSE(Money::from_double(1.00).is_negative());
}

TEST(Money, Abs) {
    Money positive = Money::from_double(50.00);
    Money negative = Money::from_double(-50.00);
    Money zero;

    EXPECT_DOUBLE_EQ(positive.abs().to_double(), 50.0);
    EXPECT_DOUBLE_EQ(negative.abs().to_double(), 50.0);
    EXPECT_TRUE(zero.abs().is_zero());
}

// =============================================================================
// Edge Cases
// =============================================================================

TEST(Money, VerySmallAmount) {
    Money m = Money::from_raw(1);  // Smallest representable: 0.0001
    EXPECT_DOUBLE_EQ(m.to_double(), 0.0001);
    EXPECT_FALSE(m.is_zero());
    EXPECT_TRUE(m.is_positive());
}

TEST(Money, LargeAmount) {
    Money m = Money::from_double(999999999.9999);
    EXPECT_EQ(m.to_string(), "999999999.9999");
}

TEST(Money, NegativeFromString) {
    Money m = Money::from_string("-0.01");
    EXPECT_TRUE(m.is_negative());
    EXPECT_DOUBLE_EQ(m.to_double(), -0.01);
}
