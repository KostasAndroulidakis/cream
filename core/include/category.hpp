#ifndef CREAM_CATEGORY_HPP
#define CREAM_CATEGORY_HPP

#include <cstdint>
#include <string>
#include <vector>
#include <optional>

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
    return CategoryType::Expense;
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
inline std::vector<Category> get_ancestors(const Category& cat,
                                           const std::vector<Category>& all_categories) {
    std::vector<Category> ancestors;
    std::optional<int64_t> current_parent_id = cat.parent_id;

    while (current_parent_id.has_value()) {
        for (const auto& c : all_categories) {
            if (c.id == current_parent_id.value()) {
                ancestors.insert(ancestors.begin(), c);
                current_parent_id = c.parent_id;
                break;
            }
        }
    }
    return ancestors;
}

} // namespace cream

#endif // CREAM_CATEGORY_HPP
