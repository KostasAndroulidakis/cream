#ifndef CREAM_WALLET_HPP
#define CREAM_WALLET_HPP

#include "money.hpp"
#include "transaction.hpp"
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

namespace cream {

enum class WalletType {
    Bank,
    Cash,
    Digital,
    Stash
};

struct Wallet {
    int64_t id;
    int64_t user_id;
    std::string name;
    WalletType type;
    std::string currency;
    Money initial_balance;

    Wallet()
        : id(0), user_id(0), name(), type(WalletType::Bank),
          currency("EUR"), initial_balance() {}

    Wallet(int64_t id, int64_t user_id, std::string name,
           WalletType type, std::string currency, Money initial_balance)
        : id(id), user_id(user_id), name(std::move(name)),
          type(type), currency(std::move(currency)), initial_balance(initial_balance) {}

    Money calculate_balance(const std::vector<Transaction>& transactions) const {
        Money balance = initial_balance;
        for (const auto& tx : transactions) {
            if (tx.wallet_id == id) {
                balance += tx.amount;
            }
        }
        return balance;
    }
};

inline const char* wallet_type_to_string(WalletType type) {
    switch (type) {
        case WalletType::Bank: return "bank";
        case WalletType::Cash: return "cash";
        case WalletType::Digital: return "digital";
        case WalletType::Stash: return "stash";
        default: return "unknown";
    }
}

inline WalletType wallet_type_from_string(const std::string& str) {
    if (str == "bank") return WalletType::Bank;
    if (str == "cash") return WalletType::Cash;
    if (str == "digital") return WalletType::Digital;
    if (str == "stash") return WalletType::Stash;
    throw std::invalid_argument("Unknown wallet type: " + str);
}

} // namespace cream

#endif // CREAM_WALLET_HPP
