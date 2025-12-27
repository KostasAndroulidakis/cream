#include <gtest/gtest.h>
#include "category.hpp"

using namespace cream;

// =============================================================================
// Construction Tests
// =============================================================================

TEST(Category, DefaultConstruction) {
    Category c;
    EXPECT_EQ(c.id, 0);
    EXPECT_FALSE(c.user_id.has_value());
    EXPECT_FALSE(c.parent_id.has_value());
    EXPECT_TRUE(c.name.empty());
    EXPECT_EQ(c.type, CategoryType::Expense);
}

TEST(Category, ParameterizedConstruction) {
    Category c(1, 2, 3, "Food", CategoryType::Expense);

    EXPECT_EQ(c.id, 1);
    EXPECT_TRUE(c.user_id.has_value());
    EXPECT_EQ(c.user_id.value(), 2);
    EXPECT_TRUE(c.parent_id.has_value());
    EXPECT_EQ(c.parent_id.value(), 3);
    EXPECT_EQ(c.name, "Food");
    EXPECT_EQ(c.type, CategoryType::Expense);
}

TEST(Category, ConstructionWithNullopt) {
    Category c(1, std::nullopt, std::nullopt, "Root", CategoryType::Income);

    EXPECT_EQ(c.id, 1);
    EXPECT_FALSE(c.user_id.has_value());
    EXPECT_FALSE(c.parent_id.has_value());
    EXPECT_EQ(c.name, "Root");
    EXPECT_EQ(c.type, CategoryType::Income);
}

// =============================================================================
// CategoryType Enum Tests
// =============================================================================

TEST(Category, CategoryTypeToString) {
    EXPECT_STREQ(category_type_to_string(CategoryType::Income), "income");
    EXPECT_STREQ(category_type_to_string(CategoryType::Expense), "expense");
}

TEST(Category, CategoryTypeFromString) {
    EXPECT_EQ(category_type_from_string("income"), CategoryType::Income);
    EXPECT_EQ(category_type_from_string("expense"), CategoryType::Expense);
}

TEST(Category, CategoryTypeFromStringThrowsOnInvalid) {
    EXPECT_THROW(category_type_from_string("invalid"), std::invalid_argument);
    EXPECT_THROW(category_type_from_string(""), std::invalid_argument);
    EXPECT_THROW(category_type_from_string("INCOME"), std::invalid_argument);  // Case sensitive
}

// =============================================================================
// Property Tests
// =============================================================================

TEST(Category, IsSystemDefault) {
    Category systemCat(1, std::nullopt, std::nullopt, "Default", CategoryType::Expense);
    Category userCat(2, 1, std::nullopt, "Custom", CategoryType::Expense);

    EXPECT_TRUE(systemCat.is_system_default());
    EXPECT_FALSE(userCat.is_system_default());
}

TEST(Category, IsRoot) {
    Category rootCat(1, 1, std::nullopt, "Root", CategoryType::Expense);
    Category childCat(2, 1, 1, "Child", CategoryType::Expense);

    EXPECT_TRUE(rootCat.is_root());
    EXPECT_FALSE(childCat.is_root());
}

TEST(Category, IsIncomeAndIsExpense) {
    Category income(1, 1, std::nullopt, "Salary", CategoryType::Income);
    Category expense(2, 1, std::nullopt, "Food", CategoryType::Expense);

    EXPECT_TRUE(income.is_income());
    EXPECT_FALSE(income.is_expense());

    EXPECT_FALSE(expense.is_income());
    EXPECT_TRUE(expense.is_expense());
}

// =============================================================================
// get_children Tests
// =============================================================================

TEST(Category, GetChildrenFindsDirectChildren) {
    Category parent(1, 1, std::nullopt, "Parent", CategoryType::Expense);
    Category child1(2, 1, 1, "Child1", CategoryType::Expense);
    Category child2(3, 1, 1, "Child2", CategoryType::Expense);
    Category grandchild(4, 1, 2, "Grandchild", CategoryType::Expense);
    Category unrelated(5, 1, std::nullopt, "Unrelated", CategoryType::Expense);

    std::vector<Category> all = {parent, child1, child2, grandchild, unrelated};

    auto children = get_children(parent, all);

    EXPECT_EQ(children.size(), 2);
    EXPECT_EQ(children[0].id, 2);
    EXPECT_EQ(children[1].id, 3);
}

TEST(Category, GetChildrenReturnsEmptyForLeaf) {
    Category leaf(1, 1, std::nullopt, "Leaf", CategoryType::Expense);
    std::vector<Category> all = {leaf};

    auto children = get_children(leaf, all);

    EXPECT_TRUE(children.empty());
}

TEST(Category, GetChildrenWithEmptyList) {
    Category parent(1, 1, std::nullopt, "Parent", CategoryType::Expense);
    std::vector<Category> all;

    auto children = get_children(parent, all);

    EXPECT_TRUE(children.empty());
}

// =============================================================================
// get_ancestors Tests
// =============================================================================

TEST(Category, GetAncestorsBuildsPathFromRoot) {
    Category root(1, 1, std::nullopt, "Root", CategoryType::Expense);
    Category child(2, 1, 1, "Child", CategoryType::Expense);
    Category grandchild(3, 1, 2, "Grandchild", CategoryType::Expense);

    std::vector<Category> all = {root, child, grandchild};

    auto ancestors = get_ancestors(grandchild, all);

    EXPECT_EQ(ancestors.size(), 2);
    EXPECT_EQ(ancestors[0].id, 1);  // Root first
    EXPECT_EQ(ancestors[1].id, 2);  // Then child
}

TEST(Category, GetAncestorsReturnsEmptyForRoot) {
    Category root(1, 1, std::nullopt, "Root", CategoryType::Expense);
    std::vector<Category> all = {root};

    auto ancestors = get_ancestors(root, all);

    EXPECT_TRUE(ancestors.empty());
}

TEST(Category, GetAncestorsHandlesMissingParent) {
    Category orphan(1, 1, 999, "Orphan", CategoryType::Expense);  // Parent 999 doesn't exist
    std::vector<Category> all = {orphan};

    auto ancestors = get_ancestors(orphan, all);

    EXPECT_TRUE(ancestors.empty());  // Stops when parent not found
}

TEST(Category, GetAncestorsDetectsCycle) {
    // Create a cycle: 1 -> 2 -> 3 -> 1
    Category c1(1, 1, 3, "C1", CategoryType::Expense);
    Category c2(2, 1, 1, "C2", CategoryType::Expense);
    Category c3(3, 1, 2, "C3", CategoryType::Expense);

    std::vector<Category> all = {c1, c2, c3};

    auto ancestors = get_ancestors(c1, all);

    // Should return empty when cycle detected
    EXPECT_TRUE(ancestors.empty());
}

TEST(Category, GetAncestorsDetectsSelfReference) {
    Category selfRef(1, 1, 1, "SelfRef", CategoryType::Expense);  // Points to itself
    std::vector<Category> all = {selfRef};

    auto ancestors = get_ancestors(selfRef, all);

    EXPECT_TRUE(ancestors.empty());
}

TEST(Category, GetAncestorsDeepHierarchy) {
    Category c1(1, 1, std::nullopt, "Level1", CategoryType::Expense);
    Category c2(2, 1, 1, "Level2", CategoryType::Expense);
    Category c3(3, 1, 2, "Level3", CategoryType::Expense);
    Category c4(4, 1, 3, "Level4", CategoryType::Expense);
    Category c5(5, 1, 4, "Level5", CategoryType::Expense);

    std::vector<Category> all = {c1, c2, c3, c4, c5};

    auto ancestors = get_ancestors(c5, all);

    EXPECT_EQ(ancestors.size(), 4);
    EXPECT_EQ(ancestors[0].id, 1);
    EXPECT_EQ(ancestors[1].id, 2);
    EXPECT_EQ(ancestors[2].id, 3);
    EXPECT_EQ(ancestors[3].id, 4);
}

// =============================================================================
// Field Modification Tests
// =============================================================================

TEST(Category, CanModifyFields) {
    Category c;

    c.id = 42;
    c.user_id = 10;
    c.parent_id = 5;
    c.name = "Updated";
    c.type = CategoryType::Income;

    EXPECT_EQ(c.id, 42);
    EXPECT_EQ(c.user_id.value(), 10);
    EXPECT_EQ(c.parent_id.value(), 5);
    EXPECT_EQ(c.name, "Updated");
    EXPECT_EQ(c.type, CategoryType::Income);
}
