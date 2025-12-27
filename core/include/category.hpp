#ifndef CREAM_CATEGORY_HPP
#define CREAM_CATEGORY_HPP

#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>

namespace cream {

enum class CategoryType {
    Income,
    Expense
};

struct Category {
    int64_t id;
    std::optional<int64_t> user_id;    // nullopt = system default
    std::optional<int64_t> parent_id;  // nullopt = root category
    std::string name;
    CategoryType type;

    Category()
        : id(0), user_id(std::nullopt), parent_id(std::nullopt),
          name(), type(CategoryType::Expense) {}

    Category(int64_t id, std::optional<int64_t> user_id,
             std::optional<int64_t> parent_id, std::string name, CategoryType type)
        : id(id), user_id(user_id), parent_id(parent_id),
          name(std::move(name)), type(type) {}

    bool is_system_default() const { return !user_id.has_value(); }
    bool is_root() const { return !parent_id.has_value(); }
    bool is_income() const { return type == CategoryType::Income; }
    bool is_expense() const { return type == CategoryType::Expense; }
};

inline const char* category_type_to_string(CategoryType type) {
    switch (type) {
        case CategoryType::Income: return "income";
        case CategoryType::Expense: return "expense";
        default: return "unknown";
    }
}

inline CategoryType category_type_from_string(const std::string& str) {
    if (str == "income") return CategoryType::Income;
    if (str == "expense") return CategoryType::Expense;
    throw std::invalid_argument("Unknown category type: " + str);
}

// Find all children of a category
inline std::vector<Category> get_children(const Category& parent,
                                          const std::vector<Category>& all_categories) {
    std::vector<Category> children;
    for (const auto& cat : all_categories) {
        if (cat.parent_id.has_value() && cat.parent_id.value() == parent.id) {
            children.push_back(cat);
        }
    }
    return children;
}

// Get full path from root to category
// Returns empty vector if a cycle is detected
inline std::vector<Category> get_ancestors(const Category& cat,
                                           const std::vector<Category>& all_categories) {
    std::vector<Category> ancestors;
    std::optional<int64_t> current_parent_id = cat.parent_id;
    std::unordered_set<int64_t> visited;
    visited.insert(cat.id);

    while (current_parent_id.has_value()) {
        // Cycle detection
        if (visited.count(current_parent_id.value()) > 0) {
            return {};  // Return empty on cycle
        }
        visited.insert(current_parent_id.value());

        bool found = false;
        for (const auto& c : all_categories) {
            if (c.id == current_parent_id.value()) {
                ancestors.insert(ancestors.begin(), c);
                current_parent_id = c.parent_id;
                found = true;
                break;
            }
        }
        // Parent not found in list - stop traversal
        if (!found) {
            break;
        }
    }
    return ancestors;
}

} // namespace cream

#endif // CREAM_CATEGORY_HPP
